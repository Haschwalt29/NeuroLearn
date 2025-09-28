from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from ..models import (
    UserXP, UserStreak, UserBadge, Badge, XPTransaction,
    PerformanceLog, EmotionLog, TopicMastery, User
)
from .. import db


class GamificationService:
    """Service for managing gamification features"""
    
    def __init__(self):
        self.xp_sources = {
            "quiz_complete": 25,
            "lesson_complete": 50,
            "quest_task": 50,
            "quest_complete": 200,
            "badge_earned": 100,
            "streak_milestone": 75,
            "daily_login": 10,
            "emotion_achievement": 30,
            "mastery_milestone": 150
        }
        
        self.streak_types = ["daily_login", "daily_lesson", "quiz_streak"]
    
    def initialize_user_gamification(self, user_id: int) -> Dict:
        """Initialize gamification data for a new user"""
        # Create XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            user_xp = UserXP(user_id=user_id)
            db.session.add(user_xp)
        
        # Create streak tracking
        for streak_type in self.streak_types:
            existing_streak = UserStreak.query.filter_by(
                user_id=user_id, 
                streak_type=streak_type
            ).first()
            
            if not existing_streak:
                streak = UserStreak(
                    user_id=user_id,
                    streak_type=streak_type,
                    current_streak=0,
                    longest_streak=0
                )
                db.session.add(streak)
        
        db.session.commit()
        
        return {
            "success": True,
            "message": "Gamification initialized",
            "xp_profile": {
                "total_xp": user_xp.total_xp,
                "current_level": user_xp.current_level,
                "xp_to_next_level": user_xp.xp_to_next_level,
                "xp_in_current_level": user_xp.xp_in_current_level
            }
        }
    
    def award_xp(self, user_id: int, source: str, source_id: int = None, 
                custom_amount: int = None, description: str = None) -> Dict:
        """
        Award XP to user
        
        Args:
            user_id: User ID
            source: XP source type
            source_id: ID of the source object
            custom_amount: Custom XP amount (overrides default)
            description: Custom description
            
        Returns:
            Dictionary with XP award result
        """
        # Get XP amount
        amount = custom_amount or self.xp_sources.get(source, 0)
        if amount <= 0:
            return {"error": "Invalid XP amount"}
        
        # Get or create user XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            user_xp = UserXP(user_id=user_id)
            db.session.add(user_xp)
        
        # Add XP
        old_level = user_xp.current_level
        user_xp.total_xp += amount
        user_xp.xp_in_current_level += amount
        
        # Check for level up
        levels_gained = 0
        while user_xp.xp_in_current_level >= user_xp.xp_to_next_level:
            user_xp.xp_in_current_level -= user_xp.xp_to_next_level
            user_xp.current_level += 1
            levels_gained += 1
            
            # Calculate XP needed for next level (exponential growth)
            user_xp.xp_to_next_level = int(100 * (1.2 ** user_xp.current_level))
        
        # Record XP transaction
        transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description or f"XP from {source}"
        )
        db.session.add(transaction)
        
        db.session.commit()
        
        return {
            "success": True,
            "xp_awarded": amount,
            "total_xp": user_xp.total_xp,
            "current_level": user_xp.current_level,
            "levels_gained": levels_gained,
            "xp_to_next_level": user_xp.xp_to_next_level,
            "xp_in_current_level": user_xp.xp_in_current_level
        }
    
    def update_streak(self, user_id: int, streak_type: str) -> Dict:
        """
        Update user streak
        
        Args:
            user_id: User ID
            streak_type: Type of streak ("daily_login", "daily_lesson", "quiz_streak")
            
        Returns:
            Dictionary with streak update result
        """
        if streak_type not in self.streak_types:
            return {"error": "Invalid streak type"}
        
        today = date.today()
        
        # Get or create streak record
        streak = UserStreak.query.filter_by(
            user_id=user_id, 
            streak_type=streak_type
        ).first()
        
        if not streak:
            streak = UserStreak(
                user_id=user_id,
                streak_type=streak_type,
                current_streak=0,
                longest_streak=0
            )
            db.session.add(streak)
        
        # Check if streak is frozen
        if streak.streak_frozen:
            return {
                "success": True,
                "streak_frozen": True,
                "current_streak": streak.current_streak,
                "message": "Streak is frozen"
            }
        
        # Update streak
        if streak.last_activity_date == today:
            # Already updated today
            return {
                "success": True,
                "already_updated": True,
                "current_streak": streak.current_streak,
                "message": "Streak already updated today"
            }
        elif streak.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            streak.current_streak += 1
        else:
            # Streak broken
            streak.current_streak = 1
        
        # Update longest streak
        if streak.current_streak > streak.longest_streak:
            streak.longest_streak = streak.current_streak
        
        streak.last_activity_date = today
        db.session.commit()
        
        # Award XP for streak milestones
        xp_bonus = 0
        if streak.current_streak % 7 == 0:  # Weekly milestone
            xp_bonus = 50
        elif streak.current_streak % 30 == 0:  # Monthly milestone
            xp_bonus = 200
        
        if xp_bonus > 0:
            self.award_xp(user_id, "streak_milestone", streak.id, xp_bonus, 
                         f"{streak_type} streak milestone: {streak.current_streak} days")
        
        return {
            "success": True,
            "current_streak": streak.current_streak,
            "longest_streak": streak.longest_streak,
            "xp_bonus": xp_bonus,
            "message": f"Streak updated: {streak.current_streak} days"
        }
    
    def check_and_award_badges(self, user_id: int) -> List[Dict]:
        """
        Check for new badge achievements and award them
        
        Args:
            user_id: User ID
            
        Returns:
            List of newly awarded badges
        """
        new_badges = []
        
        # Get user's current badges
        user_badges = UserBadge.query.filter_by(user_id=user_id).all()
        user_badge_ids = [ub.badge_id for ub in user_badges]
        
        # Get all badges
        all_badges = Badge.query.all()
        
        for badge in all_badges:
            if badge.id in user_badge_ids:
                continue  # Already earned
            
            if self._check_badge_requirements(user_id, badge):
                # Award badge
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge.id,
                    progress_data=self._get_badge_progress_data(user_id, badge)
                )
                db.session.add(user_badge)
                
                # Award badge XP
                if badge.xp_reward > 0:
                    self.award_xp(user_id, "badge_earned", badge.id, badge.xp_reward, 
                                 f"Earned badge: {badge.name}")
                
                new_badges.append({
                    "id": badge.id,
                    "name": badge.name,
                    "description": badge.description,
                    "icon": badge.icon,
                    "rarity": badge.rarity,
                    "xp_reward": badge.xp_reward
                })
        
        db.session.commit()
        return new_badges
    
    def _check_badge_requirements(self, user_id: int, badge: Badge) -> bool:
        """Check if user meets badge requirements"""
        if not badge.requirements:
            return False
        
        requirements = badge.requirements
        
        # Check XP requirements
        if "min_xp" in requirements:
            user_xp = UserXP.query.filter_by(user_id=user_id).first()
            if not user_xp or user_xp.total_xp < requirements["min_xp"]:
                return False
        
        # Check level requirements
        if "min_level" in requirements:
            user_xp = UserXP.query.filter_by(user_id=user_id).first()
            if not user_xp or user_xp.current_level < requirements["min_level"]:
                return False
        
        # Check streak requirements
        if "streak_requirements" in requirements:
            for streak_type, min_streak in requirements["streak_requirements"].items():
                streak = UserStreak.query.filter_by(
                    user_id=user_id, 
                    streak_type=streak_type
                ).first()
                if not streak or streak.longest_streak < min_streak:
                    return False
        
        # Check mastery requirements
        if "mastery_requirements" in requirements:
            mastery_reqs = requirements["mastery_requirements"]
            for topic, min_mastery in mastery_reqs.items():
                topic_mastery = TopicMastery.query.filter_by(
                    user_id=user_id, 
                    topic=topic
                ).first()
                if not topic_mastery or topic_mastery.mastery_score < min_mastery:
                    return False
        
        # Check performance requirements
        if "performance_requirements" in requirements:
            perf_reqs = requirements["performance_requirements"]
            if "min_accuracy" in perf_reqs:
                # Calculate average accuracy from recent performance logs
                recent_logs = PerformanceLog.query.filter(
                    PerformanceLog.user_id == user_id,
                    PerformanceLog.timestamp >= datetime.utcnow() - timedelta(days=30)
                ).all()
                
                if len(recent_logs) < perf_reqs.get("min_attempts", 10):
                    return False
                
                avg_accuracy = sum(log.score for log in recent_logs) / len(recent_logs)
                if avg_accuracy < perf_reqs["min_accuracy"]:
                    return False
        
        return True
    
    def _get_badge_progress_data(self, user_id: int, badge: Badge) -> Dict:
        """Get progress data for badge achievement"""
        progress_data = {
            "earned_at": datetime.utcnow().isoformat(),
            "requirements_met": badge.requirements
        }
        
        # Add current stats
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if user_xp:
            progress_data["user_level"] = user_xp.current_level
            progress_data["total_xp"] = user_xp.total_xp
        
        return progress_data
    
    def get_gamification_status(self, user_id: int) -> Dict:
        """Get complete gamification status for user"""
        # Get XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            self.initialize_user_gamification(user_id)
            user_xp = UserXP.query.filter_by(user_id=user_id).first()
        
        # Get streaks
        streaks = UserStreak.query.filter_by(user_id=user_id).all()
        streak_data = {}
        for streak in streaks:
            streak_data[streak.streak_type] = {
                "current": streak.current_streak,
                "longest": streak.longest_streak,
                "last_activity": streak.last_activity_date.isoformat() if streak.last_activity_date else None,
                "frozen": streak.streak_frozen
            }
        
        # Get badges
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
                    "earned_at": user_badge.earned_at.isoformat()
                })
        
        # Get recent XP transactions
        recent_transactions = XPTransaction.query.filter_by(user_id=user_id)\
            .order_by(XPTransaction.created_at.desc()).limit(10).all()
        
        transactions_data = []
        for transaction in recent_transactions:
            transactions_data.append({
                "amount": transaction.amount,
                "source": transaction.source,
                "description": transaction.description,
                "created_at": transaction.created_at.isoformat()
            })
        
        return {
            "xp_profile": {
                "total_xp": user_xp.total_xp,
                "current_level": user_xp.current_level,
                "xp_to_next_level": user_xp.xp_to_next_level,
                "xp_in_current_level": user_xp.xp_in_current_level,
                "progress_percentage": (user_xp.xp_in_current_level / user_xp.xp_to_next_level) * 100
            },
            "streaks": streak_data,
            "badges": badges_data,
            "recent_transactions": transactions_data,
            "total_badges": len(badges_data),
            "total_streak_days": sum(streak.current_streak for streak in streaks)
        }
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Get leaderboard of top users by XP"""
        top_users = UserXP.query.order_by(UserXP.total_xp.desc()).limit(limit).all()
        
        leaderboard = []
        for i, user_xp in enumerate(top_users):
            user = User.query.get(user_xp.user_id)
            if user:
                leaderboard.append({
                    "rank": i + 1,
                    "user_id": user.id,
                    "name": user.name,
                    "total_xp": user_xp.total_xp,
                    "level": user_xp.current_level
                })
        
        return leaderboard
    
    def freeze_streak(self, user_id: int, streak_type: str) -> Dict:
        """Freeze a user's streak (prevent it from breaking)"""
        streak = UserStreak.query.filter_by(
            user_id=user_id, 
            streak_type=streak_type
        ).first()
        
        if not streak:
            return {"error": "Streak not found"}
        
        streak.streak_frozen = True
        db.session.commit()
        
        return {
            "success": True,
            "message": f"{streak_type} streak frozen",
            "current_streak": streak.current_streak
        }
    
    def unfreeze_streak(self, user_id: int, streak_type: str) -> Dict:
        """Unfreeze a user's streak"""
        streak = UserStreak.query.filter_by(
            user_id=user_id, 
            streak_type=streak_type
        ).first()
        
        if not streak:
            return {"error": "Streak not found"}
        
        streak.streak_frozen = False
        db.session.commit()
        
        return {
            "success": True,
            "message": f"{streak_type} streak unfrozen",
            "current_streak": streak.current_streak
        }
