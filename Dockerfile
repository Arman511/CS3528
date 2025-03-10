FROM python:3.10.12-slim

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . /app

EXPOSE 8080

# Load environment variables from files
ENV BASE_EMAIL_FOR_STUDENTS=$(cat /etc/secrets/BASE_EMAIL_FOR_STUDENTS)
ENV EMAIL=$(cat /etc/secrets/EMAIL)
ENV EMAIL_PASSWORD=$(cat /etc/secrets/EMAIL_PASSWORD)
ENV GUNICORN_BIND=$(cat /etc/secrets/GUNICORN_BIND)
ENV GUNICORN_PROCESSES=$(cat /etc/secrets/GUNICORN_PROCESSES)
ENV GUNICORN_THREADS=$(cat /etc/secrets/GUNICORN_THREADS)
ENV IS_GITHUB_ACTION=$(cat /etc/secrets/IS_GITHUB_ACTION)
ENV MONGO_DB_PROD=$(cat /etc/secrets/MONGO_DB_PROD)
ENV MONGO_DB_TEST=$(cat /etc/secrets/MONGO_DB_TEST)
ENV MONGO_URI=$(cat /etc/secrets/MONGO_URI)
ENV OFFLINE=$(cat /etc/secrets/OFFLINE)
ENV PORT=$(cat /etc/secrets/PORT)
ENV SECRET_KEY=$(cat /etc/secrets/SECRET_KEY)
ENV SMTP=$(cat /etc/secrets/SMTP)
ENV SUPERUSER_EMAIL=$(cat /etc/secrets/SUPERUSER_EMAIL)
ENV SUPERUSER_PASSWORD=$(cat /etc/secrets/SUPERUSER_PASSWORD)

CMD ["gunicorn", "--config", "gunicorn_config.py", "app:app"]
