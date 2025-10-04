from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import Concept, ConceptPrerequisite, LearnerConceptMastery

kg_bp = Blueprint('knowledge_graph', __name__)

def _concept_to_dict(c: Concept, mastery_map):
    return {
        'id': c.id,
        'name': c.name,
        'subject': c.subject,
        'difficulty_level': c.difficulty_level,
        'mastery_score': mastery_map.get(c.id, 0.0)
    }

@kg_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_graph(user_id: int):
    # nodes
    concepts = Concept.query.all()
    mastery_rows = LearnerConceptMastery.query.filter_by(user_id=user_id).all()
    mastery_map = { m.concept_id: float(m.mastery_score or 0.0) for m in mastery_rows }

    nodes = [_concept_to_dict(c, mastery_map) for c in concepts]
    # edges
    edges = [
        { 'source': row.prerequisite_id, 'target': row.concept_id }
        for row in ConceptPrerequisite.query.all()
    ]
    return jsonify({ 'nodes': nodes, 'edges': edges })

@kg_bp.route('/update', methods=['POST'])
@jwt_required()
def update_mastery():
    user_id = get_jwt_identity()
    payload = request.get_json(force=True) or {}
    updates = payload.get('updates') or []  # [{ concept_id, delta, emotion_context? }]
    out = []
    for u in updates:
        cid = int(u.get('concept_id'))
        delta = float(u.get('delta', 0.0))
        row = LearnerConceptMastery.query.filter_by(user_id=user_id, concept_id=cid).first()
        if not row:
            row = LearnerConceptMastery(user_id=user_id, concept_id=cid, mastery_score=0.0)
            db.session.add(row)
        row.mastery_score = max(0.0, min(1.0, (row.mastery_score or 0.0) + delta))
        row.emotion_snapshot = u.get('emotion_context')
        out.append({ 'concept_id': cid, 'mastery_score': row.mastery_score })
    db.session.commit()
    return jsonify({ 'updated': out })


