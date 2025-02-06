
import os
import uuid
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
import pytest
from dotenv import load_dotenv

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def client():
    """Fixture to create a test client."""
    from ...app import app  # pylint: disable=import-outside-toplevel

    return app.test_client()


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    connection = MongoClient()
    if os.getenv("IS_GITHUB_ACTION") == "False":
        connection = MongoClient(os.getenv("MONGO_URI"))
    database = connection[os.getenv("MONGO_DB_TEST", "cs3528_testing")]

    return database


@pytest.fixture()
def user_logged_in_client(client, database):
    """Fixture to login a user."""
    user_collection = database["users"]
    user_collection.delete_many({"email": "dummy@dummy.com"})
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }

    user_collection.insert_one(user)

    url = "/user/login"
    client.post(
        url,
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
    )

    yield client

    # Cleanup code
    user_collection.delete_many({"email": "dummy@dummy.com"})


def test_start_session(user_logged_in_client):
    
    response = user_logged_in_client.get("/user/models")
    with user_logged_in_client.session_transaction() as session:
        assert '_id' in session['user']

