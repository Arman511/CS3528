"""Handles the routes for the skills module."""
from core import handlers
from .models import Skill

def add_skills_routes(app):
    """Skills routes"""

    @app.route('/skills/attept_add_skill_student', methods=['POST'])
    @handlers.student_login_required
    def attempt_add_skill_student():
        """Attempt to add a skill to a student."""
        return Skill().attempt_add_skill()
