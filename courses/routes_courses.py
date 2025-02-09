"""Handles the routes for the course module."""

import uuid
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

        course = {
            "_id": uuid.uuid1().hex,
            "course_id": request.form.get("course_id"),
            "course_name": request.form.get("course_name"),
            "course_description": request.form.get("course_description"),
        }
        return Course().add_course(course)

    @app.route("/courses/delete_course", methods=["POST"])
    @handlers.login_required
    def delete_course():
        uuid = request.args.get("uuid")
        return Course().delete_course(uuid)

    @app.route("/courses/search", methods=["GET"])
    @handlers.login_required
    def search_course():
        courses = Course().get_courses()

        return render_template(
            "/courses/search.html", courses=courses, user_type="admin"
        )

    @app.route("/courses/update", methods=["GET", "POST"])
    @handlers.login_required
    def update_course():
        id_val = request.args.get("uuid")
        if request.method == "GET":
            course = Course().get_course_by_uuid(id_val)
            return render_template(
                "/courses/update_course.html", course=course, user_type="admin"
            )

        course = {
            "course_id": request.form.get("course_id"),
            "course_name": request.form.get("course_name"),
            "course_description": request.form.get("course_description"),
        }
        return Course().update_course(id_val, course)
