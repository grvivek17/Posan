import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.content import Magazine, Article, ContentType
from app.models.user import AgeGroup
from datetime import datetime
import json

# Setup Database Connection
db: Session = SessionLocal()

def clear_magazines():
    print("Clearing old magazines...")
    db.query(Article).delete()
    db.query(Magazine).delete()
    db.commit()

def generate_custom_magazines():
    month_name = datetime.now().strftime("%B %Y")
    
    # Custom Data
    data = [
        {
            "age_group": AgeGroup.TODDLER,
            "title": f"Little Explorers - {month_name}",
            "cover_image_url": "https://posanlearn.vercel.app/images/magazines/animals_cover.png",
            "articles": [
                {
                    "title": "Welcome to the Jungle!",
                    "content": "![Jungle Animals](https://posanlearn.vercel.app/images/magazines/animals_cover.png)\n\n**Welcome to the Jungle!**\n\nThe jungle is full of amazing animals! Did you know that monkeys love to swing from trees, and lions have big, loud roars? \n\n🦁 **Did You Know?**\nA lion's roar can be heard from 5 miles away!\n\n**Fun Activity:**\nCan you practice your best lion roar?"
                }
            ]
        },
        {
            "age_group": AgeGroup.EARLY,
            "title": f"Young Discoverers - {month_name}",
            "cover_image_url": "https://posanlearn.vercel.app/images/magazines/science_cover.png",
            "articles": [
                {
                    "title": "Journey Through Space",
                    "content": "![Space Science](https://posanlearn.vercel.app/images/magazines/science_cover.png)\n\n**Journey Through Space**\n\nSpace is huge! It is filled with planets, stars, and galaxies. Our planet, Earth, is part of a neighborhood called the Solar System. The Sun is at the center, and 8 planets travel around it!\n\n✨ **Did You Know?**\nOne day on Venus is longer than a year on Venus! It spins very slowly.\n\n**Fun Activity:**\nDraw a picture of your favorite planet!"
                }
            ]
        },
        {
            "age_group": AgeGroup.MIDDLE,
            "title": f"Knowledge Explorers - {month_name}",
            "cover_image_url": "https://posanlearn.vercel.app/images/magazines/adventure_cover.png",
            "articles": [
                {
                    "title": "The Great Adventure",
                    "content": "![Adventure Awaits](https://posanlearn.vercel.app/images/magazines/adventure_cover.png)\n\n**The Great Adventure**\n\nExplorers have traveled across oceans, climbed the highest mountains, and even walked on the moon! Exploring helps us discover hidden treasures, new species, and understand our world better.\n\n🗺️ **Did You Know?**\nThe deepest part of the ocean, the Mariana Trench, is so deep that if you dropped Mount Everest into it, the peak would still be more than a mile underwater!\n\n**Fun Activity:**\nCreate a treasure map of your house or backyard. Hide a small toy and see if someone can follow the map to find it!"
                }
            ]
        },
        {
            "age_group": AgeGroup.PRETEEN,
            "title": f"Teen Innovators - {month_name}",
            "cover_image_url": "https://posanlearn.vercel.app/images/magazines/comics_cover.png",
            "articles": [
                {
                    "title": "The Science of Superheroes",
                    "content": "![Comic Book Heroes](https://posanlearn.vercel.app/images/magazines/comics_cover.png)\n\n**The Science of Superheroes**\n\nComic books are filled with amazing characters with superpowers! But what if those powers were real? Scientists are studying how some animals naturally possess abilities that look like superpowers—like geckos climbing walls, or jellyfish that can glow in the dark (bioluminescence).\n\n🦸 **Did You Know?**\nSpider silk is proportionally stronger than steel! If you made a web with threads as thick as a pencil, it could stop a Boeing 747 in flight!\n\n**Fun Activity:**\nIf you could have one scientifically possible superpower, what would it be and how would you use it?"
                }
            ]
        }
    ]
    
    print("Generating new magazines...")
    for item in data:
        mag = Magazine(
            title=item["title"],
            cover_image_url=item["cover_image_url"],
            age_group=item["age_group"],
            publication_date=datetime.now(),
            is_published=True
        )
        db.add(mag)
        db.commit()
        db.refresh(mag)
        
        for art_idx, article_data in enumerate(item["articles"]):
            article = Article(
                magazine_id=mag.id,
                title=article_data["title"],
                content=article_data["content"],
                illustration_url=item["cover_image_url"],
                order_in_magazine=art_idx,
                age_group=item["age_group"]
            )
            db.add(article)
            
        db.commit()
        print(f"Created magazine: {mag.title} for {mag.age_group.value}")

if __name__ == "__main__":
    clear_magazines()
    generate_custom_magazines()
    print("Seeding complete!")
