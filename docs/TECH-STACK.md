# AI Live Copilot — Technology Stack

- **Status:** Accepted (V1.1 baseline)
- **Last updated:** 2026-11-16
- **Owner:** XY-code1
- **Related:** [ADR 0001 — V1.1 architecture baseline](adr/0001-v1.1-architecture.md) · [V1.1 scope](product/V1.1-SCOPE.md) · [Architecture baseline](architecture/README.md)

## 1. Purpose

This document defines the full technology stack for AI Live Copilot, organized into eight layers. It is the reference for implementation decisions, onboarding, and progress tracking.

The product is an AI-powered livestream content intelligence platform. It turns product information — URLs, PDFs, images, manual input — into structured product knowledge, competitive insights, and accurate, traceable livestream sales scripts.

Two principles govern every layer:

1. **Shared AI core, industry-specific modules.** Provider-specific behavior must not leak into product-domain services. Travel is the first industry module; beauty, fashion, consumer electronics, and food & beverage are candidates.
2. **Evidence and provenance are first-class.** Generated content must remain traceable to source material across versions. Fact verification is not an optional add-on.

## 2. Architecture at a glance

| # | Layer | Primary technologies | Stage |
|---|---|---|---|
| 1 | Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui | P0 (initialized) |
| 2 | Backend | Python, FastAPI, Pydantic, SQLAlchemy, Alembic | P0 (initialized) |
| 3 | Database | PostgreSQL (system of record), Redis (on demand), pgvector (future) | P0 partial / on demand |
| 4 | AI core | DeepSeek API, Provider Adapter, Structured Output, Prompt Engineering | P0 (in production use) |
| 5 | File processing | PyMuPDF, PaddleOCR Adapter, URL parser | V1.1 |
| 6 | Async tasks | Celery, Redis, background job records | On demand |
| 7 | Infrastructure | Docker, Docker Compose, Git, GitHub, Ruff, ESLint, pytest | P0 (basic) |
| 8 | Desktop & realtime | Tauri 2, Rust, WebView, Cloud ASR, WebSocket, audio capture | Future |

Cross-cutting: AI engineering (prompt management, evaluation, observability) and multi-tenant SaaS (auth, workspaces, data isolation, metering).

## 3. Layer details

### 3.1 Frontend

**Runtime:** `apps/web` — Next.js (App Router), React, TypeScript, Tailwind CSS, shadcn/ui.

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| Next.js | Full-stack React framework, routing, SSR/SSG | SaaS pages and routes in one deployable unit | P0 |
| React | Component-based UI | Ecosystem and hiring surface | P0 |
| TypeScript | Static typing | Type safety across API boundaries | P0 |
| Tailwind CSS | Utility-first styling | Fast, consistent design iteration | P0 |
| shadcn/ui | Copy-in owned UI primitives (table, dialog, form) | Customizable, no heavyweight dependency | P0 |

**Owns:** dashboard/workspace shell, product knowledge base, product import, competitive diff analysis, AI script editor, user and team management, task status views.

> Note: the current `apps/web` is generated from a recent Next.js version with breaking changes. Always consult `node_modules/next/dist/docs/` for the installed version before writing framework code.

### 3.2 Backend

**Runtime:** `apps/api` — Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2.x, Alembic (uv-managed).

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| Python | Backend language | AI/ML ecosystem, velocity | P0 |
| FastAPI | Async API framework | Native Pydantic integration, OpenAPI, async I/O | P0 |
| Pydantic | Validation and structured output | Single source of truth for schemas and LLM output contracts | P0 |
| SQLAlchemy | ORM and query layer | Mature 2.x async support | P0 |
| Alembic | Schema migrations | Versioned, reviewable DDL | P0 |

**Owns:** request handling, orchestration, domain services, data access, and the boundary to the AI core. The backend is the business hub: for a travel PDF upload it receives the file, invokes parsing, calls AI analysis, persists structured results in PostgreSQL, and returns them to the frontend.

