import os
import sys
from dotenv import load_dotenv
import pymongo
from .database_interface import DatabaseInterface
from pymongo.errors import (
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
)


class DatabaseMongoManager(DatabaseInterface):
    def __init__(self, connection, database):
        super().__init__()
        if connection == "":
            return

        self.connect(connection, database)

    def connect(self, connection, database):
        load_dotenv()
        self.connection = pymongo.MongoClient()
        if os.getenv("IS_GITHUB_ACTION") == "False":
            self.connection = pymongo.MongoClient(connection)

        try:
            self.connection.admin.command("ping")
            print("Pinged your deployment. You successfully connected to MongoDB!")
        except ConfigurationError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)
        except OperationFailure as e:
            print(f"Operation failure: {e}")
            sys.exit(1)
        except ServerSelectionTimeoutError as e:
            print(f"Server selection timeout error: {e}")
            sys.exit(1)
        if database == "":
            database = "cs3528_testing"
        self.database = self.connection[database]

    def get_all(self, table):
        return list(self.database[table].find())

    def get_one_by_id(self, table, id_val):
        return self.database[table].find_one({"_id": id_val})

    def insert(self, table, data):
        return self.database[table].insert_one(data)

    def update_one_by_id(self, table, id_val, data):
        return self.database[table].update_one({"_id": id_val}, {"$set": data})

    def update_one_by_field(self, table, field, value, data):
        return self.database[table].update_one({field: value}, {"$set": data})

    def increment(self, table, id_val, field, increment):
        return self.database[table].update_one(
            {"_id": id_val}, {"$inc": {field: increment}}
        )

    def delete_by_id(self, table, id_val):
        return self.database[table].delete_one({"_id": id_val})

    def delete_one_by_field(self, table, field, value):
        return self.database[table].delete_one({field: value})

    def delete_all_by_field(self, table, field, value):
        return self.database[table].delete_many({field: value})

    def delete_all(self, table):
        return self.database[table].delete_many({})

    def get_by_email(self, table, email):
        return self.database[table].find_one({"email": email})

    def get_one_by_field(self, table, field, value):
        return self.database[table].find_one({field: value})

    def get_one_by_field_strict(self, table, field, value):
        return self.database[table].find_one(
            {field: {"$regex": f"^{value}$", "$options": "i"}}
        )

    def get_many_by_field(self, table, field, value):
        return list(self.database[table].find({field: value}))

    def is_table(self, table):
        return table in self.table_list

    def get_all_by_two_fields(self, table, field1, value1, field2, value2):
        return list(self.database[table].find({field1: value1, field2: value2}))

    def get_all_by_in_list(self, table, field, values_list):
        return list(self.database[table].find({field: {"$in": values_list}}))

    def update_by_field(self, table, field, value, data):
        return self.database[table].update_one({field: value}, {"$set": data})

    def get_all_by_field(self, table, field, value):
        return list(self.database[table].find({field: value}))

    def create_index(self, table, field):
        return self.database[table].create_index(field)

    def get_all_by_list_query(self, table, query):
        mongo_query = {}
        for field, value, match_type in query:
            if match_type == 0:
                mongo_query[field] = value
            elif match_type == 1:
                mongo_query[field] = {"$in": value}
        return list(self.database[table].find(mongo_query))

    def get_all_by_text_search(self, table, search_text):
        return list(self.database[table].find({"$text": {"$search": search_text}}))

    def close_connection(self):
        self.connection.close()

    def delete_collection(self, table):
        return self.database[table].drop()
