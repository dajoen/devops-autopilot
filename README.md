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
