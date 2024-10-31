"""
Handles connection to the MongoDB database and provides access to the collections.
"""

import os
import sys
import pymongo
from dotenv import load_dotenv

load_dotenv()
client: pymongo.MongoClient = pymongo.MongoClient()

if os.getenv("IS_GITHUB_ACTIONS") == "False":
    client = pymongo.MongoClient(os.getenv(("DB_LOGIN")))

try:
    client.admin.command("ping")
    print("Pinged your deployment. You successfully connected to MongoDB!")
except pymongo.errors.ConfigurationError as e:
    print(f"Configuration error: {e}")
    sys.exit(1)
except pymongo.errors.OperationFailure as e:
    print(f"Operation failure: {e}")
    sys.exit(1)
except pymongo.errors.ServerSelectionTimeoutError as e:
    print(f"Server selection timeout error: {e}")
    sys.exit(1)

database = client["cs3028_db"]
users_collection = database["users"]
students_collection = database["students"]
opportunities_collection = database["opportunities"]
courses_collection = database["courses"]
skills_collection = database["skills"]
attempted_skills_collection = database["attempted_skills"]
modules_collection = database["modules"]
employers_collection = database["employers"]
