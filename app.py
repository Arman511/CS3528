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
from core.database_mongo_manager import DatabaseMongoManager  # noqa: E402
from core import handlers  # noqa: E402

global database_manager
database_manager = None
global deadline_manager
deadline_manager = None

load_dotenv()

database = ""
if os.getenv("IS_GITHUB_ACTIONS") == "True":
    database = "cs3528_testing"
if os.getenv("IS_TEST"):
    database = os.getenv("MONGO_DB_TEST", "")
else:
    database = os.getenv("MONGO_DB_PROD", "")

database_manager = DatabaseMongoManager(os.getenv("MONGO_URI"), database)

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
]

for table in tables:
    database_manager.add_table(table)

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
app.permanent_session_lifetime = timedelta(minutes=30)
cache = Cache(app)
handlers.configure_routes(app, cache)

from core.deadline_manager import DeadlineManager  # noqa: E402

deadline_manager = DeadlineManager()

if __name__ == "__main__":
    app.run(debug=True)
