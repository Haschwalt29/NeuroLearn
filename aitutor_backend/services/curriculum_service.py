import requests
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .. import db, socketio
from ..models import Resource, LessonCard, LearningPath, CurriculumUpdate, User, LearnerConceptMastery

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

class CurriculumService:
    def __init__(self):
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        
        # API endpoints for different sources
        self.sources = {
            'khan_academy': {
                'api_url': 'https://www.khanacademy.org/api/v1/topics',
                'headers': {'User-Agent': 'AI-Tutor/1.0'}
            },
            'youtube_edu': {
                'api_url': 'https://www.googleapis.com/youtube/v3/search',
                'key': 'YOUR_YOUTUBE_API_KEY'  # Replace with actual key
            },
            'arxiv': {
                'api_url': 'http://export.arxiv.org/api/query',
                'headers': {'User-Agent': 'AI-Tutor/1.0'}
            }
        }

    def fetch_new_resources(self, subjects: List[str] = None) -> List[Dict[str, Any]]:
        """Fetch new resources from various educational APIs"""
        if subjects is None:
            subjects = ['mathematics', 'computer_science', 'physics', 'chemistry', 'biology']
        
        new_resources = []
        
        # Fetch from Khan Academy
        try:
            khan_resources = self._fetch_khan_academy_resources(subjects)
            new_resources.extend(khan_resources)
        except Exception as e:
            print(f"Error fetching Khan Academy resources: {e}")
        
        # Fetch from ArXiv
        try:
            arxiv_resources = self._fetch_arxiv_resources(subjects)
            new_resources.extend(arxiv_resources)
        except Exception as e:
            print(f"Error fetching ArXiv resources: {e}")
        
        # Fetch from YouTube EDU (if API key available)
        try:
            youtube_resources = self._fetch_youtube_edu_resources(subjects)
            new_resources.extend(youtube_resources)
        except Exception as e:
            print(f"Error fetching YouTube EDU resources: {e}")
        
        return new_resources

    def _fetch_khan_academy_resources(self, subjects: List[str]) -> List[Dict[str, Any]]:
        """Fetch resources from Khan Academy API"""
        resources = []
        
        for subject in subjects:
            try:
                # Map subjects to Khan Academy topics
                topic_mapping = {
                    'mathematics': 'math',
                    'computer_science': 'computing',
                    'physics': 'science',
                    'chemistry': 'science',
                    'biology': 'science'
                }
                
                topic = topic_mapping.get(subject, 'math')
                url = f"{self.sources['khan_academy']['api_url']}/{topic}"
                
                response = requests.get(url, headers=self.sources['khan_academy']['headers'])
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data.get('children', [])[:10]:  # Limit to 10 per subject
                        resource = {
                            'title': item.get('title', ''),
                            'subject': subject,
                            'difficulty': self._determine_difficulty(item.get('title', '')),
                            'type': 'video',
                            'url': f"https://www.khanacademy.org{item.get('url', '')}",
                            'source': 'khan_academy',
                            'content': item.get('description', ''),
                            'metadata': {
                                'khan_id': item.get('id'),
                                'node_type': item.get('node_type'),
                                'description': item.get('description', '')
                            }
                        }
                        resources.append(resource)
            except Exception as e:
                print(f"Error fetching Khan Academy {subject}: {e}")
        
        return resources

    def _fetch_arxiv_resources(self, subjects: List[str]) -> List[Dict[str, Any]]:
        """Fetch recent papers from ArXiv"""
        resources = []
        
        for subject in subjects:
            try:
                # Map subjects to ArXiv categories
                category_mapping = {
                    'mathematics': 'math',
                    'computer_science': 'cs',
                    'physics': 'physics',
                    'chemistry': 'physics.chem-ph',
                    'biology': 'q-bio'
                }
                
                category = category_mapping.get(subject, 'math')
                url = f"{self.sources['arxiv']['api_url']}?search_query=cat:{category}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"
                
                response = requests.get(url, headers=self.sources['arxiv']['headers'])
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    entries = soup.find_all('entry')
                    
                    for entry in entries:
                        title = entry.find('title').text.strip() if entry.find('title') else ''
                        summary = entry.find('summary').text.strip() if entry.find('summary') else ''
                        link = entry.find('id').text.strip() if entry.find('id') else ''
                        
                        resource = {
                            'title': title,
                            'subject': subject,
                            'difficulty': 'advanced',
                            'type': 'article',
                            'url': link,
                            'source': 'arxiv',
                            'content': summary,
                            'metadata': {
                                'authors': [author.find('name').text for author in entry.find_all('author')],
                                'published': entry.find('published').text if entry.find('published') else '',
                                'categories': [cat.get('term') for cat in entry.find_all('category')]
                            }
                        }
                        resources.append(resource)
            except Exception as e:
                print(f"Error fetching ArXiv {subject}: {e}")
        
        return resources

    def _fetch_youtube_edu_resources(self, subjects: List[str]) -> List[Dict[str, Any]]:
        """Fetch educational videos from YouTube EDU"""
        resources = []
        
        # This would require YouTube API key
        # For now, return mock data
        for subject in subjects:
            mock_videos = [
                {
                    'title': f'Introduction to {subject.title()} - Complete Tutorial',
                    'subject': subject,
                    'difficulty': 'beginner',
                    'type': 'video',
                    'url': f'https://youtube.com/watch?v=mock_{subject}',
                    'source': 'youtube_edu',
                    'content': f'A comprehensive introduction to {subject} covering all the basics.',
                    'metadata': {'duration': '45:30', 'views': '1000000'}
                }
            ]
            resources.extend(mock_videos)
        
        return resources

    def _determine_difficulty(self, title: str) -> str:
        """Determine difficulty level from title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['introduction', 'basics', 'beginner', 'getting started']):
            return 'beginner'
        elif any(word in title_lower for word in ['advanced', 'expert', 'master', 'deep dive']):
            return 'advanced'
        else:
            return 'intermediate'

    def generate_lesson_cards(self, resource: Resource) -> Optional[LessonCard]:
        """Convert a resource into a structured lesson card using NLP"""
        try:
            # Extract key information using NLP
            content = resource.content or ''
            title = resource.title
            
            # Generate summary
            summary = self._generate_summary(content, title)
            
            # Generate quiz questions
            quiz_questions = self._generate_quiz_questions(content, title)
            
            # Generate exercises
            exercises = self._generate_exercises(content, title)
            
            # Extract tags and learning objectives
            tags = self._extract_tags(content, title)
            learning_objectives = self._extract_learning_objectives(content, title)
            
            # Determine difficulty score
            difficulty_score = self._calculate_difficulty_score(content, title, resource.difficulty)
            
            # Estimate time
            estimated_time = self._estimate_learning_time(content, resource.type)
            
            # Create lesson card
            lesson_card = LessonCard(
                resource_id=resource.id,
                title=title,
                summary=summary,
                quiz_questions=quiz_questions,
                exercises=exercises,
                tags=tags,
                difficulty_score=difficulty_score,
                estimated_time=estimated_time,
                learning_objectives=learning_objectives,
                prerequisites=self._extract_prerequisites(content)
            )
            
            db.session.add(lesson_card)
            db.session.commit()
            
            return lesson_card
            
        except Exception as e:
            print(f"Error generating lesson card for resource {resource.id}: {e}")
            return None

    def _generate_summary(self, content: str, title: str) -> str:
        """Generate a concise summary of the content"""
        if not content:
            return f"This lesson covers {title.lower()}."
        
        # Simple extractive summarization
        sentences = sent_tokenize(content)
        if len(sentences) <= 3:
            return content
        
        # Use TF-IDF to find most important sentences
        tfidf_matrix = self.vectorizer.fit_transform(sentences)
        sentence_scores = tfidf_matrix.sum(axis=1).A1
        
        # Get top 3 sentences
        top_indices = np.argsort(sentence_scores)[-3:]
        summary_sentences = [sentences[i] for i in sorted(top_indices)]
        
        return ' '.join(summary_sentences)

    def _generate_quiz_questions(self, content: str, title: str) -> List[Dict[str, Any]]:
        """Generate quiz questions from content"""
        questions = []
        
        if not content:
            return questions
        
        # Simple question generation based on key concepts
        sentences = sent_tokenize(content)
        key_sentences = sentences[:5]  # Take first 5 sentences
        
        for i, sentence in enumerate(key_sentences):
            if len(sentence.split()) > 10:  # Only for substantial sentences
                question = {
                    'id': f'q_{i+1}',
                    'question': f"What is the main concept discussed in: '{sentence[:100]}...'?",
                    'options': [
                        "A concept related to the topic",
                        "A fundamental principle",
                        "An advanced technique",
                        "A basic definition"
                    ],
                    'correct_answer': 1,
                    'explanation': sentence
                }
                questions.append(question)
        
        return questions

    def _generate_exercises(self, content: str, title: str) -> List[Dict[str, Any]]:
        """Generate practical exercises from content"""
        exercises = []
        
        # Generate different types of exercises based on content
        exercise_types = [
            {
                'type': 'practice',
                'title': f'Practice {title}',
                'description': f'Apply the concepts from {title} in a practical scenario.',
                'instructions': 'Complete the following tasks based on what you learned.'
            },
            {
                'type': 'reflection',
                'title': f'Reflect on {title}',
                'description': f'Think critically about the concepts in {title}.',
                'instructions': 'Write a brief reflection on how this topic applies to your learning goals.'
            }
        ]
        
        for i, exercise in enumerate(exercise_types):
            exercises.append({
                'id': f'ex_{i+1}',
                **exercise
            })
        
        return exercises

    def _extract_tags(self, content: str, title: str) -> List[str]:
        """Extract relevant learning tags"""
        # Simple keyword extraction
        words = word_tokenize(content.lower())
        words = [self.lemmatizer.lemmatize(word) for word in words if word.isalpha() and word not in self.stop_words]
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top 5 most frequent words as tags
        tags = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        return [tag[0] for tag in tags]

    def _extract_learning_objectives(self, content: str, title: str) -> List[str]:
        """Extract learning objectives from content"""
        objectives = [
            f"Understand the key concepts of {title.lower()}",
            f"Apply {title.lower()} principles in practice",
            f"Analyze problems related to {title.lower()}"
        ]
        
        return objectives

    def _calculate_difficulty_score(self, content: str, title: str, difficulty: str) -> float:
        """Calculate difficulty score (0-1)"""
        difficulty_mapping = {
            'beginner': 0.2,
            'intermediate': 0.5,
            'advanced': 0.8
        }
        
        base_score = difficulty_mapping.get(difficulty, 0.5)
        
        # Adjust based on content length and complexity
        if content:
            word_count = len(word_tokenize(content))
            if word_count > 1000:
                base_score += 0.1
            if word_count < 200:
                base_score -= 0.1
        
        return max(0.0, min(1.0, base_score))

    def _estimate_learning_time(self, content: str, resource_type: str) -> int:
        """Estimate learning time in minutes"""
        base_times = {
            'video': 30,
            'article': 15,
            'tutorial': 45,
            'exercise': 20
        }
        
        base_time = base_times.get(resource_type, 30)
        
        if content:
            word_count = len(word_tokenize(content))
            # Estimate 200 words per minute reading speed
            reading_time = max(5, word_count // 200)
            return min(120, max(base_time, reading_time))
        
        return base_time

    def _extract_prerequisites(self, content: str) -> List[str]:
        """Extract prerequisite topics"""
        # Simple keyword-based prerequisite detection
        prerequisite_keywords = ['requires', 'assumes', 'prerequisite', 'before', 'previous']
        prerequisites = []
        
        sentences = sent_tokenize(content)
        for sentence in sentences:
            for keyword in prerequisite_keywords:
                if keyword in sentence.lower():
                    # Extract the topic mentioned after the keyword
                    words = sentence.split()
                    try:
                        keyword_index = words.index(keyword)
                        if keyword_index + 1 < len(words):
                            prerequisites.append(words[keyword_index + 1])
                    except ValueError:
                        continue
        
        return list(set(prerequisites))

    def update_learning_paths(self, user_id: int) -> List[Dict[str, Any]]:
        """Update user's learning path with new relevant lessons"""
        updates = []
        
        try:
            # Get user's weak areas from performance data
            weak_areas = self._get_user_weak_areas(user_id)
            
            # Get user's current learning path
            current_path = LearningPath.query.filter_by(user_id=user_id, status='upcoming').all()
            current_lesson_ids = [lp.lesson_card_id for lp in current_path]
            
            # Find new lessons that match weak areas
            for area in weak_areas:
                new_lessons = LessonCard.query.filter(
                    LessonCard.tags.contains([area]),
                    LessonCard.is_active == True,
                    ~LessonCard.id.in_(current_lesson_ids)
                ).limit(3).all()
                
                for lesson in new_lessons:
                    # Add to learning path
                    learning_path = LearningPath(
                        user_id=user_id,
                        lesson_card_id=lesson.id,
                        priority=len(current_path) + 1,
                        replacement_reason=f"Added for weak area: {area}"
                    )
                    db.session.add(learning_path)
                    
                    # Create update notification
                    update = CurriculumUpdate(
                        user_id=user_id,
                        update_type='new_lesson',
                        lesson_card_id=lesson.id,
                        message=f"New lesson added: {lesson.title}",
                        metadata={'reason': 'weak_area', 'area': area}
                    )
                    db.session.add(update)
                    
                    updates.append({
                        'type': 'new_lesson',
                        'lesson_id': lesson.id,
                        'title': lesson.title,
                        'reason': f'Added for weak area: {area}'
                    })
            
            db.session.commit()
            
            # Emit socket event
            if updates:
                socketio.emit('curriculum_update', {
                    'user_id': user_id,
                    'updates': updates
                })
            
        except Exception as e:
            print(f"Error updating learning paths for user {user_id}: {e}")
            db.session.rollback()
        
        return updates

    def _get_user_weak_areas(self, user_id: int) -> List[str]:
        """Get user's weak learning areas from performance data"""
        weak_areas = []
        
        try:
            # Get concept mastery data
            mastery_data = LearnerConceptMastery.query.filter_by(user_id=user_id).all()
            
            for mastery in mastery_data:
                if mastery.mastery_score < 0.5:  # Weak area
                    # Map concept to subject area
                    concept = mastery.concept
                    if concept:
                        subject = concept.subject or 'general'
                        weak_areas.append(subject.lower())
            
            # If no mastery data, return common subjects
            if not weak_areas:
                weak_areas = ['mathematics', 'computer_science']
                
        except Exception as e:
            print(f"Error getting weak areas for user {user_id}: {e}")
            weak_areas = ['mathematics', 'computer_science']
        
        return list(set(weak_areas))

    def replace_outdated_lessons(self, user_id: int) -> List[Dict[str, Any]]:
        """Replace outdated lessons with fresh content"""
        replacements = []
        
        try:
            # Get lessons older than 30 days
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            old_lessons = LearningPath.query.join(LessonCard).filter(
                LearningPath.user_id == user_id,
                LearningPath.status == 'upcoming',
                LessonCard.created_at < cutoff_date
            ).all()
            
            for old_path in old_lessons:
                old_lesson = old_path.lesson_card
                
                # Find a newer lesson on the same topic
                new_lesson = LessonCard.query.filter(
                    LessonCard.tags.overlap(old_lesson.tags),
                    LessonCard.created_at > cutoff_date,
                    LessonCard.is_active == True,
                    LessonCard.id != old_lesson.id
                ).first()
                
                if new_lesson:
                    # Update the learning path
                    old_path.lesson_card_id = new_lesson.id
                    old_path.replaced_from = old_lesson.id
                    old_path.replacement_reason = "Updated with fresh content"
                    
                    # Create update notification
                    update = CurriculumUpdate(
                        user_id=user_id,
                        update_type='replaced_lesson',
                        lesson_card_id=new_lesson.id,
                        old_lesson_id=old_lesson.id,
                        message=f"Lesson updated: {old_lesson.title} → {new_lesson.title}",
                        metadata={'reason': 'fresh_content'}
                    )
                    db.session.add(update)
                    
                    replacements.append({
                        'type': 'replaced_lesson',
                        'old_lesson_id': old_lesson.id,
                        'new_lesson_id': new_lesson.id,
                        'old_title': old_lesson.title,
                        'new_title': new_lesson.title
                    })
            
            db.session.commit()
            
            # Emit socket event
            if replacements:
                socketio.emit('curriculum_update', {
                    'user_id': user_id,
                    'updates': replacements
                })
            
        except Exception as e:
            print(f"Error replacing outdated lessons for user {user_id}: {e}")
            db.session.rollback()
        
        return replacements

    def get_user_learning_path(self, user_id: int) -> List[Dict[str, Any]]:
        """Get user's current learning path"""
        try:
            learning_paths = LearningPath.query.filter_by(user_id=user_id).order_by(LearningPath.priority.desc()).all()
            
            path_data = []
            for lp in learning_paths:
                lesson = lp.lesson_card
                path_data.append({
                    'id': lp.id,
                    'lesson_id': lesson.id,
                    'title': lesson.title,
                    'summary': lesson.summary,
                    'status': lp.status,
                    'priority': lp.priority,
                    'progress': lp.progress,
                    'estimated_time': lesson.estimated_time,
                    'difficulty': lesson.difficulty_score,
                    'tags': lesson.tags,
                    'is_new': lp.added_at > datetime.utcnow() - timedelta(days=7),
                    'replaced_from': lp.replaced_from,
                    'replacement_reason': lp.replacement_reason
                })
            
            return path_data
            
        except Exception as e:
            print(f"Error getting learning path for user {user_id}: {e}")
            return []

    def get_curriculum_updates(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent curriculum updates for user"""
        try:
            updates = CurriculumUpdate.query.filter_by(user_id=user_id).order_by(CurriculumUpdate.created_at.desc()).limit(limit).all()
            
            update_data = []
            for update in updates:
                lesson = update.lesson_card
                update_data.append({
                    'id': update.id,
                    'type': update.update_type,
                    'message': update.message,
                    'lesson_title': lesson.title if lesson else None,
                    'created_at': update.created_at.isoformat(),
                    'is_read': update.is_read,
                    'metadata': update.metadata
                })
            
            return update_data
            
        except Exception as e:
            print(f"Error getting curriculum updates for user {user_id}: {e}")
            return []


# Global service instance
curriculum_service = CurriculumService()
