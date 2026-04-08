from contextlib import asynccontextmanager
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import profiles, talent_finder, requirements, telecaller
from app.vector_store import get_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Initialize vector store (load from disk)
    get_collection()
    yield

app = FastAPI(title="Talent Management App", lifespan=lifespan)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(profiles.router)
app.include_router(talent_finder.router)
app.include_router(requirements.router)
app.include_router(telecaller.router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
