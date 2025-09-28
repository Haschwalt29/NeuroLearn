from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import EmotionLog, User
from ..services.emotion_service import EmotionDetectionService

emotion_bp = Blueprint("emotion", __name__)
service = EmotionDetectionService()


@emotion_bp.post("/emotion")
@jwt_required(optional=True)
def analyze_emotion():
    # Optional auth: if logged in, store; if not, just return result
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id)) if user_id else None

    if user and not user.emotion_opt_in:
        return jsonify({"error": "emotion detection disabled in settings"}), 403

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        file = request.files.get("file")
        if not file:
            return jsonify({"error": "no file uploaded"}), 400
        img_bytes = file.read()
        import numpy as np, cv2
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        analyzed = service.analyze_ndarray(img) if img is not None else None
    else:
        data = request.get_json() or {}
        image_b64 = data.get("image")
        analyzed = service.analyze_base64_image(image_b64) if image_b64 else None

    if not analyzed:
        return jsonify({"error": "no emotion detected"}), 400

    emotion, confidence = analyzed

    # Persist if user is present and opted-in
    if user:
        log = EmotionLog(user_id=user.id, emotion=emotion, confidence=confidence)
        db.session.add(log)
        db.session.commit()
        socketio.emit(
            "emotion_update",
            {"user_id": user.id, "emotion": emotion, "confidence": confidence, "timestamp": log.timestamp.isoformat()},
        )

    return jsonify({"emotion": emotion, "confidence": confidence})


@emotion_bp.get("/emotion/logs")
@jwt_required()
def get_logs():
    user_id = int(get_jwt_identity())
    logs = (
        EmotionLog.query.filter_by(user_id=user_id)
        .order_by(EmotionLog.timestamp.desc())
        .limit(200)
        .all()
    )
    return jsonify([
        {"timestamp": l.timestamp.isoformat(), "emotion": l.emotion, "confidence": l.confidence}
        for l in reversed(logs)
    ])


