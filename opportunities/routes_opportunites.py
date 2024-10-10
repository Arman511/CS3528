from flask import render_template, request
from .models import Opportunity
from core import handlers
from courses.models import Course
from skills.models import Skill

def add_opportunities_routes(app):
    """Add routes for opportunites"""

    @app.route("/opportunities/search", methods=["GET", "POST"])
    @handlers.login_required
    def search_opportunites():
        if request.method == "POST":
            return Opportunity().search_opportunities()
        
        return render_template("opportunities/search.html")
        pass
    
    