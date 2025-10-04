from datetime import datetime, timedelta
from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(120), nullable=True)
    role = db.Column(db.String(20), default="learner")
    emotion_opt_in = db.Column(db.Boolean, default=False)
    learning_style_opt_in = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    emotion_logs = db.relationship("EmotionLog", backref="user", lazy=True)
    performance_logs = db.relationship("PerformanceLog", backref="user", lazy=True)
    user_progress = db.relationship("UserProgress", backref="user", lazy=True)
    feedback_logs = db.relationship("FeedbackLog", backref="user", lazy=True)


class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(120), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Float, default=0.5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_progress = db.relationship("UserProgress", backref="content", lazy=True)


class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("content.id"), nullable=False)
    last_reviewed = db.Column(db.DateTime, default=datetime.utcnow)
    next_review = db.Column(db.DateTime, default=datetime.utcnow)
    ease_factor = db.Column(db.Float, default=2.5)
    interval_days = db.Column(db.Integer, default=1)
    repetitions = db.Column(db.Integer, default=0)
    performance_score = db.Column(db.Float, default=0.0)
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content'),)


class EmotionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    emotion = db.Column(db.String(32), nullable=False)
    confidence = db.Column(db.Float, nullable=False)


class PerformanceLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    module = db.Column(db.String(120), nullable=False)
    question_id = db.Column(db.Integer, nullable=True)
    correct = db.Column(db.Boolean, nullable=False)
    score = db.Column(db.Float, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class FeedbackLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lesson_id = db.Column(db.String(120), nullable=True)  # Can be module, content_id, or session_id
    feedback_text = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(50), default="lesson")  # lesson, quiz, milestone, etc.
    performance_data = db.Column(db.JSON, nullable=True)  # Store performance metrics as JSON
    emotion_context = db.Column(db.JSON, nullable=True)  # Store emotion data as JSON
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class LearningProgress(db.Model):
    """Track individual quiz/lesson progress for Learning DNA analysis"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.String(120), nullable=True)  # Can be content_id, lesson_id, etc.
    topic = db.Column(db.String(120), nullable=False)
    score = db.Column(db.Float, nullable=False)  # 0.0 to 1.0
    attempts = db.Column(db.Integer, default=1)
    time_spent = db.Column(db.Integer, nullable=True)  # seconds
    correct_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=1)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship("User", backref=db.backref("learning_progress_logs", lazy=True))


class TopicMastery(db.Model):
    """Track mastery level for each topic per user"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    topic = db.Column(db.String(120), nullable=False)
    mastery_score = db.Column(db.Float, default=0.0)  # 0-100
    total_attempts = db.Column(db.Integer, default=0)
    correct_attempts = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    streak_count = db.Column(db.Integer, default=0)  # consecutive improvements
    mastery_level = db.Column(db.String(20), default="beginner")  # beginner, intermediate, advanced, expert
    
    # Ensure unique user-topic pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'topic', name='unique_user_topic'),)
    
    user = db.relationship("User", backref=db.backref("topic_mastery", lazy=True))


class LearningBadge(db.Model):
    """Track badges earned by users"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    badge_type = db.Column(db.String(50), nullable=False)  # mastery_100, streak_5, etc.
    badge_name = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(120), nullable=True)  # topic-specific badges
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    badge_data = db.Column(db.JSON, nullable=True)  # Additional badge data
    
    user = db.relationship("User", backref=db.backref("learning_badges", lazy=True))


class LearningStyle(db.Model):
    """Track user's learning style preferences"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    visual_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    auditory_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    example_score = db.Column(db.Float, default=0.0)  # 0.0 to 1.0
    dominant_style = db.Column(db.String(20))  # "visual", "auditory", "example"
    total_attempts = db.Column(db.Integer, default=0)
    visual_attempts = db.Column(db.Integer, default=0)
    auditory_attempts = db.Column(db.Integer, default=0)
    example_attempts = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique user record
    __table_args__ = (db.UniqueConstraint('user_id', name='unique_user_learning_style'),)
    
    user = db.relationship("User", backref=db.backref("learning_style", lazy=True))


