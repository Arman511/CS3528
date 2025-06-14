"""
Opportunity model.
"""

from html import escape
import tempfile
import uuid
from flask import jsonify, send_file, session
import pandas as pd
from core import handlers
from employers.models import Employers


class Opportunity:
    """Opportunity class."""

    def add_update_opportunity(
        self,
        opportunity,
        is_admin=False,
    ):
        """Adding new opportunity."""
        from app import DATABASE_MANAGER

        find_opportunity = DATABASE_MANAGER.get_one_by_id(
            "opportunities", opportunity["_id"]
        )
        if find_opportunity and not is_admin:
            if find_opportunity["employer_id"] != session["employer"]["_id"]:
                return jsonify({"error": "Unauthorized Access."}), 401
        DATABASE_MANAGER.delete_by_id("opportunities", opportunity["_id"])

        DATABASE_MANAGER.insert("opportunities", opportunity)

        if opportunity:
            return jsonify(opportunity), 200

        return jsonify({"error": "Opportunity not added"}), 400

    def get_opportunities_for_search(self, _id):
        """Get opportunities for search."""
        from app import DATABASE_MANAGER

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        employers_map = {
            employer["_id"]: employer["company_name"]
            for employer in Employers().get_employers()
        }
        for opportunity in opportunities:
            if "preferences" in opportunity:
                opportunity["ranked"] = True
            opportunity["company_name"] = employers_map.get(
                opportunity["employer_id"], "Unknown Company"
            )

        if not _id:
            return opportunities

        filtered_opportunities = [
            opportunity
            for opportunity in opportunities
            if opportunity["employer_id"] == _id
        ]
        return filtered_opportunities

    def get_opportunities_by_title(self, title):
        """Fetch opportunities by title."""
        from app import DATABASE_MANAGER

        try:
            if not title:
                print("[DEBUG] No title provided.")
                return []

            query = {"title": {"$regex": title, "$options": "i"}}
            print(f"[DEBUG] Query for title: {query}")

            opportunities = DATABASE_MANAGER.get_all_by_field(
                "opportunities", "title", {"$regex": title, "$options": "i"}
            )
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

        return DATABASE_MANAGER.get_all("opportunities")

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

        students = DATABASE_MANAGER.get_all("students")

        for student in students:
            if "preferences" in student and opportunity_id in student["preferences"]:
                student["preferences"].remove(opportunity_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        return jsonify({"message": "Opportunity deleted"}), 200

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
                DATABASE_MANAGER.delete_field_by_id(
                    "students", student["_id"], "preferences"
                )

        DATABASE_MANAGER.delete_all("opportunities")

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
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
            df.to_excel(temp_file.name, index=False)
            temp_file_path = temp_file.name

            return send_file(
                temp_file_path, as_attachment=True, download_name="opportunities.xlsx"
            )

    def upload_opportunities(self, file, is_admin):
        """Upload opportunities from an Excel file."""
        from app import DATABASE_MANAGER

        expected_columns = {
            "Title",
            "Description",
            "URL",
            "Modules_required",
            "Courses_required",
            "Spots_available",
            "Location",
            "Duration",
        }
        if is_admin:
            expected_columns.add("Employer_email")

        try:
            df = handlers.excel_verifier_and_reader(file, expected_columns)
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
                    "spots_available": int(opportunity["Spots_available"]),
                    "location": opportunity["Location"],
                    "duration": opportunity["Duration"],
                }

                if (
                    not isinstance(temp["spots_available"], int)
                    or temp["spots_available"] < 1
                ):
                    raise ValueError(
                        f"Invalid spots available value in opportunity: {temp['title']}, row {i+2}"
                    )
                if is_admin:
                    employer_id = email_to_employers_map.get(
                        opportunity["Employer_email"].lower().strip()
                    )
                    if employer_id:
                        temp["employer_id"] = employer_id
                    else:
                        raise ValueError(
                            f"Employer email {opportunity['Employer_email']} not found "
                            f"in database at row {i+2}"
                        )
                else:
                    temp["employer_id"] = session["employer"]["_id"]

                if not temp["duration"]:
                    raise ValueError(
                        f"Duration is required and cannot be empty in opportunity: "
                        f"{temp['title']}, row {i+2}"
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
                    raise ValueError(
                        f"Invalid duration value in opportunity: {temp['title']}, row {i+2}"
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
                    raise ValueError(
                        f"Invalid module(s) in opportunity: {temp['title']}, row {i+2}"
                    )
                if not set(temp["courses_required"]).issubset(courses):
                    raise ValueError(
                        f"Invalid course(s) in opportunity: {temp['title']}, row {i+2}"
                    )
                if not isinstance(temp["title"], str) or not temp["title"].strip():
                    raise ValueError(
                        f"Title is required and cannot be empty in opportunity at row {i+2}"
                    )
                if (
                    not isinstance(temp["description"], str)
                    or not temp["description"].strip()
                ):
                    raise ValueError(
                        f"Description is required and cannot be empty in opportunity at row {i+2}"
                    )
                if not isinstance(temp["location"], str):
                    temp["location"] = ""
                if not isinstance(temp["url"], str):
                    temp["url"] = ""

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

                temp["title"] = escape(temp["title"])
                temp["description"] = escape(temp["description"])
                temp["url"] = escape(temp["url"])
                temp["location"] = escape(temp["location"])
                temp["duration"] = escape(temp["duration"])
                temp["modules_required"] = [
                    escape(module) for module in temp["modules_required"]
                ]
                temp["courses_required"] = [
                    escape(course) for course in temp["courses_required"]
                ]
                clean_data.append(temp)

            if clean_data:
                DATABASE_MANAGER.insert_many("opportunities", clean_data)

            return jsonify({"message": "Opportunities uploaded successfully"}), 200

        except Exception as e:
            print(f"[ERROR] Failed to upload opportunities: {e}")
            return jsonify({"error": f"Failed to upload opportunities: {e}"}), 400
