from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import Quest, UserQuest, User, Badge
from ..services.quest_engine import QuestEngine

quests_bp = Blueprint("quests", __name__)
quest_engine = QuestEngine()


@quests_bp.get("/")
@jwt_required()
def get_available_quests():
    """Get quests available to user"""
    user_id = int(get_jwt_identity())
    
    try:
        quests = quest_engine.get_available_quests(user_id)
        return jsonify({
            "quests": quests,
            "total_count": len(quests)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get quests: {str(e)}'}), 500


@quests_bp.get("/progress")
@jwt_required()
def get_user_quest_progress():
    """Get user's quest progress"""
    user_id = int(get_jwt_identity())
    
    try:
        progress = quest_engine.get_user_quest_progress(user_id)
        return jsonify({
            "quest_progress": progress,
            "total_quests": len(progress)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get quest progress: {str(e)}'}), 500


@quests_bp.post("/start")
@jwt_required()
def start_quest():
    """Start a quest for user"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    quest_id = data.get('quest_id')
    
    if not quest_id:
        return jsonify({'error': 'Quest ID is required'}), 400
    
    try:
        result = quest_engine.start_quest(user_id, quest_id)
        
        if result.get('error'):
            return jsonify(result), 400
        
        # Emit real-time update
        socketio.emit('quest_started', {
            'user_id': user_id,
            'quest_id': quest_id,
            'status': result['status'],
            'deadline': result['deadline']
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to start quest: {str(e)}'}), 500


@quests_bp.post("/complete-task")
@jwt_required()
def complete_quest_task():
    """Complete a quest task"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    quest_id = data.get('quest_id')
    task_id = data.get('task_id')
    completion_data = data.get('completion_data', {})
    
    if not quest_id or not task_id:
        return jsonify({'error': 'Quest ID and Task ID are required'}), 400
    
    try:
        result = quest_engine.complete_quest_task(user_id, quest_id, task_id, completion_data)
        
        if result.get('error'):
            return jsonify(result), 400
        
        # Emit real-time update
        socketio.emit('quest_task_completed', {
            'user_id': user_id,
            'quest_id': quest_id,
            'task_id': task_id,
            'progress_percentage': result['progress_percentage'],
            'xp_earned': result['xp_earned'],
            'remaining_tasks': result['remaining_tasks']
        }, room=str(user_id))
        
        # If quest is completed, emit quest completion event
        if result.get('quest_completed'):
            socketio.emit('quest_completed', {
                'user_id': user_id,
                'quest_id': quest_id,
                'xp_earned': result['xp_earned'],
                'badge_earned': result.get('badge_earned'),
                'completion_time': result['completion_time']
            }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to complete quest task: {str(e)}'}), 500


@quests_bp.post("/generate")
@jwt_required()
def generate_quest_from_weaknesses():
    """Generate a quest based on user's weak topics"""
    user_id = int(get_jwt_identity())
    
    try:
        quest = quest_engine.generate_quest_from_weaknesses(user_id)
        
        if not quest:
            return jsonify({
                'message': 'No weak topics found to generate quest from',
                'quest': None
            }), 200
        
        quest_data = {
            "id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "story_theme": quest.story_theme,
            "difficulty": quest.difficulty,
            "category": quest.category,
            "required_topics": quest.required_topics,
            "required_tasks": quest.required_tasks,
            "xp_reward": quest.xp_reward,
            "estimated_duration": quest.estimated_duration
        }
        
        # Emit real-time update
        socketio.emit('quest_generated', {
            'user_id': user_id,
            'quest': quest_data
        }, room=str(user_id))
        
        return jsonify({
            'message': 'Quest generated successfully',
            'quest': quest_data
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to generate quest: {str(e)}'}), 500


@quests_bp.get("/active")
@jwt_required()
def get_active_quests():
    """Get user's active quests"""
    user_id = int(get_jwt_identity())
    
    try:
        active_quests = UserQuest.query.filter(
            UserQuest.user_id == user_id,
            UserQuest.status == "active"
        ).all()
        
        quests_data = []
        for user_quest in active_quests:
            quest = Quest.query.get(user_quest.quest_id)
            if quest:
                quests_data.append({
                    "id": quest.id,
                    "title": quest.title,
                    "description": quest.description,
                    "story_theme": quest.story_theme,
                    "difficulty": quest.difficulty,
                    "progress_percentage": user_quest.progress_percentage,
                    "completed_tasks": user_quest.completed_tasks or [],
                    "current_task_index": user_quest.current_task_index,
                    "started_at": user_quest.started_at.isoformat() if user_quest.started_at else None,
                    "deadline": user_quest.deadline.isoformat() if user_quest.deadline else None,
                    "required_tasks": quest.required_tasks,
                    "xp_reward": quest.xp_reward
                })
        
        return jsonify({
            "active_quests": quests_data,
            "total_active": len(quests_data)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get active quests: {str(e)}'}), 500


@quests_bp.get("/completed")
@jwt_required()
def get_completed_quests():
    """Get user's completed quests"""
    user_id = int(get_jwt_identity())
    
    try:
        completed_quests = UserQuest.query.filter(
            UserQuest.user_id == user_id,
            UserQuest.status == "completed"
        ).all()
        
        quests_data = []
        for user_quest in completed_quests:
            quest = Quest.query.get(user_quest.quest_id)
            if quest:
                quests_data.append({
                    "id": quest.id,
                    "title": quest.title,
                    "description": quest.description,
                    "story_theme": quest.story_theme,
                    "difficulty": quest.difficulty,
                    "completed_at": user_quest.completed_at.isoformat() if user_quest.completed_at else None,
                    "xp_earned": user_quest.xp_earned,
                    "badge_earned": user_quest.badge_earned_id
                })
        
        return jsonify({
            "completed_quests": quests_data,
            "total_completed": len(quests_data)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get completed quests: {str(e)}'}), 500


@quests_bp.get("/<int:quest_id>")
@jwt_required()
def get_quest_details(quest_id):
    """Get detailed information about a specific quest"""
    user_id = int(get_jwt_identity())
    
    try:
        quest = Quest.query.get(quest_id)
        if not quest:
            return jsonify({'error': 'Quest not found'}), 404
        
        # Get user's progress on this quest
        user_quest = UserQuest.query.filter_by(
            user_id=user_id,
            quest_id=quest_id
        ).first()
        
        quest_data = {
            "id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "story_theme": quest.story_theme,
            "difficulty": quest.difficulty,
            "category": quest.category,
            "required_topics": quest.required_topics,
            "required_tasks": quest.required_tasks,
            "prerequisites": quest.prerequisites,
            "xp_reward": quest.xp_reward,
            "estimated_duration": quest.estimated_duration,
            "is_repeatable": quest.is_repeatable,
            "created_at": quest.created_at.isoformat()
        }
        
        # Add badge reward info
        if quest.badge_reward_id:
            badge = Badge.query.get(quest.badge_reward_id)
            if badge:
                quest_data["badge_reward"] = {
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity
                }
        
        # Add user progress
        if user_quest:
            quest_data["user_progress"] = {
                "status": user_quest.status,
                "progress_percentage": user_quest.progress_percentage,
                "completed_tasks": user_quest.completed_tasks or [],
                "current_task_index": user_quest.current_task_index,
                "started_at": user_quest.started_at.isoformat() if user_quest.started_at else None,
                "deadline": user_quest.deadline.isoformat() if user_quest.deadline else None,
                "completed_at": user_quest.completed_at.isoformat() if user_quest.completed_at else None,
                "xp_earned": user_quest.xp_earned
            }
        else:
            quest_data["user_progress"] = None
        
        return jsonify(quest_data), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get quest details: {str(e)}'}), 500


@quests_bp.post("/abandon")
@jwt_required()
def abandon_quest():
    """Abandon an active quest"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    quest_id = data.get('quest_id')
    
    if not quest_id:
        return jsonify({'error': 'Quest ID is required'}), 400
    
    try:
        user_quest = UserQuest.query.filter_by(
            user_id=user_id,
            quest_id=quest_id,
            status="active"
        ).first()
        
        if not user_quest:
            return jsonify({'error': 'Active quest not found'}), 404
        
        # Mark quest as failed
        user_quest.status = "failed"
        user_quest.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        # Emit real-time update
        socketio.emit('quest_abandoned', {
            'user_id': user_id,
            'quest_id': quest_id,
            'progress_lost': user_quest.progress_percentage
        }, room=str(user_id))
        
        return jsonify({
            'success': True,
            'message': 'Quest abandoned successfully',
            'quest_id': quest_id
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to abandon quest: {str(e)}'}), 500


@quests_bp.get("/stats")
@jwt_required()
def get_quest_stats():
    """Get quest statistics for user"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get all user quests
        user_quests = UserQuest.query.filter_by(user_id=user_id).all()
        
        # Calculate stats
        total_quests = len(user_quests)
        active_quests = len([uq for uq in user_quests if uq.status == "active"])
        completed_quests = len([uq for uq in user_quests if uq.status == "completed"])
        failed_quests = len([uq for uq in user_quests if uq.status == "failed"])
        
        # Calculate total XP earned from quests
        total_xp_earned = sum(uq.xp_earned for uq in user_quests if uq.xp_earned)
        
        # Calculate average completion time
        completed_with_time = [uq for uq in user_quests 
                             if uq.status == "completed" and uq.started_at and uq.completed_at]
        
        if completed_with_time:
            total_time = sum((uq.completed_at - uq.started_at).total_seconds() 
                           for uq in completed_with_time)
            avg_completion_time = total_time / len(completed_with_time)
        else:
            avg_completion_time = 0
        
        # Get quest themes distribution
        quest_themes = {}
        for user_quest in user_quests:
            quest = Quest.query.get(user_quest.quest_id)
            if quest:
                theme = quest.story_theme
                quest_themes[theme] = quest_themes.get(theme, 0) + 1
        
        return jsonify({
            "total_quests": total_quests,
            "active_quests": active_quests,
            "completed_quests": completed_quests,
            "failed_quests": failed_quests,
            "completion_rate": (completed_quests / total_quests * 100) if total_quests > 0 else 0,
            "total_xp_earned": total_xp_earned,
            "average_completion_time_hours": avg_completion_time / 3600 if avg_completion_time > 0 else 0,
            "quest_themes": quest_themes
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get quest stats: {str(e)}'}), 500
