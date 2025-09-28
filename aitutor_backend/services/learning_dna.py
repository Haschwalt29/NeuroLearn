from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models import LearningProgress, TopicMastery, LearningBadge, User
from .. import db


class LearningDNAEngine:
    """Engine for calculating and managing Learning DNA profiles"""
    
    def __init__(self):
        self.mastery_levels = {
            'beginner': (0, 25),
            'intermediate': (25, 60),
            'advanced': (60, 85),
            'expert': (85, 100)
        }
        
        # Decay rates (per day)
        self.decay_rates = {
            'beginner': 0.02,      # 2% per day
            'intermediate': 0.015,  # 1.5% per day
            'advanced': 0.01,      # 1% per day
            'expert': 0.005        # 0.5% per day
        }
    
    def calculate_mastery_score(self, correct_attempts: int, total_attempts: int, 
                              previous_score: float = 0.0, days_since_last: int = 0) -> float:
        """
        Calculate mastery score with decay over time
        
        Args:
            correct_attempts: Number of correct attempts
            total_attempts: Total number of attempts
            previous_score: Previous mastery score
            days_since_last: Days since last attempt
            
        Returns:
            New mastery score (0-100)
        """
        if total_attempts == 0:
            return 0.0
        
        # Base mastery calculation
        base_mastery = (correct_attempts / total_attempts) * 100
        
        # Apply decay if there's a gap in learning
        if days_since_last > 0 and previous_score > 0:
            # Determine decay rate based on current level
            current_level = self._get_mastery_level(previous_score)
            decay_rate = self.decay_rates.get(current_level, 0.01)
            
            # Apply exponential decay
            decay_factor = (1 - decay_rate) ** days_since_last
            decayed_score = previous_score * decay_factor
            
            # Use weighted average of new performance and decayed score
            # Recent performance gets more weight
            recent_weight = min(0.7, total_attempts / 10)  # More attempts = more weight
            base_mastery = (base_mastery * recent_weight) + (decayed_score * (1 - recent_weight))
        
        return max(0.0, min(100.0, base_mastery))
    
    def _get_mastery_level(self, score: float) -> str:
        """Get mastery level based on score"""
        for level, (min_score, max_score) in self.mastery_levels.items():
            if min_score <= score < max_score:
                return level
        return 'expert' if score >= 100 else 'beginner'
    
    def update_topic_mastery(self, user_id: int, topic: str, score: float, 
                           time_spent: int = None, quiz_id: str = None) -> Dict:
        """
        Update topic mastery after a quiz/lesson completion
        
        Args:
            user_id: User ID
            topic: Topic name
            score: Score (0.0 to 1.0)
            time_spent: Time spent in seconds
            quiz_id: Quiz/lesson identifier
            
        Returns:
            Dictionary with updated mastery data
        """
        # Create or get existing mastery record
        mastery = TopicMastery.query.filter_by(user_id=user_id, topic=topic).first()
        
        if not mastery:
            mastery = TopicMastery(
                user_id=user_id,
                topic=topic,
                mastery_score=0.0,
                total_attempts=0,
                correct_attempts=0,
                streak_count=0,
                mastery_level='beginner'
            )
            db.session.add(mastery)
        
        # Calculate days since last update
        days_since_last = 0
        if mastery.last_updated:
            days_since_last = (datetime.utcnow() - mastery.last_updated).days
        
        # Update attempt counts
        mastery.total_attempts += 1
        if score >= 0.6:  # Consider 60%+ as correct
            mastery.correct_attempts += 1
        
        # Calculate new mastery score
        old_score = mastery.mastery_score
        mastery.mastery_score = self.calculate_mastery_score(
            mastery.correct_attempts,
            mastery.total_attempts,
            old_score,
            days_since_last
        )
        
        # Update mastery level
        mastery.mastery_level = self._get_mastery_level(mastery.mastery_score)
        
        # Update streak count
        if mastery.mastery_score > old_score:
            mastery.streak_count += 1
        else:
            mastery.streak_count = 0
        
        mastery.last_updated = datetime.utcnow()
        
        # Create progress record
        progress = LearningProgress(
            user_id=user_id,
            quiz_id=quiz_id,
            topic=topic,
            score=score,
            attempts=1,
            time_spent=time_spent,
            correct_answers=1 if score >= 0.6 else 0,
            total_questions=1
        )
        db.session.add(progress)
        
        db.session.commit()
        
        # Check for badges
        badges_earned = self._check_badges(user_id, topic, mastery)
        
        return {
            'mastery_score': mastery.mastery_score,
            'mastery_level': mastery.mastery_level,
            'streak_count': mastery.streak_count,
            'total_attempts': mastery.total_attempts,
            'correct_attempts': mastery.correct_attempts,
            'improvement': mastery.mastery_score - old_score,
            'badges_earned': badges_earned
        }
    
    def _check_badges(self, user_id: int, topic: str, mastery: TopicMastery) -> List[Dict]:
        """Check and award badges for achievements"""
        badges_earned = []
        
        # Mastery 100% badge
        if mastery.mastery_score >= 100 and mastery.mastery_score < 100.1:  # Just reached 100%
            badge = LearningBadge(
                user_id=user_id,
                badge_type='mastery_100',
                badge_name=f'🎯 {topic} Master',
                topic=topic,
                badge_data={'mastery_score': mastery.mastery_score}
            )
            db.session.add(badge)
            badges_earned.append({
                'type': 'mastery_100',
                'name': f'🎯 {topic} Master',
                'description': f'Reached 100% mastery in {topic}!'
            })
        
        # Streak badges
        if mastery.streak_count == 3:
            badge = LearningBadge(
                user_id=user_id,
                badge_type='streak_3',
                badge_name='🔥 Hot Streak',
                topic=topic,
                badge_data={'streak_count': mastery.streak_count}
            )
            db.session.add(badge)
            badges_earned.append({
                'type': 'streak_3',
                'name': '🔥 Hot Streak',
                'description': f'3 consecutive improvements in {topic}!'
            })
        
        if mastery.streak_count == 5:
            badge = LearningBadge(
                user_id=user_id,
                badge_type='streak_5',
                badge_name='🚀 Learning Rocket',
                topic=topic,
                badge_data={'streak_count': mastery.streak_count}
            )
            db.session.add(badge)
            badges_earned.append({
                'type': 'streak_5',
                'name': '🚀 Learning Rocket',
                'description': f'5 consecutive improvements in {topic}!'
            })
        
        # Level up badges
        if mastery.mastery_level == 'intermediate' and mastery.total_attempts == 5:
            badge = LearningBadge(
                user_id=user_id,
                badge_type='level_intermediate',
                badge_name='📈 Rising Star',
                topic=topic,
                badge_data={'level': mastery.mastery_level}
            )
            db.session.add(badge)
            badges_earned.append({
                'type': 'level_intermediate',
                'name': '📈 Rising Star',
                'description': f'Reached intermediate level in {topic}!'
            })
        
        db.session.commit()
        return badges_earned
    
    def get_learning_dna_profile(self, user_id: int) -> Dict:
        """Get complete Learning DNA profile for a user"""
        # Get all topic mastery records
        mastery_records = TopicMastery.query.filter_by(user_id=user_id).all()
        
        # Get recent progress (last 30 days)
        since = datetime.utcnow() - timedelta(days=30)
        recent_progress = LearningProgress.query.filter(
            LearningProgress.user_id == user_id,
            LearningProgress.timestamp >= since
        ).order_by(LearningProgress.timestamp.desc()).all()
        
        # Get badges
        badges = LearningBadge.query.filter_by(user_id=user_id).order_by(LearningBadge.earned_at.desc()).all()
        
        # Analyze strengths and weaknesses
        strengths = []
        weaknesses = []
        improving_topics = []
        
        for mastery in mastery_records:
            if mastery.mastery_score >= 80:
                strengths.append({
                    'topic': mastery.topic,
                    'score': mastery.mastery_score,
                    'level': mastery.mastery_level,
                    'streak': mastery.streak_count
                })
            elif mastery.mastery_score < 40:
                weaknesses.append({
                    'topic': mastery.topic,
                    'score': mastery.mastery_score,
                    'level': mastery.mastery_level,
                    'attempts': mastery.total_attempts
                })
            
            if mastery.streak_count >= 2:
                improving_topics.append({
                    'topic': mastery.topic,
                    'score': mastery.mastery_score,
                    'streak': mastery.streak_count
                })
        
        # Calculate overall statistics
        total_topics = len(mastery_records)
        avg_mastery = sum(m.mastery_score for m in mastery_records) / total_topics if total_topics > 0 else 0
        
        # Get learning velocity (improvement over time)
        learning_velocity = self._calculate_learning_velocity(recent_progress)
        
        return {
            'user_id': user_id,
            'total_topics': total_topics,
            'average_mastery': avg_mastery,
            'strengths': strengths,
            'weaknesses': weaknesses,
            'improving_topics': improving_topics,
            'learning_velocity': learning_velocity,
            'recent_badges': [{
                'name': badge.badge_name,
                'type': badge.badge_type,
                'topic': badge.topic,
                'earned_at': badge.earned_at.isoformat()
            } for badge in badges[:5]],  # Last 5 badges
            'topic_mastery': [{
                'topic': mastery.topic,
                'score': mastery.mastery_score,
                'level': mastery.mastery_level,
                'streak': mastery.streak_count,
                'total_attempts': mastery.total_attempts,
                'last_updated': mastery.last_updated.isoformat()
            } for mastery in mastery_records]
        }
    
    def _calculate_learning_velocity(self, recent_progress: List[LearningProgress]) -> Dict:
        """Calculate learning velocity (rate of improvement)"""
        if len(recent_progress) < 2:
            return {'velocity': 0, 'trend': 'stable'}
        
        # Group by topic and calculate improvement
        topic_improvements = {}
        for progress in recent_progress:
            if progress.topic not in topic_improvements:
                topic_improvements[progress.topic] = []
            topic_improvements[progress.topic].append(progress.score)
        
        # Calculate average improvement per topic
        improvements = []
        for topic, scores in topic_improvements.items():
            if len(scores) >= 2:
                improvement = scores[0] - scores[-1]  # Latest - oldest
                improvements.append(improvement)
        
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0
        
        if avg_improvement > 0.1:
            trend = 'accelerating'
        elif avg_improvement < -0.1:
            trend = 'declining'
        else:
            trend = 'stable'
        
        return {
            'velocity': avg_improvement,
            'trend': trend,
            'topics_tracked': len(topic_improvements)
        }
    
    def get_topic_mastery_history(self, user_id: int, topic: str, days: int = 30) -> List[Dict]:
        """Get mastery history for a specific topic"""
        since = datetime.utcnow() - timedelta(days=days)
        
        progress_records = LearningProgress.query.filter(
            LearningProgress.user_id == user_id,
            LearningProgress.topic == topic,
            LearningProgress.timestamp >= since
        ).order_by(LearningProgress.timestamp.asc()).all()
        
        # Calculate mastery over time
        mastery_history = []
        current_mastery = TopicMastery.query.filter_by(user_id=user_id, topic=topic).first()
        
        if current_mastery:
            # Simulate mastery progression based on progress records
            running_correct = 0
            running_total = 0
            
            for progress in progress_records:
                running_total += 1
                if progress.score >= 0.6:
                    running_correct += 1
                
                mastery_score = (running_correct / running_total) * 100 if running_total > 0 else 0
                
                mastery_history.append({
                    'date': progress.timestamp.isoformat(),
                    'mastery_score': mastery_score,
                    'score': progress.score,
                    'time_spent': progress.time_spent
                })
        
        return mastery_history
