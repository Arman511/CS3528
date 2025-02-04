"""
This module initializes a Flask application, connects to a MongoDB database,
and defines routes with login-required decorators.
"""

from datetime import timedelta
import os
import sys
from dotenv import load_dotenv
from flask import Flask
from flask_caching import Cache

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core import handlers  # pylint: disable=C0413
from core.database_mongo_manager import DatabaseMongoManager  # pylint: disable=C0413

load_dotenv()
app = Flask(__name__)

database = ""

if os.getenv("IS_TEST"):
    database = os.getenv("MONGO_URI_TEST", "")
else:
    database = os.getenv("MONGO_URI_PROD", "")

database_manager = DatabaseMongoManager(os.getenv("MONGO_URI"), database)

app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
app.permanent_session_lifetime = timedelta(minutes=30)
cache = Cache(app)
handlers.configure_routes(app, cache)

if __name__ == "__main__":
    app.run()
