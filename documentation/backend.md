# Backend Documentation

## Architecture Overview

The NeuroLearn backend is built with Python Flask and implements a microservices-inspired architecture with clear separation of concerns. The system is designed to handle real-time features, machine learning processing, and scalable educational content delivery.

## Project Structure

```
backend/
├── aitutor_backend/           # Main Flask application
│   ├── __init__.py           # App factory and configuration
│   ├── models.py             # SQLAlchemy database models
│   ├── config.py             # Configuration management
│   ├── wsgi.py               # WSGI application entry point
│   ├── routes/               # API route definitions
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── colearner.py      # Collaborative learning
│   │   ├── curriculum.py     # Curriculum management
│   │   ├── debate.py         # AI debate system
│   │   ├── emotion.py        # Emotion detection API
│   │   ├── gamification.py   # Gamification features
│   │   ├── learning_dna.py   # Learning profiling
│   │   ├── personalization.py # Content personalization
│   │   └── ...               # Other feature endpoints
│   ├── services/             # Business logic layer
│   │   ├── adaptive_engine.py # Core adaptive learning
│   │   ├── emotion_service.py # Emotion processing
│   │   ├── gamification_service.py # Quest and badge system
│   │   ├── personalization_engine.py # Recommendation system
│   │   └── ...               # Feature-specific services
│   └── utils/                # Utility functions
│       ├── llm_utils.py      # LLM integration helpers
│       └── ...               # Other utilities
├── Face-Emotion-Detector/    # Emotion detection module
│   ├── models/              # ML model definitions
│   ├── backend/             # Flask API for emotion detection
│   └── scripts/             # Training and evaluation scripts
└── requirements.txt         # Python dependencies
```

## Database Models

### Core Models

#### User Model
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='student')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    learning_profile = db.relationship('LearningProfile', backref='user', uselist=False)
    sessions = db.relationship('LearningSession', backref='user')
    achievements = db.relationship('Achievement', backref='user')
```

#### Learning Profile
```python
class LearningProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_style = db.Column(db.String(50))  # visual, auditory, kinesthetic
    pace_preference = db.Column(db.String(20))  # slow, normal, fast
    difficulty_level = db.Column(db.Integer, default=1)
    strengths = db.Column(db.JSON)
    weaknesses = db.Column(db.JSON)
    interests = db.Column(db.JSON)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### Learning Session
```python
class LearningSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100))
    difficulty = db.Column(db.String(20))
    status = db.Column(db.String(20), default='active')  # active, paused, completed
    progress = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Session-specific data
    learning_objectives = db.Column(db.JSON)
    interactions = db.Column(db.JSON)
    performance_metrics = db.Column(db.JSON)
```

## Service Layer Architecture

### Adaptive Learning Engine

#### Core Adaptive Logic
```python
class AdaptiveEngine:
    def __init__(self):
        self.ml_model = load_adaptive_model()
        
    def adjust_content(self, user_profile, performance_data, content_catalog):
        """Adapt content based on user performance and profile"""
        
        # Analyze user performance patterns
        performance_vector = self.extract_features(performance_data)
        
        # Get user learning preferences
        preferences = self.get_user_preferences(user_profile)
        
        # Predict optimal content delivery
        recommendations = self.ml_model.predict([
            performance_vector, 
            preferences
        ])
        
        # Score and rank content
        scored_content = self.score_content(
            content_catalog, 
            recommendations
        )
        
        return self.rank_results(scored_content)
```

### Emotion Service

#### Real-time Emotion Processing
```python
class EmotionService:
    def __init__(self):
        self.emotion_model = self.load_pre_trained_model()
        self.face_detector = cv2.CascadeClassifier()
        
    def process_emotion(self, image_data):
        """Process image for emotion detection"""
        
        # Convert base64 to image
        image = self.decode_image(image_data)
        
        # Face detection
        faces = self.detect_faces(image)
        
        if faces:
            # Extract facial features
            face_features = self.extract_facial_features(
                image, faces[0]
            )
            
            # Predict emotion
            emotion_prediction = self.emotion_model.predict(face_features)
            
            return {
                'emotion': self.map_prediction_to_emotion(emotion_prediction),
                'confidence': float(emotion_prediction.confidence),
                'timestamp': datetime.utcnow()
            }
        
        return None
    
    def analyze_emotion_trajectory(self, user_id, time_window):
        """Analyze emotional changes over time"""
        
        emotions = self.get_emotions_in_window(user_id, time_window)
        
        if len(emotions) > 2:
            # Calculate emotional trajectory
            trajectory = self.calculate_trajectory(emotions)
            
            # Detect stress patterns
            stress_indicators = self.detect_stress_patterns(emotions)
            
            return {
                'trajectory': trajectory,
                'stress_level': stress_indicators['average_stress'],
                'intervention_needed': stress_indicators['should_intervene']
            }
```

### Gamification Service

