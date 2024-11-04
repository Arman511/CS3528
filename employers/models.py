"""Employer model."""

import uuid
from flask import redirect, request, jsonify, session
from core import database, email_handler


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
