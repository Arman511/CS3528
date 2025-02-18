"""
Opportunity model.
"""

from datetime import datetime
import uuid
from flask import jsonify, send_file, session
import pandas as pd
from core import handlers
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
        find_opportunity = DATABASE_MANAGER.get_one_by_id(
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
                    "opportunities", "title", {"$regex": title, "$options": "i"}
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

    def get_opportunity_by_id(self, _id):
        """Getting opportunity."""
        from app import DATABASE_MANAGER

        if cache["data"] and cache["last_updated"] > datetime.now():
            for opportunity in cache["data"]:
                if opportunity["_id"] == _id:
                    return opportunity
            return None

        cache["data"] = DATABASE_MANAGER.get_all("opportunities")
        cache["last_updated"] = datetime.now()

        opportunity = DATABASE_MANAGER.get_one_by_id("opportunities", _id)

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

        opportunity = DATABASE_MANAGER.get_one_by_id("opportunities", opportunity_id)

        if (
            handlers.get_user_type() == "employer"
            and opportunity["employer_id"] != session["employer"]["_id"]
        ):
            return jsonify({"error": "Unauthorized Access."}), 401
        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        DATABASE_MANAGER.delete_by_id("opportunities", opportunity_id)
        cache["data"] = list(DATABASE_MANAGER.get_all("opportunities"))
        cache["last_updated"] = datetime.now()

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if "preferences" in student and opportunity_id in student["preferences"]:
                student["preferences"].remove(opportunity_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Opportunity deleted"}), 200

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
                valid_students.append(student)
        return valid_students

    def rank_preferences(self, opportunity_id, preferences):
        """Sets a opportunity preferences."""
        from app import DATABASE_MANAGER

        opportunity = DATABASE_MANAGER.get_one_by_id("opportunities", opportunity_id)

        if not opportunity:
            return jsonify({"error": "Opportunity not found"}), 404

        DATABASE_MANAGER.update_one_by_field(
            "opportunities", "_id", opportunity_id, {"preferences": preferences}
        )
        return jsonify({"message": "Preferences updated"}), 200

    def delete_all_opportunities(self, is_admin):
        """Deleting all opportunities."""
        if is_admin:
            return self.delete_all_opportunities_admin()
        else:
            return self.delete_all_opportunities_employer()

    def delete_all_opportunities_employer(self):
        """Deleting all opportunities."""
        from app import DATABASE_MANAGER

        opportunities = DATABASE_MANAGER.get_all_by_field(
            "opportunities", "employer_id", session["employer"]["_id"]
        )
        opportunity_ids = set(opportunity["_id"] for opportunity in opportunities)

        for opportunity in opportunities:
            DATABASE_MANAGER.delete_by_id("opportunities", opportunity["_id"])

        cache["data"] = list(DATABASE_MANAGER.get_all("opportunities"))
        cache["last_updated"] = datetime.now()

        students = DATABASE_MANAGER.get_all("students")

        student_updates = []
        for student in students:
            if "preferences" in student:
                new_preferences = [
                    preference
                    for preference in student["preferences"]
                    if preference not in opportunity_ids
                ]
                if new_preferences != student["preferences"]:
                    student_updates.append((student["_id"], new_preferences))

        for student_id, new_preferences in student_updates:
            DATABASE_MANAGER.update_one_by_id(
                "students", student_id, {"preferences": new_preferences}
            )

        return jsonify({"message": "All opportunities deleted"}), 200

    def delete_all_opportunities_admin(self):
        """Deleting all opportunities."""
        from app import DATABASE_MANAGER

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if "preferences" in student:
                student["preferences"] = []
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        DATABASE_MANAGER.delete_all("opportunities")
        cache["data"] = []
        cache["last_updated"] = datetime.now()
        return jsonify({"message": "All opportunities deleted"}), 200

    def download_opportunities(self, is_admin):
        """Download all opportunities."""
        from app import DATABASE_MANAGER

        opportunities_data = []
        if is_admin:
            employers = DATABASE_MANAGER.get_all("employers")
            employers_dict = {
                employer["_id"]: employer["email"] for employer in employers
            }
            opportunities = DATABASE_MANAGER.get_all("opportunities")
        else:
            opportunities = DATABASE_MANAGER.get_all_by_field(
                "opportunities", "employer_id", session["employer"]["_id"]
            )

        for opportunity in opportunities:
            opportunity_data = {
                "Title": opportunity.pop("title"),
                "Description": opportunity.pop("description"),
                "URL": opportunity.pop("url"),
                "Modules_required": ",".join(opportunity.pop("modules_required")),
                "Courses_required": ",".join(opportunity.pop("courses_required")),
                "Spots_available": opportunity.pop("spots_available"),
                "Location": opportunity.pop("location"),
                "Duration": opportunity.pop("duration"),
            }
            if is_admin:
                employer_email = employers_dict.get(opportunity["employer_id"])
                if employer_email:
                    opportunity_data["Employer_email"] = employer_email
            del opportunity["_id"]
            del opportunity["employer_id"]
            opportunities_data.append(opportunity_data)

        df = pd.DataFrame(opportunities_data)
        file_path = "/tmp/opportunities.xlsx"
        df.to_excel(file_path, index=False)

        return send_file(
            file_path, as_attachment=True, download_name="opportunities.xlsx"
        )

    def upload_opportunities(self, file, is_admin):
        """Upload opportunities from an Excel file."""
        from app import DATABASE_MANAGER

        try:
            df = pd.read_excel(file)
            opportunities = df.to_dict(orient="records")

            email_to_employers_map = {
                employer["email"].lower(): employer["_id"]
                for employer in DATABASE_MANAGER.get_all("employers")
            }
            modules = set(
                module["module_id"] for module in DATABASE_MANAGER.get_all("modules")
            )
            courses = set(
                course["course_id"] for course in DATABASE_MANAGER.get_all("courses")
            )
            clean_data = []
            for i, opportunity in enumerate(opportunities):
                temp = {
                    "_id": uuid.uuid4().hex,
                    "title": opportunity["Title"],
                    "description": opportunity["Description"],
                    "url": opportunity["URL"],
                    "spots_available": opportunity["Spots_available"],
                    "location": opportunity["Location"],
                    "duration": opportunity["Duration"],
                }

                try:
                    temp["spots_available"] = int(temp["spots_available"])
                except Exception:
                    return (
                        jsonify(
                            {
                                "error": f"Invalid spots available value in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                if is_admin:
                    employer_id = email_to_employers_map.get(
                        opportunity["Employer_email"].lower().strip()
                    )
                    if employer_id:
                        temp["employer_id"] = employer_id
                    else:
                        return (
                            jsonify(
                                {
                                    "error": f"Employer email {opportunity['Employer_email']} not found in database at row {i+2}"
                                }
                            ),
                            400,
                        )
                else:
                    temp["employer_id"] = session["employer"]["_id"]

                if not temp["duration"]:
                    return (
                        jsonify(
                            {
                                "error": f"Duration is required and cannot be empty in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                if temp["duration"] not in set(
                    [
                        "1_day",
                        "1_week",
                        "1_month",
                        "3_months",
                        "6_months",
                        "12_months",
                    ]
                ):
                    return (
                        jsonify(
                            {
                                "error": f"Invalid duration value in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                modules_required_string = opportunity["Modules_required"]
                if not isinstance(modules_required_string, str):
                    temp["modules_required"] = []
                else:
                    temp["modules_required"] = [
                        module.strip()
                        for module in modules_required_string.replace('"', "").split(
                            ","
                        )
                    ]

                courses_required_string = opportunity["Courses_required"]
                if not isinstance(courses_required_string, str):
                    temp["courses_required"] = []
                else:
                    temp["courses_required"] = [
                        course.strip()
                        for course in courses_required_string.replace('"', "").split(
                            ","
                        )
                    ]

                if not set(temp["modules_required"]).issubset(modules):
                    return (
                        jsonify(
                            {
                                "error": f"Invalid module(s) in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                if not set(temp["courses_required"]).issubset(courses):
                    return (
                        jsonify(
                            {
                                "error": f"Invalid course(s) in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                if not isinstance(temp["title"], str) or not temp["title"].strip():
                    return (
                        jsonify(
                            {
                                "error": f"Title is required and cannot be empty in opportunity at row {i+2}"
                            }
                        ),
                        400,
                    )
                if (
                    not isinstance(temp["description"], str)
                    or not temp["description"].strip()
                ):
                    return (
                        jsonify(
                            {
                                "error": f"Description is required and cannot be empty in opportunity at row {i+2}"
                            }
                        ),
                        400,
                    )
                if not isinstance(temp["location"], str):
                    temp["location"] = ""
                if not isinstance(temp["url"], str):
                    temp["url"] = ""
                if (
                    not isinstance(temp["spots_available"], int)
                    or temp["spots_available"] < 1
                ):
                    return (
                        jsonify(
                            {
                                "error": f"Spots available must be at least 1 in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )
                if not isinstance(temp["duration"], str):
                    return (
                        jsonify(
                            {
                                "error": f"Duration is required and cannot be empty in opportunity: {temp['title']}, row {i+2}"
                            }
                        ),
                        400,
                    )

                temp["title"] = temp["title"].strip()
                temp["description"] = temp["description"].strip()
                temp["url"] = (
                    temp["url"].strip() if isinstance(temp["url"], str) else ""
                )
                temp["location"] = (
                    temp["location"].strip()
                    if isinstance(temp["location"], str)
                    else ""
                )

                clean_data.append(temp)

            DATABASE_MANAGER.insert_many("opportunities", clean_data)
            cache["data"] = list(DATABASE_MANAGER.get_all("opportunities"))
            cache["last_updated"] = datetime.now()

            return jsonify({"message": "Opportunities uploaded successfully"}), 200

        except Exception as e:
            print(f"[ERROR] Failed to upload opportunities: {e}")
            return jsonify({"error": "Failed to upload opportunities"}), 500
