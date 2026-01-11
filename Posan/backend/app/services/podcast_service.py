"""
AI Podcast Generation Service
Generates text-based podcast scripts using AI
"""
from typing import Optional, Dict, Any
import os
from datetime import datetime


class PodcastGenerator:
    """Generate kid-friendly podcast scripts using AI"""
    
    def __init__(self):
        self.hf_token = os.getenv("HUGGINGFACE_TOKEN")
        self.model_name = "mistralai/Mistral-7B-Instruct-v0.2"
    
    def generate_podcast_script(
        self,
        topic: str,
        age_group: str = "8-12",
        duration: str = "short",  # short (2-3 min), medium (5 min), long (10 min)
        style: str = "fun"  # fun, educational, story
    ) -> Dict[str, Any]:
        """
        Generate a podcast script on a given topic
        
        Args:
            topic: The topic to create a podcast about
            age_group: Target age group (e.g., "6-8", "8-12", "12-14")
            duration: Desired length (short, medium, long)
            style: Podcast style (fun, educational, story)
        
        Returns:
            Dictionary with podcast script and metadata
        """
        
        # Determine word count based on duration
        word_counts = {
            "short": "300-400 words (2-3 minutes)",
            "medium": "600-800 words (5 minutes)",
            "long": "1200-1500 words (10 minutes)"
        }
        
        word_count = word_counts.get(duration, word_counts["short"])
        
        # Create prompt based on style
        if style == "fun":
            prompt = f"""Create a fun and engaging podcast script for kids aged {age_group} about: {topic}

The podcast should be:
- Exciting and entertaining
- Include fun facts and interesting details
- Use simple, kid-friendly language
- Include sound effect suggestions (like *whoosh*, *ding*, etc.)
- Have a friendly, enthusiastic tone
- Length: {word_count}

Format the script with:
[INTRO] - Opening greeting
[MAIN CONTENT] - The main topic discussion
[FUN FACT] - An amazing fact
[OUTRO] - Closing message

Make it sound like a real podcast host talking to kids!"""

        elif style == "educational":
            prompt = f"""Create an educational podcast script for kids aged {age_group} about: {topic}

The podcast should be:
- Informative and accurate
- Explain concepts clearly
- Include interesting examples
- Use age-appropriate vocabulary
- Encourage curiosity and learning
- Length: {word_count}

Format the script with:
[INTRO] - Welcome and topic introduction
[LEARNING SECTION] - Main educational content
[DID YOU KNOW] - Fascinating facts
[ACTIVITY SUGGESTION] - Something kids can try
[OUTRO] - Summary and goodbye

Make it educational but fun!"""

        else:  # story style
            prompt = f"""Create a story-based podcast script for kids aged {age_group} about: {topic}

The podcast should be:
- Tell an engaging story related to the topic
- Include characters and dialogue
- Have a beginning, middle, and end
- Teach something valuable
- Be imaginative and creative
- Length: {word_count}

Format the script with:
[INTRO] - Story setup
[STORY] - The main narrative
[LESSON] - What we learned
[OUTRO] - Closing thoughts

Make it an adventure kids will love!"""

        try:
            # Try to use HuggingFace API
            if self.hf_token:
                script = self._generate_with_hf(prompt)
            else:
                # Fallback to template-based generation
                script = self._generate_template(topic, age_group, duration, style)
            
            # Parse the script into sections
            sections = self._parse_script(script)
            
            return {
                "success": True,
                "topic": topic,
                "script": script,
                "sections": sections,
                "metadata": {
                    "age_group": age_group,
                    "duration": duration,
                    "style": style,
                    "word_count": len(script.split()),
                    "estimated_minutes": self._estimate_duration(script),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "topic": topic
            }
    
    def _generate_with_hf(self, prompt: str) -> str:
        """Generate script using HuggingFace API"""
        try:
            from huggingface_hub import InferenceClient
            
            client = InferenceClient(token=self.hf_token)
            
            response = client.text_generation(
                prompt,
                model=self.model_name,
                max_new_tokens=1500,
                temperature=0.7,
                top_p=0.95,
            )
            
            return response
            
        except Exception as e:
            print(f"HuggingFace API error: {e}")
            raise
    
    def _generate_template(self, topic: str, age_group: str, duration: str, style: str) -> str:
        """Fallback template-based generation"""
        
        templates = {
            "fun": f"""[INTRO]
🎙️ Hey there, awesome kids! Welcome to Fun Facts Radio! Today we're diving into the amazing world of {topic}! Get ready for some super cool discoveries!

[MAIN CONTENT]
So, what makes {topic} so interesting? Well, let me tell you! *ding* 

{topic} is one of the most fascinating things in our world. Did you know that scientists have been studying {topic} for many years? They've discovered so many incredible things!

Let me share some of the coolest parts about {topic}. First, it's way more amazing than you might think! The way {topic} works is like magic, but it's real science!

[FUN FACT]
🌟 Here's a mind-blowing fact: {topic} has surprised even the smartest scientists! They keep finding new and exciting things about it every day!

[OUTRO]
Wow! Wasn't that amazing? I hope you learned something super cool about {topic} today! Keep being curious, keep asking questions, and remember - the world is full of awesome things to discover! See you next time on Fun Facts Radio! *whoosh*""",

            "educational": f"""[INTRO]
Hello, young learners! Welcome to Knowledge Quest. Today's topic is: {topic}. Let's explore and learn together!

[LEARNING SECTION]
{topic} is an important subject that helps us understand our world better. Let's break it down into simple parts.

First, what is {topic}? It's something that affects our daily lives in many ways. Understanding {topic} helps us make better decisions and appreciate the world around us.

[DID YOU KNOW]
Here's something fascinating: {topic} has been part of human knowledge for a very long time. People have been curious about it throughout history!

[ACTIVITY SUGGESTION]
Want to learn more? Try observing {topic} in your everyday life. Ask your parents or teachers questions about it. You can even do a simple project to explore {topic} further!

[OUTRO]
Great job learning about {topic} today! Remember, every question you ask makes you smarter. Keep exploring, keep learning, and stay curious!""",

            "story": f"""[INTRO]
*magical sound* Once upon a time, in a world not so different from ours, there was an amazing discovery about {topic}...

[STORY]
Our story begins with a curious child named Alex who loved to explore. One day, Alex wondered about {topic} and decided to find out more.

Alex's journey took them to incredible places where they learned that {topic} was more magical than anyone imagined! Along the way, Alex met helpful friends who shared their knowledge.

Together, they discovered the secrets of {topic}, and Alex learned valuable lessons about curiosity, persistence, and the joy of discovery.

[LESSON]
What did we learn from Alex's adventure? That {topic} is all around us, and when we're curious and brave enough to explore, we can discover amazing things!

[OUTRO]
And that's the end of our story! Remember, like Alex, you can be an explorer too. The world is full of wonders waiting for you to discover. Until next time, keep dreaming and exploring!"""
        }
        
        return templates.get(style, templates["fun"])
    
    def _parse_script(self, script: str) -> Dict[str, str]:
        """Parse script into sections"""
        sections = {}
        current_section = "intro"
        current_content = []
        
        for line in script.split('\n'):
            if line.strip().startswith('[') and line.strip().endswith(']'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line.strip('[').strip(']').lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        return sections
    
    def _estimate_duration(self, script: str) -> int:
        """Estimate podcast duration in minutes based on word count"""
        words = len(script.split())
        # Average speaking rate: 150 words per minute
        minutes = words / 150
        return max(1, round(minutes))
    
    def generate_weekly_highlights(self, magazine_topics: list) -> Dict[str, Any]:
        """Generate a weekly highlights podcast from magazine topics"""
        
        if not magazine_topics:
            magazine_topics = [
                "Space Exploration",
                "Ocean Animals",
                "Ancient Civilizations",
                "Cool Inventions"
            ]
        
        topics_text = ", ".join(magazine_topics)
        
        prompt = f"""Create a fun weekly highlights podcast script for kids aged 8-12 covering these topics: {topics_text}

Make it exciting and engaging! Include:
- A catchy intro
- Brief highlights of each topic (1-2 sentences each)
- One amazing fact from each topic
- An encouraging outro

Keep it under 500 words (3-4 minutes).

Format with clear sections."""

        try:
            if self.hf_token:
                script = self._generate_with_hf(prompt)
            else:
                script = self._generate_weekly_template(magazine_topics)
            
            return {
                "success": True,
                "title": "Weekly Highlights Podcast",
                "topics": magazine_topics,
                "script": script,
                "metadata": {
                    "type": "weekly_highlights",
                    "word_count": len(script.split()),
                    "estimated_minutes": self._estimate_duration(script),
                    "generated_at": datetime.utcnow().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_weekly_template(self, topics: list) -> str:
        """Template for weekly highlights"""
        
        topics_section = "\n\n".join([
            f"📌 {topic}: This week we discovered amazing things about {topic}! "
            f"Did you know that {topic} is more fascinating than we thought? "
            f"Scientists and explorers keep finding new surprises!"
            for topic in topics
        ])
        
        return f"""🎙️ WEEKLY HIGHLIGHTS PODCAST 🎙️

[INTRO]
*upbeat music* 
Hello, amazing kids! Welcome to this week's highlights show! I'm so excited to share all the cool things we've learned this week. Are you ready? Let's go!

[HIGHLIGHTS]
{topics_section}

[AMAZING FACT]
🌟 Here's the most mind-blowing fact of the week: All of these topics are connected! Everything in our world is related in surprising ways. When you learn about one thing, you're actually learning about many things!

[OUTRO]
Wow! What an incredible week of learning! I hope you're as excited as I am about all these discoveries. Remember, there's always something new to learn, and every day is an adventure!

Keep being curious, keep asking questions, and I'll see you next week with more amazing highlights!

*cheerful music fades out*

Stay awesome, young explorers! 🚀✨"""


# Create global instance
podcast_generator = PodcastGenerator()
