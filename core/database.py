"""
Handles connection to the MongoDB database and provides access to the collections.
"""

import datetime
import os
import sys
from flask import jsonify
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
deadline_collection = database["deadline"]


def get_details_deadline():
    """Get the deadline from the database."""
    find_deadline = deadline_collection.find_one({"type": 0})
    if not find_deadline:
        deadline = datetime.datetime.now().strftime("%Y-%m-%d")
        deadline_collection.insert_one({"type": 0, "deadline": deadline})
    else:
        deadline = find_deadline["deadline"]
    return deadline


def update_details_deadline(deadline):
    """Update the deadline in the database."""
    try:
        datetime.datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid deadline format. Use YYYY-MM-DD."}), 400

    if deadline > get_ranking_deadline():
        return (
            jsonify(
                {"error": "Ranking deadline cannot be earlier than details deadline."}
            ),
            400,
        )

    deadline_collection.update_one({}, {"$set": {"deadline": deadline}}, upsert=True)
    return jsonify({"message": "Deadline updated successfully"}), 200


def is_past_details_deadline():
    """Check if the deadline has passed."""
    deadline = get_details_deadline()
    return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline


def get_ranking_deadline():
    """Get the deadline from the database."""
    find_deadline = deadline_collection.find_one({"type": 1})
    if not find_deadline:
        deadline = (
            datetime.datetime.strptime(get_details_deadline(), "%Y-%m-%d")
            + datetime.timedelta(weeks=1)
        ).strftime("%Y-%m-%d")
        deadline_collection.insert_one({"type": 1, "deadline": deadline})
    else:
        deadline = find_deadline["deadline"]
    return deadline


def update_ranking_deadline(deadline):
    """Update the deadline in the database."""
    try:
        datetime.datetime.strptime(deadline, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid deadline format. Use YYYY-MM-DD."}), 400

    if deadline < get_details_deadline():
        return (
            jsonify(
                {"error": "Ranking deadline cannot be earlier than details deadline."}
            ),
            400,
        )

    deadline_collection.update_one({}, {"$set": {"deadline": deadline}}, upsert=True)
    return jsonify({"message": "Deadline updated successfully"}), 200


def is_past_ranking_deadline():
    """Check if the deadline has passed."""
    deadline = get_ranking_deadline()
    return datetime.datetime.now().strftime("%Y-%m-%d") >= deadline
