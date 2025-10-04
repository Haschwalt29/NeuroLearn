from datetime import datetime
from .. import db
from ..models import Story, Chapter, StoryQuest


def seed_sample_story():
    """Seed the database with a sample story: Math Adventure"""
    
    # Check if story already exists
    existing_story = Story.query.filter_by(title="Math Adventure: The Quest of Fractions & Algebra").first()
    if existing_story:
        print("Math Adventure story already exists. Skipping seed.")
        return
    
    # Create the main story
    story = Story(
        title="Math Adventure: The Quest of Fractions & Algebra",
        description="Join Alex the Adventurer on an epic journey through the mystical lands of mathematics, where fractions and algebra hold the key to ancient treasures!",
        theme="Math Adventure",
        cover_image="https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400",
        is_active=True
    )
    db.session.add(story)
    db.session.flush()  # Get the story ID
    
    # Chapter 1: The Broken Bridge
    chapter1 = Chapter(
        story_id=story.id,
        title="The Broken Bridge",
        description="Alex discovers a broken bridge that can only be repaired by mastering fractions!",
        order=1,
        storyline_text="""
        🌉 *The Broken Bridge*

        Alex the Adventurer stood before the ancient stone bridge, its once-mighty arches now crumbled and broken. 
        The river below rushed with crystal-clear water, but crossing seemed impossible.

        "Only those who understand the ancient art of fractions can repair this bridge," whispered the wind through the trees.

        A mysterious figure appeared - the Bridge Keeper, an old wizard with twinkling eyes.

        "Young adventurer," he said, "to cross this river, you must prove your mastery of fractions. 
        Each stone you place correctly will strengthen the bridge. Each mistake will weaken it further."

        Alex nodded determinedly. "I'm ready to learn!"

        The Bridge Keeper smiled. "Then let us begin your journey into the world of fractions..."
        """,
        visual_assets={
            "background": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
            "characters": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
                "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200"
            ]
        },
        unlock_requirements={
            "xp_required": 0,
            "topics_mastered": []
        }
    )
    db.session.add(chapter1)
    db.session.flush()
    
    # Chapter 1 Quests
    quest1_1 = StoryQuest(
        chapter_id=chapter1.id,
        title="Understanding Fractions",
        description="Learn the basics of fractions - what they represent and how to read them",
        quest_type="learning",
        difficulty_level="easy",
        topics=["fractions", "basic_math"],
        required_xp=0,
        completion_criteria={"min_score": 70, "attempts_allowed": 3},
        reward_xp=50,
        reward_badge="Fraction Novice",
        story_context="Alex learns that fractions represent parts of a whole, just like pieces of the broken bridge."
    )
    
    quest1_2 = StoryQuest(
        chapter_id=chapter1.id,
        title="Adding Fractions",
        description="Master adding fractions with the same denominator",
        quest_type="practice",
        difficulty_level="medium",
        topics=["fractions", "addition"],
        required_xp=50,
        completion_criteria={"min_score": 80, "attempts_allowed": 3},
        reward_xp=75,
        reward_badge="Bridge Builder",
        story_context="Alex combines stone pieces (fractions) to repair the first section of the bridge."
    )
    
    quest1_3 = StoryQuest(
        chapter_id=chapter1.id,
        title="Subtracting Fractions",
        description="Learn to subtract fractions and find the missing pieces",
        quest_type="challenge",
        difficulty_level="medium",
        topics=["fractions", "subtraction"],
        required_xp=125,
        completion_criteria={"min_score": 85, "attempts_allowed": 2},
        reward_xp=100,
        reward_badge="Stone Master",
        story_context="Alex removes damaged stones (subtracts fractions) to make room for new ones."
    )
    
    db.session.add_all([quest1_1, quest1_2, quest1_3])
    
    # Chapter 2: The Enchanted Forest of Algebra
    chapter2 = Chapter(
        story_id=story.id,
        title="The Enchanted Forest of Algebra",
        description="Deep in the forest, Alex discovers that algebra is the key to unlocking ancient secrets!",
        order=2,
        storyline_text="""
        🌲 *The Enchanted Forest of Algebra*

        With the bridge repaired, Alex ventured into the mysterious Enchanted Forest. 
        Ancient trees whispered secrets, and glowing symbols floated in the air.

        "Welcome, brave one," said the Forest Guardian, a majestic owl perched on a branch. 
        "You have proven yourself with fractions. Now you must master the ancient language of algebra."

        The owl's eyes gleamed with wisdom. "In this forest, letters and numbers dance together. 
        'X' is not just a letter - it's a mystery waiting to be solved!"

        Alex looked around in wonder. "How do I learn this ancient art?"

        "By solving the riddles of the forest," the owl replied. 
        "Each equation you solve will reveal a path deeper into the woods. 
        Each variable you find will unlock new treasures!"

        The adventure continued...
        """,
        visual_assets={
            "background": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=800",
            "characters": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=200"
            ]
        },
        unlock_requirements={
            "xp_required": 225,  # Total XP from Chapter 1
            "topics_mastered": ["fractions"]
        }
    )
    db.session.add(chapter2)
    db.session.flush()
    
    # Chapter 2 Quests
    quest2_1 = StoryQuest(
        chapter_id=chapter2.id,
        title="Introduction to Variables",
        description="Learn what variables are and how to use them in equations",
        quest_type="learning",
        difficulty_level="easy",
        topics=["algebra", "variables"],
        required_xp=225,
        completion_criteria={"min_score": 70, "attempts_allowed": 3},
        reward_xp=60,
        reward_badge="Variable Explorer",
        story_context="Alex discovers that 'X' represents unknown treasures hidden in the forest."
    )
    
    quest2_2 = StoryQuest(
        chapter_id=chapter2.id,
        title="Solving Simple Equations",
        description="Master solving equations with one variable",
        quest_type="practice",
        difficulty_level="medium",
        topics=["algebra", "equations"],
        required_xp=285,
        completion_criteria={"min_score": 80, "attempts_allowed": 3},
        reward_xp=90,
        reward_badge="Equation Solver",
        story_context="Alex solves riddles to find hidden paths through the forest."
    )
    
    quest2_3 = StoryQuest(
        chapter_id=chapter2.id,
        title="Word Problems with Algebra",
        description="Apply algebra to solve real-world problems",
        quest_type="challenge",
        difficulty_level="hard",
        topics=["algebra", "word_problems"],
        required_xp=375,
        completion_criteria={"min_score": 85, "attempts_allowed": 2},
        reward_xp=120,
        reward_badge="Forest Sage",
        story_context="Alex uses algebra to help forest creatures solve their problems."
    )
    
    db.session.add_all([quest2_1, quest2_2, quest2_3])
    
    # Chapter 3: The Final Challenge
    chapter3 = Chapter(
        story_id=story.id,
        title="The Final Challenge",
        description="The ultimate test combining fractions and algebra to unlock the ancient treasure!",
        order=3,
        storyline_text="""
        🏰 *The Final Challenge*

        After mastering both fractions and algebra, Alex reached the ancient castle at the heart of the forest. 
        Before the massive doors stood the Guardian of Knowledge, a wise dragon with scales that shimmered like equations.

        "You have come far, young adventurer," the dragon rumbled. 
        "But to claim the ancient treasure, you must prove you can combine all your knowledge."

        The dragon's eyes sparkled with challenge. "Fractions and algebra together - 
        this is the ultimate test of mathematical mastery!"

        Alex took a deep breath. "I'm ready. Show me the final challenge."

        The dragon smiled. "Then let us begin the greatest mathematical adventure of all..."
        """,
        visual_assets={
            "background": "https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=800",
            "characters": [
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=200",
                "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=200"
            ]
        },
        unlock_requirements={
            "xp_required": 585,  # Total XP from Chapters 1 & 2
            "topics_mastered": ["fractions", "algebra"]
        }
    )
    db.session.add(chapter3)
    db.session.flush()
    
    # Chapter 3 Quests
    quest3_1 = StoryQuest(
        chapter_id=chapter3.id,
        title="Fractions in Algebraic Expressions",
        description="Combine fractions with algebraic expressions",
        quest_type="challenge",
        difficulty_level="hard",
        topics=["fractions", "algebra", "expressions"],
        required_xp=585,
        completion_criteria={"min_score": 85, "attempts_allowed": 2},
        reward_xp=150,
        reward_badge="Mathematical Master",
        story_context="Alex combines ancient fraction magic with algebraic wisdom."
    )
    
    quest3_2 = StoryQuest(
        chapter_id=chapter3.id,
        title="The Ultimate Equation",
        description="Solve complex equations involving fractions and variables",
        quest_type="challenge",
        difficulty_level="hard",
        topics=["fractions", "algebra", "complex_equations"],
        required_xp=735,
        completion_criteria={"min_score": 90, "attempts_allowed": 1},
        reward_xp=200,
        reward_badge="Treasure Guardian",
        story_context="Alex solves the dragon's ultimate riddle to unlock the ancient treasure!"
    )
    
    db.session.add_all([quest3_1, quest3_2])
    
    # Commit all changes
    db.session.commit()
    print("✅ Math Adventure story seeded successfully!")
    print(f"   - Story: {story.title}")
    print(f"   - Chapters: 3")
    print(f"   - Quests: 7")
    print(f"   - Total XP available: {50+75+100+60+90+120+150+200} XP")


