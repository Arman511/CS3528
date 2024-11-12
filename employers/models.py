"""Employer model."""

from datetime import datetime, timedelta
import uuid
from flask import redirect, request, jsonify, session
from core import database, email_handler

employers_cache = {"data": None, "last_updated": None}


class Employers:
    """Employer class."""

    def start_session(self):
        """Starts a session."""
        session["employer_logged_in"] = True
        return redirect("/employers/home")

    def register_employer(self):
        """Adding new employer."""

        employer = {
            "_id": uuid.uuid1().hex,
            "company_name": request.form.get("company_name"),
            "email": request.form.get("email"),
        }

        if database.employers_collection.find_one({"email": request.form.get("email")}):
            return jsonify({"error": "Employer already in database"}), 400

        database.employers_collection.insert_one(employer)
        if employer:
            return jsonify(employer), 200

        return jsonify({"error": "Employer not added"}), 400

    def employer_login(self):
        """Logs in the employer."""
        session.clear()
        employer = database.employers_collection.find_one(
            {"email": request.form.get("email")}
        )
        if employer:
            email_handler.send_otp(employer["email"])
            session["employer"] = employer
            return jsonify({"message": "OTP sent"}), 200

        return jsonify({"error": "Invalid login credentials."}), 401

    def get_employers(self):
        """Gets all employers."""
        if employers_cache["data"] and datetime.now() - employers_cache[
            "last_updated"
        ] < timedelta(minutes=5):
            return employers_cache["data"]

        employers = list(database.employers_collection.find())
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
