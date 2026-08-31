# 🎓 TechUni AI Admissions Assistant (RAG with Python & Telegram)

An intelligent University Admissions Assistant powered by **Retrieval-Augmented Generation (RAG)** in Python, exposing a **FastAPI** backend and direct **Telegram Bot** channel integration. The assistant responds accurately to prospective students' inquiries regarding schedules, tuition, program levels, admissions requirements, certifications, and modalities, strictly adhering to internal business documents and escalating out-of-scope questions to human staff.

---

## 📌 Features

- **Document Grounding (RAG)**: Ingests, chunks, and indexes official business documents into **ChromaDB** using vector embeddings.
- **Strict Anti-Hallucination**: System prompt designed with brand guidelines, anti-hallucination restrictions, and **3 few-shot examples**.
- **Human Escalation Workflow**: Automatically detects out-of-scope questions or missing information, routing the user to human admissions counselors with direct contact details.
- **Dual Channels**:
  - **Telegram Bot** (`python-telegram-bot`) for direct prospective student messaging.
  - **REST API** (`FastAPI`) with `/api/query`, `/api/ingest`, and `/health` endpoints.
- **Production-Ready & Modular**: Clean separation of concerns (`config`, `ingestion`, `rag_engine`, `bot`, `main`).

---

## 🏛️ System Architecture

```
                                  +-----------------------+
                                  | Business Documents    |
                                  | (data/*.md, *.txt)    |
                                  +-----------+-----------+
                                              |
                                              v (Ingestion & Chunking)
                                  +-----------------------+
                                  | OpenAI Embeddings     |
                                  +-----------+-----------+
                                              |
                                              v
+------------------+              +-----------------------+
|  Telegram User   | <----+       | Vector DB (ChromaDB)  |
+------------------+      |       +-----------+-----------+
                          |                   |
                          v                   v (Semantic Search)
                  +---------------+   +---------------+
                  | Telegram Bot  |-->|  RAG Engine   |
                  |  (python-tg)  |   | (LangChain +  |
                  +---------------+   |  OpenAI LLM)  |
                          ^           +-------+-------+
                          |                   |
+------------------+      |                   v
| HTTP / REST API  |------+           +---------------+
| (FastAPI /docs)  |                  | In Scope?     |
+------------------+                  +-------+-------+
                                       /             \
                                (Yes) /               \ (No)
                                     v                 v
                          +---------------+   +-------------------+
                          | Factual Brand |   | Human Escalation  |
                          | Admissions    |   | Contact Details   |
                          | Response      |   | (Email & Phone)   |
                          +---------------+   +-------------------+
```

---

## 📂 Project Structure

```
Simulacro PruebaDesempeño/
├── data/                                 # Official business documents
│   ├── admissions_and_pricing.md        # Tuition, fees, scholarships, refund policies
│   ├── programs_and_levels.md           # Academic programs, curriculums, levels
│   └── schedules_and_certifications.md  # Schedules, modalities, diplomas & certifications
├── src/
│   ├── __init__.py
│   ├── config.py                        # Centralized configuration & environment loader
│   ├── ingestion.py                     # Document loader, chunking & ChromaDB vectorizer
│   ├── rag_engine.py                    # RAG pipeline, system prompt, few-shots & escalation
│   ├── bot.py                           # Telegram Bot event handlers & polling runner
│   └── main.py                          # FastAPI application & server lifecycle
├── .env.example                         # Environment variables template
├── .gitignore                           # Git ignore definitions
├── example.pdf                          # Performance test requirements
├── requirements.txt                     # Project dependencies
└── README.md                            # Complete documentation in English
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed.
- **Google Gemini API Key** (Free from [Google AI Studio](https://aistudio.google.com/)) OR OpenAI API Key.
- Telegram Bot Token (obtained from [@BotFather](https://t.me/BotFather)).

### 2. Environment Setup

1. Clone or open the repository folder.
2. Create and activate a Python virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv venv
   .\venv\Scripts\Activate.ps1

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and fill in your keys:
```ini
# Google Gemini Configuration (Recommended - Free Tier)
GOOGLE_API_KEY=AIzaSy...your_gemini_key_here
GEMINI_MODEL_NAME=gemini-1.5-flash
GEMINI_EMBEDDING_MODEL=models/text-embedding-004

# Active LLM Provider
LLM_PROVIDER=gemini

# Telegram Bot (From @BotFather)
TELEGRAM_BOT_TOKEN=123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ

