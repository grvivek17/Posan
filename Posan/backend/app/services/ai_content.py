"""
AI Content Generation Service using Hugging Face models.
Generates kid-friendly stories, articles, puzzles, and educational content.
"""
from typing import Optional, List, Dict, Any
from huggingface_hub import InferenceClient
from app.core.config import settings

# Hugging Face configuration
HF_TOKEN = settings.HUGGINGFACE_TOKEN


class ContentGenerator:
    """AI-powered content generator for kids' magazine."""
    
    def __init__(self):
        self.client = InferenceClient(token=HF_TOKEN)
        # Models that support chat completion (in order of preference)
        self.models = [
            "meta-llama/Llama-3.2-3B-Instruct",
            "meta-llama/Llama-3.2-1B-Instruct",
            "Qwen/Qwen2.5-1.5B-Instruct",
        ]
    
    def _generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Hugging Face Inference API with chat completion."""
        print(f"\n{'='*60}")
        print(f"AI GENERATION REQUEST")
        print(f"{'='*60}")
        print(f"Prompt: {prompt[:200]}...")
        print(f"Max tokens: {max_tokens}")
        
        messages = [
            {"role": "system", "content": "You are a helpful assistant that creates kid-friendly, educational content. Always be positive, fun, and age-appropriate."},
            {"role": "user", "content": prompt}
        ]
        
        for model in self.models:
            try:
                print(f"\nTrying model: {model}")
                response = self.client.chat_completion(
                    messages=messages,
                    model=model,
                    max_tokens=max_tokens,
                    temperature=0.7,
                )
                content = response.choices[0].message.content
                if content and len(content.strip()) > 10:
                    print(f"✅ Success with model: {model}")
                    print(f"Response preview: {content[:150]}...")
                    print(f"{'='*60}\n")
                    return content.strip()
            except Exception as e:
                print(f"❌ Model {model} failed: {e}")
                continue
        
        # If all models fail, return fallback content
        print("⚠️  All models failed, using fallback content")
        print(f"{'='*60}\n")
        return self._get_fallback_content(prompt)
    
    def _get_fallback_content(self, prompt: str) -> str:
        """Return fallback content when AI generation fails."""
        # Provide sample content based on keywords in the prompt
        prompt_lower = prompt.lower()
        
        if "story" in prompt_lower:
            return """Once upon a time, in a magical land far away, there lived a curious young explorer named Sam. 
Sam loved discovering new things about the world. One sunny morning, Sam decided to go on an adventure.
Along the way, Sam met new friends and learned that kindness and curiosity are the greatest treasures of all.
And they all lived happily ever after, ready for their next adventure together!"""
        
        elif "article" in prompt_lower or "fact" in prompt_lower:
            return """Did you know? The world is full of amazing wonders waiting to be discovered!
Every day, scientists learn new things about our planet, space, and the creatures that live with us.
Learning is an adventure that never ends. What will you discover today?
Fun Activity: Try to find three new facts about your favorite animal!"""
        
        elif "quiz" in prompt_lower or "question" in prompt_lower:
            return """Q: What makes learning fun?
A) Reading books
B) Asking questions
C) Exploring new places
D) All of the above!
Answer: D
Explanation: Learning is fun when we stay curious and try new things!"""
        
        elif "word" in prompt_lower:
            return "LEARN\nDISCOVER\nEXPLORE\nWONDER\nCURIOUS"
        
        elif "riddle" in prompt_lower:
            return """Riddle: I have pages but I'm not a tree. I have words but I can't speak. What am I?
