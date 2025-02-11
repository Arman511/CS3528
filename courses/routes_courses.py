"""Handles the routes for the course module."""

import uuid
from flask import render_template, request, send_file
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

    @app.route("/courses/delete", methods=["DELETE"])
    @handlers.login_required
    def delete_course():
        uuid = request.args.get("uuid")
        return Course().delete_course_by_uuid(uuid)

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
                "/courses/update.html", course=course, user_type="admin"
            )

        course = {
            "course_id": request.form.get("course_id").upper(),
            "course_name": request.form.get("course_name"),
            "course_description": request.form.get("course_description"),
        }
        return Course().update_course(id_val, course)

    @app.route("/courses/upload", methods=["GET", "POST"])
    @handlers.login_required
    def upload_courses():
        if request.method == "GET":
            return render_template("courses/upload.html", user_type="admin")

        file = request.files["file"]
        if not file:
            return {"error": "No file provided"}, 400
        if not handlers.allowed_file(file.filename, ["xlsx", "xls"]):
            return {"error": "Invalid file type"}, 400

        return Course().upload_course_data(file)

    @app.route("/courses/download_template", methods=["GET"])
    @handlers.login_required
    def download_courses_template():
        return send_file(
            "data_model_upload_template/courses_template.xlsx",
            as_attachment=True,
        )

    @app.route("/courses/delete_all", methods=["DELETE"])
    @handlers.login_required
    def delete_all_courses():
        return Course().delete_all_courses()

    @app.route("/courses/download_all", methods=["GET"])
    @handlers.login_required
    def download_all_courses():
        return Course().download_all_courses()
