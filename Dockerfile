FROM python:3.10.12-slim

COPY requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . /app

EXPOSE 8080

CMD gunicorn --config gunicorn_config.py app:app
