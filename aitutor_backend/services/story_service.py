from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .. import db
from ..models import (
    User, Story, Chapter, StoryQuest, StoryProgress, StoryReward, 
    UserXP, UserQuest, TopicMastery, PerformanceLog
)


class StoryService:
    """Service for managing story-driven quest progression"""
    
    def __init__(self):
        pass
    
    def get_current_story_progress(self, user_id: int) -> Dict:
        """Get user's current story progress with unlocked content"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        # Get or create story progress
        story_progress = StoryProgress.query.filter_by(user_id=user_id).first()
        if not story_progress:
            # Start with the first active story
            first_story = Story.query.filter_by(is_active=True).order_by(Story.id).first()
            if not first_story:
                return {"error": "No active stories available"}
            
            story_progress = self._initialize_story_progress(user_id, first_story.id)
        
        story = Story.query.get(story_progress.story_id)
        chapters = Chapter.query.filter_by(story_id=story.id).order_by(Chapter.order).all()
        
        # Determine unlocked chapters
        unlocked_chapters = []
        for chapter in chapters:
            if self._is_chapter_unlocked(user_id, chapter, story_progress):
                unlocked_chapters.append(self._format_chapter_data(chapter, story_progress))
        
        return {
            "story": self._format_story_data(story),
            "current_chapter": story_progress.current_chapter_id,
            "unlocked_chapters": unlocked_chapters,
            "total_story_xp": story_progress.total_story_xp,
            "completed_chapters": story_progress.completed_chapters,
            "completed_quests": story_progress.completed_quests
        }
    
    def update_story_progress(self, user_id: int, quest_id: int, score: float, 
                            time_spent: int = 0) -> Dict:
        """Update story progress when a quest is completed"""
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}
        
        quest = StoryQuest.query.get(quest_id)
        if not quest:
            return {"error": "Quest not found"}
        
        story_progress = StoryProgress.query.filter_by(
            user_id=user_id, story_id=quest.chapter.story_id
        ).first()
        
        if not story_progress:
            return {"error": "Story progress not found"}
        
        # Check if quest is already completed
        if quest_id in story_progress.completed_quests:
            return {"message": "Quest already completed", "rewards": []}
        
        # Check completion criteria
        completion_criteria = quest.completion_criteria or {}
        min_score = completion_criteria.get("min_score", 70)
        
        if score < min_score:
            return {"message": "Quest not completed - score too low", "rewards": []}
        
        # Mark quest as completed
        story_progress.completed_quests.append(quest_id)
        story_progress.total_story_xp += quest.reward_xp
        story_progress.last_updated = datetime.utcnow()
        
        # Award XP
        from .gamification_service import GamificationService
        gamification_service = GamificationService()
        xp_result = gamification_service.add_xp(
            user_id, quest.reward_xp, "quest_complete", quest_id, 
            f"Completed quest: {quest.title}"
        )
        
        rewards = [{
            "type": "xp",
            "amount": quest.reward_xp,
            "description": f"Completed {quest.title}"
        }]
        
        # Award badge if specified
        if quest.reward_badge:
            badge_result = gamification_service.check_and_award_badges(user_id)
            if badge_result.get("new_badges"):
                rewards.append({
                    "type": "badge",
                    "badge_name": quest.reward_badge,
                    "description": f"Earned badge: {quest.reward_badge}"
                })
        
        # Check for chapter completion
        chapter_rewards = self._check_chapter_completion(user_id, quest.chapter_id, story_progress)
        rewards.extend(chapter_rewards)
        
        # Check for story unlocks
        unlock_rewards = self._check_story_unlocks(user_id, story_progress)
        rewards.extend(unlock_rewards)
        
        db.session.commit()
        
        return {
            "message": "Quest completed successfully",
            "rewards": rewards,
            "xp_gained": quest.reward_xp,
            "new_unlocks": unlock_rewards
        }
    
    def _initialize_story_progress(self, user_id: int, story_id: int) -> StoryProgress:
        """Initialize story progress for a new user"""
        story_progress = StoryProgress(
            user_id=user_id,
            story_id=story_id,
            current_chapter_id=None,
            completed_chapters=[],
            completed_quests=[],
            total_story_xp=0
        )
        db.session.add(story_progress)
        db.session.commit()
        return story_progress
    
    def _is_chapter_unlocked(self, user_id: int, chapter: Chapter, 
                           story_progress: StoryProgress) -> bool:
        """Check if a chapter is unlocked for the user"""
        # First chapter is always unlocked
        if chapter.order == 1:
            return True
        
        # Check if previous chapter is completed
        previous_chapter = Chapter.query.filter_by(
            story_id=chapter.story_id, order=chapter.order - 1
        ).first()
        
        if previous_chapter and previous_chapter.id not in story_progress.completed_chapters:
            return False
        
        # Check unlock requirements
        requirements = chapter.unlock_requirements or {}
        
        # Check XP requirement
        xp_required = requirements.get("xp_required", 0)
        if story_progress.total_story_xp < xp_required:
            return False
        
        # Check topic mastery requirements
        topics_mastered = requirements.get("topics_mastered", [])
        for topic in topics_mastered:
            mastery = TopicMastery.query.filter_by(
                user_id=user_id, topic=topic
            ).first()
            if not mastery or mastery.mastery_score < 0.8:  # 80% mastery required
                return False
        
        return True
    
    def _check_chapter_completion(self, user_id: int, chapter_id: int, 
                                story_progress: StoryProgress) -> List[Dict]:
        """Check if a chapter is completed and award rewards"""
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return []
        
        # Check if chapter is already completed
        if chapter_id in story_progress.completed_chapters:
            return []
        
        # Get all quests in the chapter
        chapter_quests = StoryQuest.query.filter_by(chapter_id=chapter_id).all()
        quest_ids = [q.id for q in chapter_quests]
        
        # Check if all quests are completed
        completed_quests = set(story_progress.completed_quests)
        if not all(qid in completed_quests for qid in quest_ids):
            return []
        
        # Mark chapter as completed
        story_progress.completed_chapters.append(chapter_id)
        
        # Award chapter completion XP
        chapter_xp = 100  # Base XP for chapter completion
        story_progress.total_story_xp += chapter_xp
        
        # Award XP through gamification service
        from .gamification_service import GamificationService
        gamification_service = GamificationService()
        gamification_service.add_xp(
            user_id, chapter_xp, "chapter_complete", chapter_id,
            f"Completed chapter: {chapter.title}"
        )
        
        # Create story reward
        reward = StoryReward(
            user_id=user_id,
            story_id=chapter.story_id,
            reward_type="chapter_unlock",
            reward_data={
                "chapter_id": chapter_id,
                "chapter_title": chapter.title,
                "xp_gained": chapter_xp
            }
        )
        db.session.add(reward)
        
        return [{
            "type": "chapter_complete",
            "chapter_title": chapter.title,
            "xp_gained": chapter_xp,
            "description": f"Chapter completed: {chapter.title}"
        }]
    
    def _check_story_unlocks(self, user_id: int, story_progress: StoryProgress) -> List[Dict]:
        """Check for new story unlocks and create rewards"""
        story = Story.query.get(story_progress.story_id)
        chapters = Chapter.query.filter_by(story_id=story.id).order_by(Chapter.order).all()
        
        unlocks = []
        
        for chapter in chapters:
            if (chapter.id not in story_progress.completed_chapters and 
                self._is_chapter_unlocked(user_id, chapter, story_progress)):
                
                # Update current chapter if it's the next one
                if (not story_progress.current_chapter_id or 
                    chapter.order > story_progress.current_chapter.order):
                    story_progress.current_chapter_id = chapter.id
                
                # Create unlock reward
                reward = StoryReward(
                    user_id=user_id,
                    story_id=story.id,
                    reward_type="chapter_unlock",
                    reward_data={
                        "chapter_id": chapter.id,
                        "chapter_title": chapter.title,
                        "chapter_description": chapter.description
                    }
                )
                db.session.add(reward)
                
                unlocks.append({
                    "type": "chapter_unlock",
                    "chapter_title": chapter.title,
                    "chapter_description": chapter.description,
                    "description": f"New chapter unlocked: {chapter.title}"
                })
        
        return unlocks
    
    def _format_story_data(self, story: Story) -> Dict:
        """Format story data for API response"""
        return {
            "id": story.id,
            "title": story.title,
            "description": story.description,
            "theme": story.theme,
            "cover_image": story.cover_image,
            "created_at": story.created_at.isoformat()
        }
    
    def _format_chapter_data(self, chapter: Chapter, story_progress: StoryProgress) -> Dict:
        """Format chapter data for API response"""
        quests = StoryQuest.query.filter_by(chapter_id=chapter.id).all()
        
        return {
            "id": chapter.id,
            "title": chapter.title,
            "description": chapter.description,
            "order": chapter.order,
            "storyline_text": chapter.storyline_text,
            "visual_assets": chapter.visual_assets,
            "is_completed": chapter.id in story_progress.completed_chapters,
            "quests": [self._format_quest_data(quest, story_progress) for quest in quests]
        }
    
    def _format_quest_data(self, quest: StoryQuest, story_progress: StoryProgress) -> Dict:
        """Format quest data for API response"""
        return {
            "id": quest.id,
            "title": quest.title,
            "description": quest.description,
            "quest_type": quest.quest_type,
            "difficulty_level": quest.difficulty_level,
            "topics": quest.topics,
            "required_xp": quest.required_xp,
            "reward_xp": quest.reward_xp,
            "reward_badge": quest.reward_badge,
            "story_context": quest.story_context,
            "is_completed": quest.id in story_progress.completed_quests,
            "completion_criteria": quest.completion_criteria
        }
    
    def get_story_rewards(self, user_id: int, story_id: int) -> List[Dict]:
        """Get unviewed story rewards for a user"""
        rewards = StoryReward.query.filter_by(
            user_id=user_id, story_id=story_id, is_viewed=False
        ).order_by(StoryReward.created_at.desc()).all()
        
        return [{
            "id": reward.id,
            "reward_type": reward.reward_type,
            "reward_data": reward.reward_data,
            "created_at": reward.created_at.isoformat()
        } for reward in rewards]
    
    def mark_reward_viewed(self, user_id: int, reward_id: int) -> bool:
        """Mark a story reward as viewed"""
        reward = StoryReward.query.filter_by(
            id=reward_id, user_id=user_id
        ).first()
        
        if reward:
            reward.is_viewed = True
            db.session.commit()
            return True
        return False
