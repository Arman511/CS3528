"""
User model.
"""

from email.mime.text import MIMEText
import uuid
from flask import jsonify, request, session
from passlib.hash import pbkdf2_sha256
from core import database, email_handler
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
        session["user"] = user
        return jsonify(user), 200

    def register(self):
        """Registers a new user by creating a user dictionary with a unique ID,
        name, email, and password, and returns a JSON response indicating failure."""
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        # Check if passwords match (if needed here for extra validation)
        if password != confirm_password:
            return jsonify({"error": "Passwords don't match"}), 400

        user = {
            "_id": uuid.uuid1().hex,
            "name": request.form.get("name"),
            "email": request.form.get("email"),
            "password": pbkdf2_sha256.hash(password),  # Hash only the password
        }

        if database.users_collection.find_one({"email": request.form.get("email")}):
            return jsonify({"error": "Email address already in use"}), 400

        # Insert the user into the database
        database.users_collection.insert_one(user)

        # Start session or return success response
        if user:
            return self.start_session(user)

        return jsonify({"error": "Signup failed"}), 400

    def login(self):
        """Validates user credentials and returns a JSON response indicating
        invalid login credentials."""
        session.clear()
        user = database.users_collection.find_one({"email": request.form.get("email")})

        if user and pbkdf2_sha256.verify(
            request.form.get("password"), user["password"]
        ):
            return self.start_session(user)

        return jsonify({"error": "Invalid login credentials"}), 401

    def change_password(self):
        """Change user password."""
        user = session.get("user")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not pbkdf2_sha256.verify(old_password, user["password"]):
            return jsonify({"error": "Invalid old password"}), 400

        if new_password != confirm_password:
            return jsonify({"error": "Passwords don't match"}), 400

        database.users_collection.update_one(
            {"_id": user["_id"]},
            {"$set": {"password": pbkdf2_sha256.hash(new_password)}},
        )

        return jsonify({"message": "Password updated successfully"}), 200

    def change_deadline(self):
        """Change deadlines for details, student ranking, and opportunities ranking."""
        details_deadline = request.form.get("details_deadline")
        student_ranking_deadline = request.form.get("student_ranking_deadline")
        opportunities_ranking_deadline = request.form.get(
            "opportunities_ranking_deadline"
        )

        details_response = database.update_details_deadline(details_deadline)
        if details_response[1] != 200:
            return details_response

        student_response = database.update_student_ranking_deadline(
            student_ranking_deadline
        )
        if student_response[1] != 200:
            return student_response

        opportunities_response = database.update_opportunities_ranking_deadline(
            opportunities_ranking_deadline
        )
        if opportunities_response[1] != 200:
            return opportunities_response

        return jsonify({"message": "All deadlines updated successfully"}), 200

    def matching(self):
        """Match students with opportunities."""
        student = Student().get_student_by_uuid(request.form.get("student"))
        opportunity = Opportunity().get_opportunity_by_id(
            request.form.get("opportunity")
        )
        employer_name = Employers().get_company_name(opportunity["employer_id"])
        recipients = [
            request.form.get("student_email"),
            request.form.get("employer_email"),
        ]

        body = (
            f"<p>Dear {student['first_name']},</p>"
            f"<p>Congratulations! You have been matched with <strong>{employer_name}</strong> for the "
            f"opportunity: <strong>{opportunity['title']}</strong>. Please contact them at "
            f"<a href='mailto:{request.form.get('employer_email')}'>{request.form.get('employer_email')}</a> "
            f"to discuss further details.</p>"
            "<p>Best,<br>Skillpoint</p>"
        )

        msg = MIMEText(body, "html")
        msg["Subject"] = "Skillpoint: Matched with an opportunity"
        msg["To"] = ", ".join(recipients)
        email_handler.send_email(msg, recipients)
        return jsonify({"message": "Email Sent"}), 200
