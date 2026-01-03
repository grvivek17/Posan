from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from api.v1.routers import forecast, auth, orders, menu, admin, preorder, ai_concierge
import os

app = FastAPI(
    title="Smart Food Court API",
    description="FastAPI backend for Smart Food Court System",
    version="1.0.0",
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(menu.router, prefix="/api/v1/menu", tags=["menu"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(preorder.router, prefix="/api/v1/preorder", tags=["preorder"])
app.include_router(ai_concierge.router, prefix="/api/v1/ai", tags=["ai"])

@app.get("/")
async def root():
    return FileResponse("static/index.html")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
