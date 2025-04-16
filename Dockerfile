# Use Python slim image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    VENV_PATH="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install system dependencies and create a virtual environment
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    build-essential && \
    python -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --no-cache-dir --upgrade pip setuptools wheel && \
    apt-get purge -y --auto-remove gcc build-essential && \
    rm -rf /var/lib/apt/lists/*

# Pre-copy requirements to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose application port
EXPOSE 8080

# Gunicorn entrypoint
ENTRYPOINT ["gunicorn"]
CMD ["--config", "gunicorn_config.py", "app:app"]
