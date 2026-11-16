# AI Live Copilot — Development Principles

- **Status:** Binding
- **Last updated:** 2026-11-16
- **Owner:** XY-code1
- **References:** [ROADMAP.md](ROADMAP.md) · [TECH-STACK.md](TECH-STACK.md) · [ADR 0002](adr/0002-file-processing-and-async-boundaries.md)

These three principles are standing constraints on every phase. If a task conflicts with one, the task yields.

## 1. AI output never loses its source

Every piece of AI-generated content — product attributes, competitive differences, script sections — must be traceable to the raw material it came from.

**Why:** traceability is the product's actual value. A script claim without a source is a liability, not an asset.

**Checkpoints:**
- Every extracted attribute, advantage, and script claim carries a source pointer and a confirmation status.
- Missing attributes stay marked unconfirmed; AI must never fill gaps with invention.
- Evidence-backed advantages and AI-speculated advantages are stored and displayed differently.
- A user can click from any AI result to the source document, page, and fragment.

## 2. Cloud-first, no premature desktop client

The web MVP is the product. Windows/Tauri, Rust, and ASR work waits until the core business is stable and usable in the browser.

**Why:** a desktop shell multiplies build, distribution, and maintenance cost before the core loop is proven.

**Checkpoints:**
- No Tauri/Rust/ASR code enters the repository before the web MVP is usable end to end.
- Roadmap phases stay cloud-only until P6 closes and real users have exercised the loop.
- Desktop work is revisited only after the web product has demonstrated the business loop.

## 3. Every phase ships a demoable outcome

Progress is measured by whether a user can complete a real business task, not by lines of code, file counts, or completed tickets.

**Why:** demoable progress is the only signal that survives contact with a real user; activity is not outcomes.

**Checkpoints:**
- Each phase ends with something runnable that can be shown and walked through.
- Acceptance criteria describe user-visible behavior, not implementation effort.
- A phase is not done until its demo covers the phase's core business task.
- Weak or partial results are shown honestly rather than padded with busywork.

## How these bind the plan

- [ROADMAP.md](ROADMAP.md) phases and acceptance criteria must respect all three.
- [TECH-STACK.md](TECH-STACK.md) defers desktop and realtime work accordingly.
- [ADR 0002](adr/0002-file-processing-and-async-boundaries.md) implements principle 1 at the data layer.
