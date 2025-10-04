from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import TopicMastery, PerformanceLog, EmotionLog, LearningStyle, Content
from ..services.personalization_engine import PersonalizationEngine

personalization_bp = Blueprint("personalization", __name__)
personalization_engine = PersonalizationEngine()


@personalization_bp.get("/insights")
@jwt_required()
def get_learning_insights():
    user_id = int(get_jwt_identity())
    
    try:
        insights = personalization_engine.get_learning_insights(user_id)
        return jsonify(insights), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get learning insights: {str(e)}'}), 500


@personalization_bp.post("/update-mastery")
@jwt_required()
def update_mastery_profile():
    """Update user's mastery profile based on performance"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    topic = data.get('topic')
    performance_score = data.get('performance_score')
    emotion_hint = data.get('emotion_hint')
    
    if not topic or performance_score is None:
        return jsonify({'error': 'Topic and performance_score are required'}), 400
    
    if not (0.0 <= performance_score <= 1.0):
        return jsonify({'error': 'Performance score must be between 0.0 and 1.0'}), 400
    
    try:
        result = personalization_engine.update_mastery_profile(
            user_id=user_id,
            topic=topic,
            performance_score=performance_score,
            emotion_hint=emotion_hint
        )
        
        # Emit real-time update
        socketio.emit('mastery_updated', {
            'user_id': user_id,
            'topic': topic,
            'mastery_score': result['mastery_score'],
            'mastery_level': result['mastery_level'],
            'emotion_adjustment': result['emotion_adjustment']
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update mastery profile: {str(e)}'}), 500


@personalization_bp.get("/custom-exercises")
@jwt_required()
def get_custom_exercises():
    """Get custom exercises based on user's weaknesses and learning style"""
    user_id = int(get_jwt_identity())
    topic = request.args.get('topic')
    
    try:
        exercises = personalization_engine.generate_custom_exercises(user_id, topic)
        return jsonify({
            "exercises": exercises,
            "total_count": len(exercises)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get custom exercises: {str(e)}'}), 500


@personalization_bp.get("/revision-schedule")
@jwt_required()
def get_spaced_repetition_schedule():
    """Get spaced repetition schedule for user"""
    user_id = int(get_jwt_identity())
    
    try:
        schedule = personalization_engine.get_spaced_repetition_schedule(user_id)
        return jsonify(schedule), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get revision schedule: {str(e)}'}), 500


@personalization_bp.get("/mastery-map")
@jwt_required()
def get_mastery_map():
    """Get user's mastery map across all topics"""
    user_id = int(get_jwt_identity())
    
    try:
        topic_masteries = TopicMastery.query.filter_by(user_id=user_id).all()
        
        mastery_map = {}
        for mastery in topic_masteries:
            mastery_map[mastery.topic] = {
                "score": mastery.mastery_score,
                "level": mastery.mastery_level,
                "attempts": mastery.total_attempts,
                "correct_attempts": mastery.correct_attempts,
                "streak": mastery.streak_count,
                "last_updated": mastery.last_updated.isoformat() if mastery.last_updated else None
            }
        
        # Calculate overall mastery statistics
        total_topics = len(topic_masteries)
        if total_topics > 0:
            avg_mastery = sum(m.mastery_score for m in topic_masteries) / total_topics
            weak_count = len([m for m in topic_masteries if m.mastery_score < 40])
            strong_count = len([m for m in topic_masteries if m.mastery_score >= 80])
        else:
            avg_mastery = 0
            weak_count = 0
            strong_count = 0
        
        return jsonify({
            "mastery_map": mastery_map,
            "statistics": {
                "total_topics": total_topics,
                "average_mastery": avg_mastery,
                "weak_topics": weak_count,
                "strong_topics": strong_count,
                "mastery_percentage": (strong_count / total_topics * 100) if total_topics > 0 else 0
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get mastery map: {str(e)}'}), 500


@personalization_bp.get("/weaknesses")
@jwt_required()
def get_weak_topics():
    """Get user's weak topics that need attention"""
    user_id = int(get_jwt_identity())
    
    try:
        weak_topics = TopicMastery.query.filter(
            TopicMastery.user_id == user_id,
            TopicMastery.mastery_score < 40.0
        ).order_by(TopicMastery.mastery_score.asc()).all()
        
        topics_data = []
        for mastery in weak_topics:
            topics_data.append({
                "topic": mastery.topic,
                "mastery_score": mastery.mastery_score,
                "mastery_level": mastery.mastery_level,
                "total_attempts": mastery.total_attempts,
                "correct_attempts": mastery.correct_attempts,
                "streak_count": mastery.streak_count,
                "last_updated": mastery.last_updated.isoformat() if mastery.last_updated else None
            })
        
        return jsonify({
            "weak_topics": topics_data,
            "total_count": len(topics_data),
            "priority_topics": topics_data[:5]  # Top 5 weakest topics
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get weak topics: {str(e)}'}), 500


@personalization_bp.get("/strengths")
@jwt_required()
def get_strong_topics():
    """Get user's strong topics"""
    user_id = int(get_jwt_identity())
    
    try:
        strong_topics = TopicMastery.query.filter(
            TopicMastery.user_id == user_id,
            TopicMastery.mastery_score >= 80.0
        ).order_by(TopicMastery.mastery_score.desc()).all()
        
        topics_data = []
        for mastery in strong_topics:
            topics_data.append({
                "topic": mastery.topic,
                "mastery_score": mastery.mastery_score,
                "mastery_level": mastery.mastery_level,
                "total_attempts": mastery.total_attempts,
                "correct_attempts": mastery.correct_attempts,
                "streak_count": mastery.streak_count,
                "last_updated": mastery.last_updated.isoformat() if mastery.last_updated else None
            })
        
        return jsonify({
            "strong_topics": topics_data,
            "total_count": len(topics_data),
            "expert_topics": [t for t in topics_data if t["mastery_score"] >= 95]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get strong topics: {str(e)}'}), 500


@personalization_bp.get("/learning-style")
@jwt_required()
def get_learning_style_analysis():
    """Get detailed learning style analysis"""
    user_id = int(get_jwt_identity())
    
    try:
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if not learning_style:
            return jsonify({
                "message": "No learning style data available",
                "learning_style": None
            }), 200
        
        # Get recent performance data for analysis
        recent_logs = PerformanceLog.query.filter(
            PerformanceLog.user_id == user_id,
            PerformanceLog.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).all()
        
        # Analyze performance by content type (if available)
        performance_by_type = {}
        for log in recent_logs:
            # This would need to be enhanced based on actual content type tracking
            content_type = "example"  # Default assumption
            if content_type not in performance_by_type:
                performance_by_type[content_type] = []
            performance_by_type[content_type].append(log.score)
        
        # Calculate average performance by type
        avg_performance_by_type = {}
        for content_type, scores in performance_by_type.items():
            avg_performance_by_type[content_type] = sum(scores) / len(scores) if scores else 0
        
        return jsonify({
            "learning_style": {
                "visual_score": learning_style.visual_score,
                "auditory_score": learning_style.auditory_score,
                "example_score": learning_style.example_score,
                "dominant_style": learning_style.dominant_style,
                "total_attempts": learning_style.total_attempts,
                "confidence": learning_style.confidence,
                "updated_at": learning_style.updated_at.isoformat()
            },
            "performance_analysis": {
                "avg_performance_by_type": avg_performance_by_type,
                "total_attempts": len(recent_logs),
                "analysis_period_days": 30
            },
            "recommendations": [
                f"Your dominant learning style is {learning_style.dominant_style}",
                f"Focus on {learning_style.dominant_style}-based content for better results",
                "Consider mixing learning styles for comprehensive understanding"
            ]
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get learning style analysis: {str(e)}'}), 500


@personalization_bp.get("/progress-trends")
@jwt_required()
def get_progress_trends():
    """Get user's learning progress trends over time"""
    user_id = int(get_jwt_identity())
    days = int(request.args.get('days', 30))
    
    try:
        # Get performance logs for the specified period
        start_date = datetime.utcnow() - timedelta(days=days)
        performance_logs = PerformanceLog.query.filter(
            PerformanceLog.user_id == user_id,
            PerformanceLog.timestamp >= start_date
        ).order_by(PerformanceLog.timestamp.asc()).all()
        
        # Group logs by date
        daily_performance = {}
        for log in performance_logs:
            date_str = log.timestamp.date().isoformat()
            if date_str not in daily_performance:
                daily_performance[date_str] = []
            daily_performance[date_str].append(log.score)
        
        # Calculate daily averages
        trend_data = []
        for date_str, scores in daily_performance.items():
            avg_score = sum(scores) / len(scores)
            trend_data.append({
                "date": date_str,
                "average_score": avg_score,
                "attempts": len(scores),
                "total_score": sum(scores)
            })
        
        # Calculate overall trend
        if len(trend_data) >= 7:
            recent_avg = sum(t["average_score"] for t in trend_data[-7:]) / 7
            older_avg = sum(t["average_score"] for t in trend_data[:7]) / 7
            trend_direction = "improving" if recent_avg > older_avg else "declining" if recent_avg < older_avg else "stable"
        else:
            trend_direction = "insufficient_data"
        
        return jsonify({
            "trend_data": trend_data,
            "trend_direction": trend_direction,
            "analysis_period_days": days,
            "total_attempts": len(performance_logs),
            "overall_average": sum(log.score for log in performance_logs) / len(performance_logs) if performance_logs else 0
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get progress trends: {str(e)}'}), 500


@personalization_bp.get("/recommendations")
@jwt_required()
def get_personalized_recommendations():
    """Get personalized learning recommendations"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get comprehensive insights
        insights = personalization_engine.get_learning_insights(user_id)
        
        # Generate specific recommendations
        recommendations = []
        
        # Topic-based recommendations
        weak_topics = insights["topic_categories"]["weak"]
        if weak_topics:
            recommendations.append({
                "type": "focus_area",
                "priority": "high",
                "title": "Focus on Weak Areas",
                "description": f"Improve mastery in: {', '.join([t['topic'] for t in weak_topics[:3]])}",
                "action": "practice_weak_topics"
            })
        
        strong_topics = insights["topic_categories"]["strong"]
        if strong_topics:
            recommendations.append({
                "type": "advanced_challenge",
                "priority": "medium",
                "title": "Take Advanced Challenges",
                "description": f"Build on your strengths in: {', '.join([t['topic'] for t in strong_topics[:3]])}",
                "action": "advanced_exercises"
            })
        
        # Learning style recommendations
        learning_style = insights["learning_style"]
        if learning_style and learning_style.get("dominant_style") != "None":
            dominant_style = learning_style["dominant_style"]
            recommendations.append({
                "type": "learning_style",
                "priority": "medium",
                "title": f"Optimize for {dominant_style.title()} Learning",
                "description": f"Focus on {dominant_style}-based content for better retention",
                "action": f"use_{dominant_style}_content"
            })
        
        # Performance trend recommendations
        performance_trends = insights["performance_trends"]
        if performance_trends["trend"] == "declining":
            recommendations.append({
                "type": "motivation",
                "priority": "high",
                "title": "Rebuild Confidence",
                "description": "Consider reviewing easier material to rebuild confidence",
                "action": "easier_content"
            })
        elif performance_trends["trend"] == "improving":
            recommendations.append({
                "type": "challenge",
                "priority": "medium",
                "title": "Ready for More Challenge",
                "description": "Great progress! Try more challenging content",
                "action": "harder_content"
            })
        
        # Emotion-based recommendations
        emotion_patterns = insights["emotion_patterns"]
        if emotion_patterns["trend"] == "more_negative":
            recommendations.append({
                "type": "wellbeing",
                "priority": "high",
                "title": "Take Care of Your Learning Mood",
                "description": "Consider shorter sessions or breaks to maintain motivation",
                "action": "manage_stress"
            })
        
        return jsonify({
            "recommendations": recommendations,
            "total_count": len(recommendations),
            "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
            "insights_summary": {
                "total_topics": insights["mastery_summary"]["total_topics"],
                "average_mastery": insights["mastery_summary"]["average_mastery"],
                "dominant_learning_style": learning_style.get("dominant_style") if learning_style else "unknown",
                "performance_trend": performance_trends["trend"]
            }
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get recommendations: {str(e)}'}), 500