#### Quest System
```python
class QuestEngine:
    def __init__(self):
        self.quest_templates = self.load_quest_templates()
        
    def generate_adaptive_quest(self, user_profile, learning_goals):
        """Generate quest personalized to user profile"""
        
        # Analyze user's current level and interests
        difficulty = self.calculate_optimal_difficulty(user_profile)
        interests = user_profile.get('interests', [])
        
        # Select appropriate quest template
        base_quests = self.find_applicable_quests(
            difficulty, interests
        )
        
        # Personalize quest content
        personalized_quests = []
        for quest in base_quests:
            personalized = self.personalize_quest_content(
                quest, user_profile
            )
            personalized_quests.append(personalized)
        
        return self.rank_quests_by_engagement(personalized_quests)
    
    def evaluate_quest_completion(self, quest_id, user_submissions):
        """Evaluate quest completion and award points"""
        
        quest = self.get_quest(quest_id)
        evaluation_criteria = quest.evaluation_criteria
        
        # Score user submissions against criteria
        scores = {}
        for criterion, submissions in user_submissions.items():
            scores[criterion] = self.score_criterion(
                criterion, submissions, evaluation_criteria[criterion]
            )
        
        # Calculate overall quest completion
        overall_score = self.calculate_overall_score(scores)
        
        # Award points and badges
        if overall_score >= quest.completion_threshold:
            points_awarded = self.calculate_points(quest, overall_score)
            badges_earned = self.check_badge_eligibility(quest, overall_score)
            
            return {
                'completed': True,
                'score': overall_score,
                'points_awarded': points_awarded,
                'badges_earned': badges_earned
            }
        
        return {
            'completed': False,
            'score': overall_score,
            'feedback': self.generate_feedback(scores)
        }
```

## API Layer Architecture

### Route Structure

#### Authentication Routes
```python
@auth_bp.route('/login', methods=['POST'])
def login():
    """User authentication endpoint"""
    
    try:
        credentials = request.get_json()
        
        # Validate input
        if not credentials.get('username') or not credentials.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400
        
        # Authenticate user
        user = User.query.filter_by(username=credentials['username']).first()
        
        if user and user.check_password(credentials['password']):
            # Generate JWT token
            token = generate_token(user.id)
            
            return jsonify({
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            }), 200
        
        return jsonify({'error': 'Invalid credentials'}), 401
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
```

#### Emotion Detection Routes
```python
@emotion_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_emotion():
    """Real-time emotion detection endpoint"""
    
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        
        # Process image for emotion detection
        emotion_result = EmotionService().process_emotion(image_file)
        
        if emotion_result:
            # Store emotion data
            db.session.add(EmotionData(
                user_id=get_jwt_identity(),
                emotion=emotion_result['emotion'],
                confidence=emotion_result['confidence'],
                timestamp=emotion_result['timestamp']
            ))
            db.session.commit()
            
            return jsonify(emotion_result), 200
        
        return jsonify({'error': 'No face detected'}), 400
        
    except Exception as e:
        logger.error(f"Emotion detection error: {str(e)}")
        return jsonify({'error': 'Processing failed'}), 500
```

## WebSocket Implementation

### Real-time Communication
```python
from flask_socketio import SocketIO, emit, join_room, leave_room

class RealtimeHandler:
    def manipulate_lesson_update(self, session_id, update_data):
        """Handle real-time lesson updates"""
        
        # Validate user's access to session
        user_id = get_jwt_identity()
        session = get_session_with_access_check(session_id, user_id)
        
        if not session:
            emit('error', {'message': 'Session not found'})
            return
        
        # Process update (adaptive content, hints, etc.)
        adapted_content = AdaptiveEngine().adapt_content(
            user_id=user_id,
            session_id=session_id,
            current_update=update_data
        )
        
        # Broadcast to all participants in session
        emit('lesson_update', adapted_content, room=f'session_{session_id}')
    
    def manipulate_colearning_sync(self, session_id, activity_data):
        """Handle collaborative learning synchronization"""
        
        # Broadcast user activity to collaborators
        emit('peer_activity', {
            'user_id': get_jwt_identity(),
            'activity': activity_data,
            'timestamp': datetime.utcnow()
        }, room=f'colearning_{session_id}')
```

## Machine Learning Integration

### Adaptive Learning Models
```python
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier

class AdaptiveLearningModel:
    def __init__(self):
        self.content_recommender = self.load_recommender_model()
        self.difficulty_adjuster = self.load_difficulty_model()
        
    def recommend_content(self, user_profile, performance_history):
        """ML-based content recommendation"""
        
        # Feature engineering
        features = self.extract_user_features(user_profile, performance_history)
        
        # Generate recommendations
        recommendations = self.content_recommender.predict_proba([features])
        
        # Filter and rank results
        return self.filter_by_preferences(
            recommendations, 
            user_profile['preferences']
        )
    
    def adjust_difficulty(self, user_performance, content_type):
        """Dynamic difficulty adjustment"""
        
        performance_features = self.extract_performance_features(
            user_performance
        )
        
        difficulty_prediction = self.difficulty_adjuster.predict([
            performance_features + [content_type]
        ])
        
        return self.map_to_difficulty_level(difficulty_prediction)
```

