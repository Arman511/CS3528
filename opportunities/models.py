"""
Opportunity model.
"""

from datetime import datetime
from flask import jsonify, request, session
from employers.models import Employers

cache = {"data": [], "last_updated": datetime.now()}


class Opportunity:
    """Opportunity class."""

    def add_update_opportunity(
        self,
        opportunity,
        is_admin=False,
    ):
        from app import DATABASE_MANAGER

        """Adding new opportunity."""
        find_opportunity = DATABASE_MANAGER.get_by_id(
            "opportunities", opportunity["_id"]
        )
        if find_opportunity and not is_admin:
            if find_opportunity["employer_id"] != session["employer"]["_id"]:
                return jsonify({"error": "Unauthorized Access."}), 401
        DATABASE_MANAGER.delete_by_id("opportunities", opportunity["_id"])

        DATABASE_MANAGER.insert("opportunities", opportunity)

        cache["data"] = list(DATABASE_MANAGER.get_all("opportunities"))
        cache["last_updated"] = datetime.now()

        if opportunity:
            return jsonify(opportunity), 200

        return jsonify({"error": "Opportunity not added"}), 400

    def search_opportunities(self, title, company_name):
        """Search opportunities by title and/or company."""
        opportunities = []
        from app import DATABASE_MANAGER

        try:
            # Build the query dynamically based on the provided parameters
            opportunities = []
            if title and company_name:
                company = DATABASE_MANAGER.get_one_by_field(
                    "employers",
                    "company_name",
                    {"$regex": company_name, "$options": "i"},
                )
                opportunities = DATABASE_MANAGER.get_all_by_two_fields(
                    "opportunities",
                    "title",
                    {"$regex": title, "$options": "i"},
                    "employer_id",
                    company["_id"],
                )
            elif title:
                opportunities = DATABASE_MANAGER.get_all_by_field(
                    "opportunities", {"title": {"$regex": title, "$options": "i"}}
                )
            elif company_name:
                company = DATABASE_MANAGER.get_one_by_field(
                    "employers",
                    "company_name",
                    {"$regex": company_name, "$options": "i"},
                )
                opportunities = DATABASE_MANAGER.get_all_by_field(
                    "opportunities", "employer_id", company["_id"]
                )
            else:
                opportunities = DATABASE_MANAGER.get_all("opportunities")

            # Add the company name to each opportunity if available
            for opportunity in opportunities:
                employer = Employers().get_employer_by_id(opportunity["employer_id"])
                opportunity["company_name"] = (
                    employer["company_name"] if employer else "Unknown Company"
                )

            print(
                f"[DEBUG] Retrieved {len(opportunities)} opportunities after filtering."
            )
            return opportunities

        except Exception as e:
            print(f"[ERROR] Failed to search opportunities: {e}")
            return []

    def get_opportunities_by_title(self, title):
        """Fetch opportunities by title."""
        from app import DATABASE_MANAGER

        try:
            if not title:
                print("[DEBUG] No title provided.")
                return []

            query = {"title": {"$regex": title, "$options": "i"}}
            print(f"[DEBUG] Query for title: {query}")

            opportunities = DATABASE_MANAGER.get_all_by_field("opportunities", query)
            print(f"[DEBUG] Opportunities found: {len(opportunities)}")
            return opportunities
        except Exception as e:
            print(f"[ERROR] Failed to fetch opportunities by title: {e}")
            return []

    def get_opportunities_by_company(self, company_name):
        """Fetch opportunities by company."""
        from app import DATABASE_MANAGER

        try:
            if not company_name:
                print("[DEBUG] No company name provided.")
                return []

            # Find the employer by exact company name
            company = DATABASE_MANAGER.get_one_by_field(
                "employers", "company_name", company_name
            )

            if not company:
                print(f"[DEBUG] No company found for name: {company_name}")
                return []

            # Use the employer's _id to search for opportunities
            employer_id = company["_id"]
            print(f"[DEBUG] Employer ID found: {employer_id}")

            # Query the opportunities collection with employer_id

            opportunities = DATABASE_MANAGER.get_all_by_field(
                "opportunities", "employer_id", employer_id
            )
            print(f"[DEBUG] Opportunities found: {len(opportunities)}")

            return opportunities
        except Exception as e:
            print(f"[ERROR] Failed to fetch opportunities by company: {e}")
            return []

    def get_opportunity_by_company_id(self, company_id):
        """Get opportunity by company ID."""
        from app import DATABASE_MANAGER

        opportunities = DATABASE_MANAGER.get_all_by_field(
            "opportunities", "employer_id", company_id
        )
        return opportunities

    def get_opportunity_by_id(self, _id=None):
        """Getting opportunity."""
        from app import DATABASE_MANAGER

        if not _id:
            _id = request.form.get("_id")

        if cache["data"] and cache["last_updated"] > datetime.now():
            for opportunity in cache["data"]:
                if opportunity["_id"] == _id:
                    return opportunity
            return None

        cache["data"] = DATABASE_MANAGER.get_all("opportunities")
        cache["last_updated"] = datetime.now()

        opportunity = DATABASE_MANAGER.get_by_id("opportunities", _id)

        if opportunity:
            return opportunity

        return None

    def get_employer_by_id(self, _id):
        """Get employer_id by ID."""
        opportunity = self.get_opportunity_by_id(_id)
        if not opportunity:
            return ""
        return opportunity["employer_id"]

    def get_opportunities(self):
        """Getting all opportunities."""
        from app import DATABASE_MANAGER

        if cache["data"] and cache["last_updated"] > datetime.now():
            return jsonify(cache["data"]), 200

        cache["data"] = DATABASE_MANAGER.get_all("opportunities")
        cache["last_updated"] = datetime.now()

        return cache["data"]

    def get_opportunities_by_duration(self, duration):
        """Getting all opportunities that match duration."""
        from app import DATABASE_MANAGER

        duration_list = [d.strip().replace('"', "") for d in duration[1:-1].split(",")]
        data = DATABASE_MANAGER.get_all_by_in_list(
            "opportunities", "duration", duration_list
        )

        return jsonify(data), 200

    def delete_opportunity_by_id(self, opportunity_id):
        """Deleting opportunity."""
        from app import DATABASE_MANAGER

        opportunity = DATABASE_MANAGER.get_by_id("opportunities", opportunity_id)

        if opportunity:
            DATABASE_MANAGER.delete_by_id("opportunities", opportunity_id)
            cache["data"] = list(DATABASE_MANAGER.get_all("opportunities"))
            cache["last_updated"] = datetime.now()
            return jsonify({"message": "Opportunity deleted"}), 200

        return jsonify({"error": "Opportunity not found"}), 404

    def delete_opportunities(self):
        """Deleting all opportunities."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("opportunities")
        cache["data"] = []
        cache["last_updated"] = datetime.now()
        return jsonify({"message": "All opportunities deleted"}), 200

    def get_valid_students(self, opportunity_id):
        """Get valid students for an opportunity."""
        # pylint: disable=import-outside-toplevel
        from students.models import Student

        students = Student().get_students()
        valid_students = []
        for student in students:
            if "preferences" in student and opportunity_id in student["preferences"]:
                student["modules"] = [
                    d.strip().replace('"', "")
                    for d in student["modules"][1:-1].split(",")
                    if d.strip().replace('"', "") != ""
                ]
                student["skills"] = [
                    d.strip().replace('"', "")
                    for d in student["skills"][1:-1].split(",")
                    if d.strip().replace('"', "") != ""
                ]
                valid_students.append(student)
        return valid_students

    def rank_preferences(self, opportunity_id):
        """Sets a opportunity preferences."""
        from app import DATABASE_MANAGER

        opportunity = DATABASE_MANAGER.get_by_id("opportunities", opportunity_id)

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        preferences = [a[5:] for a in request.form.get("ranks").split(",")]
        DATABASE_MANAGER.update_one_by_field(
            "opportunities", "_id", opportunity_id, {"preferences": preferences}
        )
        return jsonify({"message": "Preferences updated"}), 200
