from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User
from ..services.debate_service import debate_service
from ..utils.llm_utils import llm_utils

debate_bp = Blueprint('debate', __name__)

@debate_bp.post('/start')
@jwt_required()
def start_debate():
    """Start a new debate session"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        topic = data.get('topic')
        learner_stance = data.get('stance', 'neutral')
        difficulty = data.get('difficulty', 'intermediate')
        settings = data.get('settings', {})
        
        if not topic:
            return jsonify({
                'success': False,
                'error': 'Topic is required'
            }), 400
        
        # Validate stance
        valid_stances = ['pro', 'con', 'neutral', 'for', 'against']
        if learner_stance.lower() not in valid_stances:
            return jsonify({
                'success': False,
                'error': f'Invalid stance. Must be one of: {", ".join(valid_stances)}'
            }), 400
        
        # Validate difficulty
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        if difficulty not in valid_difficulties:
            return jsonify({
                'success': False,
                'error': f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}'
            }), 400
        
        result = debate_service.start_debate(
            user_id=user_id,
            topic=topic,
            learner_stance=learner_stance,
            difficulty=difficulty,
            settings=settings
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.post('/reply')
@jwt_required()
def reply_to_debate():
    """Send learner's reply and get AI response"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        session_id = data.get('session_id')
        learner_message = data.get('learner_message')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required'
            }), 400
        
        if not learner_message:
            return jsonify({
                'success': False,
                'error': 'Learner message is required'
            }), 400
        
        # Validate session exists and belongs to user
        from ..models import DebateSession
        session = DebateSession.query.get(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Debate session not found'
            }), 404
            
        if session.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        result = debate_service.generate_ai_argument(
            session_id=session_id,
            learner_message=learner_message
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Error in reply_to_debate: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error. Please try again.'
        }), 500

@debate_bp.post('/switch')
@jwt_required()
def switch_stance():
    """Switch AI stance mid-debate"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required'
            }), 400
        
        result = debate_service.switch_stance(session_id=session_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.post('/end')
@jwt_required()
def end_debate():
    """End debate session"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'error': 'Session ID is required'
            }), 400
        
        result = debate_service.end_debate(session_id=session_id)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.get('/session/<int:session_id>')
@jwt_required()
def get_debate_session(session_id):
    """Get debate session details"""
    user_id = int(get_jwt_identity())
    
    try:
        result = debate_service.get_debate_session(session_id)
        
        # Verify user owns this session
        if result['session']['user_id'] != user_id:
            return jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.get('/history')
@jwt_required()
def get_debate_history():
    """Get user's debate history"""
    user_id = int(get_jwt_identity())
    limit = request.args.get('limit', 10, type=int)
    
    try:
        history = debate_service.get_user_debate_history(user_id, limit)
        
        return jsonify({
            'success': True,
            'data': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.get('/topics')
@jwt_required()
def get_debate_topics():
    """Get available debate topics"""
    difficulty = request.args.get('difficulty', 'intermediate')
    
    try:
        topics = llm_utils.get_debate_topics(difficulty)
        
        return jsonify({
            'success': True,
            'data': topics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.get('/stats')
@jwt_required()
def get_debate_stats():
    """Get user's debate statistics"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import DebateSession
        
        # Get user's debate sessions
        sessions = DebateSession.query.filter_by(user_id=user_id).all()
        
        if not sessions:
            return jsonify({
                'success': True,
                'data': {
                    'total_debates': 0,
                    'avg_learner_score': 0,
                    'avg_debate_quality': 0,
                    'total_turns': 0,
                    'total_stance_switches': 0,
                    'favorite_topics': [],
                    'improvement_areas': []
                }
            })
        
        # Calculate statistics
        total_debates = len(sessions)
        completed_debates = [s for s in sessions if s.status == 'ended']
        
        avg_learner_score = 0
        avg_debate_quality = 0
        total_turns = 0
        total_stance_switches = 0
        
        if completed_debates:
            avg_learner_score = sum(s.learner_score for s in completed_debates) / len(completed_debates)
            avg_debate_quality = sum(s.debate_quality for s in completed_debates) / len(completed_debates)
        
        total_turns = sum(s.total_turns for s in sessions)
        total_stance_switches = sum(s.stance_switches for s in sessions)
        
        # Get favorite topics
        topic_counts = {}
        for session in sessions:
            topic = session.topic
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        favorite_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Get common improvement areas
        from ..models import DebateScore
        improvement_areas = {}
        for session in sessions:
            scores = DebateScore.query.filter_by(
                session_id=session.id,
                scorer_type='system'
            ).all()
            
            for score in scores:
                for area in score.improvement_areas:
                    improvement_areas[area] = improvement_areas.get(area, 0) + 1
        
        common_improvement_areas = sorted(improvement_areas.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return jsonify({
            'success': True,
            'data': {
                'total_debates': total_debates,
                'avg_learner_score': round(avg_learner_score, 2),
                'avg_debate_quality': round(avg_debate_quality, 2),
                'total_turns': total_turns,
                'total_stance_switches': total_stance_switches,
                'favorite_topics': [{'topic': topic, 'count': count} for topic, count in favorite_topics],
                'improvement_areas': [{'area': area, 'count': count} for area, count in common_improvement_areas]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debate_bp.delete('/session/<int:session_id>')
@jwt_required()
def delete_debate_session(session_id):
    """Delete a debate session"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import DebateSession
        
        session = DebateSession.query.get(session_id)
        if not session:
            return jsonify({
                'success': False,
                'error': 'Debate session not found'
            }), 404
            
        if session.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        # Delete the session (cascade will handle related records)
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Debate session deleted successfully'
        })
        
    except Exception as e:
        print(f"Error deleting debate session: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete debate session'
        }), 500

@debate_bp.get('/active')
@jwt_required()
def get_active_debates():
    """Get user's active debate sessions"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import DebateSession
        
        active_sessions = DebateSession.query.filter_by(
            user_id=user_id,
            status='active'
        ).order_by(DebateSession.created_at.desc()).all()
        
        sessions_data = []
        for session in active_sessions:
            sessions_data.append({
                'id': session.id,
                'topic': session.topic,
                'learner_stance': session.learner_stance,
                'ai_stance': session.ai_stance,
                'total_turns': session.total_turns,
                'stance_switches': session.stance_switches,
                'created_at': session.created_at.isoformat(),
                'difficulty': session.difficulty_level
            })
        
        return jsonify({
            'success': True,
            'data': sessions_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
