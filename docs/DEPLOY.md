# Deploying Litmus (live demo)

Backend on **Render** (Docker + managed Postgres), frontend on **Vercel** (Next.js).
No API key required — the demo runs on the mock provider.

## 1. Backend + database on Render

1. Push this repo to GitHub (already done for the public repo).
2. Render Dashboard → **New** → **Blueprint** → connect the repo. Render reads
   [`render.yaml`](../render.yaml) and provisions:
   - `litmus-db` — a managed PostgreSQL instance.
   - `litmus-backend` — a web service built from `backend/Dockerfile`. On boot it
     runs `alembic upgrade head` then serves on `$PORT`.
3. `DATABASE_URL` is injected from the database (the app normalizes the
   `postgres://` scheme to `postgresql+asyncpg://` automatically).
4. Wait for the deploy, then open `https://<your-backend>.onrender.com/health` →
   should return `{"status":"ok",...}`. Swagger is at `/docs`.

## 2. Frontend on Vercel

1. Vercel Dashboard → **Add New… → Project** → import the repo.
2. Set **Root Directory** to `frontend`. Framework is auto-detected (Next.js).
3. Add an environment variable:
   - `NEXT_PUBLIC_API_URL = https://<your-backend>.onrender.com`
4. Deploy. Open the Vercel URL → the dashboard loads and talks to the backend.

## 3. Wire CORS

Back in Render, set the backend's `CORS_ORIGINS` env var to your Vercel URL
(e.g. `https://litmus.vercel.app`) and redeploy. The dashboard can now call the
API from the browser.

## 4. Update the README

Replace the demo-link placeholders in [`README.md`](../README.md) with your live
URLs.

## Notes

- **Free tiers sleep.** Render's free web service and Postgres may spin down when
  idle; the first request after idle is slow. Fine for a demo.
- **Redis** is not needed for Phase 1 (Celery arrives in Phase 2).
- Use Render's **Internal Database URL** (the blueprint does this) to avoid SSL
  parameters that the asyncpg driver does not accept.
