# API Documentation

## Overview

The NeuroLearn backend provides a comprehensive RESTful API built with Flask. The API is designed to support AI-powered learning experiences with features like emotion detection, adaptive tutoring, and personalized content delivery.

## Base URL

```
Development: http://localhost:5000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

All API endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### POST /api/v1/auth/login
Login with credentials and receive JWT token.

**Request:**
```json
{
  "username": "student@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "username": "student@example.com",
    "role": "student"
  }
}
```

#### POST /api/v1/auth/register
Register a new user account.

**Request:**
```json
{
  "username": "newstudent@example.com",
  "password": "password123",
  "role": "student"
}
```

## Core Learning API

### Learning DNA

#### GET /api/v1/learning-dna/{user_id}
Get user's learning DNA profile.

**Response:**
```json
{
  "user_id": 1,
  "learning_style": "visual",
  "preferred_pace": "moderate",
  "difficulty_level": 3,
  "strengths": ["mathematics", "logic"],
  "weaknesses": ["reading_comprehension"]
}
```

#### PUT /api/v1/learning-dna/{user_id}
Update user's learning DNA profile.

### Emotion Detection

#### POST /api/v1/emotion/detect
Upload image for emotion detection.

**Request:** Multipart form data with image file

**Response:**
```json
{
  "emotion": "happy",
  "confidence": 0.87,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /api/v1/emotion/history/{user_id}
Get emotion detection history for user.

### Adaptive Tutoring

#### POST /api/v1/tutor/lesson
Start a new tutoring session.

**Request:**
```json
{
  "user_id": 1,
  "topic": "algebra",
  "difficulty": "intermediate"
}
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "lesson_plan": {
    "steps": [
      {"type": "concept_introduction", "content": "..."},
      {"type": "practice_problems", "content": "..."}
    ]
  }
}
```

#### POST /api/v1/tutor/response/{session_id}
Provide student response for adaptive learning.

## Gamification

#### GET /api/v1/gamification/profile/{user_id}
Get user's gamification profile.

**Response:**
```json
{
  "level": 15,
  "experience_points": 2500,
  "badges": [
    {"name": "Problem Solver", "description": "Solved 50 math problems"},
    {"name": "Quick Learner", "description": "Completed lessons rapidly"}
  ],
  "achievements": ["week_streak", "perfect_score"]
}
```

#### GET /api/v1/quests/available/{user_id}
Get available quests for user.

### Story Learning

#### GET /api/v1/stories
Get available story-driven learning content.

#### GET /api/v1/stories/{story_id}
Get specific story details and chapters.

### Knowledge Graph

#### GET /api/v1/knowledge-graph/{user_id}
Get user's knowledge graph visualization data.

**Response:**
```json
{
  "nodes": [
    {"id": "algebra", "label": "Algebra", "level": 3, "mastery": 0.8},
    {"id": "geometry", "label": "Geometry", "level": 2, "mastery": 0.6}
  ],
  "links": [
    {"source": "algebra", "target": "quadratic_equations", "strength": 0.7}
  ]
}
```

## Performance Analytics

#### GET /api/v1/performance/analytics/{user_id}
Get comprehensive performance analytics.

**Response:**
```json
{
  "overall_progress": 0.75,
  "grade_distribution": {...},
  "learning_velocity": 1.2,
  "strength_areas": ["math", "science"],
  "improvement_areas": ["reading"]
}
```

## WebSocket Events

### Real-time Updates

Connect to WebSocket endpoint for real-time features:

```javascript
const socket = io('ws://localhost:5000/ws');
```

#### Events emitted by client:
- `join_lesson`: Join a lesson session
- `student_response`: Send response during lesson
- `emotion_update`: Real-time emotion detection

#### Events emitted by server:
- `lesson_update`: Lesson content updates
- `peer_activity`: Co-learning session updates
- `achievement_unlocked`: Real-time achievement notifications

## Error Handling

All API errors follow a consistent format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": {...}
  }
}
```

### Common HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

API requests are rate limited:
- General endpoints: 100 requests per minute
- Emotion detection: 30 requests per minute
- Real-time tutoring: 50 requests per minute

## SDK and Examples

### Python Client Example
```python
from neurolearn_client import NeuroLearnClient

client = NeuroLearnClient(api_key="your-api-key")

# Start a tutoring session
session = client.tutor.start_lesson(
    user_id=1,
    topic="calculus",
    difficulty="advanced"
)
```

### JavaScript Client Example
```javascript
import { NeuroLearnClient } from 'neurolearn-js';

const client = new NeuroLearnClient({
  apiKey: 'your-api-key',
  baseURL: 'https://api.neurolearn.com'
});

const session = await client.tutor.startLesson({
  userId: 1,
  topic: 'algebra',
  difficulty: 'intermediate'
});
```
