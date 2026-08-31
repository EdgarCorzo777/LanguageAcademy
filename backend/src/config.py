import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Base paths
SRC_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SRC_DIR.parent
BASE_DIR = BACKEND_DIR.parent

# Ensure project root and backend are in sys.path
for path in [str(BASE_DIR), str(BACKEND_DIR), str(SRC_DIR)]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Load environment variables from .env file at root or backend
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

DATA_DIR = BASE_DIR / "data"
FRONTEND_DIR = BASE_DIR / "frontend"
VECTOR_DB_DIR = Path(os.getenv("VECTOR_DB_DIR", str(BASE_DIR / "chroma_db")))
METRICS_FILE = Path(os.getenv("METRICS_FILE", str(BASE_DIR / "metrics.json")))

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_raw_gemini_model = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash-lite")
if _raw_gemini_model in [
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
]:
    GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"
else:
    GEMINI_MODEL_NAME = _raw_gemini_model

_raw_emb_model = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
if "text-embedding-004" in _raw_emb_model:
    GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
else:
    GEMINI_EMBEDDING_MODEL = _raw_emb_model

# OpenAI Configuration (Optional fallback)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Embedding Provider: 'gemini', 'openai', or 'local'
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "gemini" if GOOGLE_API_KEY else "local")

# Active LLM Provider: 'gemini' or 'openai'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini" if GOOGLE_API_KEY else "openai")

# Server Configuration (Web Form & REST API)
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# RAG & Chunking Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))

# Cache Configuration (Response Caching to reduce API cost & latency)
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() in ["true", "1", "yes"]
CACHE_SIMILARITY_THRESHOLD = float(os.getenv("CACHE_SIMILARITY_THRESHOLD", "0.92"))
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "86400"))

# Academy and Human Escalation Contact
ACADEMY_NAME = os.getenv("ACADEMY_NAME", "Language Academy")
HUMAN_SUPPORT_EMAIL = os.getenv("HUMAN_SUPPORT_EMAIL", "admisiones@languageacademy.edu.co")
HUMAN_SUPPORT_PHONE = os.getenv("HUMAN_SUPPORT_PHONE", "+57 (300) 123-4567")
HUMAN_SUPPORT_HOURS = os.getenv("HUMAN_SUPPORT_HOURS", "Monday - Friday, 8:00 AM - 6:00 PM; Saturday, 8:00 AM - 1:00 PM (COT / UTC-5)")

