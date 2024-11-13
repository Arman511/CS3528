"""
Opportunity model.
"""

from datetime import datetime
import uuid
from flask import jsonify, request, session
import pandas as pd
from core import database, handlers
from students.models import Student

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

    def search_opportunities(self):
        """Searching opportunities."""
        title = request.form.get("title")
        company = request.form.get("company")
        location = request.form.get("location")
        skills_required = request.form.get("skills_required")

        query = {}
        if title:
            query["title"] = title
        if company:
            query["company"] = company
        if location:
            query["location"] = location
        if skills_required:
            query["skills_required"] = skills_required

        opportunities = list(database.opportunities_collection.find(query))

        if opportunities:
            return jsonify(opportunities), 200

        return jsonify({"error": "No opportunities found"}), 404

    def get_opportunity_by_id(self, _id=None):
        """Getting opportunity."""
        if not _id:
            _id = request.form.get("_id")

        if cache["data"] and cache["last_updated"] > datetime.now():
            for opportunity in cache["data"]:
                if opportunity["_id"] == _id:
                    return jsonify(opportunity), 200
            return None

        cache["data"] = list(database.opportunities_collection.find())
        cache["last_updated"] = datetime.now()

        opportunity = database.opportunities_collection.find_one({"_id": _id})

        if opportunity:
            return opportunity

        return None

    def get_opportunities(self):
        """Getting all opportunities."""

        if cache["data"] and cache["last_updated"] > datetime.now():
            return jsonify(cache["data"]), 200

        cache["data"] = list(database.opportunities_collection.find())
        cache["last_updated"] = datetime.now()

        return jsonify(cache["data"]), 200

    def get_opportunities_by_duration(self, duration):
        """Getting all opportunities that macth duration."""
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

    def import_opportunities_from_csv(self):
        """Importing opportunities from CSV file."""

        if not "file" in request.files:
            return jsonify({"error": "No file part"}), 400

        if not handlers.allowed_file(request.files["file"].filename, ["csv"]):
            return jsonify({"error": "Invalid file type"}), 400

        try:
            file = request.files["file"]
            df = pd.read_csv(file)

            opportunities = df.to_dict(orient="records")
            for opportunity in opportunities:
                opportunity["_id"] = uuid.uuid1().hex
                database.opportunities_collection.delete_one(
                    {"title": opportunity["title"]}
                )

            database.opportunities_collection.insert_many(opportunities)
            return jsonify({"message": "Opportunities imported"}), 200
        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            FileNotFoundError,
        ) as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

    def import_opportunities_from_xlsx(self):
        """Importing opportunities from Excel file."""

        if not "file" in request.files:
            return jsonify({"error": "No file part"}), 400

        if not handlers.allowed_file(request.files["file"].filename, ["xlsx", "xls"]):
            return jsonify({"error": "Invalid file type"}), 400

        try:
            file = request.files["file"]
            df = pd.read_excel(file)

            opportunities = df.to_dict(orient="records")
            for opportunity in opportunities:
                opportunity["_id"] = uuid.uuid1().hex
            database.opportunities_collection.insert_many(opportunities)

            return jsonify({"message": "Opportunities imported"}), 200
        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            FileNotFoundError,
        ) as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

    def get_valid_students(self, opportunity_id):
        students = Student().get_students()
        valid_students = []
        for student in students:
            if "preference" in student and opportunity_id in student["preferences"]:
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
        opportunity = database.opportunities_collection.find_one({"opportunity_id": opportunity_id})

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        preferences = [a[5:] for a in request.form.get("ranks").split(",")]
        database.opportunities_collection.update_one(
            {"opportunity_id": opportunity_id}, {"$set": {"preferences": preferences}}
        )
        return jsonify({"message": "Preferences updated"}), 200