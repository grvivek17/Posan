# Puzzle Loading with AI & Open-Source APIs

## 🎮 **What We're Using:**

### 1. **HuggingFace AI** (Already Integrated!)
- **Word Search** - Generates themed word lists
- **Crossword** - Creates clues and answers
- Uses your existing Llama 3.2 models

### 2. **Unsplash API** (Free)
- **Jigsaw Puzzles** - Beautiful, royalty-free images
- No API key required for basic usage

### 3. **Open-Source Alternatives** (Optional)
- **Words API** - Word definitions and synonyms
- **Random Word API** - For word games
- **PuzzleScript** - Logic puzzle generation

---

## 🚀 **Quick Start - Generate Puzzles Now:**

### Method 1: Python Script (Recommended)

```bash
cd backend
python scripts/generate_puzzles_ai.py
```

**This will:**
1. ✅ Generate 10 Word Search puzzles using AI
2. ✅ Generate 8 Crossword puzzles using AI
3. ✅ Generate 8 Jigsaw puzzles using Unsplash
4. ✅ Mark 4 as "Daily Challenges"
5. ✅ Save all to database automatically

**Requirements:**
- Backend server running (`uvicorn app.main:app`)
- HUGGINGFACE_TOKEN set in environment
- Database connected

---

## 📊 **Puzzle Types Generated:**

| Type | Age Groups | Count | AI Source |
|------|------------|-------|-----------|
| 🔤 **Word Search** | All 4 | 10 | HuggingFace |
| 🔡 **Crossword** | All 4 | 8 | HuggingFace |
| 🧩 **Jigsaw** | All 4 | 8 | Unsplash Images |
| **Total** | | **26** | |

---

## 🎨 **Puzzle Topics by Age Group:**

### Toddlers (3-5):
- Animals, Colors, Shapes, Fruits, Toys

### Early (6-8):
- Dinosaurs, Ocean, Space, Sports, Food

### Middle (9-11):
- Science, Geography, History, Nature, Technology

### Preteens (12-14):
- Literature, World, Math, Chemistry, Coding

---

## 🔧 **How It Works:**

### Word Search Flow:
```
1. Script calls: POST /api/v1/ai/generate/word-search
2. AI generates themed words (e.g., "LION", "TIGER", "BEAR")
3. Saves to DB with puzzle_data: {"words": [...], "grid_size": 12}
4. Frontend generates grid and hides words
```

### Crossword Flow:
```
1. Script calls: POST /api/v1/ai/generate/crossword
2. AI generates clues and answers
3. Saves to DB with puzzle_data: {"clues": [{clue, answer},...]}
4. Frontend creates crossword grid
```

### Jigsaw Flow:
```
1. Script uses Unsplash image URLs
2. Saves to DB with image_url and pieces count
3. Frontend splits image into pieces
4. User drags/drops to solve
```

---

## 🌟 **Daily Challenges:**

The script automatically creates 4 daily challenges (one per age group):
- 🌟 Bonus points (1.5x reward)
- ⏰ Special highlighting in UI
- 🔄 Can regenerate daily

---

## 📡 **Open APIs Used:**

### 1. Your Backend AI Endpoints:
```
POST /api/v1/ai/generate/word-search
POST /api/v1/ai/generate/crossword
POST /api/v1/ai/generate/fun-fact
POST /api/v1/ai/generate/riddle
```

### 2. Unsplash (Images):
```
https://images.unsplash.com/photo-{ID}?w=600
- Free, no API key needed
- High-quality images
- Themed collections
```

### 3. Alternative Open-Source APIs:

**Words API** (wordsapi.com):
- Word definitions
- Synonyms/antonyms
- Free tier: 2,500 requests/day

**Random Word API** (random-word-api.herokuapp.com):
- GET /word?number=10
- Completely free
- No authentication

**JService** (jservice.io):
- Jeopardy questions
- GET /api/random?count=10
- Free trivia API

**Open Trivia DB** (opentdb.com):
- GET /api.php?amount=10
- Multiple categories
- Difficulty levels