# Server Settings
APP_HOST=0.0.0.0
APP_PORT=8000
VECTOR_DB_DIR=./chroma_db
SIMILARITY_THRESHOLD=0.65
HUMAN_SUPPORT_EMAIL=admissions-support@techuniversity.edu
HUMAN_SUPPORT_PHONE=+1 (800) 555-0199
```

---

## 🤖 Creating Your Telegram Bot with @BotFather

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Send `/newbot` and follow the on-screen instructions:
   - Choose a friendly display name (e.g. `TechUni Admissions Bot`).
   - Choose a unique username ending in `bot` (e.g. `techuni_admissions_bot`).
3. Copy the **HTTP API Token** provided by BotFather.
4. Paste it into your `.env` file under `TELEGRAM_BOT_TOKEN`.

---

## 📚 Ingesting Business Documents

Before querying, populate the ChromaDB vector database with the documents located in `data/`:

```bash
python -m src.ingestion
```

*Output:*
```
Loaded document: admissions_and_pricing.md (1840 characters)
Loaded document: programs_and_levels.md (1960 characters)
Loaded document: schedules_and_certifications.md (1750 characters)
Split 3 documents into 9 chunks.
Persisting vector database to ./chroma_db...
Ingestion completed successfully!
```

---

## 🌐 Running the Application

### Option A: Run Full Application (FastAPI + Telegram Bot in Background)

```bash
uvicorn src.main:app --reload --reload-dir src
```
*(Or run directly via Python: `python -m src.main`)*
- Interactive Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/health](http://localhost:8000/health)
- The Telegram Bot will automatically start listening for messages in the background.

### Option B: Run Standalone Telegram Bot

If you only want to run the Telegram Bot:
```bash
python -m src.bot
```

---

## 🧪 Testing & Query Examples

### 1. In-Scope Query (Tuition & Discounts)
- **User Query**: *"What are the tuition fees and payment options for AI Engineering?"*
- **Response**:
  > For the **AI Engineering Program**, we offer the following payment options:
  > - **Upfront Payment**: $3,200 USD.
  > - **Installment Plan**: 4 monthly payments of $850 USD (Total: $3,400 USD).
  > - **Income Share Agreement (ISA)**: 12% of gross monthly salary once you secure a tech job earning at least $1,500 USD/month (capped at $4,500 USD).
  > 
  > Additionally, you can benefit from our **Early Bird Discount of 15%** if you register at least 30 days before the cohort start date!

### 2. In-Scope Query (Schedules & Modalities)
- **User Query**: *"Do you have evening classes for working professionals?"*
- **Response**:
  > Yes! We offer a **Part-Time Evening Cohort** (Monday to Thursday, 6:00 PM – 9:30 PM, plus Saturday 9:00 AM – 1:00 PM UTC-5) in a 100% Live Online format with daily mentor office hours.

### 3. Out-of-Scope Query (Automatic Human Escalation)
- **User Query**: *"Can I enroll in a culinary arts or dentistry degree?"*
- **Response**:
  > I'm sorry, but I don't have enough specific information in our official records to answer that accurately. To make sure you get the best guidance, I have escalated your inquiry to our human admissions team.
  > 
  > 👩‍💼 **Admissions Support Contact:**
  > 📧 Email: `admissions-support@techuniversity.edu`
  > 📞 Phone/WhatsApp: `+1 (800) 555-0199`
  > ⏰ Hours: Monday - Friday, 8:00 AM - 6:00 PM (UTC-5)
  > 
  > An admissions specialist will be happy to assist you directly!

---

## 📡 REST API Documentation

### `POST /api/query`
Send a question to the assistant.

**Request:**
```bash
curl -X POST "http://localhost:8000/api/query" \
     -H "Content-Type: application/json" \
     -d '{"query": "What are the requirements for graduation and diplomas?"}'
```

**Response:**
```json
{
  "query": "What are the requirements for graduation and diplomas?",
  "answer": "To earn the official Professional Tech Specialist Diploma, you must achieve a minimum of 85% attendance across all live modules, obtain a passing grade (>= 80%) on all weekly assessments and final Capstone Project, and successfully defend your final project before the evaluation panel.",
  "escalated": false,
  "sources": [
    "schedules_and_certifications.md"
  ]
}
```

### `POST /api/ingest`
Trigger ingestion of new/modified documents dynamically.

---

## 🛡️ Acceptance Criteria Checklist

- [x] **Backend in Python**: Modular FastAPI code orchestrating LLM, embeddings, and ChromaDB.
- [x] **Populated Vector Store**: Ingests and chunks 3+ comprehensive business documents with overlap.
- [x] **Input Channel**: Telegram Bot integration with interactive responses and typing feedback.
- [x] **No n8n Required**: Python pipeline connecting triggers, semantic retrieval, and generation.
- [x] **Prompt Engineering**: System prompt with role, brand tone, anti-hallucination rules, and 3 few-shot examples.
- [x] **Human Escalation**: Automatic escalation when questions are out of scope.
- [x] **Secure Configuration**: API keys loaded via environment variables; never hardcoded.
- [x] **Language**: All code, prompts, and documentation in English.