Answer: A book!"""
        
        else:
            return "Content is being generated. Please try again in a moment!"
    
    def generate_story(
        self,
        topic: str,
        age_group: str = "6-8",
        word_count: int = 300,
        characters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate a kid-friendly story.
        
        Args:
            topic: The main theme of the story
            age_group: Target age group (3-5, 6-8, 9-11, 12-14)
            word_count: Approximate word count
            characters: Optional list of character names
        """
        age_descriptions = {
            "3-5": "simple words, short sentences, happy themes, repetition",
            "6-8": "adventurous, educational, friendly characters, moral lessons",
            "9-11": "more complex plots, mystery elements, problem-solving",
            "12-14": "deeper themes, relatable characters, coming-of-age elements"
        }
        
        char_text = f" featuring characters named {', '.join(characters)}" if characters else ""
        
        prompt = f"""Write a {word_count}-word children's story about {topic}{char_text}.

Target age: {age_group} years old
Style: {age_descriptions.get(age_group, age_descriptions['6-8'])}

Requirements:
- Kid-friendly and appropriate
- Educational value
- Positive message
- Engaging and fun

Story:
"""
        
        story_text = self._generate_text(prompt, max_tokens=word_count * 2)
        
        # Generate a title
        title_prompt = f"Create a catchy, kid-friendly title for this story about {topic}. Just the title, nothing else:"
        title = self._generate_text(title_prompt, max_tokens=20).strip()
        
        return {
            "title": title if title else f"A Story About {topic.title()}",
            "content": story_text,
            "topic": topic,
            "age_group": age_group,
            "word_count": len(story_text.split())
        }
    
    def generate_article(
        self,
        topic: str,
        age_group: str = "6-8",
        article_type: str = "educational"
    ) -> Dict[str, Any]:
        """
        Generate an educational article for kids.
        
        Args:
            topic: The subject of the article
            age_group: Target age group
            article_type: Type of article (educational, fun_facts, how_to, science)
        """
        type_prompts = {
            "educational": "informative and teaches something new",
            "fun_facts": "filled with amazing and surprising facts",
            "how_to": "step-by-step guide that's easy to follow",
            "science": "explains scientific concepts in a fun way"
        }
        
        prompt = f"""Write a short, engaging article for kids aged {age_group} about {topic}.

Article type: {type_prompts.get(article_type, 'educational')}

Requirements:
- Use simple, age-appropriate language
- Include interesting facts
- Make it fun and engaging
- Add a "Did You Know?" section
- End with a fun activity or question

Article:
"""
        
        content = self._generate_text(prompt, max_tokens=400)
        
        # Generate title
        title_prompt = f"Create an exciting article title about {topic} for kids. Just the title:"
        title = self._generate_text(title_prompt, max_tokens=15).strip()
        
        return {
            "title": title if title else f"Discover: {topic.title()}",
            "content": content,
            "topic": topic,
            "age_group": age_group,
            "article_type": article_type
        }
    
    def generate_quiz_questions(
        self,
        topic: str,
        num_questions: int = 5,
        age_group: str = "6-8"
    ) -> List[Dict[str, Any]]:
        """
        Generate quiz questions for kids.
        
        Args:
            topic: Subject of the quiz
            num_questions: Number of questions to generate
            age_group: Target age group
        """
        prompt = f"""Create {num_questions} multiple-choice quiz questions about {topic} for kids aged {age_group}.

Format each question exactly like this:
Q: [Question]
A) [Option 1]
B) [Option 2]
C) [Option 3]
D) [Option 4]
Answer: [Correct letter]
Explanation: [Brief explanation]

Make questions fun, educational, and age-appropriate.

Questions:
"""
        
        response = self._generate_text(prompt, max_tokens=num_questions * 150)
        
        # Parse the response into structured format
        questions = []
        current_q = {}
        
        lines = response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_q:
                    questions.append(current_q)
                current_q = {"question": line[2:].strip(), "options": []}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_q.setdefault("options", []).append(line[2:].strip())
            elif line.startswith('Answer:'):
                current_q["correct_answer"] = line[7:].strip()
            elif line.startswith('Explanation:'):
                current_q["explanation"] = line[12:].strip()
        
        if current_q and current_q.get("question"):
            questions.append(current_q)
        
        return questions[:num_questions]
    
    def generate_word_search_words(
        self,
        topic: str,
        num_words: int = 10,
        age_group: str = "6-8"
    ) -> List[str]:
        """Generate words for a word search puzzle."""
        max_length = {"3-5": 5, "6-8": 7, "9-11": 9, "12-14": 12}.get(age_group, 7)
        
        prompt = f"""List {num_words} simple words related to {topic} for a kids' word search puzzle.
Age group: {age_group} years
Maximum word length: {max_length} letters

Requirements:
- Simple, age-appropriate words only
- All words related to the topic
- No compound words or phrases
- One word per line

Words:
"""
        
        response = self._generate_text(prompt, max_tokens=100)
        
        # Parse words from response
        words = []
        for line in response.split('\n'):
            word = line.strip().upper()
            # Clean up the word
            word = ''.join(c for c in word if c.isalpha())
            if word and len(word) >= 3 and len(word) <= max_length:
                words.append(word)
        
        return words[:num_words]
    
    def generate_crossword_clues(
        self,
        topic: str,
        num_clues: int = 8,
        age_group: str = "6-8"
    ) -> List[Dict[str, str]]:
        """Generate crossword clues and answers."""
        prompt = f"""Create {num_clues} crossword clues and answers about {topic} for kids aged {age_group}.

Format:
Clue: [Simple clue]
Answer: [Single word, 3-8 letters]

Make clues fun and easy to understand.

Clues:
"""
        
        response = self._generate_text(prompt, max_tokens=num_clues * 50)
        
        clues = []
        current_clue = {}
        
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('Clue:'):
                if current_clue:
                    clues.append(current_clue)
                current_clue = {"clue": line[5:].strip()}
            elif line.startswith('Answer:'):
                answer = line[7:].strip().upper()
                answer = ''.join(c for c in answer if c.isalpha())
                current_clue["answer"] = answer
        
        if current_clue and current_clue.get("clue") and current_clue.get("answer"):
            clues.append(current_clue)
        
        return clues[:num_clues]
    
    def generate_fun_fact(self, topic: str, age_group: str = "6-8") -> str:
        """Generate a fun fact for kids."""
        prompt = f"""Tell me one amazing fun fact about {topic} for kids aged {age_group}.
Keep it short, surprising, and easy to understand. Just the fact, nothing else:
"""
        
        fact = self._generate_text(prompt, max_tokens=100)
        return fact.strip()
    
    def generate_riddle(self, topic: str, age_group: str = "6-8") -> Dict[str, str]:
        """Generate a kid-friendly riddle."""
        prompt = f"""Create a fun riddle about {topic} for kids aged {age_group}.

Format:
Riddle: [The riddle question]
Answer: [The answer]

Make it fun and not too hard!

"""
        
        response = self._generate_text(prompt, max_tokens=100)
        
        riddle = {"riddle": "", "answer": ""}
        for line in response.split('\n'):
            line = line.strip()
            if line.startswith('Riddle:'):
                riddle["riddle"] = line[7:].strip()
            elif line.startswith('Answer:'):
                riddle["answer"] = line[7:].strip()
        
        return riddle
    
    def analyze_test_results(
        self,
        subject: str,
        test_scores: Dict[str, Any],
        age_group: str = "6-8",
        student_name: str = "Student"
    ) -> Dict[str, Any]:
        """
        Analyze test results and provide personalized recommendations.
        
        Args:
            subject: The subject of the test (e.g., Math, Science, English)
            test_scores: Dictionary with score details (score, total, weak_areas, strong_areas)
            age_group: Target age group
            student_name: Name of the student
        
        Returns:
            Dictionary with analysis, recommendations, and encouragement
        """
        score = test_scores.get('score', 0)
        total = test_scores.get('total', 100)
        percentage = (score / total * 100) if total > 0 else 0
        weak_areas = test_scores.get('weak_areas', [])
        strong_areas = test_scores.get('strong_areas', [])
        
        # Performance level
        if percentage >= 90:
            performance_level = "excellent"
        elif percentage >= 75:
            performance_level = "very good"
        elif percentage >= 60:
            performance_level = "good"
        elif percentage >= 50:
            performance_level = "satisfactory"
        else:
            performance_level = "needs improvement"
        
        weak_areas_text = f"Areas needing improvement: {', '.join(weak_areas)}" if weak_areas else "No specific weak areas identified"
        strong_areas_text = f"Strong areas: {', '.join(strong_areas)}" if strong_areas else ""
        
        prompt = f"""Analyze this test performance for a {age_group} year old student and provide personalized, encouraging recommendations.

Student: {student_name}
Subject: {subject}
Score: {score}/{total} ({percentage:.1f}%)
Performance Level: {performance_level}
{strong_areas_text}
{weak_areas_text}

Provide a warm, encouraging analysis in this format:

**Performance Summary:**
[Brief, positive summary of overall performance]

**Strengths:**
[List 2-3 specific strengths, even if small achievements]

**Areas for Growth:**
[List 2-3 specific areas to focus on, presented positively]

**Personalized Recommendations:**
1. [Specific, actionable study tip]
2. [Fun activity or resource to help improve]
3. [Motivation and encouragement]

**Next Steps:**
[Concrete action plan for improvement]

Keep the tone positive, encouraging, and age-appropriate. Focus on growth mindset.
"""
        
        analysis = self._generate_text(prompt, max_tokens=600)
        
        # Generate motivational quote
        quote_prompt = f"Generate a short, inspiring quote about learning and growth for a {age_group} year old student. Just the quote, nothing else:"
        motivational_quote = self._generate_text(quote_prompt, max_tokens=50)
        
        return {
            "subject": subject,
            "score": score,
            "total": total,
            "percentage": round(percentage, 1),
            "performance_level": performance_level,
            "analysis": analysis,
            "motivational_quote": motivational_quote.strip('"'),
            "weak_areas": weak_areas,
            "strong_areas": strong_areas
        }



# Create a singleton instance
content_generator = ContentGenerator()


# Convenience functions
def generate_story(topic: str, age_group: str = "6-8", **kwargs) -> Dict[str, Any]:
    return content_generator.generate_story(topic, age_group, **kwargs)


def generate_article(topic: str, age_group: str = "6-8", **kwargs) -> Dict[str, Any]:
    return content_generator.generate_article(topic, age_group, **kwargs)


def generate_quiz(topic: str, num_questions: int = 5, age_group: str = "6-8") -> List[Dict]:
    return content_generator.generate_quiz_questions(topic, num_questions, age_group)


def generate_word_search(topic: str, num_words: int = 10, age_group: str = "6-8") -> List[str]:
    return content_generator.generate_word_search_words(topic, num_words, age_group)


def generate_crossword(topic: str, num_clues: int = 8, age_group: str = "6-8") -> List[Dict]:
    return content_generator.generate_crossword_clues(topic, num_clues, age_group)
