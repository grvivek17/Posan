from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.api.endpoints import auth, users, magazines, puzzles, gamification, ai_content, homework_agents, gamification_v2, podcasts, email, calculator, subscription, admin, store, promotional_email
import app.models.exam  # Ensure exam/assignment tables are created
import os

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Kids Magazine and Puzzle Web Application API",
    version="1.0.0",
    debug=settings.DEBUG
)

# Create static directory for podcast audio files
os.makedirs("static/podcasts", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(magazines.router, prefix=f"{settings.API_V1_PREFIX}/content", tags=["Content"])
app.include_router(podcasts.router, prefix=f"{settings.API_V1_PREFIX}/podcasts", tags=["AI Podcasts"])
app.include_router(email.router, prefix=f"{settings.API_V1_PREFIX}/email", tags=["Email"])
app.include_router(puzzles.router, prefix=f"{settings.API_V1_PREFIX}/puzzles", tags=["Puzzles"])
app.include_router(gamification.router, prefix=f"{settings.API_V1_PREFIX}/gamification", tags=["Gamification"])
app.include_router(gamification_v2.router, prefix=f"{settings.API_V1_PREFIX}/gamification-v2", tags=["Gamification V2"])
app.include_router(ai_content.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Content Generation"])
app.include_router(calculator.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Speaking Calculator"])
app.include_router(subscription.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Subscription"])
app.include_router(admin.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Admin"])
app.include_router(store.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Store"])
app.include_router(homework_agents.router, prefix=f"{settings.API_V1_PREFIX}/homework-agents", tags=["Homework Agents (Multi-Agent System)"])
app.include_router(promotional_email.router, prefix=f"{settings.API_V1_PREFIX}", tags=["Admin Promotional Email"])


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to POSAN API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
