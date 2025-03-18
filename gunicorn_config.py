"""Gunicorn configuration file."""

import multiprocessing
import logging
from dotenv import load_dotenv

from core import shared

load_dotenv()

# Gunicorn settings
workers = int(
    shared.getenv("GUNICORN_PROCESSES", str((multiprocessing.cpu_count() * 2) + 1))
)
threads = int(shared.getenv("GUNICORN_THREADS", str(workers)))
bind = shared.getenv("GUNICORN_BIND", "0.0.0.0:8080")
timeout = 120
max_requests = 1000
max_requests_jitter = 50
FORWARD_ALLOW_IPS = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}

# Logging settings
loglevel = shared.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = shared.getenv("GUNICORN_ACCESS_LOG", "-")  # "-" means stdout
errorlog = shared.getenv("GUNICORN_ERROR_LOG", "-")

logger = logging.getLogger("gunicorn.error")
logger.setLevel(loglevel.upper())
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.info("Gunicorn configuration loaded with logging enabled.")
