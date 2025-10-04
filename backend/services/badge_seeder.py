from ..models import Badge, db


def seed_badges():
    """Seed initial badges into the database"""
    
    # Check if badges already exist
    existing_badges = Badge.query.count()
    if existing_badges > 0:
        print(f"Badges already exist ({existing_badges} badges). Skipping seed.")
        return
    
    badges = [
        # Achievement Badges
        {
            "name": "First Steps",
            "description": "Complete your first quiz",
            "icon": "🎯",
            "category": "achievement",
            "rarity": "common",
            "xp_reward": 50,
            "requirements": {"min_attempts": 1}
        },
        {
            "name": "Quiz Master",
            "description": "Complete 10 quizzes",
            "icon": "🧠",
            "category": "achievement",
            "rarity": "common",
            "xp_reward": 100,
            "requirements": {"min_attempts": 10}
        },
        {
            "name": "Perfect Score",
            "description": "Get a perfect score on any quiz",
            "icon": "💯",
            "category": "achievement",
            "rarity": "rare",
            "xp_reward": 150,
            "requirements": {"min_accuracy": 1.0, "min_attempts": 1}
        },
        {
            "name": "Consistent Performer",
            "description": "Maintain 80% accuracy over 20 quizzes",
            "icon": "📈",
            "category": "achievement",
            "rarity": "rare",
            "xp_reward": 200,
            "requirements": {"min_accuracy": 0.8, "min_attempts": 20}
        },
        
        # Streak Badges
        {
            "name": "Daily Learner",
            "description": "Maintain a 7-day learning streak",
            "icon": "🔥",
            "category": "streak",
            "rarity": "common",
            "xp_reward": 100,
            "requirements": {"streak_requirements": {"daily_login": 7}}
        },
        {
            "name": "Streak Master",
            "description": "Maintain a 30-day learning streak",
            "icon": "⚡",
            "category": "streak",
            "rarity": "epic",
            "xp_reward": 500,
            "requirements": {"streak_requirements": {"daily_login": 30}}
        },
        {
            "name": "Quiz Streak",
            "description": "Complete quizzes for 5 consecutive days",
            "icon": "🎯",
            "category": "streak",
            "rarity": "rare",
            "xp_reward": 200,
            "requirements": {"streak_requirements": {"daily_lesson": 5}}
        },
        
        # Mastery Badges
        {
            "name": "Topic Master",
            "description": "Achieve 90% mastery in any topic",
            "icon": "🏆",
            "category": "mastery",
            "rarity": "rare",
            "xp_reward": 300,
            "requirements": {"mastery_requirements": {"any_topic": 90}}
        },
        {
            "name": "Expert Scholar",
            "description": "Achieve 95% mastery in 3 different topics",
            "icon": "🎓",
            "category": "mastery",
            "rarity": "epic",
            "xp_reward": 500,
            "requirements": {"mastery_requirements": {"multiple_topics": 95}}
        },
        {
            "name": "Learning Legend",
            "description": "Achieve 100% mastery in any topic",
            "icon": "👑",
            "category": "mastery",
            "rarity": "legendary",
            "xp_reward": 1000,
            "requirements": {"mastery_requirements": {"perfect_mastery": 100}}
        },
        
        # Level Badges
        {
            "name": "Rising Star",
            "description": "Reach level 5",
            "icon": "⭐",
            "category": "level",
            "rarity": "common",
            "xp_reward": 100,
            "requirements": {"min_level": 5}
        },
        {
            "name": "Advanced Learner",
            "description": "Reach level 10",
            "icon": "🌟",
            "category": "level",
            "rarity": "rare",
            "xp_reward": 300,
            "requirements": {"min_level": 10}
        },
        {
            "name": "Learning Champion",
            "description": "Reach level 20",
            "icon": "💎",
            "category": "level",
            "rarity": "epic",
            "xp_reward": 750,
            "requirements": {"min_level": 20}
        },
        {
            "name": "Learning Legend",
            "description": "Reach level 50",
            "icon": "👑",
            "category": "level",
            "rarity": "legendary",
            "xp_reward": 2000,
            "requirements": {"min_level": 50}
        },
        
        # Emotion Badges
        {
            "name": "Happy Learner",
            "description": "Detect happy emotion during 10 learning sessions",
            "icon": "😊",
            "category": "emotion",
            "rarity": "common",
            "xp_reward": 100,
            "requirements": {"emotion_count": {"happy": 10}}
        },
        {
            "name": "Confident Coder",
            "description": "Show confidence during 20 learning sessions",
            "icon": "💪",
            "category": "emotion",
            "rarity": "rare",
            "xp_reward": 200,
            "requirements": {"emotion_count": {"confident": 20}}
        },
        {
            "name": "Persistent Problem Solver",
            "description": "Continue learning despite frustration",
            "icon": "🛡️",
            "category": "emotion",
            "rarity": "rare",
            "xp_reward": 250,
            "requirements": {"emotion_count": {"frustrated": 5}}
        },
        
        # Quest Badges
        {
            "name": "Quest Starter",
            "description": "Complete your first quest",
            "icon": "🗡️",
            "category": "quest",
            "rarity": "common",
            "xp_reward": 150,
            "requirements": {"quests_completed": 1}
        },
        {
            "name": "Adventure Seeker",
            "description": "Complete 5 quests",
            "icon": "🗺️",
            "category": "quest",
            "rarity": "rare",
            "xp_reward": 400,
            "requirements": {"quests_completed": 5}
        },
        {
            "name": "Quest Master",
            "description": "Complete 10 quests",
            "icon": "🏰",
            "category": "quest",
            "rarity": "epic",
            "xp_reward": 750,
            "requirements": {"quests_completed": 10}
        },
        {
            "name": "Legendary Hero",
            "description": "Complete 25 quests",
            "icon": "⚔️",
            "category": "quest",
            "rarity": "legendary",
            "xp_reward": 1500,
            "requirements": {"quests_completed": 25}
        },
        
        # Special Badges
        {
            "name": "Early Bird",
            "description": "Complete learning activities before 8 AM",
            "icon": "🌅",
            "category": "special",
            "rarity": "rare",
            "xp_reward": 200,
            "requirements": {"early_bird": True}
        },
        {
            "name": "Night Owl",
            "description": "Complete learning activities after 10 PM",
            "icon": "🦉",
            "category": "special",
            "rarity": "rare",
            "xp_reward": 200,
            "requirements": {"night_owl": True}
        },
        {
            "name": "Weekend Warrior",
            "description": "Complete learning activities on weekends",
            "icon": "⚔️",
            "category": "special",
            "rarity": "common",
            "xp_reward": 150,
            "requirements": {"weekend_learner": True}
        },
        {
            "name": "Speed Demon",
            "description": "Complete a quiz in under 30 seconds",
            "icon": "⚡",
            "category": "special",
            "rarity": "rare",
            "xp_reward": 300,
            "requirements": {"speed_completion": True}
        },
        {
            "name": "Perfectionist",
            "description": "Get 10 perfect scores in a row",
            "icon": "💎",
            "category": "special",
            "rarity": "legendary",
            "xp_reward": 1000,
            "requirements": {"perfect_streak": 10}
        }
    ]
    
    # Create badge objects
    badges_created = 0
    for badge_data in badges:
        # Check if badge already exists
        existing_badge = Badge.query.filter_by(name=badge_data['name']).first()
        if not existing_badge:
            badge = Badge(**badge_data)
            db.session.add(badge)
            badges_created += 1
    
    db.session.commit()
    print(f"Seeded {badges_created} new badges successfully!")
