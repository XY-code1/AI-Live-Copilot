# V1.1 Architecture Baseline

AI Live Copilot V1.1 uses a shared AI core with industry-specific modules. Travel is the first industry module.

The full eight-layer technology stack and sequencing live in [`../TECH-STACK.md`](../TECH-STACK.md). This document states the runtime boundaries only.

## Runtime boundaries

- `apps/web`: Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui. Owns all user-facing surfaces: dashboard, product knowledge base, import, competitive analysis, script editor, and user/team management.
- `apps/api`: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic, and the AI provider adapter. Owns request handling, domain services, data access, and the boundary to the AI core.
- PostgreSQL is the system of record: users, products, competitors, scripts, sources, and versions.
- Redis and Celery remain optional until workload evidence requires background processing. The synchronous path ships first; the async seam is designed now and built later.
- File processing is a distinct pipeline layer (URL parser, PyMuPDF, OCR adapter, multimodal model) that normalizes every source into one Pydantic product schema. See [ADR 0002](../adr/0002-file-processing-and-async-boundaries.md).

## MVP boundary

The MVP covers product ingestion, knowledge management, structured analysis, comparison, advantage extraction, script generation, factual verification, editing, and version management.

Real-time livestream assistance, Cloud ASR, and the Tauri desktop client are intentionally outside V1.1 MVP.

## Sequencing principle

Ship one end-to-end vertical slice before broadening: single product import → parse → AI structured extraction → PostgreSQL → frontend display. Then add competitive analysis, script generation, and fact verification.
