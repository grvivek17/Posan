# Vercel serverless function handler
from app.main import app

# This is required for Vercel to handle the FastAPI app
handler = app
