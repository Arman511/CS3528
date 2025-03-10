# Use Python slim image
FROM python:3.10.12-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/requirements.txt

RUN python -m venv .venv && \
    .venv/bin/activate && \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV PATH=".venv/bin:$PATH"

# Copy the entire application code
COPY . /app

# Expose the application port
EXPOSE 8080

# Command to run Gunicorn with secrets loaded
CMD /load_secrets.sh && gunicorn --config gunicorn_config.py app:app
