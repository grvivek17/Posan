"""
Script to update product images in the database
Run from backend directory: python -m scripts.update_product_images
"""
import sys
sys.path.append('.')

from app.core.database import SessionLocal
from app.models.store import Product, ProductCategory

def update_product_images():
    db = SessionLocal()
    
    # Category to image mapping
    category_images = {
        ProductCategory.ACTIVITY_BOOK: '/products/activity_book.png',
        ProductCategory.PUZZLE_BOOK: '/products/puzzle_book.png',
        ProductCategory.COLORING_BOOK: '/products/coloring_book.png',
        ProductCategory.STICKER_BOOK: '/products/sticker_book.png',
        ProductCategory.EDUCATIONAL: '/products/educational_book.png',
        ProductCategory.STORIES: '/products/story_book.png',
    }
    
    products = db.query(Product).all()
    updated = 0
    
    for product in products:
        if product.category in category_images:
            product.image_url = category_images[product.category]
            updated += 1
    
    db.commit()
    print(f"✅ Updated images for {updated} products!")
    db.close()

if __name__ == "__main__":
    update_product_images()
