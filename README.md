# Language Academy AI Admissions Assistant (Multilingual RAG with Python, Gemini & Web Form)

An enterprise-grade customer support assistant designed for a **Colombian Language Academy** (*Academia de Idiomas*). The system is built with **Retrieval-Augmented Generation (RAG)** in Python, combining **FastAPI**, **ChromaDB**, **Google Gemini**, and a responsive **Web Form UI**.

The assistant automatically handles inquiries regarding **language programs, levels (CEFR), schedules, tuition in Colombian Pesos (COP), payment plans, international certifications, and campus modalities**, while strictly adhering to business documents, supporting cross-lingual semantic queries, and escalating out-of-scope requests to human advisors.

---

## Key Highlights & Features

1. **Interactive Web Form Interface (`frontend/index.html`)**:
   - Modern, responsive Single Page Application (SPA) served directly at `http://localhost:8000/`.
   - Clean view navigation across Assistant, Programs, Schedules, and Campuses.
   - Dedicated contextual modals for **Tuition Quotation Calculator (COP)** and **Direct Human Advisor Contact**.

2. **Procedural Document Generation & Knowledge Base (`generate_documents.py`)**:
   - Generates 3 comprehensive, realistic business documents in `data/`:
     - `programs_and_levels.md`: English, French, German, Italian, Portuguese tracks, CEFR levels (A1 to C2), placement test details, age requirements, and included materials.
     - `admissions_and_pricing.md`: Official tuition rates in COP, installment options, corporate discounts (Compensar, Colsubsidio, Comfama), and payment troubleshooting (PSE daily transfer limits, banking vouchers, corporate electronic invoicing).
     - `schedules_and_certifications.md`: Shifts, physical campuses in Bogotá and Medellín, live online class access troubleshooting (missing Zoom/Meet links, spam folder, student portal, WhatsApp groups), freezing policies, and refunds.

3. **Zero-Latency Intent Router (`backend/src/intent_router.py`)**:
   - Classifies conversational intents locally in `< 1 ms` (greetings with typos like `"ola"`, user disinterest/rejection, farewells, gratitude, inappropriate/troll filters, and explicit human requests).
   - Responds instantly with `$0.00` API cost and 0 token consumption for common conversational flows.

4. **Multilingual & Cross-Lingual Semantic Retrieval**:
   - Powered by Google Gemini multilingual embeddings (`gemini-embedding-001`).
   - Concepts in different languages share the same high-dimensional semantic vector space.

5. **Proactive Troubleshooting & Anti-Saturating Support**:
   - Solves payment errors (PSE transfer limits, Nequi/Daviplata vouchers), platform links, and admissions rules autonomously.
   - Restricts human advisor escalation strictly to legitimate edge cases (critical billing disputes, custom enterprise contracts) or explicit human contact requests, eliminating admissions desk saturation.

6. **Operational Telemetry & Cost Metrics (Bonus Feature)**:
   - Tracks total queries processed, cache hit rate, escalation rate, token usage, and accumulated financial cost in USD.
   - Accessible via `GET /api/metrics` and the live telemetry API.

7. **Dual-Tier Response Cache (Bonus Feature)**:
   - Exact hash cache + Semantic similarity cache (cosine similarity >= 0.92).
   - Reduces response latency to < 1 ms and API cost to $0.00 for repeated or semantically equivalent questions.

8. **Custom Skills & MCP Server (Bonus Feature)**:
   - Tuition quotation calculator with discounts (`/api/skills/quote`).
   - Free placement test scheduling (`/api/skills/placement`).
   - Model Context Protocol (MCP) server in `backend/src/mcp_server.py`.

9. **Cloud & Container Ready (Bonus Feature)**:
   - Includes `Dockerfile`, `docker-compose.yml`, `render.yaml`, and `Procfile`.

---

## System Architecture

```
                                +-----------------------------------+
                                |     Business Markdown Docs        |
                                |       (data/*.md in COP)          |
                                +-----------------+-----------------+
                                                  |
                                                  v (Chunking with Overlap)
                                +-----------------------------------+
                                |    Gemini Multilingual Embeddings |
                                |      (gemini-embedding-001)       |
                                +-----------------+-----------------+
                                                  |
                                                  v
+------------------+            +-----------------------------------+
|  Student / Lead  | <----+     |       ChromaDB Vector Store       |
+------------------+      |     +-----------------+-----------------+
        |                 |                       |
        v                 |                       v (Semantic Search)
+------------------+      |               +---------------+
| Web Form (UI) /  |----->+-------------->|  RAG Engine   |
| REST API Client  |                      | (LangChain +  |
| (FastAPI :8000)  |                      |  Gemini LLM)  |
+------------------+                      +-------+-------+
                                                  |
                                                  v
                                          +---------------+
                                          | Scope Filter  |
                                          +-------+-------+
                                           /             \
                                    (Yes) /               \ (No / Inappropriate)
                                         v                 v
                              +------------------+  +-------------------+
                              | Factual Response |  | Scope Boundary /  |
                              | in User Language |  | Human Escalation  |
                              +------------------+  +-------------------+
```

