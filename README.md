# ApplyTrack

A personal **mini-ATS** to track job applications, parse descriptions, and tailor your CV with AI.

## Features

- **Kanban Board** — Drag-and-drop applications through stages (Not Applied → Applied → Interview → Offer → Rejected → Archived).
- **AI Assistant** (5 modules):
  - **Parse JD** — Extract skills, responsibilities, and keywords from job descriptions.
  - **Match Score** — Analyse your profile against the JD and identify gaps.
  - **Tailor CV** — Generate bullet suggestions grounded in your experience.
  - **Outreach** — Draft LinkedIn and email messages.
  - **Interview Prep** — Likely questions, checklists, and STAR story suggestions.
- **Smart Reminders** — Set follow-up reminders tied to each application.
- **Dashboard** — Stats, recent activity, and upcoming reminders at a glance.
- **Evidence-Based AI** — Every claim links back to your profile or the job description.

## Tech Stack

| Layer | Stack |
|-------|-------|
| Backend | Python 3.12, FastAPI, SQLAlchemy (async), Pydantic v2, Celery, Redis |
| Frontend | Next.js 16, Tailwind CSS v4, TanStack Query, DnD Kit |
| Database | PostgreSQL (production), SQLite (local dev) |
| AI | OpenAI-compatible client (OpenRouter, Anthropic, etc.) — with full mock mode |

## Quick Start

### Docker (recommended)

```bash
cp .env.example .env      # edit secrets as needed
docker compose up --build
```

Open [http://localhost:3000](http://localhost:3000).

### Local Development

**Backend:**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn applytrack.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Celery Worker** (optional — skip if `CELERY_ALWAYS_EAGER=true`):

```bash
cd backend
source .venv/bin/activate
celery -A applytrack.workers.celery_app worker --loglevel=info
```

### Makefile Shortcuts

```bash
make install-backend   # create venv + install deps
make install-frontend  # npm install
make run-backend       # uvicorn --reload
make run-frontend      # npm run dev
make run-worker        # celery worker
make docker-up         # docker compose up --build
make lint              # ruff check + format
make test              # pytest
make seed              # populate demo data
```

## Configuration

Copy `.env.example` to `.env`. Key variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./applytrack.db` | DB connection string |
| `JWT_SECRET` | dev placeholder | **Change in production** |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis for Celery |
| `CELERY_ALWAYS_EAGER` | `false` | `true` = run tasks inline (no Redis needed) |
| `AI_MODE` | `mock` | `mock` or `real` |
| `AI_API_KEY` | empty | Required when `AI_MODE=real` |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

## License

MIT
