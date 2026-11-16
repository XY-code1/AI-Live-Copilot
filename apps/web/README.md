# AI Live Copilot — Web

Next.js 16 + React 19 + TypeScript front end for AI Live Copilot.

## Commands

```bash
pnpm install
pnpm dev        # http://localhost:3000
pnpm build
pnpm lint
pnpm exec tsc --noEmit
```

## Structure

```
src/
  app/
    layout.tsx                 root html/body + metadata
    page.tsx                   redirects to /dashboard
    (app)/                     authenticated shell routes
      layout.tsx               AppShell (sidebar + topbar)
      dashboard/  products/  analysis/  scripts/  assets/  settings/
  components/
    layout/                    app-shell, nav-items
    common/                    page-header, empty-state, state-blocks
    ui/                        button, card, badge, input, label, textarea, avatar, skeleton, separator
  lib/                         utils, format, mock-data
  types/                       domain contracts shared with the future API
```

## Conventions

- Design language: [`../docs/DESIGN_SYSTEM.md`](../docs/DESIGN_SYSTEM.md).
- Domain types mirror the future API schema; mock data uses the same types so P2 can swap in real responses.
- Next.js 16 is in use with Cache Components enabled (`cacheComponents`, `partialPrefetching`). Consult `node_modules/next/dist/docs/` before using framework APIs.
