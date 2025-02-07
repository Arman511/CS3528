"""Tests for the student model."""

import os
import sys

from dotenv import load_dotenv
import pytest
from passlib.hash import pbkdf2_sha256

from flask import session


# flake8: noqa: F811

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def app():
    """Fixture to create a test client."""
    from ...app import app  # pylint: disable=import-outside-toplevel

    return app


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


def test_add_student_success(app, database):
    """Test adding a student successfully."""
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": "123",
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }

    with app.app_context():
        with app.test_request_context():
            response = Student().add_student(student)
            json_response = response[0].get_json()
            assert response[1] == 200
            assert json_response["_id"] == student["_id"]
            assert json_response["first_name"] == student["first_name"]
            assert json_response["last_name"] == student["last_name"]
            assert json_response["email"] == student["email"]
            assert json_response["student_id"] == student["student_id"]

    database.delete_all_by_field("students", "email", "dummy@dummy.com")


def test_add_student_duplicate(app, database):
    """Test adding a student with a id."""
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }

    database.insert("students", student1)

    student1 = {
        "_id": "124",
        "first_name": "dummy2",
        "last_name": "dummy2",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }

    with app.app_context():
        with app.test_request_context():
            response = Student().add_student(student1)
            json_response = response[0].get_json()
            assert response[1] == 400
            assert json_response["error"] == "Student already in database"
            assert database.get_one_by_id("students", "123")["first_name"] == "dummy1"
            assert (
                len(database.get_all_by_field("students", "email", "dummy@dummy.com"))
                == 1
            )

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

def test_add_student_duplicate_override(app, database):
    """Test adding a student with a id."""
    from students.models import Student
    

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }
    
    database.insert("students", student1)
    
    student1 = {
        "_id": "124",
        "first_name": "dummy2",
        "last_name": "dummy2",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }
    
    with app.app_context():
        with app.test_request_context():
            response = Student().add_student(student1, overwrite=True)
            json_response = response[0].get_json()
            assert response[1] == 200
            assert database.get_one_by_id("students", "124")["first_name"] == "dummy2"
            assert (
                len(database.get_all_by_field("students", "email", "dummy@dummy.com"))
                == 1
            )

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

def test_get_student_by_id(app, database):
    """Test getting a student by id."""
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }
    
    database.insert("students", student1)
    
    assert Student().get_student_by_id("123") == student1
   
        
    
    