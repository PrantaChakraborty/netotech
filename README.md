# NeoTech Backend Developer Assignment

FastAPI-based backend service with PostgreSQL, SQLAlchemy (async), and Alembic migrations. This README explains how to configure, run, and develop the project locally and with Docker.

## Table of contents
- Prerequisites
- Environment configuration
- Quick start (Docker)
- Local development (virtualenv)
- Database migrations
- API endpoints
- Useful commands
- Troubleshooting

## Prerequisites
- Docker and Docker Compose (for containerized run)
- Python 3.12.x (for local development)
- PostgreSQL 15+ (local, or use the provided docker-compose service)

## Environment configuration
1) Create a .env file in the project root:
   - Copy .env.example to .env
   - Fill in values according to your environment:
     - DB_HOST
     - DB_NAME
     - DB_USER
     - DB_PASSWORD
     - DB_PORT
     - ENVIRONMENT (optional; defaults to local)

2) Notes:
   - If you run the entire stack with Docker Compose, DB_HOST should be db.
   - If you run locally without Docker for the API, DB_HOST is likely **localhost**.

## Quick start (Docker)
This is the easiest way to run everything (API + PostgreSQL) together.

Option A: One-liner helper script
- ./run.sh
  - Builds images, starts containers, waits for the API to be ready at http://localhost:8000

Option B: Manual steps
- docker compose build
- docker compose up -d
- Visit:
  - API root: http://localhost:8000/
  - Health check: http://localhost:8000/health
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc

Notes:
- Migrations and initial data seeding run automatically inside the API container on startup.

## Local development (virtualenv)
Use this if you want to run the API on your machine with a local Python environment. The project assumes virtualenv (venv) usage.

1) Set up and activate a virtual environment (Python 3.12.x)
- python3.13 -m venv .venv
- source .venv/bin/activate      # macOS/Linux
  -or-
- .venv\Scripts\activate         # Windows (PowerShell/CMD)

2) Install dependencies
- pip install --upgrade pip
- pip install -r requirements.txt

3) Start PostgreSQL
- Option A (recommended): Use the included DB service
  - docker compose up -d db
  - In this case, set DB_HOST=db in your .env (if you run Alembic from host with Docker DB, you can use localhost if port is mapped; otherwise use db for in-network container usage).
- Option B: Use your local PostgreSQL and ensure your .env matches it.

4) Set environment variables
- Create and configure .env (see Environment configuration section)

5) Apply database migrations
- alembic upgrade head

6) Seed initial data (optional but recommended)
- python -m src.seed_data

7) Run the API (reload for development)
- uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

8) Open in browser
- http://localhost:8000/
- http://localhost:8000/health
- http://localhost:8000/docs
- http://localhost:8000/redoc

## Database migrations
- Create a new migration (after updating models):
  - alembic revision -m "describe your change" --autogenerate
- Apply migrations:
  - alembic upgrade head
- Roll back last migration:
  - alembic downgrade -1

## API endpoints
- GET /            — basic service message
- GET /health      — app and DB connectivity check
- OpenAPI/Swagger  — /docs
- ReDoc            — /redoc

Additional feature routes are included under the application router.

## Useful commands
- Run the stack with Docker:
  - docker compose up -d
  - docker compose logs -f api
- Stop and remove containers:
  - docker compose down
- Rebuild after changes to dependencies:
  - docker compose build --no-cache
- Run tests (if present):
  - pytest
- Lint (if configured):
  - ruff check .
- Format (if configured):
  - ruff format

## Troubleshooting
- Database connection errors:
  - Ensure DB is running and credentials in .env are correct.
  - If using Docker Compose for both API and DB, DB_HOST should typically be db inside the compose network.
  - If running API locally and DB via Docker with port mapping, DB_HOST can be localhost with DB_PORT=5432 (or your mapped port).

- Port already in use:
  - Change API port (e.g., uvicorn ... --port 8001) or stop the process using the port.

- Migrations fail:
  - Verify alembic.ini configuration and that your .env values are loaded.
  - Check database connectivity: psql or pg_isready against your DB host/port.

- Container healthcheck failing:
  - docker compose logs -f api
  - Check /health endpoint and DB service logs: docker compose logs -f db

    
## Challenges and Resolutions
I typically work with FastAPI for hobby projects using synchronous PostgreSQL.
This was my first time using asyncpg. I also have a strong Django background,
where database configuration, environment variables, and settings are
convention-driven and largely pre-wired. With FastAPI, these pieces
require more manual setup. I initially ran into uncertainty around
the file structure and proper async session management.
I addressed this by following community best practices 
for FastAPI project structure and adopting a proven approach
to managing async SQLAlchemy sessions. Combined with careful
iteration and tooling assistance, this resulted in a clean, maintainable setup.


# Total hours spent: 12 hours