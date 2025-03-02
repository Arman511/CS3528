"""Tests for the user routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid
import pytest
from dotenv import load_dotenv
from flask import Flask, send_file
from io import BytesIO
import pandas as pd


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
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    courses = DATABASE.get_all("courses")
    DATABASE.delete_all("courses")
    yield DATABASE

    for course in courses:
        DATABASE.insert("courses", course)
    DATABASE.delete_all_by_field("users", "email", "dummy@dummy.com")
    DATABASE.delete_all_by_field("courses", "course_id", "CS101")
    # Cleanup code
    DATABASE.connection.close()


@pytest.fixture()
def course_model():
    """Fixture to create a Course model instance."""
    from courses.models import Course

    return Course()


@pytest.fixture()
def sample_course(database):
    """Fixture to create a sample course."""
    yield {
        "_id": uuid.uuid4().hex,
        "course_id": "CS101",
        "course_name": "Introduction to Computer Science",
        "course_description": "Basic concepts of computer science.",
    }
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_add_course(database, course_model, sample_course, app):
    """Test adding a course."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            response = course_model.add_course(sample_course)
            assert response[1] == 200
    assert database.get_one_by_field("courses", "course_id", "CS101") is not None
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_add_existing_course(database, course_model, sample_course, app):
    """Test adding an existing course."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            response = course_model.add_course(sample_course)
            assert response[1] == 400
            assert response[0].json["error"] == "Course already in database"
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_delete_course(database, course_model, sample_course, app):
    """Test deleting a course."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    database.delete_all_by_field(
        "students", "course", "CS101"
    )  # Ensure no students are linked
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            course_id = sample_course["_id"]

            # Ensure the course exists before deletion
            assert database.get_one_by_field(
                "courses", "course_id", "CS101"
            ), "Course was not added"

            response = course_model.delete_course_by_uuid(course_id)

            # Ensure course is deleted
            assert response[1] == 200, f"Unexpected response: {response[0].json}"
            assert (
                database.get_one_by_id("courses", course_id) is None
            ), "Course still exists after deletion"


def test_delete_nonexistent_course(course_model, app):
    """Test deleting a nonexistent course."""
    with app.app_context():
        with app.test_request_context():
            response = course_model.delete_course_by_uuid("nonexistent_id")
            assert response[1] == 404
            assert response[0].json["error"] == "Course not found"


def test_get_course_by_id(database, course_model, sample_course, app):
    """Test getting a course by ID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            course = course_model.get_course_by_id("CS101")
            assert course is not None
            assert course["course_id"] == "CS101"
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_course_by_uuid(database, course_model, sample_course, app):
    """Test getting a course by UUID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            course = course_model.get_course_by_uuid(sample_course["_id"])
            assert course is not None
            assert course["_id"] == sample_course["_id"]
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_course_name_by_id(database, course_model, sample_course, app):
    """Test getting a course name by ID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            course_name = course_model.get_course_name_by_id("CS101")
            assert course_name == "Introduction to Computer Science"
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_courses(database, course_model, sample_course, app):
    """Test getting all courses."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            courses = course_model.get_courses()
            assert len(courses) > 0
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_courses_map(database, course_model, sample_course, app):
    """Test getting courses map."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            courses_map = course_model.get_courses_map()
            assert "CS101" in courses_map
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_update_course(database, course_model, sample_course, app):
    """Test updating a course."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            updated_course = {
                "course_id": "CS101",
                "course_name": "Intro to CS",
                "course_description": "Updated description.",
            }
            response = course_model.update_course(sample_course["_id"], updated_course)
            assert response[1] == 200
            course = course_model.get_course_by_uuid(sample_course["_id"])
            assert course["course_name"] == "Intro to CS"
            assert course["course_description"] == "Updated description."


