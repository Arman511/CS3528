"""Debug routes for the app."""

from functools import wraps
import os

from flask import jsonify, redirect, session


def is_test_required(f):
    """Decorator to check if the app is running in test mode."""

    @wraps(f)
    def wrap(*args, **kwargs):
        if os.getenv("IS_TEST") == "True":
            return f(*args, **kwargs)

        return redirect("/students/login")

    return wrap


def add_debug_routes(app):
    """Add debug routes to the app."""

    @app.route("/debug/session")
    @is_test_required
    def get_session_debug():
        return jsonify(dict(session)), 200
