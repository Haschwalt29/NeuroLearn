from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit
import logging

from .curriculum_service import curriculum_service
from .. import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CurriculumScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.setup_jobs()
        
    def setup_jobs(self):
        """Setup scheduled jobs for curriculum updates"""
        
        # Weekly resource fetching (Sundays at 2 AM)
        self.scheduler.add_job(
            func=self.weekly_resource_fetch,
            trigger=CronTrigger(day_of_week=0, hour=2, minute=0),
            id='weekly_resource_fetch',
            name='Weekly Resource Fetch',
            replace_existing=True
        )
        
        # Daily learning path updates (Every day at 6 AM)
        self.scheduler.add_job(
            func=self.daily_learning_path_update,
            trigger=CronTrigger(hour=6, minute=0),
            id='daily_learning_path_update',
            name='Daily Learning Path Update',
            replace_existing=True
        )
        
        # Weekly lesson replacement (Saturdays at 3 AM)
        self.scheduler.add_job(
            func=self.weekly_lesson_replacement,
            trigger=CronTrigger(day_of_week=6, hour=3, minute=0),
            id='weekly_lesson_replacement',
            name='Weekly Lesson Replacement',
            replace_existing=True
        )
        
        logger.info("Curriculum scheduler jobs configured")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Curriculum scheduler started")
            
            # Register cleanup function
            atexit.register(self.shutdown)
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Curriculum scheduler stopped")
    
    def weekly_resource_fetch(self):
        """Fetch new resources from external APIs"""
        try:
            logger.info("Starting weekly resource fetch...")
            
            # Get all active users to determine subjects
            from ..models import User
            users = User.query.filter_by(role='learner').all()
            
            # Collect unique subjects from user profiles
            subjects = set()
            for user in users:
                # Get user's learning areas from their progress
                from ..models import LearnerConceptMastery
                user_concepts = LearnerConceptMastery.query.filter_by(user_id=user.id).all()
                for concept in user_concepts:
                    if concept.concept and concept.concept.subject:
                        subjects.add(concept.concept.subject.lower())
            
            # Default subjects if none found
            if not subjects:
                subjects = {'mathematics', 'computer_science', 'physics', 'chemistry', 'biology'}
            
            # Fetch new resources
            new_resources = curriculum_service.fetch_new_resources(list(subjects))
            
            # Store resources in database
            from ..models import Resource
            stored_count = 0
            for resource_data in new_resources:
                # Check if resource already exists
                existing = Resource.query.filter_by(
                    url=resource_data['url'],
                    source=resource_data['source']
                ).first()
                
                if not existing:
                    resource = Resource(
                        title=resource_data['title'],
                        subject=resource_data['subject'],
                        difficulty=resource_data['difficulty'],
                        type=resource_data['type'],
                        url=resource_data['url'],
                        source=resource_data['source'],
                        content=resource_data['content'],
                        metadata=resource_data.get('metadata', {})
                    )
                    db.session.add(resource)
                    stored_count += 1
            
            db.session.commit()
            logger.info(f"Weekly resource fetch completed. Stored {stored_count} new resources.")
            
        except Exception as e:
            logger.error(f"Error in weekly resource fetch: {e}")
            db.session.rollback()
    
    def daily_learning_path_update(self):
        """Update learning paths for all users"""
        try:
            logger.info("Starting daily learning path update...")
            
            from ..models import User
            users = User.query.filter_by(role='learner').all()
            
            total_updates = 0
            for user in users:
                updates = curriculum_service.update_learning_paths(user.id)
                total_updates += len(updates)
            
            logger.info(f"Daily learning path update completed. {total_updates} updates made.")
            
        except Exception as e:
            logger.error(f"Error in daily learning path update: {e}")
    
    def weekly_lesson_replacement(self):
        """Replace outdated lessons with fresh content"""
        try:
            logger.info("Starting weekly lesson replacement...")
            
            from ..models import User
            users = User.query.filter_by(role='learner').all()
            
            total_replacements = 0
            for user in users:
                replacements = curriculum_service.replace_outdated_lessons(user.id)
                total_replacements += len(replacements)
            
            logger.info(f"Weekly lesson replacement completed. {total_replacements} lessons replaced.")
            
        except Exception as e:
            logger.error(f"Error in weekly lesson replacement: {e}")
    
    def process_pending_resources(self):
        """Process resources that haven't been converted to lesson cards"""
        try:
            logger.info("Processing pending resources...")
            
            from ..models import Resource
            pending_resources = Resource.query.filter_by(processed=False, is_active=True).limit(50).all()
            
            processed_count = 0
            for resource in pending_resources:
                try:
                    lesson_card = curriculum_service.generate_lesson_cards(resource)
                    if lesson_card:
                        resource.processed = True
                        processed_count += 1
                        logger.info(f"Processed resource: {resource.title}")
                except Exception as e:
                    logger.error(f"Error processing resource {resource.id}: {e}")
            
            db.session.commit()
            logger.info(f"Processed {processed_count} resources into lesson cards.")
            
        except Exception as e:
            logger.error(f"Error processing pending resources: {e}")
            db.session.rollback()
    
    def manual_refresh(self, user_id: int = None):
        """Manually trigger curriculum refresh"""
        try:
            logger.info(f"Manual curriculum refresh triggered for user {user_id}")
            
            if user_id:
                # Refresh for specific user
                curriculum_service.update_learning_paths(user_id)
                curriculum_service.replace_outdated_lessons(user_id)
            else:
                # Refresh for all users
                from ..models import User
                users = User.query.filter_by(role='learner').all()
                
                for user in users:
                    curriculum_service.update_learning_paths(user.id)
                    curriculum_service.replace_outdated_lessons(user.id)
            
            logger.info("Manual curriculum refresh completed.")
            
        except Exception as e:
            logger.error(f"Error in manual curriculum refresh: {e}")


# Global scheduler instance
curriculum_scheduler = CurriculumScheduler()