class RevisionSchedule(db.Model):
    """Auto-generated revision schedules using SM-2 algorithm"""
    __tablename__ = "revision_schedules"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    content_id = db.Column(db.Integer, nullable=False)  # links to Content or Question id
    topic = db.Column(db.String(150), nullable=False)
    next_review = db.Column(db.DateTime, nullable=False)
    interval_days = db.Column(db.Integer, default=1)
    easiness_factor = db.Column(db.Float, default=2.5)  # for SM-2 style updates
    repetitions = db.Column(db.Integer, default=0)
    quality_scores = db.Column(db.JSON, nullable=True)  # Store recent quality scores
    emotion_hints = db.Column(db.JSON, nullable=True)  # Store recent emotion data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique user-content pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'content_id', name='unique_user_content_revision'),)
    
    user = db.relationship("User", backref=db.backref("revision_schedules", lazy=True))


# ===== GAMIFICATION MODELS =====

class UserXP(db.Model):
    """Track user experience points and level progression"""
    __tablename__ = "user_xp"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total_xp = db.Column(db.Integer, default=0)
    current_level = db.Column(db.Integer, default=1)
    xp_to_next_level = db.Column(db.Integer, default=100)
    xp_in_current_level = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique user record
    __table_args__ = (db.UniqueConstraint('user_id', name='unique_user_xp'),)
    
    user = db.relationship("User", backref=db.backref("xp_profile", lazy=True))


class UserStreak(db.Model):
    """Track user learning streaks"""
    __tablename__ = "user_streak"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    streak_type = db.Column(db.String(50), nullable=False)  # "daily_login", "daily_lesson", "quiz_streak"
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    streak_frozen = db.Column(db.Boolean, default=False)  # For streak freeze items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Ensure unique user-streak type pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'streak_type', name='unique_user_streak_type'),)
    
    user = db.relationship("User", backref=db.backref("streaks", lazy=True))


class Badge(db.Model):
    """Badge definitions and user badge achievements"""
    __tablename__ = "badge"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100), nullable=True)  # Icon name or URL
    category = db.Column(db.String(50), nullable=False)  # "achievement", "streak", "quest", "emotion"
    rarity = db.Column(db.String(20), default="common")  # "common", "rare", "epic", "legendary"
    xp_reward = db.Column(db.Integer, default=0)
    requirements = db.Column(db.JSON, nullable=True)  # Badge unlock conditions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserBadge(db.Model):
    """User badge achievements"""
    __tablename__ = "user_badge"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badge.id"), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress_data = db.Column(db.JSON, nullable=True)  # Additional progress info
    
    # Ensure unique user-badge pairs
    __table_args__ = (db.UniqueConstraint('user_id', 'badge_id', name='unique_user_badge'),)
    
    user = db.relationship("User", backref=db.backref("earned_badges", lazy=True))
    badge = db.relationship("Badge", backref=db.backref("user_achievements", lazy=True))


class Quest(db.Model):
    """Story-driven quest definitions"""
    __tablename__ = "quest"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    story_theme = db.Column(db.String(100), nullable=False)  # "adventure", "mystery", "heroic", "scientific"
    difficulty = db.Column(db.String(20), default="medium")  # "easy", "medium", "hard", "expert"
    category = db.Column(db.String(50), nullable=False)  # "learning", "mastery", "exploration", "challenge"
    
    # Quest requirements
    required_topics = db.Column(db.JSON, nullable=True)  # List of topics to master
    required_tasks = db.Column(db.JSON, nullable=False)  # List of tasks with descriptions
    prerequisites = db.Column(db.JSON, nullable=True)  # Required badges or quests
    
    # Rewards
    xp_reward = db.Column(db.Integer, default=0)
    badge_reward_id = db.Column(db.Integer, db.ForeignKey("badge.id"), nullable=True)
    unlock_content = db.Column(db.JSON, nullable=True)  # Content to unlock
    
    # Quest metadata
    estimated_duration = db.Column(db.Integer, default=7)  # Days
    is_active = db.Column(db.Boolean, default=True)
    is_repeatable = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    badge_reward = db.relationship("Badge", backref=db.backref("quest_rewards", lazy=True))


class UserQuest(db.Model):
    """User quest progress and completion"""
    __tablename__ = "user_quest"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quest_id = db.Column(db.Integer, db.ForeignKey("quest.id"), nullable=False)
    
    # Progress tracking
    status = db.Column(db.String(20), default="available")  # "available", "active", "completed", "failed"
    progress_percentage = db.Column(db.Float, default=0.0)
    completed_tasks = db.Column(db.JSON, nullable=True)  # List of completed task IDs
    current_task_index = db.Column(db.Integer, default=0)
    
    # Timing
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    deadline = db.Column(db.DateTime, nullable=True)
    
    # Rewards
    xp_earned = db.Column(db.Integer, default=0)
    badge_earned_id = db.Column(db.Integer, db.ForeignKey("badge.id"), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("quest_progress", lazy=True))
    quest = db.relationship("Quest", backref=db.backref("user_progress", lazy=True))
    badge_earned = db.relationship("Badge", backref=db.backref("quest_earnings", lazy=True))


