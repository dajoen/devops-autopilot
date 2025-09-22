FROM mcr.microsoft.com/vscode/devcontainers/python:3.13

# Install system deps for common Python packages (asyncpg, psycopg, build tools)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        libpq-dev \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Optional: Pre-copy requirements to leverage Docker layer caching
COPY requirements.txt /tmp/requirements.txt
COPY requirements-minimal.txt /tmp/requirements-minimal.txt
RUN pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt || pip install -r /tmp/requirements-minimal.txt

# Simple wait-for utility (optional) available in PATH
ADD https://raw.githubusercontent.com/eficode/wait-for/v2.2.4/wait-for /usr/local/bin/wait-for
RUN chmod +x /usr/local/bin/wait-for

CMD ["sleep", "infinity"]
