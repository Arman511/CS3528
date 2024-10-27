"""Handles the routes for the skills module."""

from core import handlers
from .models import Skill
from flask import render_template, request


def add_skills_routes(app):
    """Skills routes"""

    @app.route("/skills/attempt_add_skill_student", methods=["POST"])
    @handlers.student_login_required
    def attempt_add_skill_student():
        """Attempt to add a skill to a student."""
        return Skill().attempt_add_skill()

    @app.route("/skills/add_skill", methods=["POST", "GET"])
    @handlers.login_required
    def add_skill():
        if request.method == "GET":
            return render_template("/skills/adding_skills.html")
        return Skill().add_skill()
