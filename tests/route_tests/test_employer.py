""" Test for the employer routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from itsdangerous import URLSafeSerializer
from passlib.hash import pbkdf2_sha256
import pytest
from dotenv import load_dotenv

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

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    # Cleanup code
    DATABASE.connection.close()


@pytest.fixture()
def employer_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login an employer."""
    database.add_table("employers")
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")

    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "dummy",
        "email": "dummy@dummy.com",
    }

    database.insert("employers", employer)

    url = "/employers/login"
    client.post(
        url,
        data={"email": "dummy@dummy.com"},
        content_type="application/x-www-form-urlencoded",
    )
    otp_serializer = URLSafeSerializer(str(os.getenv("SECRET_KEY", "secret")))
    with client.session_transaction() as session:
        otp = otp_serializer.loads(session["OTP"])

    url = "/employers/otp"
    client.post(
        url,
        data={"otp": otp},
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    database.delete_all_by_field("employers", "email", "dummy@dummy.com")


def test_employer_login_page(client):
    """Test the employer login page."""
    url = "/employers/login"

    response = client.get(url)
    assert response.status_code == 200


def test_employer_home_page(employer_logged_in_client):
    """Test the employer home page."""
    url = "/employers/home"

    response = employer_logged_in_client.get(url)
    assert response.status_code == 200


def test_search_oppurtunities_page(employer_logged_in_client):
    """Test the search_oppurtunities page."""
    url = "/opportunities/search"

    response = employer_logged_in_client.get(url)
    assert response.status_code == 200
