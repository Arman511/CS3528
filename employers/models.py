"""Employer model."""

import tempfile
import time
import uuid
from flask import redirect, jsonify, session, send_file
import pandas as pd
from core import email_handler, handlers


class Employers:
    """Employer class."""

    def start_session(self):
        """Starts a session."""
        session["employer_logged_in"] = True
        return redirect("/employers/home", code=200)

    def register_employer(self, employer):
        """Adding new employer."""
        from app import DATABASE_MANAGER

        if DATABASE_MANAGER.get_one_by_field_strict(
            "employers", "email", employer["email"].lower()
        ):
            return jsonify({"error": "Email already in use"}), 400

        existing_employer = DATABASE_MANAGER.get_one_by_field_strict(
            "employers", "company_name", employer["company_name"]
        )
        employer["email"] = employer["email"].lower()

        if existing_employer:
            return jsonify({"error": "Company name already exists"}), 400

        DATABASE_MANAGER.insert("employers", employer)

        if employer:
            return jsonify(employer), 200

        return jsonify({"error": "Employer not added"}), 400

    def get_company_name(self, _id):
        """Get company name"""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_one_by_id("employers", _id)
        if not employer:
            return ""

        return employer["company_name"]

    def employer_login(self, email):
        """Logs in the employer."""
        handlers.clear_session_save_theme()
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_by_email("employers", email)
        if employer:
            email_handler.send_otp(employer["email"])
            session["employer"] = employer
        else:
            time.sleep(1.5)

        return jsonify({"message": "OTP sent if valid"}), 200

    def get_employers(self):
        """Gets all employers."""
        from app import DATABASE_MANAGER

        employers = DATABASE_MANAGER.get_all("employers")

        return employers

    def get_employer_by_id(self, employer_id):
        """Retrieves an employer by its ID."""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_one_by_id("employers", employer_id)
        if employer:
            return employer
        return None

    def delete_employer_by_id(self, _id):
        """Deletes an employer."""
        from app import DATABASE_MANAGER
        from opportunities.models import Opportunity

        employer = DATABASE_MANAGER.get_one_by_id("employers", _id)
        if not employer:
            return jsonify({"error": "Employer not found"}), 404
        DATABASE_MANAGER.delete_by_id("employers", _id)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if opportunity["employer_id"] == _id:
                Opportunity().delete_opportunity_by_id(opportunity["_id"])

        return jsonify({"message": "Employer deleted"}), 200

    def update_employer(self, employer_id, update_data):
        """Updates an employer in the database."""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_one_by_id("employers", employer_id)
        if not employer:
            return jsonify({"error": "Employer not found"}), 404

        DATABASE_MANAGER.update_one_by_id("employers", employer_id, update_data)

        return jsonify({"message": "Employer updated successfully"}), 200

    def rank_preferences(self, opportunity_id, preferences):
        """Sets a students preferences."""
        from app import DATABASE_MANAGER

        opportunity = DATABASE_MANAGER.get_one_by_id("opportunities", opportunity_id)

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        DATABASE_MANAGER.update_one_by_id(
            "opportunities", opportunity_id, {"preferences": preferences}
        )
        return jsonify({"message": "Preferences updated"}), 200

    def get_company_email_by_id(self, _id):
        """Get company email by id"""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_one_by_id("employers", _id)
        if not employer:
            return ""

        return employer["email"]

    def delete_all_employers(self):
        """Deletes all employers."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("employers")

        DATABASE_MANAGER.delete_all("opportunities")

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if "preferences" in student:
                student["preferences"] = []
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "All employers deleted"}), 200

    def download_all_employers(self):
        """Downloads all employers."""
        from app import DATABASE_MANAGER

        employers = DATABASE_MANAGER.get_all("employers")
        for employer in employers:
            employer.pop("_id")
            employer["Company_name"] = employer.pop("company_name")
            employer["Email"] = employer.pop("email")

        # Convert employers to DataFrame
        df = pd.DataFrame(employers)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
            df.to_excel(tmp.name, index=False)
            tmp_path = tmp.name

            return send_file(
                tmp_path, as_attachment=True, download_name="employers.xlsx"
            )

    def upload_employers(self, file):
        """Uploads employers."""

        from app import DATABASE_MANAGER

        # Read the file
        df = pd.read_excel(file)

        # Convert DataFrame to list of dictionaries
        employers = df.to_dict(orient="records")

        current_employers = DATABASE_MANAGER.get_all("employers")

        current_employer_names = set(
            employer["company_name"].lower() for employer in current_employers
        )
        current_employer_emails = set(
            employer["email"].lower() for employer in current_employers
        )

        emails = set()
        company_names = set()
        clean_data = []
        for i, employer in enumerate(employers):
            temp = {
                "_id": uuid.uuid4().hex,
                "company_name": employer["Company_name"],
                "email": employer["Email"],
            }
            if not temp["company_name"] or not temp["email"]:
                return jsonify({"error": "Company name and email are required"}), 400
            temp["email"] = temp["email"].lower()
            if temp["company_name"].lower() in current_employer_names:
                return (
                    jsonify(
                        {
                            "error": f"Company name {temp['company_name']} already exists as row {i+2}"
                        }
                    ),
                    400,
                )
            if temp["email"].lower() in current_employer_emails:
                return (
                    jsonify(
                        {"error": f"Email {temp['email']} already exists as row {i+2}"}
                    ),
                    400,
                )
            if temp["email"].lower() in emails:
                return (
                    jsonify(
                        {"error": f"Email {temp['email']} already exists as row {i+2}"}
                    ),
                    400,
                )
            if temp["company_name"].lower() in company_names:
                return (
                    jsonify(
                        {
                            "error": f"Company name {temp['company_name']} already exists as row {i+2}"
                        }
                    ),
                    400,
                )

            clean_data.append(temp)
            emails.add(temp["email"].lower())
            company_names.add(temp["company_name"].lower())

        DATABASE_MANAGER.insert_many("employers", clean_data)

        # Update cache

        return (
            jsonify({"message": f"{len(clean_data)} employers uploaded successfully"}),
            200,
        )

    def get_deadlines_for_employer_dashboard(self):
        from app import DEADLINE_MANAGER

        if not DEADLINE_MANAGER.is_past_details_deadline():
            return (
                "Add Any Number of Opportunities Deadline",
                DEADLINE_MANAGER.get_details_deadline(),
            )

        if not DEADLINE_MANAGER.is_past_student_ranking_deadline():
            return (
                "Students Ranking Opportunities/Roles Deadline",
                DEADLINE_MANAGER.get_student_ranking_deadline(),
            )

        if not DEADLINE_MANAGER.is_past_opportunities_ranking_deadline():
            return (
                "Ranking Student For Individual Opportunities/Roles Deadline",
                DEADLINE_MANAGER.get_opportunities_ranking_deadline(),
            )

        return "All Deadlines Passed", None
