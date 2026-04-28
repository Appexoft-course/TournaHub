from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.logging import setup_logging

logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")
    yield
    logger.info("Shutting down...")

app = FastAPI(lifespan=lifespan)