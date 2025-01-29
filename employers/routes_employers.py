"""Routes for employers module"""

import os
from flask import jsonify, request, render_template, session
from itsdangerous import URLSafeSerializer
from core import database, handlers
from course_modules.models import Module
from courses.models import Course
from opportunities.models import Opportunity
from skills.models import Skill
from .models import Employers


def add_employer_routes(app):
    """Add employer routes."""

    @app.route("/employers/login", methods=["GET", "POST"])
    def employer_login():
        if request.method == "POST":
            return Employers().employer_login()

        return render_template("employers/employer_login.html", user_type="employer")

    @app.route("/employers/home", methods=["GET"])
    @handlers.employers_login_required
    def employer_home(employer):
        return render_template(
            "employers/employer_home.html", employer=employer, user_type="employer"
        )

    @app.route("/employers/otp", methods=["POST"])
    def employer_otp():

        if "employer" not in session:
            return jsonify({"error": "Employer not logged in."}), 400
        otp_serializer = URLSafeSerializer(str(os.getenv("SECRET_KEY", "secret")))
        if "OTP" not in session:
            return jsonify({"error": "OTP not sent."}), 400
        if request.form.get("otp") != otp_serializer.loads(session["OTP"]):
            return jsonify({"error": "Invalid OTP."}), 400

        return Employers().start_session()

    @app.route("/employers/add_employer", methods=["GET", "POST"])
    @handlers.login_required
    def add_employer():
        if request.method == "POST":
            return Employers().register_employer()
        return render_template("employers/add_employer.html", user_type="admin")

    @app.route("/employers/rank_students", methods=["GET", "POST"])
    @handlers.employers_login_required
    def employers_rank_students():
        if database.is_past_opportunities_ranking_deadline() and "employer" in session:
            return render_template(
                "employers/past_deadline.html",
                data=(
                    f"Ranking deadline has passed as of "
                    f"{database.get_opportunities_ranking_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],
            )
        opportunity_id = request.args.get("opportunity_id")
        if not opportunity_id:
            return jsonify({"error": "Need opportunity ID."}), 400
        opportunity = Opportunity().get_opportunity_by_id(opportunity_id)
        if session["employer"]["_id"] != opportunity["employer_id"]:
            return jsonify({"error": "Employer does not own this opportunity."}), 400
        if not database.is_past_student_ranking_deadline():
            return render_template(
                "employers/past_deadline.html",
                data=(
                    "Student ranking deadline must have passed before you can start, "
                    f"wait till {database.get_student_ranking_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],
            )
        if request.method == "POST":
            return Opportunity().rank_preferences(opportunity_id)
        valid_students = Opportunity().get_valid_students(opportunity_id)
        return render_template(
            "opportunities/employer_rank_students.html",
            opportunity_id=opportunity_id,
            students=valid_students,
            get_course_name=Course().get_course_name_by_id,
            get_module_name=Module().get_module_name_by_id,
            get_skill_name=Skill().get_skill_name_by_id,
            user_type="employer",
        )
