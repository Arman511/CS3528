"""Tests for the course modules routes."""

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

from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def client():
    """Fixture to create a test client."""
    from ...app import app

    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    modules = DATABASE.get_all("modules")
    DATABASE.delete_all("modules")
    yield DATABASE
    DATABASE.delete_all("modules")
    if modules:
        DATABASE.insert_many("modules", modules)

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


@pytest.fixture()
def sample_module(database):
    """Fixture to create a sample module."""
    yield {
        "_id": "123",
        "module_id": "CS101",
        "module_name": "Intro to CS",
        "module_description": "Basic programming concepts",
    }
    database.delete_all_by_field("modules", "module_id", "CS101")


def test_add_module(user_logged_in_client, database, sample_module):
    """Test adding a module."""
    url = "/course_modules/add_module"
    response = user_logged_in_client.post(
        url,
        data={
            "module_id": sample_module["module_id"],
            "module_name": sample_module["module_name"],
            "module_description": sample_module["module_description"],
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    assert database.get_one_by_field("modules", "module_id", "CS101") is not None


def test_search_modules(user_logged_in_client, database, sample_module):
    """Test searching modules."""
    database.insert("modules", sample_module)
    url = "/course_modules/search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_delete_module(user_logged_in_client, database, sample_module):
    """Test deleting a module."""
    database.insert("modules", sample_module)
    url = f"/course_modules/delete?uuid={sample_module['_id']}"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 200
    assert database.get_one_by_id("modules", sample_module["_id"]) is None


def test_update_module(user_logged_in_client, database, sample_module):
    """Test updating a module."""
    database.insert("modules", sample_module)
    url = f"/course_modules/update?uuid={sample_module['_id']}"
    response = user_logged_in_client.post(
        url,
        data={
            "module_id": "CS102",
            "module_name": "Intro to Programming",
            "module_description": "Updated description",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    updated_module = database.get_one_by_id("modules", sample_module["_id"])
    assert updated_module["module_id"] == "CS102"
    assert updated_module["module_name"] == "Intro to Programming"


def test_upload_invalid_file(user_logged_in_client):
    """Test uploading an invalid file type."""
    url = "/course_modules/upload"
    file_path = "tests/data/invalid_course_modules.txt"

    with open(file_path, "rb") as file:
        response = user_logged_in_client.post(
            url,
            data={"file": (file, "invalid_course_modules.txt")},
            content_type="multipart/form-data",
        )

    assert response.status_code == 400
    assert response.json["error"] == "Invalid file type"


def test_download_template(user_logged_in_client):
    """Test downloading the course module template."""
    url = "/course_modules/download_template"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_delete_all_modules(user_logged_in_client, database, sample_module):
    """Test deleting all modules."""
    database.insert("modules", sample_module)
    students = database.get_all("students")
    opportunities = database.get_all("opportunities")
    url = "/course_modules/delete_all"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 200
    assert len(database.get_all("modules")) == 0

    # Restore the students and opportunities
    database.delete_all("students")
    if students:
        database.insert_many("students", students)

    database.delete_all("opportunities")
    if opportunities:
        database.insert_many("opportunities", opportunities)


def test_download_all_modules(user_logged_in_client, database, sample_module):
    """Test downloading all modules."""
    database.insert("modules", sample_module)
    url = "/course_modules/download_all"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200
