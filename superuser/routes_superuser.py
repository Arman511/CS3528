"""Super user routes"""

from flask import request, render_template
from core import handlers
from .model import Superuser


def add_superuser_routes(app):
    """Add superuser routes."""

    @app.route("/superuser/configure", methods=["GET", "POST"])
    @handlers.superuser_required
    def configure_settings():
        """Configure settings page"""
        if request.method == "GET":
            return render_template("superuser/configure.html", user_type="superuser")

        return Superuser().configure_settings(request.form)
