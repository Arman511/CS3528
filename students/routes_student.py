"""
Handles routes for the student module.
"""

import os
from dotenv import load_dotenv
from flask import redirect, render_template, request, session
from core import handlers
from courses.models import Course
from employers.models import Employers
from skills.models import Skill
from course_modules.models import Module
from .models import Student


def add_student_routes(app):
    """Add student routes."""

    @app.route("/students/add_student", methods=["POST"])
    @handlers.login_required
    def register_student_attempt():
        """Adding new student."""
        return Student().add_student()

    @app.route("/students/upload_xlsx", methods=["POST"])
    @handlers.login_required
    def upload_xlsx():
        """Route to upload students from a XLSX file."""
        load_dotenv()
        base_email = os.getenv("BASE_EMAIL_FOR_STUDENTS")
        file = request.files["file"]
        return Student().import_from_xlsx(base_email, file)

    @app.route("/students/upload", methods=["GET"])
    @handlers.login_required
    def upload_page():
        """Route to upload students from a XLSX file."""
        return render_template("/student/upload_student_data.html", user_type="admin")

    @app.route("/students/search")
    @handlers.login_required
    def search_page():
        """Getting student."""
        return render_template(
            "student/search_student.html",
            skills=Skill().get_skills(),
            courses=Course().get_courses(),
            user_type="admin",
        )

    @app.route("/students/search_students", methods=["POST"])
    @handlers.login_required
    def search_students():
        """Getting student."""
        data = request.get_json()
        # Build the query with AND logic
        query = []
        # 0 is match, 1 is in list
        if data.get("first_name"):
            query.append(("first_name", data["first_name"], 0))
        if data.get("last_name"):
            query.append(("last_name", data["last_name"], 0))
        if data.get("email"):
            query.append(("email", data["email"], 0))
        if data.get("student_id"):
            query.append(("student_id", data["student_id"], 0))
        if data.get("course"):
            query.append(("course", data["course"]), 0)
        if data.get("skills"):
            query.append(("skills", data["skills"], 1))
            # Match students with at least one of the provided skills
        if data.get("modules"):
            query.append(("modules", data["modules"], 1))
            # Match students with at least one of the provided modules
        return Student().search_students(query)

    @app.route("/students/delete_student/<int:student_id>", methods=["DELETE"])
    @handlers.login_required
    def delete_student(student_id):
        """Delete student."""
        return Student().delete_student_by_id(student_id)

    @app.route("/students/login", methods=["GET", "POST"])
    def login_student():
        """Logins a student"""
        if request.method == "POST":
            student_id = request.form.get("student_id")
            password = request.form.get("password")
            return Student().student_login(student_id, password)

        if "student" in session and "student_signed_in" in session:
            return redirect(
                "/students/details/" + str(session["student"]["student_id"])
            )
        return render_template("student/student_login.html")

    @app.route("/students/passed_deadline")
    def past_deadline():
        """Page for when the deadline has passed."""
        session.clear()
        return render_template("student/past_deadline.html")

    @app.route("/students/details/<int:student_id>", methods=["GET", "POST"])
    @handlers.student_login_required
    def student_details(student_id):
        """Get or update student details."""
        from app import DEADLINE_MANAGER

        if session["student"]["student_id"] != str(student_id):
            session.clear()
            return redirect("/students/login")

        # Handle deadlines (applicable to students only)
        if DEADLINE_MANAGER.is_past_student_ranking_deadline():
            return redirect("/students/passed_deadline")
        if DEADLINE_MANAGER.is_past_details_deadline():
            return redirect(f"/students/rank_preferences/{student_id}")

        # Handle POST request for updating details
        if request.method == "POST":
            student = {}
            student["comments"] = request.form.get("comments")
            student["skills"] = (
                request.form.get("skills")[1:-1].replace('"', "").split(",")
            )
            if student["skills"] == [""]:
                student["skills"] = []
            student["attempted_skills"] = (
                request.form.get("attempted_skills")[1:-1].replace('"', "").split(",")
            )
            if student["attempted_skills"] == [""]:
                student["attempted_skills"] = []
            student["has_car"] = request.form.get("has_car")
            student["placement_duration"] = (
                request.form.get("placement_duration")[1:-1].replace('"', "").split(",")
            )
            if student["placement_duration"] == [""]:
                student["placement_duration"] = []
            student["modules"] = (
                request.form.get("modules")[1:-1].replace('"', "").split(",")
            )
            if student["modules"] == [""]:
                student["modules"] = []
            student["course"] = request.form.get("course")
            return Student().update_student_by_id(student_id, student)

        # Render the template
        return render_template(
            "student/student_details.html",
            student=session["student"],
            skills=Skill().get_skills(),
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            attempted_skills=Skill().get_list_attempted_skills(),
            user_type="student",
        )

    @app.route("/students/update_student/", methods=["GET", "POST"])
    @handlers.login_required
    def update_student(student_id):
        """Update student for admins."""
        if request.method == "POST":
            student = {}
            uuid = request.args.get("uuid")
            student["student_id"] = request.form.get("student_id")
            student["first_name"] = request.form.get("first_name")
            student["last_name"] = request.form.get("last_name")
            student["email"] = request.form.get("email")
            student["course"] = request.form.get("course")
            student["comments"] = request.form.get("comments")
            student["skills"] = (
                request.form.get("skills")[1:-1].replace('"', "").split(",")
            )
            if student["skills"] == [""]:
                student["skills"] = []
            student["attempted_skills"] = (
                request.form.get("attempted_skills")[1:-1].replace('"', "").split(",")
            )
            if student["attempted_skills"] == [""]:
                student["attempted_skills"] = []
            student["has_car"] = request.form.get("has_car")
            student["placement_duration"] = (
                request.form.get("placement_duration")[1:-1].replace('"', "").split(",")
            )
            if student["placement_duration"] == [""]:
                student["placement_duration"] = []
            student["modules"] = (
                request.form.get("modules")[1:-1].replace('"', "").split(",")
            )
            if student["modules"] == [""]:
                student["modules"] = []
            student["course"] = request.form.get("course")
            return Student().update_student_by_uuid(uuid, student)

        student = Student().get_student_by_id(student_id)
        return render_template(
            "student/update_student.html",
            student=student,
            skills=Skill().get_skills(),
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            attempted_skills=Skill().get_list_attempted_skills(),
            user_type="admin",
        )

    @app.route("/students/rank_preferences/<int:student_id>", methods=["GET", "POST"])
    @handlers.student_login_required
    def rank_preferences(student_id):
        """Rank preferences."""
        from app import DEADLINE_MANAGER

        if "student" not in session:
            return redirect("/students/login")

        if session["student"]["student_id"] != str(student_id):
            session.clear()
            return redirect("/students/login")

        if DEADLINE_MANAGER.is_past_student_ranking_deadline():
            session.clear()
            render_template("student/past_deadline.html")

        if not DEADLINE_MANAGER.is_past_details_deadline():
            return redirect("/students/details/" + str(student_id))
        if request.method == "POST":
            preferences = [a[5:] for a in request.form.get("ranks").split(",")]
            return Student().rank_preferences(student_id, preferences)
        opportunities = Student().get_opportunities_by_student(student_id)
        return render_template(
            "student/student_rank_opportunities.html",
            opportunities=opportunities,
            employers_col=Employers().get_employer_by_id,
            user_type="student",
        )

    @app.route("/students/update_success")
    @handlers.student_login_required
    def student_update_successful():
        """Routing to deal with success"""
        session.clear()
        return render_template("student/update_successful_page.html")
