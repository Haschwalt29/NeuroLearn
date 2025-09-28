from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import PerformanceLog, LearnerConceptMastery
from ..services.adaptive_engine import get_next_question

performance_bp = Blueprint("performance", __name__)


@performance_bp.post("/log")
@jwt_required()
def create_log():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}

    module = data.get("module")
    question_id = data.get("question_id")
    correct = data.get("correct")
    score = data.get("score")
    concept_id = data.get("concept_id")  # optional: link this attempt to a concept

    if module is None or correct is None:
        return jsonify({"error": "module and correct are required"}), 400

    log = PerformanceLog(
        user_id=user_id,
        module=str(module),
        question_id=int(question_id) if question_id is not None else None,
        correct=bool(correct),
        score=float(score) if score is not None else None,
    )
    db.session.add(log)
    # Optional: update learner concept mastery & emit graph update
    if concept_id is not None:
        try:
            cid = int(concept_id)
            row = LearnerConceptMastery.query.filter_by(user_id=user_id, concept_id=cid).first()
            if not row:
                row = LearnerConceptMastery(user_id=user_id, concept_id=cid, mastery_score=0.0)
                db.session.add(row)
            # Simple delta heuristic
            delta = 0.0
            if score is not None:
                try:
                    s = float(score)
                    delta = max(-0.02, min(0.08, (s - 0.5) * 0.16))
                except Exception:
                    delta = 0.0
            elif correct is not None:
                delta = 0.05 if bool(correct) else -0.01
            row.mastery_score = max(0.0, min(1.0, (row.mastery_score or 0.0) + delta))
            db.session.flush()
            socketio.emit("knowledge_graph_updated", {
                "user_id": user_id,
                "concept_id": cid,
                "mastery_score": row.mastery_score,
                "delta": delta,
            })
        except Exception:
            pass
    db.session.commit()

    payload = {
        "user_id": user_id,
        "module": log.module,
        "question_id": log.question_id,
        "correct": log.correct,
        "score": log.score,
        "timestamp": log.timestamp.isoformat(),
    }
    socketio.emit("performance_update", payload)

    return jsonify(payload), 201


@performance_bp.get("/logs")
@jwt_required()
def list_logs():
    user_id = int(get_jwt_identity())
    logs = (
        PerformanceLog.query.filter_by(user_id=user_id)
        .order_by(PerformanceLog.timestamp.desc())
        .all()
    )
    return jsonify([
        {
            "module": l.module,
            "question_id": l.question_id,
            "correct": l.correct,
            "score": l.score,
            "timestamp": l.timestamp.isoformat(),
        }
        for l in logs
    ])


quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.get("/next")
@jwt_required()
def next_quiz():
    user_id = int(get_jwt_identity())
    module = request.args.get("module")
    if not module:
        return jsonify({"error": "module is required"}), 400
    rec = get_next_question(user_id, module)
    return jsonify(rec)


