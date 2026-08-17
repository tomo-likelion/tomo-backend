# TOMO Backend

TOMO Backend API built with FastAPI.

## Environment

- Python 3.12
- FastAPI
- PostgreSQL
- Supabase
- Docker Desktop

## Setup

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

### 4. Configure PostgreSQL

For the shared Supabase database, set `DATABASE_URL` in `.env` using the
Session pooler URI. Use the `postgresql+psycopg://` driver and URL-encode
special characters in the database password.

```env
DATABASE_URL=postgresql+psycopg://postgres.<project-ref>:<url-encoded-password>@<pooler-host>:5432/postgres?sslmode=require
```

To use local PostgreSQL instead, keep the default `DATABASE_URL` from
`.env.example` and start the Docker service:

```bash
docker compose up -d postgres
```

### 5. Create tables and seed recipients

```bash
alembic upgrade head
python -m app.scripts.seed_recipients
```

### 6. Run server

```bash
uvicorn app.main:app --reload
```

API documentation is available at `http://127.0.0.1:8000/docs`.

## Test

Tests use an isolated in-memory SQLite database.

```bash
python -m pytest
```
