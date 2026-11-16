# AI Live Copilot

### AI-Powered Livestream Content Intelligence Platform

AI Live Copilot is an AI-powered platform designed to help livestream creators, e-commerce merchants, and content operations teams transform product information into compelling, accurate, and structured livestream sales content.

It combines product intelligence, competitive analysis, AI-powered script generation, and factual verification into a unified workflow.

**Understand Products. Discover Selling Points. Create Better Livestream Content.**

## Overview

Preparing for a livestream involves more than writing a sales script.

Creators and operators need to understand product information, identify competitive advantages, organize selling points, and ensure that every claim made during a livestream is accurate.

AI Live Copilot aims to streamline this process with AI-powered content intelligence.

The authoritative engineering reference is [`docs/TECH-STACK.md`](docs/TECH-STACK.md) (eight-layer stack, sequencing, and AI engineering capabilities). This README is the product-level introduction.

## Core Capabilities

### 1. Product Intelligence
- Import product information from URLs, PDFs, images, and manual input.
- Extract structured product attributes.
- Organize product specifications, features, and selling points.
- Maintain traceable product information sources.

### 2. Competitive Analysis
- Compare products with competitor offerings.
- Identify product differences and competitive advantages.
- Extract evidence-backed selling points.
- Highlight missing or unverified information.

### 3. AI Script Generation
- Generate livestream sales scripts.
- Create product introduction and selling-point explanations.
- Generate differentiated product positioning.
- Support interactive and conversational scripts.
- Edit, rewrite, and manage script versions.

### 4. Factual Verification
- Verify generated scripts against product information.
- Detect missing fees and important restrictions.
- Identify unsupported marketing claims.
- Link script statements to their supporting sources.

### 5. Livestream Copilot
Planned capabilities:
- Real-time speech recognition.
- Context-aware script recommendations.
- Product selling-point reminders.
- AI-assisted livestream review.

## Industry Scenarios

AI Live Copilot follows a reusable architecture:

**Shared AI Engine + Industry-Specific Modules**

Initial industry scenario:
- Travel Livestream Commerce

Potential future scenarios:
- Beauty & Cosmetics
- Fashion & Apparel
- Consumer Electronics
- Food & Beverage

## Technology Stack

| Layer | Technology | Stage |
|---|---|---|
| Frontend | Next.js, React, TypeScript, Tailwind CSS, shadcn/ui | P0 |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy, Alembic | P0 |
| Database | PostgreSQL | P0 |
| Cache / broker | Redis | On demand |
| Vector search | pgvector | Future |
| AI | DeepSeek API, Provider Adapter, Structured Output | Provider skeleton |
| File processing | PyMuPDF, OCR Adapter, multimodal model, URL parser | To build |
| Async tasks | Celery, Redis, background job records | On demand |
| Infrastructure | Docker, Docker Compose, Git, GitHub, Ruff, ESLint, pytest | P0 (basic) |
| Desktop | Tauri 2, Rust, WebView | Future |
| Speech / realtime | Cloud ASR, WebSocket, audio capture | Future |

See [`docs/TECH-STACK.md`](docs/TECH-STACK.md) for per-layer rationale and the full inventory.

## Repository Layout

```
apps/
  web/    Next.js + React + TypeScript (Tailwind, shadcn/ui)
  api/    FastAPI + SQLAlchemy + Alembic (uv)
docs/
  TECH-STACK.md              Full technology stack and sequencing
  adr/0001-v1.1-architecture.md
  architecture/README.md
  product/V1.1-SCOPE.md
compose.yaml                 postgres + api + web
```

## Product Roadmap

**P0 — foundation and first vertical slice**
- [x] Project infrastructure and development environment
- [ ] First end-to-end slice: product import → parse → AI extraction → PostgreSQL → UI
- [ ] Product data model and Alembic migrations
- [ ] Structured-output validation with retry/repair
- [ ] CI (lint, type check, tests)

**P1 — product depth**
- [ ] Product information management and multi-format import
- [ ] Product intelligence engine
- [ ] Competitive analysis engine
- [ ] AI livestream script generation
- [ ] Script factual verification
- [ ] Script editing and version management
- [ ] OCR / multimodal extraction and async jobs
- [ ] AI evaluation and observability

**P2 — expansion**
- [ ] User authentication and team workspaces
- [ ] pgvector / RAG
- [ ] Windows desktop application (Tauri 2)
- [ ] Real-time livestream assistance (Cloud ASR, WebSocket)

## Product Vision

Our vision is to make AI an intelligent copilot throughout the livestream commerce workflow.

From understanding products to creating persuasive sales content, and eventually assisting creators during live sessions, AI Live Copilot aims to make livestream content preparation more efficient, structured, and reliable.

---

**Project Status:** V1.1 foundation initialized; implementation not yet started. The monorepo, compose stack, and AI provider adapter exist; business features are planned, not built.

**Note:** Features listed in the roadmap are planned capabilities and are not necessarily available in the current version.
