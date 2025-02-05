"""Tests for the user routes."""

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

    return app.test_client()


@pytest.fixture()
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    # Cleanup code
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
    )

    yield client

    # Cleanup code
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_upload_student_page(user_logged_in_client):
    """Test upload student page."""
    url = "/students/upload"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_add_employer_page(user_logged_in_client):
    """Test add employer page."""
    url = "/employers/add_employer"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_change_deadline_page(user_logged_in_client):
    """Test change deadline page."""
    url = "/user/deadline"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_search_student_page(user_logged_in_client):
    """Test search student page."""
    url = "/students/search"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_add_skill_page(user_logged_in_client):
    """Test add skill page."""
    url = "/skills/add_skill"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_add_course_module_page(user_logged_in_client):
    """Test add course module page."""
    url = "/course_modules/add_module"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_add_course_page(user_logged_in_client):
    """Test add course page."""
    url = "/courses/add_course"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_register_page(client):
    """Test register page."""
    url = "/user/register"

    response = client.get(url)
    assert response.status_code == 200


def test_register_user(client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    response = client.post(
        url,
        data={
            "name": "dummy",
            "email": "dummy@dummy.com",
            "password": "dummy",
            "confirm_password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    assert database.get_by_email("users", "dummy@dummy.com") is not None
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_user_password_mismatch(client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    response = client.post(
        url,
        data={
            "name": "dummy",
            "email": "dummy@dummy.com",
            "password": "dummy",
            "confirm_password": "jsdkcjnjkd",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400
    assert database.get_by_email("users", "dummy@dummy.com") is None
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_email_already_in_use(client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }

    database.insert("users", user)

    response = client.post(
        url,
        data={
            "name": "dummy2",
            "email": "dummy@dummy.com",
            "password": "dummy2",
            "confirm_password": "dummy2",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
