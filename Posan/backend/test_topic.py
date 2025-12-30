"""Quick test to see the AI request/response with logging"""
from app.services.ai_content import content_generator

print("Testing with topic: 'robots'")
print("=" * 70)

# Test story generation
story = content_generator.generate_story(
    topic="robots",
    age_group="6-8",
    word_count=100
)

print("\n\nRESULT:")
print(f"Title: {story['title']}")
print(f"Content: {story['content'][:300]}...")
