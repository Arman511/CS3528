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

    result = database.delete_all_by_field("students", "email", "dummy@dummy.com")

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
    database.delete_all_by_field("students", "_id", "123")


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
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "124")


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
    database.delete_all_by_field("students", "_id", "123")


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

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")


# def test_get_student_by_id_not_found(app, database):


def test_get_all_students(app, database):

    from students.models import Student

    count = len(database.get_all("students"))

    actual = len(Student().get_students())

    assert count == actual

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")


# def test_get_all_students_empty(app, database):


def test_update_student_by_id_success(app, database):

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

    UpdateStudent = {
        "first_name": "updated_dummy",
        "last_name": "updated_dummy",
        "email": "updated_dummy@dummy.com",
        "student_id": "124",
    }

    with app.app_context():
        response = Student().update_student_by_id("123", UpdateStudent)
        json_response = response[0].get_json()
        assert response[1] == 200
        assert json_response["message"] == "Student updated"

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "email", "updated_dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")


def test_update_student_by_id_not_found(app, database):
    """Test updating a student by id that does not exist."""
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    UpdateStudent = {
        "first_name": "updated_dummy",
        "last_name": "updated_dummy",
        "email": "updated_dummy@dummy.com",
        "student_id": "124",
    }

    with app.app_context():
        response = Student().update_student_by_id("999", UpdateStudent)
        json_response = response[0].get_json()
        assert response[1] == 404
        assert json_response["error"] == "Student not found"

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "999")
    database.delete_all_by_field("students", "email", "updated_dummy@dummy.com")


def test_delete_student_by_id(app, database):

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
    
    with app.app_context():
        response = Student().delete_student_by_id("123")
        json_response = response[0].get_json()
        assert response[1] == 200
        assert json_response["message"] == "Student deleted"
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")

def test_delete_student_by_id_not_found(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    with app.app_context():
        response = Student().delete_student_by_id("123")
        json_response = response[0].get_json()
        assert response[1] == 404
        assert json_response["error"] == "Student not found"
        
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")    

def test_delete_students(app, database):

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
    
    student2 = {
        "_id": "124",
        "first_name": "dummy2",
        "last_name": "dummy2",
        "email": "dummy2@dummy.com",
        "student_id": "124",
    }
    
    database.insert("students", student2)
    
    with app.app_context():
        response = Student().delete_students()
        json_response = response[0].get_json()
        assert response[1] == 200
        assert json_response["message"] == "All students deleted"
        
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")

def test_get_student_by_email(app, database):

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
    
    with app.app_context():
        response = Student().get_student_by_email("dummy@dummy.com")
        assert response[1] == 200
       
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    
    
def test_get_student_by_email_not_found(app, database):
    from students.models import Student
    
    with app.app_context():
        response = Student().get_student_by_email("dummy@dummy.com")
        json_response = response[0].get_json()
        assert response[1] == 404
        assert json_response["error"] == "Student not found"

def test_import_from_xlsx(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    mock_df = ({"_id": ["123", "124"], "first_name": ["dummy1", "dummy2"], "last_name": ["dummy1", "dummy2"], "email": ["dummy@dummy.com","dummy2@dummy.com"], "student_id": ["123", "124"]})
    
    mock_read_excel.return_value = mock_df
    
    #with app.app_context():
        

    pass


def test_student_login(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email","dummy@dummy.com")

    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
        "password": pbkdf2_sha256.hash("password")
    }

    database.insert("students", student1)
    
    with app.app_context():
        response = Student().student_login(student1["student_id"],password")
        json_response = response[0].get_json()  
        
        
        assert response[1] == 200
        assert json_response["message"] == "Login successful"
        
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
            
def test_rank_preferences(app, database):

    pass


def test_get_oppertunities_by_student(app, database):

    pass
