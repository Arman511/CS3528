"""Tests for the User model."""

import os
import sys
from dotenv import load_dotenv
import pytest
from passlib.hash import pbkdf2_sha512

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

    app.config["TESTING"] = True
    return app


@pytest.fixture()
def user_model():
    """Fixture to create a user model."""
    from user.models import User

    return User()


@pytest.fixture()
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    tables = [
        "users",
        "students",
        "employers",
    ]

    for table in tables:
        DATABASE.delete_all_by_field(table, "email", "dummy@dummy.com")

    # Cleanup code
    DATABASE.connection.close()


def test_start_session(app, user_model):
    """Tests the start_session method of the User model."""
    user = {
        "_id": "123",
        "name": "Test User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():  # Add this line
            response = user_model.start_session(user)
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "/user/home"
            assert "password" not in json_data


def test_register_success(app, database, user_model):
    """Tests the register method of the User model."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "124",
        "name": "New User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            session["superuser"] = True
            response = user_model.register(user)
            json_data = response[0].get_json()
            assert response[1] == 201
            assert json_data["message"] == "User registered successfully"
            session.clear()

    # Delete the user from the database
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_email_in_use(app, database, user_model):
    """Tests the register method of the User model when the email is already in use."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "125",
        "name": "Existing User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.register(user)
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Email address already in use"

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_failure(app, user_model):
    """Tests the register method of the User model when
    the request is missing the email or password."""

    with app.app_context():
        with app.test_request_context():
            response = user_model.register({})
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Missing email or password"


def test_login_success(app, database, user_model):
    """Tests the login method of the User model."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "126",
        "name": "Login User",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }

    # Insert the user into the database
    database.insert("users", user)

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "dummy",
    }

    with app.app_context():
        with app.test_request_context():
            response = user_model.login(attempt_user)
            json_data = response[0].get_json()
            assert "logged_in" in session
            assert response[1] == 200
            assert json_data["message"] == "/user/home"
            assert "password" not in json_data
            session.clear()

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_invalid_credentials(app, database, user_model):
    """Tests the login method of the User model when the credentials are invalid."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "127",
        "name": "Invalid User",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("password"),
    }

    # Insert the user into the database
    database.insert("users", user)

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "wrongpassword",
    }

    with app.app_context():
        with app.test_request_context():
            response = user_model.login(attempt_user)
            json_data = response[0].get_json()
            assert response[1] == 401
            assert json_data["error"] == "Invalid login credentials"

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_user_not_found(app, database, user_model):
    """Tests the login method of the User model when the user is not found."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            response = user_model.login(attempt_user)
            json_data = response[0].get_json()
            assert response[1] == 401
            assert json_data["error"] == "Invalid login credentials"


def test_update_deadlines_success(app, database, user_model):
    """Tests the change_deadline method of the User model."""
    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_deadline(
                "2023-12-31", "2024-01-15", "2024-01-31"
            )
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "All deadlines updated successfully"
            assert (
                database.get_one_by_field("deadline", "type", 0)["deadline"]
                == "2023-12-31"
            )
            assert (
                database.get_one_by_field("deadline", "type", 1)["deadline"]
                == "2024-01-15"
            )
            assert (
                database.get_one_by_field("deadline", "type", 2)["deadline"]
                == "2024-01-31"
            )

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_update_deadlines_invalid_format(app, database, user_model):
    """Tests the change_deadline method of the User model with an invalid date format."""
    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_deadline(
                "invalid-date", "2024-01-15", "2024-01-31"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Invalid deadline format. Use YYYY-MM-DD."

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_update_deadlines_details_later_than_student_ranking(app, database, user_model):
    """Tests the change_deadline method of the User model
    with the details deadline later than the student ranking deadline."""
    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_deadline(
                "2024-01-16", "2024-01-15", "2024-01-31"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert (
                json_data["error"]
                == "Details deadline cannot be later than Student Ranking deadline."
            )

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_update_deadlines_student_ranking_later_than_opportunities_ranking(
    app, database, user_model
):
    """Tests the change_deadline method of the User model
    with the student ranking deadline later than the opportunities ranking deadline."""
    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_deadline(
                "2024-01-15", "2024-01-31", "2024-01-30"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert (
                json_data["error"]
                == "Student Ranking deadline cannot be later than Opportunities Ranking deadline."
            )

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_send_match_email(app, database, user_model):
    """Tests the send_match_email method of the User model."""
    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")
    database.delete_all_by_field("opportunities", "employer_id", "employer-uuid")

    student_uuid = "student-uuid"
    student = {
        "_id": "student-uuid",
        "first_name": "Student",
        "last_name": "User",
        "email": "dummy@dummy.com",
    }
    database.insert("students", student)
    opportunity_uuid = "opportunity-uuid"
    opportunity = {
        "_id": "opportunity-uuid",
        "title": "Software Developer",
        "employer_id": "employer-uuid",
    }
    database.insert("opportunities", opportunity)

    employer = {
        "_id": "employer-uuid",
        "company_name": "Employer",
        "email": "dummy@dummy.com",
    }
    database.insert("employers", employer)
    student_email = "student@example.com"
    employer_email = "employer@example.com"

    with app.app_context():
        with app.test_request_context():
            response = user_model.send_match_email(
                student_uuid, opportunity_uuid, student_email, employer_email
            )
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "Email Sent"

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")
    database.delete_all_by_field("opportunities", "employer_id", "employer-uuid")


def test_delete_user_success(app, database, user_model):
    """Tests the delete_user_by_uuid method of the User model."""
    database.delete_all_by_field("users", "email", "delete@dummy.com")

    user_uuid = "delete-success-uuid"
    user = {
        "_id": user_uuid,
        "name": "Delete User",
        "email": "delete@dummy.com",
        "password": "password",
    }

    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.delete_user_by_uuid(user_uuid)
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "User deleted successfully"
            assert database.get_one_by_id("users", user_uuid) is None

    database.delete_all_by_field("users", "email", "delete@dummy.com")


def test_delete_user_not_found(app, user_model):
    """Tests the delete_user_by_uuid method of the User model when the user is not found."""
    user_uuid = "non-existent-uuid"

    with app.app_context():
        with app.test_request_context():
            response = user_model.delete_user_by_uuid(user_uuid)
            json_data = response[0].get_json()
            assert response[1] == 404
            assert json_data["error"] == "User not found"


def test_get_user_by_uuid_success(app, database, user_model):
    """Tests the get_user_by_uuid method of the User model."""
    database.delete_all_by_field("users", "email", "get@dummy.com")

    user_uuid = "get-success-uuid"
    user = {
        "_id": user_uuid,
        "name": "Get User",
        "email": "get@dummy.com",
        "password": "password",
    }

    # Insert the user into the database
    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            retrieved_user = user_model.get_user_by_uuid(user_uuid)
            assert retrieved_user is not None
            assert retrieved_user["_id"] == user_uuid
            assert retrieved_user["email"] == "get@dummy.com"

    database.delete_all_by_field("users", "email", "get@dummy.com")


def test_get_user_by_uuid_not_found(app, user_model):
    """Tests the get_user_by_uuid method of the User model when the user is not found."""
    user_uuid = "non-existent-uuid"

    with app.app_context():
        with app.test_request_context():
            retrieved_user = user_model.get_user_by_uuid(user_uuid)
            assert retrieved_user is None


def test_get_users_without_passwords(app, database, user_model):
    """Tests the get_users_without_passwords method of the User model."""
    database.delete_all_by_field("users", "email", "nopassword1@dummy.com")
    database.delete_all_by_field("users", "email", "nopassword2@dummy.com")
    existing_users = database.get_all("users")
    database.delete_all("users")

    user1 = {
        "_id": "user1-uuid",
        "name": "User One",
        "email": "nopassword1@dummy.com",
        "password": "password1",
    }
    user2 = {
        "_id": "user2-uuid",
        "name": "User Two",
        "email": "nopassword2@dummy.com",
        "password": "password2",
    }

    database.insert("users", user1)
    database.insert("users", user2)

    with app.app_context():
        with app.test_request_context():
            users = user_model.get_users_without_passwords()
            assert len(users) == 2
            for user in users:
                assert "password" not in user

    database.delete_all_by_field("users", "email", "nopassword1@dummy.com")
    database.delete_all_by_field("users", "email", "nopassword2@dummy.com")

    for user in existing_users:
        database.insert("users", user)


def test_update_user_success(app, database, user_model):
    """Tests the update_user method of the User model."""
    database.delete_all_by_field("users", "email", "update@dummy.com")
    database.delete_all_by_field("users", "email", "updated@dummy.com")

    user_uuid = "update-success-uuid"
    user = {
        "_id": user_uuid,
        "name": "Update User",
        "email": "update@dummy.com",
        "password": "password",
    }

    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.update_user(
                user_uuid, "Updated Name", "updated@dummy.com"
            )
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "User updated successfully"
            updated_user = database.get_one_by_id("users", user_uuid)
            assert updated_user["name"] == "Updated Name"
            assert updated_user["email"] == "updated@dummy.com"

    database.delete_all_by_field("users", "email", "update@dummy.com")
    database.delete_all_by_field("users", "email", "updated@dummy.com")


def test_update_user_email_in_use(app, database, user_model):
    """Tests the update_user method of the User model when the email is already in use."""
    database.delete_all_by_field("users", "email", "update@dummy.com")
    database.delete_all_by_field("users", "email", "existing@dummy.com")

    user_uuid = "update-email-in-use-uuid"
    user = {
        "_id": user_uuid,
        "name": "Update User",
        "email": "update@dummy.com",
        "password": "password",
    }

    existing_user = {
        "_id": "existing-uuid",
        "name": "Existing User",
        "email": "existing@dummy.com",
        "password": "password",
    }

    database.insert("users", user)
    database.insert("users", existing_user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.update_user(
                user_uuid, "Updated Name", "existing@dummy.com"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Email address already in use"

    database.delete_all_by_field("users", "email", "update@dummy.com")
    database.delete_all_by_field("users", "email", "existing@dummy.com")


def test_update_user_not_found(app, database, user_model):
    """Tests the update_user method of the User model when the user is not found."""
    database.delete_all_by_field("users", "email", "update@dummy.com")

    user_uuid = "non-existent-uuid"

    with app.app_context():
        with app.test_request_context():
            response = user_model.update_user(
                user_uuid, "Updated Name", "update@dummy.com"
            )
            json_data = response[0].get_json()
            assert response[1] == 404
            assert json_data["error"] == "User not found"


def test_change_password_success(app, database, user_model):
    """Tests the change_password method of the User model."""
    database.delete_all_by_field("users", "email", "changepassword@dummy.com")

    user_uuid = "change-password-uuid"
    user = {
        "_id": user_uuid,
        "name": "Change Password User",
        "email": "changepassword@dummy.com",
        "password": pbkdf2_sha512.hash("oldpassword"),
    }

    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_password(
                user_uuid, "newpassword", "newpassword"
            )
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["message"] == "Password updated successfully"
            updated_user = database.get_one_by_id("users", user_uuid)
            assert pbkdf2_sha512.verify("newpassword", updated_user["password"])

    database.delete_all_by_field("users", "email", "changepassword@dummy.com")


def test_change_password_mismatch(app, database, user_model):
    """Tests the change_password method of the User model when passwords don't match."""
    database.delete_all_by_field("users", "email", "changepassword@dummy.com")

    user_uuid = "change-password-uuid"
    user = {
        "_id": user_uuid,
        "name": "Change Password User",
        "email": "changepassword@dummy.com",
        "password": pbkdf2_sha512.hash("oldpassword"),
    }

    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = user_model.change_password(
                user_uuid, "newpassword", "differentpassword"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Passwords don't match"

    database.delete_all_by_field("users", "email", "changepassword@dummy.com")


def test_register_missing_name(app, database, user_model):
    """Tests the register method of the User model when the request is missing the name."""
    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "128",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            response = user_model.register(user)
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Missing name"

    database.delete_all_by_field("users", "email", "dummy@dummy.com")
