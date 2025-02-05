"""Employer model."""

from datetime import datetime, timedelta
import time
from flask import redirect, jsonify, request, session
from core import email_handler

employers_cache = {"data": None, "last_updated": None}


class Employers:
    """Employer class."""

    def start_session(self):
        """Starts a session."""
        session["employer_logged_in"] = True
        return redirect("/employers/home")

    def register_employer(self, employer):
        """Adding new employer."""
        from app import DATABASE_MANAGER

        # employer = {
        #     "_id": uuid.uuid1().hex,
        #     "company_name": request.form.get("company_name"),
        #     "email": request.form.get("email"),
        # }

        if DATABASE_MANAGER.get_by_email("employers", employer["email"]):
            return jsonify({"error": "Employer already in database"}), 400

        DATABASE_MANAGER.insert("employers", employer)
        if employer:
            return jsonify(employer), 200

        return jsonify({"error": "Employer not added"}), 400

    def get_company_name(self, _id):
        """Get company name"""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_by_id("employers", _id)
        if not employer:
            return ""

        return employer["company_name"]

    def employer_login(self, email):
        """Logs in the employer."""
        session.clear()
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

        if employers_cache["data"] and datetime.now() - employers_cache[
            "last_updated"
        ] < timedelta(minutes=5):
            return employers_cache["data"]

        employers = DATABASE_MANAGER.get_all("employers")
        employers_cache["data"] = employers
        employers_cache["last_updated"] = datetime.now()
        return employers

    def get_employer_by_id(self, employer_id):
        """Gets an employer by ID."""
        employers = self.get_employers()

        for employer in employers:
            if employer["_id"] == employer_id:
                return employer

        return None

    def delete_employer_by_id(self, _id):
        """Deletes an employer."""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_one_by_id("employers", _id)

        if employer:
            DATABASE_MANAGER.delete_by_id("employers", _id)
            employers_cache["data"] = DATABASE_MANAGER.get_all("employers")
            employers_cache["last_updated"] = datetime.now()
            return jsonify({"message": "Employer deleted"}), 200

        return jsonify({"error": "Employer not found"}), 404

    def update_employer(self):
        """Updates an employer in the database."""
        from app import DATABASE_MANAGER

        employer_id = request.form.get("employer_id")

        employer = DATABASE_MANAGER.get_one_by_id("employers", employer_id)
        if not employer:
            return jsonify({"error": "Employer not found"}), 404

        update_data = {
            "company_name": request.form.get("company_name"),
            "email": request.form.get("email"),
        }

        DATABASE_MANAGER.update_one_by_id("employers", employer_id, update_data)

        # Update cache
        employers_cache["data"] = DATABASE_MANAGER.get_all("employers")
        employers_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Employer updated successfully"}), 200

    def rank_preferences(self, opportunity_id, preferences):
        """Sets a students preferences."""
        from app import DATABASE_MANAGER

        opportunity = DATABASE_MANAGER.get_by_id("opportunities", opportunity_id)

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        DATABASE_MANAGER.update_one_by_id(
            "opportunities", opportunity_id, {"preferences": preferences}
        )
        return jsonify({"message": "Preferences updated"}), 200

    def get_company_email_by_id(self, _id):
        """Get company email by id"""
        from app import DATABASE_MANAGER

        employer = DATABASE_MANAGER.get_by_id("employers", _id)
        if not employer:
            return ""

        return employer["email"]
