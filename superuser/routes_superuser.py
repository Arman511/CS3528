"""Super user routes"""

from flask import jsonify, request, render_template
from core import handlers
from .model import Superuser


def add_superuser_routes(app):
    """Add superuser routes."""

    @app.route("/superuser/configure", methods=["GET", "POST"])
    @handlers.superuser_required
    def configure_settings():
        from app import CONFIG_MANAGER

        """Configure settings page"""
        if request.method == "GET":
            return render_template(
                "superuser/config.html",
                user_type="superuser",
                max_skills=CONFIG_MANAGER.get_max_num_of_skills(),
                min_num_ranking_student_to_opportunity=CONFIG_MANAGER.get_min_num_ranking_student_to_opportunities(),
            )
        try:
            new_max_skills = int(request.form.get("max_skills"))
            new_min_num_ranking_student_to_opportunity = int(
                request.form.get("min_num_ranking_student_to_opportunity")
            )
            return Superuser().configure_settings(
                new_max_skills, new_min_num_ranking_student_to_opportunity
            )
        except Exception:
            return jsonify({"error": "Invalid input"}), 400
