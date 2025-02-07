"""Test the MongoDB Manager class."""

import os
import sys
from dotenv import load_dotenv
import pytest
from pymongo.errors import DuplicateKeyError, ConfigurationError


# flake8: noqa: F811

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
from core.database_mongo_manager import DatabaseMongoManager

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )
    yield DATABASE
    DATABASE.delete_all("test_collection")  # Cleanup after tests
    DATABASE.delete_collection("test_collection")
    DATABASE.connection.close()


def test_insert_and_get_by_id(database):
    test_data = {"_id": "test1", "name": "Test Entry"}
    database.insert("test_collection", test_data)
    result = database.get_one_by_id("test_collection", "test1")
    assert result is not None
    assert result["name"] == "Test Entry"
    database.delete_by_id("test_collection", "test1")


def test_update_one_by_id(database):
    test_data = {"_id": "test2", "name": "Initial Name"}
    database.insert("test_collection", test_data)
    database.update_one_by_id("test_collection", "test2", {"name": "Updated Name"})
    updated = database.get_one_by_id("test_collection", "test2")
    assert updated["name"] == "Updated Name"
    database.delete_by_id("test_collection", "test2")


def test_delete_by_id(database):
    test_data = {"_id": "test3", "name": "To be deleted"}
    database.insert("test_collection", test_data)
    database.delete_by_id("test_collection", "test3")
    deleted = database.get_one_by_id("test_collection", "test3")
    assert deleted is None


def test_get_all(database):
    test_data1 = {"_id": "test4", "name": "Entry 1"}
    test_data2 = {"_id": "test5", "name": "Entry 2"}
    database.insert("test_collection", test_data1)
    database.insert("test_collection", test_data2)
    results = database.get_all("test_collection")
    assert len(results) >= 2
    database.delete_all("test_collection")


def test_increment(database):
    test_data = {"_id": "test6", "count": 0}
    database.insert("test_collection", test_data)
    database.increment("test_collection", "test6", "count", 5)
    updated = database.get_one_by_id("test_collection", "test6")
    assert updated["count"] == 5
    database.delete_by_id("test_collection", "test6")


def test_get_by_email(database):
    test_data = {"_id": "test7", "email": "test@example.com"}
    database.insert("test_collection", test_data)
    result = database.get_by_email("test_collection", "test@example.com")
    assert result is not None
    assert result["email"] == "test@example.com"
    database.delete_by_id("test_collection", "test7")


def test_connection_success():
    db = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )
    assert db.connection is not None
    db.close_connection()


def test_insert_duplicate_id(database):
    test_data = {"_id": "duplicate_test", "name": "First Entry"}
    database.insert("test_collection", test_data)

    with pytest.raises(DuplicateKeyError):
        database.insert("test_collection", test_data)

    database.delete_by_id("test_collection", "duplicate_test")


def test_update_non_existent_record(database):
    result = database.update_one_by_id(
        "test_collection", "non_existent", {"name": "Updated"}
    )
    assert result.matched_count == 0


def test_delete_non_existent_record(database):
    result = database.delete_by_id("test_collection", "non_existent")
    assert result.deleted_count == 0


def test_get_all_empty(database):
    results = database.get_all("empty_collection")
    assert results == []


def test_increment_non_existent_field(database):
    test_data = {"_id": "increment_test"}
    database.insert("test_collection", test_data)

    database.increment("test_collection", "increment_test", "counter", 10)
    updated = database.get_one_by_id("test_collection", "increment_test")

    assert updated["counter"] == 10

    database.delete_by_id("test_collection", "increment_test")


def test_case_sensitivity_strict_search(database):
    test_data = {"_id": "case_test", "email": "TEST@EXAMPLE.COM"}
    database.insert("test_collection", test_data)

    result = database.get_one_by_field_strict(
        "test_collection", "email", "test@example.com"
    )

    assert result is not None  # Should match despite case difference
    database.delete_by_id("test_collection", "case_test")


def test_large_data_insertion(database):
    large_text = "A" * 16777216
    test_data = {"_id": "large_data_test", "text": large_text}

    with pytest.raises(Exception):
        database.insert("test_collection", test_data)


def test_text_search_on_non_indexed_field(database):
    test_data = {"_id": "text_test", "description": "MongoDB text search test"}
    database.insert("test_collection", test_data)

    with pytest.raises(Exception):
        database.get_all_by_text_search("test_collection", "MongoDB")

    database.delete_by_id("test_collection", "text_test")
