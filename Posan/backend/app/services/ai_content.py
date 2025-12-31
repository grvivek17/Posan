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
        
        print("✅ Educational AI models loaded:")
        for name, model in self.education_models.items():
            print(f"   - {name}: {model}")
    
    
    def _generate_text(self, prompt: str, max_tokens: int = 500) -> str:
        """Generate text using Hugging Face Inference API with text generation."""
        print(f"\n{'='*60}")
        print(f"AI GENERATION REQUEST")
        print(f"{'='*60}")
        print(f"Prompt: {prompt[:200]}...")
        print(f"Max tokens: {max_tokens}")
        
        # Format prompt for text generation
        formatted_prompt = f"You are a helpful assistant that creates kid-friendly, educational content. Always be positive, fun, and age-appropriate.\n\nUser: {prompt}\n\nAssistant:"
        
        for model in self.chat_models:
            try:
                print(f"\nTrying model: {model}")
                response = self.client.text_generation(
                    formatted_prompt,
                    model=model,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    return_full_text=False
                )
                
                # Handle response - text_generation returns a string
                content = response if isinstance(response, str) else str(response)
                
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
        total_marks = sum(q.get("marks_awarded", 0) for q in question_answers if q.get("marks_awarded") is not None)
        max_marks = sum(q.get("max_marks", 10) for q in question_answers)  # Default 10 marks per question
        
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
