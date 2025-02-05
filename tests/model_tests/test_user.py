"""Tests for the User model."""
import os
import sys

from dotenv import load_dotenv
import pytest
# flake8: noqa: F811

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

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
