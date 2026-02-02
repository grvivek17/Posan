from app.core.database import SessionLocal
from app.models.content import Magazine, Article
from sqlalchemy import desc

db = SessionLocal()

print("📰 January 2026 Magazines in Database\n")
print("=" * 80)

# Get January 2026 magazines
magazines = db.query(Magazine).filter(
    Magazine.publication_date >= '2026-01-01'
).order_by(desc(Magazine.publication_date)).all()

if not magazines:
    print("❌ No January 2026 magazines found!")
else:
    print(f"✅ Found {len(magazines)} January 2026 magazines!\n")
    
    for mag in magazines:
        print(f"\n📖 {mag.title}")
        print(f"   Age Group: {mag.age_group}")
        print(f"   Issue #{mag.issue_number}")
        print(f"   Published: {mag.publication_date.strftime('%B %d, %Y')}")
        print(f"   Description: {mag.description[:100]}...")
        
        # Get articles for this magazine
        articles = db.query(Article).filter(Article.magazine_id == mag.id).all()
        print(f"   📝 Articles: {len(articles)}")
        for article in articles:
            print(f"      - {article.title} ({article.content_type.value})")

print("\n" + "=" * 80)
print("✨ Magazine check complete!")

db.close()
