import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  retries: process.env.CI ? 2 : 0,
  use: { baseURL: "http://127.0.0.1:13000", trace: "on-first-retry" },
  webServer: [
    {
      command: "uv run alembic upgrade head && uv run uvicorn app.main:app --host 127.0.0.1 --port 18000",
      cwd: "../api",
      url: "http://127.0.0.1:18000/health",
      reuseExistingServer: !process.env.CI,
      env: {
        ...process.env,
        DATABASE_URL: "sqlite:///./e2e.db",
        AUTH_MODE: "dev",
        CORS_ORIGINS: "http://127.0.0.1:13000",
      },
    },
    {
      command: "pnpm dev --hostname 127.0.0.1 --port 13000",
      url: "http://127.0.0.1:13000",
      reuseExistingServer: !process.env.CI,
      env: { ...process.env, NEXT_PUBLIC_API_URL: "http://127.0.0.1:18000" },
    },
  ],
});

