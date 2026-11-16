# AI Live Copilot — V1.1 MVP Roadmap

- **Status:** Accepted
- **Last updated:** 2026-11-16
- **Owner:** XY-code1
- **References:** [Development principles](PRINCIPLES.md) · [TECH-STACK.md](TECH-STACK.md) · [V1.1 scope](product/V1.1-SCOPE.md) · [ADR 0001](adr/0001-v1.1-architecture.md) · [ADR 0002](adr/0002-file-processing-and-async-boundaries.md)

> **Naming note:** `P0–P6` below are **development phases** (execution order). They are unrelated to the `P0/P1/P2` priority labels used in [TECH-STACK.md](TECH-STACK.md) for individual technologies.

## 1. Delivery cadence

Build in the order a real SaaS product is built: foundation → usable interface → first business module → differentiation → reliability → deployment. Do not start all business modules at once.

**One phase, one goal. One goal, several verifiable tasks.** A phase is not a single PR; each phase splits into tasks that can be accepted independently.

## 2. Phase overview

| Phase | Name | Status | Deliverable |
|---|---|---|---|
| P0 | Engineering foundation | **Done** | Next.js, FastAPI, PostgreSQL, Provider Adapter, Docker, ADRs |
| P1 | Product interaction & page framework | **In progress** | Design system, navigation, all core pages with mock data |
| P2 | Product knowledge base & ingestion | — | Product CRUD, PDF/image/link/manual import, AI extraction |
| P3 | Product intelligence & competitive comparison | — | Attribute normalization, diff matrix, evidence-backed advantages |
| P4 | AI script workspace | — | DeepSeek script generation, editing, versioning, export |
| P5 | Fact verification & content assets | — | Claim checking, risk wording, traceability, export |
| P6 | Full business loop & deployment | — | Auth, isolation, security, observability, cloud deploy, E2E |

## 3. Phase details

### P0 — Engineering foundation (done)

Monorepo, compose stack (postgres/api/web), FastAPI skeleton, Next.js app, DeepSeek Provider Adapter, ADR 0001/0002, tech stack reference.

**Acceptance:** services build and start; provider adapter exists; architectural decisions recorded. *Met as of 2026-11-16; business features not yet implemented.*

---

### P1 — Product interaction & page framework (in progress)

**Goal:** make the product look and feel like a SaaS workbench. No AI integration yet.

**Progress (2026-11-16):** design tokens + shadcn-style components, AppShell (sidebar + topbar), route group, dashboard and product library sample pages, domain types and mock-data contracts are in place. Remaining: accept the visual direction, then fill the remaining pages.

**Pages:**

| Page | Core content |
|---|---|
| Dashboard | Workbench, quick entries, recent tasks |
| Product Library | Product list, search, filter |
| Product Import | File, link, image, manual input |
| Product Detail | Attributes, source materials |
| Competitive Analysis | Competitor selection, diff view |
| Script Workspace | Script editor |
| Asset Library | Historical analyses, script management |
| Settings | Basic settings |

**Tasks (suggested rounds):**

1. UI design specification → `DESIGN_SYSTEM.md`.
2. Page layout and navigation (sidebar + top workspace bar).
3. Core business pages with Mock Data interactions.
4. UI acceptance pass (fix issues, screenshot review).

**Requirements:** unified UI spec; left nav and top workspace bar; all core pages reachable; empty/loading/error states designed; Mock Data demonstrates the business flow; core pages at least responsively usable on mobile.

**Acceptance:** a user can enter every page from the dashboard and run a simulated flow with no blank pages, dead links, or obvious layout breakage.

---

### P2 — Product knowledge base & ingestion

**Goal:** the first real business module.

**Order:**

1. Product CRUD (create, read, update, delete).
2. Product base info and structured attributes.
3. PDF parsing.
4. Image OCR / multimodal recognition.
5. Product link parsing.
6. Manual entry.
7. AI extraction of product information.
8. Associate raw materials with extraction results.

**Data model must include from day one:** source/evidence pointers, confirmation status (unconfirmed / confirmed / doubtful), and version. Reserve `user_id` and `workspace_id` on every business table even though auth lands in P6.

**Acceptance:** a product can be imported and the UI shows structured attributes **plus** the source document, page reference, and confirmation state. AI must never fabricate missing attributes — gaps are shown as unconfirmed.

---

### P3 — Product intelligence & competitive comparison

**Goal:** the core differentiation module.

**Scope:** link own product with competitors; multi-product comparison; attribute normalization; difference matrix; competitive advantage extraction; missing-information detection; evidence traceability.

**Critical rule:** distinguish **evidence-backed advantages** from **AI-speculated potential advantages**. Speculation must never flow directly into livestream scripts. Model this explicitly (for example `evidence_type` / `is_speculative` fields) so P5 can consume it.

**Acceptance:** uploading an own product and a competitor produces a normalized diff matrix covering price, itinerary, attractions, inclusions, and service standards, with every advantage labeled by evidence type and traceable to source.

---

### P4 — AI script workspace

**Goal:** the stage where the Provider Adapter proves its value.

**Scope:** select product; select competitive analysis; select livestream scenario; select target audience; select script style; DeepSeek generation; AI rewrite and local refinement; save and version; export.

**Use structured output, not a single Markdown blob.** Segment scripts into: opening hook, product introduction, core selling points, differentiation, audience interaction, closing/CTA, risk notes.

**Acceptance:** a user can generate a structured script from a confirmed product, rewrite a section, and see version history.

---

### P5 — Fact verification & content asset management

**Goal:** decide whether the product is trustworthy.

**Scope:** detect unsupported claims; detect price/fee inconsistency; detect exaggerated or absolute wording; detect omitted important restrictions; link scripts to raw product materials; retain history; export content.

**Acceptance:** a verification report per script, where every finding is produced by a rule plus source evidence — not by an LLM's impression. Example categories: fee info (checked), attraction info (checked), shopping arrangements (insufficient source), absolute claims (risk).

---

### P6 — Full business loop & deployment

**Goal:** connect everything and deliver the MVP.

**Business loop:** import → AI parsing → product confirmation → competitive comparison → script generation → fact verification → save & export.

**Engineering:** authentication and workspace permissions; data isolation; API authorization; upload security; logging and exception monitoring; AI timeout/retry/error handling; migration testing; Docker deployment; cloud secrets management; end-to-end tests; user trial.

**Acceptance:** full loop passes E2E; a second user cannot read another workspace's data; deployment runs from compose/cloud with secrets externalized.

## 4. Cross-phase rules

1. **Define the data contract before the UI.** Frontend TypeScript types and API schemas are fixed in P1 and reused in P2+ so mock data does not need rewriting.
2. **Provenance is not retrofitted.** Source, confirmation status, and version live in the P2 schema.
3. **Auth fields early, auth logic late.** `user_id` / `workspace_id` columns in P2; enforcement in P6.
4. **CI from P1.** Lint, type check, and pytest run automatically before the codebase grows.
5. **Evidence over impression.** Every AI-generated advantage or claim carries an evidence type; speculative output is labeled and quarantined from scripts.

## 5. Phase dependencies

```
P0 ──> P1 ──> P2 ──> P3 ──> P4 ──> P5 ──> P6
```

P1's mock data shape must anticipate P2's schema. P2's schema must anticipate P3/P5's evidence fields. P3's evidence labels feed P4 generation and P5 verification. P6 assumes P1–P5 are feature-complete and adds cross-cutting concerns rather than new business modules.
