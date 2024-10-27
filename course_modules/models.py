"""
This module defines the module class and provides methods to manage modules in the database.
Classes:
    module: A class to represent and manage modules.
Methods:
    add_module(self):
        Adds a new module to the database.
        Updates the modules cache upon successful addition.
        Returns a JSON response with the added module or an error message.
    delete_module(self):
        Deletes a module from the database based on the module_id provided in the request.
        Updates the modules cache upon successful deletion.
        Returns a JSON response with the deleted module or an error message.
    get_module_by_id(self):
        Retrieves a module from the database based on the module_id provided in the request.
        Returns a JSON response with the module details or an error message.
    get_modules(self):
        Retrieves all modules from the database. Uses a cache to store modules for up to one week.
        Returns a JSON response with the list of modules or an error message.
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

    def get_module_by_id(self):
        """Retrieves a module by its ID."""
        module = database.modules_collection.find_one(
            {"module_id": request.form.get("module_id")}
        )

        if module:
            return jsonify(module), 200

        return jsonify({"error": "module not found"}), 404

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
            return jsonify(modules_cache["data"]), 200

        # Fetch modules from the database
        modules = list(database.modules_collection.find())

        if modules:
            # Update cache
            modules_cache["data"] = modules
            modules_cache["last_updated"] = current_time
            return jsonify(modules), 200

        return jsonify({"error": "No modules found"}), 404
