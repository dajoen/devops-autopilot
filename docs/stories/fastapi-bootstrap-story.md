# User Story: Bootstrap FastAPI Service with Config, Health, and Demo Mode

As a developer onboarding this repository,
I want a working FastAPI service scaffold with configuration, health checks, and a demo mode,
so that I can run and iterate locally without heavy dependencies while retaining a production-ready structure.

## Context
- Project targets a modular FastAPI application with:
  - Routers: llm, bamboo, reports, config, health
  - YAML-based configuration with environment overrides
  - Async Postgres (SQLAlchemy) and InfluxDB 2 client (planned)
  - CORS for UI origins
  - Health endpoint returning app version and connectivity status
- Local environment uses Python 3.13; some binary wheels (asyncpg, pydantic-core) may not be readily available.
- A "demo mode" enables immediate local runs without DB drivers.

## Goals
- Provide a runnable app locally (demo) and a full-feature scaffold for later production enablement.
- Keep configuration centralized and overridable via environment variables.
- Ensure health endpoint exists and is verifiable.

## Acceptance Criteria
- Project contains:
  - Core modules: `backend/core` (config, db, influx managers)
  - Models: `backend/models` (pydantic v2 data models)
  - Services: `backend/services` (health, runs, logs)
  - Routers: `routers` (health, llm, bamboo, reports, config)
  - App entrypoints: `main.py` (full) and `run_demo.py`/`main_demo.py` (demo mode)
  - Requirements files: `requirements.txt` (full) and `requirements-minimal.txt` (demo)
  - Sample config: `config/config.yaml`
- Demo mode starts with minimal dependencies and serves:
  - `/healthz` returns OK
  - `/docs` (OpenAPI) loads without errors
- `.gitignore` excludes common build artifacts, env files, and caches.

## Notes & Constraints
- Full database/influx connectivity requires installing extra deps (see `requirements.txt`).
- Demo mode avoids binary wheels to ensure fast onboarding on Python 3.13.
- Prefer amending the most recent commit to consolidate bootstrap changes and keep history clean.

## How to Run (Demo)
1. Create and activate a virtual environment.
2. Install minimal deps: `pip install -r requirements-minimal.txt`
3. Start the server: `python run_demo.py`
4. Visit `http://127.0.0.1:8000/docs` and `http://127.0.0.1:8000/healthz`

## Future Work
- Add real database models and migrations.
- Wire async Postgres via SQLAlchemy + asyncpg.
- Integrate InfluxDB 2 client and telemetry routes.
- Add tests for health, config load, and routers.
- Dockerfile and CI workflows.
