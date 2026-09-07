# Language Academy Admissions Assistant

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-3776AB?style=flat&logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/FastAPI-0.110%2B-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI 0.110+">
  <img src="https://img.shields.io/badge/Google%20Gemini-3.5%20Flash%20Lite-8E75F4?style=flat&logo=google&logoColor=white" alt="Google Gemini 3.5 Flash Lite">
  <img src="https://img.shields.io/badge/LangChain-0.1%2B-1C3C3C?style=flat&logo=langchain&logoColor=white" alt="LangChain 0.1+">
  <img src="https://img.shields.io/badge/ChromaDB-Vector%20Store-FF6F00?style=flat&logo=databricks&logoColor=white" alt="ChromaDB">
  <img src="https://img.shields.io/badge/Storage-SQLite%20WAL-003B57?style=flat&logo=sqlite&logoColor=white" alt="SQLite WAL">
  <img src="https://img.shields.io/badge/TailwindCSS-3.4-06B6D4?style=flat&logo=tailwindcss&logoColor=white" alt="TailwindCSS 3.4">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" alt="License MIT">
</p>

An enterprise-grade customer support and admissions assistant engineered for a Colombian Language Academy (*Academia de Idiomas*). The system is built with Retrieval-Augmented Generation (RAG) in Python, combining FastAPI, ChromaDB, Google Gemini (Gemini 3.5 Flash Lite & Gemini Embeddings), SQLite relational persistence, Model Context Protocol (MCP) tooling, and an interactive Single Page Web Application (SPA).

The assistant automates inquiries regarding language programs, Common European Framework of Reference for Languages (CEFR) levels, schedules, official tuition fees in Colombian Pesos (COP), financing plans, compensation fund discounts (*Cajas de Compensacion Familiar*), international certifications, and campus modalities. It strictly adheres to official institutional documentation, supports cross-lingual semantic retrieval, and routes edge cases to human admissions advisors.

---

## Architecture Overview

The system implements a decoupled, layered software architecture designed for high availability, low operational costs, and zero-hallucination compliance:

1. **Presentation Layer (Frontend SPA)**:
   - Modern, responsive Single Page Application (`frontend/index.html`) served directly by FastAPI.
   - Includes an institutional Landing Page, interactive Language Catalog cards, Schedule and Campus matrices, an interactive Tuition Calculator in COP, a Diagnostic Placement Test booking modal, and an AI chat interface with query telemetry.
   - Zero-dependency client stack (Tailwind CSS via CDN, Lucide icons, Marked.js for secure Markdown parsing) optimized for instant rendering.

2. **API & Orchestration Layer (FastAPI)**:
   - High-performance asynchronous ASGI web server (`backend/src/main.py`) running on Uvicorn.
   - Pydantic v2 schemas for strict input/output data validation and type safety.
   - RESTful endpoints for RAG queries (`/api/query`), catalog discovery (`/api/catalog`), live telemetry (`/api/metrics`), tuition quoting (`/api/skills/quote`), and placement scheduling (`/api/skills/placement`).

3. **Cognitive & Semantic Engine (RAG Engine)**:
   - Hybrid routing pipeline: queries are first evaluated by a deterministic `IntentRouter` (< 1 ms latency, $0.00 API cost) for greetings, farewells, disinterest, or direct human escalation requests.
   - Dual-tier response caching (`backend/src/cache.py`): exact SHA-256 hash match combined with semantic cosine similarity caching (threshold >= 0.92) to eliminate redundant LLM invocations.
   - Vector Retrieval: LangChain orchestrates similarity search ($k=5$) against ChromaDB embedded with Google Gemini multilingual embeddings (`gemini-embedding-001`).
   - Contextual Generation: Grounded prompt engineering with few-shot examples and strict guardrails preventing speculative answers or unsupported claims.

4. **Persistence Layer (Dual-Store Architecture)**:
   - **Vector Database (ChromaDB)**: Embedded vector store indexing chunked Markdown documents (`programs_and_levels.md`, `admissions_and_pricing.md`, `schedules_and_certifications.md`).
   - **Relational Database (SQLite 3)**: Normalized transactional database (`database/academy.db`, defined in `database/schema.sql`) enforcing ACID compliance, foreign key constraints, cascading policies, and indexes for leads, bookings, quotes, and audit logs.

5. **Model Context Protocol (MCP) & Custom Skills**:
   - Algorithmic tools for deterministic math calculations (tuition discounts with Compensar, Colsubsidio, Comfama up to 20%).
   - Placement test booking automation.
   - Standard MCP server (`backend/src/mcp_server.py`) exposing tools to external AI agents and IDE integrations.

---

## Relational Database Schema

The relational database (`database/academy.db`) models the operational and transactional domain of the academy. It is structured into 8 normalized tables with foreign keys and performance indexes:

