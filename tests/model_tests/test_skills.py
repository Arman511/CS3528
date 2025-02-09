"""Tests for the skills routes."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from passlib.hash import pbkdf2_sha256
import pytest
from dotenv import load_dotenv

from core.database_mongo_manager import DatabaseMongoManager
from datetime import datetime, timedelta
import uuid

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

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    DATABASE.delete_all_by_field("users", "email", "dummy@dummy.com")
    DATABASE.delete_all_by_field("courses", "course_id", "CS101")
    # Cleanup code
    DATABASE.connection.close()


@pytest.fixture()
def skill_model():
    """Fixture to create a Course model instance."""
    from skills.models import Skill

    return Skill()


@pytest.fixture()
def sample_skill(database):
    """Fixture to create a sample course."""
    yield {
        "_id": uuid.uuid4().hex,
        "skill_name": "Test Skill",
        "skill_description": "Test Skill Description",
    }
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
