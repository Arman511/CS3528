# Use Python slim image
FROM python:3.10.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt

RUN python -m venv .venv && \
    . .venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV PATH=".venv/bin:$PATH"

# Copy the entire application code
COPY . /app

# Expose the application port
EXPOSE 8080

# Create a script to load secrets into environment variables
RUN echo '#!/bin/sh' > /load_secrets.sh && \
    echo 'export BASE_EMAIL_FOR_STUDENTS=$(cat /etc/secrets/BASE_EMAIL_FOR_STUDENTS)' >> /load_secrets.sh && \
    echo 'export EMAIL=$(cat /etc/secrets/EMAIL)' >> /load_secrets.sh && \
    echo 'export EMAIL_PASSWORD=$(cat /etc/secrets/EMAIL_PASSWORD)' >> /load_secrets.sh && \
    echo 'export GUNICORN_BIND=$(cat /etc/secrets/GUNICORN_BIND)' >> /load_secrets.sh && \
    echo 'export GUNICORN_PROCESSES=$(cat /etc/secrets/GUNICORN_PROCESSES)' >> /load_secrets.sh && \
    echo 'export GUNICORN_THREADS=$(cat /etc/secrets/GUNICORN_THREADS)' >> /load_secrets.sh && \
    echo 'export IS_GITHUB_ACTION=$(cat /etc/secrets/IS_GITHUB_ACTION)' >> /load_secrets.sh && \
    echo 'export MONGO_DB_PROD=$(cat /etc/secrets/MONGO_DB_PROD)' >> /load_secrets.sh && \
    echo 'export MONGO_DB_TEST=$(cat /etc/secrets/MONGO_DB_TEST)' >> /load_secrets.sh && \
    echo 'export MONGO_URI=$(cat /etc/secrets/MONGO_URI)' >> /load_secrets.sh && \
    echo 'export OFFLINE=$(cat /etc/secrets/OFFLINE)' >> /load_secrets.sh && \
    echo 'export PORT=$(cat /etc/secrets/PORT)' >> /load_secrets.sh && \
    echo 'export SECRET_KEY=$(cat /etc/secrets/SECRET_KEY)' >> /load_secrets.sh && \
    echo 'export SMTP=$(cat /etc/secrets/SMTP)' >> /load_secrets.sh && \
    echo 'export SUPERUSER_EMAIL=$(cat /etc/secrets/SUPERUSER_EMAIL)' >> /load_secrets.sh && \
    echo 'export SUPERUSER_PASSWORD=$(cat /etc/secrets/SUPERUSER_PASSWORD)' >> /load_secrets.sh && \
    chmod +x /load_secrets.sh

# Command to run Gunicorn with secrets loaded
CMD /load_secrets.sh && gunicorn --config gunicorn_config.py app:app
