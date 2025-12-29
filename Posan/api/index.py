from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.core.config import settings
from app.api.endpoints import auth, users, magazines, puzzles, gamification, ai_content

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Kids Magazine and Puzzle Web Application API",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["Authentication"])
app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["Users"])
app.include_router(magazines.router, prefix=f"{settings.API_V1_PREFIX}/content", tags=["Content"])
app.include_router(puzzles.router, prefix=f"{settings.API_V1_PREFIX}/puzzles", tags=["Puzzles"])
app.include_router(gamification.router, prefix=f"{settings.API_V1_PREFIX}/gamification", tags=["Gamification"])
app.include_router(ai_content.router, prefix=f"{settings.API_V1_PREFIX}/ai", tags=["AI Content Generation"])

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

# Mangum handler for Vercel
handler = Mangum(app)
