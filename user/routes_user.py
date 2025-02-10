"""
Handles routes for the user module.
"""

from datetime import datetime
import os
import uuid
from flask import jsonify, redirect, render_template, session, request
from passlib.hash import pbkdf2_sha256
from algorithm.matching import Matching
from core import handlers
from employers.models import Employers
from opportunities.models import Opportunity
from students.models import Student
from superuser.model import Superuser
from .models import User


def add_user_routes(app, cache):
    """Add user routes."""

    @app.route("/user/register", methods=["GET", "POST"])
    @handlers.superuser_required
    def register():
        """Give page to register a new user."""
        if request.method == "POST":
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            if password != confirm_password:
                return jsonify({"error": "Passwords don't match"}), 400
            user = {
                "_id": uuid.uuid1().hex,
                "name": request.form.get("name"),
                "email": request.form.get("email").lower(),
                "password": pbkdf2_sha256.hash(password),  # Hash only the password
            }
            return User().register(user)
        return render_template("user/register.html")

    @app.route("/user/login", methods=["GET", "POST"])
    def login():
        """Gives login form to user."""
        if request.method == "POST":
            attempt_user = {
                "email": request.form.get("email").lower(),
                "password": request.form.get("password"),
            }
            if "email" not in attempt_user or "password" not in attempt_user:
                return jsonify({"error": "Missing email or password"}), 400

            if attempt_user["email"] == os.getenv("SUPERUSER_EMAIL") and attempt_user[
                "password"
            ] == os.getenv("SUPERUSER_PASSWORD"):
                return Superuser().login(attempt_user)
            return User().login(attempt_user)
        if "logged_in" in session:
            return redirect("/")
        return render_template("user/login.html", user_type="admin")

    # @app.route("/user/change_password", methods=["GET", "POST"])
    # def change_password():
    #     """Change user password."""
    #     if request.method == "POST":
    #         return User().change_password()
    #     return render_template("user/change_password.html")

    @app.route("/user/deadline", methods=["GET", "POST"])
    @handlers.login_required
    def deadline():
        """Change deadline."""
        if request.method == "POST":
            details_deadline = request.form.get("details_deadline")
            student_ranking_deadline = request.form.get("student_ranking_deadline")
            opportunities_ranking_deadline = request.form.get(
                "opportunities_ranking_deadline"
            )
            return User().change_deadline(
                details_deadline=details_deadline,
                student_ranking_deadline=student_ranking_deadline,
                opportunities_ranking_deadline=opportunities_ranking_deadline,
            )

        from app import DEADLINE_MANAGER

        return render_template(
            "user/deadline.html",
            details_deadline=DEADLINE_MANAGER.get_details_deadline(),
            student_ranking_deadline=DEADLINE_MANAGER.get_student_ranking_deadline(),
            opportunities_ranking_deadline=DEADLINE_MANAGER.get_opportunities_ranking_deadline(),
            user_type="admin",
            user=session["user"].get("name"),
        )

    @app.route("/user/problem", methods=["GET"])
    @handlers.login_required
    def problems():
        problems = []
        from app import DEADLINE_MANAGER

        students = Student().get_students()
        passed_details_deadline = DEADLINE_MANAGER.is_past_details_deadline()
        passed_student_ranking_deadline = (
            DEADLINE_MANAGER.is_past_student_ranking_deadline()
        )
        passed_opportunities_ranking_deadline = (
            DEADLINE_MANAGER.is_past_opportunities_ranking_deadline()
        )

        for student in students:
            if "modules" not in student:
                problems.append(
                    {
                        "description": (
                            f"Student {student['student_id']}, has not filled in their details "
                            + (
                                "the deadline has passed so can not complete it"
                                if passed_details_deadline
                                else " the deadline has not passed yet"
                            )
                        ),
                        "email": student["email"],
                    }
                )

            if "preferences" not in student:
                problems.append(
                    {
                        "description": (
                            f"Student {student['student_id']}, has not ranked their opportunities "
                            + (
                                "the deadline has passed so can not complete it"
                                if passed_student_ranking_deadline
                                else " the deadline has not passed yet"
                            )
                        ),
                        "email": student["email"],
                    }
                )

        opportunities = Opportunity().get_opportunities()

        for opportunity in opportunities:
            if "preferences" not in opportunity:
                problems.append(
                    {
                        "description": (
                            f"Opportunity {opportunity['title']} with id {opportunity['_id']}, "
                            "has not ranked their students "
                            + (
                                "the deadline has passed so can not complete it"
                                if passed_opportunities_ranking_deadline
                                else " the deadline has not passed yet"
                            )
                        ),
                        "email": Employers().get_employer_by_id(
                            opportunity["employer_id"]
                        )["email"],
                    }
                )

        return render_template(
            "user/problems.html",
            problems=problems,
            user_type="admin",
            user=session["user"].get("name"),
        )

    @app.route("/user/send_match_email", methods=["POST"])
    @handlers.login_required
    def send_match_email():
        """Send match email."""
        student_uuid = request.form.get("student")
        opportunity_uuid = request.form.get("opportunity")
        student_email = (request.form.get("student_email"),)
        employer_email = (request.form.get("employer_email"),)
        return User().send_match_email(
            student_uuid, opportunity_uuid, student_email, employer_email
        )

    @app.route("/user/matching", methods=["GET"])
    @handlers.login_required
    @cache.cached(timeout=300)
    def matching():
        from app import DEADLINE_MANAGER

        if not DEADLINE_MANAGER.is_past_opportunities_ranking_deadline():
            return render_template(
                "user/past_deadline.html",
                referrer=request.referrer,
                data=(
                    "The final deadline must have passed to do matching, "
                    f"wait till {DEADLINE_MANAGER.get_opportunities_ranking_deadline()}"
                ),
                user_type="admin",
                user=session["user"].get("name"),
            )

        students = Student().get_students()
        unmatched_students = []
        students_preference = {}
        for student in students:
            if "preferences" in student:
                filtered_preferences = [
                    pref.strip() for pref in student["preferences"] if pref.strip()
                ]
                if filtered_preferences:
                    students_preference[student["_id"]] = filtered_preferences
                    continue
            # Handle unmatched students
            unmatched_students.append(
                {
                    "_id": student["_id"],
                    "student_id": student["student_id"],
                    "email": student["email"],
                    "name": f"{student['first_name']} {student['last_name']}",
                    "reason": "Student has not ranked their opportunities or has invalid preferences",
                }
            )

        opportunities = Opportunity().get_opportunities()
        opportunities_preference = {}
        for opportunity in opportunities:
            if "preferences" in opportunity:
                temp = {}
                temp["positions"] = opportunity["spots_available"]
                for i, student in enumerate(opportunity["preferences"]):
                    temp[student] = i + 1
                opportunities_preference[opportunity["_id"]] = temp
                continue

        result = Matching(
            students_preference, opportunities_preference
        ).find_best_match()
        matches_list = [
            {"opportunity": opportunity, "students": students}
            for opportunity, students in result[1].items()
        ]
        for student_id in result[0]:
            student = next((s for s in students if s["_id"] == student_id), None)
            if student is None:
                continue
            temp = {}
            temp["_id"] = student_id
            temp["student_id"] = student["student_id"]
            temp["email"] = student["email"]
            temp["name"] = f"{student['first_name']} {student['last_name']}"
            temp["reason"] = "Student was not matched"
            unmatched_students.append(temp)

        return render_template(
            "user/matching.html",
            not_matched=unmatched_students,
            matches=matches_list,
            students_map={student["_id"]: student for student in students},
            employers_map={
                employer["_id"]: employer for employer in Employers().get_employers()
            },
            opportunities_map={
                opportunity["_id"]: opportunity for opportunity in opportunities
            },
            last_updated=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_type="admin",
            user=session["user"].get("name"),
        )

    @app.route("/user/home")
    @handlers.login_required
    def user_home():
        """The home route which needs the user to be logged in and renders the 'home.html' template.

        Returns:
            str: Rendered HTML template for the home page.
        """
        return render_template("/user/home.html", user_type="admin")