class XPTransaction(db.Model):
    """Track XP transactions for transparency"""
    __tablename__ = "xp_transaction"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    amount = db.Column(db.Integer, nullable=False)  # Can be negative
    source = db.Column(db.String(100), nullable=False)  # "quiz_complete", "quest_reward", "badge_earned", etc.
    source_id = db.Column(db.Integer, nullable=True)  # ID of the source (quest_id, badge_id, etc.)
    description = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("xp_transactions", lazy=True))


# Story-Driven Quest System Models
class Story(db.Model):
    """Main story narratives"""
    __tablename__ = "story"
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    theme = db.Column(db.String(100), nullable=False)  # "Math Adventure", "Science Galaxy", etc.
    cover_image = db.Column(db.String(500))  # URL to cover image
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    chapters = db.relationship("Chapter", backref="story", lazy=True, cascade="all, delete-orphan")


class Chapter(db.Model):
    """Story chapters with narrative progression"""
    __tablename__ = "chapter"
    
    id = db.Column(db.Integer, primary_key=True)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)  # Chapter sequence
    storyline_text = db.Column(db.Text)  # Main story narrative
    visual_assets = db.Column(db.JSON)  # {"background": "url", "characters": ["url1", "url2"]}
    unlock_requirements = db.Column(db.JSON)  # {"xp_required": 100, "topics_mastered": ["fractions"]}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    quests = db.relationship("StoryQuest", backref="chapter", lazy=True, cascade="all, delete-orphan")


class StoryQuest(db.Model):
    """Learning quests within story chapters"""
    __tablename__ = "story_quest"
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    quest_type = db.Column(db.String(50), default="learning")  # "learning", "practice", "challenge"
    difficulty_level = db.Column(db.String(20), default="medium")  # "easy", "medium", "hard"
    topics = db.Column(db.JSON)  # ["fractions", "algebra", "geometry"]
    required_xp = db.Column(db.Integer, default=0)
    completion_criteria = db.Column(db.JSON)  # {"min_score": 80, "attempts_allowed": 3}
    reward_xp = db.Column(db.Integer, default=50)
    reward_badge = db.Column(db.String(100))  # Badge name to award
    story_context = db.Column(db.Text)  # How this quest fits into the story
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to existing UserQuest model (if needed)
    # user_quests = db.relationship("UserQuest", backref="story_quest_details", lazy=True)


class StoryProgress(db.Model):
    """Track user progress through stories"""
    __tablename__ = "story_progress"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id"), nullable=False)
    current_chapter_id = db.Column(db.Integer, db.ForeignKey("chapter.id"))
    completed_chapters = db.Column(db.JSON, default=list)  # List of completed chapter IDs
    completed_quests = db.Column(db.JSON, default=list)  # List of completed quest IDs
    total_story_xp = db.Column(db.Integer, default=0)
    story_started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("story_progress", lazy=True))
    story = db.relationship("Story", backref=db.backref("user_progress", lazy=True))
    current_chapter = db.relationship("Chapter", backref=db.backref("current_users", lazy=True))


class StoryReward(db.Model):
    """Track story rewards and unlocks"""
    __tablename__ = "story_reward"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    story_id = db.Column(db.Integer, db.ForeignKey("story.id"), nullable=False)
    reward_type = db.Column(db.String(50), nullable=False)  # "chapter_unlock", "quest_complete", "story_milestone"
    reward_data = db.Column(db.JSON)  # {"chapter_id": 2, "xp_gained": 100, "badge": "Bridge Builder"}
    is_viewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship("User", backref=db.backref("story_rewards", lazy=True))
    story = db.relationship("Story", backref=db.backref("rewards_given", lazy=True))


# ===== CODING SANDBOX =====
class CodingAttempt(db.Model):
    __tablename__ = "coding_attempt"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    language = db.Column(db.String(20), nullable=False)  # "python" | "javascript"
    code = db.Column(db.Text, nullable=False)
    output = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False)  # "success" | "error" | "timeout"
    exec_ms = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    user = db.relationship("User", backref=db.backref("coding_attempts", lazy=True))

