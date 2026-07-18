# Architecture

## Overview

```
┌─────────────┐      HTTPS/JSON + SSE      ┌──────────────┐
│  Next.js 15 │  ───────────────────────▶  │   FastAPI    │
│  (Vercel)   │  ◀───────────────────────  │  (Render)    │
└─────────────┘                            └──────┬───────┘
      │                                           │
      │ Supabase Auth (Google/email)              │
      ▼                                           ▼
┌─────────────┐                    ┌──────────────────────────────┐
│  Supabase   │                    │  PostgreSQL   │   ChromaDB    │
│ Auth+Storage│                    │  (relational) │ (vectors)     │
└─────────────┘                    └──────────────────────────────┘
                                                   ▲
                                                   │ Groq (default) / OpenRouter (fallback)
                                                   ▼
                                            ┌──────────────┐
                                            │   LLM APIs   │
                                            └──────────────┘
```

## Backend layers (clean architecture)

```
app/
  api/          # FastAPI routers (HTTP layer) + dependencies
  services/     # Business logic (orchestration, use cases)
  repositories/ # Data access (SQLAlchemy queries, repository pattern)
  models/       # SQLAlchemy ORM models
  schemas/      # Pydantic request/response models (validation & serialization)
  ai/           # LLM, embeddings, vector store, RAG, course/quiz generators, prompts
  core/         # config, security, logging, errors, middleware
  db/           # engine, session, declarative base + mixins
  utils/        # PDF extraction, storage, JSON parsing
```

The dependency direction is one-way: `api → services → repositories → models`. Schemas cross layers for I/O; `ai` and `utils` are stateless helpers used by services.

## AI / RAG pipeline

```
Upload PDF
  └─ PyMuPDF extract text (per page)
      └─ RecursiveCharacterTextSplitter (chunk_size=1000, overlap=150)
          └─ Sentence Transformers (all-MiniLM-L6-v2) embeddings
              └─ ChromaDB persistent collection (per upload)  + embeddings metadata in Postgres

Generate course
  └─ LLM (Groq → OpenRouter fallback) with COURSE_STRUCTURE prompt → JSON
      └─ normalized + persisted as course → chapters → lessons

Chat (RAG)
  └─ embed question → Chroma top-k retrieval (with page citations)
      └─ build context + recent history → LLM with document-only system prompt
          └─ stream tokens over SSE + return sources

Quiz
  └─ LLM with QUIZ prompt → normalized questions (mcq/true_false/short_answer)
      └─ graded on submit (exact match / normalized containment for short answer)
```

## Frontend structure

```
src/
  app/               # App Router pages
    (app)/           # Protected group (dashboard, courses, upload, search, profile)
    login, register, forgot-password, auth/callback
  components/        # UI primitives (button, card, ...), layout, charts, course card
  hooks/             # React Query hooks (auth, courses, uploads, quiz, chat, dashboard)
  lib/               # axios client (+ token refresh), supabase client, utils
  store/             # zustand auth store
  types/             # shared TypeScript types
```

State & data:
- **TanStack Query** for server state (caching, invalidation).
- **Axios** instance with JWT attach + refresh-on-401 interceptor.
- **Zustand** for lightweight auth/user state.
- **SSE via fetch** for streaming chat responses.

## Cross-cutting concerns

- **Auth:** JWT (access + refresh). Supabase JWTs are exchanged for app JWTs.
- **Security:** password hashing (bcrypt), CORS allow-list, per-IP rate limiting.
- **Performance:** GZip compression, DB connection pooling, request timing header.
- **Errors:** typed `AppError` hierarchy → consistent `{ "error": { "code", "message" } }` responses.
- **Observability:** structured logging; `/health` and `/health/ready` probes.
