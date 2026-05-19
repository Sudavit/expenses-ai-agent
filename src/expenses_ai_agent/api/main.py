from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from expenses_ai_agent.api.deps import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle handler."""
    # Startup: create database tables
    SQLModel.metadata.create_all(engine)
    yield
    # Shutdown: cleanup resources (if needed)


app = FastAPI(
    title="Expense API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
