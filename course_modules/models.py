"""
Course module model.
"""

import uuid
from datetime import datetime, timedelta
from flask import jsonify, request
from core import database

# Cache to store modules and the last update time
modules_cache = {"data": None, "last_updated": None}


class Module:
    """Module data model"""

    def add_module(self):
        """Adds a module to the database."""
        module = {
            "_id": uuid.uuid1().hex,
            "module_id": request.form.get("module_id"),
            "module_name": request.form.get("module_name"),
            "module_description": request.form.get("module_description"),
        }

        if database.modules_collection.find_one(
            {"module_id": request.form.get("module_id")}
        ):
            return jsonify({"error": "module already in database"}), 400

        database.modules_collection.insert_one(module)

        if module:
            # Update cache
            modules = list(database.modules_collection.find())
            modules_cache["data"] = modules
            modules_cache["last_updated"] = datetime.now()
            return jsonify(module), 200

        return jsonify({"error": "module not added"}), 400

    def delete_module(self):
        """Deletes a module from the database."""
        module = database.modules_collection.find_one(
            {"module_id": request.form.get("module_id")}
        )

        if not module:
            return jsonify({"error": "module not found"}), 404

        database.modules_collection.delete_one(
            {"module_id": request.form.get("module_id")}
        )

        # Update cache
        modules = list(database.modules_collection.find())
        modules_cache["data"] = modules
        modules_cache["last_updated"] = datetime.now()

        return jsonify(module), 200

    def get_module_by_id(self, module_id=None):
        """Retrieves a module by its ID."""
        if module_id is None:
            module_id = request.form.get("module_id")
        module = database.modules_collection.find_one({"module_id": module_id})

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

        # Check if cache is valid
        if (
            modules_cache["data"]
            and modules_cache["last_updated"]
            and modules_cache["last_updated"] > one_week_ago
        ):
            return modules_cache["data"]

        # Fetch modules from the database
        modules = list(database.modules_collection.find())

        if modules:
            # Update cache
            modules_cache["data"] = modules
            modules_cache["last_updated"] = current_time
            return modules

        return []
