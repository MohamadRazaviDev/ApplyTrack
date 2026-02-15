# ApplyTrack

A personal "mini-ATS" to track applications, parse descriptions, and tailor your CV with AI.

## Features

- **Application Pipeline**: Kanban board to track applications through stages (Draft -> Applied -> Interview -> Offer).
- **AI Assistant**: 
  - **Parse JD**: Extracts skills, responsibilities, and keywords from raw job descriptions.
  - **Match Score**: Analyzes your profile against the JD to identify gaps and generate a match score.
  - **Tailor CV**: Suggests project bullets tailored to the specific role.
- **Evidence-Based AI**: Every AI claim is grounded in your profile data or the job description (no hallucinations).
- **Dashboard**: Quick overview of your application stats.

## Tech Stack

- **Backend**: Python (FastAPI), SQLAlchemy (Async), Pydantic v2, Celery (Background Tasks), Redis.
- **Frontend**: Next.js (App Router), Tailwind CSS, TanStack Query, DnD Kit.
- **Database**: Postgres (Production), SQLite (Dev/Test).
- **AI**: OpenAI Client (compatible with OpenRouter/Anthropic).

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### Quick Start (Docker)

1.  Clone the repository.
2.  Create a `.env` file in the root directory (copy `.env.example`).
3.  Run:
    ```bash
    docker-compose up --build
    ```
4.  Open [http://localhost:3000](http://localhost:3000).

### Local Development

**Backend**:

```bash
cd backend
pip install poetry
poetry install
poetry run uvicorn applytrack.main:app --reload
```

**Frontend**:

```bash
cd frontend
npm install
npm run dev
```

**Worker**:

```bash
cd backend
poetry run celery -A applytrack.workers.celery_app worker --loglevel=info
```

## AI Configuration

To use real AI features, set `APPLYTRACK_OPENROUTER_API_KEY` in your `.env` file. By default, the system runs in **Mock Mode**, returning simulated responses for testing without cost.

## License

MIT
