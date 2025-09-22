# DevOps Autopilot

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

## Running the Application

```bash
python main.py
```

The application will be available at http://localhost:8000 with:
- API docs: http://localhost:8000/docs
- Health check: http://localhost:8000/healthz

## Dev Container (VS Code)

This repository includes a VS Code Dev Container for consistent development:

- Services: Python 3.12 app container, Postgres 16, InfluxDB 2.7
- Auto-forwards: 8000 (API), 5432 (Postgres), 8086 (InfluxDB)

How to use:

1. Install the "Dev Containers" extension.
2. Open the repository in VS Code.
3. Reopen in container when prompted, or run "Dev Containers: Reopen in Container".
4. The API will run via `uvicorn` with `--reload` inside the container.

Environment inside the container is pre-configured via docker-compose for DB and Influx credentials. Adjust `config/config.yaml` or use env vars as needed.
