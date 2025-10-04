from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, RevisionSchedule, Content, PerformanceLog, EmotionLog
from ..services.revision_service import RevisionService

revision_bp = Blueprint("revision", __name__)
revision_service = RevisionService()


@revision_bp.get("/due")
@jwt_required()
def get_due_reviews():
    """Get due reviews for authenticated user (paginated)"""
    user_id = int(get_jwt_identity())
    
    # Get query parameters
    limit = int(request.args.get('limit', 20))
    overdue_only = request.args.get('overdue_only', 'false').lower() == 'true'
    
    try:
        due_reviews = revision_service.get_due_reviews(user_id, limit=limit)
        
        # Filter overdue if requested
        if overdue_only:
            now = datetime.utcnow()
            due_reviews = [r for r in due_reviews if r['overdue_days'] > 0]
        
        # Sort by priority: Overdue → Today → Soon
        due_reviews.sort(key=lambda x: (x['overdue_days'], x['next_review']))
        
        return jsonify({
            'due_reviews': due_reviews,
            'total_count': len(due_reviews),
            'overdue_count': len([r for r in due_reviews if r['overdue_days'] > 0])
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get due reviews: {str(e)}'}), 500


@revision_bp.post("/complete")
@jwt_required()
def complete_review():
    """Complete a review and update schedule"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    # Validate required fields
    content_id = data.get('content_id')
    quality_score = data.get('quality_score')
    
    if not content_id or quality_score is None:
        return jsonify({'error': 'content_id and quality_score are required'}), 400
    
    if not 0 <= quality_score <= 5:
        return jsonify({'error': 'quality_score must be between 0 and 5'}), 400
    
    try:
        # Optional fields
        emotion_hint = data.get('emotion_hint')
        response_time = data.get('response_time')
        
        # Update revision schedule
        schedule_result = revision_service.update_review_after_attempt(
            user_id=user_id,
            content_id=content_id,
            quality_score=quality_score,
            emotion_hint=emotion_hint,
            response_time=response_time
        )
        
        # Create performance log
        content = Content.query.get(content_id)
        performance_log = PerformanceLog(
            user_id=user_id,
            module=content.topic if content else "Unknown",
            question_id=content_id,
            correct=quality_score >= 3,  # Consider 3+ as correct
            score=quality_score / 5.0  # Convert to 0-1 scale
        )
        db.session.add(performance_log)
        db.session.commit()
        
        # Emit real-time updates
        socketio.emit('revision_update', {
            'user_id': user_id,
            'content_id': content_id,
            'quality_score': quality_score,
            'next_review': schedule_result['next_review'],
            'interval_days': schedule_result['interval_days'],
            'easiness_factor': schedule_result['easiness_factor'],
            'repetitions': schedule_result['repetitions'],
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        socketio.emit('performance_update', {
            'user_id': user_id,
            'module': content.topic if content else "Unknown",
            'score': quality_score / 5.0,
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'success': True,
            'schedule_result': schedule_result,
            'performance_log_id': performance_log.id
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to complete review: {str(e)}'}), 500


@revision_bp.get("/calendar")
@jwt_required()
def get_revision_calendar():
    """Get review items in date range for calendar view"""
    user_id = int(get_jwt_identity())
    
    # Get query parameters
    start_date_str = request.args.get('start')
    end_date_str = request.args.get('end')
    
    if not start_date_str or not end_date_str:
        return jsonify({'error': 'start and end date parameters are required'}), 400
    
    try:
        start_date = datetime.fromisoformat(start_date_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_date_str.replace('Z', '+00:00'))
        
        calendar = revision_service.get_review_calendar(user_id, start_date, end_date)
        
        return jsonify({
            'calendar': calendar,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'total_reviews': sum(len(reviews) for reviews in calendar.values())
        }), 200
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to get calendar: {str(e)}'}), 500


@revision_bp.post("/snooze")
@jwt_required()
def snooze_review():
    """Snooze a review for specified days"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    content_id = data.get('content_id')
    days = data.get('days')
    
    if not content_id or days is None:
        return jsonify({'error': 'content_id and days are required'}), 400
    
    if not isinstance(days, int) or days < 0:
        return jsonify({'error': 'days must be a non-negative integer'}), 400
    
    try:
        success = revision_service.snooze_review(user_id, content_id, days)
        
        if success:
            # Emit update
            socketio.emit('revision_snoozed', {
                'user_id': user_id,
                'content_id': content_id,
                'days': days,
                'timestamp': datetime.utcnow().isoformat()
            }, room=str(user_id))
            
            return jsonify({
                'success': True,
                'message': f'Review snoozed for {days} days'
            }), 200
        else:
            return jsonify({'error': 'Review schedule not found'}), 404
            
    except Exception as e:
        return jsonify({'error': f'Failed to snooze review: {str(e)}'}), 500


@revision_bp.get("/stats")
@jwt_required()
def get_revision_stats():
    """Get revision statistics for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        stats = revision_service.get_revision_stats(user_id)
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@revision_bp.get("/insights")
@jwt_required()
def get_emotion_insights():
    """Get emotion-based insights for revision performance"""
    user_id = int(get_jwt_identity())
    
    try:
        insights = revision_service.get_emotion_insights(user_id)
        return jsonify(insights), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get insights: {str(e)}'}), 500


@revision_bp.post("/schedule")
@jwt_required()
def schedule_initial_review():
    """Manually schedule initial review for content"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    content_id = data.get('content_id')
    topic = data.get('topic')
    
    if not content_id:
        return jsonify({'error': 'content_id is required'}), 400
    
    try:
        # Get topic from content if not provided
        if not topic:
            content = Content.query.get(content_id)
            if not content:
                return jsonify({'error': 'Content not found'}), 404
            topic = content.topic
        
        schedule = revision_service.schedule_initial_review(user_id, content_id, topic)
        
        return jsonify({
            'success': True,
            'schedule_id': schedule.id,
            'next_review': schedule.next_review.isoformat(),
            'topic': schedule.topic
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Failed to schedule review: {str(e)}'}), 500


@revision_bp.get("/schedule/<int:content_id>")
@jwt_required()
def get_content_schedule(content_id):
    """Get revision schedule for specific content"""
    user_id = int(get_jwt_identity())
    
    try:
        schedule = RevisionSchedule.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        content = Content.query.get(content_id)
        
        return jsonify({
            'schedule_id': schedule.id,
            'content_id': schedule.content_id,
            'topic': schedule.topic,
            'next_review': schedule.next_review.isoformat(),
            'interval_days': schedule.interval_days,
            'easiness_factor': schedule.easiness_factor,
            'repetitions': schedule.repetitions,
            'quality_scores': schedule.quality_scores,
            'emotion_hints': schedule.emotion_hints,
            'created_at': schedule.created_at.isoformat(),
            'updated_at': schedule.updated_at.isoformat(),
            'content': {
                'question': content.question if content else "Content not found",
                'answer': content.answer if content else "Answer not found",
                'difficulty': content.difficulty if content else 0.5
            } if content else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get schedule: {str(e)}'}), 500


@revision_bp.delete("/schedule/<int:content_id>")
@jwt_required()
def delete_content_schedule(content_id):
    """Delete revision schedule for specific content"""
    user_id = int(get_jwt_identity())
    
    try:
        schedule = RevisionSchedule.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not schedule:
            return jsonify({'error': 'Schedule not found'}), 404
        
        db.session.delete(schedule)
        db.session.commit()
        
        # Emit update
        socketio.emit('revision_deleted', {
            'user_id': user_id,
            'content_id': content_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            'success': True,
            'message': 'Schedule deleted successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to delete schedule: {str(e)}'}), 500
