import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

from .. import db, socketio
from ..models import CoLearnerProfile, CoLearnerDialogLog, CoLearnerActivity

PRESETS_PATH = os.path.join(os.path.dirname(__file__), 'persona_presets.json')

def load_presets() -> Dict[str, Any]:
    try:
        with open(PRESETS_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def get_or_create_profile(user_id: int) -> CoLearnerProfile:
    profile = CoLearnerProfile.query.filter_by(user_id=user_id).first()
    if profile:
        return profile
    presets = load_presets()
    default_preset = presets.get('curious_companion', {})
    profile = CoLearnerProfile(
        user_id=user_id,
        persona_config=default_preset,
        xp=0,
        level=1,
        traits=default_preset.get('base_traits', []),
        humor_level=3,
        settings={"enabled": False, "save_dialogs": False}
    )
    db.session.add(profile)
    db.session.commit()
    return profile


def log_dialog(user_id: int, direction: str, text: str, metadata: Optional[dict] = None):
    profile = get_or_create_profile(user_id)
    if not (profile.settings or {}).get('save_dialogs', False):
        return
    row = CoLearnerDialogLog(user_id=user_id, direction=direction, text=text, metadata=metadata or {})
    db.session.add(row)
    db.session.commit()


def add_xp(user_id: int, amount: int, reason: str = "activity"):
    profile = get_or_create_profile(user_id)
    old_level = profile.level
    profile.xp = (profile.xp or 0) + int(amount)
    
    # Calculate new level (every 100 XP)
    new_level = (profile.xp // 100) + 1
    profile.level = new_level
    
    # Check for trait unlocks
    new_traits = []
    if new_level >= 3 and "encourager" not in profile.traits:
        new_traits.append("encourager")
    if new_level >= 5 and "humorist" not in profile.traits:
        new_traits.append("humorist")
    if new_level >= 10 and "mentor" not in profile.traits:
        new_traits.append("mentor")
    
    if new_traits:
        profile.traits = list(set(profile.traits + new_traits))
    
    db.session.commit()
    
    # Emit socket events
    socketio.emit('colearner_xp_update', {
        'user_id': user_id,
        'xp': profile.xp,
        'level': profile.level,
        'xp_gained': amount,
        'reason': reason
    })
    
    if new_level > old_level:
        socketio.emit('colearner_level_up', {
            'user_id': user_id,
            'level': new_level,
            'new_traits': new_traits,
            'total_traits': profile.traits
        })
    
    return {
        'xp': profile.xp,
        'level': profile.level,
        'new_traits': new_traits,
        'leveled_up': new_level > old_level
    }

def award_colearner_xp(user_id: int, amount: int, reason: str):
    # Keep backward compatibility
    return add_xp(user_id, amount, reason)


def _get_dialog_memory(user_id: int, limit: int = 20) -> list:
    """Get recent dialog history for context"""
    recent_dialogs = CoLearnerDialogLog.query.filter_by(
        user_id=user_id
    ).order_by(CoLearnerDialogLog.created_at.desc()).limit(limit).all()
    return [{'direction': d.direction, 'text': d.text, 'created_at': d.created_at} for d in recent_dialogs]

def _generate_humor(persona: dict, traits: list, humor_level: int, context: dict) -> str:
    """Generate humor based on persona, traits, and humor level"""
    humor_style = persona.get('humor_style', 'playful_puns')
    
    if humor_level < 3 or 'humorist' not in traits:
        return ""
    
    jokes = {
        'playful_puns': [
            "Why don't scientists trust atoms? Because they make up everything! 😄",
            "I told my computer I needed a break, and now it won't stop sending me Kit-Kat ads! 🍫",
            "Why did the math book look so sad? Because it had too many problems! 📚"
        ],
        'gentle_wisdom': [
            "A wise person once said: 'The only way to do great work is to love what you do.' 🌸",
            "Remember: even the tallest tree was once just a nut that held its ground. 🌳",
            "Patience is not the ability to wait, but how you behave while waiting. 🧘"
        ],
        'witty_sarcasm': [
            "Oh, struggling with this? How... unexpected. 😏",
            "Well, well, well. Look who's back for more punishment! 💪",
            "I see you've chosen the 'hard way' again. How delightfully predictable! ⚡"
        ]
    }
    
    import random
    joke_list = jokes.get(humor_style, jokes['playful_puns'])
    return random.choice(joke_list)

def _generate_personality_reply(persona: dict, message: str, context: dict, xp: int = 0, traits: list = None, humor_level: int = 3) -> Dict[str, Any]:
    """Generate reply with personality, humor, and growth-based traits"""
    tone = (persona or {}).get('tone', 'friendly')
    name = (persona or {}).get('name', 'Nova')
    verbosity = (persona or {}).get('verbosity', 'short')
    traits = traits or []
    
    # Base prefix with personality
    prefix = {
        'playful': "😉",
        'calm': "🌿", 
        'challenging': "🔥",
    }.get(tone, "✨")
    base = f"{prefix} {name}: "
    
    # Generate humor if conditions are met
    humor = _generate_humor(persona, traits, humor_level, context)
    
    # Base response logic
    if 'integral' in message.lower() or 'hard' in message.lower():
        if 'encourager' in traits:
            text = "I believe in you! Want me to try a step, or should I show a quick example? We've got this! 💪"
        elif 'mentor' in traits:
            text = "Ah, integrals. The art of finding the area under curves. Let me guide you through this step by step. 🧙"
        else:
            text = "Want me to try a step, or should I show a quick example?"
        actions = [
            { 'type': 'attempt_problem' },
            { 'type': 'explain_example' },
            { 'type': 'give_hint' }
        ]
    else:
        if 'encourager' in traits:
            text = "You're doing great! Want a hint, a quick example, or shall we quiz together? I'm here to support you! 🌟"
        elif 'mentor' in traits:
            text = "Wisdom comes from experience. Let's build on what you know. What would you like to explore? 🧘"
        else:
            text = "Got it! Want a hint, a quick example, or shall we quiz together?"
        actions = [
            { 'type': 'give_hint' },
            { 'type': 'explain_example' },
            { 'type': 'start_quiz' }
        ]
    
    # Add humor if generated
    if humor:
        text += f"\n\n{humor}"
    
    return { 'text': base + text, 'actions': actions, 'confidence': 0.7 + (len(traits) * 0.1) }

def _rules_reply(persona: dict, message: str, context: dict) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    return _generate_personality_reply(persona, message, context)


def generate_reply(user_id: int, message: str, context: Optional[dict] = None) -> Dict[str, Any]:
    profile = get_or_create_profile(user_id)
    
    # Get dialog memory for context
    dialog_memory = _get_dialog_memory(user_id, 20)
    
    # Award XP for interaction
    add_xp(user_id, 5, "chat_interaction")
    
    # Generate personality-based reply
    reply = _generate_personality_reply(
        profile.persona_config or {}, 
        message, 
        context or {},
        profile.xp or 0,
        profile.traits or [],
        profile.humor_level or 3
    )
    
    # Log the interaction
    log_dialog(user_id, 'user', message, metadata=(context or {}))
    log_dialog(user_id, 'colearner', reply['text'], metadata={
        'actions': reply['actions'], 
        'confidence': reply['confidence'],
        'xp': profile.xp,
        'level': profile.level,
        'traits': profile.traits
    })
    
    # Emit socket event
    socketio.emit('colearner_message', { 
        'user_id': user_id, 
        'from': 'colearner', 
        'text': reply['text'], 
        'meta': reply 
    })
    
    return reply


def suggest_activity(user_id: int, context: dict) -> Dict[str, Any]:
    # Simple: prefer start_quiz if user seems confident; otherwise give_hint
    if (context or {}).get('confidence', 0.5) > 0.6:
        return { 'type': 'start_quiz' }
    return { 'type': 'give_hint' }


def mirror_emotion(user_id: int, emotion_label: str, confidence: float) -> Dict[str, Any]:
    profile = get_or_create_profile(user_id)
    tone_map = {
        'frustrated': 'calm',
        'sad': 'calm',
        'happy': 'playful',
        'neutral': 'friendly'
    }
    persona = dict(profile.persona_config or {})
    persona['tone'] = tone_map.get(emotion_label, persona.get('tone', 'friendly'))
    profile.persona_config = persona
    db.session.commit()
    reply = None
    if emotion_label == 'frustrated':
        reply = "I feel you. Want a small hint, or should we take a short breather?"
    elif emotion_label == 'happy':
        reply = "Nice! Want to try something a bit more challenging together?"
    if reply:
        socketio.emit('colearner_message', { 'user_id': user_id, 'from': 'colearner', 'text': reply, 'meta': { 'emotion_mirror': True } })
    return { 'persona': persona, 'reply': reply }


def update_persona_learning(user_id: int, result: dict):
    profile = get_or_create_profile(user_id)
    xp = int(result.get('xp', 0))
    if xp:
        award_colearner_xp(user_id, xp, reason='activity')
    # Placeholder: update knowledge_state aggregate
    ks = dict(profile.knowledge_state or {})
    topic = result.get('topic')
    if topic:
        ks[topic] = float(result.get('mastery', 0.0))
    profile.knowledge_state = ks
    db.session.commit()


def record_activity(user_id: int, activity_type: str, payload: dict, result: Optional[dict] = None) -> CoLearnerActivity:
    row = CoLearnerActivity(user_id=user_id, activity_type=activity_type, payload=payload or {}, result=result or {})
    db.session.add(row)
    db.session.commit()
    socketio.emit('colearner_activity', { 'user_id': user_id, 'activity': { 'type': activity_type, 'payload': payload, 'result': result or {} } })
    return row


