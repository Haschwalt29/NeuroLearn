from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, LearningStyle
from ..services.learning_style_service import LearningStyleService

style_bp = Blueprint("learning_style", __name__)
style_service = LearningStyleService()


@style_bp.post("/update")
@jwt_required()
def update_learning_style():
    """Update learning style based on lesson performance"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if learning style tracking is enabled
    if not user.learning_style_opt_in:
        return jsonify({'error': 'Learning style tracking is disabled'}), 403
    
    data = request.get_json() or {}
    
    # Validate required fields
    style = data.get('style')
    score = data.get('score')
    
    if not style or score is None:
        return jsonify({'error': 'style and score are required'}), 400
    
    if style not in ['visual', 'auditory', 'example']:
        return jsonify({'error': 'style must be visual, auditory, or example'}), 400
    
    if not 0.0 <= score <= 1.0:
        return jsonify({'error': 'score must be between 0.0 and 1.0'}), 400
    
    try:
        # Optional fields
        time_spent = data.get('time_spent')
        engagement_score = data.get('engagement_score')
        
        # Update learning style
        result = style_service.update_learning_style(
            user_id=user_id,
            style=style,
            performance_score=score,
            time_spent=time_spent,
            engagement_score=engagement_score
        )
        
        # Emit real-time update
        socketio.emit('learning_style_update', {
            'user_id': user_id,
            'style': style,
            'score': score,
            'dominant_style': result['dominant_style'],
            'confidence': result['confidence'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'success': True,
            'learning_style': result
        }), 200
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to update learning style: {str(e)}'}), 500


@style_bp.get("/")
@jwt_required()
def get_learning_style():
    """Get current learning style for the logged-in user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        result = style_service.get_dominant_style(user_id)
        
        return jsonify({
            'user_id': user_id,
            'learning_style_opt_in': user.learning_style_opt_in,
            'learning_style': result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get learning style: {str(e)}'}), 500


@style_bp.get("/insights")
@jwt_required()
def get_learning_style_insights():
    """Get detailed insights about user's learning style"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.learning_style_opt_in:
        return jsonify({'error': 'Learning style tracking is disabled'}), 403
    
    try:
        insights = style_service.get_style_insights(user_id)
        
        return jsonify({
            'user_id': user_id,
            'insights': insights
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get insights: {str(e)}'}), 500


@style_bp.post("/reset")
@jwt_required()
def reset_learning_style():
    """Reset learning style data for the user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        success = style_service.reset_learning_style(user_id)
        
        if success:
            # Emit reset notification
            socketio.emit('learning_style_reset', {
                'user_id': user_id,
                'timestamp': datetime.utcnow().isoformat()
            }, room=str(user_id))
            
            return jsonify({
                'success': True,
                'message': 'Learning style data reset successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': 'No learning style data found to reset'
            }), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to reset learning style: {str(e)}'}), 500


@style_bp.get("/stats")
@jwt_required()
def get_learning_style_stats():
    """Get learning style statistics for the user"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if not learning_style:
            return jsonify({
                'user_id': user_id,
                'total_attempts': 0,
                'style_distribution': {
                    'visual': 0,
                    'auditory': 0,
                    'example': 0
                },
                'dominant_style': None,
                'confidence': 0.0
            }), 200
        
        # Calculate style distribution percentages
        total_attempts = learning_style.total_attempts
        style_distribution = {
            'visual': (learning_style.visual_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'auditory': (learning_style.auditory_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'example': (learning_style.example_attempts / total_attempts * 100) if total_attempts > 0 else 0
        }
        
        return jsonify({
            'user_id': user_id,
            'total_attempts': total_attempts,
            'style_distribution': style_distribution,
            'style_attempts': {
                'visual': learning_style.visual_attempts,
                'auditory': learning_style.auditory_attempts,
                'example': learning_style.example_attempts
            },
            'style_scores': {
                'visual': learning_style.visual_score,
                'auditory': learning_style.auditory_score,
                'example': learning_style.example_score
            },
            'dominant_style': learning_style.dominant_style,
            'confidence': style_service._calculate_confidence(learning_style),
            'last_updated': learning_style.updated_at.isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@style_bp.get("/recommendations")
@jwt_required()
def get_content_recommendations():
    """Get content recommendations based on learning style"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    if not user.learning_style_opt_in:
        return jsonify({
            'recommendations': ['Enable learning style tracking for personalized recommendations'],
            'dominant_style': None
        }), 200
    
    try:
        learning_style_data = style_service.get_dominant_style(user_id)
        dominant_style = learning_style_data['dominant_style']
        
        if not dominant_style:
            return jsonify({
                'recommendations': ['Complete more lessons to get personalized recommendations'],
                'dominant_style': None
            }), 200
        
        # Generate style-specific recommendations
        recommendations = {
            'visual': [
                '📊 Request diagrams and charts for complex topics',
                '🎨 Use mind maps for note-taking',
                '📹 Watch video content with visual aids',
                '🖼️ Look for infographics and visual summaries',
                '📐 Use color coding for different concepts'
            ],
            'auditory': [
                '🎧 Listen to audio explanations and lectures',
                '💬 Participate in group discussions',
                '🗣️ Use verbal repetition techniques',
                '🎵 Create mnemonics with rhythm or music',
                '📢 Read content aloud for better retention'
            ],
            'example': [
                '🛠️ Focus on hands-on exercises and projects',
                '📝 Work through step-by-step tutorials',
                '🧪 Try practical examples and case studies',
                '🎯 Practice with real-world scenarios',
                '🔧 Use interactive coding environments'
            ]
        }
        
        return jsonify({
            'recommendations': recommendations[dominant_style],
            'dominant_style': dominant_style,
            'confidence': learning_style_data['confidence'],
            'style_scores': {
                'visual': learning_style_data['visual_score'],
                'auditory': learning_style_data['auditory_score'],
                'example': learning_style_data['example_score']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500
