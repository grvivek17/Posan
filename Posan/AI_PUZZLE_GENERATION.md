# 🎮 AI-Powered Puzzle Generation - POSAN

## Overview
POSAN now uses **Hugging Face AI models** to generate educational puzzles dynamically! This means unlimited, unique puzzles tailored to different topics, difficulty levels, and age groups.

---

## 🤖 **AI Models Used**

### **Primary Content Generation**
- **Meta Llama 3.2** (3B & 1B Instruct) - For generating words, clues, and content
- **Qwen 2.5** (1.5B Instruct) - Alternative content generation

### **Educational AI Models**
- **DeepSet RoBERTa** - Question answering and answer validation
- **Facebook BART** - Zero-shot classification for topics
- **DistilBERT** - Sentiment and confidence analysis

---

## 🧩 **Supported Puzzle Types**

### **1. Word Search** 🔍
- **AI generates**: Topic-related words using Hugging Face models
- **Grid generation**: Automatically places words in a grid
- **Customizable**: Grid size, number of words, difficulty
- **Example topics**: Animals, Space, Ocean, Sports, Food

**Generation Process**:
```
User requests "Ocean Animals, Medium"
    ↓
AI generates: WHALE, DOLPHIN, SHARK, OCTOPUS... (10 words)
    ↓
Algorithm places words in 12x12 grid
    ↓
Fills empty cells with random letters
    ↓
Returns complete puzzle with solution
```

### **2. Crossword** 📝
- **AI generates**: Clues and answers for the topic
- **Smart cluing**: Age-appropriate difficulty
- **Example**: "A large ocean mammal (5 letters)" → WHALE

**Generation Process**:
```
Request "Dinosaurs, Easy, 6-8 years"
    ↓
AI generates 8 clue-answer pairs
    ↓
Returns clues with answers
    ↓
Frontend renders interactive crossword
```

### **3. Sudoku** 🔢
- **Smart sizing**: 
  - 4x4 for ages 6-8
  - 6x6 for ages 9-11
  - 9x9 for ages 12-14
- **Valid grids**: Uses backtracking algorithm
- **Difficulty**: Removes cells based on difficulty

**Generation Process**:
```
Request "Sudoku, Medium, 9-11 years"
    ↓
Generates valid 6x6 Sudoku solution
    ↓
Removes 50% of numbers (medium difficulty)
    ↓
Returns puzzle + solution
```

---

## 🚀 **API Endpoint**

### **Generate Random Puzzle**

```http
POST /api/v1/puzzles/generate
```

**Query Parameters**:
| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `puzzle_type` | string | "word_search" | word_search, crossword, sudoku |
| `topic` | string | "animals" | Any topic (animals, space, ocean, etc.) |
| `difficulty` | string | "easy" | easy, medium, hard |
| `age_group` | string | "6-8" | 3-5, 6-8, 9-11, 12-14 |
| `save_to_db` | boolean | false | true/false |

**Example Request**:
```bash
curl -X POST "http://localhost:8000/api/v1/puzzles/generate?puzzle_type=word_search&topic=space&difficulty=medium&age_group=9-11"
```

**Example Response**:
```json
{
  "id": 0,
  "title": "Space Word Search",
  "description": "Find words related to space!",
  "puzzle_type": "word_search",
  "difficulty": "medium",
  "age_group": "9-11",
  "puzzle_data": {
    "topic": "space",
    "grid": [
      ["S", "T", "A", "R", "S", "..."],
      ["P", "L", "A", "N", "E", "..."],
      ...
    ],
    "words": ["STARS", "PLANET", "GALAXY", "COMET", ...],
    "word_locations": [...]
  },
  "solution_data": {
    "word_locations": [
      {"word": "STARS", "start": [0, 0], "end": [0, 4]}
    ]
  },
  "points_reward": 75,
  "created_at": "2026-01-01T19:30:00Z"
}
```

---

## 💻 **Backend Implementation**

### **File Structure**:
```
backend/
├── app/
│   ├── services/
│   │   └── ai_content.py          # ✨ AI puzzle generation logic
│   ├── api/endpoints/
│   │   └── puzzles.py              # 🔌 API endpoint
│   └── models/
│       └── puzzle.py               # 📦 Database model
```

###**Key Functions** in `ai_content.py`:

#### **1. `generate_word_search_words()`**
```python
def generate_word_search_words(topic, num_words=10, age_group="6-8"):
    """Uses Hugging Face LLM to generate topic-related words"""
    # AI prompt engineering for kid-appropriate words
    # Returns: ["LION", "TIGER", "BEAR", ...]
```

#### **2. `generate_complete_word_search()`**
```python
def generate_complete_word_search(topic, grid_size=12, num_words=10):
    """Complete word search with grid generation"""
    # 1. Get AI-generated words
    # 2. Create empty grid
    # 3. Place words (right, down, diagonal)
    # 4. Fill empty cells
    # Returns: {grid, words, locations}
```

#### **3. `generate_sudoku_puzzle()`**
```python
def generate_sudoku_puzzle(difficulty="easy", age_group="9-11"):
    """Generate valid Sudoku using backtracking"""
    # 1. Create valid solved grid
    # 2. Remove numbers based on difficulty
    # Returns: {puzzle, solution, grid_size}
```

