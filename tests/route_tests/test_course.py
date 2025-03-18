"""Tests for the course routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid
from passlib.hash import pbkdf2_sha512
import pytest
from dotenv import load_dotenv

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core import shared
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

    database = DatabaseMongoManager(
        shared.getenv("MONGO_URI"), shared.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield database

    # Cleanup code
    database.delete_all_by_field("courses", "course_id", "CS101")
    database.delete_all_by_field("courses", "course_id", "CS102")

    database.connection.close()


@pytest.fixture()
def user_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a user."""
    database.add_table("users")
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
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


def test_add_course_get(user_logged_in_client):
    """Test GET request to add course route."""
    response = user_logged_in_client.get("/courses/add_course")
    assert response.status_code == 200


def test_add_course_post(user_logged_in_client, database):
    """Test POST request to add course route."""
    course_data = {
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    response = user_logged_in_client.post(
        "/courses/add_course",
        data=course_data,
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    course = database.get_one_by_field("courses", "course_id", "CS101")
    assert course is not None
    assert course["course_name"] == "Introduction to Computer Science"

    database.delete_all_by_field("courses", "course_id", "CS101")


def test_delete_course(user_logged_in_client, database):
    """Test POST request to delete course route."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    course = {
        "_id": uuid.uuid4().hex,
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    database.insert("courses", course)
    url = f"/courses/delete?uuid={course['_id']}"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 200
    deleted_course = database.get_one_by_id("courses", course["_id"])
    assert deleted_course is None

    database.delete_all_by_field("courses", "course_id", "CS101")


def test_search_course(user_logged_in_client, database):
    """Test GET request to search course route."""
    course = {
        "_id": uuid.uuid4().hex,
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    database.insert("courses", course)

    # Ensure the course is in the database
    assert database.get_one_by_id("courses", course["_id"]) is not None

    response = user_logged_in_client.get("/courses/search")
    assert response.status_code == 200

    database.delete_all_by_field("courses", "course_id", "CS101")


def test_update_course_get(user_logged_in_client, database):
    """Test GET request to update course route."""
    course = {
        "_id": uuid.uuid4().hex,
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    database.insert("courses", course)
    response = user_logged_in_client.get(f"/courses/update?uuid={course['_id']}")
    assert response.status_code == 200

    database.delete_all_by_field("courses", "course_id", "CS101")


def test_update_course_post(user_logged_in_client, database):
    """Test POST request to update course route."""
    course = {
        "_id": uuid.uuid4().hex,
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    database.insert("courses", course)
    updated_course_data = {
        "course_id": "CS102",
        "course_name": "Advanced Computer Science",
        "course_description": "Advanced concepts of computer science.",
    }
    response = user_logged_in_client.post(
        f"/courses/update?uuid={course['_id']}",
        data=updated_course_data,
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    updated_course = database.get_one_by_id("courses", course["_id"])
    assert updated_course["course_id"] == "CS102"
    assert updated_course["course_name"] == "Advanced Computer Science"
    database.delete_by_id("courses", course["_id"])
