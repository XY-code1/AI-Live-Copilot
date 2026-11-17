# ADR 0004: email/password authentication replaces Clerk

- Status: Accepted
- Date: 2026-11-17
- References: [ADR 0003](0003-v1.1-production-services.md) · [SECURITY.md](../SECURITY.md) · [DEPLOYMENT.md](../DEPLOYMENT.md)

## Context

ADR 0003 selected Clerk for identity. The owner's requirement is a self-contained email/password flow, with no third-party identity provider, so the product can run in local Docker and any cloud without external accounts.

## Decision

Use email + password authentication implemented in-house: bcrypt password hashing, HS256 JWT sessions issued and verified by FastAPI, and a `users` table plus workspace memberships. A `dev` auth mode remains for local development and tests via the `X-Dev-User` header; production uses `AUTH_MODE=password` with a strong `JWT_SECRET`.

## Consequences

- No Clerk dependency (front-end or back-end).
- Passwords are hashed with bcrypt and never stored in plaintext.
- Tokens are stateless; revocation requires expiry or secret rotation.
- Registration creates a personal workspace and owner membership.

## Supersedes

[ADR 0003](0003-v1.1-production-services.md) only with respect to the identity provider; all other ADR 0003 decisions (PaddleOCR, Render/Docker, Sentry, JSON logs) stand.
