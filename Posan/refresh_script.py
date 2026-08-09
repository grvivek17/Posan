from app.core.database import SessionLocal
from app.models.content import Article, Magazine
from app.services.magazine_fetcher import MagazineFetcher
import sys

def refresh():
    try:
        db = SessionLocal()
        db.query(Article).delete()
        db.query(Magazine).delete()
        db.commit()
        print("Cleared old magazines and articles.")
        
        fetcher = MagazineFetcher()
        fetcher.generate_monthly_magazines()
        print("Generated new magazines successfully.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    refresh()