---

## 🔌 **Alternative Puzzle Generators:**

### For Word Searches:
```python
import requests

# Random Word API
words = requests.get(
    "https://random-word-api.herokuapp.com/word?number=10"
).json()
```

### For Crosswords:
```python
# Words API (requires key)
url = "https://wordsapiv1.p.rapidapi.com/words/"
headers = {"X-RapidAPI-Key": "your_key"}
```

### For Trivia/Quiz:
```python
# Open Trivia DB
trivia = requests.get(
    "https://opentdb.com/api.php?amount=10&category=17&difficulty=easy"
).json()
```

---

## 📝 **Database Structure:**

```python
Puzzle Model:
{
    "title": "Animals Word Search",
    "puzzle_type": "WORD_SEARCH",  # or CROSSWORD, JIGSAW, SUDOKU
    "difficulty": "EASY",           # EASY, MEDIUM, HARD
    "age_group": "EARLY",           # TODDLER, EARLY, MIDDLE, PRETEEN
    "puzzle_data": {...},           # Puzzle-specific data
    "solution_data": {...},         # Solution/answers
    "image_url": "...",             # For jigsaw puzzles
    "points_reward": 50,
    "is_daily_challenge": False
}
```

---

## 🎯 **To Run the Generator:**

### Step 1: Ensure Backend is Running
```bash
# Terminal 1
cd backend
python -m uvicorn app.main:app --reload
```

### Step 2: Check HuggingFace Token
```bash
# In backend/.env
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
```

### Step 3: Run Generator
```bash
# Terminal 2
cd backend
python scripts/generate_puzzles_ai.py
```

### Step 4: Verify in Frontend
```
Open: http://localhost:5173/puzzles
See: 26 newly generated puzzles!
```

---

## 🔄 **Regenerate Puzzles:**

To create fresh puzzles:
```sql
-- Delete old puzzles (optional)
DELETE FROM puzzles;

-- Run generator again
python scripts/generate_puzzles_ai.py
```

---

## ⚡ **Performance & Costs:**

| Service | Cost | Rate Limit | Notes |
|---------|------|------------|-------|
| **HuggingFace** | Free | Generous | Your account |
| **Unsplash** | Free | 50/hour | No key needed |
| **Random Word API** | Free | Unlimited | Public API |
| **Open Trivia DB** | Free | 1 req/5sec | Public |

---

## 🚨** Troubleshooting:**

### Issue: AI generation fails
**Solution**:
- Check HUGGINGFACE_TOKEN is set
- Verify backend is running
- Check API endpoint: http://localhost:8000/docs

### Issue: Puzzles not appearing
**Solution**:
```sql
SELECT COUNT(*) FROM puzzles;
-- Should show 26+
```

### Issue: Script hangs
**Solution**:
- Increase timeout in script
- Generate in batches (modify script)
- Check internet connection

---

## 🎨 **Customization:**

### Add More Topics:
Edit `PUZZLE_TOPICS` in `generate_puzzles_ai.py`:
```python
PUZZLE_TOPICS = {
    "EARLY": ["your", "custom", "topics"],
}
```

### Change Puzzle Counts:
```python
for topic in topics[:5]:  # Generate 5 instead of 2
```

### Use Different Images:
```python
# Search Unsplash
"https://images.unsplash.com/photo-{ID}?w=600"
```

---

## 📚 **Resources:**

- **HuggingFace Hub**: https://huggingface.co/
- **Unsplash**: https://unsplash.com/
- **Random Word API**: https://random-word-api.herokuapp.com/
- **Open Trivia DB**: https://opentdb.com/
- **Words API**: https://www.wordsapi.com/

---

## ✅ **Next Steps:**

1. ✅ Run `generate_puzzles_ai.py`
2. ✅ Check `/puzzles` page
3. ✅ Test puzzle solving
4. 🔄 Generate daily challenges
5. 🎨 Customize topics/images
6. 📊 Track user progress

---

**Your puzzle system now uses AI to generate endless content!** 🎮✨
