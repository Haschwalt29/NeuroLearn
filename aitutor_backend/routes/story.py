from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, Story, Chapter, StoryQuest, StoryProgress, StoryReward
from ..services.story_service import StoryService
from datetime import datetime

story_bp = Blueprint("story", __name__)
story_service = StoryService()


@story_bp.route("/current", methods=["GET"])
@jwt_required()
def get_current_story():
    """Get user's current story progress with unlocked content"""
    user_id = int(get_jwt_identity())
    
    try:
        result = story_service.get_current_story_progress(user_id)
        
        if "error" in result:
            return jsonify(result), 400
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get story progress",
            "details": str(e)
        }), 500


@story_bp.route("/progress", methods=["POST"])
@jwt_required()
def update_story_progress():
    """Update story progress when a quest is completed"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    quest_id = data.get("quest_id")
    score = data.get("score")
    time_spent = data.get("time_spent", 0)
    
    if not quest_id or score is None:
        return jsonify({
            "error": "quest_id and score are required"
        }), 400
    
    try:
        result = story_service.update_story_progress(
            user_id, quest_id, score, time_spent
        )
        
        if "error" in result:
            return jsonify(result), 400
        
        # Emit real-time updates
        socketio.emit("story_progress_update", {
            "user_id": user_id,
            "quest_id": quest_id,
            "score": score,
            "rewards": result.get("rewards", []),
            "timestamp": datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            "success": True,
            "data": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to update story progress",
            "details": str(e)
        }), 500


@story_bp.route("/rewards", methods=["GET"])
@jwt_required()
def get_story_rewards():
    """Get unviewed story rewards for the current user"""
    user_id = int(get_jwt_identity())
    story_id = request.args.get("story_id", type=int)
    
    if not story_id:
        return jsonify({
            "error": "story_id is required"
        }), 400
    
    try:
        rewards = story_service.get_story_rewards(user_id, story_id)
        
        return jsonify({
            "success": True,
            "rewards": rewards
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get story rewards",
            "details": str(e)
        }), 500


@story_bp.route("/rewards/<int:reward_id>/viewed", methods=["POST"])
@jwt_required()
def mark_reward_viewed(reward_id):
    """Mark a story reward as viewed"""
    user_id = int(get_jwt_identity())
    
    try:
        success = story_service.mark_reward_viewed(user_id, reward_id)
        
        if not success:
            return jsonify({
                "error": "Reward not found or access denied"
            }), 404
        
        return jsonify({
            "success": True,
            "message": "Reward marked as viewed"
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to mark reward as viewed",
            "details": str(e)
        }), 500


@story_bp.route("/chapters/<int:chapter_id>", methods=["GET"])
@jwt_required()
def get_chapter_details(chapter_id):
    """Get detailed information about a specific chapter"""
    user_id = int(get_jwt_identity())
    
    try:
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return jsonify({
                "error": "Chapter not found"
            }), 404
        
        # Check if user has access to this chapter
        story_progress = StoryProgress.query.filter_by(
            user_id=user_id, story_id=chapter.story_id
        ).first()
        
        if not story_progress:
            return jsonify({
                "error": "Story progress not found"
            }), 404
        
        if not story_service._is_chapter_unlocked(user_id, chapter, story_progress):
            return jsonify({
                "error": "Chapter not unlocked"
            }), 403
        
        chapter_data = story_service._format_chapter_data(chapter, story_progress)
        
        return jsonify({
            "success": True,
            "chapter": chapter_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get chapter details",
            "details": str(e)
        }), 500


@story_bp.route("/quests/<int:quest_id>", methods=["GET"])
@jwt_required()
def get_quest_details(quest_id):
    """Get detailed information about a specific quest"""
    user_id = int(get_jwt_identity())
    
    try:
        quest = StoryQuest.query.get(quest_id)
        if not quest:
            return jsonify({
                "error": "Quest not found"
            }), 404
        
        # Check if user has access to this quest
        story_progress = StoryProgress.query.filter_by(
            user_id=user_id, story_id=quest.chapter.story_id
        ).first()
        
        if not story_progress:
            return jsonify({
                "error": "Story progress not found"
            }), 404
        
        if not story_service._is_chapter_unlocked(user_id, quest.chapter, story_progress):
            return jsonify({
                "error": "Quest not unlocked"
            }), 403
        
        quest_data = story_service._format_quest_data(quest, story_progress)
        
        return jsonify({
            "success": True,
            "quest": quest_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get quest details",
            "details": str(e)
        }), 500


@story_bp.route("/stories", methods=["GET"])
@jwt_required()
def get_available_stories():
    """Get all available stories"""
    try:
        stories = Story.query.filter_by(is_active=True).order_by(Story.id).all()
        
        stories_data = [story_service._format_story_data(story) for story in stories]
        
        return jsonify({
            "success": True,
            "stories": stories_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to get available stories",
            "details": str(e)
        }), 500


@story_bp.route("/stories/<int:story_id>/start", methods=["POST"])
@jwt_required()
def start_story(story_id):
    """Start a new story for the user"""
    user_id = int(get_jwt_identity())
    
    try:
        story = Story.query.get(story_id)
        if not story or not story.is_active:
            return jsonify({
                "error": "Story not found or not available"
            }), 404
        
        # Check if user already has progress in this story
        existing_progress = StoryProgress.query.filter_by(
            user_id=user_id, story_id=story_id
        ).first()
        
        if existing_progress:
            return jsonify({
                "error": "Story already started"
            }), 400
        
        # Initialize story progress
        story_progress = story_service._initialize_story_progress(user_id, story_id)
        
        # Emit story start event
        socketio.emit("story_started", {
            "user_id": user_id,
            "story_id": story_id,
            "story_title": story.title,
            "timestamp": datetime.utcnow().isoformat()
        }, room=str(user_id))
        
        return jsonify({
            "success": True,
            "message": f"Started story: {story.title}",
            "story_progress": {
                "story_id": story_id,
                "current_chapter_id": story_progress.current_chapter_id,
                "total_story_xp": story_progress.total_story_xp
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Failed to start story",
            "details": str(e)
        }), 500
