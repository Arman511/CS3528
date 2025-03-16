"""This module contains the Superuser class that is responsible for handling"""

import os
from flask import session, jsonify


class Superuser:
    """A class used to represent a Superuser and handle superuser-related"""

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
            return jsonify({"message": "/user/search"}), 200

        theme = session["theme"] if "theme" in session else "light"
        session.clear()
        session["theme"] = theme

        return jsonify({"error": "Invalid login credentials"}), 401

    def configure_settings(self, max_skills, min_num_ranking_student_to_opportunity):
        """Configures the settings for the superuser."""
        from app import CONFIG_MANAGER

        try:
            CONFIG_MANAGER.set_num_of_skills(max_skills)
            CONFIG_MANAGER.set_min_num_ranking_student_to_opportunities(
                min_num_ranking_student_to_opportunity
            )
            return jsonify({"message": "Settings updated successfully"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
