"""Test for the students route."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
import pytest
from unittest.mock import patch
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
    deadlines = DATABASE.get_all("deadline")

    DATABASE.delete_all("deadline")
    yield DATABASE
    DATABASE.delete_all("deadline")
    for deadline in deadlines:
        DATABASE.insert("deadline", deadline)

    # Cleanup code
    DATABASE.connection.close()


@pytest.fixture()
def student_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a student."""
    database.add_table("students")
    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": uuid.uuid1().hex,
        "first_name": "Dummy",
        "last_name": "Student",
        "email": "dummy@dummy.com",
    }

    database.insert("students", student)

    url = "/students/login"
    client.post(
        url,
        data={"email": "dummy@dummy.com"},
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
