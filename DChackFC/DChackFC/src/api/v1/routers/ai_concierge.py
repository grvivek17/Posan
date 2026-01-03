from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

# Mock AI responses (ready for Azure OpenAI integration)
DIET_PREFERENCES = {}  # Store user preferences {user_id: {diet_type, allergies, preferences}}

class ChatRequest(BaseModel):
    user_id: int
    message: str
    context: Optional[dict] = None

class RecommendationRequest(BaseModel):
    user_id: int
    diet_preferences: Optional[dict] = None
    current_appetite: Optional[str] = None  # light, moderate, heavy

class SubstitutionRequest(BaseModel):
    item_name: str
    reason: str  # out_of_stock, allergy, preference

class NutritionGenerateRequest(BaseModel):
    item_name: str
    category: str
    ingredients: Optional[List[str]] = None

@router.post("/chat")
async def chat_with_concierge(request: ChatRequest):
    """AI-powered food concierge chat"""
    message = request.message.lower()
    
    # Mock intelligent responses based on keywords
    if "recommend" in message or "suggest" in message:
        response = "Based on your preferences, I'd recommend our Classic Burger with Fries! It's highly rated (4.5⭐) and has 650 calories with 28g protein. Would you like to add it to your cart?"
    elif "vegan" in message or "vegetarian" in message:
        response = "Great choice! We have several vegetarian options. Our Veggie Pizza is very popular with 4.7⭐ rating. It's packed with fresh vegetables and has only 285 calories. Interested?"
    elif "protein" in message or "healthy" in message:
        response = "For a high-protein meal, I suggest our Grilled Chicken Salad (35g protein, 450 cal) or Classic Burger (28g protein, 650 cal). Both are excellent choices!"
    elif "allergy" in message or "allergic" in message:
        response = "I understand you have dietary restrictions. Could you tell me what ingredients you need to avoid? I'll find safe options for you."
    elif "calorie" in message or "diet" in message:
        response = "Looking for something light? Our Fries (365 cal) or Pepperoni Pizza (285 cal per slice) are great options. Need something even lighter?"
    else:
        response = "I'm here to help you find the perfect meal! You can ask me about:\n• Food recommendations based on your diet\n• Nutrition information\n• Allergen-free options\n• High-protein or low-calorie meals\n\nWhat would you like to know?"
    
    return {
        "success": True,
        "response": response,
        "suggestions": [
            {"item_id": 1, "name": "Classic Burger", "reason": "High protein, popular choice"},
            {"item_id": 2, "name": "Fries", "reason": "Great side option"}
        ]
    }

@router.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    """Get personalized food recommendations"""
    
    # Store preferences if provided
    if request.diet_preferences:
        DIET_PREFERENCES[request.user_id] = request.diet_preferences
    
    # Mock recommendations based on appetite
    if request.current_appetite == "light":
        recommendations = [
            {
                "item_id": 2,
                "name": "Fries",
                "reason": "Light option, only 365 calories",
                "match_score": 0.95,
                "nutrition": {"calories": 365, "protein": "4g"}
            }
        ]
    elif request.current_appetite == "heavy":
        recommendations = [
            {
                "item_id": 1,
                "name": "Classic Burger",
                "reason": "Filling meal with high protein (28g)",
                "match_score": 0.92,
                "nutrition": {"calories": 650, "protein": "28g"}
            },
            {
                "item_id": 3,
                "name": "Pepperoni Pizza",
                "reason": "Satisfying and highly rated (4.7⭐)",
                "match_score": 0.88,
                "nutrition": {"calories": 285, "protein": "12g"}
            }
        ]
    else:
        recommendations = [
            {
                "item_id": 1,
                "name": "Classic Burger",
                "reason": "Balanced meal, most popular choice",
                "match_score": 0.90,
                "nutrition": {"calories": 650, "protein": "28g"}
            }
        ]
    
    return {
        "success": True,
        "recommendations": recommendations,
        "personalization_note": "Recommendations based on your appetite and preferences"
    }

@router.post("/substitute")
async def get_substitution(request: SubstitutionRequest):
    """Smart substitution suggester using GenAI"""
    
    # Mock substitution logic
    substitutions = {
        "Classic Burger": [
            {
                "name": "Veggie Burger",
                "reason": "Similar taste profile, vegetarian option",
                "price_diff": 0.0,
                "nutrition_comparison": "Lower calories (450 vs 650), same protein"
            },
            {
                "name": "Chicken Burger",
                "reason": "Lighter alternative, still high protein",
                "price_diff": 1.0,
                "nutrition_comparison": "Lower fat, similar protein"
            }
        ],
        "Pepperoni Pizza": [
            {
                "name": "Margherita Pizza",
                "reason": "Vegetarian option, classic taste",
                "price_diff": -2.0,
                "nutrition_comparison": "Lower calories, less sodium"
            }
        ],
        "Fries": [
            {
                "name": "Sweet Potato Fries",
                "reason": "Healthier alternative, more nutrients",
                "price_diff": 1.5,
                "nutrition_comparison": "More fiber, vitamins A & C"
            }
        ]
    }
    
    item_subs = substitutions.get(request.item_name, [])
    
    if not item_subs:
        # Generic substitution
        item_subs = [
            {
                "name": "Chef's Special",
                "reason": f"Alternative to {request.item_name}",
                "price_diff": 0.0,
                "nutrition_comparison": "Similar nutritional profile"
            }
        ]
    
    return {
        "success": True,
        "original_item": request.item_name,
        "reason": request.reason,
        "substitutions": item_subs,
        "ai_note": "Substitutions selected based on taste profile, nutrition, and availability"
    }

@router.post("/generate-nutrition")
async def generate_nutrition_info(request: NutritionGenerateRequest):
    """Auto-generate nutrition information using AI"""
    
    # Mock AI-generated nutrition based on category and ingredients
    base_nutrition = {
        "Main": {"calories": 600, "protein": "25g", "carbs": "45g", "fat": "30g"},
        "Side": {"calories": 350, "protein": "5g", "carbs": "40g", "fat": "15g"},
        "Drink": {"calories": 150, "protein": "0g", "carbs": "38g", "fat": "0g"},
        "Dessert": {"calories": 400, "protein": "6g", "carbs": "55g", "fat": "18g"}
    }
    
    nutrition = base_nutrition.get(request.category, base_nutrition["Main"])
    
    # Add some variation
    nutrition["calories"] += random.randint(-50, 50)
    
    # Generate detailed info
    detailed_info = {
        **nutrition,
        "fiber": f"{random.randint(2, 8)}g",
        "sodium": f"{random.randint(300, 800)}mg",
        "sugar": f"{random.randint(5, 15)}g",
        "vitamins": ["Vitamin A", "Vitamin C", "Calcium", "Iron"],
        "allergens": ["May contain gluten", "May contain dairy"],
        "description": f"Delicious {request.item_name} made with fresh ingredients",
        "serving_size": "1 serving",
        "ai_generated": True,
        "confidence": 0.85
    }
    
    return {
        "success": True,
        "item_name": request.item_name,
        "nutrition_info": detailed_info,
        "note": "Nutrition information generated by AI. Vendor can update for accuracy."
    }
