import logging
import asyncio
from contextlib import asynccontextmanager
from typing import List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from src.config import (
    APP_HOST,
    APP_PORT,
    LLM_PROVIDER,
    GOOGLE_API_KEY,
    OPENAI_API_KEY,
    TELEGRAM_BOT_TOKEN,
    VECTOR_DB_DIR,
)
from src.rag_engine import rag_engine
from src.ingestion import ingest_data
from src.bot import create_bot_application

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

bot_task: Optional[asyncio.Task] = None
telegram_app = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global bot_task, telegram_app
    logger.info("Starting up TechUni Admissions RAG API...")

    # Start Telegram Bot polling in background if token is provided
    if TELEGRAM_BOT_TOKEN:
        try:
            telegram_app = create_bot_application()
            if telegram_app:
                await telegram_app.initialize()
                await telegram_app.start()
                await telegram_app.updater.start_polling()
                logger.info("Telegram Bot started in background polling mode.")
        except Exception as e:
            logger.error(f"Failed to start Telegram Bot background runner: {e}")
    else:
        logger.info("TELEGRAM_BOT_TOKEN not provided. Telegram bot runner skipped.")

    yield

    logger.info("Shutting down TechUni Admissions RAG API...")
    if telegram_app and telegram_app.updater:
        try:
            await telegram_app.updater.stop()
            await telegram_app.stop()
            await telegram_app.shutdown()
            logger.info("Telegram Bot cleanly stopped.")
        except Exception as e:
            logger.error(f"Error stopping Telegram Bot: {e}")


app = FastAPI(
    title="TechUni Admissions RAG Assistant API",
    description="Intelligent Admissions Assistant using RAG, FastAPI, ChromaDB, and Telegram Bot integration.",
    version="1.0.0",
    lifespan=lifespan,
)


# Request & Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="The admissions inquiry from the user.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What are the payment options and discounts for AI Engineering?"
            }
        }


class QueryResponse(BaseModel):
    query: str
    answer: str
    escalated: bool
    sources: List[str]


class HealthResponse(BaseModel):
    status: str
    active_provider: str
    vector_db_ready: bool
    ai_configured: bool
    telegram_configured: bool


class IngestResponse(BaseModel):
    status: str
    message: str


@app.get("/", tags=["General"])
async def root():
    """Root welcome endpoint."""
    return {
        "name": "TechUni Admissions RAG Assistant API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint checking service dependencies."""
    is_ai_ready = bool(GOOGLE_API_KEY) or bool(OPENAI_API_KEY)
    return HealthResponse(
        status="healthy",
        active_provider="gemini" if GOOGLE_API_KEY else ("openai" if OPENAI_API_KEY else "none"),
        vector_db_ready=VECTOR_DB_DIR.exists(),
        ai_configured=is_ai_ready,
        telegram_configured=bool(TELEGRAM_BOT_TOKEN),
    )


@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def handle_query(request: QueryRequest):
    """
    Process an admissions query through the RAG engine.
    If information is missing or out of scope, automatically escalates to a human.
    """
    try:
        result = rag_engine.query(request.query)
        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            escalated=result["escalated"],
            sources=result["sources"],
        )
    except Exception as e:
        logger.error(f"API Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ingest", response_model=IngestResponse, tags=["RAG"])
async def trigger_ingestion(background_tasks: BackgroundTasks):
    """Trigger ingestion of documents from data/ into ChromaDB."""
    if not GOOGLE_API_KEY and not OPENAI_API_KEY:
        raise HTTPException(
            status_code=400,
            detail="Neither GOOGLE_API_KEY nor OPENAI_API_KEY is configured in .env file.",
        )

    try:
        background_tasks.add_task(ingest_data)
        return IngestResponse(
            status="accepted",
            message="Document ingestion process started in background.",
        )
    except Exception as e:
        logger.error(f"Error starting ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=APP_HOST, port=APP_PORT, reload=True, reload_dirs=["src"])
