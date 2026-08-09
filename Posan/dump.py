from app.core.database import SessionLocal
from app.models.content import Magazine, Article
import sys

def dump():
    try:
        db = SessionLocal()
        mags = db.query(Magazine).all()
        print(f"Found {len(mags)} magazines.")
        for m in mags:
            print(f"Magazine: {m.title}")
            for a in m.articles:
                print(f"  - Article: {a.title} | Content Len: {len(a.content) if a.content else 0} | Content: {str(a.content)[:50]}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    dump()