def seed_additional_badges():
    """Seed additional badges for the story system"""
    from ..models import Badge
    
    story_badges = [
        {
            "name": "Fraction Novice",
            "description": "Completed your first fraction lesson",
            "category": "story",
            "rarity": "common",
            "icon": "🔢"
        },
        {
            "name": "Bridge Builder",
            "description": "Mastered adding fractions",
            "category": "story",
            "rarity": "common",
            "icon": "🌉"
        },
        {
            "name": "Stone Master",
            "description": "Conquered fraction subtraction",
            "category": "story",
            "rarity": "rare",
            "icon": "🪨"
        },
        {
            "name": "Variable Explorer",
            "description": "Discovered the world of algebra",
            "category": "story",
            "rarity": "common",
            "icon": "🔍"
        },
        {
            "name": "Equation Solver",
            "description": "Solved your first algebraic equations",
            "category": "story",
            "rarity": "rare",
            "icon": "⚖️"
        },
        {
            "name": "Forest Sage",
            "description": "Mastered algebra word problems",
            "category": "story",
            "rarity": "epic",
            "icon": "🦉"
        },
        {
            "name": "Mathematical Master",
            "description": "Combined fractions and algebra",
            "category": "story",
            "rarity": "epic",
            "icon": "🧮"
        },
        {
            "name": "Treasure Guardian",
            "description": "Completed the ultimate mathematical challenge",
            "category": "story",
            "rarity": "legendary",
            "icon": "🏆"
        }
    ]
    
    for badge_data in story_badges:
        existing_badge = Badge.query.filter_by(name=badge_data["name"]).first()
        if not existing_badge:
            badge = Badge(**badge_data)
            db.session.add(badge)
    
    db.session.commit()
    print("✅ Story badges seeded successfully!")
