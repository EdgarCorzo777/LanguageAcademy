# Product Requirements Document (PRD)

## 1. Executive Summary
**Language Academy Admissions Assistant** is an enterprise-grade AI customer support web application designed to resolve repetitive prospective student inquiries for a Colombian Language Academy.


The assistant is strictly grounded on official institutional documents (programs, schedules, COP pricing, certifications, and campus locations), features cross-lingual retrieval capabilities (understanding English, Spanish, and French queries), incorporates automatic human advisor escalation for out-of-scope questions, and tracks operational KPIs in real time through an interactive web interface.

---

## 2. Business Objectives & Problem Statement
- **Problem**: The admissions office is overwhelmed with daily inquiries about class schedules, tuition prices in COP, installment options, international certifications, and enrollment procedures.
- **Goals**:
  - Automate 85%+ of standard admissions queries with 0 hallucinations via an accessible web form.
  - Seamlessly escalate out-of-scope or complex inquiries to human advisors with full contact details.
  - Minimize API operational costs via exact and semantic caching layers.
  - Provide cross-lingual support (prospective students querying in English or Spanish receive accurate factual answers).

---

## 3. Key Functional Features
1. **Multilingual & Cross-Lingual RAG Pipeline**:
   - Ingests 3 core business documents (`programs_and_levels.md`, `admissions_and_pricing.md`, `schedules_and_certifications.md`).
   - Indexes text chunks using Google Gemini multilingual embeddings (`gemini-embedding-001`).
   - Matches queries across languages (e.g. English query "Tell me about the schedules" matches Spanish schedule context).
2. **Strict Grounding & Anti-Hallucination**:
   - Explicit system prompt constraints restricting knowledge strictly to retrieved context chunks.
   - Low temperature generation.
   - 3 few-shot examples illustrating correct pricing, schedule retrieval, and escalation.
3. **Response Caching (Cost & Latency Optimization)**:
   - Dual-tier caching with exact hash and cosine semantic similarity matching.
   - Reduces repeated query latency to < 1 ms and API cost to $0.00.
4. **Telemetry & Operational Metrics**:
   - Tracks total queries, cache hit rate, escalation rate, token usage, and estimated USD cost.
   - Exposed via `/api/metrics` endpoint and live dashboard on the web form.
5. **Custom Skills & MCP Server**:
   - Tuition quotation calculator with discounts (Early bird 15%, Cajas de compensacion 10-20%, Student 10%).
   - Diagnostic placement test scheduler.
   - Standard Model Context Protocol (MCP) server for agent extensibility.
6. **Web Form & REST API Reception Channel**:
   - Interactive responsive web form with question chips, live markdown rendering, latency badges, and skill tabs.
   - FastAPI REST API (`/api/query`, `/api/ingest`, `/health`, `/api/metrics`, `/api/skills/quote`, `/api/skills/placement`).