# ===== LEARNER KNOWLEDGE GRAPH =====
class Concept(db.Model):
    __tablename__ = "concept"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    subject = db.Column(db.String(100), nullable=False)
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # prerequisites via association table
    prerequisites = db.relationship(
        "Concept",
        secondary="concept_prerequisite",
        primaryjoin="Concept.id==ConceptPrerequisite.concept_id",
        secondaryjoin="Concept.id==ConceptPrerequisite.prerequisite_id",
        backref=db.backref("unlocks", lazy=True),
        lazy=True,
    )


class ConceptPrerequisite(db.Model):
    __tablename__ = "concept_prerequisite"

    id = db.Column(db.Integer, primary_key=True)
    concept_id = db.Column(db.Integer, db.ForeignKey("concept.id"), nullable=False)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey("concept.id"), nullable=False)
    __table_args__ = (db.UniqueConstraint('concept_id', 'prerequisite_id', name='unique_concept_prereq'),)


class LearnerConceptMastery(db.Model):
    __tablename__ = "learner_concept_mastery"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    concept_id = db.Column(db.Integer, db.ForeignKey("concept.id"), nullable=False)
    mastery_score = db.Column(db.Float, default=0.0)  # 0..1
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    emotion_snapshot = db.Column(db.JSON, nullable=True)

    __table_args__ = (db.UniqueConstraint('user_id', 'concept_id', name='unique_user_concept_mastery'),)

    user = db.relationship("User", backref=db.backref("concept_mastery", lazy=True))
    concept = db.relationship("Concept", backref=db.backref("learner_mastery", lazy=True))

# ===== CO-LEARNER =====
class CoLearnerProfile(db.Model):
    __tablename__ = "colearner_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    persona_config = db.Column(db.JSON, nullable=False, default=dict)
    experience = db.Column(db.Integer, default=0)
    xp = db.Column(db.Integer, default=0)  # Experience points for growth
    level = db.Column(db.Integer, default=1)  # Auto-calculated level
    traits = db.Column(db.JSON, default=lambda: [])  # Unlocked personality traits
    humor_level = db.Column(db.Integer, default=3)  # 0-10 scale
    knowledge_state = db.Column(db.JSON, default=dict)
    settings = db.Column(db.JSON, default=lambda: {"enabled": False, "save_dialogs": False})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("colearner_profile", uselist=False))


class CoLearnerDialogLog(db.Model):
    __tablename__ = "colearner_dialogs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    direction = db.Column(db.String(10))  # user | colearner
    text = db.Column(db.Text)
    dialog_metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("colearner_dialogs", lazy=True))


class CoLearnerActivity(db.Model):
    __tablename__ = "colearner_activities"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_type = db.Column(db.String(64))
    payload = db.Column(db.JSON, default=dict)
    result = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", backref=db.backref("colearner_activities", lazy=True))

# ===== CURRICULUM AUTO-EVOLUTION =====
class Resource(db.Model):
    __tablename__ = "resources"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.String(20), default="intermediate")  # beginner, intermediate, advanced
    type = db.Column(db.String(50), nullable=False)  # video, article, tutorial, exercise
    url = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100), nullable=False)  # khan_academy, youtube_edu, arxiv, etc.
    content = db.Column(db.Text)  # Raw content for processing
    resource_metadata = db.Column(db.JSON, default=dict)  # Additional metadata
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    lesson_cards = db.relationship("LessonCard", backref="resource", lazy=True)


class LessonCard(db.Model):
    __tablename__ = "lesson_cards"

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resources.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    quiz_questions = db.Column(db.JSON, default=list)  # List of quiz questions
    exercises = db.Column(db.JSON, default=list)  # List of exercises
    tags = db.Column(db.JSON, default=list)  # Learning tags
    difficulty_score = db.Column(db.Float, default=0.5)  # 0-1 difficulty
    estimated_time = db.Column(db.Integer, default=30)  # Minutes
    learning_objectives = db.Column(db.JSON, default=list)
    prerequisites = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    learning_paths = db.relationship("LearningPath", foreign_keys="LearningPath.lesson_card_id", backref="lesson_card", lazy=True)


