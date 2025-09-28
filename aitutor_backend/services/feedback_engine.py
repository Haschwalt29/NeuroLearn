from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models import User, PerformanceLog, EmotionLog, UserProgress, FeedbackLog, Content
from .. import db


class PersonalizedFeedbackEngine:
    """Generates personalized feedback based on performance, emotions, and learning history"""
    
    def __init__(self):
        self.feedback_templates = {
            'encouragement': {
                'high_performance': [
                    "🎉 Outstanding work! You're mastering this topic beautifully!",
                    "🌟 Excellent performance! Your understanding is really solid!",
                    "🚀 Fantastic job! You're making great progress!"
                ],
                'medium_performance': [
                    "👍 Good effort! You're on the right track!",
                    "💪 Keep it up! You're building strong foundations!",
                    "✨ Nice work! Every step forward counts!"
                ],
                'low_performance': [
                    "💪 Don't worry, learning takes time! You've got this!",
                    "🌟 Every expert was once a beginner. Keep going!",
                    "🎯 Focus on understanding, not perfection. You're doing great!"
                ]
            },
            'weak_areas': {
                'specific_topics': "I noticed you struggled with {topics}. Let's focus on these areas:",
                'general_difficulty': "Some concepts seemed challenging. Here's how we can improve:",
                'time_management': "Take your time with these topics - understanding is more important than speed."
            },
            'next_steps': {
                'retry_easy': "🔄 Let's review some easier examples to build confidence!",
                'practice_more': "📚 Try a few more practice problems to reinforce your learning!",
                'move_harder': "🎯 Ready for a challenge? Let's try some harder problems!",
                'spaced_review': "⏰ I'll remind you to review this in a few days to help it stick!",
                'break_time': "☕ Take a short break and come back refreshed!"
            },
            'emotion_adaptive': {
                'frustrated': {
                    'tone': 'gentle',
                    'suggestions': ['break_time', 'retry_easy'],
                    'messages': [
                        "I can see this is challenging. That's completely normal!",
                        "Learning can be tough sometimes. You're doing great by persisting!",
                        "Take a deep breath. Every challenge makes you stronger!"
                    ]
                },
                'bored': {
                    'tone': 'motivating',
                    'suggestions': ['move_harder', 'practice_more'],
                    'messages': [
                        "Ready for something more exciting? Let's level up!",
                        "You've got this down! Time for a new challenge!",
                        "Your skills are growing! Let's tackle something more interesting!"
                    ]
                },
                'happy': {
                    'tone': 'celebratory',
                    'suggestions': ['move_harder', 'spaced_review'],
                    'messages': [
                        "Your enthusiasm is contagious! Keep that energy going!",
                        "I love seeing you enjoy learning! This is how mastery happens!",
                        "Your positive attitude is your superpower! Keep shining!"
                    ]
                },
                'focused': {
                    'tone': 'encouraging',
                    'suggestions': ['practice_more', 'spaced_review'],
                    'messages': [
                        "Your focus is impressive! This is how real learning happens!",
                        "I can see you're really concentrating. That's the key to success!",
                        "Your dedication is paying off! Keep this momentum going!"
                    ]
                }
            }
        }
    
    def get_recent_emotions(self, user_id: int, hours: int = 2) -> List[Dict]:
        """Get recent emotions for context"""
        since = datetime.utcnow() - timedelta(hours=hours)
        emotions = EmotionLog.query.filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= since
        ).order_by(EmotionLog.timestamp.desc()).limit(10).all()
        
        return [{
            'emotion': e.emotion,
            'confidence': e.confidence,
            'timestamp': e.timestamp.isoformat()
        } for e in emotions]
    
    def get_performance_summary(self, user_id: int, lesson_id: str = None, hours: int = 2) -> Dict:
        """Get performance summary for recent activity"""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # Get recent performance logs
        query = PerformanceLog.query.filter(
            PerformanceLog.user_id == user_id,
            PerformanceLog.timestamp >= since
        )
        
        if lesson_id:
            query = query.filter(PerformanceLog.module == lesson_id)
            
        recent_logs = query.all()
        
        if not recent_logs:
            return {
                'total_questions': 0,
                'correct_answers': 0,
                'accuracy': 0.0,
                'average_score': 0.0,
                'average_time': 0.0,
                'topics_covered': [],
                'weak_topics': [],
                'strong_topics': []
            }
        
        total_questions = len(recent_logs)
        correct_answers = sum(1 for log in recent_logs if log.correct)
        accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        # Calculate average score
        scores = [log.score for log in recent_logs if log.score is not None]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        # Analyze topics
        topic_performance = {}
        for log in recent_logs:
            topic = log.module
            if topic not in topic_performance:
                topic_performance[topic] = {'correct': 0, 'total': 0}
            topic_performance[topic]['total'] += 1
            if log.correct:
                topic_performance[topic]['correct'] += 1
        
        # Identify strong and weak topics
        strong_topics = []
        weak_topics = []
        topics_covered = list(topic_performance.keys())
        
        for topic, perf in topic_performance.items():
            topic_accuracy = (perf['correct'] / perf['total']) * 100
            if topic_accuracy >= 80:
                strong_topics.append(topic)
            elif topic_accuracy < 60:
                weak_topics.append(topic)
        
        return {
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'average_score': average_score,
            'topics_covered': topics_covered,
            'weak_topics': weak_topics,
            'strong_topics': strong_topics,
            'topic_performance': topic_performance
        }
    
    def get_learning_trends(self, user_id: int, days: int = 7) -> Dict:
        """Get learning trends over time"""
        since = datetime.utcnow() - timedelta(days=days)
        
        # Get performance logs over time
        logs = PerformanceLog.query.filter(
            PerformanceLog.user_id == user_id,
            PerformanceLog.timestamp >= since
        ).order_by(PerformanceLog.timestamp.asc()).all()
        
        if not logs:
            return {
                'improvement_trend': 'stable',
                'consistency_score': 0.0,
                'streak_days': 0,
                'total_sessions': 0
            }
        
        # Calculate daily performance
        daily_performance = {}
        for log in logs:
            date = log.timestamp.date()
            if date not in daily_performance:
                daily_performance[date] = {'correct': 0, 'total': 0}
            daily_performance[date]['total'] += 1
            if log.correct:
                daily_performance[date]['correct'] += 1
        
        # Calculate improvement trend
        daily_accuracies = []
        for date in sorted(daily_performance.keys()):
            perf = daily_performance[date]
            accuracy = (perf['correct'] / perf['total']) * 100 if perf['total'] > 0 else 0
            daily_accuracies.append(accuracy)
        
        # Determine trend
        if len(daily_accuracies) >= 3:
            recent_avg = sum(daily_accuracies[-3:]) / 3
            early_avg = sum(daily_accuracies[:3]) / 3
            if recent_avg > early_avg + 5:
                improvement_trend = 'improving'
            elif recent_avg < early_avg - 5:
                improvement_trend = 'declining'
            else:
                improvement_trend = 'stable'
        else:
            improvement_trend = 'stable'
        
        # Calculate consistency (lower variance = more consistent)
        if len(daily_accuracies) > 1:
            mean_acc = sum(daily_accuracies) / len(daily_accuracies)
            variance = sum((acc - mean_acc) ** 2 for acc in daily_accuracies) / len(daily_accuracies)
            consistency_score = max(0, 100 - variance)  # Higher score = more consistent
        else:
            consistency_score = 100.0
        
        # Calculate streak
        streak_days = 0
        current_date = datetime.utcnow().date()
        for i in range(days):
            check_date = current_date - timedelta(days=i)
            if check_date in daily_performance:
                perf = daily_performance[check_date]
                if perf['total'] > 0 and (perf['correct'] / perf['total']) >= 0.6:
                    streak_days += 1
                else:
                    break
            else:
                break
        
        return {
            'improvement_trend': improvement_trend,
            'consistency_score': consistency_score,
            'streak_days': streak_days,
            'total_sessions': len(daily_performance)
        }
    
    def determine_dominant_emotion(self, emotions: List[Dict]) -> str:
        """Determine the dominant emotion from recent emotions"""
        if not emotions:
            return 'neutral'
        
        # Count emotions
        emotion_counts = {}
        for emotion_data in emotions:
            emotion = emotion_data['emotion']
            confidence = emotion_data['confidence']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + confidence
        
        # Return most frequent emotion
        return max(emotion_counts.items(), key=lambda x: x[1])[0]
    
    def generate_feedback(self, user_id: int, lesson_id: str = None) -> Dict:
        """Generate personalized feedback for a user"""
        # Get user
        user = User.query.get(user_id)
        if not user:
            return {'error': 'User not found'}
        
        # Gather data
        emotions = self.get_recent_emotions(user_id)
        performance = self.get_performance_summary(user_id, lesson_id)
        trends = self.get_learning_trends(user_id)
        dominant_emotion = self.determine_dominant_emotion(emotions)
        
        # Generate feedback components
        feedback_parts = []
        
        # 1. Encouragement based on performance
        if performance['accuracy'] >= 80:
            encouragement = self._get_random_template('encouragement', 'high_performance')
        elif performance['accuracy'] >= 60:
            encouragement = self._get_random_template('encouragement', 'medium_performance')
        else:
            encouragement = self._get_random_template('encouragement', 'low_performance')
        
        feedback_parts.append(encouragement)
        
        # 2. Address weak areas
        if performance['weak_topics']:
            weak_feedback = self.feedback_templates['weak_areas']['specific_topics'].format(
                topics=', '.join(performance['weak_topics'])
            )
            feedback_parts.append(weak_feedback)
        
        # 3. Emotion-adaptive message
        emotion_context = self.feedback_templates['emotion_adaptive'].get(dominant_emotion, {})
        if emotion_context:
            emotion_message = self._get_random_from_list(emotion_context.get('messages', []))
            if emotion_message:
                feedback_parts.append(emotion_message)
        
        # 4. Next steps based on performance and emotion
        next_steps = self._determine_next_steps(performance, dominant_emotion, trends)
        feedback_parts.append(next_steps)
        
        # 5. Learning trend insights
        if trends['improvement_trend'] == 'improving':
            feedback_parts.append("📈 I can see you're getting better every day! Keep up the great work!")
        elif trends['streak_days'] >= 3:
            feedback_parts.append(f"🔥 Amazing {trends['streak_days']}-day learning streak! You're on fire!")
        
        # Combine all parts
        feedback_text = " ".join(feedback_parts)
        
        # Store feedback
        feedback_log = FeedbackLog(
            user_id=user_id,
            lesson_id=lesson_id,
            feedback_text=feedback_text,
            feedback_type='lesson',
            performance_data=performance,
            emotion_context={
                'dominant_emotion': dominant_emotion,
                'recent_emotions': emotions
            }
        )
        
        db.session.add(feedback_log)
        db.session.commit()
        
        return {
            'feedback_text': feedback_text,
            'feedback_id': feedback_log.id,
            'performance_summary': performance,
            'emotion_context': {
                'dominant_emotion': dominant_emotion,
                'recent_emotions': emotions
            },
            'learning_trends': trends
        }
    
    def _get_random_template(self, category: str, subcategory: str) -> str:
        """Get a random template from a category"""
        templates = self.feedback_templates.get(category, {}).get(subcategory, [])
        return self._get_random_from_list(templates)
    
    def _get_random_from_list(self, items: List[str]) -> str:
        """Get a random item from a list"""
        import random
        return random.choice(items) if items else ""
    
    def _determine_next_steps(self, performance: Dict, emotion: str, trends: Dict) -> str:
        """Determine next steps based on performance and emotion"""
        emotion_context = self.feedback_templates['emotion_adaptive'].get(emotion, {})
        suggestions = emotion_context.get('suggestions', [])
        
        # Default suggestions based on performance
        if performance['accuracy'] < 60:
            suggestions.extend(['retry_easy', 'practice_more'])
        elif performance['accuracy'] > 80:
            suggestions.extend(['move_harder', 'spaced_review'])
        else:
            suggestions.extend(['practice_more', 'spaced_review'])
        
        # Get next step message
        next_step_key = suggestions[0] if suggestions else 'practice_more'
        return self.feedback_templates['next_steps'].get(next_step_key, "Keep practicing!")
    
    def get_feedback_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's feedback history"""
        feedback_logs = FeedbackLog.query.filter_by(user_id=user_id)\
            .order_by(FeedbackLog.timestamp.desc())\
            .limit(limit).all()
        
        return [{
            'id': log.id,
            'lesson_id': log.lesson_id,
            'feedback_text': log.feedback_text,
            'feedback_type': log.feedback_type,
            'performance_data': log.performance_data,
            'emotion_context': log.emotion_context,
            'timestamp': log.timestamp.isoformat()
        } for log in feedback_logs]
