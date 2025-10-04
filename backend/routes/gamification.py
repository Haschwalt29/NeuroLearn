from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .. import db, socketio
from ..models import User, UserXP, UserStreak, UserBadge, Badge, XPTransaction
from ..services.gamification_service import GamificationService

gamification_bp = Blueprint("gamification", __name__)
gamification_service = GamificationService()


@gamification_bp.get("/status")
@jwt_required()
def get_gamification_status():
    """Get complete gamification status for user"""
    user_id = int(get_jwt_identity())
    
    try:
        status = gamification_service.get_gamification_status(user_id)
        return jsonify(status), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get gamification status: {str(e)}'}), 500


@gamification_bp.post("/initialize")
@jwt_required()
def initialize_gamification():
    """Initialize gamification data for user"""
    user_id = int(get_jwt_identity())
    
    try:
        result = gamification_service.initialize_user_gamification(user_id)
        
        # Emit real-time update
        socketio.emit('gamification_initialized', {
            'user_id': user_id,
            'xp_profile': result['xp_profile']
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to initialize gamification: {str(e)}'}), 500


@gamification_bp.post("/award-xp")
@jwt_required()
def award_xp():
    """Award XP to user"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    source = data.get('source')
    source_id = data.get('source_id')
    custom_amount = data.get('custom_amount')
    description = data.get('description')
    
    if not source:
        return jsonify({'error': 'Source is required'}), 400
    
    try:
        result = gamification_service.award_xp(
            user_id=user_id,
            source=source,
            source_id=source_id,
            custom_amount=custom_amount,
            description=description
        )
        
        # Emit real-time update
        socketio.emit('xp_awarded', {
            'user_id': user_id,
            'xp_awarded': result['xp_awarded'],
            'total_xp': result['total_xp'],
            'current_level': result['current_level'],
            'levels_gained': result['levels_gained'],
            'source': source
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to award XP: {str(e)}'}), 500


@gamification_bp.post("/update-streak")
@jwt_required()
def update_streak():
    """Update user streak"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    streak_type = data.get('streak_type')
    
    if not streak_type:
        return jsonify({'error': 'Streak type is required'}), 400
    
    try:
        result = gamification_service.update_streak(user_id, streak_type)
        
        # Emit real-time update
        socketio.emit('streak_updated', {
            'user_id': user_id,
            'streak_type': streak_type,
            'current_streak': result['current_streak'],
            'longest_streak': result['longest_streak'],
            'xp_bonus': result.get('xp_bonus', 0)
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to update streak: {str(e)}'}), 500


@gamification_bp.get("/badges")
@jwt_required()
def get_user_badges():
    """Get user's earned badges"""
    user_id = int(get_jwt_identity())
    
    try:
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        
        badges_data = []
        for user_badge in user_badges:
            badge = Badge.query.get(user_badge.badge_id)
            if badge:
                badges_data.append({
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity,
                    "category": badge.category,
                    "earned_at": user_badge.earned_at.isoformat(),
                    "xp_reward": badge.xp_reward
                })
        
        return jsonify({
            "badges": badges_data,
            "total_badges": len(badges_data)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get badges: {str(e)}'}), 500


@gamification_bp.post("/check-badges")
@jwt_required()
def check_and_award_badges():
    """Check for new badge achievements and award them"""
    user_id = int(get_jwt_identity())
    
    try:
        new_badges = gamification_service.check_and_award_badges(user_id)
        
        if new_badges:
            # Emit real-time update for each new badge
            for badge in new_badges:
                socketio.emit('badge_earned', {
                    'user_id': user_id,
                    'badge': badge
                }, room=str(user_id))
        
        return jsonify({
            "new_badges": new_badges,
            "count": len(new_badges)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to check badges: {str(e)}'}), 500


@gamification_bp.get("/leaderboard")
@jwt_required()
def get_leaderboard():
    """Get leaderboard of top users"""
    limit = int(request.args.get('limit', 10))
    
    try:
        leaderboard = gamification_service.get_leaderboard(limit)
        return jsonify({
            "leaderboard": leaderboard,
            "total_users": len(leaderboard)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get leaderboard: {str(e)}'}), 500


@gamification_bp.get("/transactions")
@jwt_required()
def get_xp_transactions():
    """Get user's XP transaction history"""
    user_id = int(get_jwt_identity())
    limit = int(request.args.get('limit', 20))
    
    try:
        transactions = XPTransaction.query.filter_by(user_id=user_id)\
            .order_by(XPTransaction.created_at.desc()).limit(limit).all()
        
        transactions_data = []
        for transaction in transactions:
            transactions_data.append({
                "id": transaction.id,
                "amount": transaction.amount,
                "source": transaction.source,
                "source_id": transaction.source_id,
                "description": transaction.description,
                "created_at": transaction.created_at.isoformat()
            })
        
        return jsonify({
            "transactions": transactions_data,
            "total_count": len(transactions_data)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get transactions: {str(e)}'}), 500


@gamification_bp.post("/freeze-streak")
@jwt_required()
def freeze_streak():
    """Freeze a user's streak"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    streak_type = data.get('streak_type')
    
    if not streak_type:
        return jsonify({'error': 'Streak type is required'}), 400
    
    try:
        result = gamification_service.freeze_streak(user_id, streak_type)
        
        # Emit real-time update
        socketio.emit('streak_frozen', {
            'user_id': user_id,
            'streak_type': streak_type,
            'current_streak': result['current_streak']
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to freeze streak: {str(e)}'}), 500


@gamification_bp.post("/unfreeze-streak")
@jwt_required()
def unfreeze_streak():
    """Unfreeze a user's streak"""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    
    streak_type = data.get('streak_type')
    
    if not streak_type:
        return jsonify({'error': 'Streak type is required'}), 400
    
    try:
        result = gamification_service.unfreeze_streak(user_id, streak_type)
        
        # Emit real-time update
        socketio.emit('streak_unfrozen', {
            'user_id': user_id,
            'streak_type': streak_type,
            'current_streak': result['current_streak']
        }, room=str(user_id))
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': f'Failed to unfreeze streak: {str(e)}'}), 500


@gamification_bp.get("/stats")
@jwt_required()
def get_gamification_stats():
    """Get gamification statistics for user"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            gamification_service.initialize_user_gamification(user_id)
            user_xp = UserXP.query.filter_by(user_id=user_id).first()
        
        # Get streak stats
        streaks = UserStreak.query.filter_by(user_id=user_id).all()
        streak_stats = {}
        for streak in streaks:
            streak_stats[streak.streak_type] = {
                "current": streak.current_streak,
                "longest": streak.longest_streak,
                "frozen": streak.streak_frozen
            }
        
        # Get badge count
        badge_count = UserBadge.query.filter_by(user_id=user_id).count()
        
        # Get recent activity
        recent_transactions = XPTransaction.query.filter_by(user_id=user_id)\
            .filter(XPTransaction.created_at >= datetime.utcnow() - timedelta(days=7)).count()
        
        return jsonify({
            "xp_profile": {
                "total_xp": user_xp.total_xp,
                "current_level": user_xp.current_level,
                "xp_to_next_level": user_xp.xp_to_next_level,
                "xp_in_current_level": user_xp.xp_in_current_level
            },
            "streak_stats": streak_stats,
            "badge_count": badge_count,
            "recent_activity": recent_transactions,
            "total_streak_days": sum(streak.current_streak for streak in streaks)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get stats: {str(e)}'}), 500


@gamification_bp.get("/achievements")
@jwt_required()
def get_achievements():
    """Get user's achievement summary"""
    user_id = int(get_jwt_identity())
    
    try:
        # Get XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            gamification_service.initialize_user_gamification(user_id)
            user_xp = UserXP.query.filter_by(user_id=user_id).first()
        
        # Get badges by category
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        badges_by_category = {}
        
        for user_badge in user_badges:
            badge = Badge.query.get(user_badge.badge_id)
            if badge:
                category = badge.category
                if category not in badges_by_category:
                    badges_by_category[category] = []
                badges_by_category[category].append({
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity,
                    "earned_at": user_badge.earned_at.isoformat()
                })
        
        # Get streak achievements
        streaks = UserStreak.query.filter_by(user_id=user_id).all()
        streak_achievements = []
        for streak in streaks:
            if streak.longest_streak >= 7:
                streak_achievements.append({
                    "type": streak.streak_type,
                    "days": streak.longest_streak,
                    "milestone": "weekly" if streak.longest_streak >= 7 else "monthly" if streak.longest_streak >= 30 else "daily"
                })
        
        return jsonify({
            "level": user_xp.current_level,
            "total_xp": user_xp.total_xp,
            "badges_by_category": badges_by_category,
            "streak_achievements": streak_achievements,
            "total_badges": len(user_badges),
            "total_streak_days": sum(streak.current_streak for streak in streaks)
        }), 200
    except Exception as e:
        return jsonify({'error': f'Failed to get achievements: {str(e)}'}), 500
