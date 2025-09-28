# AI Co-Learner Feature

The AI Co-Learner is an opt-in feature that provides an AI study buddy that learns alongside the user, offering personalized support, motivation, and collaborative learning experiences.

## Features

- **AI Study Buddy**: An AI character that studies alongside the user
- **Persona System**: Multiple personality types (Curious Companion, Zen Coach, Challenger)
- **Growth System**: Co-learner levels up, unlocks traits, and develops personality over time
- **Humor System**: Adjustable humor level (0-10) with persona-specific jokes and wit
- **Trait Unlocks**: New personality traits unlock at level milestones
- **Real-time Chat**: Interactive conversation with the co-learner
- **Activity Tracking**: Co-learner responds to lesson completions, quiz results, and study activities
- **Emotion Mirroring**: Adapts tone and responses based on user's emotional state
- **XP System**: Co-learner earns experience points and grows with the user
- **Dialog Memory**: Remembers recent conversations for better context
- **Privacy-First**: All features are opt-in with granular privacy controls

## Backend API

### Endpoints

- `GET /api/colearner/state` - Get co-learner profile and settings
- `POST /api/colearner/message` - Send message to co-learner
- `POST /api/colearner/action` - Record learning activity
- `POST /api/colearner/settings` - Update co-learner settings
- `POST /api/colearner/mirror_emotion` - Mirror user's emotional state

### Models

- `CoLearnerProfile` - User's co-learner configuration and progress
  - `xp` - Experience points for growth
  - `level` - Current level (calculated from XP)
  - `traits` - Unlocked personality traits
  - `humor_level` - Humor intensity (0-10)
- `CoLearnerDialogLog` - Chat history (if enabled)
- `CoLearnerActivity` - Learning activities and outcomes

## Frontend Components

- `CoLearnerWidget` - Floating widget for quick access
- `CoLearnerPanel` - Main chat interface
- `CoLearnerAvatar` - Animated avatar with mood indicators
- `CoLearnerSettings` - Settings panel for configuration

## Persona Types

### Curious Companion (Nova)
- **Tone**: Playful and inquisitive
- **Behavior**: Asks questions, tries problems, explains examples
- **Humor Style**: Playful puns and dad jokes
- **Base Traits**: curious, enthusiastic
- **Best for**: Learners who enjoy collaborative exploration

### Zen Coach (Asha)
- **Tone**: Calm and supportive
- **Behavior**: Provides hints, suggests breaks, offers breathing exercises
- **Humor Style**: Gentle wisdom and philosophical insights
- **Base Traits**: wise, patient
- **Best for**: Learners who need emotional support and stress management

### Challenger (Rex)
- **Tone**: Motivating and challenging
- **Behavior**: Pushes limits, suggests harder problems, time trials
- **Humor Style**: Witty sarcasm and competitive banter
- **Base Traits**: determined, sarcastic
- **Best for**: Learners who thrive on competition and challenges

## Growth System

### XP and Leveling
- **XP Sources**: Chat interactions (5 XP), lesson completion (10-60 XP), quiz completion (5-35 XP)
- **Level Calculation**: Level = (XP ÷ 100) + 1
- **Level Up Events**: Triggered every 100 XP with celebratory animations

### Trait Unlocks
- **Level 3**: "Encourager" - Adds motivational phrases and support
- **Level 5**: "Humorist" - Unlocks jokes and witty responses
- **Level 10**: "Mentor" - Gains wisdom-like guidance and deeper insights

### Humor System
- **Range**: 0 (serious) to 10 (hilarious)
- **Persona-Specific**: Each persona has unique humor styles
- **Growth Integration**: Higher levels unlock more sophisticated humor

## Setup and Usage

### 1. Enable Co-Learner

1. Go to Settings page
2. Find "AI Co-Learner Settings" section
3. Toggle "Enable Co-Learner" to ON
4. Choose your preferred persona
5. Adjust humor level (0-10) to your preference
6. Optionally enable "Save Conversations" for better personalization

### 2. Interact with Co-Learner

1. Click the floating co-learner widget (bottom-right corner)
2. Send messages or ask questions
3. Co-learner will respond based on your chosen persona and current level
4. Watch the XP bar fill up as you interact
5. Celebrate level-ups and trait unlocks with your co-learner
6. Co-learner automatically responds to your learning activities

### 3. Activity Integration

The co-learner automatically responds when you:
- Complete lessons
- Finish quizzes
- Complete revision sessions
- Experience different emotions during learning

## Privacy and Data

- **Default State**: Co-learner is disabled by default
- **Dialog Logging**: Disabled by default, must be explicitly enabled
- **Data Storage**: Only basic profile and activity data is stored
- **Emotion Data**: Only used for tone adaptation, not stored permanently

## Development

### Adding New Personas

1. Add persona configuration to `aitutor_backend/services/persona_presets.json`
2. Update `PERSONA_OPTIONS` in `CoLearnerSettings.jsx`
3. Add persona-specific behavior in `colearner_service.py`

### Customizing Responses

Edit the `_rules_reply` function in `colearner_service.py` to customize:
- Response templates
- Action suggestions
- Confidence scoring
- Context-aware replies

### Adding Activity Types

1. Add new activity type to the `/api/colearner/action` endpoint
2. Define XP calculation logic
3. Add response generation logic
4. Update frontend hooks to call the new activity type

## Testing

### Manual Testing

1. Create a new user account
2. Enable co-learner in settings
3. Send messages and verify responses
4. Complete a lesson and check co-learner reaction
5. Test different personas and their behaviors

### API Testing

```bash
# Get co-learner state
curl -H "Authorization: Bearer <token>" http://localhost:8002/api/colearner/state

# Send message
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"message": "I need help with calculus"}' \
  http://localhost:8002/api/colearner/message

# Record activity
curl -X POST -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{"activity_type": "lesson_complete", "payload": {"lesson_id": 1, "score": 0.8}}' \
  http://localhost:8002/api/colearner/action
```

## Future Enhancements

- **LLM Integration**: Replace rules-based responses with actual LLM calls
- **Voice Interaction**: Add voice chat capabilities
- **Advanced Analytics**: Track learning patterns and suggest optimizations
- **Multi-User**: Support for group study sessions with multiple co-learners
- **Custom Avatars**: Allow users to customize their co-learner's appearance
