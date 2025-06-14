"""Module for managing MongoDB database operations."""

import sys
from dotenv import load_dotenv
import pymongo
from pymongo.errors import (
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
)
from colorama import Fore, Style

from core import shared
from .database_interface import DatabaseInterface


class DatabaseMongoManager(DatabaseInterface):
    """Class to manage MongoDB database operations."""

    def __init__(self, connection, database):
        """Initialize the DatabaseMongoManager class."""
        super().__init__()

        self.connect(connection, database)

    def connect(self, connection, database):
        """Connect to the MongoDB database."""
        load_dotenv()
        self.connection = pymongo.MongoClient(serverSelectionTimeoutMS=5000)
        if (
            shared.getenv("IS_GITHUB_ACTION") == "False"
            and connection is not None
            and shared.getenv("OFFLINE") != "True"
        ):
            self.connection = pymongo.MongoClient(
                connection, serverSelectionTimeoutMS=5000
            )

        try:
            self.connection.admin.command("ping")
            print(
                Fore.GREEN
                + "Pinged your deployment. You successfully connected to MongoDB!"
                + Style.RESET_ALL
            )
        except ConfigurationError as e:
            print(Fore.RED + f"Configuration error: {e}" + Style.RESET_ALL)
            sys.exit(1)
        except OperationFailure as e:
            print(Fore.RED + f"Operation failure: {e}" + Style.RESET_ALL)
            sys.exit(1)
        except ServerSelectionTimeoutError as e:
            print(Fore.RED + f"Server selection timeout error: {e}" + Style.RESET_ALL)
            sys.exit(1)
        if database == "":
            database = "cs3528_testing"
        self.database = self.connection[database]

    def get_all(self, table):
        """Get all records from a table."""
        return list(self.database[table].find())

    def get_one_by_id(self, table, id_val):
        """Get one record by ID."""
        return self.database[table].find_one({"_id": id_val})

    def insert(self, table, data):
        """Insert a record into a table."""
        return self.database[table].insert_one(data)

    def update_one_by_id(self, table, id_val, data):
        """Update a record
        Args:
            table: The table to update
            id_val: The ID of the record to update
            data: The data to update
        """
        return self.database[table].update_one({"_id": id_val}, {"$set": data})

    def update_one_by_field(self, table, field, value, data):
        """Update a record by field.
        Args:
            table: The table to update
            field: The field to search
            value: The value to search
            data: The data to update
        """
        return self.database[table].update_one({field: value}, {"$set": data})

    def increment(self, table, id_val, field, increment):
        """Increment a field by a value.
        Args:
            table: The table to update
            id_val: The ID of the record to update
            field: The field to increment
            increment: The value to increment by
        """
        return self.database[table].update_one(
            {"_id": id_val}, {"$inc": {field: increment}}
        )

    def delete_by_id(self, table, id_val):
        """Delete a record by ID.
        Args:
            table: The table to delete from
            id_val: The ID of the record to delete
        """
        return self.database[table].delete_one({"_id": id_val})

    def delete_one_by_field(self, table, field, value):
        """Delete a record by field.
        Args:
            table: The table to delete from
            field: The field to search
            value: The value to search
        """
        return self.database[table].delete_one({field: value})

    def delete_all_by_field(self, table, field, value):
        """Delete all records by field.
        Args:
            table: The table to delete from
            field: The field to search
            value: The value to search
        """
        return self.database[table].delete_many({field: value})

    def delete_all(self, table):
        """Delete all records from a table.
        Args:
            table: The table to delete from
        """
        return self.database[table].delete_many({})

    def get_by_email(self, table, email):
        """Get a record by email.
        Args:
            table: The table to search
            email: The email to search
        """
        return self.database[table].find_one({"email": email})

    def delete_field_by_id(self, table, id_val, field):
        """Delete a field by ID.
        Args:
            table: The table to update
            id_val: The ID of the record to update
            field: The field to delete
        """
        return self.database[table].update_one({"_id": id_val}, {"$unset": {field: ""}})

    def get_one_by_field(self, table, field, value):
        """Get one record by field."""
        return self.database[table].find_one({field: value})

    def get_one_by_field_strict(self, table, field, value):
        """Get one record by field with strict matching."""
        return self.database[table].find_one(
            {field: {"$regex": f"^{value}$", "$options": "i"}}
        )

    def is_table(self, table):
        """Check if a table exists."""
        return table in self.table_list

    def get_all_by_two_fields(self, table, field1, value1, field2, value2):
        """Get all records by two fields."""
        return list(self.database[table].find({field1: value1, field2: value2}))

    def get_all_by_in_list(self, table, field, values_list):
        """Get all records by a list of values."""
        return list(self.database[table].find({field: {"$in": values_list}}))

    def update_by_field(self, table, field, value, data):
        """Update a record by field."""
        return self.database[table].update_one({field: value}, {"$set": data})

    def get_all_by_field(self, table, field, value):
        """Get all records by field."""
        return list(self.database[table].find({field: value}))

    def create_index(self, table, field):
        """Create an index on a field."""
        return self.database[table].create_index(field)

    def get_all_by_text_search(self, table, search_text):
        """Get all records by text search."""
        return list(self.database[table].find({"$text": {"$search": search_text}}))

    def close_connection(self):
        """Close the connection to the database."""
        self.connection.close()

    def delete_collection(self, table):
        """Delete a collection."""
        return self.database[table].drop()

    def insert_many(self, table, data):
        """Insert many records into a table."""
        return self.database[table].insert_many(data)