---

## Project Structure

```
chatbot-university/
├── data/                                    # Official business knowledge base
│   ├── admissions_and_pricing.md           # Tuition in COP, installment plans, discounts, payments
│   ├── programs_and_levels.md              # Language tracks, CEFR progression (A1-C2), academic FAQ
│   └── schedules_and_certifications.md     # Shifts, campuses, class link troubleshooting, policies
├── frontend/                                # Client-side presentation layer (UI)
│   └── index.html                           # Language Academy educational portal & assistant
├── backend/                                 # Server-side architecture (Python / FastAPI)
│   ├── requirements.txt                     # Backend dependencies
│   └── src/
│       ├── __init__.py
│       ├── config.py                       # Configuration & environment loader
│       ├── generate_documents.py           # Procedural business document generator
│       ├── ingestion.py                    # Chunking, embeddings & vector persistence
│       ├── intent_router.py                # Zero-latency local intent & boundary router
│       ├── rag_engine.py                   # RAG pipeline, cross-lingual prompt & few-shots
│       ├── catalog_service.py              # Dynamic business catalog extractor
│       ├── cache.py                        # Exact hash & semantic similarity cache
│       ├── metrics.py                      # Operational & financial telemetry
│       ├── skills.py                       # Tuition calculator, test scheduler
│       ├── mcp_server.py                   # Model Context Protocol (MCP) server
│       └── main.py                         # FastAPI server & endpoints
├── docs/                                   # Rigorous technical documentation
│   ├── 01-product/PRD.md                   # Product requirements & user stories
│   ├── 03-architecture/system-architecture.md # Technical design & data flows
│   └── 05-ai/rag-and-prompt-engineering.md # Embedding space & prompt engineering
├── .env.example                            # Environment variables template
├── Dockerfile                              # Production container image
├── docker-compose.yml                      # Container orchestration
├── generate_documents.py                   # Root runner for document generation
├── render.yaml                             # 1-Click cloud deployment on Render
├── Procfile                                # PaaS runner for Railway / Heroku
├── requirements.txt                        # Root dependencies pointer
└── README.md                               # Complete project documentation
```

---

## Quick Start Guide

