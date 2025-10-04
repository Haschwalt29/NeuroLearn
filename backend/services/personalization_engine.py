from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models import (
    TopicMastery, PerformanceLog, EmotionLog, LearningStyle,
    Content, User, UserXP, UserStreak
)
from .. import db


class PersonalizationEngine:
    """Engine for personalizing learning experiences"""
    
    def __init__(self):
        self.mastery_thresholds = {
            "weak": 40.0,
            "improving": 60.0,
            "strong": 80.0,
            "expert": 95.0
        }
        
        self.emotion_weights = {
            "happy": 1.2,
            "confident": 1.1,
            "neutral": 1.0,
            "confused": 0.8,
            "frustrated": 0.6,
            "sad": 0.7,
            "angry": 0.5
        }
    
    def update_mastery_profile(self, user_id: int, topic: str, 
                             performance_score: float, emotion_hint: str = None) -> Dict:
        """
        Update user's mastery profile based on performance and emotion
        
        Args:
            user_id: User ID
            topic: Topic name
            performance_score: Performance score (0.0 to 1.0)
            emotion_hint: Detected emotion
            
        Returns:
            Dictionary with updated mastery data
        """
        # Get or create topic mastery record
        topic_mastery = TopicMastery.query.filter_by(
            user_id=user_id, 
            topic=topic
        ).first()
        
        if not topic_mastery:
            topic_mastery = TopicMastery(
                user_id=user_id,
                topic=topic,
                mastery_score=0.0,
                total_attempts=0,
                correct_attempts=0,
                streak_count=0,
                mastery_level="beginner"
            )
            db.session.add(topic_mastery)
        
        # Apply emotion-based adjustment
        emotion_multiplier = self.emotion_weights.get(emotion_hint, 1.0) if emotion_hint else 1.0
        adjusted_score = performance_score * emotion_multiplier
        
        # Update mastery score using weighted average
        total_attempts = topic_mastery.total_attempts + 1
        correct_attempts = topic_mastery.correct_attempts + (1 if adjusted_score >= 0.6 else 0)
        
        # Calculate new mastery score
        if total_attempts == 1:
            new_mastery = adjusted_score * 100
        else:
            # Weighted average with recent performance having more weight
            recent_weight = 0.3
            historical_weight = 0.7
            
            new_mastery = (adjusted_score * 100 * recent_weight) + \
                         (topic_mastery.mastery_score * historical_weight)
        
        # Update mastery record
        topic_mastery.mastery_score = min(100.0, max(0.0, new_mastery))
        topic_mastery.total_attempts = total_attempts
        topic_mastery.correct_attempts = correct_attempts
        topic_mastery.last_updated = datetime.utcnow()
        
        # Update streak count
        if adjusted_score >= 0.6:
            topic_mastery.streak_count += 1
        else:
            topic_mastery.streak_count = 0
        
        # Update mastery level
        topic_mastery.mastery_level = self._get_mastery_level(topic_mastery.mastery_score)
        
        db.session.commit()
        
        return {
            "topic": topic,
            "mastery_score": topic_mastery.mastery_score,
            "mastery_level": topic_mastery.mastery_level,
            "total_attempts": topic_mastery.total_attempts,
            "correct_attempts": topic_mastery.correct_attempts,
            "streak_count": topic_mastery.streak_count,
            "emotion_adjustment": emotion_multiplier
        }
    
    def _get_mastery_level(self, mastery_score: float) -> str:
        """Get mastery level based on score"""
        if mastery_score >= self.mastery_thresholds["expert"]:
            return "expert"
        elif mastery_score >= self.mastery_thresholds["strong"]:
            return "strong"
        elif mastery_score >= self.mastery_thresholds["improving"]:
            return "improving"
        else:
            return "weak"
    
    def get_learning_insights(self, user_id: int) -> Dict:
        """
        Get comprehensive learning insights for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with learning insights
        """
        # Get topic mastery data
        topic_masteries = TopicMastery.query.filter_by(user_id=user_id).all()
        
        # Categorize topics
        weak_topics = []
        improving_topics = []
        strong_topics = []
        
        for mastery in topic_masteries:
            if mastery.mastery_score < self.mastery_thresholds["weak"]:
                weak_topics.append({
                    "topic": mastery.topic,
                    "score": mastery.mastery_score,
                    "attempts": mastery.total_attempts,
                    "streak": mastery.streak_count
                })
            elif mastery.mastery_score < self.mastery_thresholds["improving"]:
                improving_topics.append({
                    "topic": mastery.topic,
                    "score": mastery.mastery_score,
                    "attempts": mastery.total_attempts,
                    "streak": mastery.streak_count
                })
            else:
                strong_topics.append({
                    "topic": mastery.topic,
                    "score": mastery.mastery_score,
                    "attempts": mastery.total_attempts,
                    "streak": mastery.streak_count
                })
        
        # Get learning style data
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        style_data = None
        if learning_style:
            style_data = {
                "visual_score": learning_style.visual_score,
                "auditory_score": learning_style.auditory_score,
                "example_score": learning_style.example_score,
                "dominant_style": learning_style.dominant_style,
                "total_attempts": learning_style.total_attempts
            }
        
        # Get recent performance trends
        recent_logs = PerformanceLog.query.filter(
            PerformanceLog.user_id == user_id,
            PerformanceLog.timestamp >= datetime.utcnow() - timedelta(days=30)
        ).order_by(PerformanceLog.timestamp.desc()).all()
        
        performance_trends = self._analyze_performance_trends(recent_logs)
        
        # Get emotion patterns
        emotion_patterns = self._analyze_emotion_patterns(user_id)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            weak_topics, improving_topics, strong_topics, 
            style_data, performance_trends, emotion_patterns
        )
        
        return {
            "mastery_summary": {
                "total_topics": len(topic_masteries),
                "weak_topics": len(weak_topics),
                "improving_topics": len(improving_topics),
                "strong_topics": len(strong_topics),
                "average_mastery": sum(m.mastery_score for m in topic_masteries) / len(topic_masteries) if topic_masteries else 0
            },
            "topic_categories": {
                "weak": weak_topics,
                "improving": improving_topics,
                "strong": strong_topics
            },
            "learning_style": style_data,
            "performance_trends": performance_trends,
            "emotion_patterns": emotion_patterns,
            "recommendations": recommendations
        }
    
    def _analyze_performance_trends(self, performance_logs: List[PerformanceLog]) -> Dict:
        """Analyze performance trends from recent logs"""
        if not performance_logs:
            return {"trend": "no_data", "average_score": 0, "improvement_rate": 0}
        
        # Calculate average score
        total_score = sum(log.score for log in performance_logs)
        average_score = total_score / len(performance_logs)
        
        # Calculate improvement trend
        if len(performance_logs) >= 10:
            recent_scores = [log.score for log in performance_logs[:5]]
            older_scores = [log.score for log in performance_logs[-5:]]
            
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            improvement_rate = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
        else:
            improvement_rate = 0
        
        # Determine trend
        if improvement_rate > 0.1:
            trend = "improving"
        elif improvement_rate < -0.1:
            trend = "declining"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_score": average_score,
            "improvement_rate": improvement_rate,
            "total_attempts": len(performance_logs)
        }
    
    def _analyze_emotion_patterns(self, user_id: int) -> Dict:
        """Analyze emotion patterns from recent logs"""
        recent_emotions = EmotionLog.query.filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).order_by(EmotionLog.timestamp.desc()).all()
        
        if not recent_emotions:
            return {"dominant_emotion": "neutral", "emotion_distribution": {}, "trend": "no_data"}
        
        # Count emotions
        emotion_counts = {}
        for emotion_log in recent_emotions:
            emotion = emotion_log.emotion
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Find dominant emotion
        dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
        
        # Calculate emotion trend (simplified)
        if len(recent_emotions) >= 5:
            recent_emotions_list = [log.emotion for log in recent_emotions[:3]]
            older_emotions_list = [log.emotion for log in recent_emotions[-3:]]
            
            positive_emotions = ["happy", "confident", "excited"]
            recent_positive = sum(1 for e in recent_emotions_list if e in positive_emotions)
            older_positive = sum(1 for e in older_emotions_list if e in positive_emotions)
            
            if recent_positive > older_positive:
                trend = "more_positive"
            elif recent_positive < older_positive:
                trend = "more_negative"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "dominant_emotion": dominant_emotion,
            "emotion_distribution": emotion_counts,
            "trend": trend,
            "total_logs": len(recent_emotions)
        }
    
    def _generate_recommendations(self, weak_topics: List, improving_topics: List, 
                                 strong_topics: List, style_data: Dict, 
                                 performance_trends: Dict, emotion_patterns: Dict) -> List[str]:
        """Generate personalized learning recommendations"""
        recommendations = []
        
        # Topic-based recommendations
        if weak_topics:
            weak_topic_names = [topic["topic"] for topic in weak_topics[:3]]
            recommendations.append(f"Focus on improving these weak areas: {', '.join(weak_topic_names)}")
        
        if improving_topics:
            recommendations.append(f"Great progress! Keep practicing {improving_topics[0]['topic']} to reach mastery level")
        
        if strong_topics:
            strong_topic_names = [topic["topic"] for topic in strong_topics[:3]]
            recommendations.append(f"Excellent mastery in: {', '.join(strong_topic_names)}. Consider advanced challenges!")
        
        # Learning style recommendations
        if style_data and style_data.get("dominant_style") != "None":
            dominant_style = style_data["dominant_style"]
            if dominant_style == "visual":
                recommendations.append("Try visual learning aids like diagrams and charts for better understanding")
            elif dominant_style == "auditory":
                recommendations.append("Consider audio lectures or reading content aloud for better retention")
            elif dominant_style == "example":
                recommendations.append("Focus on practical examples and hands-on exercises")
        
        # Performance trend recommendations
        if performance_trends["trend"] == "declining":
            recommendations.append("Consider taking a break or reviewing easier material to rebuild confidence")
        elif performance_trends["trend"] == "improving":
            recommendations.append("Great improvement! You're ready for more challenging content")
        
        # Emotion-based recommendations
        if emotion_patterns["trend"] == "more_negative":
            recommendations.append("Consider shorter study sessions or easier topics to maintain motivation")
        elif emotion_patterns["trend"] == "more_positive":
            recommendations.append("Your positive mood is great for learning! Try tackling challenging topics")
        
        return recommendations
    
    def generate_custom_exercises(self, user_id: int, topic: str = None) -> List[Dict]:
        """
        Generate custom exercises based on user's weaknesses and learning style
        
        Args:
            user_id: User ID
            topic: Specific topic (optional)
            
        Returns:
            List of custom exercise recommendations
        """
        # Get user's weak topics
        if topic:
            weak_topics = TopicMastery.query.filter(
                TopicMastery.user_id == user_id,
                TopicMastery.topic == topic,
                TopicMastery.mastery_score < self.mastery_thresholds["weak"]
            ).all()
        else:
            weak_topics = TopicMastery.query.filter(
                TopicMastery.user_id == user_id,
                TopicMastery.mastery_score < self.mastery_thresholds["weak"]
            ).all()
        
        if not weak_topics:
            return []
        
        # Get learning style
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        dominant_style = learning_style.dominant_style if learning_style else "example"
        
        # Get available content
        content_items = Content.query.filter(
            Content.topic.in_([t.topic for t in weak_topics])
        ).all()
        
        exercises = []
        for content_item in content_items:
            # Create exercise based on learning style
            exercise = {
                "id": content_item.id,
                "topic": content_item.topic,
                "question": content_item.question,
                "difficulty": content_item.difficulty,
                "type": self._get_exercise_type(dominant_style),
                "estimated_time": self._estimate_exercise_time(content_item.difficulty),
                "priority": self._calculate_exercise_priority(content_item, weak_topics)
            }
            exercises.append(exercise)
        
        # Sort by priority
        exercises.sort(key=lambda x: x["priority"], reverse=True)
        
        return exercises[:5]  # Return top 5 exercises
    
    def _get_exercise_type(self, learning_style: str) -> str:
        """Get exercise type based on learning style"""
        if learning_style == "visual":
            return "diagram_analysis"
        elif learning_style == "auditory":
            return "audio_explanation"
        else:
            return "practical_example"
    
    def _estimate_exercise_time(self, difficulty: float) -> int:
        """Estimate exercise completion time in minutes"""
        return int(5 + (difficulty * 15))  # 5-20 minutes
    
    def _calculate_exercise_priority(self, content: Content, weak_topics: List) -> float:
        """Calculate exercise priority based on topic weakness"""
        topic_mastery = next((t for t in weak_topics if t.topic == content.topic), None)
        if not topic_mastery:
            return 0.5
        
        # Higher priority for weaker topics
        weakness_factor = (self.mastery_thresholds["weak"] - topic_mastery.mastery_score) / self.mastery_thresholds["weak"]
        
        # Adjust by difficulty (easier exercises for weaker topics)
        difficulty_factor = 1.0 - content.difficulty if topic_mastery.mastery_score < 20 else content.difficulty
        
        return weakness_factor * difficulty_factor
    
    def get_spaced_repetition_schedule(self, user_id: int) -> Dict:
        """
        Get spaced repetition schedule for user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with revision schedule
        """
        # Get topics that need review (mastery < 80%)
        review_topics = TopicMastery.query.filter(
            TopicMastery.user_id == user_id,
            TopicMastery.mastery_score < 80.0
        ).order_by(TopicMastery.mastery_score.asc()).all()
        
        # Get revision schedules
        from ..models import RevisionSchedule
        revision_schedules = RevisionSchedule.query.filter_by(user_id=user_id).all()
        
        # Organize by priority
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for topic_mastery in review_topics:
            if topic_mastery.mastery_score < 30:
                high_priority.append(topic_mastery.topic)
            elif topic_mastery.mastery_score < 60:
                medium_priority.append(topic_mastery.topic)
            else:
                low_priority.append(topic_mastery.topic)
        
        # Get upcoming reviews
        upcoming_reviews = []
        for schedule in revision_schedules:
            if schedule.next_review <= datetime.utcnow() + timedelta(days=7):
                upcoming_reviews.append({
                    "topic": schedule.topic,
                    "next_review": schedule.next_review.isoformat(),
                    "interval_days": schedule.interval_days,
                    "priority": "high" if schedule.topic in high_priority else "medium"
                })
        
        return {
            "review_priorities": {
                "high": high_priority,
                "medium": medium_priority,
                "low": low_priority
            },
            "upcoming_reviews": upcoming_reviews,
            "total_topics_needing_review": len(review_topics),
            "next_review_date": min([s.next_review for s in revision_schedules]).isoformat() if revision_schedules else None
        }
