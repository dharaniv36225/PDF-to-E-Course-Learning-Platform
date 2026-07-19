---
name: testing-e2e
description: Run the PDF-to-E-Course platform locally and test the golden path (auth, dashboard, upload, nav, dark mode) end-to-end. Use when verifying frontend/backend changes at runtime.
---

# Local end-to-end testing

## Services to start (three components)
1. **Postgres** (docker):
   ```bash
   docker run -d --name ecourse-pg -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=ecourse -p 5432:5432 postgres:16-alpine
   ```
2. **Backend** (from `backend/`, venv at `backend/.venv`):
   ```bash
   export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ecourse"
   export SECRET_KEY=dev-test-secret
   export BACKEND_CORS_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
   export ENVIRONMENT=development
   alembic upgrade head    # first time only
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
   Health check: `curl http://localhost:8000/health` → `{"status":"ok",...}`.
3. **Frontend** (from `frontend/`):
   ```bash
   export NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"
   export NEXT_PUBLIC_APP_URL="http://localhost:3000"
   npm run dev   # serves http://localhost:3000
   ```

## Gotchas
- **`BACKEND_CORS_ORIGINS`**: a comma-separated string works (e.g. `http://localhost:3000,http://127.0.0.1:3000`), as does a JSON array `["http://localhost:3000"]`. If startup ever fails with `SettingsError: error parsing value for field "BACKEND_CORS_ORIGINS"`, the pydantic-settings JSON-decode is being hit before the validator — check `NoDecode` is still on the field in `backend/app/core/config.py`.
- **`SECRET_KEY` + `ENVIRONMENT=production`**: the app refuses to start in production with the default `change-me-in-production`. For local testing keep `ENVIRONMENT=development` (docker-compose defaults to development).
- **passlib/bcrypt warning**: backend logs `error reading bcrypt version` — harmless; register still returns 201.
- **AI deps must be installed for uploads**: uploads call ChromaDB + sentence-transformers at request time. If the venv lacks them, `POST /uploads` 500s with `ModuleNotFoundError: No module named 'chromadb'`. Run `pip install -r requirements.txt` in `backend/.venv` before testing AI features (they ARE in requirements.txt, so Docker/Render are fine; a bare local venv may not have them). First embed downloads the sentence-transformers model.
- **AI features need an LLM key**: course generation, RAG chat, and quiz generation require `GROQ_API_KEY` (or `OPENROUTER_API_KEY`). Without one, the golden path below still works, but you cannot create a course through the UI. Set the key as an env var when starting the backend.
- **`UID` is a bash readonly builtin** — never use it as a shell variable name in test scripts (use `UPID` etc.), or you get `UID: readonly variable`.
- **Dev-mode React hydration warning** may appear ("1 Issue" indicator) pointing at the Spinner; the diff may show a `devin-hidden` attribute which is injected by the DOM-inspection tooling, so it can be a test-harness artifact rather than an app bug. Confirm in a plain browser before reporting as a defect.

## Golden path (no LLM key required)
Register (`/register`, fields full_name/email/password) → auto-redirect `/dashboard` (proves CORS + auth) → empty stats (Courses/Uploads/Avg quiz/streak all 0; "No courses yet", "No quiz attempts yet") → sidebar "Upload PDF" → `/upload` ("Upload PDFs", drag&drop zone) → theme toggle in header → user menu (top-right initials) → "Sign out" → `/login` → direct-nav `/dashboard` while logged out redirects to `/login`.

## AI path (requires GROQ_API_KEY or OPENROUTER_API_KEY)
Create a small text-based PDF (e.g. via PyMuPDF `fitz`, a few pages of clear factual content so RAG/quiz have material). Flow: Upload page → click dropzone → OS file picker → select PDF → card shows page count + green **Ready** badge. Click **Generate course** (~30s LLM) → redirects to `/courses/{id}` with title/chapters/objectives. **Ask AI tutor** (`/courses/{id}/chat`) → grounded answer with `[p.N]` citations + Sources badges. **Quizzes** (`/courses/{id}/quiz`) → select types + Generate (~15-60s, scales with #questions) → answer radios → Submit → score % view with per-question explanations. Back to Dashboard → Courses/Uploads/Avg-score stats + course card populated.
- Quiz submit exercises the UUID-in-JSONB fix; dashboard-with-a-course exercises the recent_courses response-model fix. Both should return 200 with no error toast.
- To smoke-test the whole pipeline fast (no browser), hit the API: register → `POST /uploads` (multipart) → `POST /courses/generate` → `POST /chat` → `POST /quizzes/generate` → `POST /quizzes/{id}/submit` → `GET /dashboard`.

## Quality gates
- Backend: `cd backend && . .venv/bin/activate && ruff check app tests && pytest -q` (needs Postgres + DATABASE_URL + SECRET_KEY).
- Frontend: `cd frontend && npm run lint && npm run typecheck && npm run build`.

## Devin Secrets Needed
- None for the golden path. For AI features: `GROQ_API_KEY` or `OPENROUTER_API_KEY`.
