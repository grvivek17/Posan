"""Test Hugging Face API integration"""
from app.services.ai_content import content_generator
import sys

print("Testing Hugging Face AI Content Generation...")
print("=" * 50)

try:
    print("\n1. Testing story generation...")
    story = content_generator.generate_story(
        topic="space adventure",
        age_group="6-8",
        word_count=100
    )
    print(f"Title: {story['title']}")
    print(f"Content preview: {story['content'][:200]}...")
    print(f"Word count: {story['word_count']}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Test complete!")
