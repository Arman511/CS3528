import sys
import os
from dotenv import load_dotenv
import pytest
import datetime

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

os.environ["IS_TEST"] = "True"

load_dotenv()
from core import shared
from core.database_mongo_manager import DatabaseMongoManager
from core.deadline_manager import DeadlineManager


@pytest.fixture()
def database():
    """Fixture to create a test database."""

    DATABASE = DatabaseMongoManager(
        shared.getenv("MONGO_URI"),
        shared.getenv("MONGO_DB_TEST", "cs3528_testing"),
    )
    deadlines = DATABASE.get_all("deadline")
    DATABASE.delete_all("deadline")
    yield DATABASE
    DATABASE.delete_all("deadline")
    for deadline in deadlines:
        DATABASE.insert("deadline", deadline)

    # Cleanup code after the test
    DATABASE.connection.close()


@pytest.fixture
def deadline_manager(database, app):
    """Create an instance of DeadlineManager using the database fixture."""
    deadlines = database.get_all("deadline")

    database.delete_all("deadline")

    with app.app_context():
        with app.test_request_context():
            deadline_manager = DeadlineManager()
            database.delete_all("deadline")
            yield deadline_manager
    database.delete_all("deadline")

    for deadline in deadlines:
        database.insert("deadline", deadline)


@pytest.fixture
def app():
    from app import app

    app.config["TESTING"] = True
    return app


def test_get_details_deadline(database, deadline_manager):
    """Test fetching the details deadline from the database."""
    database.insert("deadline", {"type": 0, "deadline": "2025-03-01"})

    deadline = deadline_manager.get_details_deadline()
    assert deadline == "2025-03-01"


def test_get_details_deadline_default(database, deadline_manager, app):
    """Test default deadline when no deadline exists."""

    expected = (datetime.datetime.now() + datetime.timedelta(weeks=1)).strftime(
        "%Y-%m-%d"
    )
    with app.app_context():
        with app.test_request_context():
            deadline = deadline_manager.get_details_deadline()
            assert deadline == expected
            assert (
                database.get_one_by_field("deadline", "type", 0)["deadline"] == expected
            )


def test_is_past_details_deadline(deadline_manager, database):
    """Test checking if the details deadline has passed."""
    database.insert("deadline", {"type": 0, "deadline": "2024-03-01"})

    # Past date
    result = deadline_manager.is_past_details_deadline()
    assert result

    # Future date
    database.update_one_by_field(
        "deadline",
        "type",
        0,
        {
            "deadline": (
                datetime.datetime.now() + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
        },
    )
    result = deadline_manager.is_past_details_deadline()
    assert not result


def test_get_student_ranking_deadline(database, deadline_manager):
    """Test fetching the student ranking deadline from the database."""
    database.insert("deadline", {"type": 1, "deadline": "2025-04-01"})

    deadline = deadline_manager.get_student_ranking_deadline()
    assert deadline == "2025-04-01"


def test_get_student_ranking_deadline_default(database, deadline_manager):
    """Test default student ranking deadline when no deadline exists."""

    expected = (
        datetime.datetime.strptime(deadline_manager.get_details_deadline(), "%Y-%m-%d")
        + datetime.timedelta(weeks=1)
    ).strftime("%Y-%m-%d")

    deadline = deadline_manager.get_student_ranking_deadline()
    assert deadline == expected
    assert database.get_one_by_field("deadline", "type", 1)["deadline"] == expected


def test_is_past_student_ranking_deadline(deadline_manager, database):
    """Test checking if the student ranking deadline has passed."""
    database.insert("deadline", {"type": 1, "deadline": "2024-04-01"})

    # Past date
    result = deadline_manager.is_past_student_ranking_deadline()
    assert result

    # Future date
    database.update_one_by_field(
        "deadline",
        "type",
        1,
        {
            "deadline": (
                datetime.datetime.now() + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
        },
    )
    result = deadline_manager.is_past_student_ranking_deadline()
    assert not result


def test_get_opportunities_ranking_deadline(database, deadline_manager):
    existing_deadline = database.get_one_by_field("deadline", "type", 2)

    database.insert("deadline", {"type": 2, "deadline": "2025-05-01"})

    deadline = deadline_manager.get_opportunities_ranking_deadline()
    assert deadline == "2025-05-01"


def test_get_opportunities_ranking_deadline_default(database, deadline_manager):
    """Test default opportunities ranking deadline when no deadline exists."""
    expected = (
        datetime.datetime.strptime(
            deadline_manager.get_student_ranking_deadline(), "%Y-%m-%d"
        )
        + datetime.timedelta(weeks=1)
    ).strftime("%Y-%m-%d")

    deadline = deadline_manager.get_opportunities_ranking_deadline()
    assert deadline == expected
    assert database.get_one_by_field("deadline", "type", 2)["deadline"] == expected


def test_is_past_opportunities_ranking_deadline(deadline_manager, database):
    """Test checking if the opportunities ranking deadline has passed."""
    database.insert("deadline", {"type": 2, "deadline": "2024-05-01"})

    # Past date
    result = deadline_manager.is_past_opportunities_ranking_deadline()
    assert result

    # Future date
    database.update_one_by_field(
        "deadline",
        "type",
        2,
        {
            "deadline": (
                datetime.datetime.now() + datetime.timedelta(weeks=1)
            ).strftime("%Y-%m-%d")
        },
    )
    result = deadline_manager.is_past_opportunities_ranking_deadline()
    assert not result


def test_update_deadlines_invalid_format(deadline_manager, app):
    """Test invalid date format in update_deadlines."""
    invalid_format = "invalid-date"
    with app.test_request_context():
        response = deadline_manager.update_deadlines(
            invalid_format, "2025-03-01", "2025-04-01"
        )
    assert response[1] == 400
    assert response[0].json["error"] == "Invalid deadline format. Use YYYY-MM-DD."


def test_update_deadlines_conflicting_deadlines(deadline_manager, app):
    """Test when one deadline is after another (conflicting)."""
    with app.test_request_context():
        response = deadline_manager.update_deadlines(
            "2025-04-01", "2025-03-01", "2025-05-01"
        )
    assert response[1] == 400
    assert (
        response[0].json["error"]
        == "Details deadline cannot be later than Student Ranking deadline."
    )


def test_update_deadlines_success(deadline_manager, database, app):
    """Test successful update of deadlines in the database."""
    database.insert("deadline", {"type": 0, "deadline": "2024-03-01"})
    database.insert("deadline", {"type": 1, "deadline": "2024-04-01"})
    database.insert("deadline", {"type": 2, "deadline": "2024-05-01"})
    with app.test_request_context():
        response = deadline_manager.update_deadlines(
            "2025-03-01", "2025-04-01", "2025-05-01"
        )
    assert response[1] == 200
    assert response[0].json["message"] == "All deadlines updated successfully"

    # Check that the deadlines were updated correctly in the database
    deadline = database.get_one_by_field("deadline", "type", 0)
    assert deadline["deadline"] == "2025-03-01"

    deadline = database.get_one_by_field("deadline", "type", 1)
    assert deadline["deadline"] == "2025-04-01"

    deadline = database.get_one_by_field("deadline", "type", 2)
    assert deadline["deadline"] == "2025-05-01"
