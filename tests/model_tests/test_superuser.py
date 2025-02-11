import os
import sys
from unittest import mock
from dotenv import load_dotenv


# pylint: disable=redefined-outer-name
# flake8: noqa: F811

os.environ["IS_TEST"] = "True"
load_dotenv()
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.database_mongo_manager import DatabaseMongoManager


import pytest


@pytest.fixture()
def app():
    """Fixture to create a test client."""
    from app import app

    app.config["TESTING"] = True
    return app


def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    # Cleanup code
    DATABASE.connection.close()


@pytest.fixture()
def data_model():
    """Fixture to create a test data model."""
    from superuser.model import Superuser

    return Superuser()


def test_login_success(app, data_model):
    """Test logging in a user successfully."""
    attempt_user = {
        "email": os.getenv("SUPERUSER_EMAIL"),
        "password": os.getenv("SUPERUSER_PASSWORD"),
    }

    with app.app_context():
        with app.test_request_context():
            response = data_model.login(attempt_user)

    assert response[0].status_code == 200
    assert response[0].json == {"message": "/user/search"}


def test_login_missing_credentials(app, data_model):
    """Test logging in with missing credentials."""
    attempt_user = {}

    with app.app_context():
        with app.test_request_context():
            response = data_model.login(attempt_user)

    assert response[1] == 400
    assert response[0].json == {"error": "Missing email or password"}


def test_login_invalid_credentials(app, data_model):
    """Test logging in with invalid credentials."""
    attempt_user = {
        "email": "invalid@example.com",
        "password": "wrongpassword",
    }

    with app.app_context():
        with app.test_request_context():
            response = data_model.login(attempt_user)

    assert response[1] == 401
    assert response[0].json == {"error": "Invalid login credentials"}


def test_configure_settings_success(app, data_model):
    """Test configuring settings successfully."""
    max_skills = 10
    min_num_ranking_student_to_opportunity = 5

    with app.app_context():
        with app.test_request_context():
            with mock.patch("app.CONFIG_MANAGER") as mock_config_manager:
                response = data_model.configure_settings(
                    max_skills, min_num_ranking_student_to_opportunity
                )

    assert response[1] == 200
    assert response[0].json == {"message": "Settings updated successfully"}
    mock_config_manager.set_num_of_skills.assert_called_once_with(max_skills)
    mock_config_manager.set_min_num_ranking_student_to_opportunities.assert_called_once_with(
        min_num_ranking_student_to_opportunity
    )


def test_configure_settings_failure(app, data_model):
    """Test configuring settings with an exception."""
    max_skills = 10
    min_num_ranking_student_to_opportunity = 5

    with app.app_context():
        with app.test_request_context():
            with mock.patch("app.CONFIG_MANAGER") as mock_config_manager:
                mock_config_manager.set_num_of_skills.side_effect = Exception(
                    "Test exception"
                )
                response = data_model.configure_settings(
                    max_skills, min_num_ranking_student_to_opportunity
                )

    assert response[1] == 500
    assert response[0].json == {"error": "Test exception"}
