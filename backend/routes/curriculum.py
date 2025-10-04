from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db
from ..models import User, CurriculumUpdate
from ..services.curriculum_service import curriculum_service
from ..services.curriculum_scheduler import curriculum_scheduler

curriculum_bp = Blueprint('curriculum', __name__)

@curriculum_bp.get('/updates')
@jwt_required()
def get_updates():
    """Get recent curriculum updates for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        limit = request.args.get('limit', 10, type=int)
        updates = curriculum_service.get_curriculum_updates(user_id, limit)
        
        return jsonify({
            'success': True,
            'updates': updates,
            'count': len(updates)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.post('/refresh')
@jwt_required()
def refresh_curriculum():
    """Manually trigger curriculum refresh (admin only)"""
    user_id = int(get_jwt_identity())
    
    try:
        # Check if user is admin
        user = User.query.get(user_id)
        if not user or user.role != 'teacher':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        # Trigger manual refresh
        curriculum_scheduler.manual_refresh()
        
        return jsonify({
            'success': True,
            'message': 'Curriculum refresh triggered successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.get('/path')
@jwt_required()
def get_learning_path():
    """Get user's current adaptive learning path"""
    user_id = int(get_jwt_identity())
    
    try:
        learning_path = curriculum_service.get_user_learning_path(user_id)
        
        return jsonify({
            'success': True,
            'learning_path': learning_path,
            'count': len(learning_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.post('/path/<int:lesson_id>/start')
@jwt_required()
def start_lesson(lesson_id):
    """Mark a lesson as started"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import LearningPath
        from datetime import datetime
        
        learning_path = LearningPath.query.filter_by(
            user_id=user_id,
            lesson_card_id=lesson_id
        ).first()
        
        if not learning_path:
            return jsonify({
                'success': False,
                'error': 'Lesson not found in learning path'
            }), 404
        
        learning_path.status = 'in-progress'
        learning_path.started_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Lesson started successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.post('/path/<int:lesson_id>/complete')
@jwt_required()
def complete_lesson(lesson_id):
    """Mark a lesson as completed"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import LearningPath
        from datetime import datetime
        
        learning_path = LearningPath.query.filter_by(
            user_id=user_id,
            lesson_card_id=lesson_id
        ).first()
        
        if not learning_path:
            return jsonify({
                'success': False,
                'error': 'Lesson not found in learning path'
            }), 404
        
        learning_path.status = 'completed'
        learning_path.completed_at = datetime.utcnow()
        learning_path.progress = 1.0
        db.session.commit()
        
        # Trigger curriculum update for this user
        curriculum_service.update_learning_paths(user_id)
        
        return jsonify({
            'success': True,
            'message': 'Lesson completed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.post('/path/<int:lesson_id>/progress')
@jwt_required()
def update_lesson_progress(lesson_id):
    """Update lesson progress"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    try:
        from ..models import LearningPath
        
        progress = data.get('progress', 0.0)
        if not 0.0 <= progress <= 1.0:
            return jsonify({
                'success': False,
                'error': 'Progress must be between 0.0 and 1.0'
            }), 400
        
        learning_path = LearningPath.query.filter_by(
            user_id=user_id,
            lesson_card_id=lesson_id
        ).first()
        
        if not learning_path:
            return jsonify({
                'success': False,
                'error': 'Lesson not found in learning path'
            }), 404
        
        learning_path.progress = progress
        
        # Auto-complete if progress is 100%
        if progress >= 1.0:
            learning_path.status = 'completed'
            from datetime import datetime
            learning_path.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.get('/fresh-lessons')
@jwt_required()
def get_fresh_lessons():
    """Get fresh lessons added in the last 7 days"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import LearningPath, LessonCard
        from datetime import datetime, timedelta
        
        # Get lessons added in the last 7 days
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        fresh_lessons = db.session.query(LearningPath, LessonCard).join(
            LessonCard, LearningPath.lesson_card_id == LessonCard.id
        ).filter(
            LearningPath.user_id == user_id,
            LearningPath.added_at > cutoff_date
        ).order_by(LearningPath.added_at.desc()).all()
        
        lessons_data = []
        for learning_path, lesson in fresh_lessons:
            lessons_data.append({
                'id': learning_path.id,
                'lesson_id': lesson.id,
                'title': lesson.title,
                'summary': lesson.summary,
                'status': learning_path.status,
                'added_at': learning_path.added_at.isoformat(),
                'estimated_time': lesson.estimated_time,
                'difficulty': lesson.difficulty_score,
                'tags': lesson.tags,
                'is_new': True,
                'replacement_reason': learning_path.replacement_reason
            })
        
        return jsonify({
            'success': True,
            'fresh_lessons': lessons_data,
            'count': len(lessons_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.get('/stats')
@jwt_required()
def get_curriculum_stats():
    """Get curriculum statistics for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        from ..models import LearningPath, LessonCard
        from datetime import datetime, timedelta
        
        # Get learning path stats
        total_lessons = LearningPath.query.filter_by(user_id=user_id).count()
        completed_lessons = LearningPath.query.filter_by(user_id=user_id, status='completed').count()
        in_progress_lessons = LearningPath.query.filter_by(user_id=user_id, status='in-progress').count()
        upcoming_lessons = LearningPath.query.filter_by(user_id=user_id, status='upcoming').count()
        
        # Get fresh lessons count
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        fresh_lessons_count = LearningPath.query.join(LessonCard).filter(
            LearningPath.user_id == user_id,
            LearningPath.added_at > cutoff_date
        ).count()
        
        # Get recent updates
        recent_updates = CurriculumUpdate.query.filter_by(user_id=user_id).order_by(
            CurriculumUpdate.created_at.desc()
        ).limit(5).all()
        
        updates_data = []
        for update in recent_updates:
            updates_data.append({
                'type': update.update_type,
                'message': update.message,
                'created_at': update.created_at.isoformat(),
                'is_read': update.is_read
            })
        
        return jsonify({
            'success': True,
            'stats': {
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons,
                'in_progress_lessons': in_progress_lessons,
                'upcoming_lessons': upcoming_lessons,
                'fresh_lessons': fresh_lessons_count,
                'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            },
            'recent_updates': updates_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@curriculum_bp.post('/updates/<int:update_id>/read')
@jwt_required()
def mark_update_read(update_id):
    """Mark a curriculum update as read"""
    user_id = int(get_jwt_identity())
    
    try:
        update = CurriculumUpdate.query.filter_by(
            id=update_id,
            user_id=user_id
        ).first()
        
        if not update:
            return jsonify({
                'success': False,
                'error': 'Update not found'
            }), 404
        
        update.is_read = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Update marked as read'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
