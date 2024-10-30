"""Employer model."""

import uuid
from flask import request, jsonify, session, render_template
from passlib.hash import pbkdf2_sha256
from core import database


class Employers:
    """Employer class."""

    def start_session(self, employer):
        """Starts a session."""
        del employer["password"]
        session["employer_logged_in"] = True
        session["employer"] = employer
        return render_template("employer/employer_home.html", employer=employer)

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
            "password": pbkdf2_sha256.hash(password),
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

        if employer and pbkdf2_sha256.verify(
            request.form.get("password"), employer["password"]
        ):
            return self.start_session(employer)

        return jsonify({"error": "Invalid login credentials."}), 401
