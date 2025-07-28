# ---- Base image ----
FROM python:3.11-slim

# ---- Set environment variables ----
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2

# ---- System deps ----
RUN apt-get update && apt-get install -y curl build-essential && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# ---- Set workdir ----
WORKDIR /app

# ---- Copy poetry files and install deps ----
COPY pyproject.toml poetry.lock /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# ---- Copy the rest of the code ----
COPY . /app

# ---- Expose port and run ----
EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--reload", "--port", "8000", "--host", "0.0.0.0"]