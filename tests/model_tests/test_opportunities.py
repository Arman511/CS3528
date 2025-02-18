"""Test for the Opportunities model."""

import os
import sys
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
        
def test_get_opportunities_by_title_exception(opportunity_model, app):
    """Test getting opportunities by title."""
    
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
    
    database.insert("opportunities", {"_id": "123", "title": "SE", "employer_id": "456"})
    database.insert("employers", {"_id": "456", "company_name": "Company1"})
    
    with app.app_context():
        opportunities = opportunity_model.get_opportunities_by_company("Company1")
        
        assert len(opportunities) == 1
        assert opportunities[0]["_id"] == "123"
        assert opportunities[0]["title"] == "SE"
        assert opportunities[0]["employer_id"] == "456"

def test_get_opportunities_by_company_id(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "_id", "123")

    database.insert("opportunities", {"_id": "123", "title": "SE", "employer_id": "456"})
    
    with app.app_context():
        with app.test_request_context():
            opportunites = opportunity_model.get_opportunity_by_company_id("456")
            assert len(opportunites) == 1
            assert opportunites[0]["_id"] == "123"

    database.delete_all_by_field("opportunities", "_id", "123")
    
cache = {}

def test_get_opportunity_by_id(opportunity_model, database, app):
    # Set up the cache with predefined data
    cache["data"] = [
        {"_id": "1", "name": "Opportunity 1"},
        {"_id": "2", "name": "Opportunity 2"},
        {"_id": "3", "name": "Opportunity 3"},
    ]
    cache["last_updated"] = datetime.now() + timedelta(minutes=5)  # Future date to ensure cache is valid

    with app.app_context():
        with app.test_request_context():
            # Test for an existing opportunity
            opportunity = opportunity_model.get_opportunity_by_id("2")
            assert opportunity is not None
            assert opportunity["_id"] == "2"
            assert opportunity["name"] == "Opportunity 2"

            # Test for a non-existing opportunity
            opportunity = opportunity_model.get_opportunity_by_id("999")
            assert opportunity is None

            # Clean up the cache
            cache.clear()
    
def test_get_employer_by_id(opportunity_model, database, app):
    database.delete_all_by_field("opportunities", "_id", "123")
    database.insert("opportunities", {"_id": "123", "employer_id": "456"})
    
    with app.app_context():
        with app.test_request_context():
            employer = opportunity_model.get_employer_by_id("123")
            assert employer == "456"
            
            database.delete_all_by_field("opportunities", "_id", "123")
            employer = opportunity_model.get_employer_by_id("123")
            assert employer == ""

def test_get_opportunities(opportunity_model, database, app):
    with app.app_context():
        with app.test_request_context():
            opportunities = opportunity_model.get_opportunities()