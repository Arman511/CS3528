"""Tests for the user routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
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

    yield database

    # Cleanup code
    database.connection.close()


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


def test_login(client):
    """Test logging in a user."""
    attempt_user = {
        "email": shared.getenv("SUPERUSER_EMAIL"),
        "password": shared.getenv("SUPERUSER_PASSWORD"),
    }

    response = client.post(
        "/user/login",
        data=attempt_user,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200
    assert response.json["message"] == "/user/search"


def test_configure_settings(superuser_logged_in_client, database):
    """Test configuring settings as a superuser."""
    current_config = database.get_all("config")
    database.delete_all("config")
    response = superuser_logged_in_client.get("/superuser/configure")
    assert response.status_code == 200

    response = superuser_logged_in_client.post(
        "/superuser/configure",
        data={
            "max_skills": 5,
            "min_num_ranking_student_to_opportunity": 3,
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    assert response.json["message"] == "Settings updated successfully"

    for entry in current_config:
        database.insert("config", entry)


def test_get_config_page(superuser_logged_in_client):
    """Test getting the configure settings page."""
    response = superuser_logged_in_client.get("/superuser/configure")
    assert response.status_code == 200


def test_configure_settings_invalid_input(superuser_logged_in_client):
    """Test configuring settings with invalid input."""
    response = superuser_logged_in_client.post(
        "/superuser/configure",
        data={
            "max_skills": "invalid",
            "min_num_ranking_student_to_opportunity": "invalid",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Invalid input"
