from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from ..models import (
    Quest, UserQuest, UserXP, UserBadge, Badge, 
    TopicMastery, PerformanceLog, EmotionLog, User
)
from .. import db


class QuestEngine:
    """Engine for generating and managing story-driven quests"""
    
    def __init__(self):
        self.story_themes = {
            "adventure": {
                "titles": ["The Lost Code", "Dungeon of Algorithms", "Quest for Knowledge"],
                "descriptions": "Embark on an epic journey through the digital realm..."
            },
            "mystery": {
                "titles": ["The Case of the Missing Function", "Debugging Detective", "The Cryptic Code"],
                "descriptions": "Solve mysterious puzzles and uncover hidden secrets..."
            },
            "heroic": {
                "titles": ["Rise of the Code Warrior", "Defender of Data", "The Algorithm Avenger"],
                "descriptions": "Become a hero in the world of programming and save the day..."
            },
            "scientific": {
                "titles": ["The Lab of Logic", "Experiment with Code", "The Research Quest"],
                "descriptions": "Conduct experiments and discover new programming techniques..."
            }
        }
        
        self.difficulty_multipliers = {
            "easy": 1.0,
            "medium": 1.5,
            "hard": 2.0,
            "expert": 3.0
        }
    
    def generate_quest_from_weaknesses(self, user_id: int) -> Optional[Quest]:
        """
        Generate a quest based on user's weak topics
        
        Args:
            user_id: User ID
            
        Returns:
            Generated Quest or None if no weaknesses found
        """
        # Get user's weak topics (mastery < 40%)
        weak_topics = TopicMastery.query.filter(
            TopicMastery.user_id == user_id,
            TopicMastery.mastery_score < 40.0
        ).all()
        
        if not weak_topics:
            return None
        
        # Select 2-3 weak topics for the quest
        selected_topics = weak_topics[:3] if len(weak_topics) >= 3 else weak_topics
        
        # Choose a story theme
        theme = self._select_theme_for_topics(selected_topics)
        
        # Generate quest content
        quest_title = self._generate_quest_title(theme, selected_topics)
        quest_description = self._generate_quest_description(theme, selected_topics)
        
        # Create required tasks
        required_tasks = self._generate_quest_tasks(selected_topics, theme)
        
        # Calculate rewards based on difficulty
        difficulty = self._calculate_difficulty(selected_topics)
        xp_reward = int(100 * self.difficulty_multipliers[difficulty])
        
        # Create the quest
        quest = Quest(
            title=quest_title,
            description=quest_description,
            story_theme=theme,
            difficulty=difficulty,
            category="mastery",
            required_topics=[topic.topic for topic in selected_topics],
            required_tasks=required_tasks,
            xp_reward=xp_reward,
            estimated_duration=len(required_tasks) * 2,  # 2 days per task
            is_active=True,
            is_repeatable=False
        )
        
        db.session.add(quest)
        db.session.commit()
        
        return quest
    
    def _select_theme_for_topics(self, topics: List[TopicMastery]) -> str:
        """Select appropriate story theme based on topics"""
        topic_names = [topic.topic.lower() for topic in topics]
        
        # Simple theme selection based on topic keywords
        if any(keyword in " ".join(topic_names) for keyword in ["algorithm", "data", "structure"]):
            return "scientific"
        elif any(keyword in " ".join(topic_names) for keyword in ["debug", "error", "problem"]):
            return "mystery"
        elif any(keyword in " ".join(topic_names) for keyword in ["advanced", "complex", "expert"]):
            return "heroic"
        else:
            return "adventure"
    
    def _generate_quest_title(self, theme: str, topics: List[TopicMastery]) -> str:
        """Generate quest title based on theme and topics"""
        theme_data = self.story_themes[theme]
        base_title = theme_data["titles"][0]  # Use first title for simplicity
        
        if len(topics) == 1:
            return f"{base_title}: {topics[0].topic}"
        else:
            return f"{base_title}: Master Multiple Skills"
    
    def _generate_quest_description(self, theme: str, topics: List[TopicMastery]) -> str:
        """Generate quest description"""
        theme_data = self.story_themes[theme]
        base_description = theme_data["descriptions"]
        
        topic_list = ", ".join([topic.topic for topic in topics])
        
        return f"{base_description} Master the following topics: {topic_list}. Complete all tasks to earn rewards and unlock new content!"
    
    def _generate_quest_tasks(self, topics: List[TopicMastery], theme: str) -> List[Dict]:
        """Generate quest tasks based on topics and theme"""
        tasks = []
        
        for i, topic in enumerate(topics):
            task = {
                "id": f"task_{i+1}",
                "title": f"Master {topic.topic}",
                "description": f"Complete quizzes and exercises related to {topic.topic}",
                "type": "mastery",
                "target_mastery": 70.0,  # Target 70% mastery
                "topic": topic.topic,
                "xp_reward": 50
            }
            tasks.append(task)
        
        # Add a final challenge task
        final_task = {
            "id": "final_challenge",
            "title": "Final Challenge",
            "description": f"Complete a comprehensive test covering all topics",
            "type": "comprehensive_test",
            "topics": [topic.topic for topic in topics],
            "xp_reward": 100
        }
        tasks.append(final_task)
        
        return tasks
    
    def _calculate_difficulty(self, topics: List[TopicMastery]) -> str:
        """Calculate quest difficulty based on topics"""
        avg_mastery = sum(topic.mastery_score for topic in topics) / len(topics)
        
        if avg_mastery < 20:
            return "expert"
        elif avg_mastery < 30:
            return "hard"
        elif avg_mastery < 40:
            return "medium"
        else:
            return "easy"
    
    def start_quest(self, user_id: int, quest_id: int) -> Dict:
        """
        Start a quest for a user
        
        Args:
            user_id: User ID
            quest_id: Quest ID
            
        Returns:
            Dictionary with quest start result
        """
        quest = Quest.query.get(quest_id)
        if not quest:
            return {"error": "Quest not found"}
        
        # Check if user already has this quest
        existing_quest = UserQuest.query.filter_by(
            user_id=user_id, 
            quest_id=quest_id
        ).first()
        
        if existing_quest:
            if existing_quest.status == "active":
                return {"error": "Quest already active"}
            elif existing_quest.status == "completed" and not quest.is_repeatable:
                return {"error": "Quest already completed and not repeatable"}
        
        # Check prerequisites
        if quest.prerequisites:
            if not self._check_prerequisites(user_id, quest.prerequisites):
                return {"error": "Prerequisites not met"}
        
        # Create or update user quest
        if existing_quest:
            user_quest = existing_quest
            user_quest.status = "active"
            user_quest.started_at = datetime.utcnow()
            user_quest.deadline = datetime.utcnow() + timedelta(days=quest.estimated_duration)
        else:
            user_quest = UserQuest(
                user_id=user_id,
                quest_id=quest_id,
                status="active",
                started_at=datetime.utcnow(),
                deadline=datetime.utcnow() + timedelta(days=quest.estimated_duration),
                progress_percentage=0.0,
                completed_tasks=[],
                current_task_index=0
            )
            db.session.add(user_quest)
        
        db.session.commit()
        
        return {
            "success": True,
            "quest_id": quest_id,
            "status": "active",
            "deadline": user_quest.deadline.isoformat(),
            "tasks": quest.required_tasks
        }
    
    def _check_prerequisites(self, user_id: int, prerequisites: Dict) -> bool:
        """Check if user meets quest prerequisites"""
        # Check required badges
        if "badges" in prerequisites:
            required_badges = prerequisites["badges"]
            user_badges = UserBadge.query.filter_by(user_id=user_id).all()
            user_badge_ids = [ub.badge_id for ub in user_badges]
            
            for badge_id in required_badges:
                if badge_id not in user_badge_ids:
                    return False
        
        # Check required quests
        if "quests" in prerequisites:
            required_quests = prerequisites["quests"]
            completed_quests = UserQuest.query.filter(
                UserQuest.user_id == user_id,
                UserQuest.status == "completed"
            ).all()
            completed_quest_ids = [uq.quest_id for uq in completed_quests]
            
            for quest_id in required_quests:
                if quest_id not in completed_quest_ids:
                    return False
        
        return True
    
    def complete_quest_task(self, user_id: int, quest_id: int, task_id: str, 
                          completion_data: Dict) -> Dict:
        """
        Complete a quest task and update progress
        
        Args:
            user_id: User ID
            quest_id: Quest ID
            task_id: Task ID
            completion_data: Data about task completion
            
        Returns:
            Dictionary with completion result
        """
        user_quest = UserQuest.query.filter_by(
            user_id=user_id, 
            quest_id=quest_id
        ).first()
        
        if not user_quest or user_quest.status != "active":
            return {"error": "Quest not active"}
        
        quest = Quest.query.get(quest_id)
        if not quest:
            return {"error": "Quest not found"}
        
        # Check if task is already completed
        completed_tasks = user_quest.completed_tasks or []
        if task_id in completed_tasks:
            return {"error": "Task already completed"}
        
        # Add task to completed list
        completed_tasks.append(task_id)
        user_quest.completed_tasks = completed_tasks
        
        # Update progress
        total_tasks = len(quest.required_tasks)
        completed_count = len(completed_tasks)
        progress_percentage = (completed_count / total_tasks) * 100
        user_quest.progress_percentage = progress_percentage
        
        # Award XP for task completion
        task_xp = 0
        for task in quest.required_tasks:
            if task["id"] == task_id:
                task_xp = task.get("xp_reward", 0)
                break
        
        if task_xp > 0:
            self._award_xp(user_id, task_xp, "quest_task", quest_id, f"Completed task: {task_id}")
        
        # Check if quest is complete
        if completed_count >= total_tasks:
            return self._complete_quest(user_id, quest_id, user_quest, quest)
        
        db.session.commit()
        
        return {
            "success": True,
            "task_completed": task_id,
            "progress_percentage": progress_percentage,
            "xp_earned": task_xp,
            "remaining_tasks": total_tasks - completed_count
        }
    
    def _complete_quest(self, user_id: int, quest_id: int, user_quest: UserQuest, quest: Quest) -> Dict:
        """Complete the entire quest and award final rewards"""
        user_quest.status = "completed"
        user_quest.completed_at = datetime.utcnow()
        user_quest.progress_percentage = 100.0
        
        # Award quest completion XP
        quest_xp = quest.xp_reward
        user_quest.xp_earned = quest_xp
        self._award_xp(user_id, quest_xp, "quest_complete", quest_id, f"Completed quest: {quest.title}")
        
        # Award badge if available
        badge_earned = None
        if quest.badge_reward_id:
            badge = Badge.query.get(quest.badge_reward_id)
            if badge:
                # Check if user already has this badge
                existing_badge = UserBadge.query.filter_by(
                    user_id=user_id,
                    badge_id=badge.id
                ).first()
                
                if not existing_badge:
                    user_badge = UserBadge(
                        user_id=user_id,
                        badge_id=badge.id,
                        progress_data={"quest_id": quest_id}
                    )
                    db.session.add(user_badge)
                    
                    # Award badge XP
                    if badge.xp_reward > 0:
                        self._award_xp(user_id, badge.xp_reward, "badge_earned", badge.id, f"Earned badge: {badge.name}")
                    
                    badge_earned = {
                        "id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "icon": badge.icon,
                        "rarity": badge.rarity
                    }
        
        db.session.commit()
        
        return {
            "success": True,
            "quest_completed": True,
            "quest_id": quest_id,
            "xp_earned": quest_xp,
            "badge_earned": badge_earned,
            "completion_time": user_quest.completed_at.isoformat()
        }
    
    def _award_xp(self, user_id: int, amount: int, source: str, source_id: int, description: str):
        """Award XP to user and update level"""
        # Get or create user XP profile
        user_xp = UserXP.query.filter_by(user_id=user_id).first()
        if not user_xp:
            user_xp = UserXP(user_id=user_id)
            db.session.add(user_xp)
        
        # Add XP
        user_xp.total_xp += amount
        user_xp.xp_in_current_level += amount
        
        # Check for level up
        levels_gained = 0
        while user_xp.xp_in_current_level >= user_xp.xp_to_next_level:
            user_xp.xp_in_current_level -= user_xp.xp_to_next_level
            user_xp.current_level += 1
            levels_gained += 1
            
            # Calculate XP needed for next level (exponential growth)
            user_xp.xp_to_next_level = int(100 * (1.2 ** user_xp.current_level))
        
        # Record XP transaction
        transaction = XPTransaction(
            user_id=user_id,
            amount=amount,
            source=source,
            source_id=source_id,
            description=description
        )
        db.session.add(transaction)
        
        return levels_gained
    
    def get_available_quests(self, user_id: int) -> List[Dict]:
        """Get quests available to a user"""
        # Get all active quests
        active_quests = Quest.query.filter_by(is_active=True).all()
        
        available_quests = []
        for quest in active_quests:
            # Check if user already has this quest
            user_quest = UserQuest.query.filter_by(
                user_id=user_id, 
                quest_id=quest.id
            ).first()
            
            # Skip if already completed and not repeatable
            if user_quest and user_quest.status == "completed" and not quest.is_repeatable:
                continue
            
            # Check prerequisites
            if quest.prerequisites and not self._check_prerequisites(user_id, quest.prerequisites):
                continue
            
            quest_data = {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "story_theme": quest.story_theme,
                "difficulty": quest.difficulty,
                "category": quest.category,
                "required_topics": quest.required_topics,
                "xp_reward": quest.xp_reward,
                "estimated_duration": quest.estimated_duration,
                "status": user_quest.status if user_quest else "available"
            }
            
            if quest.badge_reward_id:
                badge = Badge.query.get(quest.badge_reward_id)
                if badge:
                    quest_data["badge_reward"] = {
                        "name": badge.name,
                        "icon": badge.icon,
                        "rarity": badge.rarity
                    }
            
            available_quests.append(quest_data)
        
        return available_quests
    
    def get_user_quest_progress(self, user_id: int) -> List[Dict]:
        """Get user's quest progress"""
        user_quests = UserQuest.query.filter_by(user_id=user_id).all()
        
        progress_data = []
        for user_quest in user_quests:
            quest = Quest.query.get(user_quest.quest_id)
            if not quest:
                continue
            
            quest_data = {
                "id": quest.id,
                "title": quest.title,
                "description": quest.description,
                "story_theme": quest.story_theme,
                "difficulty": quest.difficulty,
                "status": user_quest.status,
                "progress_percentage": user_quest.progress_percentage,
                "completed_tasks": user_quest.completed_tasks or [],
                "current_task_index": user_quest.current_task_index,
                "started_at": user_quest.started_at.isoformat() if user_quest.started_at else None,
                "deadline": user_quest.deadline.isoformat() if user_quest.deadline else None,
                "completed_at": user_quest.completed_at.isoformat() if user_quest.completed_at else None,
                "xp_earned": user_quest.xp_earned,
                "required_tasks": quest.required_tasks
            }
            
            progress_data.append(quest_data)
        
        return progress_data