class LearningPath(db.Model):
    __tablename__ = "learning_paths"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lesson_card_id = db.Column(db.Integer, db.ForeignKey("lesson_cards.id"), nullable=False)
    status = db.Column(db.String(20), default="upcoming")  # upcoming, in-progress, completed, skipped
    priority = db.Column(db.Integer, default=0)  # Higher number = higher priority
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    progress = db.Column(db.Float, default=0.0)  # 0-1 progress
    replaced_from = db.Column(db.Integer, db.ForeignKey("lesson_cards.id"))  # If this replaced another lesson
    replacement_reason = db.Column(db.String(255))  # Why it was replaced

    user = db.relationship("User", backref=db.backref("learning_paths", lazy=True))
    replaced_lesson = db.relationship("LessonCard", foreign_keys=[replaced_from], backref="replacements")


class CurriculumUpdate(db.Model):
    __tablename__ = "curriculum_updates"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    update_type = db.Column(db.String(50), nullable=False)  # new_lesson, replaced_lesson, updated_path
    lesson_card_id = db.Column(db.Integer, db.ForeignKey("lesson_cards.id"))
    old_lesson_id = db.Column(db.Integer, db.ForeignKey("lesson_cards.id"))  # If replacing
    message = db.Column(db.String(500))
    update_metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref=db.backref("curriculum_updates", lazy=True))
    lesson_card = db.relationship("LessonCard", foreign_keys=[lesson_card_id], backref="updates")
    old_lesson = db.relationship("LessonCard", foreign_keys=[old_lesson_id])

# ===== AI SOCRATIC DEBATE =====
class DebateSession(db.Model):
    __tablename__ = "debate_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    topic = db.Column(db.String(500), nullable=False)
    learner_stance = db.Column(db.String(100), nullable=False)  # pro, con, neutral
    ai_stance = db.Column(db.String(100), nullable=False)  # pro, con
    status = db.Column(db.String(20), default="active")  # active, ended, paused
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    total_turns = db.Column(db.Integer, default=0)
    stance_switches = db.Column(db.Integer, default=0)
    
    # Performance metrics
    learner_score = db.Column(db.Float, default=0.0)  # Overall debate performance
    ai_score = db.Column(db.Float, default=0.0)
    debate_quality = db.Column(db.Float, default=0.0)  # Overall debate quality
    
    # Metadata
    difficulty_level = db.Column(db.String(20), default="intermediate")  # beginner, intermediate, advanced
    llm_model = db.Column(db.String(100))  # Model used for AI responses
    settings = db.Column(db.JSON, default=dict)  # Debate settings and preferences
    
    user = db.relationship("User", backref=db.backref("debate_sessions", lazy=True))
    turns = db.relationship("DebateTurn", backref="session", lazy=True, cascade="all, delete-orphan")
    scores = db.relationship("DebateScore", backref="session", lazy=True, cascade="all, delete-orphan")


class DebateTurn(db.Model):
    __tablename__ = "debate_turns"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("debate_sessions.id"), nullable=False)
    turn_number = db.Column(db.Integer, nullable=False)
    speaker = db.Column(db.String(20), nullable=False)  # learner, ai
    message = db.Column(db.Text, nullable=False)
    stance = db.Column(db.String(100))  # Current stance when this turn was made
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Turn-specific metrics
    word_count = db.Column(db.Integer, default=0)
    sentiment_score = db.Column(db.Float)  # -1 to 1
    complexity_score = db.Column(db.Float)  # 0 to 1
    response_time = db.Column(db.Float)  # Seconds to respond
    
    # Metadata
    llm_metadata = db.Column(db.JSON, default=dict)  # LLM response metadata
    turn_type = db.Column(db.String(50), default="argument")  # argument, question, rebuttal, etc.


class DebateScore(db.Model):
    __tablename__ = "debate_scores"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("debate_sessions.id"), nullable=False)
    turn_id = db.Column(db.Integer, db.ForeignKey("debate_turns.id"), nullable=False)
    scorer_type = db.Column(db.String(20), nullable=False)  # learner, ai, system
    
    # Scoring dimensions (0-10 scale)
    logic_score = db.Column(db.Float, nullable=False)
    clarity_score = db.Column(db.Float, nullable=False)
    persuasiveness_score = db.Column(db.Float, nullable=False)
    evidence_quality = db.Column(db.Float, default=0.0)
    critical_thinking = db.Column(db.Float, default=0.0)
    respectfulness = db.Column(db.Float, default=0.0)
    
    # Overall scores
    overall_score = db.Column(db.Float, nullable=False)
    improvement_areas = db.Column(db.JSON, default=list)  # Areas for improvement
    strengths = db.Column(db.JSON, default=list)  # Identified strengths
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    turn = db.relationship("DebateTurn", backref="scores")

