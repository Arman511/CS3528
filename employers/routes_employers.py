"""Routes for employers module"""

import os
import uuid
from flask import flash, jsonify, redirect, request, render_template, session, url_for
from itsdangerous import URLSafeSerializer
from core import handlers
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
            email = request.form.get("email")
            return Employers().employer_login(email)

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
            employer = {
                "_id": uuid.uuid1().hex,
                "company_name": request.form.get("company_name"),
                "email": request.form.get("email"),
            }
            return Employers().register_employer(employer)
        return render_template("employers/add_employer.html", user_type="admin")

    @app.route("/employers/search_employers", methods=["GET", "POST"])
    @handlers.login_required
    def search_employers():
        if request.method == "POST":
            data = request.get_json()
            title = data.get("title", "").strip().lower()
            email = data.get("email", "").strip().lower()

            # Get all employers
            employers = Employers().get_employers()

            # Filter employers based on search criteria
            filtered_employers = [
                employer
                for employer in employers
                if (title in employer["company_name"].lower() if title else True)
                and (email in employer["email"].lower() if email else True)
            ]

            return jsonify(filtered_employers)

        # Render search page for GET requests
        return render_template("employers/search_employers.html", user_type="admin")

    @app.route("/employers/update_employer", methods=["GET", "POST"])
    @handlers.login_required
    def update_employer():
        from app import DATABASE_MANAGER

        employer_id = request.args.get("employer_id")  # Get employer_id from URL query
        if request.method == "POST":
            employer_id = request.form.get("employer_id")

            update_data = {
                "company_name": request.form.get("company_name"),
                "email": request.form.get("email"),
            }
            return Employers().update_employer(employer_id, update_data)

        employer = DATABASE_MANAGER.get_one_by_id("employers", employer_id)
        if not employer:
            flash("Employer not found", "error")
            return redirect(url_for("search_employers"))

        return render_template(
            "employers/update_employer.html", user_type="admin", employer=employer
        )

    @app.route("/employers/delete_employer", methods=["POST"])
    @handlers.login_required
    def delete_employer():
        data = request.get_json()  # Get JSON data from the request
        employer_id = data.get("employer_id")  # Extract employer_id from JSON

        if not employer_id:
            return jsonify({"error": "Employer ID is required"}), 400

        response = Employers().delete_employer_by_id(
            employer_id
        )  # Call delete function

        return response  # `delete_employer_by_id` already returns a JSON response

    @app.route("/employers/rank_students", methods=["GET", "POST"])
    @handlers.employers_login_required
    def employers_rank_students(_stuff):
        from app import DEADLINE_MANAGER

        if (
            DEADLINE_MANAGER.is_past_opportunities_ranking_deadline()
            and "employer" in session
        ):
            return render_template(
                "employers/past_deadline.html",
                data=(
                    f"Ranking deadline has passed as of "
                    f"{DEADLINE_MANAGER.get_opportunities_ranking_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],
                user_type="employer",
            )
        opportunity_id = request.args.get("opportunity_id")
        if not opportunity_id:
            return jsonify({"error": "Need opportunity ID."}), 400
        opportunity = Opportunity().get_opportunity_by_id(opportunity_id)
        if session["employer"]["_id"] != opportunity["employer_id"]:
            return jsonify({"error": "Employer does not own this opportunity."}), 400
        if not DEADLINE_MANAGER.is_past_student_ranking_deadline():
            return render_template(
                "employers/past_deadline.html",
                data=(
                    "Student ranking deadline must have passed before you can start, "
                    f"wait till {DEADLINE_MANAGER.get_student_ranking_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],
            )
        if request.method == "POST":
            ranks = request.form.get("ranks")
            preferences = [a[5:].strip() for a in ranks.split(",")]
            return Opportunity().rank_preferences(opportunity_id, preferences)
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
