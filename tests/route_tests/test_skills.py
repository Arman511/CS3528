"""Tests for the skills routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from passlib.hash import pbkdf2_sha256
import pytest
from dotenv import load_dotenv

from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def client():
    """Fixture to create a test client."""
    from ...app import app  # pylint: disable=import-outside-toplevel

    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture()
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    # Cleanup code
    DATABASE.delete_all_by_field("courses", "course_id", "CS101")
    DATABASE.delete_all_by_field("courses", "course_id", "CS102")

    DATABASE.connection.close()


@pytest.fixture()
def user_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a user."""
    database.add_table("users")
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }

    database.insert("users", user)

    url = "/user/login"
    client.post(
        url,
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    # Cleanup code
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
