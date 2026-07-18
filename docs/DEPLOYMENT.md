# Deployment Guide

This guide covers deploying the platform:

- **Backend (FastAPI)** → Render (Docker) + managed PostgreSQL
- **Frontend (Next.js)** → Vercel
- **Auth & Storage** → Supabase (optional but recommended)
- **Local / self-hosted** → Docker Compose

---

## 1. Prerequisites

| Service | Purpose | Required |
| --- | --- | --- |
| Groq API key | Default LLM for generation & RAG | Yes (or OpenRouter) |
| OpenRouter API key | Fallback LLM | Optional |
| Supabase project | Auth (Google/email) + PDF storage | Optional |
| PostgreSQL 16 | Primary datastore | Yes |

Get keys:
- Groq: https://console.groq.com/keys
- OpenRouter: https://openrouter.ai/keys
- Supabase: https://supabase.com/dashboard

---

## 2. Local with Docker Compose

```bash
cp .env.example .env          # fill in SECRET_KEY, GROQ_API_KEY, etc.
docker compose up --build
```

Services:
- Frontend → http://localhost:3000
- Backend → http://localhost:8000 (Swagger at `/docs`)
- Postgres → localhost:5432

Migrations run automatically on backend start (`scripts/start.sh`). Seed sample data:

```bash
docker compose exec backend python -m scripts.seed
```

---

## 3. Backend on Render

### Option A — Blueprint (recommended)

1. Push this repo to GitHub.
2. In Render: **New → Blueprint**, point it at the repo. Render reads [`render.yaml`](../render.yaml).
3. It provisions a Dockerized web service (`ecourse-backend`) + a managed Postgres (`ecourse-db`).
4. Set the `sync: false` env vars in the dashboard:
   - `GROQ_API_KEY`, `OPENROUTER_API_KEY`
   - `BACKEND_CORS_ORIGINS` → your Vercel URL, e.g. `https://your-app.vercel.app`
   - `SUPABASE_URL`, `SUPABASE_JWT_SECRET`, `SUPABASE_SERVICE_ROLE_KEY` (if using Supabase)
5. `DATABASE_URL` and `SECRET_KEY` are wired automatically.

`DATABASE_URL` from Render uses the `postgresql://` scheme; the backend normalizes it to the psycopg driver automatically (see `app/core/config.py`).

### Option B — Manual

- New Web Service → Docker → root `./backend`.
- Add a Render PostgreSQL instance and copy its Internal Connection String into `DATABASE_URL`.
- Health check path: `/health`.

> **Note on model downloads:** the embedding model (`all-MiniLM-L6-v2`) downloads on first use. Use at least the Starter plan so the container has enough memory; the first request that triggers embedding will be slower.

---

## 4. Frontend on Vercel

1. In Vercel: **New Project** → import the repo → set **Root Directory** to `frontend`.
2. Framework preset: **Next.js** (auto-detected; see [`vercel.json`](../frontend/vercel.json)).
3. Environment variables:
   - `NEXT_PUBLIC_API_URL` → `https://<render-backend>.onrender.com/api/v1`
   - `NEXT_PUBLIC_APP_URL` → your Vercel URL
   - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` (if using Supabase)
4. Deploy. Then add the Vercel URL to the backend's `BACKEND_CORS_ORIGINS`.

---

## 5. Supabase setup (optional)

1. Create a project; copy the Project URL, `anon` key, `service_role` key, and JWT secret (Settings → API).
2. **Auth → Providers → Google**: enable and add your OAuth client. Redirect URL: `https://<your-app>/auth/callback`.
3. **Storage**: create a bucket named `pdfs` (matches `SUPABASE_STORAGE_BUCKET`). Set `USE_SUPABASE_STORAGE=true` on the backend to store PDFs there instead of local disk.
4. Backend verifies Supabase-issued JWTs using `SUPABASE_JWT_SECRET` and bridges them to app JWTs via `POST /api/v1/auth/supabase`.

---

## 6. Post-deploy checklist

- [ ] `GET /health` returns `{"status":"ok"}` on the backend.
- [ ] Swagger reachable at `/docs`.
- [ ] Frontend can register/login (network tab hits `NEXT_PUBLIC_API_URL`).
- [ ] `BACKEND_CORS_ORIGINS` includes the exact frontend origin (no trailing slash).
- [ ] At least one LLM key (`GROQ_API_KEY` or `OPENROUTER_API_KEY`) is set.
- [ ] Upload a small PDF and generate a course end-to-end.

---

## 7. CI/CD

GitHub Actions ([`.github/workflows`](../.github/workflows)):
- `ci.yml` — backend lint (Ruff) + migrations + pytest against a Postgres service; frontend lint + typecheck + build.
- `docker.yml` — validates both Docker images build.

Render and Vercel both auto-deploy on push to the default branch once connected.
