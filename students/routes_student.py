"""
Handles routes for the student module.
"""

import os
import uuid
from dotenv import load_dotenv
from flask import jsonify, redirect, render_template, request, session
from itsdangerous import URLSafeSerializer
from core import handlers
from courses.models import Course
from employers.models import Employers
from skills.models import Skill
from course_modules.models import Module
from .models import Student


def add_student_routes(app):
    """Add student routes."""

    @app.route("/students/add_student", methods=["GET", "POST"])
    @handlers.login_required
    def register_student_attempt():
        """Adding new student."""
        if request.method == "GET":
            return render_template(
                "student/add_student.html",
                courses=Course().get_courses(),
                modules=Module().get_modules(),
                user_type="admin",
                page="students",
            )
        student = request.json

        if student["modules"] == [""]:
            student["modules"] = []

        if not student["student_id"]:
            return jsonify({"error": "Please enter a student ID"}), 400
        if not student["first_name"]:
            return jsonify({"error": "Please enter a first name"}), 400
        if not student["last_name"]:
            return jsonify({"error": "Please enter a last name"}), 400
        if not student["email"]:
            return jsonify({"error": "Please enter an email"}), 400
        if not student["course"]:
            return jsonify({"error": "Please select a course"}), 400
        if not student["comments"]:
            student["comments"] = ""

        student["_id"] = uuid.uuid4().hex

        return Student().add_student(student)

    @app.route("/students/upload", methods=["GET", "POST"])
    @handlers.login_required
    def upload_page():
        """Route to upload students from a XLSX file."""
        if request.method == "GET":
            return render_template(
                "/student/upload_student_data.html", user_type="admin", page="students"
            )
        load_dotenv()
        base_email = os.getenv("BASE_EMAIL_FOR_STUDENTS")
        if "file" not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files["file"]

        if not handlers.allowed_file(file.filename, ["xlsx", "xls"]):
            return jsonify({"error": "Invalid file type"}), 400

        return Student().import_from_xlsx(base_email, file)

    @app.route("/students/search")
    @handlers.login_required
    def search_page():
        """Getting student."""
        return render_template(
            "student/search_student.html",
            skills_map=Skill().get_skills_map(),
            skills=Skill().get_skills(),
            courses_map=Course().get_courses_map(),
            courses=Course().get_courses(),
            modules_map=Module().get_modules_map(),
            modules=Module().get_modules(),
            students=Student().get_students(),
            user_type="admin",
            page="students",
        )

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
            return Student().student_login(student_id)

        if "student" in session and "student_logged_in" in session:
            return redirect(
                "/students/details/" + str(session["student"]["student_id"])
            )
        return render_template("student/student_login.html")

    @app.route("/students/otp", methods=["POST"])
    def student_otp():

        if "student" not in session:
            return jsonify({"error": "Employer not logged in."}), 400
        otp_serializer = URLSafeSerializer(str(os.getenv("SECRET_KEY", "secret")))
        if "OTP" not in session:
            return jsonify({"error": "OTP not sent."}), 400
        if request.form.get("otp") != otp_serializer.loads(session["OTP"]):
            return jsonify({"error": "Invalid OTP."}), 400

        session["student_logged_in"] = True

        return jsonify({"message": "OTP verified"}), 200

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
        from app import CONFIG_MANAGER

        if session["student"]["student_id"] != str(student_id):
            session.clear()
            return redirect("/students/login")

        # Handle deadlines (applicable to students only)
        if (
            DEADLINE_MANAGER.is_past_student_ranking_deadline()
            and request.method == "GET"
        ):
            return redirect("/students/passed_deadline")
        if DEADLINE_MANAGER.is_past_details_deadline() and request.method == "GET":
            return redirect(f"/students/rank_preferences/{student_id}")

        # Handle POST request for updating details
        if request.method == "POST":
            student = {}
            student["comments"] = request.form.get("comments")
            skills = request.form.get("skills").split(",")
            attempted_skills = request.form.get("attempted_skills").split(",")
            max_skills = CONFIG_MANAGER.get_max_num_of_skills()
            total_skills = len(skills) + len(attempted_skills)

            if total_skills > max_skills:
                skills = skills[: max_skills - len(attempted_skills)]

            student["skills"] = [skill for skill in skills if skill]
            student["attempted_skills"] = [skill for skill in attempted_skills if skill]
            student["has_car"] = request.form.get("has_car")
            student["placement_duration"] = request.form.get(
                "placement_duration"
            ).split(",")
            if (
                student["placement_duration"] == [""]
                or student["placement_duration"] == []
            ):
                return jsonify({"error": "Please select a placement duration"}), 400
            valid_durations = set(
                ["1_day", "1_week", "1_month", "3_months", "6_months", "12_months"]
            )
            if not set(student["placement_duration"]).issubset(valid_durations):
                return jsonify({"error": "Invalid placement duration"}), 400
            student["modules"] = request.form.get("modules").split(",")
            if student["modules"] == [""]:
                student["modules"] = []
            student["course"] = request.form.get("course")
            if student["course"] == "":
                return jsonify({"error": "Please select a course"}), 400
            student["course"] = student["course"].upper()
            return Student().update_student_by_id(student_id, student)

        # Render the template
        return render_template(
            "student/student_details.html",
            student=session["student"],
            skills=Skill().get_skills(),
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            attempted_skill_map={
                skill["_id"]: skill for skill in Skill().get_list_attempted_skills()
            },
            user_type="student",
            max_num_skills=CONFIG_MANAGER.get_max_num_of_skills(),
        )

    @app.route("/students/update_student", methods=["GET", "POST"])
    @handlers.login_required
    def update_student():
        """Update student for admins."""
        if request.method == "POST":
            student = {}
            uuid = request.args.get("uuid")
            if not uuid or uuid == "":
                return jsonify({"error": "Invalid request"}), 404
            student["student_id"] = request.form.get("student_id")
            student["first_name"] = request.form.get("first_name")
            student["last_name"] = request.form.get("last_name")
            student["email"] = request.form.get("email")
            student["course"] = request.form.get("course")
            student["comments"] = request.form.get("comments")
            student["skills"] = request.form.get("skills").split(",")

            if student["skills"] == [""]:
                student["skills"] = []
            student["attempted_skills"] = request.form.get("attempted_skills").split(
                ","
            )

            if student["attempted_skills"] == [""]:
                student["attempted_skills"] = []
            student["has_car"] = request.form.get("has_car")
            student["placement_duration"] = request.form.get(
                "placement_duration"
            ).split(",")

            if (
                student["placement_duration"] == [""]
                or student["placement_duration"] == []
            ):
                return jsonify({"error": "Please select a placement duration"}), 400
            valid_durations = set(
                ["1_day", "1_week", "1_month", "3_months", "6_months", "12_months"]
            )
            if not set(student["placement_duration"]).issubset(valid_durations):
                return jsonify({"error": "Invalid placement duration"}), 400
            student["modules"] = request.form.get("modules").split(",")

            if student["modules"] == [""]:
                student["modules"] = []
            if student["course"] == "":
                return jsonify({"error": "Please select a course"}), 400
            student["course"] = student["course"].upper()
            return Student().update_student_by_uuid(uuid, student)

        uuid = request.args.get("uuid")
        student = Student().get_student_by_uuid(uuid)
        return render_template(
            "student/update_student.html",
            student=student,
            skills=Skill().get_skills(),
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            attempted_skills=Skill().get_list_attempted_skills(),
            user_type="admin",
            page="students",
        )

    @app.route("/students/rank_preferences/<int:student_id>", methods=["GET", "POST"])
    @handlers.student_login_required
    def rank_preferences(student_id):
        """Rank preferences."""
        from app import DEADLINE_MANAGER
        from app import CONFIG_MANAGER

        if "student" not in session:
            return redirect("/students/login")

        if session["student"]["student_id"] != str(student_id):
            session.clear()
            return redirect("/students/login")

        if (
            DEADLINE_MANAGER.is_past_student_ranking_deadline()
            and request.method == "GET"
        ):
            session.clear()
            render_template("student/past_deadline.html")

        if not DEADLINE_MANAGER.is_past_details_deadline():
            return redirect("/students/details/" + str(student_id))
        opportunities = Student().get_opportunities_by_student(student_id)
        if request.method == "POST":
            preferences = [a[5:].strip() for a in request.form.get("ranks").split(",")]
            min_ranked = CONFIG_MANAGER.get_min_num_ranking_student_to_opportunities()
            if len(opportunities) > min_ranked:
                if len(preferences) < min_ranked:
                    return (
                        jsonify(
                            {
                                "error": "Please rank at least "
                                + str(min_ranked)
                                + " opportunities"
                            }
                        ),
                        400,
                    )
            return Student().rank_preferences(student_id, preferences)
        return render_template(
            "student/student_rank_opportunities.html",
            opportunities=opportunities,
            employers_col=Employers().get_employer_by_id,
            user_type="student",
            min_ranked=CONFIG_MANAGER.get_min_num_ranking_student_to_opportunities(),
        )

    @app.route("/students/update_success")
    @handlers.student_login_required
    def student_update_successful():
        """Routing to deal with success"""
        session.clear()
        return render_template("student/update_successful_page.html")

    @app.route("/students/download", methods=["GET"])
    @handlers.login_required
    def download_all_students():
        """Download students."""
        return Student().download_students()

    @app.route("/students/delete_all", methods=["DELETE"])
    @handlers.login_required
    def delete_all_students():
        """Delete all students."""
        return Student().delete_all_students()
