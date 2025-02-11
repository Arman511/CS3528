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
    
             
def test_add_student_no_id(app, database):
    
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    student = {
        "_id": "123",
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }
    

    database.insert("students", student)  
        
    with app.app_context():
        with app.test_request_context():
            response = Student().add_student(student)
            json_response = response[0].get_json()
            assert response[1] == 400
            assert json_response["error"] == "Student already in database"
             
    

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


def test_get_student_by_id_not_found(app, database):

    from students.models import Student

    assert Student().get_student_by_id("999") == None

    database.delete_all_by_field("students", "_id", "999")


def test_get_all_students(app, database):

    from students.models import Student

    count = len(database.get_all("students"))

    actual = len(Student().get_students())

    assert count == actual
  
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")


def test_get_all_students_empty(app, database):

    from students.models import Student

    current_students = database.get_all("students")
    database.delete_all("students")

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    result = Student().get_students()

    assert result == []

    for student in current_students:
        database.insert("students", student)

def test_get_student_map(app, database):  
    
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
        "student_id": "123",
    }
    
    database.insert("students", student2)
    
    student_map = Student().get_students_map()
    assert student_map["123"] == student1
    assert student_map["124"] == student2
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "124")
    
    
def test_get_student_map_empty(app, database):  
    
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    student_map = Student().get_students_map()
    assert student_map == {}
        
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
def test_get_student_by_uuid(app, database):
    
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
    
    assert Student().get_student_by_uuid("123") == student1
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")

    

def test_get_student_by_uuid_not_found(app, database):
    
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    assert Student().get_student_by_uuid("999") == None
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "999")



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

def test_update_student_by_uuid_success(app, database):
    
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
        response = Student().update_student_by_uuid("123", UpdateStudent)
        json_response = response[0].get_json()
        assert response[1] == 200
        assert json_response["message"] == "Student updated"
        
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "124")
    database.delete_all_by_field("students", "email", "updated_dummy@dummy.com")

def test_update_student_by_uuid_not_found(app, database):
    
        
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    UpdateStudent = {
        "first_name": "updated_dummy",
        "last_name": "updated_dummy",
        "email": "updated_dummy@dummy.com",
        "student_id": "124",
    }
    
    with app.app_context():
        response = Student().update_student_by_uuid("123", UpdateStudent)
        json_response = response[0].get_json()
        assert response[1] == 404
        assert json_response["error"] == "Student not found"
        
    
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "124")
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
    
def test_delete_student_by_Id_opportunities(app, database):
    
    from students.models import Student
    from unittest.mock import patch

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("modules", "module_id", "123")
    database.delete_all_by_field("modules", "module_id", "124")
    
    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
    }

    database.insert("students", student1)
                                 
    opportunity1 = {
        "_id": "123",
        "title": "dummy1",
        "description": "dummy1",
        "modules_required": ["123"],
        "courses_required": ["123"],
        "duration": "1_day",
    }
    database.insert("opportunities", opportunity1)

    opportunity2 = {
        "_id": "124",
        "title": "dummy2",
        "description": "dummy2",
        "modules_required": ["123", "124"],
        "courses_required": ["123"],
        "duration": "1_week",
    }
    database.insert("opportunities", opportunity2)
    
 
    with patch('app.DATABASE_MANAGER.update_one_by_id') as mock_update:
        with app.app_context():
            response = Student().delete_student_by_id("123")
            json_response = response[0].get_json()
            assert response[1] == 200
            assert json_response["message"] == "Student deleted"
            
            
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")        
    database.delete_all_by_field("opportunities", "title", "dummy1")
    database.delete_all_by_field("opportunities", "title", "dummy1")
    

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
    current_students = database.get_all("students")

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
        assert len(database.get_all("students")) == 0

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("students", "_id", "124")

    for student in current_students:
        database.insert("students", student)


def test_get_student_by_email(app, database):
    """Test getting a student by email."""
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


def test_import_from_xlsx_valid(app, database):
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    with app.app_context():
        with app.test_request_context():
            with open("tests/data/valid_students.xlsx", "rb") as f:
                response = Student().import_from_xlsx("dummy.com", f)
                json_response = response[0].get_json()
                assert response[1] == 200
                assert json_response["message"] == "27 students imported"

        students = database.get_all_by_field("students", "email", "dummy@dummy.com")
        assert len(students) == 27

    database.delete_all_by_field("students", "email", "dummy@dummy.com")


