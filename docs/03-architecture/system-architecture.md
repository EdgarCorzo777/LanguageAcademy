# System Architecture & Technical Design

## 1. High-Level Architecture

```
                                +-----------------------------------+
                                |     Business Markdown Docs        |
                                |       (data/*.md in COP)          |
                                +-----------------+-----------------+
                                                  |
                                                  v (Chunking & Overlap)
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

## 2. Component Breakdown

### 2.1 Document Ingestion (`backend/src/ingestion.py` & `generate_documents.py`)
- Reads 3 official business markdown documents from `data/` (`programs_and_levels.md`, `admissions_and_pricing.md`, `schedules_and_certifications.md`).
- Splits content into 500-character chunks with 100-character overlap using `RecursiveCharacterTextSplitter`.
- Generates 3072-dimensional vector embeddings with Google's `gemini-embedding-001`.
- Persists indexed chunks in local `chroma_db`.

### 2.2 Zero-Latency Intent Router (`backend/src/intent_router.py`)
- Sub-millisecond deterministic intent classifier for greetings, disinterest/rejections, gratitude, farewells, inappropriate inputs, and explicit human requests.
- Eliminates unnecessary API token consumption and reduces latency to `< 1 ms` for high-frequency conversational flows.

### 2.3 Dual-Tier Caching System (`backend/src/cache.py`)
- **Tier 1 (Exact Hash Match)**: SHA-256 hash computed from normalized lowercased query. Instant O(1) retrieval with 0 latency.
- **Tier 2 (Semantic Similarity Match)**: Cosine similarity search over cached query vectors with a similarity threshold of >= 0.92.

### 2.4 RAG Inference Engine (`backend/src/rag_engine.py`)
- System prompt containing brand voice, strict grounding guidelines, autonomous troubleshooting instructions, and cross-lingual support.
- Few-shot demonstrations covering pricing in COP, PSE payment resolution, polite off-topic boundaries, and legitimate human escalation.
- Fallback escalation token `[ESCALATE_TO_HUMAN]` triggered strictly for critical administrative/accounting disputes or explicit human requests.

### 2.5 Presentation Layer (`frontend/index.html`)
- Standalone Single Page Application (SPA) with 4 focused views: Assistant, Programs, Schedules, and Campuses.
- Contextual interactive modals for Tuition Calculation in COP and Direct Advisor Contact.
