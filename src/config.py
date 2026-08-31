import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = Path(os.getenv("VECTOR_DB_DIR", str(BASE_DIR / "chroma_db")))

# Embedding Provider: 'local' (Free offline default), 'gemini', or 'openai'
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local")

# Google Gemini Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
_raw_gemini_model = os.getenv("GEMINI_MODEL_NAME", "gemini-3.5-flash-lite")
# Auto-resolve deprecated or unavailable model names
if _raw_gemini_model in ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"]:
    GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"
else:
    GEMINI_MODEL_NAME = _raw_gemini_model

GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo")
OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

# Active LLM Provider: 'gemini' or 'openai'
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini" if GOOGLE_API_KEY else "openai")

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Server Configuration
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8000"))

# RAG & Chunking Parameters
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))

# Human Escalation Contact
HUMAN_SUPPORT_EMAIL = os.getenv("HUMAN_SUPPORT_EMAIL", "admissions-support@techuniversity.edu")
HUMAN_SUPPORT_PHONE = os.getenv("HUMAN_SUPPORT_PHONE", "+1 (800) 555-0199")
