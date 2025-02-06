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
    
    @app.route("/courses/search")
    @handlers.login_required
    def search_courses_page():
        """Getting course."""
        return render_template(
            "courses/search_courses.html",
            courses=Course().get_courses(),
            user_type="admin",
        )
    
    @app.route("/courses/search_courses", methods=["POST"])
    @handlers.login_required
    def search_courses():
        """Getting course."""
        return Course().search_courses()
