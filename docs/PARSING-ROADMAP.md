# AI Live Copilot — Parsing Evidence & Quality Roadmap (P7)

- **Status:** Accepted
- **Last updated:** 2026-11-17
- **Owner:** XY-code1
- **References:** [ROADMAP.md](ROADMAP.md) · [PRINCIPLES.md](PRINCIPLES.md) · [TECH-STACK.md](TECH-STACK.md) · [ADR 0002](adr/0002-file-processing-and-async-boundaries.md)

## 1. Purpose

Make the ingestion pipeline **auditable** (where exactly is a fee or restriction lost?) and **regression-safe** (sample corpus, diff reports, specialist checks for fees/itinerary/notes).

The plan is **additive**: existing PDF, image, manual entry, product knowledge base and script generation interfaces are preserved. New tables and a compatibility layer are introduced incrementally; no big-bang rewrite.

## 2. Guiding rules

1. **Every ingestion step is recorded.** Raw snapshot, final URL, redirect chain, content hash, segments, parser version, and an `ingestion_run` id.
2. **Extraction and completeness are separate.** DeepSeek extracts; completeness/scoring is computed by rules (consistent with [P5 fact verification](ROADMAP.md)).
3. **Evidence first.** A fact without an evidence pointer is treated as unconfirmed, not as truth.
4. **Additive migrations.** New tables first; old columns are derived or synced, then deprecated in a later step.

## 3. Phases

### P0 — Evidence & observability

**Goal:** answer "where was the fee information lost?".

**Deliverables**

- `ingestion_run` table: id, source_id, type, started/finished, status, parser version, error.
- Raw page snapshot stored on local disk (persistent volume) with its path recorded.
- Final URL, redirect chain, content hash (SHA-256), and per-segment content captured.
- `run_id` threaded through parsing → extraction → attributes → script → verification.

**Acceptance**

- Every source has a run record with hash and parser version.
- Given a product, the UI/API can show each pipeline stage's input/output and where a field disappeared (parse → extract → attribute → script).
- A missing fee field can be traced to the exact stage in one query.

### P1 — Static deep parsing

**Goal:** extract structure, not just text.

**Deliverables**

- Structured body extraction (headings, lists, paragraphs).
- Table preservation (PyMuPDF `find_tables` / HTML tables → structured rows).
- JSON-LD and safe embedded structured data (schema.org `Product`/`TouristTrip`).
- PDF page discovery + per-page text; image detection with OCR fallback (PaddleOCR, optional dependency).
- Parser version recorded per run (P0).

**Acceptance**

- Tables and per-page text are stored as segments with references.
- Fees/inclusions inside tables are extracted as facts with page/segment evidence.
- OCR fallback is used only for scanned pages; text PDFs skip OCR.

### P2 — Dynamic pages

**Goal:** handle JS-rendered product pages without breaking boundaries.

**Deliverables**

- Content-sufficiency rules (minimum length, key blocks present).
- Playwright **conditional escalation** only when static content is insufficient.
- Scroll and normal expand/collapse handling; network-idle waits.
- Explicit `restricted` status for login-walled/blocked pages.

**Dependencies / risks**

- Playwright adds a browser runtime to the API image; keep it an optional dependency and document the Docker cost.
- SSRF protection from the existing URL validator must also apply to redirected final URLs.

**Acceptance**

- Static-sufficient pages never launch a browser.
- Insufficient pages are retried once with Playwright; restricted pages return a clear status instead of empty content.
- Dynamic fetch honours the same timeout/size limits as static fetch.

### P3 — Unified product facts

**Goal:** one authoritative fact layer with evidence and completeness.

**Deliverables**

- `product_facts` (canonical facts) and `fact_evidence` (fact ↔ source segment).
- Missing / conflicting state per fact.
- Rule-based completeness scoring (fees, inclusions, restrictions, itinerary, notes).
- DeepSeek performs extraction only; it never assigns completeness.

**Migration**

- New tables are authoritative; existing `ProductAttribute` / `ProductSource` fields are derived or synced through a compatibility layer, then deprecated in a later migration.

**Acceptance**

- Every fact has ≥1 evidence pointer or is explicitly `unconfirmed`.
- Conflicts are surfaced, not silently overwritten.
- Completeness is reproducible from rules (no model in the loop).

### P4 — Regression & operations

**Goal:** catch quality regressions before users do.

**Deliverables**

- Real-material sample corpus (PDF/image/URL) with expected facts.
- Parser version management and re-parse on demand.
- Old-vs-new diff report per re-parse.
- Specialist regression for fees, itinerary and important notes.

**Acceptance**

- CI runs the corpus against the current parser and fails on dropped/changed key facts.
- A re-parse produces a diff report (added/removed/changed facts with evidence).
- Fee/itinerary/notes regressions are reported separately.

## 4. Existing interfaces kept

`POST /products/{id}/sources` (PDF/image), `POST /products/{id}/sources/url`, manual attributes, product CRUD, AI extraction, comparison, script generation and verification keep their contracts. P0–P4 add fields/tables behind them.

## 5. Dependency & risk summary

| Phase | Depends on | Main risk |
|---|---|---|
| P0 | existing sources | snapshot storage volume / retention |
| P1 | P0 run metadata | table extraction quality on complex layouts |
| P2 | P1 | Playwright runtime cost and bot-blocked pages |
| P3 | P1 evidence | dual-write consistency during migration |
| P4 | P0–P3 | corpus licensing/privacy of real materials |
