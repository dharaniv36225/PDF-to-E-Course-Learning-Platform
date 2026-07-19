# PDF to E-Course Learning Platform

Turn any PDF into a structured, AI-powered course — with auto-generated chapters, lessons, summaries and quizzes, plus a Retrieval-Augmented-Generation (RAG) chatbot that answers **only** from the uploaded document.

> Full-stack monorepo: **Next.js 15** frontend, **FastAPI** backend, **PostgreSQL + ChromaDB**, **LangChain + Groq** AI engine. Production-ready with Docker, CI/CD and deploy configs for Vercel + Render.

---

## ✨ Features

- **Auth** — email/password + Google OAuth (Supabase), JWT access/refresh, protected routes.
- **PDF upload** — drag & drop, multiple files, progress bar, PyMuPDF extraction, chunking, local or Supabase storage.
- **AI course generation** — title, description, objectives, prerequisites, difficulty, estimated time, chapters → lessons (explanation, examples, notes, summary, key takeaways).
- **RAG chatbot** — document-grounded answers, conversation memory, streaming (SSE), source citations with page numbers.
- **Quizzes** — MCQ / true-false / short-answer generation, instant grading, explanations, saved attempts.
- **Progress tracking** — mark lessons complete, resume, completion %, time spent.
- **Dashboard** — stats, learning activity chart, quiz scores, learning streak, recent courses.
- **Search** — keyword (Postgres) + semantic (vector) search across content.
- **UX** — responsive, dark mode, animations (Framer Motion), loading skeletons.

## 🧱 Tech stack

| Layer | Technologies |
| --- | --- |
| Frontend | Next.js 15 (App Router), TypeScript, Tailwind CSS, shadcn-style UI, TanStack Query, React Hook Form + Zod, Framer Motion, Axios, Recharts |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, LangChain, PyMuPDF, ChromaDB, Sentence Transformers |
| AI | Groq (default) with OpenRouter fallback, `all-MiniLM-L6-v2` embeddings, RAG pipeline |
| Data | PostgreSQL (relational) + ChromaDB (vectors) |
| Auth/Storage | Supabase Auth (Google/email) + Supabase Storage |
| Infra | Docker, docker-compose, GitHub Actions, Vercel (frontend), Render (backend) |

## 📁 Structure

```
.
├── frontend/     # Next.js 15 app (pages, components, hooks, lib)
├── backend/      # FastAPI app (api, services, repositories, models, ai, core)
├── database/     # schema.sql + ERD / notes
├── docs/         # ARCHITECTURE.md, DEPLOYMENT.md
├── docker-compose.yml
├── render.yaml   # Render blueprint (backend + Postgres)
└── .github/workflows/  # CI + Docker build
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full design and the AI/RAG pipeline.

---

## 🚀 Quick start (Docker Compose)

```bash
cp .env.example .env      # set SECRET_KEY and GROQ_API_KEY (minimum)
docker compose up --build
```

- Frontend → http://localhost:3000
- Backend API docs (Swagger) → http://localhost:8000/docs

Seed sample data (demo user `demo@ecourse.dev` / `demopassword123`):

```bash
docker compose exec backend python -m scripts.seed
```

---

## 🛠️ Local development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env      # set DATABASE_URL, SECRET_KEY, GROQ_API_KEY

alembic upgrade head      # run migrations
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000 (Swagger at `/docs`, OpenAPI at `/api/v1/openapi.json`).

Lint & test:

```bash
ruff check app tests
pytest -q
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # set NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
```

Frontend runs at http://localhost:3000.

Lint, typecheck & build:

```bash
npm run lint
npm run typecheck
npm run build
```

---

## 🔑 Environment variables

Minimum to run: `SECRET_KEY`, `DATABASE_URL`, and one LLM key (`GROQ_API_KEY` or `OPENROUTER_API_KEY`). Supabase vars are optional (email/password auth and local storage work without them).

See [`.env.example`](.env.example) (root/compose), [`backend/.env.example`](backend/.env.example) and [`frontend/.env.example`](frontend/.env.example) for the complete list.

### 🤖 Configuring the AI provider

All AI features (course generation, RAG chatbot, quiz generation, summaries) read their credentials from environment variables — nothing is hardcoded and keys are never logged. Add the following to `backend/.env` (copied from [`backend/.env.example`](backend/.env.example)):

```bash
# backend/.env

# Set at least one of these. Groq is tried first, OpenRouter is the fallback.
GROQ_API_KEY=your-groq-key            # https://console.groq.com/keys
OPENROUTER_API_KEY=your-openrouter-key # https://openrouter.ai/keys

# Optional: override the model used for the active provider.
# Leave empty to use the per-provider defaults (GROQ_MODEL / OPENROUTER_MODEL).
MODEL_NAME=llama-3.3-70b-versatile
```

If you run the stack via docker-compose, the same three variables live in the root [`.env`](.env.example) instead.

Behavior:

- **A valid key is present** → the app automatically uses the configured provider (Groq preferred, OpenRouter fallback). No code changes or restarts of anything but the backend are needed.
- **No key is configured** → non-AI functionality (auth, uploads, browsing courses, progress, search) works normally, and any AI endpoint returns a clear message:

  > AI provider is not configured. Please add GROQ_API_KEY or OPENROUTER_API_KEY to your environment variables.

---

## 📡 API overview

Base path: `/api/v1`. Full interactive docs at `/docs`.

| Group | Endpoints |
| --- | --- |
| Auth | `POST /auth/register`, `/auth/login`, `/auth/login/oauth`, `/auth/supabase`, `/auth/refresh`, `/auth/forgot-password`, `GET /auth/me` |
| Users | `GET /users/me`, `PATCH /users/me` |
| Uploads | `POST /uploads`, `GET /uploads`, `GET /uploads/{id}`, `DELETE /uploads/{id}` |
| Courses | `POST /courses/generate`, `GET /courses`, `GET /courses/{id}`, `GET /courses/{id}/lessons/{lessonId}`, `DELETE /courses/{id}` |
| Chat | `POST /chat`, `POST /chat/stream`, `GET /chat/sessions`, `GET /chat/sessions/{id}`, `DELETE /chat/sessions/{id}` |
| Quizzes | `POST /quizzes/generate`, `GET /quizzes/course/{courseId}`, `GET /quizzes/{id}`, `POST /quizzes/{id}/submit` |
| Progress | `PUT /progress/courses/{courseId}/lessons/{lessonId}`, `GET /progress/courses/{courseId}` |
| Dashboard/Search | `GET /dashboard`, `GET /search?q=` |
| Health | `GET /health`, `GET /health/ready` |

---

## 🗄️ Database

PostgreSQL schema (users, uploads, embeddings, courses, chapters, lessons, lesson_progress, chat_sessions, chat_messages, quizzes, quiz_questions, quiz_attempts). Migrations via Alembic; a generated snapshot lives in [`database/schema.sql`](database/schema.sql) with an ERD in [`database/README.md`](database/README.md).

---

## ☁️ Deployment

Frontend → Vercel, Backend → Render, DB → Render/Supabase Postgres. Step-by-step in [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md).

## ✅ CI

GitHub Actions run backend lint + migrations + tests (against a Postgres service) and frontend lint + typecheck + build on every push/PR, plus Docker image build validation.

## 📄 License

MIT
