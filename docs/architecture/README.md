# V1.1 Architecture Baseline

AI Live Copilot V1.1 uses a shared AI core with industry-specific modules. Travel is the first industry module.

## Runtime boundaries

- `apps/web`: Next.js, React, TypeScript, Tailwind CSS, and shadcn/ui.
- `apps/api`: FastAPI, SQLAlchemy 2.x, Alembic, and the AI provider adapter.
- PostgreSQL is the system of record.
- Redis and Celery remain optional until workload evidence requires background processing.

## MVP boundary

The MVP covers product ingestion, knowledge management, structured analysis, comparison, advantage extraction, script generation, factual verification, editing, and version management.

Real-time livestream assistance, Cloud ASR, and the Tauri desktop client are intentionally outside V1.1 MVP.

