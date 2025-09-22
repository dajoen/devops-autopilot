# Contributing

Thanks for contributing to DevOps Autopilot!

## Local Setup

- Python 3.12 recommended. Or use the VS Code Dev Container.
- Demo run (no DB drivers):
  - `python3 -m venv venv && source venv/bin/activate`
  - `pip install -r requirements-minimal.txt`
  - `python run_demo.py`
- Full run:
  - `pip install -r requirements.txt`
  - Ensure Postgres and InfluxDB are available
  - `uvicorn main:app --reload`

## Dev Container

- Open in VS Code and choose "Reopen in Container".
- Services: Postgres + InfluxDB available inside compose network.

## Commit Style

- Use conventional commits, e.g.:
  - `feat(core): add settings facade`
  - `fix(health): handle missing token`
  - `docs(readme): add demo quickstart`

## Branching

- `develop`: active development
- `main`: stable releases

## Pull Requests

- Fill the PR template
- Link issues/stories
- Ensure CI passes
- Include tests when behavior changes

## Security

- Do not commit secrets. Use environment variables.
