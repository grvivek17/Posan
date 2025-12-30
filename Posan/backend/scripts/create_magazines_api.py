"""
Populate magazines through the backend API
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api/v1"

magazines_data = [
    {
        "title": "Wild Explorers",
        "description": "Discover amazing animals, nature, and wildlife from around the world!",
        "age_group": "6-8",
        "issue_number": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=600&fit=crop"
    },
    {
        "title": "Science Wizards",
        "description": "Explore fun experiments, cool inventions, and amazing discoveries!",
        "age_group": "9-11",
        "issue_number": 3,
        "cover_image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=600&fit=crop"
    },
    {
        "title": "Little Learners",
        "description": "Fun stories and colorful activities for our youngest readers!",
        "age_group": "3-5",
        "issue_number": 5,
        "cover_image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=600&fit=crop"
    },
    {
        "title": "Space Adventures",
        "description": "Blast off and learn about planets, stars, and the mysteries of space!",
        "age_group": "9-11",
        "issue_number": 2,
        "cover_image_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400&h=600&fit=crop"
    },
    {
        "title": "Creative Minds",
        "description": "Art projects and DIY crafts to spark imagination!",
        "age_group": "6-8",
        "issue_number": 4,
        "cover_image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=600&fit=crop"
    },
    {
        "title": "History Heroes",
        "description": "Travel back in time and meet amazing historical figures!",
        "age_group": "9-11",
        "issue_number": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&h=600&fit=crop"
    },
    {
        "title": "Math Magicians",
        "description": "Fun number games and puzzles that make math magical!",
        "age_group": "6-8",
        "issue_number": 2,
        "cover_image_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=600&fit=crop"
    },
    {
        "title": "Young Inventors",
        "description": "Learn about amazing inventions and create your own!",
        "age_group": "12-14",
       "issue_number": 1,
        "cover_image_url": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=400&h=600&fit=crop"
    },
    {
        "title": "Story Time Tales",
        "description": "Magical stories and fairy tales full of wonder!",
        "age_group": "3-5",
        "issue_number": 7,
        "cover_image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop"
    },
    {
        "title": "Ocean Explorers",
        "description": "Dive deep and discover incredible sea creatures!",
        "age_group": "6-8",
        "issue_number": 3,
        "cover_image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=600&fit=crop"
    },
    {
        "title": "Coding Kids",
        "description": "Learn to code through fun games and projects!",
        "age_group": "9-11",
        "issue_number": 2,
        "cover_image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=600&fit=crop"
    },
    {
        "title": "Planet Earth",
        "description": "Explore our amazing planet and learn how to protect it!",
        "age_group": "9-11",
        "issue_number": 5,
        "cover_image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=600&fit=crop"
    }
]

def create_magazines():
    print("🌱 Creating sample magazines...")
    created = 0
    
    for mag in magazines_data:
        try:
            response = requests.post(f"{API_BASE}/content/magazines", json=mag)
            if response.status_code == 201:
                created += 1
                print(f"  ✅ Created: {mag['title']}")
            else:
                print(f"  ❌ Failed: {mag['title']} - {response.text}")
        except Exception as e:
            print(f"  ❌ Error creating {mag['title']}: {e}")
    
    print(f"\n🎉 Successfully created {created}/{len(magazines_data)} magazines!")

if __name__ == "__main__":
    create_magazines()
