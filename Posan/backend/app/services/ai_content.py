"""
AI Content Generation Service using Hugging Face models.
Generates kid-friendly stories, articles, puzzles, and educational content.
Enhanced with Education Toolkit models for better educational analysis.
"""
from typing import Optional, List, Dict, Any
from huggingface_hub import InferenceClient
from app.core.config import settings
import re

# Hugging Face configuration
HF_TOKEN = settings.HUGGINGFACE_TOKEN


class ContentGenerator:
    """AI-powered content generator for kids' magazine with educational AI models."""
    
    def __init__(self):
        self.client = InferenceClient(token=HF_TOKEN)
        
        # Primary chat models for content generation
        self.chat_models = [
            "meta-llama/Llama-3.2-3B-Instruct",
            "meta-llama/Llama-3.2-1B-Instruct",
            "Qwen/Qwen2.5-1.5B-Instruct",
        ]
        
        # Educational-specific models
        self.education_models = {
            # Question answering for educational content
            "qa_model": "deepset/roberta-base-squad2",  # Excellent for Q&A
            
            # Text classification for subject/topic detection
            "classifier": "facebook/bart-large-mnli",  # Zero-shot classification
            
            # Question generation from context
            "question_gen": "mrm8488/t5-base-finetuned-question-generation-ap",
            
            # Educational content difficulty assessment
            "readability": "distilbert-base-uncased",  # For readability analysis
            
            # Sentiment/confidence detection in student answers
            "sentiment": "distilbert-base-uncased-finetuned-sst-2-english",
        }
        
        print("[OK] Educational AI models loaded:")
        for name, model in self.education_models.items():
            print(f"   - {name}: {model}")
    
    
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
        
        for model in self.chat_models:
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
                    print(f"[OK] Success with model: {model}")
                    print(f"Response preview: {content[:150]}...")
                    print(f"{'='*60}\n")
                    return content.strip()
            except Exception as e:
                print(f"[FAIL] Model {model} failed: {e}")
                continue
        
        # If all models fail, return fallback content
        print("[WARN] All models failed, using fallback content")
        print(f"{'='*60}\n")
        return self._get_fallback_content(prompt)
    
    def _extract_topic_from_prompt(self, prompt: str) -> str:
        """Extract the topic from an AI prompt string."""
        prompt_lower = prompt.lower()
        # Match patterns like "story about TOPIC", "article about TOPIC", etc.
        for pattern in [r"(?:story|article|content|quiz|riddle|word.?search)\s+about\s+(.+?)(?:\.\s|\.\n|,|\n|featuring| for kids| for children)", 
                        r"about\s+(.+?)(?:\.\s|\.\n|,|\n| for kids| for children)"]:
            match = re.search(pattern, prompt_lower)
            if match:
                return match.group(1).strip()
        return ""

    def _get_fallback_content(self, prompt: str) -> str:
        """Return topic-aware fallback content when AI generation fails with randomized templates."""
        import random
        prompt_lower = prompt.lower()
        topic = self._extract_topic_from_prompt(prompt)
        topic_title = topic.title() if topic else "Amazing Things"
        
        if ("title" in prompt_lower or "just the title" in prompt_lower) and len(prompt) < 200:
            # Title generation fallback
            titles = [
                f"The Amazing Adventure of {topic_title}",
                f"Discovering {topic_title}",
                f"The Secret World of {topic_title}",
                f"{topic_title}: A Magical Journey"
            ]
            return random.choice(titles)
        
        elif "story" in prompt_lower:
            story_templates = [
                f"""Once upon a time, there was a young explorer who was very curious about {topic or 'the world'}.
Every day, they would learn something new and exciting about {topic or 'amazing things'}. They read books, asked questions, and went on adventures to discover more.
One special day, they made a wonderful discovery about {topic or 'something magical'}! They couldn't wait to share what they learned with all their friends.
"The more you learn about {topic or 'the world'}," they said, "the more amazing it becomes!"
And so the adventure continued, with new things to discover about {topic or 'the world'} every single day.""",

                f"""In a faraway land, a group of friends wanted to learn all about {topic or 'mysteries'}.
They packed their bags and set out on a grand quest to find out the secrets of {topic or 'the unknown'}. Along the way, they met wise creatures who taught them amazing facts.
"Wow! I never knew {topic or 'this'} was so fascinating," said one of the friends.
By the end of their journey, they were experts in {topic or 'their favorite subject'} and shared their knowledge with everyone in their village.
It was the best adventure ever!""",

                f"""Have you ever wondered what it would be like to travel into the world of {topic or 'magic'}?
One sunny morning, a brave child named Leo did just that! Leo discovered a magical portal that led straight to {topic or 'a wonderful place'}.
Inside, everything was related to {topic or 'amazing wonders'}. Leo spent the whole day exploring and learning.
When it was time to go home, Leo promised to never stop being curious about {topic or 'the universe'}.
What a fantastic day it was!"""
            ]
            return random.choice(story_templates)
        
        elif "article" in prompt_lower or "fact" in prompt_lower:
            article_templates = [
                f"""Did you know? There are so many amazing things to learn about {topic or 'our world'}!
Scientists and explorers have been studying {topic or 'the world around us'} for many years, and they keep making exciting new discoveries.
Here are some cool things about {topic or 'this subject'}:
- {topic_title} is a fascinating topic that people of all ages enjoy learning about.
- There are many books, videos, and websites where you can explore more about {topic or 'this topic'}.
- Every day, we learn something new about {topic or 'amazing things'}.
Fun Activity: Try to find three new facts about {topic or 'your favorite subject'}!""",

                f"""Let's dive into the fascinating world of {topic or 'science and nature'}!
For centuries, humans have been amazed by {topic or 'these incredible phenomena'}. It is one of the most interesting subjects you can explore.
Check out these facts about {topic or 'it'}:
- Learning about {topic_title} can help us understand our world better.
- Many experts dedicate their whole lives to studying {topic or 'this'}.
- You can find examples of {topic or 'this'} almost everywhere if you look closely!
Did You Know: {topic_title} has inspired many famous books and movies!""",

                f"""Welcome to today's special feature on {topic_title}!
If you love learning about {topic or 'new things'}, you are in for a treat. {topic_title} is full of surprises.
- It is one of the most popular topics for young explorers.
- There are museums and exhibits dedicated entirely to {topic or 'this subject'}.
- Exploring {topic or 'this'} can spark your imagination and creativity!
Fun Activity: Draw a picture of what you think {topic or 'this'} looks like!"""
            ]
            return random.choice(article_templates)
        
        elif "quiz" in prompt_lower or "question" in prompt_lower:
            return f"""Q: What is one interesting thing about {topic or 'learning'}?
A) It helps us understand the world
B) It makes us smarter
C) It is fun to explore
D) All of the above!
Answer: D
Explanation: Learning about {topic or 'new things'} is always an adventure because there is so much to discover!"""
        
        elif "word" in prompt_lower:
            return "LEARN\nDISCOVER\nEXPLORE\nWONDER\nCURIOUS"
        
        elif "riddle" in prompt_lower:
            return f"""Riddle: I am something you can always learn more about. The more you study me, the more interesting I become. I am related to {topic or 'knowledge'}. What am I?
Answer: {topic_title}!"""
        
        else:
            return f"Welcome to the amazing world of {topic_title}! Content is being generated, please try again in a moment."
    
    # ==================== Educational AI Methods ====================
    
    def answer_question(self, question: str, context: str) -> Dict[str, Any]:
        """
        Use question-answering model to extract answers from context.
        Useful for checking if student answers match expected content.
        """
        try:
            result = self.client.question_answering(
                question=question,
                context=context,
                model=self.education_models["qa_model"]
            )
            return {
                "answer": result.get("answer", ""),
                "score": result.get("score", 0.0),
                "start": result.get("start", 0),
                "end": result.get("end", 0)
            }
        except Exception as e:
            print(f"Question answering failed: {e}")
            return {"answer": "", "score": 0.0}
    
    def classify_subject(self, text: str, candidate_subjects: List[str] = None) -> Dict[str, float]:
        """
        Classify educational content into subjects using zero-shot classification.
        Returns probability distribution over subjects.
        """
        if candidate_subjects is None:
            candidate_subjects = [
                "Mathematics", "Science", "English", "History", 
                "Geography", "Art", "Physical Education", "Music"
            ]
        
        try:
            result = self.client.zero_shot_classification(
                text=text,
                labels=candidate_subjects,
                model=self.education_models["classifier"]
            )
            
            # Create subject: confidence mapping
            subject_scores = {}
            for label, score in zip(result.get("labels", []), result.get("scores", [])):
                subject_scores[label] = score
            
            return subject_scores
        except Exception as e:
            print(f"Subject classification failed: {e}")
            return {subj: 1.0/len(candidate_subjects) for subj in candidate_subjects}
    
    def evaluate_answer_correctness(
        self, 
        question: str, 
        student_answer: str, 
        correct_answer: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate if student answer is correct using AI,
        handles variations in phrasing, synonyms, etc.
        
        Returns: score (0-1), explanation, is_correct
        """
        # Use QA model to check if student answer appears in correct context
        full_context = f"Question: {question}\nCorrect Answer: {correct_answer}\n{context}"
        
        try:
            # Check if student answer is semantically similar to correct answer
            qa_result = self.answer_question(
                question=f"What is the answer to: {question}?",
                context=full_context
            )
            
            # Simple string similarity check
            student_clean = student_answer.lower().strip()
            correct_clean = correct_answer.lower().strip()
            
            # Exact match
            if student_clean == correct_clean:
                return {
                    "is_correct": True,
                    "confidence": 1.0,
                    "explanation": "Exact match with correct answer"
                }
            
            # Partial match (for numbers, single words)
            if student_clean in correct_clean or correct_clean in student_clean:
                return {
                    "is_correct": True,
                    "confidence": 0.9,
                    "explanation": "Partial match with correct answer"
                }
            
            # Use sentiment to gauge if answer seems confident/uncertain
            sentiment = self.analyze_sentiment(student_answer)
            
            return {
                "is_correct": False,
                "confidence": qa_result.get("score", 0.0),
                "explanation": f"Answer differs from expected. QA model suggests: {qa_result.get('answer', 'N/A')}",
                "student_confidence": sentiment.get("label", "NEUTRAL")
            }
            
        except Exception as e:
            print(f"Answer evaluation failed: {e}")
            # Fallback to simple comparison
            return {
                "is_correct": student_answer.lower().strip() == correct_answer.lower().strip(),
                "confidence": 0.5,
                "explanation": "Basic comparison used"
            }
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment/confidence in student's answer.
        Helps identify if student seems confident or uncertain.
        """
        try:
            result = self.client.text_classification(
                text=text,
                model=self.education_models["sentiment"]
            )
            
            if result and len(result) > 0:
                return {
                    "label": result[0].get("label", "NEUTRAL"),
                    "score": result[0].get("score", 0.5)
                }
            return {"label": "NEUTRAL", "score": 0.5}
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return {"label": "NEUTRAL", "score": 0.5}
    
    def assess_difficulty(self, text: str, age_group: str = "6-8") -> Dict[str, Any]:
        """
        Assess readability/difficulty level of educational content.
        Returns complexity score and recommendations.
        """
        # Simple readability metrics
        words = text.split()
        sentences = text.split('.')
        
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Age-appropriate thresholds
        thresholds = {
            "3-5": {"max_word_len": 5, "max_sent_len": 8},
            "6-8": {"max_word_len": 7, "max_sent_len": 12},
            "9-11": {"max_word_len": 9, "max_sent_len": 15},
            "12-14": {"max_word_len": 11, "max_sent_len": 20}
        }
        
        threshold = thresholds.get(age_group, thresholds["6-8"])
        
        # Calculate difficulty score (0 = easy, 1 = hard)
        word_difficulty = min(avg_word_length / threshold["max_word_len"], 1.0)
        sentence_difficulty = min(avg_sentence_length / threshold["max_sent_len"], 1.0)
        
        difficulty_score = (word_difficulty + sentence_difficulty) / 2
        
        if difficulty_score < 0.5:
            level = "Easy"
            recommendation = "Appropriate for age group"
        elif difficulty_score < 0.75:
            level = "Moderate"
            recommendation = "Challenging but suitable"
        else:
            level = "Hard"
            recommendation = "May be too difficult, consider simplifying"
        
        return {
            "difficulty_score": round(difficulty_score, 2),
            "level": level,
            "avg_word_length": round(avg_word_length, 1),
            "avg_sentence_length": round(avg_sentence_length, 1),
            "recommendation": recommendation,
            "age_appropriate": difficulty_score < 0.75
        }
    
    def generate_similar_questions(
        self, 
        question: str, 
        num_questions: int = 3
    ) -> List[str]:
        """
        Generate similar practice questions based on a given question.
        Useful for creating personalized practice sets.
        """
        prompt = f"""Generate {num_questions} similar practice questions to this one:

Original Question: {question}

Requirements:
- Same difficulty level
- Same concept/topic
- Different numbers or context
- One question per line
- No numbering, just the questions

Practice Questions:"""
        
        response = self._generate_text(prompt, max_tokens=200)
        
        # Parse questions
        questions = [line.strip() for line in response.split('\n') if line.strip() and not line.strip().startswith('#')]
        return questions[:num_questions]
    

    def generate_story(
        self,
        topic: str,
        age_group: str = "6-8",
        word_count: int = 300,
        characters: Optional[List[str]] = None,
        details: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a kid-friendly story.
        
        Args:
            topic: The main theme of the story
            age_group: Target age group (3-5, 6-8, 9-11, 12-14)
            word_count: Approximate word count
            characters: Optional list of character names
            details: Optional specific details or plot points
        """
        age_descriptions = {
            "3-5": "simple words, short sentences, happy themes, repetition",
            "6-8": "adventurous, educational, friendly characters, moral lessons",
            "9-11": "more complex plots, mystery elements, problem-solving",
            "12-14": "deeper themes, relatable characters, coming-of-age elements"
        }
        
        char_text = f" featuring characters named {', '.join(characters)}" if characters else ""
        details_text = f"\nSpecific Plot Details: {details}" if details else ""
        
        prompt = f"""Write a {word_count}-word children's story about {topic}{char_text}.
The story MUST be specifically about {topic} - include details, facts, or scenarios directly related to {topic}.{details_text}

Target age: {age_group} years old
Style: {age_descriptions.get(age_group, age_descriptions['6-8'])}

Requirements:
- The story must be centered on the topic: {topic}
- Kid-friendly and appropriate
- Educational value related to {topic}
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
    
    def analyze_test_paper_content(
        self,
        subject: str,
        question_answers: List[Dict[str, Any]],
        extracted_text: str,
        age_group: str = "6-8",
        student_name: str = "Student"
    ) -> Dict[str, Any]:
        """
        Deep analysis of test paper based on actual question-answer content.
        
        This method analyzes:
        - Student's actual answers vs correct answers
        - Common mistakes and misconceptions
        - Patterns in errors
        - Specific recommendations for each weak area
        
        Args:
            subject: The subject of the test
            question_answers: List of question-answer dictionaries from OCR
            extracted_text: Full extracted text from test paper
            age_group: Student's age group
            student_name: Student's name
        
        Returns:
            Detailed analysis with specific feedback on answers
        """
        # Calculate statistics
        total_questions = len(question_answers)
        if total_questions == 0:
            return {
                "subject": subject,
                "score": 0,
                "total": 100,
                "percentage": 0,
                "performance_level": "needs review",
                "analysis": "No questions could be extracted from the test paper. Please ensure the test paper is clear and readable.",
                "motivational_quote": "Every challenge is an opportunity to learn!",
                "weak_areas": [],
                "strong_areas": [],
                "question_feedback": []
            }
        
        correct_count = sum(1 for q in question_answers if q.get("is_correct") == True)
        incorrect_count = sum(1 for q in question_answers if q.get("is_correct") == False)
        unclear_count = sum(1 for q in question_answers if q.get("is_correct") is None and q.get("student_answer"))
        
        # Calculate score
        total_marks = sum(q.get("marks_awarded") or 0 for q in question_answers)
        max_marks = sum(q.get("max_marks") or 10 for q in question_answers)  # Default 10 marks per question
        
        if max_marks == 0:
            max_marks = total_questions * 10
        
        # If we don't have marks, estimate from correct/incorrect
        if total_marks == 0 and (correct_count > 0 or incorrect_count > 0):
            marks_per_question = max_marks / total_questions if total_questions > 0 else 10
            total_marks = int(correct_count * marks_per_question)
        
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
        
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
        
        # Build detailed question summary for AI
        question_summaries = []
        enhanced_qa_analysis = []  # Store AI-enhanced analysis
        
        for q in question_answers:
            q_num = q.get("question_number", "?")
            q_text = q.get("question_text", "")[:100]  # First 100 chars
            student_ans = q.get("student_answer", "No answer")
            correct_ans = q.get("correct_answer", "Not provided")
            is_correct = q.get("is_correct")
            
            status = "✓ Correct" if is_correct == True else ("✗ Incorrect" if is_correct == False else "? Unclear")
            
            summary = f"Q{q_num}: {q_text}\n  Student: {student_ans}\n  Correct: {correct_ans}\n  Status: {status}"
            question_summaries.append(summary)
            
            # ===== EDUCATIONAL AI ENHANCEMENT =====
            ai_insight = {
                "question_number": q_num,
                "question_text": q_text,
                "student_answer": student_ans,
                "is_correct": is_correct
            }
            
            # Use AI to evaluate answer correctness for unclear cases
            if is_correct is None and student_ans and correct_ans and correct_ans != "Not provided":
                try:
                    evaluation = self.evaluate_answer_correctness(
                        question=q_text,
                        student_answer=student_ans,
                        correct_answer=correct_ans,
                        context=extracted_text
                    )
                    ai_insight["ai_evaluation"] = evaluation
                    ai_insight["is_correct"] = evaluation.get("is_correct", False)
                    # Update the original question data
                    q["is_correct"] = evaluation.get("is_correct", False)
                except Exception as e:
                    print(f"AI evaluation failed for Q{q_num}: {e}")
            
            # Analyze student confidence from their answer
            if student_ans and student_ans != "No answer":
                try:
                    sentiment = self.analyze_sentiment(student_ans)
                    ai_insight["student_confidence"] = sentiment.get("label", "NEUTRAL")
                except Exception as e:
                    print(f"Sentiment analysis failed for Q{q_num}: {e}")
            
            # For incorrect answers, generate similar practice questions
            if is_correct == False and q_text:
                try:
                    practice_questions = self.generate_similar_questions(q_text, num_questions=2)
                    ai_insight["practice_questions"] = practice_questions
                except Exception as e:
                    print(f"Practice generation failed for Q{q_num}: {e}")
            
            enhanced_qa_analysis.append(ai_insight)
        
        # Use AI to classify subject from test content (verify/improve subject detection)
        try:
            subject_scores = self.classify_subject(extracted_text)
            detected_subject = max(subject_scores, key=subject_scores.get)
            subject_confidence = subject_scores.get(detected_subject, 0.0)
            
            # Use AI-detected subject if confidence is high enough
            if subject_confidence > 0.6:
                print(f"AI detected subject: {detected_subject} (confidence: {subject_confidence:.2f})")
        except Exception as e:
            print(f"Subject classification failed: {e}")
        
        question_details = "\n\n".join(question_summaries[:10])  # First 10 questions
        
        # Identify patterns in incorrect answers
        incorrect_questions = [q for q in question_answers if q.get("is_correct") == False]
        
        prompt = f"""Analyze this {subject} test for {student_name}, a {age_group} year old student. Provide detailed, actionable feedback based on their actual answers.

**Test Overview:**
- Total Questions: {total_questions}
- Correct Answers: {correct_count}
- Incorrect Answers: {incorrect_count}
- Score: {total_marks}/{max_marks} ({percentage:.1f}%)
- Performance Level: {performance_level}

**Question-by-Question Analysis:**
{question_details}

Based on the student's actual answers, provide a comprehensive analysis in this format:

**Performance Summary:**
[Warm, encouraging overview of their performance. Acknowledge what they did well.]

**What You Did Great:**
[List 2-3 specific strengths based on their correct answers or good attempts]

**Areas to Focus On:**
[Identify 2-3 specific concepts or types of questions where they struggled. Be specific about what went wrong in their answers.]

**Understanding Your Mistakes:**
[Explain common misconceptions or errors you noticed in their incorrect answers. Help them understand WHY they got things wrong.]

**Personalized Learning Plan:**
1. [Specific topic/skill to practice based on their mistakes]
2. [Concrete exercise or activity to improve that area]
3. [Study strategy tailored to their learning needs]

**Next Steps:**
[Clear, actionable plan for what to study next]

**Encouragement:**
[Positive, motivating message that acknowledges their effort and builds confidence]

Keep the tone warm, supportive, and focused on growth. Be specific about their actual answers, not generic."""

        analysis = self._generate_text(prompt, max_tokens=800)
        
        # Generate motivational quote
        quote_prompt = f"Generate a short, inspiring quote about learning from mistakes for a {age_group} year old. Just the quote:"
        motivational_quote = self._generate_text(quote_prompt, max_tokens=50)
        
        # Identify weak and strong areas
        weak_areas = []
        strong_areas = []
        
        # Analyze patterns in incorrect answers
        if incorrect_count > 0:
            weak_prompt = f"Based on these incorrect answers from a {subject} test, list 2-3 specific topics/concepts the student needs to review. Just the topics, one per line:\n"
            for q in incorrect_questions[:5]:
                weak_prompt += f"- Q{q.get('question_number')}: {q.get('question_text', '')[:60]}\n"
            
            weak_response = self._generate_text(weak_prompt, max_tokens=100)
            weak_areas = [line.strip('- ').strip() for line in weak_response.split('\n') if line.strip()][:3]
        
        # Identify strong areas from correct answers
        correct_questions = [q for q in question_answers if q.get("is_correct") == True]
        if correct_count > 0:
            strong_prompt = f"Based on these correct answers from a {subject} test, list 2-3 specific strengths/concepts the student has mastered. Just the topics, one per line:\n"
            for q in correct_questions[:5]:
                strong_prompt += f"- Q{q.get('question_number')}: {q.get('question_text', '')[:60]}\n"
            
            strong_response = self._generate_text(strong_prompt, max_tokens=100)
            strong_areas = [line.strip('- ').strip() for line in strong_response.split('\n') if line.strip()][:3]
        
        return {
            "subject": subject,
            "score": total_marks,
            "total": max_marks,
            "percentage": round(percentage, 1),
            "performance_level": performance_level,
            "analysis": analysis,
            "motivational_quote": motivational_quote.strip('"'),
            "weak_areas": weak_areas if weak_areas else ["Review test content"],
            "strong_areas": strong_areas if strong_areas else ["Attempted questions"],
            "question_feedback": question_answers,  # Include full Q&A details
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "total_questions": total_questions,
            "ai_enhanced_analysis": enhanced_qa_analysis,  # NEW: AI-powered insights
            "uses_educational_ai": True  # Flag to indicate enhanced analysis
        }
    
    # ==================== GRADE-SPECIFIC ACTIVITY TEMPLATES ====================
    
    GRADE_ACTIVITIES = {
        1: {
            "label": "Grade 1",
            "age": "6-7",
            "activity_types": {
                "Mathematics": [
                    {"title": "Counting with Objects", "description": "Use buttons, beads, or toys to count and practice addition. Line up 5 toys, then add 3 more - how many now?", "type": "hands_on", "duration": "10 min"},
                    {"title": "Number Tracing Worksheet", "description": "Trace numbers 1-20 and draw that many stars next to each number.", "type": "writing", "duration": "15 min"},
                    {"title": "Skip Counting Song", "description": "Sing along while counting by 2s and 5s. Clap your hands on each number!", "type": "fun", "duration": "5 min"},
                ],
                "Science": [
                    {"title": "Nature Walk & Draw", "description": "Go for a short walk and draw 3 living things and 3 non-living things you see.", "type": "hands_on", "duration": "20 min"},
                    {"title": "Sort It Out", "description": "Collect 10 items from around the house and sort them: big/small, hard/soft, heavy/light.", "type": "hands_on", "duration": "10 min"},
                ],
                "English": [
                    {"title": "Letter Sound Hunt", "description": "Pick a letter and find 5 things in your room that start with that sound.", "type": "fun", "duration": "10 min"},
                    {"title": "Story Time Drawing", "description": "Listen to a short story, then draw your favorite part and write one sentence about it.", "type": "creative", "duration": "15 min"},
                ],
                "default": [
                    {"title": "Color and Learn", "description": "Color a picture related to today's topic. Tell someone what you learned!", "type": "creative", "duration": "10 min"},
                    {"title": "Show and Tell", "description": "Find something at home related to what you studied. Show it to your family and explain it.", "type": "fun", "duration": "5 min"},
                ]
            }
        },
        2: {
            "label": "Grade 2",
            "age": "7-8",
            "activity_types": {
                "Mathematics": [
                    {"title": "Math Story Problems", "description": "Create your own word problem using your favorite toys. Write it down and solve it!", "type": "creative", "duration": "15 min"},
                    {"title": "Place Value Craft", "description": "Use straws or sticks - bundle 10 together for tens, single ones for units. Build different numbers!", "type": "hands_on", "duration": "15 min"},
                    {"title": "Mental Math Race", "description": "Ask a family member to give you 10 quick addition problems. Time yourself and try to beat your record!", "type": "practice", "duration": "10 min"},
                ],
                "Science": [
                    {"title": "Mini Experiment", "description": "Plant a seed in a cup. Water it daily and draw what you see each day for a week.", "type": "hands_on", "duration": "10 min/day"},
                    {"title": "Body Parts Poster", "description": "Draw yourself and label 10 body parts. Add arrows showing what each part does.", "type": "creative", "duration": "20 min"},
                ],
                "English": [
                    {"title": "Sentence Builder", "description": "Write 5 sentences using this week's spelling words. Draw a picture for each!", "type": "writing", "duration": "15 min"},
                    {"title": "Read Aloud", "description": "Read a short story aloud to a family member. Practice reading smoothly and with expression.", "type": "practice", "duration": "10 min"},
                ],
                "default": [
                    {"title": "Teach Your Teddy", "description": "Pretend your stuffed toy is a student. Teach it what you learned today!", "type": "fun", "duration": "10 min"},
                    {"title": "Quiz Cards", "description": "Make 5 question cards about what you studied. Test a family member!", "type": "creative", "duration": "15 min"},
                ]
            }
        },
        3: {
            "label": "Grade 3",
            "age": "8-9",
            "activity_types": {
                "Mathematics": [
                    {"title": "Multiplication Flashcards", "description": "Make flashcards for the times tables you're learning. Practice 10 minutes daily!", "type": "practice", "duration": "10 min"},
                    {"title": "Fraction Pizza", "description": "Draw 4 circles (pizzas). Divide them into halves, thirds, fourths, and sixths. Color different fractions!", "type": "hands_on", "duration": "15 min"},
                    {"title": "Math in the Kitchen", "description": "Help with cooking and practice measuring - cups, spoons, halves and quarters.", "type": "real_world", "duration": "20 min"},
                ],
                "Science": [
                    {"title": "States of Matter Hunt", "description": "Find 3 solids, 3 liquids, and 1 gas in your house. Make a chart with drawings.", "type": "hands_on", "duration": "15 min"},
                ],
                "English": [
                    {"title": "Paragraph Writing", "description": "Write a paragraph about your favorite animal. Include a topic sentence, 3 details, and a closing sentence.", "type": "writing", "duration": "15 min"},
                    {"title": "Grammar Detective", "description": "Read a page from your favorite book. Find 5 nouns, 5 verbs, and 3 adjectives.", "type": "practice", "duration": "10 min"},
                ],
                "default": [
                    {"title": "Mind Map", "description": "Draw a mind map of the topic in the center, with branches for key facts you remember.", "type": "creative", "duration": "15 min"},
                    {"title": "Practice Problems", "description": "Solve 10 problems related to the weak areas identified in your test.", "type": "practice", "duration": "20 min"},
                ]
            }
        },
        4: {
            "label": "Grade 4",
            "age": "9-10",
            "activity_types": {
                "Mathematics": [
                    {"title": "Long Division Practice", "description": "Solve 8 division problems. Check each answer by multiplying back!", "type": "practice", "duration": "20 min"},
                    {"title": "Geometry Scavenger Hunt", "description": "Walk around your home and find examples of parallel lines, right angles, and symmetry. Photograph or draw them.", "type": "real_world", "duration": "15 min"},
                ],
                "Science": [
                    {"title": "Food Chain Poster", "description": "Create a food chain poster for a habitat (forest, ocean, or desert). Show producers, consumers, and decomposers.", "type": "creative", "duration": "25 min"},
                ],
                "English": [
                    {"title": "Story Continuation", "description": "Take a story you know and write what happens next. Use at least 3 paragraphs with dialogue.", "type": "writing", "duration": "20 min"},
                ],
                "default": [
                    {"title": "Summary Notes", "description": "Write a 1-page summary of the topic in your own words. Highlight key vocabulary.", "type": "writing", "duration": "20 min"},
                    {"title": "Teach Someone", "description": "Explain the topic to a family member or friend. Teaching helps you learn better!", "type": "practice", "duration": "10 min"},
                ]
            }
        },
        5: {
            "label": "Grade 5",
            "age": "10-11",
            "activity_types": {
                "Mathematics": [
                    {"title": "Decimal Practice Set", "description": "Complete 10 problems with decimals - adding, subtracting, and comparing. Show your working!", "type": "practice", "duration": "20 min"},
                    {"title": "Real-World Math", "description": "Look at a grocery flyer or menu. Calculate totals, discounts, and change for different scenarios.", "type": "real_world", "duration": "15 min"},
                ],
                "Science": [
                    {"title": "Experiment Journal", "description": "Design a simple experiment to test a question you have. Write: hypothesis, materials, steps, and what you observed.", "type": "hands_on", "duration": "30 min"},
                ],
                "English": [
                    {"title": "Essay Outline", "description": "Create an outline for a 5-paragraph essay on a topic you choose. Include introduction, 3 body paragraph ideas, and conclusion.", "type": "writing", "duration": "15 min"},
                ],
                "default": [
                    {"title": "Concept Map", "description": "Create a concept map connecting the key ideas from this topic. Show how they relate to each other.", "type": "creative", "duration": "15 min"},
                    {"title": "Self-Quiz", "description": "Write 10 questions about the topic and answer them without looking at notes. Check your answers after.", "type": "practice", "duration": "20 min"},
                ]
            }
        },
        6: {
            "label": "Grade 6",
            "age": "11-12",
            "activity_types": {
                "Mathematics": [
                    {"title": "Ratio & Proportion Problems", "description": "Solve 10 real-life ratio problems. Example: If 3 apples cost Rs 30, how much do 7 cost?", "type": "practice", "duration": "25 min"},
                    {"title": "Algebra Introduction", "description": "Practice solving for x in 8 simple equations. Write out each step clearly.", "type": "practice", "duration": "20 min"},
                ],
                "Science": [
                    {"title": "Classification Chart", "description": "Create a classification chart for the topic (e.g., types of forces, parts of a cell). Add diagrams.", "type": "creative", "duration": "20 min"},
                ],
                "English": [
                    {"title": "Comprehension Practice", "description": "Read a passage and answer 5 questions: who, what, when, where, why. Support answers with evidence from the text.", "type": "practice", "duration": "20 min"},
                ],
                "default": [
                    {"title": "Study Notes", "description": "Create neat, organized study notes for this topic. Use headings, bullet points, and diagrams.", "type": "writing", "duration": "25 min"},
                    {"title": "Practice Test", "description": "Create a mini practice test (8 questions) and solve it under timed conditions.", "type": "practice", "duration": "25 min"},
                ]
            }
        },
        7: {
            "label": "Grade 7",
            "age": "12-13",
            "activity_types": {
                "Mathematics": [
                    {"title": "Equation Solving Set", "description": "Solve 12 equations of increasing difficulty. Include linear equations and those with brackets.", "type": "practice", "duration": "30 min"},
                    {"title": "Geometry Constructions", "description": "Practice compass-and-ruler constructions: angle bisectors, perpendicular bisectors, and triangle construction.", "type": "practice", "duration": "25 min"},
                ],
                "Science": [
                    {"title": "Diagram & Label", "description": "Draw and label a detailed diagram of the topic (e.g., human digestive system, electric circuit). Add brief explanations.", "type": "creative", "duration": "25 min"},
                ],
                "English": [
                    {"title": "Analytical Writing", "description": "Write a 3-paragraph analysis of a poem or short story. Discuss theme, language, and your interpretation.", "type": "writing", "duration": "25 min"},
                ],
                "default": [
                    {"title": "Revision Flashcards", "description": "Create 15 flashcards with key terms on one side and definitions/explanations on the other.", "type": "practice", "duration": "20 min"},
                    {"title": "Error Analysis", "description": "Review your test mistakes. For each wrong answer, write: what you wrote, the correct answer, and WHY you made the error.", "type": "practice", "duration": "20 min"},
                ]
            }
        },
        8: {
            "label": "Grade 8",
            "age": "13-14",
            "activity_types": {
                "Mathematics": [
                    {"title": "Mixed Problem Set", "description": "Solve 15 problems covering the weak areas. Include algebraic expressions, geometry proofs, and data handling.", "type": "practice", "duration": "35 min"},
                    {"title": "Application Problems", "description": "Solve 5 real-world application problems that use the concepts from this chapter.", "type": "real_world", "duration": "25 min"},
                ],
                "Science": [
                    {"title": "Concept Summary", "description": "Write a 1-page summary explaining the key scientific concept in your own words. Include a diagram and real-world example.", "type": "writing", "duration": "25 min"},
                ],
                "English": [
                    {"title": "Critical Response", "description": "Write a critical response (300+ words) to a text you've studied. Include thesis, evidence, and personal reflection.", "type": "writing", "duration": "30 min"},
                ],
                "default": [
                    {"title": "Mock Test", "description": "Create a 30-minute mock test for yourself covering the weak areas. Solve it, mark it, and review mistakes.", "type": "practice", "duration": "40 min"},
                    {"title": "Peer Study", "description": "Study with a friend or sibling. Quiz each other on the difficult topics and explain concepts to each other.", "type": "collaborative", "duration": "30 min"},
                ]
            }
        }
    }
    
    def generate_structured_exam_report(
        self,
        subject: str,
        grade: int,
        question_answers: List[Dict[str, Any]],
        extracted_text: str,
        teacher_corrections: Optional[Dict[str, Any]] = None,
        rubric_comparison: Optional[List[Dict[str, Any]]] = None,
        student_name: str = "Student"
    ) -> Dict[str, Any]:
        """
        Generate a structured exam evaluation report with three clear sections:
        A. Strong Zones - topics where the student performs well
        B. Weak Zones - topics with mistakes or misunderstandings
        C. Focus Plan - personalized, grade-appropriate study activities
        
        Args:
            subject: Subject of the test
            grade: Student's grade level (1-8)
            question_answers: Parsed question-answer data
            extracted_text: Full OCR text
            teacher_corrections: Optional teacher correction data
            rubric_comparison: Optional rubric comparison results
            student_name: Student's name
            
        Returns:
            Structured report dict with strong_zones, weak_zones, focus_plan
        """
        grade = max(1, min(8, grade))  # Clamp to 1-8
        age_group = self.GRADE_ACTIVITIES.get(grade, {}).get("age", "6-8")
        
        total_questions = len(question_answers)
        correct_questions = [q for q in question_answers if q.get("is_correct") == True]
        incorrect_questions = [q for q in question_answers if q.get("is_correct") == False]
        correct_count = len(correct_questions)
        incorrect_count = len(incorrect_questions)
        
        # Calculate score
        total_marks = sum(q.get("marks_awarded") or 0 for q in question_answers)
        max_marks = sum(q.get("max_marks") or 10 for q in question_answers)
        if max_marks == 0:
            max_marks = total_questions * 10
        if total_marks == 0 and (correct_count > 0 or incorrect_count > 0):
            marks_per_q = max_marks / total_questions if total_questions > 0 else 10
            total_marks = int(correct_count * marks_per_q)
        
        percentage = (total_marks / max_marks * 100) if max_marks > 0 else 0
        
        # ===== A. STRONG ZONES =====
        strong_zones = self._identify_strong_zones(
            subject, grade, correct_questions, extracted_text, student_name
        )
        
        # ===== B. WEAK ZONES =====
        weak_zones = self._identify_weak_zones(
            subject, grade, incorrect_questions, extracted_text, student_name
        )
        
        # ===== C. FOCUS PLAN =====
        focus_plan = self._generate_focus_plan(
            subject, grade, weak_zones, strong_zones, percentage, student_name
        )
        
        # Performance level
        if percentage >= 90:
            performance_level = "Excellent"
        elif percentage >= 75:
            performance_level = "Very Good"
        elif percentage >= 60:
            performance_level = "Good"
        elif percentage >= 45:
            performance_level = "Satisfactory"
        else:
            performance_level = "Needs Improvement"
        
        # Teacher insights
        teacher_insights = None
        if teacher_corrections and teacher_corrections.get("has_corrections"):
            teacher_insights = {
                "comments": teacher_corrections.get("comments", []),
                "marks_detected": len(teacher_corrections.get("marks_per_question", {})),
                "ticks_detected": sum(1 for m in teacher_corrections.get("tick_cross_marks", []) if m["type"] == "correct"),
                "crosses_detected": sum(1 for m in teacher_corrections.get("tick_cross_marks", []) if m["type"] == "incorrect"),
            }
        
        return {
            "report_type": "structured_exam_evaluation",
            "student_name": student_name,
            "subject": subject,
            "grade": grade,
            "score": total_marks,
            "total": max_marks,
            "percentage": round(percentage, 1),
            "performance_level": performance_level,
            "total_questions": total_questions,
            "correct_count": correct_count,
            "incorrect_count": incorrect_count,
            "strong_zones": strong_zones,
            "weak_zones": weak_zones,
            "focus_plan": focus_plan,
            "teacher_insights": teacher_insights,
            "encouragement": self._get_encouragement(percentage, student_name, grade)
        }
    
    def _identify_strong_zones(
        self, subject: str, grade: int, correct_questions: List[Dict], 
        extracted_text: str, student_name: str
    ) -> List[Dict[str, str]]:
        """Identify topics where the student consistently performs well."""
        if not correct_questions:
            return [{
                "topic": "Attempting Questions",
                "evidence": "Keep trying! Every question you attempt is a step forward.",
                "message": f"Great job for taking the test, {student_name}! That takes courage."
            }]
        
        # Build question summary for AI
        q_summary = "\n".join(
            f"Q{q.get('question_number', '?')}: {q.get('question_text', '')[:80]}"
            for q in correct_questions[:8]
        )
        
        prompt = f"""Analyze these CORRECT answers from a Grade {grade} {subject} test for {student_name}.

Correct answers:
{q_summary}

Identify 2-3 specific topic areas (Strong Zones) where the student performed well.
For each zone, provide:
1. Topic name (specific, not vague)
2. Brief evidence (which questions show this strength)
3. An encouraging message for the student (warm, age-appropriate for Grade {grade})

Format each zone on its own line as:
TOPIC: [topic name] | EVIDENCE: [evidence] | MESSAGE: [encouraging message]"""
        
        response = self._generate_text(prompt, max_tokens=300)
        
        zones = []
        for line in response.split('\n'):
            line = line.strip()
            if not line or 'TOPIC:' not in line:
                continue
            
            parts = {}
            for segment in line.split('|'):
                segment = segment.strip()
                if segment.startswith('TOPIC:'):
                    parts['topic'] = segment.replace('TOPIC:', '').strip()
                elif segment.startswith('EVIDENCE:'):
                    parts['evidence'] = segment.replace('EVIDENCE:', '').strip()
                elif segment.startswith('MESSAGE:'):
                    parts['message'] = segment.replace('MESSAGE:', '').strip()
            
            if parts.get('topic'):
                zones.append({
                    "topic": parts.get('topic', 'General Knowledge'),
                    "evidence": parts.get('evidence', f'Answered correctly in the {subject} test'),
                    "message": parts.get('message', f'Great work, {student_name}!')
                })
        
        # Fallback if AI didn't produce parseable results
        if not zones:
            zones = [{
                "topic": f"{subject} Fundamentals",
                "evidence": f"Got {len(correct_questions)} out of {len(correct_questions) + len([q for q in correct_questions])} questions right",
                "message": f"Well done, {student_name}! You have a solid understanding of the basics."
            }]
        
        return zones[:3]
    
    def _identify_weak_zones(
        self, subject: str, grade: int, incorrect_questions: List[Dict],
        extracted_text: str, student_name: str
    ) -> List[Dict[str, str]]:
        """Identify topics with frequent mistakes or misunderstandings."""
        if not incorrect_questions:
            return []  # No weak zones is great!
        
        q_summary = "\n".join(
            f"Q{q.get('question_number', '?')}: {q.get('question_text', '')[:80]} "
            f"(Student wrote: {q.get('student_answer', 'no answer')[:50]})"
            for q in incorrect_questions[:8]
        )
        
        prompt = f"""Analyze these INCORRECT answers from a Grade {grade} {subject} test for {student_name}.

Incorrect answers:
{q_summary}

Identify 2-3 specific Weak Zones (topics where the student struggled).
For each zone, provide:
1. Topic name (specific concept, not vague)
2. What went wrong (common mistake or misconception observed)
3. An encouraging message (positive, growth-mindset, age-appropriate for Grade {grade})

Format each zone on its own line as:
TOPIC: [topic name] | ISSUE: [what went wrong] | MESSAGE: [encouraging message]"""
        
        response = self._generate_text(prompt, max_tokens=300)
        
        zones = []
        for line in response.split('\n'):
            line = line.strip()
            if not line or 'TOPIC:' not in line:
                continue
            
            parts = {}
            for segment in line.split('|'):
                segment = segment.strip()
                if segment.startswith('TOPIC:'):
                    parts['topic'] = segment.replace('TOPIC:', '').strip()
                elif segment.startswith('ISSUE:'):
                    parts['issue'] = segment.replace('ISSUE:', '').strip()
                elif segment.startswith('MESSAGE:'):
                    parts['message'] = segment.replace('MESSAGE:', '').strip()
            
            if parts.get('topic'):
                zones.append({
                    "topic": parts.get('topic', 'Review Needed'),
                    "issue": parts.get('issue', 'Some answers need correction'),
                    "message": parts.get('message', f"Don't worry, {student_name}! This is how we learn and grow.")
                })
        
        if not zones:
            zones = [{
                "topic": f"{subject} Practice Needed",
                "issue": f"Made errors on {len(incorrect_questions)} questions",
                "message": f"Every mistake is a chance to learn something new, {student_name}!"
            }]
        
        return zones[:3]
    
    def _generate_focus_plan(
        self, subject: str, grade: int, weak_zones: List[Dict],
        strong_zones: List[Dict], percentage: float, student_name: str
    ) -> Dict[str, Any]:
        """Generate a personalized, grade-appropriate Focus Plan."""
        grade_data = self.GRADE_ACTIVITIES.get(grade, self.GRADE_ACTIVITIES.get(3, {}))
        activity_pool = grade_data.get("activity_types", {})
        
        # Get subject-specific activities, falling back to default
        subject_activities = activity_pool.get(subject, activity_pool.get("default", []))
        default_activities = activity_pool.get("default", [])
        
        # Pick activities based on performance
        selected_activities = []
        
        # Always include subject-specific activities
        for act in subject_activities[:2]:
            selected_activities.append(act)
        
        # Add default activities if we need more
        for act in default_activities:
            if len(selected_activities) >= 3:
                break
            if act not in selected_activities:
                selected_activities.append(act)
        
        # Generate AI-powered specific recommendations based on weak zones
        weak_topics = [z.get("topic", "") for z in weak_zones]
        specific_tips = []
        
        if weak_topics:
            tips_prompt = f"""For a Grade {grade} student named {student_name} who needs to improve in {subject}, specifically in: {', '.join(weak_topics)}.

Give 3 simple, specific study tips. Each tip should be:
- One sentence
- Actionable (something they can do TODAY)
- Encouraging and age-appropriate for Grade {grade}

Format: one tip per line, starting with a number."""
            
            tips_response = self._generate_text(tips_prompt, max_tokens=200)
            for line in tips_response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    tip = line.lstrip('0123456789.-) ').strip()
                    if tip and len(tip) > 10:
                        specific_tips.append(tip)
        
        if not specific_tips:
            specific_tips = [
                f"Practice {subject} for 15-20 minutes every day.",
                "Review your test mistakes and understand why each answer was wrong.",
                "Ask your teacher or a parent if you're stuck on a concept."
            ]
        
        # Summary message based on performance
        if percentage >= 80:
            summary = f"Amazing work, {student_name}! You're doing great in {subject}. Here are some ways to become even better!"
        elif percentage >= 60:
            summary = f"Good effort, {student_name}! You understand a lot already. Let's work on making those tricky parts easier!"
        elif percentage >= 40:
            summary = f"You're learning, {student_name}! With some focused practice, you'll see big improvements. Let's make a plan!"
        else:
            summary = f"Every expert was once a beginner, {student_name}! Let's start with the basics and build up step by step. You can do this!"
        
        return {
            "summary": summary,
            "activities": selected_activities,
            "specific_tips": specific_tips[:3],
            "daily_goal": f"Spend 15-20 minutes practicing {subject} every day",
            "weekly_goal": f"Complete all {len(selected_activities)} activities this week",
            "encouragement": f"Remember, {student_name} - making mistakes means you're learning! Keep going!"
        }
    
    def _get_encouragement(self, percentage: float, student_name: str, grade: int) -> str:
        """Get a warm, grade-appropriate encouragement message."""
        if grade <= 3:
            # Younger kids - very warm, simple language
            if percentage >= 80:
                return f"WOW, {student_name}! You are a superstar! Your hard work is really showing!"
            elif percentage >= 60:
                return f"Great job, {student_name}! You're learning so much. Keep being awesome!"
            elif percentage >= 40:
                return f"You're doing good, {student_name}! Every time you try, you get a little bit better!"
            else:
                return f"You're so brave for trying, {student_name}! Let's practice together and you'll get better really fast!"
        else:
            # Older kids - encouraging but more mature
            if percentage >= 80:
                return f"Excellent performance, {student_name}! Your dedication to studying is clearly paying off."
            elif percentage >= 60:
                return f"Good work, {student_name}! You have a solid foundation. With focused practice, you'll master the rest."
            elif percentage >= 40:
                return f"Keep going, {student_name}! The areas you found difficult are exactly where the biggest learning happens."
            else:
                return f"Don't be discouraged, {student_name}. Every expert was once a beginner. Focus on one topic at a time and you'll improve steadily."
    
    def generate_sudoku_puzzle(
        self,
        difficulty: str = "easy",
        age_group: str = "9-11"
    ) -> Dict[str, Any]:
        """
        Generate a Sudoku puzzle using AI.
        
        Args:
            difficulty: easy, medium, or hard
            age_group: Target age group
        
        Returns:
            Dict with puzzle grid, solution, and hints
        """
        import random
        
        # Define grid sizes based on age group
        grid_sizes = {
            "6-8": 4,   # 4x4 Sudoku for younger kids
            "9-11": 6,  # 6x6 Sudoku
            "12-14": 9  # Classic 9x9 Sudoku
        }
        
        grid_size = grid_sizes.get(age_group, 6)
        
        # Generate a simple valid Sudoku grid using backtracking
        def generate_solved_grid(size):
            grid = [[0 for _ in range(size)] for _ in range(size)]
            
            def is_valid(grid, row, col, num):
                # Check row
                if num in grid[row]:
                    return False
                
                # Check column
                if num in [grid[i][col] for i in range(size)]:
                    return False
                
                # Check box
                box_size = int(size ** 0.5)
                box_row, box_col = row // box_size * box_size, col // box_size * box_size
                for i in range(box_row, box_row + box_size):
                    for j in range(box_col, box_col + box_size):
                        if grid[i][j] == num:
                            return False
                
                return True
            
            def solve(grid):
                for row in range(size):
                    for col in range(size):
                        if grid[row][col] == 0:
                            numbers = list(range(1, size + 1))
                            random.shuffle(numbers)
                            for num in numbers:
                                if is_valid(grid, row, col, num):
                                    grid[row][col] = num
                                    if solve(grid):
                                        return True
                                    grid[row][col] = 0
                            return False
                return True
            
            solve(grid)
            return grid
        
        # Generate solution
        solution = generate_solved_grid(grid_size)
        
        # Create puzzle by removing numbers
        puzzle = [row[:] for row in solution]  # Deep copy
        
        # Remove numbers based on difficulty
        cells_to_remove = {
            "easy": int(grid_size * grid_size * 0.3),
            "medium": int(grid_size * grid_size * 0.5),
            "hard": int(grid_size * grid_size * 0.7)
        }.get(difficulty, int(grid_size * grid_size * 0.4))
        
        positions = [(i, j) for i in range(grid_size) for j in range(grid_size)]
        random.shuffle(positions)
        
        for i, (row, col) in enumerate(positions):
            if i >= cells_to_remove:
                break
            puzzle[row][col] = 0
        
        return {
            "grid_size": grid_size,
            "puzzle": puzzle,
            "solution": solution,
            "difficulty": difficulty,
            "age_group": age_group,
            "instructions": f"Fill in the {grid_size}x{grid_size} grid so that each row, column, and box contains all numbers from 1 to {grid_size}!"
        }
    
    def generate_complete_word_search(
        self,
        topic: str,
        grid_size: int = 12,
        num_words: int = 10,
        age_group: str = "6-8"
    ) -> Dict[str, Any]:
        """
        Generate a complete word search puzzle with grid.
        
        Args:
            topic: Theme for the words
            grid_size: Size of the grid (NxN)
            num_words: Number of words to hide
            age_group: Target age group
        
        Returns:
            Complete puzzle with grid, words, and solutions
        """
        import random
        
        # Get words from AI
        words = self.generate_word_search_words(topic, num_words, age_group)
        
        # Create empty grid
        grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
        placed_words = []
        
        # Directions: right, down, diagonal-right-down
        directions = [(0, 1), (1, 0), (1, 1)]
        
        # Place each word
        for word in words:
            placed = False
            attempts = 0
            max_attempts = 50
            
            while not placed and attempts < max_attempts:
                attempts += 1
                
                # Random starting position
                row = random.randint(0, grid_size - 1)
                col = random.randint(0, grid_size - 1)
                direction = random.choice(directions)
                
                # Check if word fits
                end_row = row + direction[0] * len(word)
                end_col = col + direction[1] * len(word)
                
                if end_row > grid_size or end_col > grid_size:
                    continue
                
                # Check if cells are empty
                cells_available = True
                for i, char in enumerate(word):
                    check_row = row + direction[0] * i
                    check_col = col + direction[1] * i
                    if grid[check_row][check_col] not in (' ', char):
                        cells_available = False
                        break
                
                if cells_available:
                    # Place the word
                    for i, char in enumerate(word):
                        check_row = row + direction[0] * i
                        check_col = col + direction[1] * i
                        grid[check_row][check_col] = char
                    
                    placed_words.append({
                        "word": word,
                        "start": [row, col],
                        "end": [row + direction[0] * (len(word) - 1), 
                               col + direction[1] * (len(word) - 1)],
                        "direction": direction
                    })
                    placed = True
        
        # Fill empty cells with random letters
        for i in range(grid_size):
            for j in range(grid_size):
                if grid[i][j] == ' ':
                    grid[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        
        return {
            "topic": topic,
            "grid": grid,
            "words": [w["word"] for w in placed_words],
            "word_locations": placed_words,
            "grid_size": grid_size,
            "age_group": age_group,
            "instructions": f"Find all {len(placed_words)} words related to {topic}!"
        }
    
    def generate_complete_puzzle(
        self,
        puzzle_type: str,
        topic: str,
        difficulty: str = "easy",
        age_group: str = "6-8"
    ) -> Dict[str, Any]:
        """
        Master method to generate any type of complete puzzle.
        
        Args:
            puzzle_type: word_search, crossword, sudoku, or jigsaw
            topic: Theme for the puzzle
            difficulty: easy, medium, or hard
            age_group: Target age group
        
        Returns:
            Complete puzzle data ready to be saved or displayed
        """
        if puzzle_type == "word_search":
            grid_sizes = {"3-5": 8, "6-8": 10, "9-11": 12, "12-14": 15}
            grid_size = grid_sizes.get(age_group, 10)
            num_words = {"easy": 6, "medium": 10, "hard": 15}.get(difficulty, 10)
            
            puzzle_data = self.generate_complete_word_search(
                topic=topic,
                grid_size=grid_size,
                num_words=num_words,
                age_group=age_group
            )
            
            title = f"{topic.title()} Word Search"
            return {
                "title": title,
                "description": f"Find words related to {topic}!",
                "puzzle_type": "word_search",
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": puzzle_data,
                "solution_data": {
                    "word_locations": puzzle_data["word_locations"]
                }
            }
        
        elif puzzle_type == "crossword":
            num_clues = {"easy": 5, "medium": 8, "hard": 12}.get(difficulty, 8)
            clues = self.generate_crossword_clues(topic, num_clues, age_group)
            
            title = f"{topic.title()} Crossword"
            return {
                "title": title,
                "description": f"Solve this crossword puzzle about {topic}!",
                "puzzle_type": "crossword",
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": {
                    "clues": clues,
                    "topic": topic
                },
                "solution_data": {
                    "answers": [(c["clue"], c["answer"]) for c in clues if "answer" in c]
                }
            }
        
        elif puzzle_type == "sudoku":
            puzzle_data = self.generate_sudoku_puzzle(difficulty, age_group)
            
            return {
                "title": f"Sudoku {difficulty.title()}",
                "description": "Fill in the numbers to complete the puzzle!",
                "puzzle_type": "sudoku",
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": puzzle_data,
                "solution_data": {
                    "solution": puzzle_data["solution"]
                }
            }
        
        else:  # fallback
            return {
                "title": f"{topic.title()} Puzzle",
                "description": f"A {difficulty} {puzzle_type} puzzle about {topic} for ages {age_group}.",
                "puzzle_type": puzzle_type,
                "difficulty": difficulty,
                "age_group": age_group,
                "puzzle_data": {},
                "solution_data": {}
            }
    def summarize_study_material(self, text: str, age_group: str = "9-11") -> Dict[str, Any]:
        """
        Summarize study material and create a study plan.
        
        Args:
            text: Extracted text from PDF
            age_group: Student's age group
        
        Returns:
            Dict with summary, key topics, study plan
        """
        prompt = f"""Analyze this study material for a student aged {age_group} years:

{text[:3000]}

Provide:
1. **Summary**: A clear, kid-friendly summary (3-4 paragraphs)
2. **Key Topics**: List 5-7 main topics covered
3. **Important Terms**: List 8-10 key vocabulary words with simple definitions
4. **Study Plan**: A 5-day study schedule to master this material
5. **Learning Objectives**: What the student should know after studying

Format your response clearly with headers."""

        response = self._generate_text(prompt, max_tokens=800)
        
        # Parse key topics from response
        topics = []
        lines = response.split('\n')
        for line in lines:
            line_clean = line.strip()
            if line_clean.startswith(('-', '•', '*')) and len(line_clean) > 3:
                topic = line_clean.lstrip('-•* ').strip()
                if topic and len(topic) < 100:
                    topics.append(topic)
        
        # Heuristic fallback if no topics were parsed
        if not topics or len(response) < 100:
            # Look for capitalized words or long words in the source text
            words = re.findall(r'\b[A-Z][a-z]{4,}\b', text[:1000])
            topics = list(set(words))[:5]
            if not topics:
                topics = ["General Knowledge", "Study Skills", "Critical Thinking"]

        return {
            "summary": response,
            "key_topics": topics[:7],
            "age_group": age_group,
            "original_length": len(text),
            "summarized": True
        }
    
    def generate_practice_questions(
        self, 
        text: str, 
        num_mcq: int = 5, 
        num_short: int = 3,
        age_group: str = "9-11"
    ) -> Dict[str, Any]:
        """
        Generate practice questions from study material.
        
        Args:
            text: Study material text
            num_mcq: Number of MCQ questions
            num_short: Number of short answer questions
            age_group: Student's age group
        
        Returns:
            Dict with MCQs and short answer questions
        """
        # Generate MCQs
        mcq_prompt = f"""Based on this study material, create {num_mcq} multiple choice questions for students aged {age_group}:

{text[:2500]}

Format each question as:
Q1: [Question]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [Letter]

Make questions clear and educational."""

        mcq_response = self._generate_text(mcq_prompt, max_tokens=600)
        
        # Parse MCQs
        mcqs = []
        current_q = {}
        for line in mcq_response.split('\n'):
            line = line.strip()
            if line.startswith(('Q', 'q')) and ':' in line:
                if current_q:
                    mcqs.append(current_q)
                current_q = {"question": line.split(':', 1)[1].strip(), "options": []}
            elif line.startswith(('A)', 'B)', 'C)', 'D)')):
                current_q.setdefault("options", []).append(line[2:].strip())
            elif 'correct' in line.lower():
                answer = line.split(':')[-1].strip().upper()
                if answer in ['A', 'B', 'C', 'D']:
                    current_q["correct"] = answer
        
        if current_q and current_q.get("question"):
            mcqs.append(current_q)
        
        # Generate short answer questions
        short_prompt = f"""Create {num_short} short answer questions from this material for students aged {age_group}:

{text[:2000]}

Format:
Q1: [Question]
Answer: [Expected answer in 1-2 sentences]

Make questions test understanding, not just memorization."""

        short_response = self._generate_text(short_prompt, max_tokens=400)
        
        # Parse short answers
        short_questions = []
        current_sq = {}
        for line in short_response.split('\n'):
            line = line.strip()
            if line.startswith(('Q', 'q')) and ':' in line:
                if current_sq:
                    short_questions.append(current_sq)
                current_sq = {"question": line.split(':', 1)[1].strip()}
            elif line.lower().startswith('answer:'):
                current_sq["expected_answer"] = line.split(':', 1)[1].strip()
        
        if current_sq and current_sq.get("question"):
            short_questions.append(current_sq)
        
        return {
            "mcqs": mcqs[:num_mcq],
            "short_answers": short_questions[:num_short],
            "total_questions": len(mcqs) + len(short_questions),
            "source_material_length": len(text)
        }
    
    def evaluate_answer(
        self, 
        question: str, 
        student_answer: str, 
        expected_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a student's answer using AI.
        
        Args:
            question: The question asked
            student_answer: Student's answer
            expected_answer: Expected/correct answer
        
        Returns:
            Dict with evaluation result, score, feedback
        """
        # First, use QA model to check relevance
        try:
            qa_result = self.answer_question(
                context=expected_answer,
                question=f"Is this correct: {student_answer}?"
            )
        except:
            qa_result = {"answer": ""}
        
        # Use text generation for detailed evaluation
        eval_prompt = f"""Evaluate this student's answer:

Question: {question}
Student's Answer: {student_answer}
Expected Answer: {expected_answer}

Rate the answer:
1. Score (0-100)
2. Is it correct? (Yes/Partially/No)
3. What's good about the answer?
4. What could be improved?
5. Brief encouraging feedback

Be kind and constructive for a young student."""

        response = self._generate_text(eval_prompt, max_tokens=250)
        
        # Extract score
        score = 0
        is_correct = "no"
        
        lines = response.lower()
        if "100" in lines or "perfect" in lines or "excellent" in lines:
            score = 100
            is_correct = "yes"
        elif "80" in lines or "good" in lines:
            score = 80
            is_correct = "yes"
        elif "60" in lines or "partial" in lines:
            score = 60
            is_correct = "partially"
        elif "40" in lines or "some" in lines:
            score = 40
            is_correct = "partially"
        else:
            score = 20
            is_correct = "no"
        
        return {
            "question": question,
            "student_answer": student_answer,
            "expected_answer": expected_answer,
            "score": score,
            "is_correct": is_correct,
            "feedback": response,
            "qa_similarity": qa_result.get("score", 0) if isinstance(qa_result, dict) else 0
        }
    
    def analyze_weak_topics(
        self, 
        answers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze student answers to identify weak topics.
        
        Args:
            answers: List of evaluated answers with scores
        
        Returns:
            Dict with weak topics, strengths, and recommendations
        """
        if not answers:
            return {"weak_topics": [], "strengths": [], "recommendations": []}
        
        # Calculate overall performance
        total_score = sum(a.get("score", 0) for a in answers)
        avg_score = total_score / len(answers) if answers else 0
        
        # Identify weak and strong areas
        weak_answers = [a for a in answers if a.get("score", 0) < 60]
        strong_answers = [a for a in answers if a.get("score", 0) >= 80]
        
        # Generate recommendations
        reco_prompt = f"""Based on a student's performance:
- Average score: {avg_score:.0f}%
- Questions struggled with: {len(weak_answers)}
- Questions done well: {len(strong_answers)}

Weak areas (questions they got wrong):
{chr(10).join([a.get('question', '')[:80] for a in weak_answers[:3]])}

Provide:
1. 3 topics they should review more
2. 2 study strategies to improve
3. An encouraging message

Be positive and supportive."""

        recommendations = self._generate_text(reco_prompt, max_tokens=300)
        
        return {
            "total_questions": len(answers),
            "average_score": round(avg_score, 1),
            "weak_count": len(weak_answers),
            "strong_count": len(strong_answers),
            "weak_questions": [a.get("question", "") for a in weak_answers],
            "strong_questions": [a.get("question", "") for a in strong_answers],
            "recommendations": recommendations,
            "performance_level": (
                "Excellent!" if avg_score >= 80 else
                "Good progress!" if avg_score >= 60 else
                "Keep practicing!" if avg_score >= 40 else
                "Let's review together!"
            )
        }
    
    def generate_study_plan(
        self, 
        topics: List[str], 
        weak_areas: List[str],
        days: int = 7,
        age_group: str = "9-11"
    ) -> Dict[str, Any]:
        """
        Generate a personalized study plan.
        
        Args:
            topics: All topics from study material
            weak_areas: Topics student struggles with
            days: Number of days to plan
            age_group: Student's age group
        
        Returns:
            Dict with day-by-day study plan
        """
        prompt = f"""Create a {days}-day study plan for a {age_group} year old student.

Topics to cover: {', '.join(topics[:5])}
Weak areas to focus on: {', '.join(weak_areas[:3])}

For each day provide:
- Main topic to study (30 min)
- Practice activity (15 min)
- Fun learning tip

Make it engaging and not overwhelming. Include short breaks."""

        response = self._generate_text(prompt, max_tokens=500)
        
        # Parse into days
        plan = []
        current_day = {}
        for line in response.split('\n'):
            line = line.strip()
            if 'day 1' in line.lower() or 'day 2' in line.lower() or any(f"day {i}" in line.lower() for i in range(1, 8)):
                if current_day:
                    plan.append(current_day)
                current_day = {"day": len(plan) + 1, "activities": line}
            elif line and current_day:
                current_day["activities"] = current_day.get("activities", "") + "\n" + line
        
        if current_day:
            plan.append(current_day)
        
        return {
            "duration_days": days,
            "daily_plan": plan[:days],
            "focus_topics": weak_areas[:3] if weak_areas else topics[:3],
            "full_response": response
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


def generate_complete_puzzle(puzzle_type: str, topic: str, difficulty: str = "easy", age_group: str = "6-8") -> Dict[str, Any]:
    """Generate a complete puzzle of any type using AI."""
    return content_generator.generate_complete_puzzle(puzzle_type, topic, difficulty, age_group)
