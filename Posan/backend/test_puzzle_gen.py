import requests

# Test the AI puzzle generation endpoint
url = "http://localhost:8000/api/v1/puzzles/generate"
params = {
    "puzzle_type": "word_search",
    "topic": "animals",
    "difficulty": "easy",
    "age_group": "6-8"
}

print("Testing AI Puzzle Generation Endpoint...")
print(f"URL: {url}")
print(f"Params: {params}")

try:
    response = requests.post(url, params=params)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! Puzzle generated")
        data = response.json()
        print(f"Title: {data.get('title')}")
        print(f"Puzzle Type: {data.get('puzzle_type')}")
        print(f"Description: {data.get('description')}")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Exception: {e}")
