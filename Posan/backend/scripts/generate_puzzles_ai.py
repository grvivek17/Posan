"""
Puzzle Generator & Loader
Generates puzzles using HuggingFace AI and open-source APIs
"""
import requests
import json
import random
from datetime import datetime, timedelta

# Backend API base URL
API_BASE = "http://localhost:8000/api/v1"

# Puzzle topics for different age groups
PUZZLE_TOPICS = {
    "TODDLER": ["animals", "colors", "shapes", "fruits", "toys"],
    "EARLY": ["dinosaurs", "ocean", "space", "sports", "food"],
    "MIDDLE": ["science", "geography", "history", "nature", "technology"],
    "PRETEEN": ["literature", "world", "math", "chemistry", "coding"]
}

AGE_GROUP_MAP = {
    "TODDLER": "3-5",
    "EARLY": "6-8",
    "MIDDLE": "9-11",
    "PRETEEN": "12-14"
}

def generate_word_search_puzzles():
    """Generate word search puzzles using HuggingFace AI"""
    print("🔤 Generating Word Search Puzzles...")
    puzzles = []
    
    for age_group, topics in PUZZLE_TOPICS.items():
        for topic in topics[:2]:  # 2 per age group
            try:
                # Call AI endpoint to generate words
                response = requests.post(
                    f"{API_BASE}/ai/generate/word-search",
                    json={
                        "topic": topic,
                        "num_words": 10 if age_group in ['TODDLER', 'EARLY'] else 12,
                        "age_group": AGE_GROUP_MAP[age_group]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    words = data.get('words', [])
                    
                    if words:
                        puzzle = {
                            "title": f"{topic.title()} Word Search",
                            "description": f"Find all the {topic}-related words hidden in the grid!",
                            "puzzle_type": "WORD_SEARCH",
                            "difficulty": "EASY" if age_group in ['TODDLER', 'EARLY'] else "MEDIUM",
                            "age_group": age_group,
                            "puzzle_data": {"words": words, "grid_size": 12},
                            "solution_data": {"words": words},
                            "points_reward": 50,
                            "is_daily_challenge": False
                        }
                        puzzles.append(puzzle)
                        print(f"  ✅ Created: {puzzle['title']}")
                else:
                    print(f"  ❌ Failed for {topic}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error for {topic}: {e}")
    
    return puzzles

def generate_crossword_puzzles():
    """Generate crossword puzzles using HuggingFace AI"""
    print("\n🔡 Generating Crossword Puzzles...")
    puzzles = []
    
    for age_group, topics in PUZZLE_TOPICS.items():
        for topic in topics[2:4]:  # Different topics than word search
            try:
                # Call AI endpoint to generate clues
                response = requests.post(
                    f"{API_BASE}/ai/generate/crossword",
                    json={
                        "topic": topic,
                        "num_clues": 6 if age_group == 'TODDLER' else 8,
                        "age_group": AGE_GROUP_MAP[age_group]
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    clues = response.json()
                    
                    if clues and len(clues) > 0:
                        puzzle = {
                            "title": f"{topic.title()} Crossword",
                            "description": f"Solve the crossword puzzle about {topic}!",
                            "puzzle_type": "CROSSWORD",
                            "difficulty": "MEDIUM" if age_group in ['EARLY', 'MIDDLE'] else "HARD",
                            "age_group": age_group,
                            "puzzle_data": {"clues": clues},
                            "solution_data": {"clues": clues},
                            "points_reward": 75,
                            "is_daily_challenge": False
                        }
                        puzzles.append(puzzle)
                        print(f"  ✅ Created: {puzzle['title']}")
                else:
                    print(f"  ❌ Failed for {topic}: {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ Error for {topic}: {e}")
    
    return puzzles

def generate_jigsaw_puzzles():
    """Generate jigsaw puzzles using Unsplash images"""
    print("\n🧩 Generating Jigsaw Puzzles...")
    puzzles = []
    
    # Unsplash topics for different age groups
    unsplash_topics = {
        "TODDLER": [
            ("cute animals", "https://images.unsplash.com/photo-1425082661705-1834bfd09dca?w=600"),
            ("colorful toys", "https://images.unsplash.com/photo-1558060370-d644479cb6f7?w=600")
        ],
        "EARLY": [
            ("dinosaurs", "https://images.unsplash.com/photo-1551903011-8f86fea08f73?w=600"),
            ("underwater", "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=600")
        ],
        "MIDDLE": [
            ("space galaxy", "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=600"),
            ("nature landscape", "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=600")
        ],
        "PRETEEN": [
            ("architecture", "https://images.unsplash.com/photo-1511818966892-d7d671e672a2?w=600"),
            ("abstract art", "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=600")
        ]
    }
    
    for age_group, topics in unsplash_topics.items():
        for topic_name, image_url in topics:
            pieces = {"TODDLER": 9, "EARLY": 16, "MIDDLE": 25, "PRETEEN": 36}[age_group]
            
            puzzle = {
                "title": f"{topic_name.title()} Jigsaw",
                "description": f"Put together this beautiful {topic_name} puzzle!",
                "puzzle_type": "JIGSAW",
                "difficulty": "EASY" if age_group == 'TODDLER' else ("MEDIUM" if age_group == 'EARLY' else "HARD"),
                "age_group": age_group,
                "puzzle_data": {
                    "pieces": pieces,
                    "grid": f"{int(pieces**0.5)}x{int(pieces**0.5)}"
                },
                "solution_data": {"image_url": image_url},
                "image_url": image_url,
                "points_reward": 30 * (pieces // 9),
                "time_limit_seconds": 300 * (pieces // 9),
                "is_daily_challenge": False
            }
            puzzles.append(puzzle)
            print(f"  ✅ Created: {puzzle['title']}")
    
    return puzzles

def create_daily_challenges(all_puzzles):
    """Mark some puzzles as daily challenges"""
    print("\n⭐ Creating Daily Challenges...")
    
    if not all_puzzles:
        return []
    
    # Select 4 puzzles as daily challenges (one per age group)
    daily_puzzles = []
    for age_group in ["TODDLER", "EARLY", "MIDDLE", "PRETEEN"]:
        age_puzzles = [p for p in all_puzzles if p['age_group'] == age_group]
        if age_puzzles:
            challenge = random.choice(age_puzzles)
            challenge['is_daily_challenge'] = True
            challenge['challenge_date'] = datetime.now()
            challenge['points_reward'] = int(challenge['points_reward'] * 1.5)  # Bonus points
            daily_puzzles.append(challenge)
            print(f"  🌟 {age_group}: {challenge['title']}")
    
    return daily_puzzles

def save_puzzles_to_db(puzzles):
    """Save puzzles to database via API"""
    print("\n💾 Saving Puzzles to Database...")
    saved = 0
    failed = 0
    
    for puzzle in puzzles:
        try:
            response = requests.post(
                f"{API_BASE}/puzzles/puzzles",
                json=puzzle,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                saved += 1
                print(f"  ✅ Saved: {puzzle['title']}")
            else:
                failed += 1
                print(f"  ❌ Failed: {puzzle['title']} - {response.text[:100]}")
                
        except Exception as e:
            failed += 1
            print(f"  ❌ Error saving {puzzle['title']}: {e}")
    
    return saved, failed

def main():
    print("=" * 60)
    print(" 🎮 PUZZLE GENERATOR - Using HuggingFace AI & Open APIs")
    print("=" * 60)
    
    all_puzzles = []
    
    # Generate Word Search puzzles
    word_searches = generate_word_search_puzzles()
    all_puzzles.extend(word_searches)
    
    # Generate Crossword puzzles
    crosswords = generate_crossword_puzzles()
    all_puzzles.extend(crosswords)
    
    # Generate Jigsaw puzzles
    jigsaws = generate_jigsaw_puzzles()
    all_puzzles.extend(jigsaws)
    
    # Create daily challenges
    create_daily_challenges(all_puzzles)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Generated {len(all_puzzles)} puzzles:")
    print(f"   🔤 Word Search: {len(word_searches)}")
    print(f"   🔡 Crossword: {len(crosswords)}")
    print(f"   🧩 Jigsaw: {len(jigsaws)}")
    print("=" * 60)
    
    # Save to database
    if all_puzzles:
        saved, failed = save_puzzles_to_db(all_puzzles)
        print("\n" + "=" * 60)
        print(f"✅ Successfully saved: {saved} puzzles")
        print(f"❌ Failed: {failed} puzzles")
        print("=" * 60)
    
    print("\n🎉 Puzzle generation complete!")

if __name__ == "__main__":
    main()
