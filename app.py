"""
This module initializes a Flask application, connects to a MongoDB database,
and defines routes with login-required decorators.
"""

from datetime import timedelta
import os
import sys
import signal
import threading
from dotenv import load_dotenv
from flask import Flask


sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from core.configuration_settings import Config  # noqa: E402
from core.database_mongo_manager import DatabaseMongoManager  # noqa: E402
from core import handlers, shared  # noqa: E402

DATABASE_MANAGER = None
DEADLINE_MANAGER = None
CONFIG_MANAGER = None

load_dotenv()


DATABASE = "cs3528_testing"

if shared.getenv("IS_TEST") == "True":
    print("In test mode")
    DATABASE = shared.getenv("MONGO_DB_TEST", "")
else:
    print("In production mode")
    DATABASE = shared.getenv("MONGO_DB_PROD", "")

DATABASE_MANAGER = DatabaseMongoManager(shared.getenv("MONGO_URI"), DATABASE)

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
PORT = int(shared.getenv("PORT", "5000"))
app.config["SECRET_KEY"] = shared.getenv("SECRET_KEY")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB
app.config["CACHE_TYPE"] = "SimpleCache"
app.config["CACHE_DEFAULT_TIMEOUT"] = 300
app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.permanent_session_lifetime = timedelta(minutes=30)


handlers.configure_routes(app)

from core.deadline_manager import DeadlineManager  # noqa: E402

DEADLINE_MANAGER = DeadlineManager()


def handle_kill_signal(_signum, _frame):
    """
    Handle the kill signal to gracefully shut down the server.
    """
    print("Kill signal received. Shutting down the server...")
    DATABASE_MANAGER.close_connection()
    sys.exit(0)


signal.signal(signal.SIGTERM, handle_kill_signal)


def run_app():
    """Run the Flask application."""
    try:
        app.run(port=PORT)
    except KeyboardInterrupt:
        DATABASE_MANAGER.close_connection()
        print("Shutting down the server...")
    except OSError:
        DATABASE_MANAGER.close_connection()
        print("Shutting down the server...")
    except RuntimeError as e:
        print(f"Runtime error: {e}")
    except ValueError as e:
        print(f"Value error: {e}")
    finally:
        DATABASE_MANAGER.close_connection()
        print("Shutting down the server...")


if __name__ == "__main__":
    app_thread = threading.Thread(target=run_app)
    app_thread.start()
    app_thread.join()
