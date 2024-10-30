"""Employer model."""

import uuid
from flask import request, jsonify, session, render_template
from core import database, email_handler


class Employers:
    """Employer class."""

    def start_session(self):
        """Starts a session."""
        session["employer_logged_in"] = True
        return render_template(
            "employer/employer_home.html", employer=session["employer"]
        )

    def register_employer(self):
        """Adding new employer."""
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password != confirm_password:
            return jsonify({"error": "Passwords do not match."}), 400

        employer = {
            "_id": uuid.uuid1().hex,
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
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
            return render_template("employer/otp.html", employer=employer)

        return jsonify({"error": "Invalid login credentials."}), 401
