from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models import RevisionSchedule, User, EmotionLog, Content
from .. import db


class RevisionService:
    """Service for managing auto-generated revision schedules using SM-2 algorithm"""
    
    def __init__(self):
        self.default_easiness_factor = 2.5
        self.min_easiness_factor = 1.3
        self.emotion_adjustments = {
            'frustrated': -0.1,
            'confused': -0.1,
            'angry': -0.1,
            'sad': -0.05,
            'happy': 0.05,
            'excited': 0.1,
            'confident': 0.1,
            'neutral': 0.0
        }
    
    def schedule_initial_review(self, user_id: int, content_id: int, topic: str) -> RevisionSchedule:
        """
        Create initial revision schedule for new content
        
        Args:
            user_id: User ID
            content_id: Content/Question ID
            topic: Topic name
            
        Returns:
            Created RevisionSchedule record
        """
        # Check if schedule already exists
        existing = RevisionSchedule.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if existing:
            return existing
        
        # Create new schedule
        schedule = RevisionSchedule(
            user_id=user_id,
            content_id=content_id,
            topic=topic,
            next_review=datetime.utcnow() + timedelta(days=1),  # Initial 1-day interval
            interval_days=1,
            easiness_factor=self.default_easiness_factor,
            repetitions=0,
            quality_scores=[],
            emotion_hints=[]
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        return schedule
    
    def update_review_after_attempt(self, user_id: int, content_id: int, 
                                  quality_score: float, emotion_hint: str = None,
                                  response_time: float = None) -> Dict:
        """
        Update revision schedule after user attempts a review using SM-2 algorithm
        
        Args:
            user_id: User ID
            content_id: Content ID
            quality_score: Quality score (0-5 scale)
            emotion_hint: Emotion detected during review
            response_time: Time taken to respond (seconds)
            
        Returns:
            Dictionary with updated schedule data
        """
        # Get or create schedule
        schedule = RevisionSchedule.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not schedule:
            # Get topic from content
            content = Content.query.get(content_id)
            topic = content.topic if content else "Unknown Topic"
            schedule = self.schedule_initial_review(user_id, content_id, topic)
        
        # Store quality score and emotion hint
        if not schedule.quality_scores:
            schedule.quality_scores = []
        if not schedule.emotion_hints:
            schedule.emotion_hints = []
        
        schedule.quality_scores.append({
            'score': quality_score,
            'timestamp': datetime.utcnow().isoformat(),
            'response_time': response_time
        })
        
        if emotion_hint:
            schedule.emotion_hints.append({
                'emotion': emotion_hint,
                'timestamp': datetime.utcnow().isoformat()
            })
        
        # Keep only last 10 entries
        schedule.quality_scores = schedule.quality_scores[-10:]
        schedule.emotion_hints = schedule.emotion_hints[-10:]
        
        # Apply emotion-aware adjustment to easiness factor
        emotion_adjustment = self._get_emotion_adjustment(emotion_hint)
        adjusted_easiness = schedule.easiness_factor + emotion_adjustment
        
        # SM-2 Algorithm Implementation
        if quality_score >= 3:  # Successful recall
            if schedule.repetitions == 0:
                schedule.interval_days = 1
            elif schedule.repetitions == 1:
                schedule.interval_days = 6
            else:
                schedule.interval_days = max(1, round(schedule.interval_days * adjusted_easiness))
            
            schedule.repetitions += 1
        else:  # Failed recall
            schedule.repetitions = 0
            schedule.interval_days = 1
        
        # Update easiness factor using SM-2 formula
        ef_calculation = adjusted_easiness + (0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02))
        schedule.easiness_factor = max(self.min_easiness_factor, ef_calculation)
        
        # Set next review date
        schedule.next_review = datetime.utcnow() + timedelta(days=schedule.interval_days)
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return {
            'schedule_id': schedule.id,
            'next_review': schedule.next_review.isoformat(),
            'interval_days': schedule.interval_days,
            'easiness_factor': schedule.easiness_factor,
            'repetitions': schedule.repetitions,
            'emotion_adjustment': emotion_adjustment,
            'quality_score': quality_score
        }
    
    def _get_emotion_adjustment(self, emotion_hint: str) -> float:
        """Get easiness factor adjustment based on emotion"""
        if not emotion_hint:
            return 0.0
        
        return self.emotion_adjustments.get(emotion_hint.lower(), 0.0)
    
    def get_due_reviews(self, user_id: int, date: datetime = None, limit: int = 50) -> List[Dict]:
        """
        Get all reviews due for a user
        
        Args:
            user_id: User ID
            date: Date to check against (default: now)
            limit: Maximum number of reviews to return
            
        Returns:
            List of due review records
        """
        if date is None:
            date = datetime.utcnow()
        
        schedules = RevisionSchedule.query.filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.next_review <= date
        ).order_by(RevisionSchedule.next_review.asc()).limit(limit).all()
        
        due_reviews = []
        for schedule in schedules:
            # Get content details
            content = Content.query.get(schedule.content_id)
            
            due_reviews.append({
                'schedule_id': schedule.id,
                'content_id': schedule.content_id,
                'topic': schedule.topic,
                'next_review': schedule.next_review.isoformat(),
                'interval_days': schedule.interval_days,
                'easiness_factor': schedule.easiness_factor,
                'repetitions': schedule.repetitions,
                'overdue_days': max(0, (date - schedule.next_review).days),
                'content': {
                    'question': content.question if content else "Content not found",
                    'answer': content.answer if content else "Answer not found",
                    'difficulty': content.difficulty if content else 0.5
                } if content else None
            })
        
        return due_reviews
    
    def get_review_calendar(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """
        Get reviews scheduled in a date range for calendar view
        
        Args:
            user_id: User ID
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Dictionary with reviews grouped by date
        """
        schedules = RevisionSchedule.query.filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.next_review >= start_date,
            RevisionSchedule.next_review <= end_date
        ).order_by(RevisionSchedule.next_review.asc()).all()
        
        calendar = {}
        for schedule in schedules:
            date_str = schedule.next_review.date().isoformat()
            if date_str not in calendar:
                calendar[date_str] = []
            
            content = Content.query.get(schedule.content_id)
            calendar[date_str].append({
                'schedule_id': schedule.id,
                'content_id': schedule.content_id,
                'topic': schedule.topic,
                'time': schedule.next_review.time().isoformat(),
                'interval_days': schedule.interval_days,
                'repetitions': schedule.repetitions,
                'content': {
                    'question': content.question if content else "Content not found",
                    'difficulty': content.difficulty if content else 0.5
                } if content else None
            })
        
        return calendar
    
    def force_reschedule(self, user_id: int, content_id: int, days: int) -> bool:
        """
        Manually reschedule a review (user-controlled)
        
        Args:
            user_id: User ID
            content_id: Content ID
            days: Days to add/subtract from current schedule
            
        Returns:
            True if successful, False otherwise
        """
        schedule = RevisionSchedule.query.filter_by(
            user_id=user_id, 
            content_id=content_id
        ).first()
        
        if not schedule:
            return False
        
        # Update next review date
        schedule.next_review = schedule.next_review + timedelta(days=days)
        schedule.updated_at = datetime.utcnow()
        
        db.session.commit()
        return True
    
    def snooze_review(self, user_id: int, content_id: int, days: int) -> bool:
        """
        Snooze a review for specified days
        
        Args:
            user_id: User ID
            content_id: Content ID
            days: Days to snooze
            
        Returns:
            True if successful, False otherwise
        """
        return self.force_reschedule(user_id, content_id, days)
    
    def get_revision_stats(self, user_id: int) -> Dict:
        """
        Get revision statistics for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with revision statistics
        """
        now = datetime.utcnow()
        
        # Get all schedules for user
        schedules = RevisionSchedule.query.filter_by(user_id=user_id).all()
        
        # Calculate statistics
        total_schedules = len(schedules)
        due_now = len([s for s in schedules if s.next_review <= now])
        overdue = len([s for s in schedules if s.next_review < now])
        
        # Calculate average easiness factor
        avg_easiness = sum(s.easiness_factor for s in schedules) / total_schedules if total_schedules > 0 else 0
        
        # Get recent activity (last 7 days)
        week_ago = now - timedelta(days=7)
        recent_activity = RevisionSchedule.query.filter(
            RevisionSchedule.user_id == user_id,
            RevisionSchedule.updated_at >= week_ago
        ).count()
        
        # Get topic distribution
        topic_counts = {}
        for schedule in schedules:
            topic_counts[schedule.topic] = topic_counts.get(schedule.topic, 0) + 1
        
        return {
            'total_schedules': total_schedules,
            'due_now': due_now,
            'overdue': overdue,
            'average_easiness_factor': round(avg_easiness, 2),
            'recent_activity': recent_activity,
            'topic_distribution': topic_counts,
            'next_review_date': min([s.next_review for s in schedules]).isoformat() if schedules else None
        }
    
    def get_emotion_insights(self, user_id: int) -> Dict:
        """
        Get insights based on emotion data in revision schedules
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with emotion insights
        """
        schedules = RevisionSchedule.query.filter_by(user_id=user_id).all()
        
        emotion_counts = {}
        emotion_performance = {}
        
        for schedule in schedules:
            if schedule.emotion_hints:
                for hint in schedule.emotion_hints:
                    emotion = hint['emotion']
                    emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                    
                    # Find corresponding quality score
                    for score_data in schedule.quality_scores:
                        if score_data['timestamp'] == hint['timestamp']:
                            if emotion not in emotion_performance:
                                emotion_performance[emotion] = []
                            emotion_performance[emotion].append(score_data['score'])
                            break
        
        # Calculate average performance per emotion
        avg_performance = {}
        for emotion, scores in emotion_performance.items():
            avg_performance[emotion] = sum(scores) / len(scores) if scores else 0
        
        # Generate insights
        insights = []
        if emotion_counts:
            dominant_emotion = max(emotion_counts, key=emotion_counts.get)
            insights.append(f"Most common emotion during reviews: {dominant_emotion}")
            
            if avg_performance:
                best_emotion = max(avg_performance, key=avg_performance.get)
                worst_emotion = min(avg_performance, key=avg_performance.get)
                insights.append(f"Best performance with: {best_emotion}")
                insights.append(f"Challenging emotions: {worst_emotion}")
        
        return {
            'emotion_counts': emotion_counts,
            'average_performance': avg_performance,
            'insights': insights
        }
