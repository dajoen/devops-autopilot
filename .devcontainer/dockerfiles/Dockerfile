FROM mcr.microsoft.com/vscode/devcontainers/python:3.12

# Install system deps for common Python packages (asyncpg, psycopg, build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Optional: Pre-copy requirements to leverage Docker layer caching
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt || true

CMD ["sleep", "infinity"]