### 3.3 Database

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| PostgreSQL | System of record: users, products, competitors, scripts, sources, versions | Relational integrity for structured product data and evidence | P0 |
| Redis | Cache, rate limiting, task coordination | Needed when concurrency/retries/jobs become real | On demand |
| pgvector | Semantic retrieval over product knowledge | Introduce when structured queries no longer suffice | Future |

**Note on RAG:** the first version does not require RAG. Structured product information and competitor comparison are well served by ordinary PostgreSQL queries. Introduce pgvector only when knowledge scale and semantic search demand it. This keeps the initial data model honest and avoids a premature vector dependency.

### 3.4 AI core

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| DeepSeek API | First model provider | Capable and cost-effective for Chinese-language content | In use (5 services) |
| Provider Adapter | Unified model interface (`get_provider()`) | Swap providers without rewriting domain services | In use (single entry point) |
| Pydantic Structured Output | Enforce JSON contracts | Fail fast on malformed model output, with bounded retry | In use |
| Prompt Engineering | Extraction, comparison, script, rewrite, verification prompts | Product quality depends on prompt design | In use |

**Call chain (verified):** every AI-backed service goes through the adapter — `app/services/extraction.py`, `comparison_generation.py`, `script_generation.py`, `script_rewrite.py`, and `verification.py` all call `get_provider()` from `app/ai`. No service calls DeepSeek directly or constructs `DeepSeekProvider` itself. Adding a provider means implementing `AIProvider` and updating `get_provider()`.

**Five AI tasks:**

1. Product information extraction.
2. Product attribute and selling-point analysis.
3. Competitive difference analysis.
4. Livestream script generation.
5. Script fact verification (claim → source evidence).

The Provider Adapter is the seam that lets future providers (other Chinese or international models) plug in without touching product code.

### 3.5 File processing and information extraction

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| PyMuPDF | PDF text and layout extraction | Fast, pure-Python-friendly PDF parsing | V1.1 |
| OCR Adapter | PaddleOCR text recognition from images and scans | Travel itineraries and posters are often images | V1.1 |
| Multimodal model | Complex layout and image understanding | OCR alone misses structure and context | To build |
| URL parser | Extract product page content with SSRF and size controls | Link-based import is a primary input | V1.1 |
| Pydantic | Normalize all extractions | One canonical product schema regardless of source | To build |

This layer is a pipeline, not a single model call. For a travel itinerary the system must identify destination, day-by-day itinerary, attractions, hotels, inclusions, and exclusions, then normalize everything into the product data model.

**Open decision:** OCR execution model — local OCR (PaddleOCR/Tesseract), multimodal model reading, or a cloud OCR API. The choice affects cost, accuracy, latency, and compliance, and should be settled before building the pipeline. A pragmatic default is multimodal-first for complex layouts and PyMuPDF text-first for text PDFs, with OCR as fallback.

### 3.6 Async tasks (on demand)

| Technology | Purpose | Why this choice | Stage |
|---|---|---|---|
| Celery | Background task execution | Durable, retryable processing | On demand |
| Redis | Broker and coordination | Already in the optional data layer | On demand |
| Job records | Track task status in PostgreSQL | Frontend needs observable progress | On demand |

**Why:** a 100-page product document cannot be parsed inside a synchronous HTTP request. The flow is: upload → API accepts → create job → Celery worker runs PDF/OCR/AI → results written to PostgreSQL → frontend polls or streams status. Redis and Celery are intentionally deferred until measured workload requires them; the synchronous path ships first.

### 3.7 Infrastructure and engineering

| Technology | Purpose | Stage |
|---|---|---|
| Docker | Containerization of api and web | P0 |
| Docker Compose | Local orchestration (postgres, api, web) | P0 |
| Git / GitHub | Version control and collaboration | P0 |
| Ruff | Python linting | P0 |
| ESLint + `tsc` | Frontend linting and type checking | P0 |
| pytest | Backend tests | P0 (health test only) |

**Not yet present:** CI/CD, structured logging, error monitoring, object storage, backup/restore, Nginx or cloud load balancer, HTTPS termination. These are added when the product moves beyond local development.

### 3.8 Desktop and realtime (future)

