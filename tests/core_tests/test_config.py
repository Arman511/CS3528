from flask import session
import pytest
import os
import datetime
import sys

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core.configuration_settings import Config
from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"


@pytest.fixture()
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )
    yield DATABASE
    # Cleanup code after the test
    DATABASE.connection.close()


@pytest.fixture
def app():
    from app import app

    app.config["TESTING"] = True
    return app


def test_config_initialization(database):
    current_config = database.get_all("config")
    database.delete_all("config")
    config = Config(database)

    assert config.get_max_num_of_skills() == 10
    assert config.get_min_num_ranking_student_to_opportunities() == 5

    # Test updating the config values
    config.set_num_of_skills(15)
    config.set_min_num_ranking_student_to_opportunities(8)

    assert config.get_max_num_of_skills() == 15
    assert config.get_min_num_ranking_student_to_opportunities() == 8

    # Reset the values to default
    config.set_num_of_skills(10)
    config.set_min_num_ranking_student_to_opportunities(5)

    # Reset the database
    database.delete_all("config")

    for entry in current_config:
        database.insert("config", entry)
