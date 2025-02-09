import pytest
from flask import session

import os
import sys

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core import handlers

os.environ["IS_TEST"] = "True"


@pytest.fixture()
def app():
    from app import app

    yield app

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess.clear()


@pytest.fixture()
def client(app):
    yield app.test_client()


def test_allowed_file():
    """Test allowed_file function."""

    assert handlers.allowed_file("document.pdf", {"pdf", "txt"}) is True
    assert handlers.allowed_file("image.jpeg", {"png", "jpg"}) is False
    assert handlers.allowed_file("no_extension", {"pdf", "txt"}) is False


def test_login_required_redirect(client):
    """Test login_required decorator redirects when not logged in."""
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/students/login"


def test_student_login_required_redirect(client):
    """Test student_login_required decorator redirects when student is not logged in."""
    response = client.get("/students/details/12345678")
    assert response.status_code == 302
    assert response.headers["Location"] == "/students/login"


def test_employers_login_required_redirect(client):
    """Test employers_login_required decorator redirects when employer is not logged in."""
    response = client.get("/employers/home")
    assert response.status_code == 302
    assert response.headers["Location"] == "/employers/login"


def test_admin_or_employers_required_redirect(client):
    """Test admin_or_employers_required decorator redirects when neither admin nor employer is logged in."""
    response = client.get("/opportunities/search")
    assert response.status_code == 302
    assert response.headers["Location"] == "/students/login"


def test_get_user_type(app):
    """Test get_user_type function with different session states."""
    with app.app_context():
        with app.test_request_context():
            session["user"] = {"name": "AdminUser"}
            assert handlers.get_user_type() == "admin"
            session.clear()

            session["employer"] = {"company_name": "TechCorp"}
            assert handlers.get_user_type() == "employer"
            session.clear()

            session["student"] = "student_id"
            assert handlers.get_user_type() == "student"
            session.clear()

            assert handlers.get_user_type() is None


def test_index_route(client):
    """Test home page route."""

    with client.session_transaction() as session:
        session["user"] = {"name": "AdminUser"}
        session["logged_in"] = True

    response = client.get("/")
    assert response.status_code == 200


def test_get_session(client):
    """Test /api/session route for different users."""
    with client.session_transaction() as sess:
        sess["user"] = {"name": "AdminUser"}
        sess["logged_in"] = True

    response = client.get("/api/session")
    assert response.status_code == 200
    assert response.json == {"user_type": "adminuser"}

    with client.session_transaction() as sess:
        sess.clear()
        sess["employer"] = {"company_name": "TechCorp"}
        sess["employer_logged_in"] = True

    response = client.get("/api/session")
    assert response.status_code == 200
    assert response.json == {"user_type": "TechCorp"}

    with client.session_transaction() as sess:
        sess.clear()
        sess["logged_in"] = True

    response = client.get("/api/session")
    assert response.status_code == 200
    assert response.json == {"user_type": None}


def test_privacy_policy(client):
    """Test privacy policy page route."""
    response = client.get("/privacy_policy")
    assert response.status_code == 200


def test_robots_txt(client):
    """Test robots.txt route."""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert response.content_type == "text/plain; charset=utf-8"


def test_favicon(client):
    """Test favicon route."""
    response = client.get("/favicon.ico")
    assert response.status_code == 200
    assert response.content_type in ["image/vnd.microsoft.icon", "image/x-icon"]


def test_signout(client):
    """Test signout clears session and redirects."""
    with client.session_transaction() as sess:
        sess["logged_in"] = True

    response = client.get("/signout")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"

    with client.session_transaction() as sess:
        assert "logged_in" not in sess


def test_404_page(client):
    """Test custom 404 error page."""
    response = client.get("/404")
    assert response.status_code == 200


def test_500_page(client):
    """Test custom 500 error page."""
    response = client.get("/500")
    assert response.status_code == 200
