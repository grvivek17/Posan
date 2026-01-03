import requests
import json

url = "http://localhost:8000/api/v1/puzzles/generate"
params = {
    "puzzle_type": "word_search",
    "topic": "animals",
    "difficulty": "easy",
    "age_group": "6-8"
}

print("Testing AI Puzzle Generation...")
response = requests.post(url, params=params)

print(f"\nStatus: {response.status_code}")

if response.status_code == 201:
    print("✅ SUCCESS!")
    data = response.json()
    print(f"\nTitle: {data.get('title')}")
    print(f"Description: {data.get('description')}")
    print(f"Puzzle Type: {data.get('puzzle_type')}")
    print(f"Difficulty: {data.get('difficulty')}")
    print(f"Points: {data.get('points_reward')}")
    
    puzzle_data = data.get('puzzle_data', {})
    print(f"\nWords: {puzzle_data.get('words', [])}")
    print(f"Grid Size: {puzzle_data.get('grid_size')}")
    print(f"✨ AI puzzle generation is working!")
else:
    print(f"❌ Error: {response.text}")