#### **4. `generate_complete_puzzle()` - Master Function**
```python
def generate_complete_puzzle(puzzle_type, topic, difficulty, age_group):
    """Universal puzzle generator"""
    # Routes to specific generator based on puzzle_type
    # Returns: Complete puzzle data ready for frontend
```

---

## 🎨 **Frontend Integration**

### **Using the API**:

```javascript
// In your React component
import { puzzlesAPI } from '../services/api';

const generatePuzzle = async () => {
    try {
        const response = await puzzlesAPI.generateAIPuzzle({
            puzzle_type: "word_search",
            topic: "ocean",
            difficulty: "medium",
            age_group: "6-8"
        });
        
        setPuzzle(response.data);
    } catch (error) {
        console.error("Failed to generate puzzle:", error);
    }
};
```

### **Add to `frontend/src/services/api.js`**:

```javascript
// Puzzles API
export const puzzlesAPI = {
    // ... existing methods ...
    
    generateAIPuzzle: (params) => api.post('/puzzles/generate', null, { params }),
};
```

---

## 🎯 **Use Cases**

### **1. Daily Challenges**
```javascript
// Generate a new puzzle every day
const dailyPuzzle = await puzzlesAPI.generateAIPuzzle({
    topic: getRandomTopic(), // Animals, Space, Ocean, etc.
    difficulty: "medium",
    save_to_db: true  // Save for tracking
});
```

### **2. Personalized Learning**
```javascript
// Generate puzzles based on student's weak subjects
if (student.weakSubject === "Science") {
    const puzzle = await puzzlesAPI.generateAIPuzzle({
        topic: "science experiments",
        age_group: student.ageGroup
    });
}
```

### **3. Infinite Practice**
```javascript
// Students can generate unlimited puzzles
const generateNewPuzzle = () => {
    puzzlesAPI.generateAIPuzzle({
        puzzle_type: selectedType,
        topic: selectedTopic,
        difficulty: studentLevel
    });
};
```

---

## 📊 **Example Topics**

### **Education**:
- Math operations
- Science concepts
- Historical events
- Literary terms

### **Fun & Engaging**:
- Animals
- Sports
- Space
- Ocean life
- Dinosaurs
- Food
- Vehicles
- Weather

### **Seasonal**:
- Holidays
- Seasons
- Special events

---

## ⚙️ **Configuration**

### **Difficulty Scaling**:

| Difficulty | Word Search | Crossword | Sudoku |
|-----------|-------------|-----------|---------|
| **Easy** | 6 words, 10x10 grid | 5 clues | 30% cells removed |
| **Medium** | 10 words, 12x12 grid | 8 clues | 50% cells removed |
| **Hard** | 15 words, 15x15 grid | 12 clues | 70% cells removed |

### **Age-Appropriate Adjustments**:

| Age Group | Max Word Length | Grid Size | Sudoku Size |
|-----------|----------------|-----------|-------------|
| **3-5** | 5 letters | 8x8 | N/A |
| **6-8** | 7 letters | 10x10 | 4x4 |
| **9-11** | 9 letters | 12x12 | 6x6 |
| **12-14** | 12 letters | 15x15 | 9x9 |

---

## 🧪 **Testing the Feature**

### **1. Test via API Docs**:
```
1. Navigate to: http://localhost:8000/docs
2. Find: POST /api/v1/puzzles/generate
3. Click "Try it out"
4. Set parameters:
   - puzzle_type: word_search
   - topic: animals
   - difficulty: easy
   - age_group: 6-8
5. Execute
6. View generated puzzle!
```

### **2. Test via cURL**:
```bash
curl -X POST \
  "http://localhost:8000/api/v1/puzzles/generate?puzzle_type=sudoku&difficulty=medium&age_group=9-11" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **3. Test via Frontend** (after integration):
```javascript
<button onClick={() => generatePuzzle("word_search", "space")}>
    Generate Space Puzzle
</button>
```

---

## 🚀 **Benefits**

✅ **Unlimited Content**: Never run out of puzzles
✅ **Personalized**: Tailored to each child's level
✅ **Educational**: AI ensures topic relevance
✅ **Engaging**: Fresh puzzles keep kids interested
✅ **Scalable**: Generate on-demand, no storage needed
✅ **Cost-Effective**: Uses free Hugging Face inference

---

## 🔮 **Future Enhancements**

1. **Image-based Puzzles**: Use Stable Diffusion for jigsaw images
2. **Adaptive Difficulty**: AI learns and adjusts based on student performance
3. **Multi-language**: Generate puzzles in different languages
4. **Custom Themes**: Parents can request specific topics
5. **Collaborative Puzzles**: Multi-player puzzle solving

---

## 📝 **Summary**

The AI-powered puzzle generation system:
- Uses **Hugging Face models** to create unique puzzles
- Supports **Word Search, Crossword, and Sudoku**
- Generates content **on-demand** with custom topics
- Adapts to **age groups** and **difficulty levels**
- Available via **REST API** at `/api/v1/puzzles/generate`

**Backend**: Running ✅ (http://localhost:8000)  
**Frontend**: Ready for integration ⏳  
**AI Models**: Connected ✅

Start generating puzzles now! 🎉
