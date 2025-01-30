"""Handles the routes for the course module."""

from flask import render_template, request
from core import handlers
from .models import Course


def add_course_routes(app):
    """Courses routes"""

    @app.route("/courses/add_course", methods=["POST", "GET"])
    @handlers.login_required
    def add_course():
        if request.method == "GET":
            return render_template("/courses/adding_course.html", user_type="admin")
        return Course().add_course()
