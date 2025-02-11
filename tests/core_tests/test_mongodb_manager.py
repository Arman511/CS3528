"""Test the MongoDB Manager class."""

import os
import sys
from dotenv import load_dotenv
import pytest
from pymongo.errors import (
    ConfigurationError,
    OperationFailure,
    ServerSelectionTimeoutError,
    DuplicateKeyError,
)


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
    DATABASE.delete_all("test_collection")  # Cleanup after tests
    DATABASE.delete_collection("test_collection")
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


def test_get_all_by_field(database):
    """Test fetching all entries by a specific field value."""
    database.delete_all("test_collection")
    database.delete_collection("test_collection")
    test_data1 = {"_id": "test8", "category": "A", "name": "Entry 1"}
    test_data2 = {"_id": "test9", "category": "B", "name": "Entry 2"}
    test_data3 = {"_id": "test10", "category": "A", "name": "Entry 3"}
    database.insert("test_collection", test_data1)
    database.insert("test_collection", test_data2)
    database.insert("test_collection", test_data3)

    results = database.get_all_by_field("test_collection", "category", "A")
    assert len(results) == 2
    assert results[0]["category"] == "A"
    assert results[0]["name"] == "Entry 1"
    assert results[1]["category"] == "A"
    assert results[1]["name"] == "Entry 3"

    database.delete_by_id("test_collection", "test8")
    database.delete_by_id("test_collection", "test9")
    database.delete_by_id("test_collection", "test10")


def test_is_table(database):
    assert database.is_table("test_collection") is False
    database.add_table("test_collection")
    assert database.is_table("test_collection") is True
    assert database.is_table("non_existent_collection") is False


def test_get_all_by_two_fields(database):
    test_data1 = {"_id": "test10", "category": "A", "status": "active"}
    test_data2 = {"_id": "test11", "category": "A", "status": "inactive"}
    test_data3 = {"_id": "test12", "category": "B", "status": "active"}
    test_data4 = {"_id": "test13", "category": "B", "status": "inactive"}
    test_data5 = {"_id": "test14", "category": "A", "status": "active"}
    database.insert("test_collection", test_data1)
    database.insert("test_collection", test_data2)
    database.insert("test_collection", test_data3)
    database.insert("test_collection", test_data4)
    database.insert("test_collection", test_data5)

    results = database.get_all_by_two_fields(
        "test_collection", "category", "A", "status", "active"
    )
    assert len(results) == 2
    assert results[0]["status"] == "active"
    assert results[1]["status"] == "active"
    assert results[0]["_id"] == "test10"
    assert results[1]["_id"] == "test14"

    database.delete_by_id("test_collection", "test10")
    database.delete_by_id("test_collection", "test11")
    database.delete_by_id("test_collection", "test12")
    database.delete_by_id("test_collection", "test13")
    database.delete_by_id("test_collection", "test14")


def test_update_by_field(database):
    test_data = {"_id": "test15", "category": "A", "name": "Old Name"}
    database.insert("test_collection", test_data)
    database.update_by_field("test_collection", "category", "A", {"name": "New Name"})

    updated = database.get_one_by_id("test_collection", "test15")
    assert updated["name"] == "New Name"

    database.delete_by_id("test_collection", "test15")


def test_create_index(database):
    result = database.create_index("test_collection", "name")
    assert isinstance(result, str)


def test_delete_one_by_field(database):
    test_data = {"_id": "test20", "category": "A", "name": "Entry to delete"}
    database.insert("test_collection", test_data)

    database.delete_one_by_field("test_collection", "category", "A")
    deleted = database.get_one_by_id("test_collection", "test20")
    assert deleted is None


def test_get_all_by_in_list(database):
    test_data1 = {"_id": "test21", "category": "A", "name": "Entry 1"}
    test_data2 = {"_id": "test22", "category": "B", "name": "Entry 2"}
    test_data3 = {"_id": "test23", "category": "C", "name": "Entry 3"}
    test_data4 = {"_id": "test24", "category": "A", "name": "Entry 4"}

    database.insert("test_collection", test_data1)
    database.insert("test_collection", test_data2)
    database.insert("test_collection", test_data3)
    database.insert("test_collection", test_data4)

    # Fetch entries with category "A" or "C"
    results = database.get_all_by_in_list("test_collection", "category", ["A", "C"])

    assert len(results) == 3
    assert any(item["_id"] == "test21" for item in results)
    assert any(item["_id"] == "test23" for item in results)
    assert any(item["_id"] == "test24" for item in results)

    database.delete_by_id("test_collection", "test21")
    database.delete_by_id("test_collection", "test22")
    database.delete_by_id("test_collection", "test23")
    database.delete_by_id("test_collection", "test24")


def test_empty_connection_string():
    """Test that an empty connection string raises a ValueError."""
    with pytest.raises(ValueError, match="Connection string cannot be empty"):
        DatabaseMongoManager("", "cs3528_testing")


def test_invalid_connection_string(monkeypatch):
    """Test that an invalid connection string raises ConfigurationError."""

    def mock_mongo_client(*args, **kwargs):
        raise ConfigurationError("Invalid MongoDB connection string")

    monkeypatch.setattr("pymongo.MongoClient", mock_mongo_client)

    with pytest.raises(ConfigurationError, match="Invalid MongoDB connection string"):
        DatabaseMongoManager("invalid_connection_string", "cs3528_testing")


def test_operation_failure(monkeypatch):
    """Test that an operation failure raises SystemExit."""

    class MockClient:
        class MockAdmin:
            def command(self, cmd):
                raise OperationFailure("Authentication failed")

        def __init__(self, *args, **kwargs):
            self.admin = self.MockAdmin()

    monkeypatch.setattr(
        "pymongo.MongoClient", MockClient
    )  # Correctly patch inside pymongo

    with pytest.raises(SystemExit) as excinfo:
        DatabaseMongoManager("invalid_connection_string", "cs3528_testing")

    assert excinfo.value.code == 1


def test_server_selection_timeout(monkeypatch):
    """Test that a server selection timeout raises SystemExit."""

    class MockClient:
        class MockAdmin:
            def command(self, cmd):
                raise ServerSelectionTimeoutError("Server selection timed out")

        def __init__(self, *args, **kwargs):
            self.admin = self.MockAdmin()

    monkeypatch.setattr(
        "pymongo.MongoClient", MockClient
    )  # Correctly mock inside pymongo

    with pytest.raises(SystemExit) as excinfo:
        DatabaseMongoManager("invalid_connection_string", "cs3528_testing")

    assert excinfo.value.code == 1


def test_default_database_if_empty():
    """Test that an empty database name defaults to 'cs3528_testing'."""
    db_manager = DatabaseMongoManager(os.getenv("MONGO_URI"), "")
    assert db_manager.database.name == "cs3528_testing"
