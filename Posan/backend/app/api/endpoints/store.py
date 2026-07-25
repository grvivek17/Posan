"""
Store API endpoints for Kids Activity Books
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.store import Product, Cart, CartItem, Order, OrderItem, ProductCategory, OrderStatus

router = APIRouter(prefix="/store", tags=["store"])


# ==================== PRODUCTS ====================

@router.get("/products")
async def get_products(
    category: Optional[str] = None,
    age_range: Optional[str] = None,
    search: Optional[str] = None,
    bestseller: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db)
):
    """Get all products with optional filters"""
    query = db.query(Product).filter(Product.is_available == True)
    
    if category:
        try:
            cat_enum = ProductCategory(category)
            query = query.filter(Product.category == cat_enum)
        except ValueError:
            pass
    
    if age_range:
        query = query.filter(Product.age_range == age_range)
    
    if search:
        query = query.filter(
            (Product.name.ilike(f"%{search}%")) |
            (Product.description.ilike(f"%{search}%"))
        )
    
    if bestseller:
        query = query.filter(Product.is_bestseller == True)
    
    total = query.count()
    products = query.order_by(desc(Product.is_bestseller), desc(Product.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "original_price": p.original_price,
                "image_url": p.image_url,
                "category": p.category.value if p.category else None,
                "age_range": p.age_range,
                "pages": p.pages,
                "is_bestseller": p.is_bestseller,
                "is_new": p.is_new,
                "stock": p.stock,
                "rating": p.rating,
                "reviews_count": p.reviews_count
            }
            for p in products
        ]
    }


@router.get("/products/{product_id}")
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get single product details"""
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "original_price": product.original_price,
        "image_url": product.image_url,
        "category": product.category.value if product.category else None,
        "age_range": product.age_range,
        "pages": product.pages,
        "is_bestseller": product.is_bestseller,
        "is_new": product.is_new,
        "is_available": product.is_available,
        "stock": product.stock,
        "rating": product.rating,
        "reviews_count": product.reviews_count
    }


@router.get("/categories")
async def get_categories():
    """Get all product categories"""
    return {
        "categories": [
            {"value": cat.value, "label": cat.value.replace("_", " ").title()}
            for cat in ProductCategory
        ]
    }


# ==================== CART ====================

@router.get("/cart")
async def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        return {"items": [], "total": 0, "item_count": 0}
    
    items = []
    total = 0
    
    for item in cart.items:
        item_total = item.product.price * item.quantity
        total += item_total
        items.append({
            "id": item.id,
            "product_id": item.product.id,
            "name": item.product.name,
            "price": item.product.price,
            "image_url": item.product.image_url,
            "quantity": item.quantity,
            "item_total": item_total
        })
    
    return {
        "items": items,
        "total": total,
        "item_count": sum(item["quantity"] for item in items)
    }