| Technology | Purpose |
|---|---|
| Tauri 2 | Windows desktop client |
| Rust | Desktop-native capabilities |
| WebView | Render the existing frontend |
| Cloud ASR | Real-time speech recognition |
| WebSocket | Realtime transport |
| Audio capture | Microphone/system audio input |

Long-term flow: streamer speaks → Windows audio capture → Cloud ASR → transcript → AI context understanding → next-line recommendation → overlay window. This is deliberately outside V1.1.

## 4. AI engineering capabilities

Building this product is as much AI application engineering as full-stack development. The capabilities to develop alongside the features:

| Capability | What it means here | Priority |
|---|---|---|
| LLM engineering | Prompt design, structured output, provider abstraction, retry/validation | P0 — built |
| Multi-tenant SaaS | Email/password JWT auth, workspace isolation, upload/URL security | P0 — built (P6) |
| AI observability | LLM call chain tracing, token cost, latency, failures (Langfuse) | Not built (only JSON request logs + Sentry) |
| AI evaluation | Golden datasets, accuracy/quality metrics, regression evaluation | Not built |
| Prompt management | Prompt versioning, experiments, comparison | Partial (prompts are constants in `app/ai/prompts.py`, no version registry) |
| RAG | Knowledge retrieval, embeddings, vector search (pgvector) | Future — structured queries suffice for V1.1 |

Guidance: do not over-build multi-tenancy in P0. Reserve `user` and `workspace` fields and row ownership; defer full permission systems and billing until the core loop is validated.

## 5. Reference data flow — travel product import

```
Upload (PDF / image / URL)
      ↓
FastAPI receives and validates
      ↓
File processing pipeline (PyMuPDF / OCR / multimodal / URL parser)
      ↓
Normalized product schema (Pydantic)
      ↓
AI core: attribute + selling-point analysis
      ↓
PostgreSQL: product, sources, extraction version
      ↓
Frontend: knowledge base + comparison + script generation + fact check
```

Async variant (when enabled): the HTTP request returns a job id; Celery performs the heavy stages; the frontend polls job status.

## 6. Full inventory

| Category | Technology | Stage |
|---|---|---|
| Frontend framework | Next.js | P0 |
| UI library | React | P0 |
| Frontend language | TypeScript | P0 |
| Styling | Tailwind CSS | P0 |
| UI components | shadcn/ui | P0 |
| Backend language | Python | P0 |
| API framework | FastAPI | P0 |
| Validation | Pydantic | P0 |
| ORM | SQLAlchemy | P0 |
| Migrations | Alembic | P0 |
| Database | PostgreSQL | P0 |
| Cache / broker | Redis | On demand |
| LLM | DeepSeek API | In use |
| Model adapter | Provider Adapter | In use |
| PDF | PyMuPDF | V1.1 |
| OCR | PaddleOCR Adapter | V1.1 |
| Async tasks | Celery | On demand |
| Vector search | pgvector | Future |
| Containerization | Docker / Compose | P0 |
| Desktop | Tauri 2 | Future |
| Desktop core | Rust | Future |
| Speech | Cloud ASR | Future |
| Realtime | WebSocket | Future |
| Testing | pytest, ESLint, tsc | P0 (basic) |

## 7. Sequencing

Execution phases (`P0–P6`) are defined in [`ROADMAP.md`](ROADMAP.md). The `P0/P1/P2` labels used elsewhere in this document are **technology priorities** and are unrelated to those phases.

In short: establish the schema and Alembic migrations from the first model, add structured-output validation with retry/repair for malformed LLM responses, add CI before the codebase grows, and remove template residue. Redis/Celery, pgvector, and desktop/realtime work stay deferred per the phase plan.

## 8. Explicit non-goals for V1.1

- Real-time livestream assistant.
- Windows desktop client (Tauri).
- Cloud ASR.
- Full multi-tenant permission and billing system.

These follow the [development principles](PRINCIPLES.md): cloud-first, no premature desktop client, and traceable AI output.

## 9. Decision record

Architectural decisions live in [`docs/adr/`](adr/). This document is the inventory and sequencing reference; ADRs remain the authority on *why* a decision was made.
