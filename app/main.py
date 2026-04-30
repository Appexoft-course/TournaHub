from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging import setup_logging
from app.core.config import settings
from app.api.v1.router import api_router

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

app = FastAPI(
    title="TournaHub",
    lifespan=lifespan        
)

app.include_router(api_router, prefix="/api/v1")