@router.post("/cart/add")
async def add_to_cart(
    product_id: int,
    quantity: int = 1,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    # Check product exists and is available
    product = db.query(Product).filter(Product.id == product_id, Product.is_available == True).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or unavailable")
    
    if product.stock < quantity:
        raise HTTPException(status_code=400, detail="Not enough stock")
    
    # Get or create cart
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    
    # Check if item already in cart
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
        db.add(cart_item)
    
    db.commit()
    
    return {"message": "Item added to cart", "quantity": cart_item.quantity}


@router.put("/cart/update/{item_id}")
async def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update cart item quantity"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    if quantity <= 0:
        db.delete(cart_item)
    else:
        cart_item.quantity = quantity
    
    db.commit()
    
    return {"message": "Cart updated"}


@router.delete("/cart/remove/{item_id}")
async def remove_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()
    
    if not cart_item:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    db.delete(cart_item)
    db.commit()
    
    return {"message": "Item removed from cart"}


@router.delete("/cart/clear")
async def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear entire cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
        db.commit()
    
    return {"message": "Cart cleared"}


# ==================== ORDERS ====================

@router.post("/checkout")
async def checkout(
    shipping_address: str,
    phone: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create order from cart"""
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total
    total = sum(item.product.price * item.quantity for item in cart.items)
    
    # Create order
    order = Order(
        user_id=current_user.id,
        total_amount=total,
        shipping_address=shipping_address,
        phone=phone,
        status=OrderStatus.PENDING
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Create order items
    for cart_item in cart.items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity,
            price=cart_item.product.price
        )
        db.add(order_item)
        
        # Reduce stock
        cart_item.product.stock -= cart_item.quantity
    
    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    
    return {
        "message": "Order created",
        "order_id": order.id,
        "total": total,
        "razorpay_order": {
            "amount": int(total * 100),  # Razorpay expects paise
            "currency": "INR",
            "notes": {"order_id": order.id}
        }
    }


@router.post("/orders/{order_id}/confirm-payment")
async def confirm_payment(
    order_id: int,
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Confirm payment for order"""
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order.payment_id = payment_id
    order.payment_provider = "razorpay"
    order.status = OrderStatus.PAID
    
    db.commit()
    
    return {"message": "Payment confirmed", "status": order.status.value}


@router.get("/orders")
async def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's orders"""
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(desc(Order.created_at)).all()
    
    return {
        "orders": [
            {
                "id": order.id,
                "total_amount": order.total_amount,
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "item_count": len(order.items),
                "items": [
                    {
                        "name": item.product.name,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ]
            }
            for order in orders
        ]
    }


# ==================== ADMIN: SEED DATA ====================

@router.post("/admin/seed-products")
async def seed_products(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Seed sample products (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if products already exist
    existing = db.query(Product).count()
    if existing > 0:
        return {"message": f"Products already exist ({existing} products)"}
    
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
    
    return {"message": f"Created {len(sample_products)} sample products"}


# ==================== ADMIN: PRODUCT MANAGEMENT ====================

@router.get("/admin/products")
async def get_all_products_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all products including hidden ones (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    total = db.query(Product).count()
    products = db.query(Product).order_by(desc(Product.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "original_price": p.original_price,
                "image_url": p.image_url,
                "category": p.category.value if p.category else None,
                "age_range": p.age_range,
                "pages": p.pages,
                "is_bestseller": p.is_bestseller,
                "is_new": p.is_new,
                "is_available": p.is_available,
                "stock": p.stock,
                "rating": p.rating,
                "reviews_count": p.reviews_count
            }
            for p in products
        ]
    }

@router.post("/admin/products")
async def create_product(
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new product (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        category = ProductCategory(product_data.get('category', 'activity_book'))
    except ValueError:
        category = ProductCategory.ACTIVITY_BOOK
    
    product = Product(
        name=product_data.get('name'),
        description=product_data.get('description'),
        price=product_data.get('price'),
        original_price=product_data.get('original_price'),
        image_url=product_data.get('image_url'),
        category=category,
        age_range=product_data.get('age_range'),
        pages=product_data.get('pages'),
        is_bestseller=product_data.get('is_bestseller', False),
        is_new=product_data.get('is_new', False),
        is_available=product_data.get('is_available', True),
        stock=product_data.get('stock', 100),
        rating=product_data.get('rating', 4.5),
        reviews_count=product_data.get('reviews_count', 0)
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Product created successfully",
        "product_id": product.id
    }


@router.put("/admin/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a product (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Update fields
    updatable_fields = [
        'name', 'description', 'price', 'original_price', 'image_url',
        'age_range', 'pages', 'is_bestseller', 'is_new', 'is_available', 'stock'
    ]
    
    for field in updatable_fields:
        if field in product_data:
            setattr(product, field, product_data[field])
    
    # Handle category separately
    if 'category' in product_data:
        try:
            product.category = ProductCategory(product_data['category'])
        except ValueError:
            pass
    
    db.commit()
    db.refresh(product)
    
    return {
        "message": "Product updated successfully",
        "product": {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    }


@router.delete("/admin/products/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a product (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product has any orders
    order_items = db.query(OrderItem).filter(OrderItem.product_id == product_id).count()
    if order_items > 0:
        # Soft delete - just mark as unavailable
        product.is_available = False
        db.commit()
        return {"message": "Product hidden (has order history)"}
    
    # Hard delete if no orders
    db.query(CartItem).filter(CartItem.product_id == product_id).delete()
    db.delete(product)
    db.commit()
    
    return {"message": "Product deleted successfully"}


@router.get("/admin/orders")
async def get_all_orders(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all orders (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    query = db.query(Order)
    
    if status:
        try:
            status_enum = OrderStatus(status)
            query = query.filter(Order.status == status_enum)
        except ValueError:
            pass
    
    total = query.count()
    orders = query.order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "orders": [
            {
                "id": order.id,
                "user_id": order.user_id,
                "user_email": order.user.email if order.user else "Unknown",
                "total_amount": order.total_amount,
                "status": order.status.value,
                "shipping_address": order.shipping_address,
                "phone": order.phone,
                "created_at": order.created_at.isoformat(),
                "item_count": len(order.items),
                "items": [
                    {
                        "name": item.product.name,
                        "quantity": item.quantity,
                        "price": item.price
                    }
                    for item in order.items
                ]
            }
            for order in orders
        ]
    }


@router.put("/admin/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update order status (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    try:
        order.status = OrderStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    db.commit()
    
    return {"message": f"Order status updated to {status}"}

