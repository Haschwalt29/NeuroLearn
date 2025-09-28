from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import CoLearnerProfile
from ..services.colearner_service import (
    get_or_create_profile, generate_reply, suggest_activity,
    mirror_emotion, update_persona_learning, record_activity, add_xp
)

co_bp = Blueprint('colearner', __name__)

@co_bp.get('/state')
@jwt_required()
def state():
    user_id = int(get_jwt_identity())
    profile = get_or_create_profile(user_id)
    return jsonify({
        'profile': {
            'experience': profile.experience,
            'xp': profile.xp or 0,
            'level': profile.level or 1,
            'traits': profile.traits or [],
            'humor_level': profile.humor_level or 3,
            'persona_config': profile.persona_config,
            'knowledge_state': profile.knowledge_state,
            'settings': profile.settings,
        }
    })

@co_bp.post('/message')
@jwt_required()
def message():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    msg = (data.get('message') or '').strip()
    if not msg:
        return jsonify({ 'error': 'message required' }), 400
    reply = generate_reply(user_id, msg, context=data.get('context') or {})
    return jsonify(reply)

@co_bp.post('/action')
@jwt_required()
def action():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    atype = data.get('action_type')
    payload = data.get('payload') or {}
    if not atype:
        return jsonify({ 'error': 'action_type required' }), 400
    
    # Calculate XP based on activity type and performance
    xp_amount = 0
    if atype == 'lesson_complete':
        score = payload.get('score', 0)
        xp_amount = int(score * 50) + 10  # Base 10 + up to 50 based on score
    elif atype == 'quiz_complete':
        correct = payload.get('correct_answers', 0)
        total = payload.get('total_questions', 1)
        score = correct / total if total > 0 else 0
        xp_amount = int(score * 30) + 5  # Base 5 + up to 30 based on score
    elif atype == 'review_complete':
        quality = payload.get('quality_score', 0)
        xp_amount = int(quality * 20) + 5  # Base 5 + up to 20 based on quality
    
    # Award XP and record activity
    if xp_amount > 0:
        add_xp(user_id, xp_amount, f'{atype}_completion')
    
    # Generate co-learner response based on performance
    reply = None
    if atype in ['lesson_complete', 'quiz_complete', 'review_complete']:
        score = payload.get('score', payload.get('quality_score', 0))
        if score >= 0.8:
            reply = "Awesome work! You're really getting the hang of this! 🎉"
        elif score >= 0.6:
            reply = "Nice job! Want to try something a bit more challenging?"
        else:
            reply = "No worries, learning takes time. Want me to explain this step by step?"
        
        if reply:
            from ..services.colearner_service import generate_reply
            generate_reply(user_id, reply, context={'activity_type': atype, 'score': score})
    
    row = record_activity(user_id, atype, payload, result={ 'xp_awarded': xp_amount, 'reply_generated': reply is not None })
    return jsonify({ 'ok': True, 'id': row.id, 'xp_awarded': xp_amount })

@co_bp.post('/settings')
@jwt_required()
def settings():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    profile = get_or_create_profile(user_id)
    new_settings = dict(profile.settings or {})
    for k in ('enabled', 'save_dialogs'):
        if k in data:
            new_settings[k] = bool(data[k])
    persona = data.get('persona')
    if persona:
        pc = dict(profile.persona_config or {})
        pc.update(persona)
        profile.persona_config = pc
    if 'humor_level' in data:
        profile.humor_level = max(0, min(10, int(data['humor_level'])))
    profile.settings = new_settings
    db.session.commit()
    return jsonify({ 'profile': { 'settings': new_settings, 'persona_config': profile.persona_config } })

@co_bp.post('/mirror_emotion')
@jwt_required()
def mirror():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    emotion = data.get('emotion')
    confidence = float(data.get('confidence') or 0)
    res = mirror_emotion(user_id, emotion, confidence)
    return jsonify(res)