### 1. Prerequisites
- Python 3.10+ installed.
- Git installed.
- **Google Gemini API Key** (Free tier from [Google AI Studio](https://aistudio.google.com/)).

### 2. Clone the Repository

```bash
git clone https://github.com/EdgarCorzo777/prueba-languageacademy.git
cd prueba-languageacademy
```

### 3. Environment Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # Linux / macOS
# .\venv\Scripts\Activate.ps1 # Windows

# 2. Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment Variables


Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` and configure your API key:
```ini
# Google Gemini Settings (Free Tier)
GOOGLE_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

# Application Server Settings
APP_HOST=0.0.0.0
APP_PORT=8000
VECTOR_DB_DIR=./chroma_db
CACHE_ENABLED=true
```

### 5. Generate Business Documents

Generate the Colombian Language Academy documents procedurally:
```bash
python generate_documents.py
```

### 6. Ingest Documents into Vector Database


Populate ChromaDB with chunked embeddings:
```bash
python -m backend.src.ingestion
```

---

## Running the Application

### Start the Server (Web Form & REST API):

```bash
python -m backend.src.main
```
*(Or `uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload`)*

Once started, open your browser:
- **Interactive Web Form UI**: [http://localhost:8000/](http://localhost:8000/)
- **Swagger REST API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Live Metrics JSON**: [http://localhost:8000/api/metrics](http://localhost:8000/api/metrics)
- **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

### Running with Docker:

```bash
docker-compose up --build
```

---

## Testing & Validation Examples

### 1. In-Scope Query (Spanish - Tuition & Discounts)
- **Query**: *¿Cuánto cuesta el curso de inglés y qué descuentos tienen con Compensar?*
- **Response**:
  > ¡Hola! Con gusto te comparto los valores oficiales de nuestros programas de inglés y los beneficios del convenio con la caja de compensación **Compensar**:
  > 
  > - **Programa Estándar (1 Nivel / 16 semanas - 96 horas)**:
  >   - **Pago de contado**: $1,450,000 COP por nivel.
  >   - **Plan financiado**: 4 cuotas mensuales de $395,000 COP (Total: $1,580,000 COP).
  > - **Descuento Compensar**:
  >   - Afiliados Categoría A: **20% de descuento**.
  >   - Afiliados Categoría B: **15% de descuento**.

### 2. Operational Troubleshooting (Payment Issue via PSE)
- **Query**: *Tengo un problema con el pago de PSE, me sale rechazado*
- **Response**:
  > Lamento el inconveniente con tu pago por PSE. Este rechazo suele deberse a situaciones muy comunes que puedes solucionar rápidamente:
  > 1. **Topes diarios de transferencia en tu app bancaria:** En Colombia (Bancolombia, Davivienda, etc.), el límite diario por defecto para PSE suele ser de $1,000,000 COP. Ingresa a tu app y sube temporalmente el tope.
  > 2. **Fondos disponibles:** Verifica que tu saldo cubra el valor total.
  > 3. **Alternativas:** Puedes elegir el **Plan en 4 Cuotas de $395,000 COP** o pagar directamente por **Nequi / Daviplata**.

### 3. Cross-Lingual In-Scope Query (English - Schedules & Saturdays)
- **Query**: *Tell me about the schedule and if I can take classes on Saturdays.*
- **Response**:
  > Hello! Yes, you can absolutely take classes on Saturdays. We offer flexible schedule options:
  > - **Saturday Intensive Shift**: Saturdays, 8:00 AM to 1:00 PM or 1:30 PM to 6:30 PM (COT / UTC-5).
  > - **Weekday Shifts**: Morning (7:00-8:30 AM or 9:00-11:00 AM), Afternoon, and Evening (6:30-8:30 PM).

### 4. Respectful Disinterest / Negative Intent (Zero Latency - No Escalation)
- **Query**: *no quiero que me asesores, no me interesa*
- **Response**:
  > Entendido, no hay ningún problema. Si en algún momento necesitas información sobre los programas de idiomas, horarios o tarifas de **Language Academy**, aquí estaré a tu disposición. ¡Que tengas un excelente día!

### 5. Legitimate Human Escalation (Explicit Contact Request)
- **Query**: *Por favor pásame a un asesor humano de admisiones*
- **Response**:
  > ¡Con mucho gusto! Te pongo en contacto directo con nuestro equipo de admisiones de **Language Academy**:
  > 
  > **Canales Oficiales de Atención:**
  > - **WhatsApp / Teléfono Móvil:** [+57 (300) 123-4567](https://wa.me/573001234567)
  > - **Correo de Admisiones:** `admisiones@languageacademy.edu.co`
  > - **PBX Bogotá:** +57 (601) 745-8900
  > - **Horario de Atención:** Lunes a Viernes de 8:00 AM a 6:00 PM | Sábados de 8:00 AM a 1:00 PM (Hora Colombia)

### 6. Cache Verification
- Submitting the same question a second time returns `cached: true` with a response time of < 1 ms and $0.00 API cost.

---

## REST API Reference

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/` | `GET` | Serves the interactive Single Page Web Form application. |
| `/api/query` | `POST` | Process admissions query with RAG, caching, and escalation. |
| `/api/catalog` | `GET` | Dynamic business catalog extracted directly from markdown docs. |
| `/api/metrics` | `GET` | Retrieve live operational telemetry, token counts, and costs. |
| `/api/metrics/reset` | `POST` | Reset operational telemetry counters. |
| `/api/cache/stats` | `GET` | Check exact and semantic response cache statistics. |
| `/api/cache/clear` | `POST` | Flush response cache entries. |
| `/api/skills/quote` | `POST` | Calculate custom tuition quote in COP with discounts. |
| `/api/skills/placement` | `POST` | Book a free language diagnostic placement test. |
| `/api/ingest` | `POST` | Trigger background document reindexing into ChromaDB. |
| `/health` | `GET` | Service readiness and dependency health status. |

---

## Acceptance Criteria Checklist

- [x] **Reception Channel**: Interactive Responsive Web Form + REST API (`FastAPI`).
- [x] **AI Model Integration**: Integrated with Google Gemini (`gemini-3.5-flash-lite` / `gemini-embedding-001`) for low latency and high cost efficiency.
- [x] **Procedural Documents**: `.py` script (`generate_documents.py`) creating the 3 rich business documents for the Colombian Language Academy in COP.
- [x] **RAG Vector Base**: Ingests, chunks (with overlap), and embeds documents into ChromaDB.
- [x] **Cross-Lingual Support**: Native cross-lingual semantic retrieval across English, Spanish, and French.
- [x] **Prompt Engineering**: System prompt with brand voice, anti-hallucination rules, and few-shot examples.
- [x] **Human Escalation**: Deterministic fallback and human advisor contact routing when out of scope.
- [x] **Bonus 1 - Custom Skills & MCP**: Tuition calculator, placement test scheduler, and MCP server (`backend/src/mcp_server.py`).
- [x] **Bonus 2 - Metrics**: Real-time queries, token counts, cost in USD, and escalation rate tracking (`/api/metrics`).
- [x] **Bonus 3 - Response Cache**: Dual exact and semantic cache reducing latency to < 1 ms and eliminating redundant API costs.
- [x] **Bonus 4 - Public Deployment**: `Dockerfile`, `docker-compose.yml`, `render.yaml`, and `Procfile`.
- [x] **Security**: API Keys loaded strictly from `.env`, never hardcoded.
- [x] **Deliverable Documentation**: Full documentation and `README.md` in English without emojis.
