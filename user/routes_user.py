"""
Handles routes for the user module.
"""

from flask import redirect, render_template, session, request

from core import database, handlers
from .models import User


def add_user_routes(app):
    """Add user routes."""

    @app.route("/user/register", methods=["GET", "POST"])
    def register():
        """Give page to register a new user."""
        if request.method == "POST":
            return User().register()
        return render_template("user/register.html")

    @app.route("/user/login", methods=["GET", "POST"])
    def login():
        """Gives login form to user."""
        if request.method == "POST":
            return User().login()
        if "logged_in" in session:
            return redirect("/")
        return render_template("user/login.html")

    @app.route("/user/change_password", methods=["GET", "POST"])
    def change_password():
        """Change user password."""
        if request.method == "POST":
            return User().change_password()
        return render_template("user/change_password.html")

    @app.route("/user/deadline", methods=["GET", "POST"])
    @handlers.login_required
    def deadline():
        """Change deadline."""
        if request.method == "POST":
            return User().change_deadline()
        return render_template(
            "user/deadline.html", deadline=database.get_details_deadline()
        )
