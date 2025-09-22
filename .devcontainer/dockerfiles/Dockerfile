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

# Install Poetry
RUN pip install --upgrade pip \
    && pip install poetry==1.8.4

# Configure Poetry: Don't create virtual env (we're already in container)
RUN poetry config virtualenvs.create false

WORKDIR /workspace

# Pre-copy Poetry files for layer caching
COPY pyproject.toml poetry.loc[k] /tmp/
RUN cd /tmp && poetry install --only=main --no-root || poetry install --only=main,minimal --no-root || echo "Poetry install failed, will retry at runtime"# Simple wait-for utility (optional) available in PATH
ADD https://raw.githubusercontent.com/eficode/wait-for/v2.2.4/wait-for /usr/local/bin/wait-for
RUN chmod +x /usr/local/bin/wait-for

CMD ["sleep", "infinity"]