def test_import_from_xlsx_invalid_email(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    with app.app_context():
        with open("tests/data/Invalid_students_email.xlsx", "rb") as f:
            response = Student().import_from_xlsx("dummy.com", f)
            json_response = response[0].get_json()
            assert json_response["error"] == "Invalid student dummy1, dummy1"
            assert response[1] == 400

        students = database.get_all_by_field("students", "email", "dummy@dummy.com")
        assert len(students) == 0

    database.delete_all_by_field("students", "email", "dummy@dummy.com")


def test_import_from_xlsx_invalid_student_id(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    with app.app_context():
        with open("tests/data/Invalid_students_Id.xlsx", "rb") as f:
            response = Student().import_from_xlsx("dummy.com", f)
            json_response = response[0].get_json()
            assert json_response["error"] == "Invalid student dummy1, dummy1"
            assert response[1] == 400

        students = database.get_all_by_field("students", "email", "dummy@dummy.com")
        assert len(students) == 0

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
def test_import_from_wrong_format(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    with app.app_context():
        with open("tests/data/Invalid_doc_type.docx", "rb") as f:
            with pytest.raises(ValueError, match="Invalid file format. Please provide a valid Excel file."):
                response = Student().import_from_xlsx("dummy.com", f)
                
    assert response.status_code == 400
    students = database.get_all_by_field("students", "email", "dummy@dummy.com")
    assert len(students) == 0

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    
    
    
    

def test_student_login(app, database):

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
        with app.test_request_context():
            response = Student().student_login(student1["student_id"], student1["_id"])
            json_response = response[0].get_json()
            assert response[1] == 200
            assert json_response["message"] == "Login successful"

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("students", "_id", "123")


def test_student_login_invalid(app, database):

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
        with app.test_request_context():
            response = Student().student_login(student1["student_id"], "124")
            json_response = response[0].get_json()
            assert response[1] == 401
            assert json_response["error"] == "Invalid id or password"


def test_rank_preferences(app, database):
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
        with app.test_request_context():
            response = Student().rank_preferences(
                student1["student_id"], ["1", "2", "3"]
            )
            json_response = response[0].get_json()
            assert response[1] == 200
            assert json_response["message"] == "Preferences updated"


def test_rank_preferences_invalid_student(app, database):

    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    with app.app_context():
        with app.test_request_context():
            response = Student().rank_preferences(["student_id"], ["1", "2", "3"])
            json_response = response[0].get_json()
            assert json_response["error"] == "Student not found"
            assert response[1] == 404

def test_get_opportunities_by_student(app, database):
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("modules", "module_id", "123")
    database.delete_all_by_field("modules", "module_id", "124")
    database.delete_all_by_field("courses", "course_id", "123")
    database.delete_all_by_field("opportunities", "title", "dummy1")
    database.delete_all_by_field("opportunities", "title", "dummy2")
    database.delete_all_by_field("opportunities", "title", "dummy3")

    module1 = {
        "_id": "123",
        "module_id": "123",
        "module_name": "dummy1",
        "module_description": "dummy1",
    }
    database.insert("modules", module1)
    module2 = {
        "_id": "124",
        "module_id": "124",
        "module_name": "dummy2",
        "module_description": "dummy2",
    }
    database.insert("modules", module2)

    course = {
        "_id": "123",
        "course_id": "123",
        "course_name": "dummy1",
        "course_description": "dummy1",
    }
    database.insert("courses", course)

    opportunity1 = {
        "_id": "123",
        "title": "dummy1",
        "description": "dummy1",
        "modules_required": ["123"],
        "courses_required": ["123"],
        "duration": "1_day",
    }
    database.insert("opportunities", opportunity1)

    opportunity2 = {
        "_id": "124",
        "title": "dummy2",
        "description": "dummy2",
        "modules_required": ["123", "124"],
        "courses_required": ["123"],
        "duration": "1_week",
    }
    database.insert("opportunities", opportunity2)

    opportunity3 = {
        "_id": "125",
        "title": "dummy3",
        "description": "dummy3",
        "modules_required": ["123", "124"],
        "courses_required": ["123"],
        "duration": "1_month",
    }

    student1 = {
        "_id": "123",
        "first_name": "dummy1",
        "last_name": "dummy1",
        "email": "dummy@dummy.com",
        "student_id": "123",
        "modules": ["123", "124"],
        "course": "123",
        "placement_duration": ["1_day", "1_week"],
    }

    database.insert("students", student1)

    with app.app_context():
        with app.test_request_context():
            response = Student().get_opportunities_by_student(student1["student_id"])
            assert len(response) == 2

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("modules", "module_id", "123")
    database.delete_all_by_field("modules", "module_id", "124")
    database.delete_all_by_field("courses", "course_id", "123")
    database.delete_all_by_field("opportunities", "title", "dummy1")
    database.delete_all_by_field("opportunities", "title", "dummy2")
    database.delete_all_by_field("opportunities", "title", "dummy3")


def test_get_opportunities_by_student_invalid(app, database):
    from students.models import Student

    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    with app.app_context():
        with app.test_request_context():
            response = Student().get_opportunities_by_student(["student_id"])
            json_response = response[0].get_json()
            assert json_response["error"] == "Student not found"
            assert response[1] == 404