### Emotion Recognition Models
```python
class EmotionRecognitionModel:
    def __init__(self):
        self.model = tf.keras.models.load_model('emotion_model.h5')
        self.emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
        
    def predict_emotion(self, face_features):
        """Predict emotion from facial features"""
        
        # Preprocess features
        processed_features = self.preprocess_features(face_features)
        
        # Make prediction
        prediction = self.burn_model.predict(processed_features)
        
        # Post-process results
        emotion_idx = np.argmax(prediction)
        confidence = float(np.max(prediction))
        
        return {
            'emotion': self.emotions[emotion_idx],
            'confidence': confidence,
            'probabilities': {
                emotion: float(prob) 
                for emotion, prob in zip(self.emotions, prediction[0])
            }
        }
```

## Configuration Management

### Environment Configuration
```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'development-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aitutor.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # ML Model paths
    EMOTION_MODEL_PATH = os.environ.get('EMOTION_MODEL_PATH') or 'models/emotion_model.h5'
    ADAPTIVE_MODEL_PATH = os.environ.get('ADAPTIVE_MODEL_PATH') or 'models/adaptive_model.pkl'
    
    # External API keys
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    
    # WebSocket configuration
    SOCKETIO_CORS_ALLOWED_ORIGINS = os.environ.get('ALLOWED_ORIGINS', '*').split(',')
```

## Testing Strategy

### Unit Testing
```python
import pytest
from unittest.mock import Mock, patch
from aitutor_backend.services.adaptive_engine import AdaptiveEngine

class TestAdaptiveEngine:
    def setup_method(self):
        self.engine = AdaptiveEngine()
        
    @patch('aitutor_backend.services.adaptive_engine.load_adaptive_model')
    def test_content_adaptation(self, mock_model):
        """Test content adaptation based on user profile"""
        
        mock_model.return_value.predict.return_value = [0.8, 0.6, 0.4]
        
        user_profile = {'learning_style': 'visual', 'difficulty': 2}
        performance_data = {'accuracy': 0.75, 'speed': 1.2}
        content_catalog = ['content1', 'content2', 'content3']
        
        result = self.engine.adjust_content(
            user_profile, 
            performance_data, 
            content_catalog
        )
        
        assert len(result) == 3
        assert all('score' in item for item in result)
```

### Integration Testing
```python
@pytest.fixture
def client():
    """Test client for API testing"""
    app = create_app('testing')
    with app.test_client() as client:
        yield client

def test_emotion_detection_api(client):
    """Test emotion detection API endpoint"""
    
    # Mock successful image processing
    with patch('aitutor_backend.services.emotion_service.EmotionService') as mock_service:
        mock_service.return_value.process_emotion.return_value = {
            'emotion': 'happy',
            'confidence': 0.85,
            'timestamp': datetime.utcnow()
        }
        
        # Test API endpoint
        response = client.post('/api/v1/emotion/detect', 
                            data={'image': 'fake_image_data'})
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['emotion'] == 'happy'
        assert data['confidence'] == 0.85
```

## Deployment Configuration

### Production Setup
```python
# wsgi.py
from aitutor_backend import create_app

application = create_app('production')

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=5000)
```

### Docker Configuration
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY aitutor_backend/ .
COPY models/ models/

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "wsgi:application"]
```

## Performance Optimization

### Database Optimization
```python
# Add database indexes for performance
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

# Use eager loading for relationships
users_with_profiles = User.query.options(
    db.joinedload(User.learning_profile),
    db.joinedload(User.sessions)
).all()

# Implement caching for frequently accessed data
@cache.memoize(timeout=300)
def get_user_profile(user_id):
    return LearningProfile.query.filter_by(user_id=user_id).first()
```

### API Rate Limiting
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379"
)

# Apply rate limits to endpoints
@emotion_bp.route('/detect', methods=['POST'])
@limiter.limit("30 per minute")
@jwt_required()
def detect_emotion():
    # Endpoint implementation
    pass
```

## Security Considerations

### Input Validation
```python
from marshmallow import Schema, fields, validate

class EmotionDetectionSchema(Schema):
    image = fields.Str(required=True, validate=validate.Length(min=1))
    timestamp = fields.DateTime()

# Validate requests
def validate_request_data(schema_class):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            schema = schema_class()
            errors = schema.validate(request.get_json())
            if errors:
                return jsonify({'errors': errors}), 400
            return f(*args, **kwargs)
        return wrapper
    return decorator
```

### Data Security
- Password hashing using bcrypt
- JWT token authentication
- Input sanitization and validation
- Rate limiting on all endpoints
- CORS configuration for security
- SQL injection prevention through ORM
