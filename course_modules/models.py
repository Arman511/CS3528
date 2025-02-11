"""
Course module model.
"""

from datetime import datetime, timedelta
import uuid
from flask import jsonify
import pandas as pd
from flask import send_file

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

        DATABASE_MANAGER.delete("modules", module["_id"])

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
            if "modules" in student and uuid in student["modules"]:
                student["modules"].remove(uuid)
                DATABASE_MANAGER.update_one_by_id("students", student["_id"], student)

        opportunities = DATABASE_MANAGER.get_all("opportunities")
        for opportunity in opportunities:
            if (
                "modules_required" in opportunity
                and uuid in opportunity["modules_required"]
            ):
                opportunity["modules_required"].remove(uuid)
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

        return

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
        return jsonify({"message": "Deleted"}), 200

    def download_all_modules(self):
        """Download all modules"""
        from app import DATABASE_MANAGER

        modules = DATABASE_MANAGER.get_all("modules")
        # Create a DataFrame from the modules
        df = pd.DataFrame(modules)

        # Define the file path
        file_path = "/tmp/modules.xlsx"

        df.drop(columns=["_id"], inplace=True)
        # Save the DataFrame to an Excel file
        df.to_excel(
            file_path,
            index=False,
            header=["Module_id", "Module_name", "Module_description"],
        )

        # Send the file as an attachment
        return send_file(file_path, download_name="modules.xlsx", as_attachment=True)

    def upload_course_modules(self, file):
        """Add course modules from an Excel file."""

        from app import DATABASE_MANAGER

        # Read the Excel file
        df = pd.read_excel(file)

        # Convert the DataFrame to a list of dictionaries
        modules = df.to_dict(orient="records")

        clean_data = []

        for i, module in enumerate(modules):
            temp = {
                "_id": uuid.uuid4().hex,
                "module_id": module.get("Module_id", ""),
                "module_name": module.get("Module_name", ""),
                "module_description": module.get("Module_description", ""),
            }
            if temp["module_id"] and temp["module_name"]:
                clean_data.append(temp)
            else:
                return jsonify({"error": "Invalid data in row " + str(i + 1)}), 400

            if DATABASE_MANAGER.get_one_by_field(
                "modules", "module_id", temp["module_id"]
            ):
                return jsonify({"error": "module already in database"}), 400

        for module in clean_data:
            DATABASE_MANAGER.insert("modules", module)

        # Update cache
        modules = DATABASE_MANAGER.get_all("modules")
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify({"message": "Uploaded"}), 200
