# DevOps Autopilot

![CI](https://github.com/dajoen/devops-autopilot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.12-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Python 3.12 FastAPI application for automated DevOps operations with PostgreSQL and InfluxDB integration.

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Multiple Routers**: Organized endpoints for LLM, Bamboo CI/CD, Reports, Config, and Health
- **Configuration Management**: YAML-based config with environment variable overrides
- **Database Integration**: 
  - PostgreSQL with async SQLAlchemy for operational data
  - InfluxDB 2.0 for metrics and time-series data
- **CORS Support**: Configurable cross-origin resource sharing
- **Health Monitoring**: Comprehensive health checks with database connectivity
- **Modular Architecture**: Clean separation with models, services, and core utilities

## Project Structure

```
devops-autopilot/
├── backend/
│   ├── models/          # Pydantic data models
│   ├── services/        # Business logic services
│   └── core/           # Core utilities (config, database, influxdb)
├── routers/            # FastAPI route handlers
├── config/             # Configuration files
├── main.py            # Main application entry point
└── requirements.txt   # Python dependencies
```

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL database**:
   ```bash
   createdb devops_autopilot
   ```

3. **Configure the application**:
   Edit `config/config.yaml` with your database settings.

# DevOps Autopilot

A FastAPI application for automated DevOps operations with PostgreSQL and InfluxDB integration.

## Features


## Project Structure

```
devops-autopilot/
├── backend/
│   ├── core/             # Config manager, DB/Influx managers, Settings facade
│   ├── models/           # Pydantic data models (app, db, influx, health, runs, logs)
│   └── services/         # Business logic (health, runs, logs)
├── routers/              # FastAPI route handlers
├── config/               # Configuration files (YAML)
├── .devcontainer/        # Dev Container config (Dockerfile + docker-compose)
├── main.py               # Full application (DB + Influx initialization)
├── main_demo.py          # Demo application (no external drivers needed)
├── run_demo.py           # Demo runner script
├── requirements.txt      # Full dependencies
└── requirements-minimal.txt  # Minimal deps for demo mode
```

## Quickstart (Demo mode)

Use this when you want to run immediately without installing DB drivers.

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements-minimal.txt
python run_demo.py
```

Browse:
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/healthz

## Full setup (Local)

Recommended Python: 3.12 (or use the Dev Container below).

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ensure your Postgres and InfluxDB are available, or use the Dev Container which provides both.

## Dev Container (VS Code)

This repository includes a VS Code Dev Container for consistent development:

- Services: Python 3.12 app container, Postgres 16, InfluxDB 2.7
- Auto-forwards: 8000 (API), 5432 (Postgres), 8086 (InfluxDB)

How to use:

1. Install the "Dev Containers" extension.
2. Open the repository in VS Code.
3. Reopen in container when prompted, or run "Dev Containers: Reopen in Container".
4. The API runs via `uvicorn` with `--reload` inside the container.

InfluxDB defaults (via compose):
- Org: `dev-org`
- Bucket: `devops-metrics`
- Token: `dev-token`

## Configuration

Configuration is loaded from `config/config.yaml` and can be overridden by environment variables.

Examples in `config/config.yaml` include `app`, `database`, `influxdb`, `cors`, and commented `external_apis`.

Environment variables (subset):
- App: `APP_NAME`, `APP_VERSION`, `APP_HOST`, `APP_PORT`, `APP_DEBUG`
- Postgres: `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`
- InfluxDB: `INFLUXDB_URL`, `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`
- CORS: `CORS_ORIGINS` (comma-separated)
- LLM: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`
- Bamboo: `BAMBOO_BASE_URL`, `BAMBOO_USERNAME`, `BAMBOO_TOKEN`

## Settings helpers

High-level accessors for common config, with strict validation and helpful errors.

```python
from backend.core.settings import Settings

s = Settings()
dsn = s.postgres_dsn()              # e.g., postgresql+asyncpg://...
url, org, bucket, token = s.influx_config()
provider = s.provider()             # raises if not configured
base_url, user, token = s.bamboo_auth()
```

## Endpoints (demo)

- `GET /healthz` — health summary (demo mode uses mocked DB)
- `GET /healthz/ping` — simple ping
- `GET /docs` — OpenAPI UI

## Troubleshooting

- On Python 3.13, some binary wheels may be unavailable (e.g., asyncpg, pydantic-core). Use the Dev Container or Python 3.12 locally, or run in demo mode with `requirements-minimal.txt`.
- If ports are in use (8000/5432/8086), stop existing services or change port mappings in `.devcontainer/docker-compose.yml`.

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines, commit style, and PR process.
