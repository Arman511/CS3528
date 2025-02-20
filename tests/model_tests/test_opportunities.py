"""Test for the Opportunities model."""

import os
import sys
import uuid
from dotenv import load_dotenv
import pytest
from passlib.hash import pbkdf2_sha256

from flask import session, jsonify
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO


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
def employer_model():
    """Fixture to create an employer model."""
    from ...employers.models import Employers  # pylint: disable=import-outside-toplevel

    return Employers()


@pytest.fixture()
def opportunity_model():
    """Fixture to create a user model."""
    from ...opportunities.models import (
        Opportunity,
    )  # pylint: disable=import-outside-toplevel

    return Opportunity()


@pytest.fixture()
def database():
    """Fixture to create a database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )
    current_opportunities = DATABASE.get_all("opportunities")
    DATABASE.delete_all("opportunities")
    yield DATABASE
    DATABASE.delete_all("opportunities")
    for opportunity in current_opportunities:
        DATABASE.insert("opportunities", opportunity)

    DATABASE.connection.close()


@pytest.fixture()
def dummy_data(database):
    """Gives dummy data"""
    data = {
        "Title": ["Opportunity 1", "Opportunity 2"],
        "Description": ["Description 1", "Description 2"],
        "URL": ["http://example.com/1", "http://example.com/2"],
        "Spots_available": [5, 10],
        "Location": ["Location 1", "Location 2"],
        "Duration": ["1_week", "1_month"],
        "Employer_email": ["employer1@example.com", "employer2@example.com"],
        "Modules_required": ["THING1,THING2", "THING3"],
        "Courses_required": ["THING1", "THING2"],
    }
    module1 = {
        "_id": uuid.uuid4().hex,
        "module_id": "THING1",
        "module_name": "THING1",
        "module_description": "THING1",
    }
    module2 = {
        "_id": uuid.uuid4().hex,
        "module_id": "THING2",
        "module_name": "THING2",
        "module_description": "THING2",
    }
    module3 = {
        "_id": uuid.uuid4().hex,
        "module_id": "THING3",
        "module_name": "THING3",
        "module_description": "THING3",
    }
    course1 = {
        "_id": uuid.uuid4().hex,
        "course_id": "THING1",
        "course_name": "THING1",
        "course_description": "THING1",
    }
    course2 = {
        "_id": uuid.uuid4().hex,
        "course_id": "THING2",
        "course_name": "THING2",
        "course_description": "THING2",
    }
    employer1 = {
        "_id": uuid.uuid4().hex,
        "company_name": "Company1",
        "email": "employer1@example.com",
    }
    employer2 = {
        "_id": uuid.uuid4().hex,
        "company_name": "Company2",
        "email": "employer2@example.com",
    }

    database.insert("modules", module1)
    database.insert("modules", module2)
    database.insert("modules", module3)
    database.insert("courses", course1)
    database.insert("courses", course2)
    database.insert("employers", employer1)
    database.insert("employers", employer2)

    yield data

    database.delete_by_id("modules", module1["_id"])
    database.delete_by_id("modules", module2["_id"])
    database.delete_by_id("modules", module3["_id"])
    database.delete_by_id("courses", course1["_id"])
    database.delete_by_id("courses", course2["_id"])
    database.delete_by_id("employers", employer1["_id"])
    database.delete_by_id("employers", employer2["_id"])


def test_start_session(app, employer_model):
    """Test starting a session."""
    with app.app_context():
        with app.test_request_context():
            response = employer_model.start_session()
            assert response.status_code == 302
            assert session["employer_logged_in"] == True


def test_add_update_opportunity_unauthorized(opportunity_model, database, app):
    """Test unauthorized access when updating an opportunity."""
    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123", "employer_id": "456"})
    with app.app_context():  # Set up Flask application context
        with app.test_request_context():  # Set up request context for session
            # Mock the session
            session["employer"] = {"_id": "123"}

            # Call the method
            response = opportunity_model.add_update_opportunity(
                {"_id": "123", "employer_id": "456"}
            )

            # Verify the response
            assert response[1] == 401
            assert response[0].json == {"error": "Unauthorized Access."}


def test_rank_preferences_success(opportunity_model, database, app):
    """Test updating preferences for an existing opportunity."""
    with app.app_context():  # Set up Flask application context
        # Mock the database manager
        with patch("app.DATABASE_MANAGER", database):
            # Mock the database responses
            database.get_one_by_id = MagicMock(
                return_value={"_id": "1", "title": "Job 1"}
            )
            database.update_one_by_field = MagicMock(return_value=True)

            # Call the method
            response = opportunity_model.rank_preferences("1", ["pref1", "pref2"])

            # Verify the database calls
            database.get_one_by_id.assert_called_once_with("opportunities", "1")
            database.update_one_by_field.assert_called_once_with(
                "opportunities", "_id", "1", {"preferences": ["pref1", "pref2"]}
            )

            # Verify the response
            assert response[1] == 200
            assert response[0].json == {"message": "Preferences updated"}


def test_rank_preferences_not_found(opportunity_model, database, app):
    """Test updating preferences for a non-existent opportunity."""
    with app.app_context():  # Set up Flask application context
        # Mock the database manager
        with patch("app.DATABASE_MANAGER", database):
            # Mock the database responses
            database.get_one_by_id = MagicMock(return_value=None)
            database.update_one_by_field = MagicMock()  # Properly mock this method

            # Call the method
            response = opportunity_model.rank_preferences("1", ["pref1", "pref2"])

            # Verify the database calls
            database.get_one_by_id.assert_called_once_with("opportunities", "1")
            database.update_one_by_field.assert_not_called()  # Now this will work

            # Verify the response
            assert response[1] == 404
            assert response[0].json == {"error": "Opportunity not found"}


def test_search_opportunities_exception(opportunity_model, database, app):
    """Test searching opportunities with an exception."""

    with app.app_context():  # Set up Flask application context
        with app.test_request_context():  # Set up request context for session
            opportunites = opportunity_model.search_opportunities("Job 1", "Company1")
            assert opportunites == []


def test_search_opportunities_both_title_and_company(opportunity_model, database, app):
    """Test searching opportunities by both title and company name."""

    # Clear any existing data
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")

    # Insert test data
    database.insert("employers", {"_id": "456", "company_name": "Company1"})
    database.insert(
        "opportunities", {"_id": "123", "title": "Job 1", "employer_id": "456"}
    )

    with app.app_context():  # Set up Flask application context
        # Call the function
        opportunities = opportunity_model.search_opportunities("Job 1", "Company1")

        # Assert the results
        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "Job 1"
        assert opportunities[0]["company_name"] == "Company1"

    # Clean up
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")


def test_search_opportunities_by_title(opportunity_model, database, app):
    """Test searching opportunities by title only."""

    # Clear any existing data
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")

    # Insert test data
    database.insert(
        "opportunities", {"_id": "123", "title": "SE", "employer_id": "456"}
    )
    database.insert("employers", {"_id": "456", "company_name": "Company1"})

    with app.app_context():  # Set up Flask application context
        # Call the function with only the title
        opportunities = opportunity_model.search_opportunities("SE", "")

        # Assert the results
        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "SE"
        assert opportunities[0]["company_name"] == "Company1"

    # Clean up
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")


def test_search_opportunities_by_company(opportunity_model, database, app):
    """Test searching opportunities by company name only."""

    # Clear any existing data
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")

    # Insert test data
    database.insert(
        "opportunities", {"_id": "123", "title": "SE", "employer_id": "456"}
    )
    database.insert("employers", {"_id": "456", "company_name": "Company1"})

    with app.app_context():  # Set up Flask application context
        # Call the function with only the company name
        opportunities = opportunity_model.search_opportunities("", "Company1")

        # Assert the results
        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "SE"
        assert opportunities[0]["company_name"] == "Company1"

    # Clean up
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")


def test_get_opportunities_by_title_no_title(opportunity_model, app):
    """Test getting opportunities by title."""

    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_title("")
        assert opportunities == []


def test_get_opportunities_by_title_exception(opportunity_model, app, database):
    """Test getting opportunities by title."""
    assert database.get_all("opportunities") == []
    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_title("SE")
        assert opportunities == []


def test_get_opportunities_by_title(opportunity_model, database, app):
    """Test getting opportunities by title."""

    # Clear any existing data
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")

    # Insert test data
    database.insert(
        "opportunities", {"_id": "123", "title": "SE", "employer_id": "456"}
    )
    database.insert("employers", {"_id": "456", "company_name": "Company1"})

    with app.app_context():  # Set up Flask application context
        # Call the function with only the title
        opportunities = opportunity_model.get_opportunities_by_title("SE")

        # Assert the results
        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "SE"
        assert opportunities[0]["employer_id"] == "456"

    # Clean up
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")


def test_get_opportunities_by_company_no_company(opportunity_model, app):
    """Test getting opportunities by company."""

    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_company("")
        assert opportunities == []


def test_get_opportunities_by_company_doesnt_exist(opportunity_model, app):
    """Test getting opportunities by company."""

    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_company("Company1")
        assert opportunities == []


def test_get_opportunities_by_company(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")

    database.insert(
        "opportunities", {"_id": "123", "title": "SE", "employer_id": "456"}
    )
    database.insert("employers", {"_id": "456", "company_name": "Company1"})

    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_company("Company1")

        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "SE"
        assert opportunities[0]["employer_id"] == "456"

    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("employers", "_id", "456")


def test_get_opportunities_by_company_id(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "_id", "123")

    database.insert(
        "opportunities", {"_id": "123", "title": "SE", "employer_id": "456"}
    )

    with app.app_context():
        with app.test_request_context():
            opportunites = opportunity_model.get_opportunity_by_company_id("456")
            assert len(opportunites) == 1
            assert opportunites[0]["_id"] == "123"

    database.delete_all_by_field("opportunities", "_id", "123")


def test_get_opportunity_by_id(opportunity_model, database, app):
    # Set up the cache with predefined data
    opportunities = database.get_all("opportunities")
    database.delete_all("opportunities")

    op = {
        "_id": "2",
        "name": "Opportunity 2",
    }
    database.insert("opportunities", op)
    with app.app_context():
        with app.test_request_context():
            # Test for an existing opportunity
            opportunity_model.get_opportunity_by_id("2")
            opportunity = opportunity_model.get_opportunity_by_id("2")
            assert opportunity is not None
            assert opportunity["_id"] == "2"
            assert opportunity["name"] == "Opportunity 2"

            # Test for a non-existing opportunity
            opportunity = opportunity_model.get_opportunity_by_id("999")
            assert opportunity is None

    database.delete_all("opportunities")
    for opportunity in opportunities:
        database.insert("opportunities", opportunity)


def test_get_employer_by_id(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "employer_id", "456")
    opportunity = {"_id": uuid.uuid4().hex, "employer_id": "456"}
    database.insert("opportunities", opportunity)
    database.insert("employers", {"_id": "456", "company_name": "Company1"})

    with app.app_context():
        with app.test_request_context():
            employer = opportunity_model.get_employer_by_id(opportunity["_id"])
            assert employer == "456"

    database.delete_all("opportunities")
    database.delete_all_by_field("employers", "_id", "456")


def test_get_employer_by_id_no_employer(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "_id", "123")

    with app.app_context():
        with app.test_request_context():
            employer = opportunity_model.get_employer_by_id("123")
            assert employer == ""


def test_get_opportunities(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    database.delete_all("opportunities")

    database.insert("opportunities", {"_id": "123", "employer_id": "456"})

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.get_opportunities()
            opportunities = opportunity_model.get_opportunities()

            assert len(opportunities) == 1

    database.delete_all_by_field("opportunities", "_id", "123")

    for op in opportunity:
        database.insert("opportunities", op)


def test_get_opportunities_by_duration(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    database.delete_all("opportunities")

    database.insert(
        "opportunities", {"_id": "123", "employer_id": "456", "duration": "1_week"}
    )

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.get_opportunities_by_duration(
                '["1_week", "1_day"]'
            )

            assert opportunities[1] == 200

    for op in opportunity:
        database.insert("opportunities", op)


def test_delete_opportunity_by_id(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    students = database.get_all("students")

    database.delete_all("opportunities")
    database.delete_all("students")

    database.insert("opportunities", {"_id": "123", "employer_id": "456"})
    database.insert("students", {"_id": "123", "preferences": ["123"]})

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.delete_opportunity_by_id("123")

            assert opportunities[1] == 200

    database.delete_all_by_field("opportunities", "_id", "123")
    database.delete_all_by_field("students", "_id", "123")

    for op in opportunity:
        database.insert("opportunities", op)

    for student in students:
        database.insert("students", student)


def test_delete_opportunity_by_id_no_opportunity(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")

    database.delete_all("opportunities")

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.delete_opportunity_by_id("123")
            assert opportunities[1] == 404
            assert opportunities[0].json == {"error": "Opportunity not found"}

    for op in opportunity:
        database.insert("opportunities", op)


def test_delete_opportunities(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    database.delete_all("opportunities")

    database.insert("opportunities", {"_id": "123", "employer_id": "456"})

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.delete_opportunities()

            assert opportunities[1] == 200
            assert opportunities[0].json == {"message": "All opportunities deleted"}

    database.delete_all_by_field("opportunities", "_id", "123")

    for op in opportunity:
        database.insert("opportunities", op)


def test_get_valid_students(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    students = database.get_all("students")

    database.delete_all("opportunities")
    database.delete_all("students")

    database.insert("opportunities", {"_id": "1234", "employer_id": "456"})
    database.insert("students", {"_id": "123", "preferences": ["1234"]})

    with app.app_context():
        with app.test_request_context():
            result = opportunity_model.get_valid_students("1234")

            assert result[0]["_id"] == "123"
            assert result[0]["preferences"] == ["1234"]

    database.delete_all_by_field("opportunities", "_id", "1234")
    database.delete_all_by_field("students", "_id", "123")

    for op in opportunity:
        database.insert("opportunities", op)

    for student in students:
        database.insert("students", student)


def test_rank_preferences(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")

    database.delete_all("opportunities")

    database.insert(
        "opportunities", {"_id": "1234", "employer_id": "456", "preferences": ["123"]}
    )

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.rank_preferences("1234", ["321"])
            assert opportunities[1] == 200
            assert opportunities[0].json == {"message": "Preferences updated"}

            updated = database.get_one_by_id("opportunities", "1234")
            assert updated["preferences"] == ["321"]

    database.delete_all_by_field("opportunities", "_id", "1234")

    for op in opportunity:
        database.insert("opportunities", op)


def test_rank_preferences_no_opportunity(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")

    database.delete_all("opportunities")

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.rank_preferences("1234", ["321"])
            assert opportunities[1] == 404
            assert opportunities[0].json == {"error": "Opportunity not found"}

    for op in opportunity:
        database.insert("opportunities", op)


def test_delete_all_opportunity_admin(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    students = database.get_all("students")

    database.delete_all("opportunities")
    database.delete_all("students")

    database.insert("opportunities", {"_id": "1234", "employer_id": "456"})
    database.insert("students", {"_id": "123", "preferences": ["1234"]})

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.delete_all_opportunities(True)
            assert opportunities[1] == 200
            assert opportunities[0].json == {"message": "All opportunities deleted"}

    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("opportunities", "_id", "1234")

    for op in opportunity:
        database.insert("opportunities", op)

    for student in students:
        database.insert("students", student)


def test_delete_all_opportunity_employer(
    opportunity_model, employer_model, database, app
):
    opportunity = database.get_all("opportunities")
    students = database.get_all("students")

    database.delete_all("opportunities")
    database.delete_all("students")

    database.insert("opportunities", {"_id": "1234", "employer_id": "456"})
    database.insert("students", {"_id": "123", "preferences": ["1234"]})

    with app.app_context():
        with app.test_request_context():
            employer_model.start_session()
            session["employer"] = {"_id": "456"}
            opportunities = opportunity_model.delete_all_opportunities(False)
            assert opportunities[1] == 200
            assert opportunities[0].json == {"message": "All opportunities deleted"}

            result = database.get_all("opportunities")
            assert len(result) == 0

    database.delete_all_by_field("students", "_id", "123")
    database.delete_all_by_field("opportunities", "_id", "1234")

    for op in opportunity:
        database.insert("opportunities", op)

    for student in students:
        database.insert("students", student)


def test_download_opportunities_admin(opportunity_model, database, app):
    opportunity = database.get_all("opportunities")
    employers = database.get_all("employers")

    database.delete_all("opportunities")
    database.delete_all("employers")

    database.insert(
        "employers",
        {"_id": "456", "company_name": "Company1", "email": "dummy@dummy.com"},
    )
    database.insert(
        "opportunities",
        {
            "_id": "1234",
            "employer_id": "456",
            "title": "Job 1",
            "description": "Description 1",
            "duration": "1_week",
            "location": "Location 1",
            "modules_required": ["Module 1", "Module 2"],
            "url": "URL 1",
            "courses_required": ["Course 1", "Course 2"],
            "spots_available": 10,
        },
    )

    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.download_opportunities(True)
            assert opportunities.status_code == 200

    database.delete_all_by_field("opportunities", "_id", "1234")
    database.delete_all_by_field("employers", "_id", "456")

    for op in opportunity:
        database.insert("opportunities", op)

    for employer in employers:
        database.insert("employers", employer)


def test_download_opportunities_employer(
    opportunity_model, employer_model, database, app
):
    opportunity = database.get_all("opportunities")
    employers = database.get_all("employers")

    database.delete_all("opportunities")
    database.delete_all("employers")

    database.insert(
        "employers",
        {"_id": "456", "company_name": "Company1", "email": "dummy@dummy.com"},
    )
    database.insert(
        "opportunities",
        {
            "_id": "1234",
            "employer_id": "456",
            "title": "Job 1",
            "description": "Description 1",
            "duration": "1_week",
            "location": "Location 1",
            "modules_required": ["Module 1", "Module 2"],
            "url": "URL 1",
            "courses_required": ["Course 1", "Course 2"],
            "spots_available": 10,
        },
    )

    with app.app_context():
        with app.test_request_context():
            employer_model.start_session()
            session["employer"] = {"_id": "456"}
            opportunities = opportunity_model.download_opportunities(False)
            assert opportunities.status_code == 200

    database.delete_all_by_field("opportunities", "_id", "1234")
    database.delete_all_by_field("employers", "_id", "456")

    for op in opportunity:
        database.insert("opportunities", op)

    for employer in employers:
        database.insert("employers", employer)


def test_upload_opportunities(opportunity_model, database, app, dummy_data):
    """Test upload opportunities"""
    assert len(database.get_all("opportunities")) == 0
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            # Test successful upload (admin)
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[0].json == {
                "message": "Opportunities uploaded successfully"
            }
            assert response[1] == 200

            result = database.get_one_by_field(
                "opportunities", "title", "Opportunity 1"
            )
            assert result["title"] == "Opportunity 1"
            result = database.get_one_by_field(
                "opportunities", "title", "Opportunity 2"
            )
            assert result["title"] == "Opportunity 2"


def test_upload_opportunities_employer(
    opportunity_model, employer_model, database, app, dummy_data
):
    """Test upload opportunities by employer"""
    assert len(database.get_all("opportunities")) == 0

    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            employer_model.start_session()
            session["employer"] = {"_id": "456"}
            response = opportunity_model.upload_opportunities(file, is_admin=False)
            assert response[0].json == {
                "message": "Opportunities uploaded successfully"
            }
            assert response[1] == 200

            result = database.get_all_by_field("opportunities", "employer_id", "456")
            assert len(result) == 2
            assert result[0]["title"] == "Opportunity 1"
            assert result[1]["title"] == "Opportunity 2"


def test_upload_opportunities_wrong_spot_available(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with invalid spots available value"""
    assert len(database.get_all("opportunities")) == 0

    dummy_data["Spots_available"] = ["invalid", 10]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert "Invalid spots available value" in response[0].json["error"]


