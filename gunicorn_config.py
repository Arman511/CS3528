"""Gunicorn configuration file."""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Gunicorn settings
workers = int(os.getenv("GUNICORN_PROCESSES", "2"))
threads = int(os.getenv("GUNICORN_THREADS", "4"))
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8080")
FORWARD_ALLOW_IPS = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

# Logging settings
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = os.getenv("GUNICORN_ACCESS_LOG", "-")  # "-" means stdout
errorlog = os.getenv("GUNICORN_ERROR_LOG", "-")  # "-" means stderr

# Configuring logging
logger = logging.getLogger("gunicorn.error")
logger.setLevel(loglevel.upper())
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Gunicorn configuration loaded with logging enabled.")
