"""
User model.
"""

from email.mime.text import MIMEText
from flask import jsonify, request, session
from passlib.hash import pbkdf2_sha256
from core import email_handler
from employers.models import Employers
from opportunities.models import Opportunity
from students.models import Student


class User:
    """A class used to represent a User and handle user-related operations
    such as session management, registration and login."""

    def start_session(self, user):
        """Starts a session for the given user by removing the password from the
        user dictionary, setting session variables, and returning a JSON response."""
        del user["password"]
        session["logged_in"] = True
        session["user"] = {"_id": user["_id"], "name": user["name"]}
        return jsonify(session["user"]), 200

    def register(self, user):
        """Registers a new user by creating a user dictionary with a unique ID,
        name, email, and password, and returns a JSON response indicating failure."""
        session.clear()
        from app import database_manager

        if database_manager.get_by_email("users", user["email"]):
            return jsonify({"error": "Email address already in use"}), 400

        # Insert the user into the database
        database_manager.insert("users", user)

        # Start session or return success response
        if user:
            return self.start_session(user)

        return jsonify({"error": "Signup failed"}), 400

    def login(self, attempt_user):
        """Validates user credentials and returns a JSON response indicating
        invalid login credentials."""
        from app import database_manager

        session.clear()
        user = database_manager.get_by_email("users", attempt_user["email"])

        if user and pbkdf2_sha256.verify(attempt_user["password"], user["password"]):
            return self.start_session(user)

        return jsonify({"error": "Invalid login credentials"}), 401

    # def change_password(self):
    #     """Change user password."""
    #     user = session.get("user")
    #     old_password = request.form.get("old_password")
    #     new_password = request.form.get("new_password")
    #     confirm_password = request.form.get("confirm_password")

    #     if not pbkdf2_sha256.verify(old_password, user["password"]):
    #         return jsonify({"error": "Invalid old password"}), 400

    #     if new_password != confirm_password:
    #         return jsonify({"error": "Passwords don't match"}), 400

    #     database.users_collection.update_one(
    #         {"_id": user["_id"]},
    #         {"$set": {"password": pbkdf2_sha256.hash(new_password)}},
    #     )

    #     return jsonify({"message": "Password updated successfully"}), 200

    def change_deadline(self):
        """Change deadlines for details, student ranking, and opportunities ranking."""
        from app import deadline_manager

        details_deadline = request.form.get("details_deadline")
        student_ranking_deadline = request.form.get("student_ranking_deadline")
        opportunities_ranking_deadline = request.form.get(
            "opportunities_ranking_deadline"
        )

        response = deadline_manager.update_deadlines(
            details_deadline, student_ranking_deadline, opportunities_ranking_deadline
        )

        if response[1] != 200:
            return response
        return jsonify({"message": "All deadlines updated successfully"}), 200

    def send_match_email(
        self, student_uuid, opportunity_uuid, student_email, employer_email
    ):
        """Match students with opportunities."""

        student = Student().get_student_by_uuid(student_uuid)
        opportunity = Opportunity().get_opportunity_by_id(opportunity_uuid)
        employer_name = Employers().get_company_name(opportunity["employer_id"])
        recipients = [
            student_email,
            employer_email,
        ]

        body = (
            f"<p>Dear {student['first_name']},</p>"
            f"<p>Congratulations! You have been matched with <strong>{employer_name}</strong> for "
            f"the opportunity: <strong>{opportunity['title']}</strong>. Please contact them at "
            f"<a href='mailto:{employer_email}'>{employer_email}</a> "
            f"to discuss further details.</p>"
            "<p>Best,<br>Skillpoint</p>"
        )

        msg = MIMEText(body, "html")
        msg["Subject"] = "Skillpoint: Matched with an opportunity"
        msg["To"] = ", ".join(recipients)
        email_handler.send_email(msg, recipients)
        return jsonify({"message": "Email Sent"}), 200
