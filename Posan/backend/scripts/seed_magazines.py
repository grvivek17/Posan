"""
Seed script to populate database with sample magazine data
Inspired by popular kids' educational content platforms
"""
import sys
import os
from datetime import datetime, timedelta

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import SessionLocal
from app.models.content import Magazine
from app.models.user import AgeGroup
from sqlalchemy import func

def create_sample_magazines():
    db = SessionLocal()
    
    try:
        # Check if magazines already exist
        existing_count = db.query(func.count(Magazine.id)).scalar()
        
        if existing_count > 0:
            print(f"Database already has {existing_count} magazines. Skipping seed.")
            return
        
        # Sample magazines inspired by popular kids' platforms
        magazines = [
            {
                "title": "Wild Explorers",
                "description": "Discover amazing animals, nature, and wildlife from around the world! Learn fascinating facts about creatures big and small.",
                "age_group": AgeGroup.AGE_6_8,
                "issue_number": 1,
                "cover_image_url": "https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=7)
            },
            {
                "title": "Science Wizards",
                "description": "Become a science wizard! Explore fun experiments, cool inventions, and amazing discoveries that will blow your mind.",
                "age_group": AgeGroup.AGE_9_11,
                "issue_number": 3,
                "cover_image_url": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=14)
            },
            {
                "title": "Little Learners",
                "description": "Fun stories, colorful activities, and simple lessons perfect for our youngest readers! Learning has never been this fun.",
                "age_group": AgeGroup.AGE_3_5,
                "issue_number": 5,
                "cover_image_url": "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=3)
            },
            {
                "title": "Space Adventures",
                "description": "Blast off into space! Learn about planets, stars, astronauts, and the mysteries of the universe in this cosmic journey.",
                "age_group": "9-11",
                "issue_number": 2,
                "cover_image_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=10)
            },
            {
                "title": "Creative Minds",
                "description": "Unleash your creativity! Art projects, DIY crafts, and fun activities to spark imagination and artistic expression.",
                "age_group": AgeGroup.AGE_6_8,
                "issue_number": 4,
                "cover_image_url": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=5)
            },
            {
                "title": "History Heroes",
                "description": "Travel back in time and meet amazing historical figures! Discover how people lived in different eras.",
                "age_group": "9-11",
                "issue_number": 1,
                "cover_image_url": "https://images.unsplash.com/photo-1461360228754-6e81c478b882?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=12)
            },
            {
                "title": "Math Magicians",
                "description": "Make math magical! Fun number games, puzzles, and tricks that make learning math exciting and entertaining.",
                "age_group": AgeGroup.AGE_6_8,
                "issue_number": 2,
                "cover_image_url": "https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=8)
            },
            {
                "title": "Young Inventors",
                "description": "Learn about amazing inventions and how to create your own! Perfect for curious minds who love to build and tinker.",
                "age_group": AgeGroup.AGE_12_14,
                "issue_number": 1,
                "cover_image_url": "https://images.unsplash.com/photo-1581092918056-0c4c3acd3789?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=6)
            },
            {
                "title": "Story Time Tales",
                "description": "Magical stories, fairy tales, and adventures! Perfect bedtime reading full of wonder and imagination.",
                "age_group": "3-5",
                "issue_number": 7,
                "cover_image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=2)
            },
            {
                "title": "Ocean Explorers",
                "description": "Dive deep into the ocean and discover incredible sea creatures, coral reefs, and underwater mysteries!",
                "age_group": AgeGroup.AGE_6_8,
                "issue_number": 3,
                "cover_image_url": "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=9)
            },
            {
                "title": "Coding Kids",
                "description": "Learn to code through fun games and projects! Build your own apps, games, and digital creations.",
                "age_group": "9-11",
                "issue_number": 2,
                "cover_image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=4)
            },
            {
                "title": "Planet Earth",
                "description": "Explore our amazing planet! Learn about climates, continents, natural wonders, and how to protect our Earth.",
                "age_group": "9-11",
                "issue_number": 5,
                "cover_image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&h=600&fit=crop",
                "is_published": True,
                "publication_date": datetime.now() - timedelta(days=11)
            }
        ]
        
        # Create magazine objects
        db_magazines = []
        for mag_data in magazines:
            magazine = Magazine(**mag_data)
            db_magazines.append(magazine)
        
        # Add all magazines to database
        db.add_all(db_magazines)
        db.commit()
        
        print(f"✅ Successfully created {len(db_magazines)} sample magazines!")
        print("\nMagazines created:")
        for mag in db_magazines:
            print(f"  - {mag.title} (Issue #{mag.issue_number}, Age: {mag.age_group})")
        
    except Exception as e:
        print(f"❌ Error creating magazines: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🌱 Seeding database with sample magazines...")
    create_sample_magazines()
    print("\n🎉 Database seeding complete!")
