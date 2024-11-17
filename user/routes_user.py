"""
Handles routes for the user module.
"""

import random
from flask import redirect, render_template, session, request

from core import database, handlers
from students.models import Student
from .models import User


def add_user_routes(app):
    """Add user routes."""

    @app.route("/user/register", methods=["GET", "POST"])
    def register():
        """Give page to register a new user."""
        if request.method == "POST":
            return User().register()
        return render_template("user/register.html")

    @app.route("/user/login", methods=["GET", "POST"])
    def login():
        """Gives login form to user."""
        if request.method == "POST":
            return User().login()
        if "logged_in" in session:
            return redirect("/")
        return render_template("user/login.html")

    @app.route("/user/change_password", methods=["GET", "POST"])
    def change_password():
        """Change user password."""
        if request.method == "POST":
            return User().change_password()
        return render_template("user/change_password.html")

    @app.route("/user/deadline", methods=["GET", "POST"])
    @handlers.login_required
    def deadline():
        """Change deadline."""
        if request.method == "POST":
            return User().change_deadline()

        return render_template(
            "user/deadline.html",
            details_deadline=database.get_details_deadline(),
            student_ranking_deadline=database.get_student_ranking_deadline(),
            opportunities_ranking_deadline=database.get_opportunities_ranking_deadline(),
        )

    @app.route("/user/ranking", methods=["GET"])
    @handlers.login_required
    def ranking():
        if not database.is_past_opportunities_ranking_deadline():
            return render_template(
                "user/past_deadline",
                referrer=request.referrer,
                data=f"The final deadline must have passed to do matching, wait till {database.get_opportunities_ranking_deadline()}",
            )

        students = list(database.students_collection.find())
        valid_students = []
        for student in students:
            if "preferences" in student:
                valid_students.append(student)
                continue

            # """Put this for an eirlier time, maybe at system start"""
            # opp_for_student = Student().get_opportunities_by_student(student["student_id"])
            # random.shuffle(opp_for_student)
            # student["preferences"] =  opp_for_student
            # valid_students.append(student)

        opportunities = list(database.opportunities_collection.find())
        valid_opportunities = []
        for opportunity in opportunities:
            if "preferences" in opportunity:
                valid_opportunities.append(opportunity)
                continue
