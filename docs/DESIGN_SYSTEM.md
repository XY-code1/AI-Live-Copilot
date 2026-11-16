# AI Live Copilot — Design System

- **Status:** P1 baseline
- **Last updated:** 2026-11-16
- **Owner:** XY-code1
- **References:** [PRINCIPLES.md](PRINCIPLES.md) · [ROADMAP.md](ROADMAP.md) · [TECH-STACK.md](TECH-STACK.md)

## 1. Purpose

This document defines the visual language for the web app: color, typography, spacing, radius, elevation, component usage, and page states. It exists so every P1+ page looks like one product and so future pages can be built from a shared set of tokens instead of ad-hoc styles.

## 2. Design principles

1. **Clarity over decoration.** Dense information (products, comparisons, scripts) must stay readable. Use borders and muted text before color.
2. **Evidence is visible.** Confirmation status (confirmed / unconfirmed / doubtful) and evidence type (source / inferred / speculative) are always shown, never implied.
3. **Neutral base, one accent.** Neutral grayscale carries the interface; the brand indigo is reserved for primary actions, active nav, and key highlights.
4. **Consistency through tokens.** Components consume CSS variables from `globals.css`, never raw hex values.
5. **Responsive by default.** Every page works on mobile first, then scales up.

## 3. Color

Tokens live in `apps/web/src/app/globals.css`. Dark mode follows `prefers-color-scheme`.

| Token | Light | Dark | Usage |
|---|---|---|---|
| `--background` | `#ffffff` | `#09090b` | Page background |
| `--foreground` | `#0a0a0b` | `#fafafa` | Primary text |
| `--card` | `#ffffff` | `#111113` | Cards, sidebar, panels |
| `--muted` | `#f4f4f5` | `#1c1c1f` | Muted fills, skeletons |
| `--muted-foreground` | `#71717a` | `#a1a1aa` | Secondary text |
| `--border` | `#e4e4e7` | `#27272a` | Borders, dividers |
| `--input` | `#d4d4d8` | `#3f3f46` | Input borders |
| `--primary` | `#4f46e5` | `#6366f1` | Brand indigo: primary buttons, active nav, links |
| `--accent` | `#eef2ff` | `#1e1b4b` | Selected nav, hover fills |
| `--accent-foreground` | `#3730a3` | `#c7d2fe` | Text on accent |
| `--destructive` | `#dc2626` | `#ef4444` | Errors, destructive actions |
| `--success` | `#16a34a` | `#22c55e` | Confirmed status |
| `--warning` | `#d97706` | `#f59e0b` | Doubtful / pending status |

**Semantic status mapping:** confirmed → success, doubtful → warning, unconfirmed → muted, source evidence → success, inferred → warning, speculative → muted.

## 4. Typography

Font stack (no web-font download at build time; CJK uses system fonts):

```
ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
"PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans SC", sans-serif
```

| Style | Size / weight | Usage |
|---|---|---|
| Page title | `text-xl` (1.25rem) / 600 | Page headers |
| Card title | `text-sm` / 600 | Card and section titles |
| Body | `text-sm` (0.875rem) / 400 | Default text |
| Secondary | `text-xs` / 400, muted | Metadata, timestamps |
| Stat | `text-2xl` / 600 | Dashboard metrics |
| Mono | `font-mono` | IDs, codes, raw values |

## 5. Spacing, radius, elevation

- Spacing uses the default Tailwind scale (`p-3`, `p-4`, `gap-4`, ...). Page gutters: `p-4` mobile, `sm:p-6` desktop.
- Radius: `--radius-sm` 0.375rem (badges/inputs), `--radius-md` 0.5rem, `--radius` 0.625rem (buttons), `--radius-lg` 0.875rem (cards).
- Elevation: cards use `shadow-sm`; overlays (mobile drawer) use `shadow-lg`. Avoid stacking shadows.

## 6. Layout

- Sidebar: `w-60` (240px), fixed on `md+`, off-canvas drawer below `md`.
- Topbar: `h-14` (56px), sticky, contains mobile menu, workspace name and plan, search, avatar.
- Content: single column, `max-width` emerges from the grid; grids collapse to one column on mobile (`sm:grid-cols-2`, `lg:grid-cols-3`).
- Page structure: `PageHeader` (title, description, actions) → content sections.

## 7. Components

Available in `apps/web/src/components/ui` (shadcn-style, copy-in):

- **Button** — variants `default` (brand), `secondary`, `outline`, `ghost`, `destructive`, `link`; sizes `sm`, `default`, `lg`, `icon`. Use `buttonVariants()` with `Link` for link-buttons.
- **Card** — `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`.
- **Badge** — variants `default`, `secondary`, `outline`, `success`, `warning`, `destructive`, `muted`. Used for status and evidence labels.
- **Input / Textarea / Label** — form controls; always pair a label.
- **Avatar** — `Avatar`, `AvatarImage`, `AvatarFallback` (initials).
- **Skeleton** — loading placeholders.
- **Separator** — horizontal/vertical dividers.

Common building blocks in `src/components/common`:

- **PageHeader** — page title, description, action slot.
- **EmptyState** — icon, title, description, optional action.
- **LoadingBlock / ErrorBlock** — loading rows and error panel with retry.

## 8. Page states

Every data view must define three states:

- **Loading:** `Skeleton` rows via `LoadingBlock`.
- **Empty:** `EmptyState` with a descriptive message and, where possible, a primary action.
- **Error:** `ErrorBlock` with a retry action.

Route-level states live in `src/app/(app)/loading.tsx` and `error.tsx`.

## 9. Data and traceability conventions

- Domain types are defined in `src/types/index.ts` and mirror the future API schema. Do not invent ad-hoc shapes in pages.
- Mock data lives in `src/lib/mock-data.ts` and uses those types, so P2 can replace mock with real responses without touching pages.
- Every AI-derived value must render its confirmation status; advantages must render their evidence type. Speculative values are visually muted and never presented as confirmed.

## 10. Accessibility

- Visible focus rings via `focus-visible:ring-2 ring-ring`.
- Interactive elements have `aria-label` when text is absent (icon buttons).
- Active nav uses `aria-current="page"`.
- Loading regions expose `aria-busy`; errors expose `role="alert"`.
- Touch targets at least 32px (`size-8`/`size-9`) on mobile.

## 11. Do / Don't

**Do:** use tokens; keep status labels next to values; design mobile-first; show unconfirmed data honestly.

**Don't:** hardcode colors; invent component APIs outside `ui/`; hide missing information; use color alone to convey status (pair with text).