```
+--------------------+        +---------------------+        +--------------------+
|     PROGRAMAS      | 1    N |   PROGRAMAS_SEDES   | N    1 |       SEDES        |
+--------------------+--------+---------------------+--------+--------------------+
| id (PK)            |        | id (PK)             |        | id (PK)            |
| codigo (UNIQUE)    |        | programa_id (FK)    |        | nombre             |
| nombre             |        | sede_id (FK)        |        | ciudad             |
| idioma             |        | cupos_disponibles   |        | direccion          |
| nivel_mcer         |        +---------------------+        | modalidad          |
| precio_contado_cop |                                       | telefono           |
+---------+----------+                                       +----+----------+----+
          | 1                                                     | 1        | 1
          |                                                       |          |
          | N                                                   N |          | N
+---------v----------+        +---------------------+             |          |
|    COTIZACIONES    | N    1 |  ESTUDIANTES_LEADS  |<------------+          |
+--------------------+--------+---------------------+                        |
| id (PK)            |        | id (PK)             |                        |
| numero_cotizacion  |        | tipo_documento      |                        |
| programa_id (FK)   |        | numero_documento    |                        |
| estudiante_id (FK) |        | nombre_completo     |                        |
| plan_pago          |        | email (INDEX)       |                        |
| valor_final_cop    |        | telefono            |                        |
+--------------------+        | sede_preferida_id(FK)                        |
                              +----------+----------+                        |
                                         | 1                                 |
                                         |                                   |
                                         | N                               N |
                              +----------v----------+                        |
                              | AGENDAMIENTOS_TEST  |<-----------------------+
                              +---------------------+
                              | id (PK)             |
                              | codigo_confirmacion |
                              | estudiante_id (FK)  |
                              | programa_id (FK)    |
                              | sede_id (FK)        |
                              | modalidad           |
                              | fecha_preferida     |
                              | estado              |
                              +---------------------+
```

### Table Definitions & Roles

1. **`programas`**: Catalogs official academic programs (English, French, German, Italian, Portuguese), CEFR levels, duration in weeks, total instructional hours, and tuition in COP (cash and installment rates).
2. **`sedes`**: Physical campuses (Chapinero, Calle 100 in Bogota; El Poblado, Laureles in Medellin) and the 100% live Online Campus.
3. **`programas_sedes`**: Associative junction table resolving Many-to-Many (M:N) relationships between academic offerings and authorized campus locations.
4. **`estudiantes_leads`**: Master registry of prospective and active students, tracking contact information, identification, and preferred campus.
5. **`agendamientos_test`**: Placement test bookings with unique confirmation codes (`TEST-YYYYMM-XXXXXX`), scheduled dates, modalities, and campus assignments.
6. **`cotizaciones`**: Historical record of tuition calculations generated via the interactive quoter or API, storing payment plans and applied corporate discounts.
7. **`tickets_escalamiento`**: Audit trail of conversations escalated to human admissions advisors, capturing user questions and escalation reasons.
8. **`transacciones_pagos`**: Transaction ledger tracking payment vouchers, PSE transfer references, and billing verifications.

---

## Directory Tree

```
LanguageAcademy/
├── backend/                                 # Server application
│   ├── requirements.txt                     # Python dependencies
│   └── src/
│       ├── __init__.py                      # Package initialization
│       ├── config.py                        # Environment variables and constants
│       ├── database.py                      # SQLite transactional connection and DAOs
│       ├── generate_documents.py            # Procedural generator for institutional docs
│       ├── ingestion.py                     # Document chunking, embedding, ChromaDB loading
│       ├── intent_router.py                 # Deterministic zero-latency intent classifier
│       ├── rag_engine.py                    # LangChain retrieval pipeline and Gemini LLM
│       ├── catalog_service.py               # Markdown parser for dynamic course catalog
│       ├── cache.py                         # Dual-tier response caching (hash + semantic)
│       ├── metrics.py                       # Operational and financial telemetry tracker
│       ├── skills.py                        # Tuition calculator and placement test scheduler
│       ├── mcp_server.py                    # Model Context Protocol (MCP) server
│       └── main.py                          # FastAPI ASGI application and REST routes
├── frontend/                                # Presentation layer
│   └── index.html                           # Responsive SPA: landing page, catalog, quoter, chat
├── data/                                    # Official institutional knowledge base (Markdown)
│   ├── programs_and_levels.md               # Language tracks, CEFR progression, academic FAQ
│   ├── admissions_and_pricing.md            # Tuition fees in COP, installments, discounts, PSE
│   └── schedules_and_certifications.md      # Timetables, physical/virtual campuses, policies
├── database/                                # Relational storage
│   ├── schema.sql                           # DDL schema script with foreign keys and seed data
│   └── academy.db                           # SQLite database file
├── .env.example                             # Environment variables template
├── .gitignore                               # Git ignored files and directories
├── Dockerfile                               # Production multi-stage container specification
├── docker-compose.yml                       # Docker Compose orchestration
├── generate_documents.py                    # Root entry point to generate business docs
├── requirements.txt                         # Root requirements pointer
└── README.md                                # Comprehensive system documentation
```

---

## Installation and Quick Start

### 1. Prerequisites

