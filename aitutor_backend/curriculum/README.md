# Curriculum Auto-Evolution System

The Curriculum Auto-Evolution system automatically fetches, processes, and integrates new educational resources into the AI Tutor platform, ensuring students always have access to the latest and most relevant learning materials.

## Features

- **Automated Resource Fetching**: Weekly scraping from Khan Academy, ArXiv, YouTube EDU, and other educational sources
- **NLP-Powered Processing**: Converts raw resources into structured lesson cards with quizzes and exercises
- **Adaptive Learning Paths**: Dynamically updates user learning paths based on weak areas and performance
- **Real-time Updates**: Live notifications when new lessons are added or existing ones are updated
- **Fresh Content Detection**: Identifies and highlights newly added lessons
- **Smart Replacement**: Replaces outdated lessons with fresh content automatically

## Architecture

### Backend Components

#### Models
- **Resource**: Stores external educational resources (videos, articles, tutorials)
- **LessonCard**: Generated structured lessons from resources with quizzes and exercises
- **LearningPath**: Links users to lesson cards with progress tracking
- **CurriculumUpdate**: Tracks curriculum changes and notifications

#### Services
- **CurriculumService**: Core service for resource processing and learning path management
- **CurriculumScheduler**: Automated scheduling for weekly updates and maintenance

#### API Endpoints
- `GET /api/curriculum/updates` - Get recent curriculum updates
- `POST /api/curriculum/refresh` - Manually trigger refresh (admin only)
- `GET /api/curriculum/path` - Get user's learning path
- `GET /api/curriculum/fresh-lessons` - Get lessons added in last 7 days
- `GET /api/curriculum/stats` - Get curriculum statistics

### Frontend Components

#### React Components
- **FreshLessons**: Displays newly added lessons with animations
- **AdaptivePath**: Shows user's personalized learning path
- **CurriculumUpdates**: Real-time notifications for curriculum changes

#### Dashboard Integration
- New "Curriculum" tab for learning path management
- New "Updates" tab for curriculum notifications
- Real-time updates via WebSocket events

## Resource Sources

### Khan Academy
- **API**: Khan Academy REST API
- **Content**: Math, science, computing videos and exercises
- **Processing**: Automatic difficulty detection and subject mapping

### ArXiv
- **API**: ArXiv API
- **Content**: Recent research papers and academic articles
- **Processing**: Advanced content analysis and learning objective extraction

### YouTube EDU
- **API**: YouTube Data API v3
- **Content**: Educational videos and tutorials
- **Processing**: Video metadata analysis and content summarization

## NLP Processing Pipeline

### 1. Content Analysis
- **Text Extraction**: Extract text from videos, articles, and tutorials
- **Language Processing**: Tokenization, lemmatization, and stopword removal
- **Key Concept Extraction**: Identify important topics and concepts

### 2. Lesson Generation
- **Summary Creation**: Generate concise summaries using TF-IDF
- **Quiz Generation**: Create multiple-choice questions from content
- **Exercise Creation**: Generate practical exercises and activities
- **Tag Extraction**: Identify relevant learning tags and categories

### 3. Difficulty Assessment
- **Content Analysis**: Analyze text complexity and vocabulary
- **Length Consideration**: Factor in content length and depth
- **Source Mapping**: Map source difficulty levels to internal scale

## Learning Path Adaptation

### Weak Area Detection
- **Performance Analysis**: Identify concepts with low mastery scores
- **Progress Tracking**: Monitor learning progress and completion rates
- **Gap Analysis**: Find knowledge gaps in user's learning journey

### Dynamic Updates
- **New Lesson Integration**: Add relevant lessons for weak areas
- **Content Replacement**: Replace outdated lessons with fresh content
- **Priority Adjustment**: Adjust lesson priorities based on user needs

### Real-time Notifications
- **WebSocket Events**: Live updates when curriculum changes
- **User Notifications**: Alert users to new lessons and updates
- **Progress Tracking**: Real-time progress updates and achievements

## Scheduling System

### Automated Tasks
- **Weekly Resource Fetch**: Sundays at 2 AM
- **Daily Path Updates**: Every day at 6 AM
- **Weekly Lesson Replacement**: Saturdays at 3 AM

