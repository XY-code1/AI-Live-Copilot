# V1.1 security baseline

- Clerk signs user sessions; FastAPI verifies RS256 JWTs and never stores passwords.
- Every top-level business query is restricted by workspace membership.
- New products, competitors, comparisons, and scripts receive the authenticated workspace ID on the server; client-supplied workspace IDs are ignored.
- Uploads are size limited and restricted to PDF, PNG, JPEG, and WebP. PDF page counts are limited and encrypted/damaged files are rejected.
- URL imports accept only public HTTP/HTTPS addresses, reject credentials, private/reserved IP ranges, excessive redirects, unsupported content types, and oversized responses.
- Secrets remain external environment variables. `.env` files are ignored by Git.
- Sentry runs without default personal-data collection; API logs are structured JSON with request IDs.

Before production launch, rotate any key previously stored outside the deployment secret manager and run the GitHub Actions suite.

