"""
Script to seed sample products for the Activity Book Store
Run from backend directory: python -m scripts.seed_products
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.store import Product, ProductCategory

def seed_products():
    db = SessionLocal()
    
    # Check if products already exist
    existing = db.query(Product).count()
    if existing > 0:
        print(f"Products already exist ({existing} products)")
        return
    
    sample_products = [
        Product(
            name="Ultimate Activity Book for Kids",
            description="200+ puzzles, mazes, word searches, and brain teasers! Perfect for keeping kids entertained during travel or at home.",
            price=349,
            original_price=499,
            category=ProductCategory.ACTIVITY_BOOK,
            age_range="5-8",
            pages=120,
            is_bestseller=True,
            rating=4.8,
            reviews_count=234
        ),
        Product(
            name="Puzzle Paradise - 500 Puzzles",
            description="Crosswords, Sudoku, Word Searches, and Logic Puzzles for young minds. Hours of screen-free entertainment!",
            price=449,
            original_price=599,
            category=ProductCategory.PUZZLE_BOOK,
            age_range="8-12",
            pages=200,
            is_bestseller=True,
            rating=4.9,
            reviews_count=189
        ),
        Product(
            name="Magical Coloring Adventure",
            description="Beautiful illustrations of fairies, dragons, unicorns and magical creatures. Thick paper prevents bleed-through.",
            price=199,
            original_price=299,
            category=ProductCategory.COLORING_BOOK,
            age_range="3-6",
            pages=80,
            is_new=True,
            rating=4.7,
            reviews_count=156
        ),
        Product(
            name="Dinosaur Sticker Fun",
            description="500+ reusable dinosaur stickers! Create your own prehistoric scenes with T-Rex, Triceratops, and more.",
            price=249,
            category=ProductCategory.STICKER_BOOK,
            age_range="3-5",
            pages=40,
            is_new=True,
            rating=4.6,
            reviews_count=98
        ),
        Product(
            name="Math Champions Workbook",
            description="Fun math exercises, puzzles, and games. Build strong math foundations while having fun!",
            price=279,
            original_price=349,
            category=ProductCategory.EDUCATIONAL,
            age_range="6-8",
            pages=100,
            rating=4.5,
            reviews_count=145
        ),
        Product(
            name="Science Explorer Activity Book",
            description="Experiments, diagrams, and activities about space, animals, plants, and the human body!",
            price=329,
            category=ProductCategory.EDUCATIONAL,
            age_range="8-12",
            pages=96,
            is_bestseller=True,
            rating=4.8,
            reviews_count=167
        ),
        Product(
            name="Bedtime Stories Collection",
            description="50 enchanting stories to read before bed. Beautiful illustrations and moral lessons.",
            price=399,
            original_price=499,
            category=ProductCategory.STORIES,
            age_range="3-8",
            pages=180,
            rating=4.9,
            reviews_count=312
        ),
        Product(
            name="Animal Kingdom Coloring Book",
            description="Lions, elephants, dolphins and 100+ animals to color! Learn fun facts about each animal.",
            price=179,
            category=ProductCategory.COLORING_BOOK,
            age_range="4-8",
            pages=64,
            rating=4.6,
            reviews_count=89
        ),
        Product(
            name="Brain Games for Smart Kids",
            description="Logic puzzles, riddles, optical illusions, and memory challenges. Train your brain!",
            price=299,
            original_price=399,
            category=ProductCategory.PUZZLE_BOOK,
            age_range="9-12",
            pages=128,
            is_new=True,
            rating=4.7,
            reviews_count=76
        ),
        Product(
            name="Princess Sticker Dress-Up",
            description="300+ beautiful stickers to dress up princesses for balls, adventures, and more!",
            price=199,
            category=ProductCategory.STICKER_BOOK,
            age_range="4-7",
            pages=32,
            rating=4.5,
            reviews_count=134
        ),
        Product(
            name="World Atlas for Kids",
            description="Explore every continent with maps, flags, fun facts, and activities about countries!",
            price=549,
            original_price=699,
            category=ProductCategory.EDUCATIONAL,
            age_range="6-12",
            pages=160,
            is_bestseller=True,
            rating=4.9,
            reviews_count=201
        ),
        Product(
            name="Space Adventure Activity Book",
            description="Rockets, planets, astronauts! Puzzles, coloring, and facts about our solar system.",
            price=279,
            category=ProductCategory.ACTIVITY_BOOK,
            age_range="5-10",
            pages=88,
            is_new=True,
            rating=4.7,
            reviews_count=67
        ),
    ]
    
    for product in sample_products:
        db.add(product)
    
    db.commit()
    print(f"✅ Created {len(sample_products)} sample products!")
    db.close()

if __name__ == "__main__":
    seed_products()
