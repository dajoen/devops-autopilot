# DevOps Autopilot

![CI](https://github.com/dajoenA modern FastAPI application for automated DevOps operations with PostgreSQL and InfluxDB integration.

## Features

- **FastAPI Framework**: High-performance async web framework with automatic OpenAPI documentation
- **Multiple Operation Modes**: Full mode with databases or lightweight demo mode
- **Database Integration**: 
  - PostgreSQL with async SQLAlchemy for operational data
  - InfluxDB 2.0 for metrics and time-series data
- **LLM Integration**: Pluggable provider system supporting LocalAI, OpenAI, and custom providers
- **External APIs**: Bamboo CI/CD integration with authentication
- **Configuration Management**: YAML-based config with environment variable overrides
- **Strict Validation**: Pydantic models with SecretStr for sensitive data
- **Health Monitoring**: Comprehensive health checks with database connectivity
- **Dev Container**: Complete development environment with PostgreSQL and InfluxDB
- **Poetry**: Modern dependency management with lock filesvops-autopilot/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.13-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A modern FastAPI application for automated DevOps operations with PostgreSQL and InfluxDB integration.

## Features


## Project Structure

```
devops-autopilot/
├── backend/
│   ├── core/             # Config manager, DB/Influx managers, Settings facade
│   ├── models/           # Pydantic data models (config, health, runs, logs)
│   └── services/         # Business logic and LLM providers
├── routers/              # FastAPI route handlers
├── config/               # Configuration files (YAML)
├── tests/                # Unit tests with pytest
├── .devcontainer/        # Dev Container with PostgreSQL + InfluxDB
├── .github/workflows/    # CI/CD pipelines
├── main.py               # Full application (DB + Influx initialization)
├── main_demo.py          # Demo application (no external drivers needed)
├── run_demo.py           # Demo runner script
├── pyproject.toml        # Poetry configuration and dependencies
└── poetry.lock           # Locked dependency versions
```

## Quickstart (Demo mode)

Use this when you want to run immediately without installing DB drivers.

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install minimal dependencies for demo mode
poetry install --only=main,minimal

# Run demo mode (easiest way)
poetry run demo
```

Browse:
- Docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/healthz

## Full setup (Local)

Recommended Python: 3.13 (or use the Dev Container below).

```bash
# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install all dependencies
poetry install --with dev

# Run the application
poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Ensure your Postgres and InfluxDB are available, or use the Dev Container which provides both.

## Dev Container (Recommended)

This repository includes a complete VS Code Dev Container setup:

**Services:**
- Python 3.13 app container with Poetry
- PostgreSQL 16 (port 5432)
- InfluxDB 2.7 (port 8086)

**Quick Start:**
1. Install the "Dev Containers" extension in VS Code
2. Open this repository in VS Code
3. Choose "Reopen in Container" when prompted
4. Services start automatically with health checks
5. Run the app: `poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`

**Default Credentials:**
- PostgreSQL: `postgres/postgres` → `devops_autopilot` database
- InfluxDB: Org `dev-org`, Bucket `devops-metrics`, Token `dev-token`

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

## Settings & Configuration

The app uses a strict configuration system with validation:

```python
from backend.core.settings import Settings

# Initialize settings (loads config.yaml + env overrides)
s = Settings()

# Database connection
dsn = s.postgres_dsn()  # postgresql+asyncpg://user:pass@host:port/db

# InfluxDB config
url, org, bucket, token = s.influx_config()

# LLM provider (validates configuration)
provider = s.provider()  # e.g., "localai", "dummy"

# Bamboo CI integration
base_url, username, token = s.bamboo_auth()
```

**Environment Variables:**
- Database: `DB_HOST`, `DB_PORT`, `DB_DATABASE`, `DB_USERNAME`, `DB_PASSWORD`
- InfluxDB: `INFLUXDB_URL`, `INFLUXDB_TOKEN`, `INFLUXDB_ORG`, `INFLUXDB_BUCKET`
- LLM: `LLM_PROVIDER`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`
- Bamboo: `BAMBOO_BASE_URL`, `BAMBOO_USERNAME`, `BAMBOO_TOKEN`

## API Endpoints

**Health & Status:**
- `GET /healthz` — Comprehensive health check with database status
- `GET /healthz/ping` — Simple alive check
- `GET /` — API information and status

**LLM Operations:**
- `POST /llm/generate` — Generate text using configured LLM provider
- `GET /llm/models` — List available models
- `GET /llm/usage` — Usage statistics

**DevOps Integration:**
- `GET /bamboo/*` — Bamboo CI/CD operations
- `GET /reports/*` — Generate reports
- `GET /config/*` — Configuration management

**Documentation:**
- `GET /docs` — Interactive OpenAPI/Swagger UI
- `GET /redoc` — ReDoc documentation

## Troubleshooting

**Python 3.13 Compatibility:**
- Some binary wheels may be unavailable. Use Poetry's minimal install: `poetry install --only=main,minimal`
- Alternatively, use the Dev Container (Python 3.13 + pre-built dependencies)
- For local development, Python 3.12 works perfectly with all dependencies

**Port Conflicts:**
- API (8000), PostgreSQL (5432), or InfluxDB (8086) ports in use
- Stop existing services: `docker stop $(docker ps -q)`
- Or modify port mappings in `.devcontainer/docker-compose.yml`

**Configuration Issues:**
- Missing config: Copy `config/config.yaml` and update database credentials
- Environment variables override YAML settings
- Use `Settings().postgres_dsn()` to validate database config

**Dev Container Problems:**
- Rebuild container: "Dev Containers: Rebuild and Reopen in Container"
- Check Docker is running: `docker version`
- Clear Docker cache: `docker system prune`

### Development Commands

```bash
# Dependency Management
poetry install --with dev          # All dependencies + dev tools
poetry install --only=main,minimal # Minimal set for demo mode
poetry update                       # Update dependencies
poetry show --tree                  # Show dependency tree

# Running the Application
poetry run demo                         # Demo mode (no databases)
poetry run dev                          # Full mode (requires databases)
poetry run python run_demo.py          # Demo mode (alternative)
poetry run uvicorn main:app --reload   # Full mode with auto-reload

# Testing & Quality
poetry run pytest                    # Run all tests
poetry run pytest --cov=backend     # With coverage report
poetry run pytest -v tests/         # Verbose test output

# Code Formatting & Linting
poetry run black .                   # Format code
poetry run isort .                   # Sort imports
poetry run flake8 backend routers   # Lint code
poetry run mypy backend routers     # Type checking

# All quality checks at once
poetry run black . && poetry run isort . && poetry run flake8 backend routers && poetry run mypy backend routers
```

## Contributing

Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for:
- Development setup and workflow
- Code style guidelines (Black + isort)
- Commit message format
- Pull request process
- Testing requirements

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.
