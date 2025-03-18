"""Test for the employer routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid
from unittest.mock import patch
from itsdangerous import URLSafeSerializer
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
    otp_serializer = URLSafeSerializer(str(shared.getenv("SECRET_KEY", "secret")))
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

    with client.session_transaction() as session:
        session.clear()


def test_employer_otp_no_login(client):
    """Test OTP endpoint when employer is not logged in."""
    response = client.post("/employers/otp", data={"otp": "123456"})
    assert response.status_code == 400
    assert response.json == {"error": "Employer not logged in."}


def test_employer_otp_no_otp(client):
    """Test OTP endpoint when OTP is not in session."""
    with client.session_transaction() as session:
        session["employer"] = {"_id": "123"}

    response = client.post("/employers/otp", data={"otp": "123456"})
    assert response.status_code == 400
    assert response.json == {"error": "OTP not sent."}


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


def test_search_opportunities_page(employer_logged_in_client):
    """Test the search_opportunities page."""
    url = "/opportunities/search"

    response = employer_logged_in_client.get(url)
    assert response.status_code == 200


def test_employer_delete_opportunity_page_no_opportunity_id(employer_logged_in_client):
    """Test the employer_delete_opportunity page."""
    url = "/opportunities/employer_delete_opportunity"

    response = employer_logged_in_client.get(url)
    assert response.status_code == 302


def test_employers_rank_students_no_opportunity_id(employer_logged_in_client):
    """Test the rank_students page without providing an opportunity ID."""

    url = "/employers/rank_students"  # No opportunity_id in the request

    with patch(
        "app.DEADLINE_MANAGER.is_past_opportunities_ranking_deadline",
        return_value=False,
    ):
        response = employer_logged_in_client.get(url)  # GET request

    assert response.status_code == 400
    assert response.json == {"error": "Need opportunity ID."}


def test_employers_rank_students_past_opportunities_deadline(
    employer_logged_in_client, database
):
    """Test the rank_students page."""
    url = "/employers/rank_students"

    database.insert("deadline", {"type": 0, "deadline": "2022-10-10"})
    database.insert("deadline", {"type": 1, "deadline": "2022-10-12"})
    database.insert("deadline", {"type": 2, "deadline": "2022-10-15"})

    response = employer_logged_in_client.get(url)
    assert response.status_code == 200
    assert b"Ranking deadline has passed as of 2022-10-15" in response.data


def test_employers_rank_students_wrong_opportunity_id(
    employer_logged_in_client, database
):
    """Test the rank_students page with an incorrect opportunity_id."""

    url = "/employers/rank_students?opportunity_id=123"  # Pass opportunity_id in query string
    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123", "employer_id": "23424"})

    with patch(
        "app.DEADLINE_MANAGER.is_past_opportunities_ranking_deadline",
        return_value=False,
    ):
        response = employer_logged_in_client.get(url)  # GET request

    assert response.status_code == 400
    assert response.json == {"error": "Employer does not own this opportunity."}

    database.delete_all_by_field("opportunities", "_id", "123")


def test_employers_rank_students_past_student_ranking_deadline(
    employer_logged_in_client, database
):
    """Test that employers cannot rank students before the student ranking deadline has passed."""

    url = "/employers/rank_students?opportunity_id=123"
    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123", "employer_id": "test_employer_id"})

    with employer_logged_in_client.session_transaction() as session:
        session["employer"] = {"_id": "test_employer_id"}

    # Use patch directly
    with patch(
        "app.DEADLINE_MANAGER.is_past_opportunities_ranking_deadline",
        return_value=False,
    ), patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=False
    ), patch(
        "app.DEADLINE_MANAGER.get_student_ranking_deadline", return_value="2025-10-15"
    ):

        response = employer_logged_in_client.get(url)

    assert response.status_code == 200
    assert (
        b"Student ranking deadline must have passed before you can start, wait till 2025-10-15"
        in response.data
    )

    database.delete_all_by_field("opportunities", "_id", "123")


def test_employer_update_opportunity(employer_logged_in_client):
    """Test the employer_update_opportunity page."""
    url = "/opportunities/employer_add_update_opportunity"

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=True):
        response = employer_logged_in_client.get(url)

    assert response.status_code == 200
    assert b"Adding/Updating details deadline has passed as of " in response.data


def test_employer_add_opportunity_post(employer_logged_in_client, database):
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
        response = employer_logged_in_client.post(
            url, data=opportunity, content_type="application/x-www-form-urlencoded"
        )

    assert response.status_code == 200  # Adjust based on actual expected behaviour
    database.delete_by_id("opportunities", "1234")
    database.delete_all_by_field("employers", "email", "dummy@dummy,com")


def test_employer_add_opportunity_post_different_employer_id(
    employer_logged_in_client, database
):
    """Test the employer_update_opportunity page."""
    url = "/opportunities/employer_add_update_opportunity"

    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("opportunities", "_id", "1234")
    opportunity = {
        "_id": "123",
        "title": "Software Internship",
        "description": "A great opportunity to learn.",
        "url": "https://example.com",
        "location": "Remote",
        "modules_required": '["CS101", "CS102"]',  # Matches how the request expects it
        "courses_required": '["Computer_Science"]',
        "spots_available": 3,
        "duration": "6_months",
    }
    database.insert("opportunities", {"_id": "123", "employer_id": "test_employer_id"})

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = employer_logged_in_client.post(
            url, data=opportunity, content_type="application/x-www-form-urlencoded"
        )

    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized Access."}
    database.delete_by_id("opportunities", "123")
    database.delete_all_by_field("employers", "email", "dummy@dummy,com")


def test_get_opportunity_page_no_id(employer_logged_in_client):
    """Test retrieving an opportunity without an ID, ensuring UUID is generated."""
    url = "/opportunities/employer_add_update_opportunity"  # No opportunity_id

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = employer_logged_in_client.get(url)

    assert response.status_code == 200


def test_get_opportunity_page_with_id(employer_logged_in_client, database):
    """Test retrieving an opportunity with an ID."""
    url = "/opportunities/employer_add_update_opportunity?opportunity_id=123"  # Pass opportunity

    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert(
        "opportunities",
        {"_id": "123", "employer_id": "test_employer_id", "spots_available": 1},
    )

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = employer_logged_in_client.get(url)

    assert response.status_code == 200


def test_employers_rank_students_success(employer_logged_in_client, database):
    """Test the rank_students page."""
    url = "/employers/rank_students?opportunity_id=123"
    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123", "employer_id": "test_employer_id"})

    with employer_logged_in_client.session_transaction() as session:
        session["employer"] = {"_id": "test_employer_id"}

    with patch(
        "app.DEADLINE_MANAGER.is_past_opportunities_ranking_deadline",
        return_value=False,
    ), patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=True
    ):

        response = employer_logged_in_client.get(url)

    assert response.status_code == 200

    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "test_employer_id")
