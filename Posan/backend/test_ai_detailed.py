"""Test Hugging Face API integration - show full output"""
from app.services.ai_content import content_generator

print("Testing Hugging Face AI Content Generation...")
print("=" * 70)

# Test 1
print("\nTest 1: Story Generation")
print("-" * 70)
story = content_generator.generate_story(
    topic="underwater adventure",
    age_group="6-8",
    word_count=150
)
print(f"Title: {story['title']}")
print(f"\nFull Content:\n{story['content']}")
print(f"\nWord count: {story['word_count']}")

print("\n" + "=" * 70)

# Test 2
print("\nTest 2: Fun Fact Generation")
print("-" * 70)
fact = content_generator.generate_fun_fact("dolphins", "6-8")
print(f"Fun Fact: {fact}")

print("\n" + "=" * 70)
print("Both tests complete - AI is working if content is unique!")
