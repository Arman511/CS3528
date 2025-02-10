"""
Course module model.
"""

from datetime import datetime, timedelta
from flask import jsonify

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
