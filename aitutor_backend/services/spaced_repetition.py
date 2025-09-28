from datetime import datetime, timedelta
from typing import Tuple, Optional, List
from ..models import UserProgress, Content, EmotionLog
from .. import db


class SpacedRepetitionEngine:
    """SM2 Algorithm implementation for spaced repetition learning"""
    
    def __init__(self):
        self.default_ease_factor = 2.5
        self.min_ease_factor = 1.3
        self.max_ease_factor = 3.0
        
    def calculate_quality_score(self, correct: bool, response_time_seconds: float, 
                               confidence: float = 1.0) -> float:
        """
        Calculate quality score (0-5) based on correctness, speed, and confidence
        
        Args:
            correct: Whether the answer was correct
            response_time_seconds: Time taken to answer
            confidence: User's confidence level (0-1)
            
        Returns:
            Quality score (0-5)
        """
        if not correct:
            return 0.0
            
        # Base score for correct answer
        base_score = 3.0
        
        # Speed bonus (faster = higher score)
        if response_time_seconds < 5:
            speed_bonus = 1.0
        elif response_time_seconds < 15:
            speed_bonus = 0.5
        elif response_time_seconds < 30:
            speed_bonus = 0.0
        else:
            speed_bonus = -0.5
            
        # Confidence bonus
        confidence_bonus = confidence * 1.0
        
        quality = base_score + speed_bonus + confidence_bonus
        return max(0.0, min(5.0, quality))
    
    def update_ease_factor(self, current_ease: float, quality: float) -> float:
        """
        Update ease factor based on SM2 algorithm
        
        Args:
            current_ease: Current ease factor
            quality: Quality score (0-5)
            
        Returns:
            New ease factor
        """
        if quality < 3:
            # Failed recall - decrease ease factor
            new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        else:
            # Successful recall - increase ease factor slightly
            new_ease = current_ease + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            
        return max(self.min_ease_factor, min(self.max_ease_factor, new_ease))
    
    def calculate_next_interval(self, current_interval: int, ease_factor: float, 
                              repetitions: int, quality: float) -> int:
        """
        Calculate next review interval in days
        
        Args:
            current_interval: Current interval in days
            ease_factor: Current ease factor
            repetitions: Number of successful repetitions
            quality: Quality score (0-5)
            
        Returns:
            Next interval in days
        """
        if quality < 3:
            # Failed - reset to 1 day
            return 1
        elif repetitions == 0:
            # First successful review
            return 1
        elif repetitions == 1:
            # Second successful review
            return 6
        else:
            # Subsequent reviews
            return max(1, int(current_interval * ease_factor))
    
    def get_emotion_adjustment(self, user_id: int, hours: int = 2) -> float:
        """
        Get emotion-based adjustment factor for spaced repetition
        
        Args:
            user_id: User ID
            hours: Hours to look back for emotions
            
        Returns:
            Adjustment factor (0.8-1.2)
        """
        since = datetime.utcnow() - timedelta(hours=hours)
        recent_emotions = EmotionLog.query.filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= since
        ).order_by(EmotionLog.timestamp.desc()).limit(5).all()
        
        if not recent_emotions:
            return 1.0
            
        # Calculate emotion-based adjustment
        positive_emotions = ['happy', 'surprise', 'neutral']
        negative_emotions = ['sad', 'angry', 'fear', 'disgust']
        
        positive_count = sum(1 for e in recent_emotions if e.emotion in positive_emotions)
        negative_count = sum(1 for e in recent_emotions if e.emotion in negative_emotions)
        
        total_emotions = len(recent_emotions)
        
        if total_emotions == 0:
            return 1.0
            
        positive_ratio = positive_count / total_emotions
        negative_ratio = negative_count / total_emotions
        
        # Adjust based on emotion patterns
        if negative_ratio > 0.6:
            # Mostly negative emotions - slow down learning
            return 0.8
        elif positive_ratio > 0.6:
            # Mostly positive emotions - speed up learning
            return 1.2
        else:
            # Mixed emotions - neutral adjustment
            return 1.0
    
    def update_progress(self, user_id: int, content_id: int, correct: bool, 
                       response_time_seconds: float, confidence: float = 1.0) -> UserProgress:
        """
        Update user progress with spaced repetition algorithm
        
        Args:
            user_id: User ID
            content_id: Content ID
            correct: Whether answer was correct
            response_time_seconds: Response time
            confidence: User confidence (0-1)
            
        Returns:
            Updated UserProgress object
        """
        # Get or create user progress
        progress = UserProgress.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                content_id=content_id,
                ease_factor=self.default_ease_factor,
                interval_days=1,
                repetitions=0,
                performance_score=0.0
            )
            db.session.add(progress)
        
        # Calculate quality score
        quality = self.calculate_quality_score(correct, response_time_seconds, confidence)
        
        # Get emotion adjustment
        emotion_adj = self.get_emotion_adjustment(user_id)
        
        # Update ease factor with emotion adjustment
        new_ease_factor = self.update_ease_factor(progress.ease_factor, quality)
        progress.ease_factor = new_ease_factor * emotion_adj
        progress.ease_factor = max(self.min_ease_factor, min(self.max_ease_factor, progress.ease_factor))
        
        # Update interval
        if correct:
            progress.repetitions += 1
            progress.interval_days = self.calculate_next_interval(
                progress.interval_days, 
                progress.ease_factor, 
                progress.repetitions, 
                quality
            )
        else:
            # Reset on failure
            progress.repetitions = 0
            progress.interval_days = 1
            
        # Update timestamps
        progress.last_reviewed = datetime.utcnow()
        progress.next_review = datetime.utcnow() + timedelta(days=progress.interval_days)
        progress.performance_score = quality
        
        db.session.commit()
        return progress
    
    def get_due_content(self, user_id: int, limit: int = 10) -> List[Tuple[Content, UserProgress]]:
        """
        Get content that is due for review
        
        Args:
            user_id: User ID
            limit: Maximum number of items to return
            
        Returns:
            List of (Content, UserProgress) tuples
        """
        now = datetime.utcnow()
        
        due_progress = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.next_review <= now
        ).order_by(UserProgress.next_review.asc()).limit(limit).all()
        
        result = []
        for progress in due_progress:
            content = Content.query.get(progress.content_id)
            if content:
                result.append((content, progress))
                
        return result
    
    def get_learning_stats(self, user_id: int) -> dict:
        """
        Get learning statistics for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with learning statistics
        """
        progress_items = UserProgress.query.filter_by(user_id=user_id).all()
        
        if not progress_items:
            return {
                'total_items': 0,
                'due_items': 0,
                'average_ease_factor': 2.5,
                'strong_topics': [],
                'weak_topics': []
            }
        
        now = datetime.utcnow()
        due_count = sum(1 for p in progress_items if p.next_review <= now)
        
        # Calculate topic performance
        topic_performance = {}
        for progress in progress_items:
            content = Content.query.get(progress.content_id)
            if content:
                topic = content.topic
                if topic not in topic_performance:
                    topic_performance[topic] = []
                topic_performance[topic].append(progress.performance_score)
        
        # Find strong and weak topics
        strong_topics = []
        weak_topics = []
        
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            if avg_score >= 4.0:
                strong_topics.append(topic)
            elif avg_score <= 2.0:
                weak_topics.append(topic)
        
        return {
            'total_items': len(progress_items),
            'due_items': due_count,
            'average_ease_factor': sum(p.ease_factor for p in progress_items) / len(progress_items),
            'strong_topics': strong_topics,
            'weak_topics': weak_topics,
            'topic_performance': {topic: sum(scores)/len(scores) for topic, scores in topic_performance.items()}
        }
