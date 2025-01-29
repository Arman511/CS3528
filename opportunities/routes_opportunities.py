"""Routes for opportunities"""

import uuid
from flask import flash, jsonify, redirect, render_template, request, session, url_for
from core import database, handlers
from course_modules.models import Module
from courses.models import Course
from employers.models import Employers
from .models import Opportunity


def add_opportunities_routes(app):
    """Add routes for opportunities"""

    @app.route("/admin/opportunities/search", methods=["GET", "POST"])
    @handlers.admin_or_employers_required
    def search_opportunities_admin():
        if request.method == "POST":
            data = request.get_json()  # Get the JSON data from the request
            title = data.get("title")
            company_name = data.get("company")
            print("Admin - Method POST")
            return Opportunity().search_opportunities(title, company_name)

        # For GET requests
        opportunities = Opportunity().search_opportunities(title="", company_name="")
        employers_map = {
            employer["_id"]: employer for employer in list(Employers().get_employers())
        }
        return render_template(
            "opportunities/search.html",
            opportunities=opportunities,
            employers_map=employers_map,
            user_type="admin",
        )

    @app.route("/employer/opportunities/search", methods=["GET", "POST"])
    @handlers.employers_login_required
    def search_opportunities_employers(employer):
        """
        Search opportunities for an employer by title and/or company name.
        """
        # Extract the company name from the `employer` object
        company_name = employer.get(
            "company_name", "Unknown Company"
        )  # Default to "Unknown Company" if key is missing

        print(f"[DEBUG] Employer company_name: {company_name}")

        if request.method == "POST":
            data = request.get_json()  # Get the JSON data from the request
            title = data.get("title")  # Extract title from the request payload

            print(f"[DEBUG] POST request, employer_filter: {company_name}")

            if not title:
                return {"error": "No title provided for filtering."}, 400

            print(
                f"[DEBUG] POST request with title: {title} for company {company_name}"
            )

            # Use the unified search_opportunities function
            opportunities = Opportunity().search_opportunities(
                title=title, company_name=company_name
            )
            print(f"[DEBUG] Found {len(opportunities)} opportunities after filtering.")

            return opportunities

        # For GET requests, show all opportunities for the company
        print(f"[DEBUG] GET request for all opportunities for company {company_name}.")
        opportunities = Opportunity().search_opportunities(
            title="", company_name=company_name
        )

        return render_template(
            "opportunities/search.html",
            opportunities=opportunities,
            user_type="employer",
            employer=employer,
        )

    @app.route(
    "/opportunities/employer_add_update_opportunity", methods=["GET", "POST"]
    )
    @handlers.admin_or_employers_required
    def employer_add_update_opportunity():
        # Check if the details deadline has passed and the employer is in the session
        if database.is_past_details_deadline() and "employer" in session:
            return render_template(
                "employers/past_deadline.html",
                data=(
                    "Adding/Updating details deadline has passed as of "
                    f"{database.get_details_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],  # Pass employer to the template
                user_type="employer",
            )

        if request.method == "POST":
            return Opportunity().add_update_opportunity()

        # Get the opportunity by ID if it exists
        opportunity_id = request.args.get("opportunity_id")
        if opportunity_id is not None:
            opportunity = Opportunity().get_opportunity_by_id(opportunity_id)
        else:
            opportunity = {"_id": uuid.uuid1().hex}

        # Include employer in the context
        employer = session.get("employer", None)

        return render_template(
            "opportunities/employer_add_update_opportunity.html",
            opportunity=opportunity,
            courses=Course().get_courses(),
            modules=Module().get_modules(),
            user_type="admin" if "logged_in" in session else "employer",
            employer=employer,  # Add employer to the template context
        )


    @app.route("/opportunities/employer_delete_opportunity", methods=["POST", "GET"])
    @handlers.admin_or_employers_required
    def employer_delete_opportunity():
        opportunity_id = request.args.get("opportunity_id")
        if not opportunity_id:
            flash("Opportunity ID is required", "error")
            return redirect(request.referrer)

        Opportunity().delete_opportunity_by_id(opportunity_id)
        flash("Opportunity deleted successfully", "success")
        return redirect(url_for("search_opportunities_admin"))
