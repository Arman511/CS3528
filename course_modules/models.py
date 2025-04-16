"""
Course module model.
"""

from datetime import datetime, timedelta
from html import escape
import tempfile
import uuid
import pandas as pd
from flask import send_file, jsonify

from core import handlers

# Cache to store modules and the last update time
modules_cache = {"data": None, "last_updated": None}


class Module:
    """Module data model"""

    def add_module(self, module):
        """Adds a module to the database."""
        from app import DATABASE_MANAGER

        # module = {
        #     "_id": uuid.uuid1().hex,
        #     "module_id": request.form.get("module_id"),
        #     "module_name": request.form.get("module_name"),
        #     "module_description": request.form.get("module_description"),
        # }

        if DATABASE_MANAGER.get_one_by_field(
            "modules", "module_id", module["module_id"]
        ):
            return jsonify({"error": "module already in database"}), 400

        DATABASE_MANAGER.insert("modules", module)

        if module:
            # Update cache
            modules = DATABASE_MANAGER.get_all("modules")
            modules_cache["data"] = modules
            modules_cache["last_updated"] = datetime.now()
            return jsonify(module), 200

        return jsonify({"error": "module not added"}), 400

    def delete_module_by_id(self, module_id):
        """Deletes a module from the database."""
        from app import DATABASE_MANAGER

        module = DATABASE_MANAGER.get_one_by_field("modules", "module_id", module_id)

        if not module:
            return jsonify({"error": "module not found"}), 404

        DATABASE_MANAGER.delete_by_id("modules", module["_id"])

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if "modules" in student and module_id in student["modules"]:
                student["modules"].remove(module_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if (
                "modules_required" in opportunity
                and module_id in opportunity["modules_required"]
            ):
                opportunity["modules_required"].remove(module_id)
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        # Update cache
        modules = DATABASE_MANAGER.get_all("modules")
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify(module), 200

    def delete_module_by_uuid(self, uuid):
        """Deletes a module from the database."""

        from app import DATABASE_MANAGER

        module = DATABASE_MANAGER.get_one_by_id("modules", uuid)

        if not module:
            return jsonify({"error": "module not found"}), 404

        DATABASE_MANAGER.delete_by_id("modules", uuid)

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if "modules" in student and module["module_id"] in student["modules"]:
                student["modules"].remove(module["module_id"])
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if (
                "modules_required" in opportunity
                and uuid in opportunity["modules_required"]
            ):
                opportunity["modules_required"].remove(module["module_id"])
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        # Update cache
        modules = DATABASE_MANAGER.get_all("modules")
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify(module), 200

    def get_module_by_id(self, module_id):
        """Retrieves a module by its ID."""
        from app import DATABASE_MANAGER

        module = DATABASE_MANAGER.get_one_by_field("modules", "module_id", module_id)

        if module:
            return module

        return None

    def get_module_by_uuid(self, uuid):
        """Retrieves a module by its ID."""
        from app import DATABASE_MANAGER

        module = DATABASE_MANAGER.get_one_by_id("modules", uuid)

        if module:
            return module

        return None

    def get_module_name_by_id(self, module_id):
        """Get module name by id"""
        module = self.get_module_by_id(module_id)
        if not module:
            return None
        return module["module_name"]

    def get_modules(self):
        """Retrieves all modules."""
        current_time = datetime.now()
        one_week_ago = current_time - timedelta(weeks=1)
        from app import DATABASE_MANAGER

        # Check if cache is valid
        if (
            modules_cache["data"]
            and modules_cache["last_updated"]
            and modules_cache["last_updated"] > one_week_ago
        ):
            return modules_cache["data"]

        # Fetch modules from the database
        modules = DATABASE_MANAGER.get_all("modules")

        if modules:
            # Update cache
            modules_cache["data"] = modules
            modules_cache["last_updated"] = current_time
            return modules

        return []

    def get_modules_map(self):
        """Get modules map"""
        modules = self.get_modules()
        return {module["module_id"]: module for module in modules}

    def reset_cache(self):
        """Reset cache"""
        from app import DATABASE_MANAGER

        modules_cache["data"] = DATABASE_MANAGER.get_all("modules")
        modules_cache["last_updated"] = datetime.now()

    def update_module_by_uuid(self, uuid, module_id, module_name, module_description):
        """Updates a module in the database."""

        from app import DATABASE_MANAGER

        original_module = DATABASE_MANAGER.get_one_by_id("modules", uuid)
        if not DATABASE_MANAGER.get_one_by_id("modules", uuid):
            return jsonify({"error": "module not found"}), 404

        updated_module = {
            "_id": uuid,
            "module_id": module_id,
            "module_name": module_name,
            "module_description": module_description,
        }

        DATABASE_MANAGER.update_one_by_id("modules", uuid, updated_module)

        students = DATABASE_MANAGER.get_all("students")
        for student in students:
            if (
                "modules" in student
                and original_module["module_id"] in student["modules"]
            ):
                student["modules"].remove(original_module["module_id"])
                student["modules"].append(module_id)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if (
                "modules_required" in opportunity
                and original_module["module_id"] in opportunity["modules_required"]
            ):
                opportunity["modules_required"].remove(original_module["module_id"])
                opportunity["modules_required"].append(module_id)
                DATABASE_MANAGER.update_one_by_id(
                    "opportunities", opportunity["_id"], opportunity
                )

        # Update cache
        modules = DATABASE_MANAGER.get_all("modules")
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Updated"}), 200

    def delete_all_modules(self):
        """Deletes all modules from the database."""
        from app import DATABASE_MANAGER

        DATABASE_MANAGER.delete_all("modules")
        modules_cache["data"] = []
        modules_cache["last_updated"] = datetime.now()

        students = DATABASE_MANAGER.get_all("students")
        DATABASE_MANAGER.delete_all("students")
        updated_students = []
        for student in students:
            if "modules" in student:
                student["modules"] = []
            updated_students.append(student)

        if updated_students:
            DATABASE_MANAGER.insert_many("students", updated_students)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        DATABASE_MANAGER.delete_all("opportunities")
        updated_opportunities = []
        for opp in opportunities:
            opp["modules_required"] = []
            updated_opportunities.append(opp)
        if updated_opportunities:
            DATABASE_MANAGER.insert_many("opportunities", updated_opportunities)

        return jsonify({"message": "Deleted"}), 200

    def download_all_modules(self):
        """Download all modules"""
        from app import DATABASE_MANAGER

        modules = DATABASE_MANAGER.get_all("modules")
        # Create a DataFrame from the modules
        df = pd.DataFrame(modules)

        # Use tempfile to create a temporary file
        df.drop(columns=["_id"], inplace=True)
        with tempfile.NamedTemporaryFile(suffix=".xlsx") as tmp:
            file_path = tmp.name
            # Save the DataFrame to an Excel file
            df.to_excel(
                file_path,
                index=False,
                header=["Module_id", "Module_name", "Module_description"],
            )

            return send_file(
                file_path, download_name="modules.xlsx", as_attachment=True
            )

    def upload_course_modules(self, file):
        """Add course modules from an Excel file."""

        from app import DATABASE_MANAGER

        # Read the Excel file
        try:
            df = handlers.excel_verifier_and_reader(
                file,
                {"Module_id", "Module_name", "Module_description"},
            )
        except Exception as e:
            return jsonify({"error": f"Failed to read file: {str(e)}"}), 400

        # Convert the DataFrame to a list of dictionaries
        modules = df.to_dict(orient="records")

        clean_data = []
        current_ids = set(
            module["module_id"] for module in DATABASE_MANAGER.get_all("modules")
        )

        ids = set()

        for i, module in enumerate(modules):
            temp = {
                "_id": uuid.uuid4().hex,
                "module_id": escape(module.get("Module_id", "")),
                "module_name": escape(module.get("Module_name", "")),
                "module_description": escape(module.get("Module_description", "")),
            }
            if not temp["module_id"] or not temp["module_name"]:
                return jsonify({"error": "Invalid data in row " + str(i + 1)}), 400
            if temp["module_id"] in ids:
                return (
                    jsonify({"error": "Duplicate module ID in row " + str(i + 1)}),
                    400,
                )
            if temp["module_id"] in current_ids:
                return jsonify({"error": "Module already in database"}), 400
            clean_data.append(temp)
            ids.add(temp["module_id"])

        DATABASE_MANAGER.insert_many("modules", clean_data)

        # Update cache
        modules = DATABASE_MANAGER.get_all("modules")
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Uploaded"}), 200
