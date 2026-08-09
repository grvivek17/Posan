import sys
import os
from datetime import datetime

# Ensure app is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.content import Article, Magazine
from app.models.user import AgeGroup
from app.services.magazine_fetcher import MagazineFetcher
from app.services.ai_content import ContentGenerator

def generate_archives():
    try:
        db = SessionLocal()
        print("Connected to DB.")
        
        # We need AI Content Generator since user requested AI generated articles
        ai_generator = ContentGenerator()
        fetcher = MagazineFetcher(ai_generator=ai_generator)
        
        # Generate archives for Jan to July 2026.
        for i in range(1, 8):
            target_date = datetime(2026, i, 1)
            print(f"\nGenerating for {target_date.strftime('%B %Y')}")
            
            magazines_data = fetcher.generate_monthly_magazines(target_date)
            
            for mag_data in magazines_data:
                mag_dict = mag_data["magazine"]
                mag_dict["age_group"] = AgeGroup(mag_dict["age_group"])
                
                db_mag = Magazine(**mag_dict)
                db.add(db_mag)
                db.flush() # get id
                
                for art_idx, art_data in enumerate(mag_data["articles"]):
                    art_data["magazine_id"] = db_mag.id
                    art_data["age_group"] = AgeGroup(art_data["age_group"])
                    art_data["order_in_magazine"] = art_idx
                    db_art = Article(**art_data)
                    db.add(db_art)
                    
            db.commit()
            print(f"Committed {target_date.strftime('%B %Y')} to DB.")
            
        print("Archive generation complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    generate_archives()
