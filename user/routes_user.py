"""
Handles routes for the user module.
"""

from datetime import datetime
from html import escape
import uuid
from flask import jsonify, redirect, render_template, session, request
from passlib.hash import pbkdf2_sha512
from algorithm.matching import Matching
from core import handlers, shared
from employers.models import Employers
from opportunities.models import Opportunity
from students.models import Student
from superuser.model import Superuser
from .models import User


def add_user_routes(app, cache):
    """Add user routes."""

    @app.route("/user/register", methods=["GET", "POST"])
    @handlers.superuser_required
    def register_user():
        """Give page to register a new user."""
        if request.method == "POST":
            password = request.form.get("password")
            confirm_password = request.form.get("confirm_password")
            if password != confirm_password:
                return jsonify({"error": "Passwords don't match"}), 400
            user = {
                "_id": uuid.uuid1().hex,
                "name": escape(request.form.get("name").title()),
                "email": escape(request.form.get("email").lower()),
                "password": pbkdf2_sha512.hash(password),  # Hash only the password
            }
            return User().register(user)
        return render_template("user/register.html", user_type="superuser")

    @app.route("/user/update", methods=["GET", "POST"])
    @handlers.superuser_required
    def update_user():
        """Update user."""
        if request.method == "GET":
            uuid = request.args.get("uuid")
            user = User().get_user_by_uuid(uuid)
            if not user:
                return redirect("/404")
            return render_template("user/update.html", user=user, user_type="superuser")
        uuid = request.args.get("uuid")
        name = escape(request.form.get("name"))
        email = escape(request.form.get("email"))
        return User().update_user(uuid, name, email)

    @app.route("/user/login", methods=["GET", "POST"])
    def login():
        """Gives login form to user."""
        if request.method == "POST":
            handlers.clear_session_save_theme()
            attempt_user = {
                "email": request.form.get("email"),
                "password": request.form.get("password"),
            }
            if not attempt_user["email"] or not attempt_user["password"]:
                return jsonify({"error": "Missing email or password"}), 400
            attempt_user["email"] = escape(attempt_user["email"].lower())
            if attempt_user["email"] == shared.getenv(
                "SUPERUSER_EMAIL"
            ) and attempt_user["password"] == shared.getenv("SUPERUSER_PASSWORD"):
                return Superuser().login(attempt_user)
            result = User().login(attempt_user)
            return result

        if "logged_in" in session:
            handlers.clear_session_save_theme()
        return render_template("user/login.html")

    @app.route("/user/delete", methods=["DELETE"])
    @handlers.superuser_required
    def delete_user():
        """Delete user."""
        uuid = request.args.get("uuid")
        return User().delete_user_by_uuid(uuid)

    @app.route("/user/change_password", methods=["GET", "POST"])
    @handlers.superuser_required
    def change_password():
        """Change user password."""
        uuid = request.args.get("uuid")
        if request.method == "POST":
            new_password = request.form.get("new_password")
            confirm_password = request.form.get("confirm_password")
            if new_password != confirm_password:
                return jsonify({"error": "Passwords don't match"}), 400
            return User().change_password(uuid, new_password, confirm_password)
        return render_template(
            "user/change_password.html", uuid=uuid, user_type="superuser"
        )

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
            page="deadline",
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
                if "title" not in opportunity:
                    opportunity["title"] = "Opportunity without title"

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
            page="problems",
        )

    @app.route("/user/send_match_email", methods=["POST"])
    @handlers.login_required
    def send_match_email():
        """Send match email."""
        student_uuid = request.form.get("student")
        opportunity_uuid = request.form.get("opportunity")
        student_email = request.form.get("student_email")
        employer_email = request.form.get("employer_email")
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
                page="matching",
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
            page="matching",
        )

    @app.route("/user/home")
    @handlers.login_required
    def user_home():
        """Handles the user home route and provides nearest deadlines & stats."""

        deadline_info = User().get_nearest_deadline_for_dashboard()
        deadline_name, deadline_date, num_students, num_opportunities = deadline_info

        formatted_date = (
            datetime.strptime(deadline_date, "%Y-%m-%d").strftime("%d-%m-%Y")
            if deadline_date
            else None
        )

        stats_data = {}
        if "Add Details" in deadline_name:
            stats_data = {
                "title": "📊 Student & Employer Details Stats",
                "label1": "Remaining Students To Fill In Their Details",
                "label2": "Opportunities Added by Employers",
                "count1": num_students,
                "count2": num_opportunities,
            }
        elif "Students Ranking" in deadline_name:
            stats_data = {
                "title": "📊 Student Rankings",
                "label1": "Remaining Students To Rank Their Opportunities",
                "label2": None,
                "count1": num_students,
                "count2": None,
            }
        elif "Employers Ranking" in deadline_name:
            stats_data = {
                "title": "📊 Employer Rankings",
                "label1": "Remaining Employers To Rank Students",
                "label2": None,
                "count1": num_opportunities,
                "count2": None,
            }
        else:
            stats_data = {
                "title": "🎯 Matching Ready!",
                "message": "✅ All deadlines have passed. The matchmaking is complete.",
            }

        return render_template(
            "user/home.html",
            user_type="admin",
            deadline_name=deadline_name,
            deadline_date=formatted_date,
            stats_data=stats_data,
        )

    @app.route("/user/search", methods=["GET"])
    @handlers.superuser_required
    def search_users():
        users = User().get_users_without_passwords()
        return render_template("user/search.html", users=users, user_type="superuser")
