"""Test for the Opportunities model."""

import os
import sys
from dotenv import load_dotenv
import pytest
from passlib.hash import pbkdf2_sha256

from flask import session
from unittest.mock import patch


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
def opportunity_model():
    """Fixture to create a user model."""
    from opportunities.models import Opportunity  # pylint: disable=import-outside-toplevel

    return app.test_client()

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
    
