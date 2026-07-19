---
title: Litmus Backend
emoji: 🧪
colorFrom: indigo
colorTo: gray
sdk: docker
app_port: 8000
pinned: false
license: mit
---

# Litmus — Backend API

The FastAPI backend for [Litmus](https://github.com/oussamaelbourakadi/litmus),
running on a Hugging Face Docker Space with a Neon Postgres database.

- Health: `/health`
- API docs (Swagger): `/docs`

Set these as **Space secrets** (Settings → Variables and secrets):

- `DATABASE_URL` — your Neon **direct** connection string
  (`postgresql://…?sslmode=require`; asyncpg SSL is handled automatically).
- `CORS_ORIGINS` — your Vercel frontend URL (e.g. `https://litmus.vercel.app`).
