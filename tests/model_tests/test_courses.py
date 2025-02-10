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
from datetime import datetime, timedelta
import uuid

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

    yield DATABASE

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
    with app.app_context():
        with app.test_request_context():
            course_model.add_course(sample_course)
            course_id = sample_course["_id"]
            response = course_model.delete_course_by_uuid(course_id)
            assert response[1] == 200
            assert database.get_one_by_id("courses", course_id) is None
    database.delete_all_by_field("courses", "course_id", "CS101")


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
