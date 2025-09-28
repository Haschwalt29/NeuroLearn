from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import Content, UserProgress, User
from ..services.spaced_repetition import SpacedRepetitionEngine
from ..services.feedback_engine import PersonalizedFeedbackEngine
from ..services.learning_dna import LearningDNAEngine
from ..services.learning_style_service import LearningStyleService
from ..services.revision_service import RevisionService

spaced_bp = Blueprint("spaced_repetition", __name__)
engine = SpacedRepetitionEngine()
feedback_engine = PersonalizedFeedbackEngine()
dna_engine = LearningDNAEngine()
style_service = LearningStyleService()
revision_service = RevisionService()


@spaced_bp.get("/quiz/next")
@jwt_required()
def get_next_quiz():
    """Get next due content for spaced repetition review"""
    user_id = int(get_jwt_identity())
    limit = int(request.args.get('limit', 10))
    
    due_content = engine.get_due_content(user_id, limit)
    
    if not due_content:
        return jsonify({
            'message': 'No content due for review',
            'due_items': [],
            'stats': engine.get_learning_stats(user_id)
        })
    
    # Format response
    quiz_items = []
    for content, progress in due_content:
        quiz_items.append({
            'content_id': content.id,
            'topic': content.topic,
            'question': content.question,
            'difficulty': content.difficulty,
            'progress': {
                'repetitions': progress.repetitions,
                'ease_factor': progress.ease_factor,
                'interval_days': progress.interval_days,
                'last_reviewed': progress.last_reviewed.isoformat(),
                'next_review': progress.next_review.isoformat()
            }
        })
    
    return jsonify({
        'due_items': quiz_items,
        'stats': engine.get_learning_stats(user_id)
    })


@spaced_bp.post("/quiz/submit")
@jwt_required()
def submit_quiz_answer():
    """Submit quiz answer and update spaced repetition schedule"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    content_id = data.get('content_id')
    correct = data.get('correct')
    response_time_seconds = data.get('response_time_seconds', 0)
    confidence = data.get('confidence', 1.0)
    
    if content_id is None or correct is None:
        return jsonify({'error': 'content_id and correct are required'}), 400
    
    # Validate content exists
    content = Content.query.get(content_id)
    if not content:
        return jsonify({'error': 'Content not found'}), 404
    
    # Update progress with spaced repetition algorithm
    progress = engine.update_progress(
        user_id=user_id,
        content_id=content_id,
        correct=correct,
        response_time_seconds=response_time_seconds,
        confidence=confidence
    )
    
    # Generate personalized feedback
    try:
        feedback_data = feedback_engine.generate_feedback(user_id, f"content_{content_id}")
        feedback_included = True
    except Exception as e:
        feedback_data = {'error': f'Failed to generate feedback: {str(e)}'}
        feedback_included = False
    
    # Update Learning DNA profile
    try:
        dna_result = dna_engine.update_topic_mastery(
            user_id=user_id,
            topic=content.topic,
            score=score,
            time_spent=response_time_seconds,
            quiz_id=f"content_{content_id}"
        )
        dna_included = True
    except Exception as e:
        dna_result = {'error': f'Failed to update Learning DNA: {str(e)}'}
        dna_included = False
    
    # Update Learning Style (assume example-based for spaced repetition)
    try:
        style_result = style_service.update_learning_style(
            user_id=user_id,
            style="example",  # Spaced repetition is typically example-based
            performance_score=score,
            time_spent=response_time_seconds,
            engagement_score=confidence
        )
        style_included = True
    except Exception as e:
        style_result = {'error': f'Failed to update Learning Style: {str(e)}'}
        style_included = False
    
    # Update Revision Schedule
    try:
        # Convert score to quality score (0-5 scale)
        quality_score = score * 5.0  # Convert from 0-1 to 0-5
        
        # Get recent emotion for emotion hint
        recent_emotion = None
        if user.emotion_opt_in:
            from ..models import EmotionLog
            recent_emotion_log = EmotionLog.query.filter_by(user_id=user_id)\
                .order_by(EmotionLog.timestamp.desc()).first()
            if recent_emotion_log:
                recent_emotion = recent_emotion_log.emotion
        
        revision_result = revision_service.update_review_after_attempt(
            user_id=user_id,
            content_id=content_id,
            quality_score=quality_score,
            emotion_hint=recent_emotion,
            response_time=response_time_seconds
        )
        revision_included = True
    except Exception as e:
        revision_result = {'error': f'Failed to update Revision Schedule: {str(e)}'}
        revision_included = False
    
    # Check for story progress updates
    story_rewards = []
    try:
        from ..services.story_service import StoryService
        from ..models import StoryQuest, StoryProgress
        
        story_service = StoryService()
        
        # Find quests that might be related to this content
        related_quests = StoryQuest.query.filter(
            StoryQuest.topics.contains([content.topic])
        ).all()
        
        for quest in related_quests:
            # Check if user has completed this quest
            story_progress = StoryProgress.query.filter_by(
                user_id=user_id, story_id=quest.chapter.story_id
            ).first()
            
            if story_progress and quest.id not in story_progress.completed_quests:
                # Check if this performance qualifies for quest completion
                if quality_score >= 3:  # Good performance
                    story_result = story_service.update_story_progress(
                        user_id, quest.id, quality_score * 20, 0  # Convert to 0-100 scale
                    )
                    
                    if story_result.get("rewards"):
                        story_rewards.extend(story_result["rewards"])
                        
                        # Emit story progress update
                        socketio.emit("story_progress_update", {
                            "user_id": user_id,
                            "quest_id": quest.id,
                            "rewards": story_result["rewards"],
                            "timestamp": datetime.utcnow().isoformat()
                        }, room=str(user_id))
        
        story_included = True
    except Exception as e:
        story_rewards = []
        story_included = False
    
    # Emit real-time update
    socketio.emit('spaced_repetition_update', {
        'user_id': user_id,
        'content_id': content_id,
        'correct': correct,
        'new_interval': progress.interval_days,
        'new_ease_factor': progress.ease_factor,
        'repetitions': progress.repetitions,
        'next_review': progress.next_review.isoformat(),
        'feedback': feedback_data if feedback_included else None,
        'learning_dna': dna_result if dna_included else None,
        'learning_style': style_result if style_included else None,
        'revision_schedule': revision_result if revision_included else None
    })
    
    response_data = {
        'success': True,
        'progress': {
            'repetitions': progress.repetitions,
            'ease_factor': progress.ease_factor,
            'interval_days': progress.interval_days,
            'next_review': progress.next_review.isoformat(),
            'performance_score': progress.performance_score
        },
        'stats': engine.get_learning_stats(user_id)
    }
    
    # Include feedback if successfully generated
    if feedback_included and 'error' not in feedback_data:
        response_data['feedback'] = feedback_data
    
    # Include Learning DNA if successfully updated
    if dna_included and 'error' not in dna_result:
        response_data['learning_dna'] = dna_result
    
    # Include Learning Style if successfully updated
    if style_included and 'error' not in style_result:
        response_data['learning_style'] = style_result
    
    # Include Story Rewards if any were earned
    if story_rewards:
        response_data['story_rewards'] = story_rewards
    
    # Include Revision Schedule if successfully updated
    if revision_included and 'error' not in revision_result:
        response_data['revision_schedule'] = revision_result
    
    return jsonify(response_data)


@spaced_bp.get("/quiz/stats")
@jwt_required()
def get_learning_stats():
    """Get user's learning statistics"""
    user_id = int(get_jwt_identity())
    stats = engine.get_learning_stats(user_id)
    return jsonify(stats)


