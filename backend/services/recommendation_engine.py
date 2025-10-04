import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from ..models import User, EmotionLog
from .. import db

class RecommendationEngine:
    def __init__(self):
        self.emotion_weights = {
            'happy': 1.2,
            'surprise': 1.1,
            'neutral': 1.0,
            'sad': 0.8,
            'fear': 0.7,
            'angry': 0.6,
            'disgust': 0.5
        }
        
        self.difficulty_adjustments = {
            'happy': 0.1,
            'surprise': 0.05,
            'neutral': 0.0,
            'sad': -0.1,
            'fear': -0.15,
            'angry': -0.2,
            'disgust': -0.1
        }

    def get_emotion_trend(self, user_id: int, hours: int = 24) -> Dict:
        """Get emotion trend for user over specified hours"""
        since = datetime.utcnow() - timedelta(hours=hours)
        emotions = EmotionLog.query.filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= since
        ).order_by(EmotionLog.timestamp.desc()).all()

        if not emotions:
            return {'trend': 'neutral', 'confidence': 0.0, 'emotions': []}

        # Calculate emotion frequencies
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion.emotion] = emotion_counts.get(emotion.emotion, 0) + 1

        # Find dominant emotion
        dominant_emotion = max(emotion_counts.items(), key=lambda x: x[1])
        
        # Calculate trend confidence
        total_emotions = len(emotions)
        confidence = dominant_emotion[1] / total_emotions

        return {
            'trend': dominant_emotion[0],
            'confidence': confidence,
            'emotions': [{'emotion': e.emotion, 'confidence': e.confidence, 'timestamp': e.timestamp} for e in emotions]
        }

    def calculate_learning_difficulty(self, user_id: int, base_difficulty: float = 0.5) -> float:
        """Calculate adaptive difficulty based on recent emotions"""
        trend = self.get_emotion_trend(user_id, hours=2)
        
        if trend['confidence'] < 0.3:  # Not enough data
            return base_difficulty

        emotion = trend['trend']
        adjustment = self.difficulty_adjustments.get(emotion, 0.0)
        
        # Apply confidence weighting
        adjustment *= trend['confidence']
        
        new_difficulty = base_difficulty + adjustment
        return max(0.0, min(1.0, new_difficulty))

    def get_content_recommendations(self, user_id: int, current_topic: str = None) -> List[Dict]:
        """Get content recommendations based on emotions and learning history"""
        trend = self.get_emotion_trend(user_id, hours=6)
        difficulty = self.calculate_learning_difficulty(user_id)
        
        # Content database (in real app, this would be from database)
        content_db = {
            'beginner': [
                {'id': 1, 'title': 'Introduction to Variables', 'topic': 'programming', 'difficulty': 0.2},
                {'id': 2, 'title': 'Basic Data Types', 'topic': 'programming', 'difficulty': 0.3},
                {'id': 3, 'title': 'Simple Functions', 'topic': 'programming', 'difficulty': 0.4},
            ],
            'intermediate': [
                {'id': 4, 'title': 'Object-Oriented Programming', 'topic': 'programming', 'difficulty': 0.6},
                {'id': 5, 'title': 'Data Structures', 'topic': 'programming', 'difficulty': 0.7},
                {'id': 6, 'title': 'Algorithm Design', 'topic': 'programming', 'difficulty': 0.8},
            ],
            'advanced': [
                {'id': 7, 'title': 'Machine Learning Basics', 'topic': 'ml', 'difficulty': 0.9},
                {'id': 8, 'title': 'Neural Networks', 'topic': 'ml', 'difficulty': 1.0},
            ]
        }

        # Select appropriate difficulty level
        if difficulty < 0.4:
            level = 'beginner'
        elif difficulty < 0.7:
            level = 'intermediate'
        else:
            level = 'advanced'

        recommendations = content_db[level].copy()
        
        # Apply emotion-based filtering
        if trend['trend'] in ['sad', 'fear', 'angry']:
            # Suggest easier content or breaks
            recommendations = [r for r in recommendations if r['difficulty'] < 0.6]
            recommendations.insert(0, {
                'id': 'break',
                'title': 'Take a Break',
                'topic': 'wellness',
                'difficulty': 0.0,
                'type': 'break'
            })
        elif trend['trend'] in ['happy', 'surprise']:
            # Suggest more challenging content
            recommendations = [r for r in recommendations if r['difficulty'] > 0.5]

        return recommendations[:3]  # Return top 3 recommendations

    def get_adaptive_message(self, user_id: int) -> str:
        """Get adaptive encouragement message based on emotions"""
        trend = self.get_emotion_trend(user_id, hours=1)
        
        messages = {
            'happy': "You're doing great! Your positive attitude is helping you learn faster!",
            'surprise': "Your curiosity is showing! Let's explore this concept further.",
            'neutral': "You're focused and ready to learn. Let's continue!",
            'sad': "Don't worry, learning can be challenging. Take your time and don't hesitate to ask for help.",
            'fear': "It's okay to feel uncertain. We'll break this down into smaller, manageable steps.",
            'angry': "I can see you're feeling frustrated. Let's try a different approach to this topic.",
            'disgust': "This topic isn't resonating with you. Let's try something that interests you more."
        }
        
        return messages.get(trend['trend'], messages['neutral'])

    def should_suggest_break(self, user_id: int) -> bool:
        """Determine if user should take a break based on emotions"""
        trend = self.get_emotion_trend(user_id, hours=1)
        
        # Suggest break if consistently negative emotions
        negative_emotions = ['sad', 'angry', 'fear', 'disgust']
        if trend['trend'] in negative_emotions and trend['confidence'] > 0.6:
            return True
            
        # Check for prolonged study time (mock implementation)
        # In real app, would check actual study time
        return False

    def get_emotion_insights(self, user_id: int, days: int = 7) -> Dict:
        """Get insights about user's emotional learning patterns"""
        since = datetime.utcnow() - timedelta(days=days)
        emotions = EmotionLog.query.filter(
            EmotionLog.user_id == user_id,
            EmotionLog.timestamp >= since
        ).all()

        if not emotions:
            return {'insights': [], 'recommendations': []}

        # Analyze patterns
        emotion_counts = {}
        confidence_scores = []
        
        for emotion in emotions:
            emotion_counts[emotion.emotion] = emotion_counts.get(emotion.emotion, 0) + 1
            confidence_scores.append(emotion.confidence)

        total_emotions = len(emotions)
        avg_confidence = np.mean(confidence_scores)
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Most common emotion
        most_common = max(emotion_counts.items(), key=lambda x: x[1])
        insights.append(f"Your most common emotion while learning is {most_common[0]} ({most_common[1]} times)")
        
        # Confidence analysis
        if avg_confidence > 0.8:
            insights.append("The emotion detection is working well with high confidence scores")
        elif avg_confidence < 0.5:
            insights.append("Consider improving lighting or camera positioning for better emotion detection")
            recommendations.append("Adjust your camera setup for better emotion detection")
        
        # Emotional patterns
        positive_emotions = ['happy', 'surprise']
        negative_emotions = ['sad', 'angry', 'fear', 'disgust']
        
        positive_count = sum(emotion_counts.get(e, 0) for e in positive_emotions)
        negative_count = sum(emotion_counts.get(e, 0) for e in negative_emotions)
        
        if positive_count > negative_count * 1.5:
            insights.append("You generally have a positive learning experience!")
            recommendations.append("Keep up the great work! Consider tackling more challenging topics.")
        elif negative_count > positive_count * 1.5:
            insights.append("You seem to be struggling with the current difficulty level")
            recommendations.append("Consider taking breaks more frequently or reducing difficulty")
        
        return {
            'insights': insights,
            'recommendations': recommendations,
            'stats': {
                'total_detections': total_emotions,
                'avg_confidence': round(avg_confidence, 2),
                'most_common_emotion': most_common[0],
                'positive_ratio': round(positive_count / total_emotions, 2) if total_emotions > 0 else 0
            }
        }
