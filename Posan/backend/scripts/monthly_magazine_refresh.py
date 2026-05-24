"""
Monthly Magazine Refresh Script
Run this as a Render cron job on the 1st of every month.
It calls the backend API to generate fresh magazine content
from educational web sources (RSS feeds + web scraping).

Usage:
  python scripts/monthly_magazine_refresh.py
  python scripts/monthly_magazine_refresh.py --force       # Force regenerate even if magazines exist
  python scripts/monthly_magazine_refresh.py --direct       # Direct DB insertion (no API call)
  python scripts/monthly_magazine_refresh.py --direct --force

Environment:
  BACKEND_URL      - Base URL of the backend API (default: http://localhost:8000)
  REFRESH_METHOD   - "api" (default) or "direct"
  FORCE_REFRESH    - "true" to force regeneration even if magazines already exist
  
For Render cron job, set BACKEND_URL to your Render backend URL.
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def refresh_via_api(force: bool = False):
    """Call the refresh-monthly API endpoint."""
    import requests
    
    backend_url = os.environ.get("BACKEND_URL", "http://localhost:8000")
    url = f"{backend_url}/api/v1/content/magazines/refresh-monthly"
    if force:
        url += "?force=true"
    
    print(f"Calling: POST {url}")
    
    try:
        response = requests.post(url, timeout=180)
        response.raise_for_status()
        data = response.json()
        
        print(f"\nResult: {data.get('status', 'unknown')}")
        print(f"Message: {data.get('message', 'No message')}")
        
        if data.get("magazines"):
            print(f"\nMagazines created:")
            for mag in data["magazines"]:
                print(f"  - {mag['title']} (Ages {mag['age_group']}, {mag['articles_count']} articles)")
        
        return data
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Cannot connect to {backend_url}. Is the server running?")
        return None
    except requests.exceptions.Timeout:
        print(f"[ERROR] Request timed out after 180s. The server might be slow.")
        return None
    except Exception as e:
        print(f"[ERROR] API call failed: {e}")
        return None


def refresh_directly(force: bool = False):
    """Directly generate and insert magazines (for when running within the backend environment)."""
    try:
        from app.core.database import SessionLocal
        from app.models.content import Magazine, Article, Quiz, ContentType
        from app.models.user import AgeGroup
        from sqlalchemy import extract
    except ImportError:
        print("[ERROR] Cannot import backend modules. Use API method instead.")
        return None
    
    db = SessionLocal()
    now = datetime.now()
    month_name = now.strftime("%B")
    year = now.year
    
    try:
        # Check if magazines already exist for this month
        existing = db.query(Magazine).filter(
            extract("month", Magazine.publication_date) == now.month,
            extract("year", Magazine.publication_date) == now.year
        ).all()
        
        if existing and not force:
            print(f"Magazines for {month_name} {year} already exist ({len(existing)} found). Skipping.")
            print("  Use --force flag to regenerate.")
            return {"status": "skipped", "count": len(existing)}
        
        # Force refresh: delete existing magazines and their articles
        if existing and force:
            print(f"Force refresh: deleting {len(existing)} old magazines for {month_name} {year}...")
            for mag in existing:
                articles = db.query(Article).filter(Article.magazine_id == mag.id).all()
                for art in articles:
                    db.query(Quiz).filter(Quiz.article_id == art.id).delete()
                    db.delete(art)
                db.delete(mag)
            db.flush()
            print("  Old magazines deleted.")
        
        # Initialize AI generator (optional)
        ai_generator = None
        try:
            from app.services.ai_content import ContentGenerator
            ai_generator = ContentGenerator()
            print("  AI content generator initialized.")
        except Exception as e:
            print(f"[WARN] AI generator not available: {e}")
        
        # Initialize fetcher
        from app.services.magazine_fetcher import MagazineFetcher
        fetcher = MagazineFetcher(ai_generator=ai_generator)
        
        # Try web fetching, fallback to curated content
        magazines_data = None
        try:
            print("\n  Fetching content from web sources...")
            magazines_data = fetcher.generate_monthly_magazines()
        except Exception as e:
            print(f"[WARN] Web fetch failed: {e}. Using fallback.")
        
        if not magazines_data:
            print("  Using fallback curated content...")
            magazines_data = fetcher.generate_fallback_magazines()
        
        age_group_map = {
            "3-5": AgeGroup.TODDLER,
            "6-8": AgeGroup.EARLY,
            "9-11": AgeGroup.MIDDLE,
            "12-14": AgeGroup.PRETEEN,
        }
        content_type_map = {
            "article": ContentType.ARTICLE,
            "story": ContentType.STORY,
            "activity": ContentType.ACTIVITY,
            "comic": ContentType.COMIC,
        }
        
        created = []
        for mag_data in magazines_data:
            age_str = mag_data["magazine"]["age_group"]
            age_enum = age_group_map.get(age_str, AgeGroup.EARLY)
            
            magazine = Magazine(
                title=mag_data["magazine"]["title"],
                description=mag_data["magazine"]["description"],
                age_group=age_enum,
                issue_number=mag_data["magazine"]["issue_number"],
                cover_image_url=mag_data["magazine"]["cover_image_url"],
                is_published=mag_data["magazine"]["is_published"],
                publication_date=mag_data["magazine"]["publication_date"],
            )
            db.add(magazine)
            db.flush()
            
            for article_data in mag_data["articles"]:
                art_age = age_group_map.get(article_data["age_group"], AgeGroup.EARLY)
                ct = content_type_map.get(article_data.get("content_type", "article"), ContentType.ARTICLE)
                
                article = Article(
                    magazine_id=magazine.id,
                    title=article_data["title"],
                    content=article_data["content"],
                    content_type=ct,
                    author=article_data.get("author", "Poshan Team"),
                    reading_time_minutes=article_data.get("reading_time_minutes", 5),
                    age_group=art_age,
                    order_in_magazine=article_data.get("order_in_magazine", 1),
                )
                db.add(article)
            
            created.append(magazine.title)
            print(f"  Created: {magazine.title} ({len(mag_data['articles'])} articles)")
        
        db.commit()
        print(f"\nSuccessfully created {len(created)} magazines for {month_name} {year}!")
        return {"status": "success", "count": len(created)}
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return None
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print(f"Monthly Magazine Refresh - {datetime.now().strftime('%B %Y')}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()
    
    # Determine if force refresh
    force = os.environ.get("FORCE_REFRESH", "false").lower() == "true" or "--force" in sys.argv
    
    # Determine method: API or direct
    method = os.environ.get("REFRESH_METHOD", "api")
    
    if force:
        print("Mode: FORCE REFRESH (will replace existing magazines)")
    
    if method == "direct" or "--direct" in sys.argv:
        print("Method: Direct database insertion")
        result = refresh_directly(force=force)
    else:
        print("Method: API call")
        result = refresh_via_api(force=force)
    
    if result:
        print(f"\nDone! Status: {result.get('status', 'unknown')}")
    else:
        print("\nFailed to refresh magazines.")
        sys.exit(1)
