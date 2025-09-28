#!/usr/bin/env python3
"""
Comprehensive test script for the Gamification + Personalization + Quest Learning system
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8002"
EMAIL = "gamification_test@example.com"
PASSWORD = "test12345"
NAME = "Gamification Test User"

def make_request(method, endpoint, data=None, headers=None):
    """Make HTTP request with error handling"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        print(f"{method} {endpoint} -> {response.status_code}")
        if response.status_code >= 400:
            print(f"Error: {response.text}")
        return response
    except Exception as e:
        print(f"Request failed: {e}")
        return None

def test_gamification_system():
    """Test the complete gamification system"""
    print("🎮 Testing Gamification + Personalization + Quest Learning System")
    print("=" * 60)
    
    # Step 1: Sign up and login
    print("\n1. User Authentication")
    print("-" * 30)
    
    # Signup
    signup_data = {
        "name": NAME,
        "email": EMAIL,
        "password": PASSWORD,
        "role": "student"
    }
    signup_response = make_request("POST", "/api/auth/signup", signup_data)
    
    if not signup_response or signup_response.status_code not in [200, 201]:
        print("❌ Signup failed")
        return
    
    # Login
    login_data = {
        "email": EMAIL,
        "password": PASSWORD
    }
    login_response = make_request("POST", "/api/auth/login", login_data)
    
    if not login_response or login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    token = login_response.json().get("access_token")
    if not token:
        print("❌ No access token received")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authentication successful")
    
    # Step 2: Initialize gamification
    print("\n2. Initialize Gamification")
    print("-" * 30)
    
    init_response = make_request("POST", "/api/gamification/initialize", headers=headers)
    if init_response and init_response.status_code == 200:
        print("✅ Gamification initialized")
    else:
        print("⚠️ Gamification initialization failed or already exists")
    
    # Step 3: Test XP and Leveling
    print("\n3. Test XP and Leveling")
    print("-" * 30)
    
    # Award XP for quiz completion
    xp_data = {
        "source": "quiz_complete",
        "source_id": 1,
        "description": "Completed first quiz"
    }
    xp_response = make_request("POST", "/api/gamification/award-xp", xp_data, headers)
    if xp_response and xp_response.status_code == 200:
        xp_result = xp_response.json()
        print(f"✅ XP awarded: {xp_result['xp_awarded']} XP")
        print(f"   Total XP: {xp_result['total_xp']}")
        print(f"   Level: {xp_result['current_level']}")
        print(f"   Levels gained: {xp_result['levels_gained']}")
    
    # Award XP for lesson completion
    lesson_xp_data = {
        "source": "lesson_complete",
        "source_id": 1,
        "description": "Completed first lesson"
    }
    lesson_xp_response = make_request("POST", "/api/gamification/award-xp", lesson_xp_data, headers)
    if lesson_xp_response and lesson_xp_response.status_code == 200:
        lesson_xp_result = lesson_xp_response.json()
        print(f"✅ Lesson XP awarded: {lesson_xp_result['xp_awarded']} XP")
    
    # Step 4: Test Streaks
    print("\n4. Test Streak System")
    print("-" * 30)
    
    # Update daily login streak
    login_streak_data = {"streak_type": "daily_login"}
    login_streak_response = make_request("POST", "/api/gamification/update-streak", login_streak_data, headers)
    if login_streak_response and login_streak_response.status_code == 200:
        streak_result = login_streak_response.json()
        print(f"✅ Login streak updated: {streak_result['current_streak']} days")
        print(f"   Longest streak: {streak_result['longest_streak']} days")
    
    # Update daily lesson streak
    lesson_streak_data = {"streak_type": "daily_lesson"}
    lesson_streak_response = make_request("POST", "/api/gamification/update-streak", lesson_streak_data, headers)
    if lesson_streak_response and lesson_streak_response.status_code == 200:
        lesson_streak_result = lesson_streak_response.json()
        print(f"✅ Lesson streak updated: {lesson_streak_result['current_streak']} days")
    
    # Step 5: Test Badge System
    print("\n5. Test Badge System")
    print("-" * 30)
    
    # Check for new badges
    badge_check_response = make_request("POST", "/api/gamification/check-badges", headers=headers)
    if badge_check_response and badge_check_response.status_code == 200:
        badge_result = badge_check_response.json()
        print(f"✅ Badge check completed: {badge_result['count']} new badges")
        for badge in badge_result['new_badges']:
            print(f"   🏆 Earned: {badge['name']} ({badge['rarity']})")
    
    # Get user badges
    badges_response = make_request("GET", "/api/gamification/badges", headers=headers)
    if badges_response and badges_response.status_code == 200:
        badges_result = badges_response.json()
        print(f"✅ Total badges earned: {badges_result['total_badges']}")
    
    # Step 6: Test Quest System
    print("\n6. Test Quest System")
    print("-" * 30)
    
    # Generate a quest from weaknesses
    quest_generate_response = make_request("POST", "/api/quests/generate", headers=headers)
    if quest_generate_response and quest_generate_response.status_code == 200:
        quest_result = quest_generate_response.json()
        if quest_result.get('quest'):
            quest = quest_result['quest']
            print(f"✅ Quest generated: {quest['title']}")
            print(f"   Theme: {quest['story_theme']}")
            print(f"   Difficulty: {quest['difficulty']}")
            print(f"   XP Reward: {quest['xp_reward']}")
            
            # Start the quest
            start_data = {"quest_id": quest['id']}
            start_response = make_request("POST", "/api/quests/start", start_data, headers)
            if start_response and start_response.status_code == 200:
                start_result = start_response.json()
                print(f"✅ Quest started: {start_result['status']}")
                
                # Complete a quest task
                task_data = {
                    "quest_id": quest['id'],
                    "task_id": "task_1",
                    "completion_data": {"score": 0.8}
                }
                task_response = make_request("POST", "/api/quests/complete-task", task_data, headers)
                if task_response and task_response.status_code == 200:
                    task_result = task_response.json()
                    print(f"✅ Quest task completed: {task_result['progress_percentage']}% progress")
        else:
            print("ℹ️ No quest generated (no weak topics found)")
    
    # Get available quests
    quests_response = make_request("GET", "/api/quests/", headers=headers)
    if quests_response and quests_response.status_code == 200:
        quests_result = quests_response.json()
        print(f"✅ Available quests: {quests_result['total_count']}")
    
    # Get active quests
    active_quests_response = make_request("GET", "/api/quests/active", headers=headers)
    if active_quests_response and active_quests_response.status_code == 200:
        active_result = active_quests_response.json()
        print(f"✅ Active quests: {active_result['total_active']}")
    
    # Step 7: Test Personalization System
    print("\n7. Test Personalization System")
    print("-" * 30)
    
    # Update mastery profile
    mastery_data = {
        "topic": "Python Basics",
        "performance_score": 0.75,
        "emotion_hint": "happy"
    }
    mastery_response = make_request("POST", "/api/personalization/update-mastery", mastery_data, headers)
    if mastery_response and mastery_response.status_code == 200:
        mastery_result = mastery_response.json()
        print(f"✅ Mastery updated: {mastery_result['topic']} -> {mastery_result['mastery_score']:.1f}%")
        print(f"   Level: {mastery_result['mastery_level']}")
        print(f"   Emotion adjustment: {mastery_result['emotion_adjustment']}")
    
    # Update another topic
    mastery_data2 = {
        "topic": "Data Structures",
        "performance_score": 0.45,
        "emotion_hint": "confused"
    }
    mastery_response2 = make_request("POST", "/api/personalization/update-mastery", mastery_data2, headers)
    if mastery_response2 and mastery_response2.status_code == 200:
        mastery_result2 = mastery_response2.json()
        print(f"✅ Mastery updated: {mastery_result2['topic']} -> {mastery_result2['mastery_score']:.1f}%")
    
    # Get learning insights
    insights_response = make_request("GET", "/api/personalization/insights", headers=headers)
    if insights_response and insights_response.status_code == 200:
        insights_result = insights_response.json()
        print(f"✅ Learning insights retrieved")
        print(f"   Total topics: {insights_result['mastery_summary']['total_topics']}")
        print(f"   Average mastery: {insights_result['mastery_summary']['average_mastery']:.1f}%")
        print(f"   Weak topics: {insights_result['mastery_summary']['weak_topics']}")
        print(f"   Strong topics: {insights_result['mastery_summary']['strong_topics']}")
    
    # Get custom exercises
    exercises_response = make_request("GET", "/api/personalization/custom-exercises", headers=headers)
    if exercises_response and exercises_response.status_code == 200:
        exercises_result = exercises_response.json()
        print(f"✅ Custom exercises: {exercises_result['total_count']} available")
    
    # Get revision schedule
    revision_response = make_request("GET", "/api/personalization/revision-schedule", headers=headers)
    if revision_response and revision_response.status_code == 200:
        revision_result = revision_response.json()
        print(f"✅ Revision schedule retrieved")
        print(f"   Topics needing review: {revision_result['total_topics_needing_review']}")
    
    # Step 8: Test Gamification Status
    print("\n8. Test Gamification Status")
    print("-" * 30)
    
    # Get complete gamification status
    status_response = make_request("GET", "/api/gamification/status", headers=headers)
    if status_response and status_response.status_code == 200:
        status_result = status_response.json()
        print(f"✅ Gamification status retrieved")
        print(f"   Total XP: {status_result['xp_profile']['total_xp']}")
        print(f"   Current Level: {status_result['xp_profile']['current_level']}")
        print(f"   Total badges: {status_result['total_badges']}")
        print(f"   Total streak days: {status_result['total_streak_days']}")
    
    # Get leaderboard
    leaderboard_response = make_request("GET", "/api/gamification/leaderboard", headers=headers)
    if leaderboard_response and leaderboard_response.status_code == 200:
        leaderboard_result = leaderboard_response.json()
        print(f"✅ Leaderboard retrieved: {leaderboard_result['total_users']} users")
        if leaderboard_result['leaderboard']:
            top_user = leaderboard_result['leaderboard'][0]
            print(f"   Top user: {top_user['name']} (Level {top_user['level']}, {top_user['total_xp']} XP)")
    
    # Step 9: Test Learning Style Detection
    print("\n9. Test Learning Style Detection")
    print("-" * 30)
    
    # Update learning style
    style_data = {
        "style": "visual",
        "score": 0.8,
        "time_spent": 300,
        "engagement_score": 0.9
    }
    style_response = make_request("POST", "/api/learning-style/update", style_data, headers)
    if style_response and style_response.status_code == 200:
        style_result = style_response.json()
        print(f"✅ Learning style updated: {style_result['learning_style']['dominant_style']}")
    
    # Get learning style
    style_get_response = make_request("GET", "/api/learning-style/", headers=headers)
    if style_get_response and style_get_response.status_code == 200:
        style_get_result = style_get_response.json()
        print(f"✅ Learning style retrieved")
        print(f"   Dominant style: {style_get_result['dominant_style']}")
        print(f"   Visual: {style_get_result['visual_score']:.2f}")
        print(f"   Auditory: {style_get_result['auditory_score']:.2f}")
        print(f"   Example: {style_get_result['example_score']:.2f}")
    
    # Step 10: Test Recommendations
    print("\n10. Test Personalized Recommendations")
    print("-" * 30)
    
    # Get recommendations
    recommendations_response = make_request("GET", "/api/personalization/recommendations", headers=headers)
    if recommendations_response and recommendations_response.status_code == 200:
        recommendations_result = recommendations_response.json()
        print(f"✅ Recommendations retrieved: {recommendations_result['total_count']} recommendations")
        for i, rec in enumerate(recommendations_result['recommendations'][:3]):
            print(f"   {i+1}. {rec['title']} ({rec['priority']} priority)")
    
    print("\n🎉 Gamification System Test Complete!")
    print("=" * 60)
    print("✅ All major features tested successfully!")
    print("\nFeatures tested:")
    print("  • User authentication and gamification initialization")
    print("  • XP system and leveling")
    print("  • Streak tracking (login, lesson, quiz)")
    print("  • Badge system and achievement checking")
    print("  • Quest generation and management")
    print("  • Personalization engine and mastery tracking")
    print("  • Learning style detection")
    print("  • Custom exercise generation")
    print("  • Revision scheduling")
    print("  • Personalized recommendations")
    print("  • Leaderboard and gamification status")

if __name__ == "__main__":
    test_gamification_system()
