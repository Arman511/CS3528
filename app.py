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
from core.configuration_settings import Config  # noqa: E402
from core.database_mongo_manager import DatabaseMongoManager  # noqa: E402
from core import handlers  # noqa: E402

DATABASE_MANAGER = None
DEADLINE_MANAGER = None
CONFIG_MANAGER = None

load_dotenv()

os.environ["IS_TEST"] = "True"

DATABASE = "cs3528_testing"

if os.getenv("IS_TEST") == "True":
    print("In test mode")
    DATABASE = os.getenv("MONGO_DB_TEST", "")
else:
    print("In production mode")
    DATABASE = os.getenv("MONGO_DB_PROD", "")

DATABASE_MANAGER = DatabaseMongoManager(os.getenv("MONGO_URI"), DATABASE)

tables = [
    "users",
    "students",
    "opportunities",
    "courses",
    "skills",
    "attempted_skills",
    "modules",
    "employers",
    "deadline",
    "config",
]

for table in tables:
    DATABASE_MANAGER.add_table(table)

CONFIG_MANAGER = Config(DATABASE_MANAGER)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
app.permanent_session_lifetime = timedelta(minutes=30)
cache = Cache(app)
handlers.configure_routes(app, cache)

from core.deadline_manager import DeadlineManager  # noqa: E402

DEADLINE_MANAGER = DeadlineManager()

if __name__ == "__main__":
    try:
        app.run()
    except KeyboardInterrupt:
        DATABASE_MANAGER.close_connection()
        print("Shutting down the server...")
