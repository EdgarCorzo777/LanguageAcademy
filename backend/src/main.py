import sys
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

try:
    from backend.src.config import (
        APP_HOST,
        APP_PORT,
        LLM_PROVIDER,
        GOOGLE_API_KEY,
        OPENAI_API_KEY,
        VECTOR_DB_DIR,
        FRONTEND_DIR,
        ACADEMY_NAME,
    )
    from backend.src.rag_engine import rag_engine
    from backend.src.metrics import metrics_collector
    from backend.src.cache import response_cache
    from backend.src.skills import calculate_tuition_quote, schedule_placement_test
    from backend.src.catalog_service import extract_catalog_from_documents
except ImportError:
    from src.config import (
        APP_HOST,
        APP_PORT,
        LLM_PROVIDER,
        GOOGLE_API_KEY,
        OPENAI_API_KEY,
        VECTOR_DB_DIR,
        FRONTEND_DIR,
        ACADEMY_NAME,
    )
    from src.rag_engine import rag_engine
    from src.metrics import metrics_collector
    from src.cache import response_cache
    from src.skills import calculate_tuition_quote, schedule_placement_test
    from src.catalog_service import extract_catalog_from_documents

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title=f"{ACADEMY_NAME} Admissions Assistant",
    description="Customer Support AI Assistant with RAG, Multilingual Semantic Retrieval, Web Form, and FastAPI.",
    version="2.1.0",
)

# Mount frontend directory for static assets if needed
if FRONTEND_DIR.exists():
    app.mount("/frontend", StaticFiles(directory=str(FRONTEND_DIR)), name="frontend")


# Request & Response Models
class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Admissions inquiry from student or prospective lead.")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "¿Cuánto cuesta el curso de inglés y qué facilidades de pago tienen?"
            }
        }


class QueryResponse(BaseModel):
    query: str
    answer: str
    escalated: bool
    sources: List[str]
    cached: bool
    latency_ms: float


class TuitionQuoteRequest(BaseModel):
    program_type: str = Field("standard", description="standard, intensive, business, exam_prep")
    payment_plan: str = Field("upfront", description="upfront or installments")
    discount_code: str = Field("none", description="early_bird, compensar_a, colsubsidio_a, comfama_a, student, none")


class PlacementTestRequest(BaseModel):
    student_name: str
    language: str
    modality: str = "online"
    preferred_date: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    academy_name: str
    active_provider: str
    vector_db_ready: bool
    ai_configured: bool
    cache_enabled: bool


@app.get("/", response_class=HTMLResponse, tags=["Web Form"])
async def serve_web_form():
    """Serve the interactive web form UI from frontend/ directory."""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Language Academy Assistant</h1><p>Frontend index.html not found.</p>")



@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint checking service dependencies and readiness."""
    is_ai_ready = bool(GOOGLE_API_KEY) or bool(OPENAI_API_KEY)
    return HealthResponse(
        status="healthy",
        academy_name=ACADEMY_NAME,
        active_provider="gemini" if GOOGLE_API_KEY else ("openai" if OPENAI_API_KEY else "local"),
        vector_db_ready=VECTOR_DB_DIR.exists(),
        ai_configured=is_ai_ready,
        cache_enabled=True,
    )


@app.post("/api/query", response_model=QueryResponse, tags=["RAG"])
async def handle_query(request: QueryRequest):
    """
    Process an admissions query through RAG engine.
    Applies caching, semantic search, anti-hallucination prompt, and escalation.
    """
    try:
        result = rag_engine.query(request.query, channel="web_form")
        return QueryResponse(
            query=request.query,
            answer=result["answer"],
            escalated=result["escalated"],
            sources=result["sources"],
            cached=result.get("cached", False),
            latency_ms=result.get("latency_ms", 0.0),
        )
    except Exception as e:
        logger.error(f"API Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/metrics", tags=["Telemetry & Metrics"])
async def get_metrics():
    """Retrieve operational metrics (queries processed, cost, escalation rate, token consumption)."""
    return metrics_collector.get_metrics()


@app.post("/api/metrics/reset", tags=["Telemetry & Metrics"])
async def reset_metrics():
    """Reset telemetry metrics."""
    metrics_collector.reset()
    return {"status": "success", "message": "Metrics successfully reset."}


@app.get("/api/cache/stats", tags=["Cache"])
async def get_cache_stats():
    """Retrieve response cache statistics."""
    return response_cache.get_stats()


@app.post("/api/cache/clear", tags=["Cache"])
async def clear_cache():
    """Clear all entries in response cache."""
    response_cache.clear()
    return {"status": "success", "message": "Response cache cleared."}


@app.post("/api/skills/quote", tags=["Custom Skills"])
async def calculate_quote(request: TuitionQuoteRequest):
    """Calculate customized tuition quote with discounts and payment plans."""
    return calculate_tuition_quote(
        program_type=request.program_type,
        payment_plan=request.payment_plan,
        discount_code=request.discount_code,
    )


@app.post("/api/skills/placement", tags=["Custom Skills"])
async def register_placement_test(request: PlacementTestRequest):
    """Schedule a free diagnostic placement test for a prospective student."""
    return schedule_placement_test(
        student_name=request.student_name,
        language=request.language,
        modality=request.modality,
        preferred_date=request.preferred_date,
        email=request.email,
        phone=request.phone,
    )


@app.get("/api/catalog", tags=["Catalog & Knowledge Base"])
async def get_dynamic_catalog():
    """Extract and return dynamic catalog of programs, schedules, and campuses from active documents."""
    return extract_catalog_from_documents()


@app.get("/api/knowledge-base", tags=["RAG"])

async def get_knowledge_base():
    """Dynamically scan and list all active business documents loaded in data/."""
    from backend.src.config import DATA_DIR
    docs = []
    if DATA_DIR.exists():
        for file_path in sorted(DATA_DIR.glob("*.md")):
            try:
                content = file_path.read_text(encoding="utf-8")
                first_line = content.splitlines()[0].replace("#", "").strip() if content.splitlines() else file_path.name
                docs.append({
                    "filename": file_path.name,
                    "title": first_line,
                    "size_bytes": file_path.stat().st_size,
                    "char_count": len(content),
                    "modified_at": file_path.stat().st_mtime,
                })
            except Exception as e:
                logger.warning(f"Could not read document {file_path}: {e}")
    return {"total_documents": len(docs), "documents": docs}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.src.main:app", host=APP_HOST, port=APP_PORT, reload=True)
