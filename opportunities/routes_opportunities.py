"""Routes for opportunities"""

import uuid
from flask import flash, redirect, render_template, request, session, url_for
from core import handlers
from course_modules.models import Module
from courses.models import Course
from employers.models import Employers
from .models import Opportunity


def add_opportunities_routes(app):
    """Add routes for opportunities"""

    @app.route("/opportunities/search", methods=["GET", "POST"])
    @handlers.admin_or_employers_required
    def search_opportunities():
        """
        Unified route for searching opportunities by admins and employers.
        Determines user type from session.
        """
        # Fetch user session details
        user = session.get("user")
        employer = session.get("employer")

        # Determine user_type based on session data
        user_type = None
        if user:
            user_type = "admin"
        else:
            user_type = "employer"

        print(f"[DEBUG] User type: {user_type}")
        if user_type is None:
            return {"error": "Unauthorized access."}, 403

        if request.method == "POST":
            data = request.get_json()  # Get the JSON data from the request

            title = data.get("title")
            if user_type == "admin":
                company_name = data.get("company")
                print("Admin - Method POST")
                return Opportunity().search_opportunities(title, company_name)
            else:
                print("Employer - Method POST")
                return Opportunity().search_opportunities(
                    title, employer["company_name"]
                )

        # For GET requests
        if user_type == "admin":
            print("Admin - Method GET")
            opportunities = Opportunity().search_opportunities(
                title="", company_name=""
            )
            employers_map = {
                employer["_id"]: employer
                for employer in list(Employers().get_employers())
            }
            return render_template(
                "opportunities/search.html",
                opportunities=opportunities,
                employers_map=employers_map,
                user_type=user_type,
            )
        elif user_type == "employer":
            print("Employer - Method GET")
            opportunities = Opportunity().search_opportunities(
                title="", company_name=employer["company_name"]
            )
            return render_template(
                "opportunities/search.html",
                opportunities=opportunities,
                user_type=user_type,
            )

    @app.route(
        "/opportunities/employer_add_update_opportunity", methods=["GET", "POST"]
    )
    @handlers.admin_or_employers_required
    def employer_add_update_opportunity():
        # Check if the details deadline has passed and the employer is in the session
        from app import DEADLINE_MANAGER

        if DEADLINE_MANAGER.is_past_details_deadline() and "employer" in session:
            return render_template(
                "employers/past_deadline.html",
                data=(
                    "Adding/Updating details deadline has passed as of "
                    f"{DEADLINE_MANAGER.get_details_deadline()}"
                ),
                referrer=request.referrer,
                employer=session["employer"],  # Pass employer to the template
                user_type="employer",
            )

        if request.method == "POST":
            opportunity = {
                "_id": request.form.get("_id"),
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "url": request.form.get("url"),
                "employer_id": None,
                "location": request.form.get("location"),
                "modules_required": request.form.get("modules_required")[1:-1].replace('"', '').split(','),
                "courses_required": request.form.get("courses_required")[1:-1].replace('"', '').split(','),
                "spots_available": request.form.get("spots_available"),
                "duration": request.form.get("duration"),
            }
            if handlers.is_admin():
                opportunity["employer_id"] = request.form.get("employer_id")
                return Opportunity().add_update_opportunity(opportunity, True)

            opportunity["employer_id"] = session["employer"]["_id"]
            return Opportunity().add_update_opportunity(opportunity, False)

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
        return redirect(url_for("search_opportunities"))