@spaced_bp.post("/content")
@jwt_required()
def create_content():
    """Create new learning content (for teachers/admin)"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Only teachers can create content
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can create content'}), 403
    
    data = request.get_json() or {}
    topic = data.get('topic')
    question = data.get('question')
    answer = data.get('answer')
    difficulty = data.get('difficulty', 0.5)
    
    if not all([topic, question, answer]):
        return jsonify({'error': 'topic, question, and answer are required'}), 400
    
    content = Content(
        topic=topic,
        question=question,
        answer=answer,
        difficulty=difficulty
    )
    
    db.session.add(content)
    db.session.commit()
    
    return jsonify({
        'id': content.id,
        'topic': content.topic,
        'question': content.question,
        'difficulty': content.difficulty,
        'created_at': content.created_at.isoformat()
    }), 201


@spaced_bp.get("/content")
@jwt_required()
def get_content():
    """Get all learning content"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    # Only teachers can view all content
    if user.role != 'teacher':
        return jsonify({'error': 'Only teachers can view all content'}), 403
    
    content_items = Content.query.all()
    
    return jsonify([{
        'id': c.id,
        'topic': c.topic,
        'question': c.question,
        'difficulty': c.difficulty,
        'created_at': c.created_at.isoformat()
    } for c in content_items])


@spaced_bp.get("/progress")
@jwt_required()
def get_user_progress():
    """Get user's progress for all content"""
    user_id = int(get_jwt_identity())
    
    progress_items = UserProgress.query.filter_by(user_id=user_id).all()
    
    result = []
    for progress in progress_items:
        content = Content.query.get(progress.content_id)
        if content:
            result.append({
                'content_id': content.id,
                'topic': content.topic,
                'question': content.question,
                'difficulty': content.difficulty,
                'progress': {
                    'repetitions': progress.repetitions,
                    'ease_factor': progress.ease_factor,
                    'interval_days': progress.interval_days,
                    'performance_score': progress.performance_score,
                    'last_reviewed': progress.last_reviewed.isoformat(),
                    'next_review': progress.next_review.isoformat()
                }
            })
    
    return jsonify(result)


@spaced_bp.get("/calendar")
@jwt_required()
def get_review_calendar():
    """Get upcoming reviews in calendar format"""
    user_id = int(get_jwt_identity())
    
    # Get next 30 days of reviews
    from datetime import datetime, timedelta
    now = datetime.utcnow()
    end_date = now + timedelta(days=30)
    
    upcoming_reviews = UserProgress.query.filter(
        UserProgress.user_id == user_id,
        UserProgress.next_review >= now,
        UserProgress.next_review <= end_date
    ).order_by(UserProgress.next_review.asc()).all()
    
    # Group by date
    calendar = {}
    for progress in upcoming_reviews:
        content = Content.query.get(progress.content_id)
        if content:
            date_key = progress.next_review.date().isoformat()
            if date_key not in calendar:
                calendar[date_key] = []
            calendar[date_key].append({
                'content_id': content.id,
                'topic': content.topic,
                'question': content.question,
                'difficulty': content.difficulty,
                'repetitions': progress.repetitions,
                'ease_factor': progress.ease_factor
            })
    
    return jsonify(calendar)
