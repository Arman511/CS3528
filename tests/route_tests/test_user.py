"""Tests for the user routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid
from unittest.mock import patch
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
    deadlines = database.get_all("deadline")
    database.delete_all("deadline")
    yield database

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)

    # Cleanup code
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


@pytest.fixture()
def superuser_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a superuser."""
    database.add_table("users")

    superuser_email = shared.getenv("SUPERUSER_EMAIL")
    superuser_password = shared.getenv("SUPERUSER_PASSWORD")

    url = "/user/login"

    client.post(
        url,
        data={
            "email": superuser_email,
            "password": superuser_password,
        },
        content_type="application/x-www-form-urlencoded",
    )

    yield client


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


def test_search_employer_page(user_logged_in_client):
    """Test search employer page."""
    url = "/employers/search"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_matching_page(user_logged_in_client):
    """Test matching page."""
    url = "/user/matching"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_problem_page(user_logged_in_client):
    """Test problem page."""
    url = "/user/problem"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_search_opportunity_page(user_logged_in_client):
    """Test search opportunity page."""
    url = "/opportunities/search"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_register_page(superuser_logged_in_client):
    """Test register page."""
    url = "/user/register"

    response = superuser_logged_in_client.get(url)
    assert response.status_code == 200


def test_register_user(superuser_logged_in_client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    response = superuser_logged_in_client.post(
        url,
        data={
            "name": "dummy",
            "email": "dummy@dummy.com",
            "password": "dummy",
            "confirm_password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 201
    assert database.get_by_email("users", "dummy@dummy.com") is not None
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_user_password_mismatch(superuser_logged_in_client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    response = superuser_logged_in_client.post(
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


def test_email_already_in_use(superuser_logged_in_client, database):
    """Test register user."""
    url = "/user/register"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    response = superuser_logged_in_client.post(
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


def test_deadline_change(user_logged_in_client, database):
    """Test deadline change."""
    url = "/user/deadline"

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    response = user_logged_in_client.post(
        url,
        data={
            "details_deadline": "2022-10-11",
            "student_ranking_deadline": "2022-10-14",
            "opportunities_ranking_deadline": "2022-10-18",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    assert response.json["message"] == "All deadlines updated successfully"
    assert database.get_one_by_field("deadline", "type", 0)["deadline"] == "2022-10-11"
    assert database.get_one_by_field("deadline", "type", 1)["deadline"] == "2022-10-14"
    assert database.get_one_by_field("deadline", "type", 2)["deadline"] == "2022-10-18"


def test_update_user(superuser_logged_in_client, database):
    """Test update user."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    database.delete_all_by_field("users", "email", "dummy_updated@dummy.com")
    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    url = f"/user/update?uuid={user['_id']}"
    response = superuser_logged_in_client.post(
        url,
        data={
            "name": "dummy_updated",
            "email": "dummy_updated@dummy.com",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    updated_user = database.get_by_email("users", "dummy_updated@dummy.com")
    assert updated_user is not None
    assert updated_user["name"] == "dummy_updated"
    assert updated_user["email"] == "dummy_updated@dummy.com"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    database.delete_all_by_field("users", "email", "dummy_updated@dummy.com")


def test_update_user_not_found(superuser_logged_in_client):
    """Test update user not found."""
    url = "/user/update"
    non_existent_uuid = uuid.uuid4().hex

    response = superuser_logged_in_client.post(
        url,
        data={
            "uuid": non_existent_uuid,
            "name": "non_existent_user",
            "email": "non_existent@dummy.com",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 404


def test_update_user_get_request(superuser_logged_in_client, database):
    """Test update user GET request."""
    url = "/user/update"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    response = superuser_logged_in_client.get(url, query_string={"uuid": user["_id"]})

    assert response.status_code == 200
    assert b"Update User" in response.data
    assert b"dummy" in response.data
    assert b"dummy@dummy.com" in response.data

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_user(client, database):
    """Test login user."""
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
    response = client.post(
        url,
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_user_invalid_password(client, database):
    """Test login user with invalid password."""
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
    response = client.post(
        url,
        data={
            "email": "dummy@dummy.com",
            "password": "wrongpassword",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 401

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_user_missing_fields(client):
    """Test login user with missing fields."""
    url = "/user/login"
    response = client.post(
        url,
        data={
            "email": "dummy@dummy.com",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400

    url = "/user/login"
    response = client.post(
        url,
        data={
            "password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400

    url = "/user/login"
    response = client.post(
        url,
        data={},
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400


def test_login_superuser(client):
    """Test login superuser."""
    url = "/user/login"
    response = client.post(
        url,
        data={
            "email": shared.getenv("SUPERUSER_EMAIL"),
            "password": shared.getenv("SUPERUSER_PASSWORD"),
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200


def test_login_already_login(user_logged_in_client):
    """Test login already login."""
    url = "/user/login"
    response = user_logged_in_client.get(url)

    assert response.status_code == 200


def test_get_login_page(client):
    """Test get login page."""
    url = "/user/login"
    response = client.get(url)

    assert response.status_code == 200


def test_delete_user(superuser_logged_in_client, database):
    """Test delete user."""
    url = "/user/delete"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    response = superuser_logged_in_client.delete(
        url,
        query_string={"uuid": user["_id"]},
    )

    assert response.status_code == 200
    assert database.get_by_email("users", "dummy@dummy.com") is None

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_change_password(superuser_logged_in_client, database):
    """Test change password."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    url = f"/user/change_password?uuid={user['_id']}"
    response = superuser_logged_in_client.post(
        url,
        data={
            "new_password": "new_dummy_password",
            "confirm_password": "new_dummy_password",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    updated_user = database.get_by_email("users", "dummy@dummy.com")
    assert updated_user is not None
    assert pbkdf2_sha512.verify("new_dummy_password", updated_user["password"])

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_change_password_mismatch(superuser_logged_in_client, database):
    """Test change password with mismatch."""
    url = "/user/change_password"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    response = superuser_logged_in_client.post(
        url,
        data={
            "uuid": user["_id"],
            "new_password": "new_dummy_password",
            "confirm_password": "mismatch_password",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400
    assert b"Passwords don't match" in response.data

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_get_change_password_page(superuser_logged_in_client, database):
    """Test get change password page."""
    url = "/user/change_password"
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    database.insert("users", user)

    response = superuser_logged_in_client.get(url, query_string={"uuid": user["_id"]})

    assert response.status_code == 200
    assert b"Change Password" in response.data

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_send_match_email(user_logged_in_client, database):
    """Test send match email."""
    url = "/user/send_match_email"
    database.delete_all_by_field("students", "email", "dummy_student@dummy.com")
    database.delete_all_by_field("employers", "email", "dummy_employer@dummy.com")
    database.delete_all_by_field("opportunities", "title", "dummy_opportunity")

    student = {
        "_id": uuid.uuid4().hex,
        "first_name": "dummy_student",
        "email": "dummy_student@dummy.com",
    }

    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "dummy_employer",
        "email": "dummy_employer@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    opportunity = {
        "_id": uuid.uuid4().hex,
        "title": "dummy_opportunity",
        "employer_id": employer["_id"],
    }

    database.insert("students", student)
    database.insert("opportunities", opportunity)
    database.insert("employers", employer)

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")
    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    response = user_logged_in_client.post(
        url,
        data={
            "student": student["_id"],
            "opportunity": opportunity["_id"],
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    assert response.json["message"] == "Email Sent"

    database.delete_all_by_field("students", "email", "dummy_student@dummy.com")
    database.delete_all_by_field("employers", "email", "dummy_employer@dummy.com")
    database.delete_all_by_field("opportunities", "title", "dummy_opportunity")
    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_user_home(user_logged_in_client):
    """Test user home page."""
    url = "/user/home"

    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_search_users_page(superuser_logged_in_client):
    """Test search users page."""
    url = "/user/search"

    response = superuser_logged_in_client.get(url)
    assert response.status_code == 200


def test_delete_opportunity(user_logged_in_client, database):
    """Test the delete opportunity."""
    url = "/opportunities/employer_delete_opportunity?opportunity_id=123"

    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123"})

    response = user_logged_in_client.get(url)

    assert response.status_code == 302


def test_add_employer_post(user_logged_in_client, database):
    """Test POST request to add employer route."""
    url = "/employers/add_employer"
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    employer_data = {
        "_id": uuid.uuid1().hex,
        "company_name": "dummy",
        "email": "dummy@dummy.com",
    }

    response = user_logged_in_client.post(
        url,
        data=employer_data,
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")


def test_update_employer_post(user_logged_in_client, database):
    """Test POST request to update employer route."""

    url = "/employers/update_employer"

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    database.insert(
        "employers", {"_id": "123", "company_name": "dummy", "email": "dummy@dummy.com"}
    )

    updated_data = {
        "employer_id": "123",
        "company_name": "dummy1",
        "email": "dummy@dummy.com",
    }

    response = user_logged_in_client.post(
        url,
        data=updated_data,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")


def test_update_employer_post_wrong_id(user_logged_in_client, database):
    """Test POST request to update employer route."""

    url = "/employers/update_employer"

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    database.insert(
        "employers", {"_id": "123", "company_name": "dummy", "email": "dummy@dummy.com"}
    )

    updated_data = {
        "employer_id": "1234",
        "company_name": "dummy1",
        "email": "dummy@dummy.com",
    }

    response = user_logged_in_client.post(
        url,
        data=updated_data,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 404
    assert response.json == {"error": "Employer not found"}

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")


def test_update_employer_get_wrong_id(user_logged_in_client):
    """Test GET request to update employer with a non-existent employer ID."""

    url = "/employers/update_employer?employer_id=9999"  # Non-existent employer_id

    response = user_logged_in_client.get(
        url, follow_redirects=True
    )  # Follow the redirect

    assert (
        response.status_code == 200
    )  # Since it redirects, it should be 200 after landing


def test_update_employer_get_method(user_logged_in_client, database):
    """Test GET request to update employer route."""
    url = "/employers/update_employer"

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    database.insert(
        "employers", {"_id": "123", "company_name": "dummy", "email": "dummy@dummy.com"}
    )

    response = user_logged_in_client.get(url, query_string={"employer_id": "123"})

    assert response.status_code == 200


def test_delete_employer_no_id(user_logged_in_client):
    """Test POST request to delete employer route without providing an employer ID."""
    url = "/employers/delete_employer"

    response = user_logged_in_client.post(url, json={}, content_type="application/json")

    assert response.status_code == 400
    assert response.json == {"error": "Employer ID is required"}


def test_delete_employer(user_logged_in_client, database):
    """Test POST request to delete employer route."""
    url = "/employers/delete_employer"
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    employer = {"_id": "123", "company_name": "dummy", "email": "dummy@dummy.com"}
    database.insert("employers", employer)

    response = user_logged_in_client.post(
        url,
        json={"employer_id": "123"},
        content_type="application/json",
    )

    assert response.status_code == 200
    assert response.json == {"message": "Employer deleted"}

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")


def test_employer_add_opportunity_post(user_logged_in_client, database):
    """Test the employer_update_opportunity page."""
    url = "/opportunities/employer_add_update_opportunity"

    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("opportunities", "_id", "1234")
    opportunity = {
        "_id": "1234",
        "title": "Software Internship",
        "description": "A great opportunity to learn.",
        "url": "https://example.com",
        "location": "Remote",
        "modules_required": '["CS101", "CS102"]',  # Matches how the request expects it
        "courses_required": '["Computer_Science"]',
        "spots_available": 3,
        "duration": "6_months",
    }

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = user_logged_in_client.post(
            url, data=opportunity, content_type="application/x-www-form-urlencoded"
        )

    assert response.status_code == 200
    database.delete_by_id("opportunities", "1234")
    database.delete_all_by_field("employers", "email", "dummy@dummy,com")


def test_delete_student(user_logged_in_client, database):
    """Test the delete student route."""

    student_id = 123

    url = f"/students/delete_student/{student_id}"  # Format the URL correctly

    # Ensure no existing student with this ID
    database.delete_all_by_field("students", "_id", str(student_id))

    # Insert a test student with an integer ID
    student = {
        "student_id": str(student_id),
        "first_name": "dummy",
        "email": "dummy@dummy.com",
    }
    database.insert("students", student)

    # Send DELETE request
    response = user_logged_in_client.delete(url)

    # Check response
    assert response.status_code == 200
    assert response.json == {"message": "Student deleted"}


def test_register_student(user_logged_in_client, database):
    """Test the register student route."""
    url = "/students/add_student"

    database.delete_all_by_field(
        "students", "student_id", "123"
    )  # Ensure no existing student with this ID

    student = {
        "student_id": "123",
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "course": "Computer Science",
        "modules": [],
        "comments": "",
    }

    response = user_logged_in_client.post(
        url, json=student, content_type="application/json"
    )

    assert response.status_code == 200

    database.delete_all_by_field("students", "student_id", "123")  # Clean up


def test_update_student_post_no_uuid(user_logged_in_client, database):
    """Test POST request to update student route."""
    url = "/students/update_student"

    database.delete_all_by_field("students", "student_id", "123")
    database.insert("students", {"_id": "123", "student_id": "123"})
    student = {
        "_id": "123",
        "student_id": "123",
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "course": "dummy",
        "skills": ["dummy"],
        "comments": "dummy",
        "attempted_skills": ["dummy"],
        "has_car": "dummy",
        "placement_duration": "dummy",
        "modules": ["dummy"],
    }

    response = user_logged_in_client.post(
        url,
        data=student,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 404
    assert response.json == {"error": "Invalid request"}

    database.delete_all_by_field("students", "student_id", "123")  # Clean up


def test_update_student_post_with_uuid(user_logged_in_client, database):
    """Test POST request to update student route."""
    url = "/students/update_student?uuid=123"

    database.delete_all_by_field("students", "student_id", "123")
    database.insert("students", {"_id": "123", "student_id": "123"})
    student = {
        "_id": "123",
        "student_id": "123",
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "course": "dummy",
        "skills": ["dummy"],
        "comments": "dummy",
        "attempted_skills": ["dummy"],
        "has_car": "dummy",
        "placement_duration": ["1_day"],
        "modules": ["dummy"],
    }

    response = user_logged_in_client.post(
        url,
        data=student,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    assert response.json == {"message": "Student updated"}
    found_student = database.get_one_by_id("students", "123")
    assert found_student is not None
    assert found_student["first_name"] == "dummy"
    database.delete_all_by_field("students", "student_id", "123")


def test_update_student_get_method(user_logged_in_client, database):
    """Test GET request to update student route."""
    url = "/students/update_student"

    database.delete_all_by_field("students", "student_id", "123")
    database.insert("students", {"_id": "123", "student_id": "123"})
    response = user_logged_in_client.get(url, query_string={"uuid": "123"})

    assert response.status_code == 200
    database.delete_all_by_field("students", "student_id", "123")  # Clean up