def test_upload_opportunities_wrong_duration(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with invalid duration value"""

    assert len(database.get_all("opportunities")) == 0
    dummy_data["Spots_available"] = [5, 10]
    dummy_data["Duration"] = ["invalid", "1_month"]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert "Invalid duration value" in response[0].json["error"]


def test_upload_opportunities_no_employer(opportunity_model, database, app, dummy_data):
    """Test upload opportunities with no employer in the database"""

    assert len(database.get_all("opportunities")) == 0
    dummy_data["Employer_email"] = ["dummy@dummy.com", "dummy1@dummy.com"]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert (
                "Employer email dummy@dummy.com not found in database at row 2"
                in response[0].json["error"]
            )

            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 1"
            )
            assert len(result) == 0
            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 2"
            )
            assert len(result) == 0


def test_upload_opportunities_failed_modules(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with invalid modules required"""
    assert len(database.get_all("opportunities")) == 0
    dummy_data["Modules_required"] = ["invalid", "module2"]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)

    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert "Invalid module(s)" in response[0].json["error"]

            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 1"
            )
            assert len(result) == 0
            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 2"
            )
            assert len(result) == 0

    database.delete_all_by_field("employers", "_id", "456")


def test_upload_opportunities_failed_courses(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with invalid courses required"""
    assert len(database.get_all("opportunities")) == 0
    dummy_data["Courses_required"] = ["invalid", "course2"]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)
    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert "Invalid course(s)" in response[0].json["error"]

            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 1"
            )
            assert len(result) == 0
            result = database.get_all_by_field(
                "opportunities", "title", "Opportunity 2"
            )
            assert len(result) == 0


def test_upload_opportunities_wrong_title(opportunity_model, database, app, dummy_data):
    """Test upload opportunities with wrong title"""
    assert len(database.get_all("opportunities")) == 0
    dummy_data["Title"] = ["", "Opportunity 2"]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)
    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert (
                "Title is required and cannot be empty in opportunity at row"
                in response[0].json["error"]
            )

    database.delete_all_by_field("employers", "_id", "456")


def test_upload_opportunities_wrong_description(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with wrong description"""
    dummy_data["Description"] = ["Description 1", ""]
    assert len(database.get_all("opportunities")) == 0
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)
    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert (
                "Description is required and cannot be empty in opportunity at row"
                in response[0].json["error"]
            )


def test_upload_opportunities_wrong_spots(opportunity_model, database, app, dummy_data):
    """Test upload opportunities with wrong spots available"""
    assert len(database.get_all("opportunities")) == 0
    dummy_data["Spots_available"] = [0, 10]
    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)
    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
            assert (
                "Spots available must be at least 1 in opportunity"
                in response[0].json["error"]
            )


def test_upload_opportunities_wrong_duration(
    opportunity_model, database, app, dummy_data
):
    """Test upload opportunities with wrong duration"""
    assert len(database.get_all("opportunities")) == 0
    dummy_data["Duration"] = ["1_week", "invalid"]

    df = pd.DataFrame(dummy_data)
    file = BytesIO()
    df.to_excel(file, index=False)
    file.seek(0)
    with app.app_context():
        with app.test_request_context():
            response = opportunity_model.upload_opportunities(file, is_admin=True)
            assert response[1] == 400
