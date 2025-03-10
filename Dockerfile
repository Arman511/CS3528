# Use Python slim image
FROM python:3.10.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    VENV_PATH="/app/.venv" \
    PATH="/app/.venv/bin:$PATH"

# Set the working directory
WORKDIR /app

# Install dependencies and create virtual environment in one step
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    python -m venv $VENV_PATH && \
    $VENV_PATH/bin/pip install --no-cache-dir --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency file first to leverage Docker cache
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . /app

# Create a non-root user
RUN adduser --disabled-login --no-create-home appuser && chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Expose the application port
EXPOSE 8080

# Use Gunicorn with a configuration file
ENTRYPOINT ["gunicorn"]
CMD ["--config", "gunicorn_config.py", "app:app"]
