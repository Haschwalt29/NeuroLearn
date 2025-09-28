from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, TopicMastery, LearningProgress, LearningBadge
from ..services.learning_dna import LearningDNAEngine

dna_bp = Blueprint("learning_dna", __name__)
dna_engine = LearningDNAEngine()


@dna_bp.get("/profile/mastery/<int:user_id>")
@jwt_required()
def get_topic_mastery(user_id):
    """Get topic mastery scores for a user"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        mastery_records = TopicMastery.query.filter_by(user_id=user_id).all()
        
        mastery_data = []
        for mastery in mastery_records:
            mastery_data.append({
                'topic': mastery.topic,
                'mastery_score': mastery.mastery_score,
                'mastery_level': mastery.mastery_level,
                'total_attempts': mastery.total_attempts,
                'correct_attempts': mastery.correct_attempts,
                'streak_count': mastery.streak_count,
                'last_updated': mastery.last_updated.isoformat()
            })
        
        return jsonify({
            'user_id': user_id,
            'topic_mastery': mastery_data,
            'total_topics': len(mastery_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get mastery data: {str(e)}'}), 500


@dna_bp.get("/profile/progress/<int:user_id>")
@jwt_required()
def get_progress_history(user_id):
    """Get progress history for a user"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get query parameters
        days = int(request.args.get('days', 30))
        topic = request.args.get('topic')
        limit = int(request.args.get('limit', 100))
        
        # Build query
        query = LearningProgress.query.filter_by(user_id=user_id)
        
        if topic:
            query = query.filter(LearningProgress.topic == topic)
        
        if days:
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(LearningProgress.timestamp >= since)
        
        progress_records = query.order_by(LearningProgress.timestamp.desc()).limit(limit).all()
        
        progress_data = []
        for progress in progress_records:
            progress_data.append({
                'id': progress.id,
                'quiz_id': progress.quiz_id,
                'topic': progress.topic,
                'score': progress.score,
                'attempts': progress.attempts,
                'time_spent': progress.time_spent,
                'correct_answers': progress.correct_answers,
                'total_questions': progress.total_questions,
                'timestamp': progress.timestamp.isoformat()
            })
        
        return jsonify({
            'user_id': user_id,
            'progress_history': progress_data,
            'total_records': len(progress_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get progress history: {str(e)}'}), 500


@dna_bp.post("/profile/update")
@jwt_required()
def update_profile():
    """Update Learning DNA profile after quiz/lesson completion"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        # Validate required fields
        topic = data.get('topic')
        score = data.get('score')
        
        if not topic or score is None:
            return jsonify({'error': 'topic and score are required'}), 400
        
        # Optional fields
        time_spent = data.get('time_spent')
        quiz_id = data.get('quiz_id')
        
        # Update mastery
        mastery_result = dna_engine.update_topic_mastery(
            user_id=user_id,
            topic=topic,
            score=score,
            time_spent=time_spent,
            quiz_id=quiz_id
        )
        
        # Emit real-time update
        socketio.emit('learning_dna_update', {
            'user_id': user_id,
            'topic': topic,
            'mastery_score': mastery_result['mastery_score'],
            'mastery_level': mastery_result['mastery_level'],
            'improvement': mastery_result['improvement'],
            'badges_earned': mastery_result['badges_earned'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'success': True,
            'mastery_result': mastery_result
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to update profile: {str(e)}'}), 500


@dna_bp.get("/profile/dna/<int:user_id>")
@jwt_required()
def get_learning_dna_profile(user_id):
    """Get complete Learning DNA profile"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        profile = dna_engine.get_learning_dna_profile(user_id)
        return jsonify(profile)
        
    except Exception as e:
        return jsonify({'error': f'Failed to get Learning DNA profile: {str(e)}'}), 500


@dna_bp.get("/profile/topic-history/<int:user_id>/<topic>")
@jwt_required()
def get_topic_mastery_history(user_id, topic):
    """Get mastery history for a specific topic"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        days = int(request.args.get('days', 30))
        history = dna_engine.get_topic_mastery_history(user_id, topic, days)
        
        return jsonify({
            'user_id': user_id,
            'topic': topic,
            'mastery_history': history,
            'days_tracked': days
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get topic history: {str(e)}'}), 500


@dna_bp.get("/badges/<int:user_id>")
@jwt_required()
def get_user_badges(user_id):
    """Get all badges earned by a user"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        badges = LearningBadge.query.filter_by(user_id=user_id)\
            .order_by(LearningBadge.earned_at.desc()).all()
        
        badge_data = []
        for badge in badges:
            badge_data.append({
                'id': badge.id,
                'badge_type': badge.badge_type,
                'badge_name': badge.badge_name,
                'topic': badge.topic,
                'earned_at': badge.earned_at.isoformat(),
                'badge_data': badge.badge_data
            })
        
        return jsonify({
            'user_id': user_id,
            'badges': badge_data,
            'total_badges': len(badge_data)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get badges: {str(e)}'}), 500


@dna_bp.get("/stats/<int:user_id>")
@jwt_required()
def get_learning_stats(user_id):
    """Get learning statistics for a user"""
    current_user_id = int(get_jwt_identity())
    
    # Users can only view their own data
    if current_user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        # Get basic stats
        total_topics = TopicMastery.query.filter_by(user_id=user_id).count()
        total_badges = LearningBadge.query.filter_by(user_id=user_id).count()
        
        # Get mastery distribution
        mastery_records = TopicMastery.query.filter_by(user_id=user_id).all()
        mastery_distribution = {
            'beginner': 0,
            'intermediate': 0,
            'advanced': 0,
            'expert': 0
        }
        
        total_mastery = 0
        for mastery in mastery_records:
            mastery_distribution[mastery.mastery_level] += 1
            total_mastery += mastery.mastery_score
        
        avg_mastery = total_mastery / total_topics if total_topics > 0 else 0
        
        # Get recent activity (last 7 days)
        since = datetime.utcnow() - timedelta(days=7)
        recent_activity = LearningProgress.query.filter(
            LearningProgress.user_id == user_id,
            LearningProgress.timestamp >= since
        ).count()
        
        return jsonify({
            'user_id': user_id,
            'total_topics': total_topics,
            'total_badges': total_badges,
            'average_mastery': avg_mastery,
            'mastery_distribution': mastery_distribution,
            'recent_activity': recent_activity,
            'learning_level': 'expert' if avg_mastery >= 80 else 'advanced' if avg_mastery >= 60 else 'intermediate' if avg_mastery >= 30 else 'beginner'
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get learning stats: {str(e)}'}), 500


@dna_bp.get("/leaderboard")
@jwt_required()
def get_leaderboard():
    """Get learning leaderboard (top performers)"""
    try:
        # Get top 10 users by average mastery
        top_users = db.session.query(
            User.id,
            User.name,
            db.func.avg(TopicMastery.mastery_score).label('avg_mastery'),
            db.func.count(TopicMastery.id).label('topic_count')
        ).join(TopicMastery).group_by(User.id, User.name)\
        .having(db.func.count(TopicMastery.id) >= 3)\
        .order_by(db.func.avg(TopicMastery.mastery_score).desc())\
        .limit(10).all()
        
        leaderboard = []
        for i, user in enumerate(top_users, 1):
            leaderboard.append({
                'rank': i,
                'user_id': user.id,
                'name': user.name,
                'average_mastery': round(user.avg_mastery, 1),
                'topics_studied': user.topic_count
            })
        
        return jsonify({
            'leaderboard': leaderboard,
            'total_participants': len(leaderboard)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to get leaderboard: {str(e)}'}), 500
