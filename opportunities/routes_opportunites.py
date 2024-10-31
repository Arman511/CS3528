"""Routes for opportunites"""

import uuid
from flask import render_template, request
from core import handlers
from .models import Opportunity


def add_opportunities_routes(app):
    """Add routes for opportunites"""

    @app.route("/opportunities/search", methods=["GET", "POST"])
    @handlers.login_required
    def search_opportunites():
        if request.method == "POST":
            return Opportunity().search_opportunities()

        return render_template("opportunities/search.html")

    @app.route(
        "/opportunities/employer_add_update_opportunity", methods=["GET", "POST"]
    )
    @handlers.employers_login_required
    def employer_add_update_opportunity():
        if request.method == "POST":
            return Opportunity().add_update_opportunity()
        opportunity_id = request.args.get("opportunity_id")
        if opportunity_id != "":
            opportunity = Opportunity().get_opportunity_by_id(opportunity_id)[0]["json"]
        else:
            opportunity = {"_id": uuid.uuid1().hex}

        return render_template(
            "opportunities/employer_add_update_opportunity.html",
            opportunity=opportunity,
        )
