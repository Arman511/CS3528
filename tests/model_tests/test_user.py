"""Tests for the User model."""

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


def test_start_session(app):
    from user.models import User

    user = {
        "_id": "123",
        "name": "Test User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():  # Add this line
            response = User().start_session(user)
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["_id"] == "123"
            assert json_data["name"] == "Test User"
            assert "password" not in json_data


def test_register_success(app, database):
    from user.models import User

    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "124",
        "name": "New User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            response = User().register(user)
            json_data = response[0].get_json()
            assert response[1] == 200
            assert json_data["_id"] == "124"
            assert json_data["name"] == "New User"
            assert "password" not in json_data
            assert "logged_in" in session
            session.clear()

    # Delete the user from the database
    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_email_in_use(app, database):
    from user.models import User

    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "125",
        "name": "Existing User",
        "email": "dummy@dummy.com",
        "password": "password",
    }

    # Insert the user into the database to simulate existing user
    database.insert("users", user)

    with app.app_context():
        with app.test_request_context():
            response = User().register(user)
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Email address already in use"

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_register_failure(app):
    from user.models import User

    # Simulate failure by not inserting the user into the database
    with app.app_context():
        with app.test_request_context():
            response = User().register({})
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Missing email or password"


def test_login_success(app, database):
    from user.models import User

    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "126",
        "name": "Login User",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("password"),
    }

    # Insert the user into the database
    database.insert("users", user)

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            response = User().login(attempt_user)
            json_data = response[0].get_json()
            assert "logged_in" in session
            assert response[1] == 200
            assert json_data["_id"] == "126"
            assert json_data["name"] == "Login User"
            assert "password" not in json_data
            session.clear()

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_invalid_credentials(app, database):
    from user.models import User

    database.delete_all_by_field("users", "email", "dummy@dummy.com")
    user = {
        "_id": "127",
        "name": "Invalid User",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("password"),
    }

    # Insert the user into the database
    database.insert("users", user)

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "wrongpassword",
    }

    with app.app_context():
        with app.test_request_context():
            response = User().login(attempt_user)
            json_data = response[0].get_json()
            assert response[1] == 401
            assert json_data["error"] == "Invalid login credentials"

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


def test_login_user_not_found(app, database):
    from user.models import User

    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    attempt_user = {
        "email": "dummy@dummy.com",
        "password": "password",
    }

    with app.app_context():
        with app.test_request_context():
            response = User().login(attempt_user)
            json_data = response[0].get_json()
            assert response[1] == 401
            assert json_data["error"] == "Invalid login credentials"


def test_update_deadlines_success(app, database):
    from user.models import User

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = User().change_deadline("2023-12-31", "2024-01-15", "2024-01-31")
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


def test_update_deadlines_invalid_format(app, database):
    from user.models import User

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = User().change_deadline(
                "invalid-date", "2024-01-15", "2024-01-31"
            )
            json_data = response[0].get_json()
            assert response[1] == 400
            assert json_data["error"] == "Invalid deadline format. Use YYYY-MM-DD."

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)


def test_update_deadlines_details_later_than_student_ranking(app, database):
    from user.models import User

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = User().change_deadline("2024-01-16", "2024-01-15", "2024-01-31")
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
    app, database
):
    from user.models import User

    deadlines = database.get_all("deadline")
    if deadlines:
        database.delete_all("deadline")

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    with app.app_context():
        with app.test_request_context():
            response = User().change_deadline("2024-01-15", "2024-01-31", "2024-01-30")
            json_data = response[0].get_json()
            assert response[1] == 400
            assert (
                json_data["error"]
                == "Student Ranking deadline cannot be later than Opportunities Ranking deadline."
            )

    database.delete_all("deadline")
    for deadline in deadlines:
        database.insert("deadline", deadline)
