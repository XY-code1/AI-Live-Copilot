# ADR 0002: file processing and async boundaries

- Status: Accepted
- Date: 2026-11-16
- References: [TECH-STACK.md](../TECH-STACK.md) · [ADR 0001 — V1.1 architecture baseline](0001-v1.1-architecture.md)

## Context

The first industry scenario (travel livestream commerce) imports product information as URLs, PDFs, images, and manual input. Travel itineraries are frequently image-based or scanned, so text extraction alone is insufficient. Large documents also cannot be processed inside a synchronous HTTP request without degrading the user experience.

## Decision

1. **Treat ingestion as a pipeline, not a model call.** Every source funnels into one normalization stage and one canonical product schema (Pydantic), regardless of origin. Stages: URL parser, PyMuPDF (text/layout), OCR adapter, multimodal model for complex layouts.
2. **AI output is a contract.** All model responses are validated against Pydantic schemas. Malformed or partial output triggers a bounded retry/repair path, and validation failure rates are observed.
3. **Evidence is preserved.** Every extracted attribute and every generated claim keeps a pointer to its source fragment so fact verification can trace statements back to the input.
4. **Async is a boundary, not a rewrite.** The API first ships a synchronous flow. Redis and Celery are introduced only when workload evidence requires retries, concurrency control, or durable background jobs; the job record lives in PostgreSQL so the frontend can observe progress.
5. **OCR execution model is decided before implementation.** Choose between local OCR, multimodal reading, and cloud OCR based on cost, accuracy, latency, and compliance. Default direction: text-first with PyMuPDF, multimodal for complex layouts, OCR as fallback.

## Consequences

- Parsing complexity is isolated behind a single ingestion interface, so adding a new source format does not touch domain services.
- Structured-output validation adds a required error-handling path; skipping it is not acceptable.
- Provenance data increases storage and schema complexity, but is the basis of the product's factual-verification claim and cannot be retrofitted cheaply.
- The sync-first path keeps P0 small; the async seam must be designed now and built later.

## Alternatives considered

- **Synchronous-only processing:** rejected for large documents; would couple request latency to AI and OCR time.
- **RAG-first knowledge layer:** deferred; structured relational data is sufficient for V1.1 product and competitor analysis, and pgvector can be introduced later.
- **Cloud OCR only:** viable but locks cost and compliance to a vendor; kept as one option rather than the default.
