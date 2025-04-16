"""
User model.
"""

from email.mime.text import MIMEText
from flask import jsonify, session
from passlib.hash import pbkdf2_sha512
from core import email_handler, handlers, shared
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
        return jsonify({"message": "/user/home"}), 200

    def register(self, user):
        """Registers a new user by creating a user dictionary with a unique ID,
        name, email, and password, and returns a JSON response indicating failure."""
        from app import DATABASE_MANAGER

        if "email" not in user or "password" not in user:
            return jsonify({"error": "Missing email or password"}), 400
        if "name" not in user:
            return jsonify({"error": "Missing name"}), 400
        if DATABASE_MANAGER.get_by_email("users", user["email"]):
            return jsonify({"error": "Email address already in use"}), 400
        if user["email"] == shared.getenv("SUPERUSER_EMAIL"):
            return jsonify({"error": "Email address already in use"}), 400

        # Insert the user into the database
        DATABASE_MANAGER.insert("users", user)

        return jsonify({"message": "User registered successfully"}), 201

    def login(self, attempt_user):
        """Validates user credentials and returns a JSON response indicating
        invalid login credentials."""
        from app import DATABASE_MANAGER

        handlers.clear_session_save_theme()

        user = DATABASE_MANAGER.get_by_email("users", attempt_user["email"])

        if user and pbkdf2_sha512.verify(attempt_user["password"], user["password"]):
            return self.start_session(user)

        handlers.clear_session_save_theme()
        return jsonify({"error": "Invalid login credentials"}), 401

    def change_password(self, uuid, new_password, confirm_password):
        """Change user password."""
        from app import DATABASE_MANAGER

        if new_password != confirm_password:
            return jsonify({"error": "Passwords don't match"}), 400

        DATABASE_MANAGER.update_one_by_id(
            "users", uuid, {"password": pbkdf2_sha512.hash(new_password)}
        )

        return jsonify({"message": "Password updated successfully"}), 200

    def change_deadline(
        self, details_deadline, student_ranking_deadline, opportunities_ranking_deadline
    ):
        """Change deadlines for details, student ranking, and opportunities ranking."""
        from app import DEADLINE_MANAGER

        response = DEADLINE_MANAGER.update_deadlines(
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

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <p style="font-size: 16px;">Dear {student['first_name']},</p>
            <p style="font-size: 16px;"><strong>Congratulations!</strong> We’re thrilled to inform you that you have been <strong>matched</strong> with <strong>{employer_name}</strong> for an exciting opportunity!</p>
            <p style="font-size: 20px; font-weight: bold; color: #2c3e50;">{opportunity['title']}</p>
            <p style="font-size: 16px;">This is a great chance to connect and explore potential collaboration. We encourage you to reach out to <strong>{employer_name}</strong> at <a href='mailto:{employer_email}' style="color: #3498db; text-decoration: none;">{employer_email}</a> to discuss the next steps.</p>
            <p style="font-size: 16px;">If you have any questions or need any assistance, feel free to get in touch with our support team.</p>

            <hr style="border: 0; height: 1px; background: #ddd; margin: 20px 0;">

            <p style="font-size: 16px;"><strong>Wishing you all the best on this exciting journey!</strong></p>

            <p style="font-size: 16px;"><strong>Best Regards,</strong><br> The Skillpilot Team</p>
        </body>
        </html>
        """

        msg = MIMEText(body, "html")
        msg["Subject"] = "🎯 Skillpilot: You Have Been Matched!"
        msg["To"] = ", ".join(recipients)
        email_handler.send_email(msg, recipients)
        return jsonify({"message": "Email Sent"}), 200

    def delete_user_by_uuid(self, user_uuid):
        """Deletes a user by their UUID."""
        from app import DATABASE_MANAGER

        user = DATABASE_MANAGER.get_one_by_id("users", user_uuid)
        if not user:
            return jsonify({"error": "User not found"}), 404

        DATABASE_MANAGER.delete_by_id("users", user_uuid)
        return jsonify({"message": "User deleted successfully"}), 200

    def get_user_by_uuid(self, user_uuid):
        """Retrieves a user by their UUID."""
        from app import DATABASE_MANAGER

        user = DATABASE_MANAGER.get_one_by_id("users", user_uuid)
        if user:
            return user
        return None

    def get_users_without_passwords(self):
        """Retrieves all users without passwords."""
        from app import DATABASE_MANAGER

        users = DATABASE_MANAGER.get_all("users")
        for user in users:
            del user["password"]
        return users

    def update_user(self, user_uuid, name, email):
        """Updates a user's name and email by their UUID."""
        from app import DATABASE_MANAGER

        original = DATABASE_MANAGER.get_one_by_id("users", user_uuid)
        find_email = DATABASE_MANAGER.get_by_email("users", email)
        if find_email and find_email["_id"] != user_uuid:
            return jsonify({"error": "Email address already in use"}), 400
        if not original:
            return jsonify({"error": "User not found"}), 404
        if email == shared.getenv("SUPERUSER_EMAIL"):
            return jsonify({"error": "Email address already in use"}), 400

        update_data = {"name": name, "email": email}
        DATABASE_MANAGER.update_one_by_id("users", user_uuid, update_data)
        return jsonify({"message": "User updated successfully"}), 200

    def get_nearest_deadline_for_dashboard(self):
        """Retrieves the nearest deadline for the dashboard."""
        from app import DEADLINE_MANAGER, DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all("students")
        opportunities = DATABASE_MANAGER.get_all("opportunities")

        number_of_students = 0
        number_of_opportunities = 0

        if not DEADLINE_MANAGER.is_past_details_deadline():
            for student in students:
                if student.get("course"):  # Ensure student has added details
                    number_of_students += 1
            number_of_students = len(students) - number_of_students
            number_of_opportunities = len(DATABASE_MANAGER.get_all("opportunities"))

            return (
                "Student and Employers Add Details/Opportunities Deadline",
                DEADLINE_MANAGER.get_details_deadline(),
                number_of_students,
                number_of_opportunities,
            )

        if not DEADLINE_MANAGER.is_past_student_ranking_deadline():
            for student in students:
                if student.get("preferences") is not None:
                    number_of_students += 1

            number_of_students = len(students) - number_of_students

            return (
                "Students Ranking Opportunities Deadline",
                DEADLINE_MANAGER.get_student_ranking_deadline(),
                number_of_students,
                None,
            )

        if not DEADLINE_MANAGER.is_past_opportunities_ranking_deadline():
            for opportunity in opportunities:
                if opportunity.get("preferences") is not None:
                    number_of_opportunities += 1

            number_of_opportunities = len(opportunities) - number_of_opportunities

            return (
                "Employers Ranking Students Deadline",
                DEADLINE_MANAGER.get_opportunities_ranking_deadline(),
                None,
                number_of_opportunities,
            )

        # 4️ No upcoming deadlines
        return "No Upcoming Deadlines", None, None, None
