from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from ..models import LearningStyle, User
from .. import db


class LearningStyleService:
    """Service for detecting and managing user learning styles"""
    
    def __init__(self):
        self.style_weights = {
            'visual': 1.0,
            'auditory': 1.0,
            'example': 1.0
        }
        
        # Minimum attempts needed for reliable detection
        self.min_attempts = 3
        
        # Confidence thresholds
        self.confidence_threshold = 0.05  # Minimum difference to be considered dominant
    
    def update_learning_style(self, user_id: int, style: str, performance_score: float, 
                            time_spent: int = None, engagement_score: float = None) -> Dict:
        """
        Update learning style scores based on lesson performance
        
        Args:
            user_id: User ID
            style: Learning style used ("visual", "auditory", "example")
            performance_score: Performance score (0.0 to 1.0)
            time_spent: Time spent on lesson (seconds)
            engagement_score: Engagement score (0.0 to 1.0)
            
        Returns:
            Dictionary with updated learning style data
        """
        # Validate style
        if style not in ['visual', 'auditory', 'example']:
            raise ValueError(f"Invalid learning style: {style}")
        
        # Validate performance score
        if not 0.0 <= performance_score <= 1.0:
            raise ValueError(f"Performance score must be between 0.0 and 1.0, got: {performance_score}")
        
        # Get or create learning style record
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if not learning_style:
            learning_style = LearningStyle(
                user_id=user_id,
                visual_score=0.0,
                auditory_score=0.0,
                example_score=0.0,
                dominant_style=None,
                total_attempts=0,
                visual_attempts=0,
                auditory_attempts=0,
                example_attempts=0
            )
            db.session.add(learning_style)
        
        # Update attempt counts
        learning_style.total_attempts += 1
        
        if style == 'visual':
            learning_style.visual_attempts += 1
        elif style == 'auditory':
            learning_style.auditory_attempts += 1
        elif style == 'example':
            learning_style.example_attempts += 1
        
        # Calculate weighted performance score
        # Consider time spent and engagement for more accurate scoring
        weighted_score = performance_score
        
        if time_spent:
            # Optimal time range (adjust based on your content)
            optimal_time = 300  # 5 minutes
            time_factor = min(1.0, optimal_time / max(time_spent, 1))
            weighted_score *= time_factor
        
        if engagement_score:
            # Blend performance with engagement
            weighted_score = (weighted_score * 0.7) + (engagement_score * 0.3)
        
        # Update style score using exponential moving average
        alpha = 0.3  # Learning rate
        current_score = getattr(learning_style, f"{style}_score")
        new_score = (alpha * weighted_score) + ((1 - alpha) * current_score)
        setattr(learning_style, f"{style}_score", new_score)
        
        # Update timestamp
        learning_style.updated_at = datetime.utcnow()
        
        # Determine dominant style
        dominant_style = self._get_dominant_style(learning_style)
        learning_style.dominant_style = dominant_style
        
        db.session.commit()
        
        return {
            'visual_score': learning_style.visual_score,
            'auditory_score': learning_style.auditory_score,
            'example_score': learning_style.example_score,
            'dominant_style': dominant_style,
            'confidence': self._calculate_confidence(learning_style),
            'total_attempts': learning_style.total_attempts,
            'style_attempts': {
                'visual': learning_style.visual_attempts,
                'auditory': learning_style.auditory_attempts,
                'example': learning_style.example_attempts
            }
        }
    
    def _get_dominant_style(self, learning_style: LearningStyle) -> Optional[str]:
        """Determine the dominant learning style"""
        scores = {
            'visual': learning_style.visual_score,
            'auditory': learning_style.auditory_score,
            'example': learning_style.example_score
        }
        
        # Find highest score
        max_score = max(scores.values())
        max_style = max(scores, key=scores.get)
        
        # Check if we have enough data and sufficient confidence
        if learning_style.total_attempts < self.min_attempts:
            return None
        
        # Check if the difference is significant enough
        sorted_scores = sorted(scores.values(), reverse=True)
        if len(sorted_scores) >= 2 and (sorted_scores[0] - sorted_scores[1]) < self.confidence_threshold:
            return None
        
        return max_style
    
    def _calculate_confidence(self, learning_style: LearningStyle) -> float:
        """Calculate confidence in the learning style detection"""
        if learning_style.total_attempts < self.min_attempts:
            return 0.0
        
        scores = [
            learning_style.visual_score,
            learning_style.auditory_score,
            learning_style.example_score
        ]
        
        # Confidence based on score separation and total attempts
        max_score = max(scores)
        second_max = sorted(scores, reverse=True)[1]
        score_separation = max_score - second_max
        
        # Normalize confidence (0.0 to 1.0)
        attempt_factor = min(1.0, learning_style.total_attempts / 10)  # Max confidence at 10 attempts
        separation_factor = min(1.0, score_separation / 0.5)  # Max confidence at 0.5 separation
        
        confidence = (attempt_factor * 0.6) + (separation_factor * 0.4)
        return min(1.0, confidence)
    
    def get_dominant_style(self, user_id: int) -> Dict:
        """Get the dominant learning style for a user"""
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if not learning_style:
            return {
                'dominant_style': None,
                'confidence': 0.0,
                'visual_score': 0.0,
                'auditory_score': 0.0,
                'example_score': 0.0,
                'total_attempts': 0,
                'recommendation': 'Complete more lessons to detect your learning style'
            }
        
        dominant_style = self._get_dominant_style(learning_style)
        confidence = self._calculate_confidence(learning_style)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(learning_style, dominant_style, confidence)
        
        return {
            'dominant_style': dominant_style,
            'confidence': confidence,
            'visual_score': learning_style.visual_score,
            'auditory_score': learning_style.auditory_score,
            'example_score': learning_style.example_score,
            'total_attempts': learning_style.total_attempts,
            'style_attempts': {
                'visual': learning_style.visual_attempts,
                'auditory': learning_style.auditory_attempts,
                'example': learning_style.example_attempts
            },
            'recommendation': recommendation,
            'last_updated': learning_style.updated_at.isoformat()
        }
    
    def _generate_recommendation(self, learning_style: LearningStyle, dominant_style: Optional[str], 
                               confidence: float) -> str:
        """Generate personalized recommendation based on learning style"""
        if not dominant_style or confidence < 0.3:
            return "Complete more lessons to better understand your learning style"
        
        recommendations = {
            'visual': {
                'high': "You're a strong visual learner! Focus on diagrams, charts, and visual content.",
                'medium': "You tend to learn well with visual content. Try more visual materials.",
                'low': "Visual content might help you learn better. Give it a try!"
            },
            'auditory': {
                'high': "You're an excellent auditory learner! Audio content and discussions work best for you.",
                'medium': "You learn well through listening. Try audio lessons and explanations.",
                'low': "Audio content might be helpful for your learning. Consider trying it."
            },
            'example': {
                'high': "You're a great example-based learner! Hands-on practice and examples are perfect for you.",
                'medium': "You learn best through examples and practice. Focus on practical content.",
                'low': "Examples and practice might help you learn better. Try more hands-on content."
            }
        }
        
        if confidence >= 0.7:
            confidence_level = 'high'
        elif confidence >= 0.4:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'
        
        return recommendations[dominant_style][confidence_level]
    
    def get_style_insights(self, user_id: int) -> Dict:
        """Get detailed insights about user's learning style"""
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if not learning_style:
            return {
                'insights': [],
                'suggestions': ['Start learning to discover your style preferences']
            }
        
        insights = []
        suggestions = []
        
        # Analyze score patterns
        scores = {
            'visual': learning_style.visual_score,
            'auditory': learning_style.auditory_score,
            'example': learning_style.example_score
        }
        
        # Find patterns
        max_score = max(scores.values())
        min_score = min(scores.values())
        score_range = max_score - min_score
        
        if score_range > 0.3:
            insights.append("You have a clear learning style preference")
        elif score_range > 0.1:
            insights.append("You have a moderate learning style preference")
        else:
            insights.append("You're a balanced learner across different styles")
        
        # Style-specific insights
        for style, score in scores.items():
            if score > 0.7:
                insights.append(f"You excel with {style} content")
            elif score < 0.3:
                insights.append(f"You might struggle with {style} content")
        
        # Generate suggestions
        if learning_style.total_attempts < 5:
            suggestions.append("Complete more lessons for better style detection")
        
        dominant_style = self._get_dominant_style(learning_style)
        if dominant_style:
            style_suggestions = {
                'visual': [
                    "Request more diagrams and visual aids",
                    "Use mind maps for note-taking",
                    "Look for video content with graphics"
                ],
                'auditory': [
                    "Listen to audio explanations",
                    "Participate in discussions",
                    "Use verbal repetition techniques"
                ],
                'example': [
                    "Focus on practical examples",
                    "Try hands-on exercises",
                    "Look for step-by-step tutorials"
                ]
            }
            suggestions.extend(style_suggestions[dominant_style])
        
        return {
            'insights': insights,
            'suggestions': suggestions,
            'style_distribution': scores,
            'confidence': self._calculate_confidence(learning_style)
        }
    
    def reset_learning_style(self, user_id: int) -> bool:
        """Reset learning style data for a user"""
        learning_style = LearningStyle.query.filter_by(user_id=user_id).first()
        
        if learning_style:
            learning_style.visual_score = 0.0
            learning_style.auditory_score = 0.0
            learning_style.example_score = 0.0
            learning_style.dominant_style = None
            learning_style.total_attempts = 0
            learning_style.visual_attempts = 0
            learning_style.auditory_attempts = 0
            learning_style.example_attempts = 0
            learning_style.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True
        
        return False
