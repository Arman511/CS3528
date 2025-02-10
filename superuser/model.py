"""This module contains the Superuser class that is responsible for handling"""

import os
from flask import session, jsonify, redirect


class Superuser:

    def login(self, attempt_user):
        """Validates user credentials and returns a JSON response indicating
        invalid login credentials."""
        if not attempt_user:
            return jsonify({"error": "Missing email or password"}), 400

        if "email" not in attempt_user or "password" not in attempt_user:
            return jsonify({"error": "Missing email or password"}), 400

        if attempt_user["email"] == os.getenv("SUPERUSER_EMAIL") and attempt_user[
            "password"
        ] == os.getenv("SUPERUSER_PASSWORD"):
            session["user"] = {"email": attempt_user["email"]}
            session["superuser"] = True
            return redirect("/users/search")
        session.clear()

        return jsonify({"error": "Invalid login credentials"}), 401
