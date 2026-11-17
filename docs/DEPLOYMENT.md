# V1.1 deployment guide

## Recommended topology

- Render Web Service: `apps/web` (Next.js)
- Render Web Service: `apps/api` (FastAPI + PaddleOCR)
- Render PostgreSQL
- Render persistent disk mounted at `/var/data` for uploaded source files
- Email/password authentication with JWT sessions (bcrypt + HS256)
- Sentry for frontend and backend error monitoring

`render.yaml` contains the deployable Blueprint. Create a Render Blueprint from the GitHub repository, then provide the environment variables marked `sync: false`.

## Required production variables

### API

- `DEEPSEEK_API_KEY`
- `AUTH_MODE=password`
- `JWT_SECRET` (long random string; keep it secret)
- `CORS_ORIGINS=https://your-domain.example`
- `SENTRY_DSN`

### Web

- `NEXT_PUBLIC_API_URL=https://api.your-domain.example`
- `NEXT_PUBLIC_API_URL` (optional; defaults to `http://localhost:8000`)
- `NEXT_PUBLIC_SENTRY_DSN`
- `SENTRY_DSN`

## Domain plan

1. Bind `app.example.com` to the web service.
2. Bind `api.example.com` to the API service.
3. Set `NEXT_PUBLIC_API_URL` and `CORS_ORIGINS` to those final HTTPS origins.
4. Add the production domain to `CORS_ORIGINS`.
5. Run `/health`, `/ready`, sign-in, and the Playwright core flow before inviting users.

## Local development

Local development can set `AUTH_MODE=dev` to skip login (uses the `X-Dev-User` header). Start PostgreSQL/API/Web with Docker Compose, or run the two applications directly. Production must use `AUTH_MODE=password` with a strong `JWT_SECRET`.

