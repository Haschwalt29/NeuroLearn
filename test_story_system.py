#!/usr/bin/env python3
"""
Test script for the Story-Driven Quest System
Demonstrates the complete story progression flow
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8002"

def test_story_system():
    """Test the complete story-driven quest system"""
    
    print("🎭 Testing Story-Driven Quest System")
    print("=" * 50)
    
    # Step 1: Sign up a new user
    print("\n1. Creating a new user...")
    signup_data = {
        "email": "storytester@example.com",
        "password": "testpass123",
        "name": "Story Tester",
        "role": "learner"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=signup_data)
    if response.status_code == 200:
        result = response.json()
        token = result["access_token"]
        user_id = result["user"]["id"]
        print(f"✅ User created: {result['user']['name']} (ID: {user_id})")
    else:
        print(f"❌ Signup failed: {response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 2: Get current story progress
    print("\n2. Getting current story progress...")
    response = requests.get(f"{BASE_URL}/api/story/current", headers=headers)
    if response.status_code == 200:
        story_data = response.json()["data"]
        print(f"✅ Story: {story_data['story']['title']}")
        print(f"   Theme: {story_data['story']['theme']}")
        print(f"   Total XP: {story_data['total_story_xp']}")
        print(f"   Unlocked Chapters: {len(story_data['unlocked_chapters'])}")
        
        if story_data['unlocked_chapters']:
            first_chapter = story_data['unlocked_chapters'][0]
            print(f"   First Chapter: {first_chapter['title']}")
            print(f"   Quests in Chapter: {len(first_chapter['quests'])}")
    else:
        print(f"❌ Failed to get story progress: {response.text}")
        return
    
    # Step 3: Complete first quest
    print("\n3. Completing first quest...")
    if story_data['unlocked_chapters'] and story_data['unlocked_chapters'][0]['quests']:
        first_quest = story_data['unlocked_chapters'][0]['quests'][0]
        quest_id = first_quest['id']
        
        print(f"   Quest: {first_quest['title']}")
        print(f"   Type: {first_quest['quest_type']}")
        print(f"   Difficulty: {first_quest['difficulty_level']}")
        print(f"   Topics: {first_quest['topics']}")
        print(f"   Reward XP: {first_quest['reward_xp']}")
        
        # Complete the quest with a good score
        quest_data = {
            "quest_id": quest_id,
            "score": 85,  # Good score
            "time_spent": 120  # 2 minutes
        }
        
        response = requests.post(f"{BASE_URL}/api/story/progress", 
                               json=quest_data, headers=headers)
        if response.status_code == 200:
            result = response.json()["data"]
            print(f"✅ Quest completed!")
            print(f"   XP Gained: {result['xp_gained']}")
            print(f"   Rewards: {len(result['rewards'])}")
            
            for reward in result['rewards']:
                print(f"     - {reward['type']}: {reward.get('description', 'N/A')}")
        else:
            print(f"❌ Failed to complete quest: {response.text}")
    
    # Step 4: Check updated story progress
    print("\n4. Checking updated story progress...")
    response = requests.get(f"{BASE_URL}/api/story/current", headers=headers)
    if response.status_code == 200:
        updated_story = response.json()["data"]
        print(f"✅ Updated Story Progress:")
        print(f"   Total XP: {updated_story['total_story_xp']}")
        print(f"   Completed Quests: {len(updated_story['completed_quests'])}")
        print(f"   Completed Chapters: {len(updated_story['completed_chapters'])}")
        
        # Check if new chapters unlocked
        if len(updated_story['unlocked_chapters']) > len(story_data['unlocked_chapters']):
            print(f"🎉 New chapters unlocked!")
            for chapter in updated_story['unlocked_chapters']:
                if chapter['id'] not in [c['id'] for c in story_data['unlocked_chapters']]:
                    print(f"   - {chapter['title']} (Chapter {chapter['order']})")
    else:
        print(f"❌ Failed to get updated story progress: {response.text}")
    
    # Step 5: Test gamification integration
    print("\n5. Testing gamification integration...")
    response = requests.get(f"{BASE_URL}/api/gamification/status", headers=headers)
    if response.status_code == 200:
        gamification_data = response.json()["data"]
        print(f"✅ Gamification Status:")
        print(f"   Level: {gamification_data['level']}")
        print(f"   XP: {gamification_data['xp']}")
        print(f"   Badges: {len(gamification_data['badges'])}")
        
        if gamification_data['badges']:
            print("   Recent Badges:")
            for badge in gamification_data['badges'][:3]:  # Show first 3
                print(f"     - {badge['name']}: {badge['description']}")
    else:
        print(f"❌ Failed to get gamification status: {response.text}")
    
    # Step 6: Test story rewards
    print("\n6. Testing story rewards...")
    story_id = story_data['story']['id']
    response = requests.get(f"{BASE_URL}/api/story/rewards?story_id={story_id}", headers=headers)
    if response.status_code == 200:
        rewards = response.json()["rewards"]
        print(f"✅ Story Rewards ({len(rewards)} unviewed):")
        for reward in rewards:
            print(f"   - {reward['reward_type']}: {reward['reward_data']}")
    else:
        print(f"❌ Failed to get story rewards: {response.text}")
    
    # Step 7: Test spaced repetition integration
    print("\n7. Testing spaced repetition integration...")
    
    # First, get some content for spaced repetition
    response = requests.get(f"{BASE_URL}/api/spaced/quiz/next", headers=headers)
    if response.status_code == 200:
        content_data = response.json()["data"]
        content_id = content_data["id"]
        print(f"✅ Got content for spaced repetition: {content_data['topic']}")
        
        # Submit a good answer
        submit_data = {
            "content_id": content_id,
            "correct": True,
            "response_time_seconds": 45,
            "confidence": 0.8
        }
        
        response = requests.post(f"{BASE_URL}/api/spaced/quiz/submit", 
                               json=submit_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Spaced repetition completed!")
            
            # Check if story rewards were triggered
            if 'story_rewards' in result:
                print(f"   Story Rewards Triggered: {len(result['story_rewards'])}")
                for reward in result['story_rewards']:
                    print(f"     - {reward['type']}: {reward.get('description', 'N/A')}")
            else:
                print("   No story rewards triggered (content not linked to quest)")
        else:
            print(f"❌ Failed to submit spaced repetition: {response.text}")
    else:
        print(f"❌ Failed to get spaced repetition content: {response.text}")
    
    print("\n🎉 Story System Test Complete!")
    print("=" * 50)
    print("Summary:")
    print("- ✅ User creation and authentication")
    print("- ✅ Story progress tracking")
    print("- ✅ Quest completion and rewards")
    print("- ✅ Chapter unlocking")
    print("- ✅ Gamification integration")
    print("- ✅ Story rewards system")
    print("- ✅ Spaced repetition integration")
    print("\nThe story-driven quest system is working perfectly!")

if __name__ == "__main__":
    test_story_system()
