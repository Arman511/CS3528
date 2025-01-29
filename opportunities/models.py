"""
Opportunity model.
"""

from datetime import datetime
from flask import jsonify, request, session
from core import database
from employers.models import Employers

cache = {"data": [], "last_updated": datetime.now()}


class Opportunity:
    """Opportunity class."""

    def add_update_opportunity(self, is_admin=False):
        """Adding new opportunity."""
        if is_admin:
            opportunity = {
                "_id": request.form.get("_id"),
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "url": request.form.get("url"),
                "employer_id": request.form.get("employer_id"),
                "location": request.form.get("location"),
                "modules_required": request.form.get("modules_required"),
                "courses_required": request.form.get("courses_required"),
                "spots_available": request.form.get("spots_available"),
                "duration": request.form.get("duration"),
            }
            database.opportunities_collection.delete_one(
                {"_id": request.form.get("_id")}
            )
            database.opportunities_collection.insert_one(opportunity)

            cache["data"] = list(database.opportunities_collection.find())
            cache["last_updated"] = datetime.now()
            return jsonify(opportunity), 200

        opportunity = {
            "_id": request.form.get("_id"),
            "title": request.form.get("title"),
            "description": request.form.get("description"),
            "url": request.form.get("url"),
            "employer_id": session["employer"]["_id"],
            "location": request.form.get("location"),
            "modules_required": request.form.get("modules_required"),
            "courses_required": request.form.get("courses_required"),
            "spots_available": request.form.get("spots_available"),
            "duration": request.form.get("duration"),
        }
        find_opportunity = database.opportunities_collection.find_one(
            {"_id": request.form.get("_id")}
        )
        if find_opportunity:
            if find_opportunity["employer_id"] != session["employer"]["_id"]:
                return jsonify({"error": "Unauthorized Access."}), 401
        database.opportunities_collection.delete_one({"_id": request.form.get("_id")})

        database.opportunities_collection.insert_one(opportunity)

        cache["data"] = list(database.opportunities_collection.find())
        cache["last_updated"] = datetime.now()

        if opportunity:
            return jsonify(opportunity), 200

        return jsonify({"error": "Opportunity not added"}), 400

    def search_opportunities(self, title, company_name):
        """Search opportunities by title and/or company."""
        opportunities = []

        try:
            # Build the query dynamically based on the provided parameters
            query = {}
            if title:
                query["title"] = {"$regex": title, "$options": "i"}
            if company_name:
                company = database.employers_collection.find_one(
                    {"company_name": company_name}
                )
                if company:
                    query["employer_id"] = company["_id"]
                else:
                    print(f"[DEBUG] No employer found for company name: {company_name}")
                    return []

            print(f"[DEBUG] Querying opportunities with filter: {query}")
            opportunities = list(database.opportunities_collection.find(query))

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
        try:
            if not title:
                print("[DEBUG] No title provided.")
                return []

            query = {"title": {"$regex": title, "$options": "i"}}
            print(f"[DEBUG] Query for title: {query}")

            opportunities = list(database.opportunities_collection.find(query))
            print(f"[DEBUG] Opportunities found: {len(opportunities)}")
            return opportunities
        except Exception as e:
            print(f"[ERROR] Failed to fetch opportunities by title: {e}")
            return []

    def get_opportunities_by_company(self, company_name):
        """Fetch opportunities by company."""
        try:
            if not company_name:
                print("[DEBUG] No company name provided.")
                return []

            # Find the employer by exact company name
            company = database.employers_collection.find_one(
                {"company_name": company_name}
            )

            if not company:
                print(f"[DEBUG] No company found for name: {company_name}")
                return []

            # Use the employer's _id to search for opportunities
            employer_id = company["_id"]
            print(f"[DEBUG] Employer ID found: {employer_id}")

            # Query the opportunities collection with employer_id
            query = {"employer_id": employer_id}
            print(f"[DEBUG] Query for opportunities: {query}")

            opportunities = list(database.opportunities_collection.find(query))
            print(f"[DEBUG] Opportunities found: {len(opportunities)}")

            return opportunities
        except Exception as e:
            print(f"[ERROR] Failed to fetch opportunities by company: {e}")
            return []

    def get_opportunity_by_company_id(self, company_id):
        """Get opportunity by company ID."""
        opportunities = list(
            database.opportunities_collection.find({"employer_id": company_id})
        )
        return opportunities

    def get_opportunity_by_id(self, _id=None):
        """Getting opportunity."""
        if not _id:
            _id = request.form.get("_id")

        if cache["data"] and cache["last_updated"] > datetime.now():
            for opportunity in cache["data"]:
                if opportunity["_id"] == _id:
                    return opportunity
            return None

        cache["data"] = list(database.opportunities_collection.find())
        cache["last_updated"] = datetime.now()

        opportunity = database.opportunities_collection.find_one({"_id": _id})

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

        if cache["data"] and cache["last_updated"] > datetime.now():
            return jsonify(cache["data"]), 200

        cache["data"] = list(database.opportunities_collection.find())
        cache["last_updated"] = datetime.now()

        return cache["data"]

    # def get_opportunities_by_company(self, user_type=None):
    #     """Getting all opportunities by company."""
    #     if user_type == "admin":
    #         return self.get_opportunities()

    #     valid_opportunities = []
    #     for opp in self.get_opportunities():
    #         if opp["employer_id"] == user_type:
    #             valid_opportunities.append(opp)

    #     return valid_opportunities

    def get_opportunities_by_duration(self, duration):
        """Getting all opportunities that match duration."""
        duration_list = [d.strip().replace('"', "") for d in duration[1:-1].split(",")]
        data = list(
            database.opportunities_collection.find({"duration": {"$in": duration_list}})
        )
        return jsonify(data), 200

    def update_opportunity(self):
        """Updating opportunity."""
        opportunity = database.opportunities_collection.find_one(
            {"_id": request.form.get("_id")}
        )

        if opportunity:
            database.opportunities_collection.update_one(
                {"_id": request.form.get("_id")}, {"$set": request.form}
            )

            cache["data"] = list(database.opportunities_collection.find())
            cache["last_updated"] = datetime.now()
            return jsonify({"message": "Opportunity updated"}), 200

        return jsonify({"error": "Opportunity not found"}), 404

    def delete_opportunity_by_id(self, opportunity_id):
        """Deleting opportunity."""
        opportunity = database.opportunities_collection.find_one(
            {"_id": opportunity_id}
        )

        if opportunity:
            database.opportunities_collection.delete_one({"_id": opportunity_id})
            cache["data"] = list(database.opportunities_collection.find())
            cache["last_updated"] = datetime.now()
            return jsonify({"message": "Opportunity deleted"}), 200

        return jsonify({"error": "Opportunity not found"}), 404

    def delete_opportunities(self):
        """Deleting all opportunities."""
        opportunities = list(database.opportunities_collection.find())

        if opportunities:
            database.opportunities_collection.delete_many({})
            cache["data"] = []
            cache["last_updated"] = datetime.now()
            return jsonify({"message": "All opportunities deleted"}), 200

        return jsonify({"error": "No opportunities found"}), 404

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
        opportunity = database.opportunities_collection.find_one(
            {"_id": opportunity_id}
        )

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        preferences = [a[5:] for a in request.form.get("ranks").split(",")]
        database.opportunities_collection.update_one(
            {"_id": opportunity_id}, {"$set": {"preferences": preferences}}
        )
        return jsonify({"message": "Preferences updated"}), 200
