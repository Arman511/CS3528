FROM python:3.13-alpine

ENV PYTHONUNBUFFERED=1 \
    VENV_PATH="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN apk add --no-cache \
    gcc \
    libffi-dev \
    musl-dev \
    openssl-dev \
    python3-dev && \
    python -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENTRYPOINT ["gunicorn"]
CMD ["--config", "gunicorn_config.py", "app:app"]
