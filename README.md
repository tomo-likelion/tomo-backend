# TOMO Backend

TOMO Backend API built with FastAPI.

## Environment

- Python 3.12
- FastAPI
- PostgreSQL

## Setup

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies
```pip install -r requirements.txt ```
### 3. Configure environment
```cp .env.example .env```
### 4. Run server 
```uvicorn app.main:app --reload ```
