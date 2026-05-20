from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from expenses_ai_agent.api.deps import engine
from expenses_ai_agent.api.routes import analytics, categories, expenses


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

app.include_router(expenses.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/api/v1/health")
async def health():
    return {"status": "ok"}