- Python 3.10, 3.11, or 3.12 (64-bit).
- Git.
- Google Gemini API Key (free tier available at [Google AI Studio](https://aistudio.google.com/)).

### 2. Clone the Repository

```bash
git clone https://github.com/EdgarCorzo777/LanguageAcademy.git
cd LanguageAcademy
```

### 3. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Open `.env` and set your Google Gemini API key:

```ini
GOOGLE_API_KEY=AIzaSy...your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-3.5-flash-lite
GEMINI_EMBEDDING_MODEL=gemini-embedding-001

APP_HOST=0.0.0.0
APP_PORT=8000
VECTOR_DB_DIR=./chroma_db
CACHE_ENABLED=true
```

### 6. Generate Business Documents

Generate the official institutional Markdown documents:

```bash
python generate_documents.py
```

This creates `programs_and_levels.md`, `admissions_and_pricing.md`, and `schedules_and_certifications.md` in the `data/` directory.

### 7. Ingest Knowledge Base into Vector Database

Process, chunk, and embed the documents into ChromaDB:

```bash
python -m backend.src.ingestion
```

---

## Running the Application

### Local Development Server

Run the application using Python:

```bash
python -m backend.src.main
```

Or using Uvicorn directly:

```bash
uvicorn backend.src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Application URLs

Once the server is running, navigate to:

- **Institutional Web Portal & Assistant**: `http://localhost:8000/`
- **Interactive Swagger REST Documentation**: `http://localhost:8000/docs`
- **ReDoc API Documentation**: `http://localhost:8000/redoc`
- **System Health Status**: `http://localhost:8000/health`
- **Live Telemetry & Cost KPIs**: `http://localhost:8000/api/metrics`

### Running with Docker

Build and start the containerized application with Docker Compose:

```bash
docker-compose up --build
```

The container automatically generates the documents, initializes ChromaDB and SQLite, and starts the FastAPI server on port 8000.

---

## REST API Reference

| Endpoint | Method | Tag | Description |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Web Form | Delivers the Single Page Web Application. |
| `/health` | `GET` | General | Checks service health, vector store presence, and AI configuration. |
| `/api/query` | `POST` | RAG | Processes admissions inquiries with semantic search, few-shots, and guardrails. |
| `/api/catalog` | `GET` | Catalog | Returns dynamically parsed course offerings, schedules, and campuses. |
| `/api/knowledge-base` | `GET` | RAG | Lists active Markdown documents loaded in `data/` with metadata. |
| `/api/skills/quote` | `POST` | Custom Skills | Calculates customized tuition in COP with financing and corporate discounts. |
| `/api/skills/placement` | `POST` | Custom Skills | Schedules a free placement exam and registers the booking in SQLite. |
| `/api/metrics` | `GET` | Telemetry | Returns operational KPIs: query counts, token usage, latency, and costs in USD. |
| `/api/metrics/reset` | `POST` | Telemetry | Resets telemetry counters. |
| `/api/cache/stats` | `GET` | Cache | Returns exact hash and semantic similarity cache hit rates. |
| `/api/cache/clear` | `POST` | Cache | Flushes in-memory cache entries. |

---

## Query Verification and Test Scenarios

### 1. In-Scope Inquiries (Spanish - Pricing and Financing)

- **Input**: *¿Cuánto cuesta el curso de inglés y qué facilidades de pago tienen?*
- **Expected Outcome**:
  - Exact tuition amounts in COP ($1,450,000 COP upfront or 4 installments of $395,000 COP).
  - Discount details for compensation funds (Compensar, Colsubsidio, Comfama: 15% to 20%).
  - Metadata indicates the source document (`admissions_and_pricing.md`) and execution latency.

### 2. Operational Troubleshooting (Payment Rejection)

- **Input**: *Tengo un problema con el pago por PSE, me sale rechazado*
- **Expected Outcome**:
  - Immediate operational guidance explaining daily bank transfer limits in Colombia.
  - Actionable steps to increase daily transfer limits in online banking apps or switch to installment/Nequi alternatives.
  - Zero false escalation to admissions desks.

### 3. Cross-Lingual Semantic Retrieval (English Input)

- **Input**: *Tell me about the available schedules and if I can take classes on Saturdays.*
- **Expected Outcome**:
  - Accurate response in English describing the Saturday Intensive Shift (8:00 AM to 1:00 PM or 1:30 PM to 6:30 PM COT).
  - Retrieved from Spanish-authored institutional documentation via multilingual vector embeddings.

### 4. Zero-Latency Guardrail Routing (Disinterest / Negative Intent)

- **Input**: *no me interesa, no quiero nada*
- **Expected Outcome**:
  - Classifies intent locally within `IntentRouter`.
  - Latency < 1 ms, 0 tokens consumed, $0.00 API cost.
  - Courteous closing message without invoking Google Gemini.

### 5. Deterministic Human Escalation

- **Input**: *Por favor comunícame con un asesor humano de admisiones*
- **Expected Outcome**:
  - Detects explicit human assistance request.
  - Returns official contact channels: WhatsApp (+57 300 123-4567), email (`admisiones@languageacademy.edu.co`), and PBX (+57 601 745-8900).
  - Sets `escalated: true` in response payload for CRM tracking.

### 6. Response Caching Verification

- Submitting the identical question a second time returns `cached: true` with a response latency < 1 ms and zero token consumption.

---

## License

This project is licensed under the MIT License.