def test_reset_cache(database, course_model, sample_course, app):
    """Test resetting the courses cache."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            result = course_model.reset_cache()
            assert len(result) > 0
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_course_by_invalid_id(database, course_model, app):
    """Test getting a course by invalid ID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course = course_model.get_course_by_id("INVALID_ID")
            assert course is None
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_course_by_invalid_uuid(database, course_model, app):
    """Test getting a course by invalid UUID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course = course_model.get_course_by_uuid("INVALID_UUID")
            assert course is None
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_get_course_name_by_invalid_id(database, course_model, app):
    """Test getting a course name by invalid ID."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            course_name = course_model.get_course_name_by_id("INVALID_ID")
            assert course_name is None
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_update_course_not_updated(database, course_model, sample_course, app):
    """Test updating a course that does not exist."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    with app.app_context():
        with app.test_request_context():
            response = course_model.update_course("nonexistent_uuid", sample_course)
            assert response[1] == 404
            assert response[0].json["error"] == "Course not found"
    database.delete_all_by_field("courses", "course_id", "CS101")


def test_update_course_students(database, course_model, sample_course, app):
    """Test updating a course and ensuring students are updated."""
    database.delete_all_by_field("courses", "course_id", "CS101")
    database.delete_all_by_field("courses", "course_id", "CS102")
    database.delete_all_by_field("students", "email", "student@dummy.com")
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            student = {
                "_id": uuid.uuid4().hex,
                "email": "student@dummy.com",
                "course": "CS101",
            }
            database.insert("students", student)
            updated_course = {
                "course_id": "CS102",
                "course_name": "Intro to CS",
                "course_description": "Updated description.",
            }
            response = course_model.update_course(sample_course["_id"], updated_course)
            assert response[1] == 200
            updated_student = database.get_one_by_field(
                "students", "email", "student@dummy.com"
            )
            assert updated_student["course"] == "CS102"
    database.delete_all_by_field("courses", "course_id", "CS101")
    database.delete_all_by_field("courses", "course_id", "CS102")
    database.delete_all_by_field("students", "email", "student@dummy.com")


def test_delete_all_courses(database, course_model, sample_course, app):
    """Test deleting all courses."""
    if database.get_one_by_field("courses", "course_id", sample_course["course_id"]):
        database.delete_all("courses")
    database.insert("courses", sample_course)
    assert (
        database.get_one_by_field("courses", "course_id", sample_course["course_id"])
        is not None
    )
    database.delete_all("students")

    with app.app_context():
        response = course_model.delete_all_courses()
        assert response[1] == 200
        assert database.get_all("courses") == []


def test_download_all_courses(database, course_model, sample_course, app):
    """Test downloading all courses."""
    database.insert("courses", sample_course)
    with app.app_context():
        with app.test_request_context():
            # Ensure the directory exists
            if os.name == "nt":
                os.makedirs("temp", exist_ok=True)
            else:
                os.makedirs("/tmp", exist_ok=True)
            response = course_model.download_all_courses()
            assert response.status_code == 200
            assert (
                response.mimetype
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


def test_upload_course_data(database, course_model, app):
    database.delete_all_by_field("courses", "course_id", "CS102")
    """Test uploading course data from an Excel file."""
    df = pd.DataFrame(
        [
            {
                "UCAS_code": "CS102",
                "Course_name": "Data Science",
                "Qualification": "BSc",
                "Course_description": "Intro to Data Science",
            }
        ]
    )
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    with app.app_context():
        response = course_model.upload_course_data(excel_buffer)
        assert response[1] == 200
        assert database.get_one_by_field("courses", "course_id", "CS102") is not None

    database.delete_all_by_field("courses", "course_id", "CS102")


def test_update_course_duplicate_id(database, course_model, sample_course, app):
    """Test updating a course to an existing course ID."""
    database.delete_all_by_field("courses", "course_id", "CS102")
    database.insert("courses", sample_course)
    second_course = {
        "_id": uuid.uuid4().hex,
        "course_id": "CS102",
        "course_name": "Advanced Programming",
        "course_description": "Advanced topics in programming",
    }
    database.insert("courses", second_course)
    updated_course = {"course_id": "CS102", "course_name": "New Name"}
    with app.app_context():
        response = course_model.update_course(sample_course["_id"], updated_course)
        assert response[1] == 400
        assert response[0].json["error"] == "Course ID already exists"

    database.delete_all_by_field("courses", "course_id", "CS102")


def test_delete_course_with_students(database, course_model, sample_course, app):
    """Test deleting a course with enrolled students."""
    database.insert("courses", sample_course)
    student = {
        "_id": uuid.uuid4().hex,
        "email": "student@example.com",
        "course": "CS101",
    }
    database.insert("students", student)
    with app.app_context():
        response = course_model.delete_course_by_uuid(sample_course["_id"])
        assert response[1] == 400
        assert response[0].json["error"] == "Course has students enrolled"