### Manual Triggers
- **Admin Refresh**: Manual curriculum refresh for administrators
- **User-specific Updates**: Targeted updates for individual users
- **Emergency Updates**: Immediate updates for critical changes

## Configuration

### Environment Variables
```bash
# YouTube API Key (optional)
YOUTUBE_API_KEY=your_youtube_api_key

# Resource fetching settings
MAX_RESOURCES_PER_SOURCE=50
RESOURCE_FETCH_INTERVAL=7  # days
```

### Database Settings
- **Resource Storage**: Stores raw content and metadata
- **Processing Queue**: Tracks resources awaiting processing
- **Update History**: Maintains history of curriculum changes

## Usage

### For Students
1. **View Fresh Lessons**: Check the "Curriculum" tab for new lessons
2. **Track Progress**: Monitor learning path progress and completion
3. **Receive Updates**: Get notified when new content is available
4. **Adaptive Learning**: Benefit from personalized lesson recommendations

### For Administrators
1. **Monitor System**: Check curriculum statistics and update logs
2. **Manual Refresh**: Trigger manual curriculum updates when needed
3. **Quality Control**: Review and approve new resources
4. **Performance Monitoring**: Track system performance and resource usage

## API Examples

### Get Fresh Lessons
```javascript
const response = await fetch('/api/curriculum/fresh-lessons', {
  headers: { Authorization: `Bearer ${token}` }
});
const data = await response.json();
```

### Start a Lesson
```javascript
const response = await fetch(`/api/curriculum/path/${lessonId}/start`, {
  method: 'POST',
  headers: { Authorization: `Bearer ${token}` }
});
```

### Update Lesson Progress
```javascript
const response = await fetch(`/api/curriculum/path/${lessonId}/progress`, {
  method: 'POST',
  headers: { 
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ progress: 0.8 })
});
```

## WebSocket Events

### Curriculum Updates
```javascript
socket.on('curriculum_update', (data) => {
  console.log('New curriculum update:', data);
  // Update UI with new lessons or changes
});
```

### Real-time Notifications
- **New Lesson Added**: When a new lesson is added to user's path
- **Lesson Replaced**: When an existing lesson is updated
- **Path Updated**: When learning path structure changes

## Performance Optimization

### Caching
- **Resource Caching**: Cache frequently accessed resources
- **Query Optimization**: Optimize database queries for better performance
- **CDN Integration**: Use CDN for static content delivery

### Scalability
- **Background Processing**: Process resources in background tasks
- **Queue Management**: Use task queues for resource processing
- **Load Balancing**: Distribute processing across multiple workers

## Monitoring and Analytics

### Metrics Tracked
- **Resource Fetch Success Rate**: Percentage of successful resource fetches
- **Processing Time**: Time taken to process resources into lesson cards
- **User Engagement**: How users interact with fresh lessons
- **Content Quality**: User feedback and completion rates

### Logging
- **Resource Fetch Logs**: Track resource fetching activities
- **Processing Logs**: Monitor lesson card generation
- **Error Logs**: Track and debug system errors
- **Performance Logs**: Monitor system performance metrics

## Troubleshooting

### Common Issues
1. **Resource Fetch Failures**: Check API keys and network connectivity
2. **Processing Errors**: Verify NLP dependencies and content format
3. **Database Issues**: Check database connections and query performance
4. **WebSocket Disconnections**: Monitor socket connections and reconnection logic

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
- **AI-Powered Content Curation**: Use machine learning for better content selection
- **Multi-language Support**: Support for multiple languages and content sources
- **Advanced Analytics**: Detailed learning analytics and insights
- **Content Quality Scoring**: Automated content quality assessment

### Integration Opportunities
- **External LMS**: Integration with Learning Management Systems
- **Content Management**: Advanced content management and editing tools
- **Collaborative Learning**: Support for group learning and collaboration
- **Mobile Optimization**: Enhanced mobile experience and offline support

## Contributing

### Development Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment variables
3. Run database migrations
4. Start the development server

### Testing
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test API endpoints and database operations
- **End-to-End Tests**: Test complete user workflows

### Code Style
- Follow PEP 8 for Python code
- Use TypeScript for frontend components
- Write comprehensive docstrings and comments
- Maintain test coverage above 80%
