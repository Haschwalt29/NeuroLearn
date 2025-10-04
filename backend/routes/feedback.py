from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, FeedbackLog
from ..services.feedback_engine import PersonalizedFeedbackEngine

feedback_bp = Blueprint("feedback", __name__)
feedback_engine = PersonalizedFeedbackEngine()


@feedback_bp.post("/generate")
@jwt_required()
def generate_feedback():
    """Generate personalized feedback after a lesson/quiz"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    lesson_id = data.get('lesson_id')
    
    try:
        feedback_data = feedback_engine.generate_feedback(user_id, lesson_id)
        
        if 'error' in feedback_data:
            return jsonify(feedback_data), 400
        
        # Emit real-time feedback update
        socketio.emit('feedback_generated', {
            'user_id': user_id,
            'feedback_id': feedback_data['feedback_id'],
            'feedback_text': feedback_data['feedback_text'],
            'performance_summary': feedback_data['performance_summary'],
            'emotion_context': feedback_data['emotion_context'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify(feedback_data), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to generate feedback: {str(e)}'}), 500


@feedback_bp.get("/history")
@jwt_required()
def get_feedback_history():
    """Get user's feedback history"""
    user_id = int(get_jwt_identity())
    limit = int(request.args.get('limit', 10))
    
    try:
        feedback_history = feedback_engine.get_feedback_history(user_id, limit)
        return jsonify({
            'feedback_history': feedback_history,
            'total_count': len(feedback_history)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get feedback history: {str(e)}'}), 500


@feedback_bp.get("/latest")
@jwt_required()
def get_latest_feedback():
    """Get the most recent feedback for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        latest_feedback = FeedbackLog.query.filter_by(user_id=user_id)\
            .order_by(FeedbackLog.timestamp.desc())\
            .first()
        
        if not latest_feedback:
            return jsonify({'message': 'No feedback available yet'}), 404
        
        return jsonify({
            'id': latest_feedback.id,
            'lesson_id': latest_feedback.lesson_id,
            'feedback_text': latest_feedback.feedback_text,
            'feedback_type': latest_feedback.feedback_type,
            'performance_data': latest_feedback.performance_data,
            'emotion_context': latest_feedback.emotion_context,
            'timestamp': latest_feedback.timestamp.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get latest feedback: {str(e)}'}), 500


@feedback_bp.get("/stats")
@jwt_required()
def get_feedback_stats():
    """Get feedback statistics for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get recent performance summary
        performance = feedback_engine.get_performance_summary(user_id)
        
        # Get learning trends
        trends = feedback_engine.get_learning_trends(user_id)
        
        # Get recent emotions
        emotions = feedback_engine.get_recent_emotions(user_id)
        dominant_emotion = feedback_engine.determine_dominant_emotion(emotions)
        
        # Get feedback count
        feedback_count = FeedbackLog.query.filter_by(user_id=user_id).count()
        
        return jsonify({
            'performance_summary': performance,
            'learning_trends': trends,
            'emotion_context': {
                'dominant_emotion': dominant_emotion,
                'recent_emotions': emotions
            },
            'feedback_count': feedback_count
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get feedback stats: {str(e)}'}), 500


@feedback_bp.post("/lesson/complete")
@jwt_required()
def lesson_complete():
    """Trigger feedback generation when a lesson is completed"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    lesson_id = data.get('lesson_id')
    module = data.get('module')
    performance_data = data.get('performance_data', {})
    
    try:
        # Generate feedback
        feedback_data = feedback_engine.generate_feedback(user_id, lesson_id or module)
        
        if 'error' in feedback_data:
            return jsonify(feedback_data), 400
        
        # Emit lesson completion event
        socketio.emit('lesson_completed', {
            'user_id': user_id,
            'lesson_id': lesson_id or module,
            'feedback': feedback_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'message': 'Lesson completed successfully',
            'feedback': feedback_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to complete lesson: {str(e)}'}), 500


@feedback_bp.post("/quiz/complete")
@jwt_required()
def quiz_complete():
    """Trigger feedback generation when a quiz is completed"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    quiz_id = data.get('quiz_id')
    module = data.get('module')
    quiz_results = data.get('quiz_results', {})
    
    try:
        # Generate feedback
        feedback_data = feedback_engine.generate_feedback(user_id, quiz_id or module)
        
        if 'error' in feedback_data:
            return jsonify(feedback_data), 400
        
        # Emit quiz completion event
        socketio.emit('quiz_completed', {
            'user_id': user_id,
            'quiz_id': quiz_id or module,
            'quiz_results': quiz_results,
            'feedback': feedback_data,
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'message': 'Quiz completed successfully',
            'feedback': feedback_data
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to complete quiz: {str(e)}'}), 500


@feedback_bp.get("/milestone/<milestone_type>")
@jwt_required()
def check_milestone(milestone_type):
    """Check if user has achieved a milestone and generate celebratory feedback"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get learning trends
        trends = feedback_engine.get_learning_trends(user_id)
        
        milestone_achieved = False
        milestone_message = ""
        
        if milestone_type == "streak":
            if trends['streak_days'] >= 7:
                milestone_achieved = True
                milestone_message = f"🎉 Congratulations! You've achieved a {trends['streak_days']}-day learning streak!"
            elif trends['streak_days'] >= 3:
                milestone_achieved = True
                milestone_message = f"🔥 Great job! You're on a {trends['streak_days']}-day streak!"
        
        elif milestone_type == "improvement":
            if trends['improvement_trend'] == 'improving':
                milestone_achieved = True
                milestone_message = "📈 Amazing progress! Your learning is accelerating!"
        
        elif milestone_type == "consistency":
            if trends['consistency_score'] >= 80:
                milestone_achieved = True
                milestone_message = "🎯 Excellent consistency! You're building great learning habits!"
        
        if milestone_achieved:
            # Create milestone feedback
            feedback_log = FeedbackLog(
                user_id=user_id,
                lesson_id=f"milestone_{milestone_type}",
                feedback_text=milestone_message,
                feedback_type="milestone",
                performance_data={'milestone_type': milestone_type},
                emotion_context={'trends': trends}
            )
            
            db.session.add(feedback_log)
            db.session.commit()
            
            # Emit milestone achievement
            socketio.emit('milestone_achieved', {
                'user_id': user_id,
                'milestone_type': milestone_type,
                'message': milestone_message,
                'timestamp': datetime.utcnow().isoformat()
            }, room=str(user_id))
            
            return jsonify({
                'milestone_achieved': True,
                'message': milestone_message,
                'feedback_id': feedback_log.id
            })
        else:
            return jsonify({
                'milestone_achieved': False,
                'message': f'Keep working towards your {milestone_type} milestone!'
            })
        
    except Exception as e:
        return jsonify({'error': f'Failed to check milestone: {str(e)}'}), 500
