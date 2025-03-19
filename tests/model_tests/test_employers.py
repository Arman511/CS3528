"""This module contains tests for the Employers model."""

import os
import uuid
import sys
from io import BytesIO
import pytest
import pandas as pd
from dotenv import load_dotenv
from core import shared
from core.database_mongo_manager import DatabaseMongoManager

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
def database():
    """Fixture to create a test database."""

    database = DatabaseMongoManager(
        shared.getenv("MONGO_URI"),
        shared.getenv("MONGO_DB_TEST", "cs3528_testing"),
    )
    employers = database.get_all("employers")
    database.delete_all("employers")
    yield database

    database.delete_all("employers")

    for employer in employers:
        database.insert("employers", employer)
    database.delete_all_by_field("_id", "company_name", "email")
    # Cleanup code
    database.connection.close()


@pytest.fixture()
def employer_model():
    """Fixture to create a Employer model instance."""
    from employers.models import Employers  # pylint: disable=import-outside-toplevel

    return Employers()


@pytest.fixture()
def sample_employer(database):
    """Fixture to create a sample employer."""
    yield {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.delete_all_by_field("employers", "company_name", "TechCorp")


def test_register_employer(database, employer_model, app):
    """Test registering an employer."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.delete_all_by_field("employers", "email", "contact@techcorp.com")
    with app.app_context():
        response = employer_model.register_employer(employer)
        assert response[1] == 200
        assert (
            database.get_one_by_field("employers", "email", "contact@techcorp.com")
            is not None
        )


def test_register_existing_email(database, employer_model, app):
    """Test registering an employer with an existing email."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.insert("employers", employer)
    with app.app_context():
        response = employer_model.register_employer(employer)
        assert response[1] == 400
        assert response[0].json["error"] == "Email already in use"


def test_get_employer_by_id(database, employer_model, app):
    """Test retrieving an employer by ID."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.insert("employers", employer)
    with app.app_context():
        retrieved_employer = employer_model.get_employer_by_id(employer["_id"])
        assert retrieved_employer is not None
        assert retrieved_employer["company_name"] == "TechCorp"


def test_delete_employer(database, employer_model, app):
    """Test deleting an employer."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.insert("employers", employer)
    with app.app_context():
        response = employer_model.delete_employer_by_id(employer["_id"])
        assert response[1] == 200
        assert database.get_one_by_id("employers", employer["_id"]) is None


def test_download_all_employers(database, employer_model, app):
    """Test downloading all employers."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.insert("employers", employer)

    with app.app_context():
        with app.test_request_context():  # Ensure proper request context
            response = employer_model.download_all_employers()
            assert response.status_code == 200
            assert (
                response.mimetype
                == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )


def test_upload_employers(database, employer_model, app):
    """Test uploading employers from an Excel file."""
    df = pd.DataFrame([{"Company_name": "TechCorp", "Email": "contact@techcorp.com"}])
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    with app.app_context():
        response = employer_model.upload_employers(excel_buffer)
        assert response[1] == 200
        assert (
            database.get_one_by_field("employers", "email", "contact@techcorp.com")
            is not None
        )


def test_get_company_name(database, employer_model, app, sample_employer):
    """Test getting company name by ID."""
    database.insert("employers", sample_employer)
    with app.app_context():
        company_name = employer_model.get_company_name(sample_employer["_id"])
        assert company_name == "TechCorp"


def test_employer_login(database, employer_model, app, sample_employer):
    """Test employer login."""
    database.insert("employers", sample_employer)
    with app.app_context():
        with app.test_request_context():
            response = employer_model.employer_login(sample_employer["email"])
            assert response[1] == 200
            assert response[0].json["message"] == "OTP sent"


def test_get_employers(database, employer_model, app, sample_employer):
    """Test getting all employers."""
    database.insert("employers", sample_employer)
    with app.app_context():
        employers = employer_model.get_employers()
        assert len(employers) > 0
        assert employers[0]["company_name"] == "TechCorp"


def test_update_employer(database, employer_model, app, sample_employer):
    """Test updating an employer."""
    database.insert("employers", sample_employer)
    update_data = {"company_name": "TechCorp Updated"}
    with app.app_context():
        response = employer_model.update_employer(sample_employer["_id"], update_data)
        assert response[1] == 200
        updated_employer = database.get_one_by_id("employers", sample_employer["_id"])
        assert updated_employer["company_name"] == "TechCorp Updated"


def test_rank_preferences(database, employer_model, app):
    """Test ranking preferences for an opportunity."""
    opportunity = {
        "_id": uuid.uuid4().hex,
        "employer_id": "E101",
        "title": "Internship",
        "preferences": [],
    }
    database.insert("opportunities", opportunity)
    preferences = ["Preference1", "Preference2"]
    with app.app_context():
        response = employer_model.rank_preferences(opportunity["_id"], preferences)
        assert response[1] == 200
        updated_opportunity = database.get_one_by_id(
            "opportunities", opportunity["_id"]
        )
        assert updated_opportunity["preferences"] == preferences


def test_get_company_email_by_id(database, employer_model, app, sample_employer):
    """Test getting company email by ID."""
    database.insert("employers", sample_employer)
    with app.app_context():
        email = employer_model.get_company_email_by_id(sample_employer["_id"])
        assert email == "contact@techcorp.com"


def test_delete_all_employers(database, employer_model, app):
    """Test deleting all employers."""
    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "TechCorp",
        "email": "contact@techcorp.com",
    }
    database.insert("employers", employer)
    with app.app_context():
        response = employer_model.delete_all_employers()
        assert response[1] == 200
        assert database.get_all("employers") == []
