# Deploying Litmus (free, no credit card)

A 100% free, permanent stack — **no credit card anywhere**:

| Component | Platform | Card? |
| --- | --- | --- |
| Database (Postgres) | **Neon** | No |
| Backend (FastAPI, Docker) | **Hugging Face Spaces** | No |
| Frontend (Next.js) | **Vercel** | No |

The demo runs on the mock provider, so **no API key** is needed either.

---

## 1. Database — Neon (no card)

1. Sign up at https://neon.com with GitHub (no credit card).
2. Create a project (any region). Neon creates a database automatically.
3. On the project dashboard, open **Connection Details** and copy the connection
   string. **Choose the "Direct connection"** (not the `-pooler` one) — it works
   best with asyncpg. It looks like:
   ```
   postgresql://user:password@ep-xxxx.region.aws.neon.tech/dbname?sslmode=require
   ```
   Keep it for step 2.

> The backend handles the scheme and SSL automatically (`postgres://` →
> `postgresql+asyncpg://`, and it strips `sslmode`/`channel_binding`), so paste
> the URL exactly as Neon gives it.

## 2. Backend — Hugging Face Space (no card)

1. Sign up at https://huggingface.co (no credit card).
2. **New → Space**. Choose **Docker** as the SDK, a name (e.g. `litmus-backend`),
   visibility Public.
3. In the Space's **Files** tab, add two files (copy from
   [`deploy/huggingface/`](../deploy/huggingface/) in this repo):
   - `Dockerfile` — clones this repo's backend and runs it (reuses the same code).
   - `README.md` — the Space metadata (`sdk: docker`, `app_port: 8000`).
4. Go to **Settings → Variables and secrets** and add:
   - `DATABASE_URL` = your Neon connection string (from step 1).
   - `CORS_ORIGINS` = your Vercel URL (add after step 3; you can set it later and
     re-run the Space).
5. The Space builds and starts. Your API is at
   `https://<your-username>-litmus-backend.hf.space` — check `/health` and `/docs`.

## 3. Frontend — Vercel (no card)

1. Sign up at https://vercel.com with GitHub (no credit card).
2. **Add New… → Project** → import this repo.
3. Set **Root Directory** to `frontend`. Framework is auto-detected (Next.js).
4. Add an environment variable:
   - `NEXT_PUBLIC_API_URL` = your Hugging Face Space URL
     (e.g. `https://<your-username>-litmus-backend.hf.space`).
5. Deploy. Open the Vercel URL — the dashboard loads and talks to the backend.

## 4. Wire CORS

Back in the Hugging Face Space secrets, set `CORS_ORIGINS` to your Vercel URL
(e.g. `https://litmus.vercel.app`) and **Restart** the Space (Settings → Factory
rebuild, or just restart). The dashboard can now call the API from the browser.

## 5. Update the README

Replace the demo-link placeholders in [`README.md`](../README.md) with your live
URLs (Vercel dashboard + Hugging Face `/docs`).

---

## Notes

- **Idle behavior.** Neon compute scales to zero after ~5 min idle; free HF Spaces
  sleep after ~48h idle and wake on visit. The first request after idle is slow —
  fine for a demo.
- **Updating the backend.** The Space builds from a `git clone` of `main`. To pull
  new changes, trigger a **Factory rebuild** on the Space.
- **Redis** is not needed for Phase 1 (Celery arrives in Phase 2).

## Alternative: Render (also card-free for web services)

Render web services don't require a card either, but Render's **free Postgres
expires after 30 days**. If you prefer Render for the backend, use the
[`render.yaml`](../render.yaml) blueprint and point `DATABASE_URL` at Neon instead
of a Render database (the blueprint no longer provisions one, so no card is asked).
