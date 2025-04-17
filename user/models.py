"""
User model.
"""

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from io import BytesIO
from flask import jsonify, session
import pandas as pd
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
        self,
        student_uuid,
        opportunity_uuid,
    ):
        """Match students with opportunities."""

        student = Student().get_student_by_uuid(student_uuid)
        opportunity = Opportunity().get_opportunity_by_id(opportunity_uuid)
        employer = Employers().get_employer_by_id(opportunity["employer_id"])

        if not student or not opportunity or not employer:
            return jsonify({"error": "Invalid student, opportunity, or employer"}), 400
        if (
            not student["email"]
            or not employer["email"]
            or not employer["company_name"]
        ):
            return jsonify({"error": "Missing email or name"}), 400
        if not opportunity["title"]:
            return jsonify({"error": "Missing opportunity title"}), 400
        if not student["first_name"]:
            return jsonify({"error": "Missing student first name"}), 400
        student_email = student["email"]
        employer_email = employer["email"]
        employer_name = employer["company_name"]
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

    def send_all_match_email(self, student_map_to_placments):
        """Send match email to all students and employers."""
        employer_emails: dict[str, list] = dict()
        students_map = Student().get_students_map()

        opportunity_map = {
            opportunity["_id"]: opportunity
            for opportunity in Opportunity().get_opportunities()
        }
        employer_map = {
            employer["_id"]: employer for employer in Employers().get_employers()
        }

        for row, map_item in enumerate(student_map_to_placments["students"]):
            student = students_map.get(map_item["student"])
            opportunity_uuid = map_item["opportunity"]
            opportunity = opportunity_map.get(opportunity_uuid)
            employer = employer_map.get(opportunity["employer_id"])
            if not student or not opportunity or not employer:
                return (
                    jsonify(
                        {
                            "error": f"Invalid student, opportunity, or employer at row: {row+1}"
                        }
                    ),
                    400,
                )

            if (
                not student["email"]
                or not employer["email"]
                or not employer["company_name"]
            ):
                return jsonify({"error": "Missing email or name"}), 400
            if not opportunity["title"]:
                return jsonify({"error": "Missing opportunity title"}), 400
            if not student["first_name"]:
                return jsonify({"error": "Missing student first name"}), 400

            student_email = student["email"]
            employer_email = employer["email"]
            employer_name = employer["company_name"]

            # --- Student Email ---
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
            msg["Subject"] = "🎯 Skillpilot: You’ve Been Matched!"
            msg["To"] = student_email
            email_handler.send_email(msg, student_email)

            # Collect for employer
            employer_emails.setdefault(opportunity["employer_id"], []).append(
                (
                    student["first_name"],
                    student["last_name"],
                    student_email,
                    opportunity["title"],
                    opportunity_uuid,
                )
            )

        # --- Employer Emails ---
        for employer_id, matches in employer_emails.items():
            employer = employer_map[employer_id]
            employer_email = employer["email"]
            employer_name = employer["company_name"]

            # HTML email with a table
            table_rows = ""
            for (
                student_first_name,
                student_last_name,
                student_email,
                title,
                opportunity_uuid,
            ) in matches:
                table_rows += f"""
                <tr>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px;">{student_first_name}</td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px;">{student_last_name}</td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px;"><a href="mailto:{student_email}" style="color: #3498db; text-decoration: none;">{student_email}</a></td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px;">{title}</td>
                    <td style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">{opportunity_uuid}</td>
                </tr>
                """

            html_body = f"""
            <html>
            <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6; background-color: #f9f9f9; padding: 20px;">
                <div style="max-width: 100%; margin: 0 auto; background: #fff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); padding: 20px; overflow-x: auto;">
                    <p style="font-size: 16px; color: #2c3e50;">Dear <strong>{employer_name}</strong>,</p>
                    <p style="font-size: 16px; color: #2c3e50;">We’re excited to share that you’ve been matched with the following students for your opportunities:</p>
                    <table style="border-collapse: collapse; width: 100%; margin-top: 20px; font-size: 14px;">
                        <thead>
                            <tr style="background-color: #f2f2f2;">
                                <th style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">Student First Name</th>
                                <th style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">Student Last Name</th>
                                <th style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">Email</th>
                                <th style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">Opportunity Title</th>
                                <th style="padding: 12px; border: 1px solid #ddd; text-align: left; font-size: 14px; color: #555;">Opportunity UUID</th>
                            </tr>
                        </thead>
                        <tbody>
                            {table_rows}
                        </tbody>
                    </table>
                    <p style="font-size: 16px; color: #2c3e50; margin-top: 20px;">Please feel free to reach out to the students to discuss the next steps. For your convenience, we’ve also attached this information as an Excel file.</p>
                    <hr style="border: 0; height: 1px; background: #ddd; margin: 20px 0;">
                    <p style="font-size: 16px; color: #2c3e50;"><strong>Best regards,</strong><br>The Skillpilot Team</p>
                </div>
            </body>
            </html>
            """

            # Create a DataFrame for the matches
            data = [
                {
                    "Student First Name": student_first_name,
                    "Student Last Name": student_last_name,
                    "Email": student_email,
                    "Opportunity Title": title,
                    "Opportunity UUID": opportunity_uuid,
                }
                for student_first_name, student_last_name, student_email, title, opportunity_uuid in matches
            ]
            df = pd.DataFrame(data)

            # Save the DataFrame to an Excel file in memory
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Matches")
            excel_buffer.seek(0)

            # Create the full email
            msg = MIMEMultipart()
            msg["Subject"] = "🎯 Skillpilot: Student Matches Summary"
            msg["To"] = employer_email

            # Attach the Excel file
            part = MIMEApplication(excel_buffer.read(), Name="student_matches.xlsx")
            part["Content-Disposition"] = 'attachment; filename="student_matches.xlsx"'
            msg.attach(part)

            # Attach the HTML body
            msg.attach(MIMEText(html_body, "html"))

            email_handler.send_email(msg, employer_email)

        return jsonify({"message": "Emails Sent"}), 200

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
