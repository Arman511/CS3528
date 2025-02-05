"""Test configuration."""

import os
import uuid
from pymongo import MongoClient
import pytest
from passlib.hash import pbkdf2_sha256

from dotenv import load_dotenv

load_dotenv()

os.environ["IS_TEST"] = "True"
# pylint: disable=redefined-outer-name
# flake8: noqa: F811

from core.database_mongo_manager import DatabaseMongoManager


@pytest.fixture()
def client():
    """Fixture to create a test client."""
    from ..app import app  # pylint: disable=import-outside-toplevel

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
def user_logged_in_client(client, database):
    """Fixture to login a user."""
    database.add_table("users")
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
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


def test_base(client):
    """Test base route."""
    url = "/"

    response = client.get(url)
    expected = (
        b"<!doctype html>\n<html lang=en>\n<title>Redirecting...</title>\n"
        b"<h1>Redirecting...</h1>\n<p>You should be redirected automatically "
        b'to the target URL: <a href="/students/login">/students/login</a>. '
        b"If not, click the link.\n"
    )
    assert response.status_code == 302
    assert response.get_data() == expected


def test_user_login_page(client):
    """Test user login page."""
    url = "/user/login"

    response = client.get(url)
    assert response.status_code == 200


def test_student_login_page(client):
    """Test student login page."""
    url = "/students/login"

    response = client.get(url)
    assert response.status_code == 200


def test_employers_login_page(client):
    """Test employers login page."""
    url = "/employers/login"

    response = client.get(url)
    assert response.status_code == 200


def test_login(user_logged_in_client):
    """Test login."""

    url = "/"
    response = user_logged_in_client.get(url)

    assert response.status_code == 200


def test_signout(user_logged_in_client):
    """Test signout."""
    url = "/signout"
    response = user_logged_in_client.get(url)

    response = user_logged_in_client.get("/")
    assert response.status_code == 302
    expected = (
        b"<!doctype html>\n<html lang=en>\n<title>Redirecting...</title>\n"
        b"<h1>Redirecting...</h1>\n<p>You should be redirected automatically "
        b'to the target URL: <a href="/students/login">/students/login</a>. '
        b"If not, click the link.\n"
    )
    assert response.status_code == 302
    assert response.get_data() == expected
