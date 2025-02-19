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
import pytest
from dotenv import load_dotenv

from core.database_mongo_manager import DatabaseMongoManager

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
    skills = DATABASE.get_all("skills")
    attempted_skills = DATABASE.get_all("attempted_skills")
    DATABASE.delete_all("skills")
    DATABASE.delete_all("attempted_skills")
    yield DATABASE

    for skill in skills:
        DATABASE.insert("skills", skill)
    for skill in attempted_skills:
        DATABASE.insert("attempted_skills", skill)
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


def test_find_skill_by_id(database, sample_skill, app, skill_model):
    """Test find_skill method by ID."""

    database.insert("skills", sample_skill)

    skill_id = sample_skill["_id"]

    with app.app_context():
        with app.test_request_context():
            skill = skill_model.find_skill(None, skill_id)
            assert skill["_id"] == sample_skill["_id"]
            assert skill["skill_name"] == sample_skill["skill_name"]
            assert skill["skill_description"] == sample_skill["skill_description"]

    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_add_skill(database, skill_model, app):
    """Test add_skill method."""
    database.delete_all_by_field("skills", "skill_name", "New Skill")

    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "New Skill",
        "skill_description": "New Skill Description",
    }

    with app.app_context():
        with app.test_request_context():
            response = skill_model.add_skill(sample_skill)[0]
            assert response.status_code == 200
            assert database.get_one_by_id("skills", sample_skill["_id"]) is not None

    database.delete_all_by_field("skills", "skill_name", "New Skill")


def test_delete_skill(database, skill_model, app):
    """Test delete_skill method."""
    database.delete_all_by_field("skills", "skill_name", "Delete Skill")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Delete Skill",
        "skill_description": "Skill to delete",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.delete_skill(sample_skill["_id"])[0]
            assert response.status_code == 200
            assert database.get_one_by_id("skills", sample_skill["_id"]) is None

    database.delete_all_by_field("skills", "skill_name", "Delete Skill")


def test_get_skill_by_id(database, skill_model, app):
    """Test get_skill_by_id method."""
    database.delete_all_by_field("skills", "skill_name", "Find Skill")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Find Skill",
        "skill_description": "Skill to find",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            skill = skill_model.get_skill_by_id(sample_skill["_id"])
            assert skill is not None
            assert skill["skill_name"] == "Find Skill"

    database.delete_all_by_field("skills", "skill_name", "Find Skill")


def test_get_skills(database, skill_model, app):
    """Test get_skills method."""
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "List Skill",
        "skill_description": "Skill in list",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            skills = skill_model.get_skills()
            assert any(skill["skill_name"] == "List Skill" for skill in skills)

    database.delete_all_by_field("skills", "skill_name", "List Skill")


def test_update_skill(database, skill_model, app):
    """Test update_skill method."""
    database.delete_all_by_field("skills", "skill_name", "Updated Skill")
    database.delete_all_by_field("skills", "skill_name", "Old Skill")
    database.delete_all_by_field("skills", "skill_name", "Updated skill")
    database.delete_all_by_field("skills", "skill_name", "Old skill")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Old Skill",
        "skill_description": "Old description",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.update_skill(
                sample_skill["_id"], "Updated Skill", "Updated description"
            )[0]
            assert response.status_code == 200
            updated_skill = database.get_one_by_id("skills", sample_skill["_id"])
            assert updated_skill["skill_name"] == "Updated skill"

    database.delete_all_by_field("skills", "skill_name", "Updated Skill")


def test_attempt_add_skill(database, skill_model, app):
    """Test attempt_add_skill method."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")
    with app.app_context():
        with app.test_request_context():
            response = skill_model.attempt_add_skill("Attempted Skill")[0]
            assert response.status_code == 200
            assert (
                database.get_one_by_field(
                    "attempted_skills", "skill_name", "Attempted Skill"
                )
                is not None
            )

    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")


def test_approve_skill(database, skill_model, app):
    """Test approve_skill method."""
    database.delete_all_by_field("skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("skills", "skill_name", "Approve skill")
    attempted_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Approve Skill",
        "used": 1,
    }
    database.insert("attempted_skills", attempted_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.approve_skill(
                attempted_skill["_id"], "Approved Description"
            )[0]
            assert response.status_code == 200
            assert database.get_one_by_id("skills", attempted_skill["_id"]) is not None

    database.delete_all_by_field("skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("skills", "skill_name", "Approve skill")


def test_reject_skill(database, skill_model, app):
    """Test reject_skill method."""
    database.delete_all_by_field("skills", "skill_name", "Reject Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Reject Skill")
    attempted_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Reject Skill",
        "used": 1,
    }
    database.insert("attempted_skills", attempted_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.reject_skill(attempted_skill["_id"])[0]
            assert response.status_code == 200
            assert (
                database.get_one_by_id("attempted_skills", attempted_skill["_id"])
                is None
            )

    database.delete_all_by_field("attempted_skills", "skill_name", "Reject Skill")


def test_update_skill_name_conflict(database, skill_model, app):
    """Test update_skill method with name conflict."""
    database.delete_all_by_field("skills", "skill_name", "Conflict Skill")
    database.delete_all_by_field("skills", "skill_name", "Existing Skill")

    existing_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Existing Skill",
        "skill_description": "Existing description",
    }
    database.insert("skills", existing_skill)

    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Conflict Skill",
        "skill_description": "Conflict description",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.update_skill(
                sample_skill["_id"], "Existing Skill", "Updated description"
            )
            assert response[1] == 400
            assert response[0].json["error"] == "Skill name already in use"

    database.delete_all_by_field("skills", "skill_name", "Conflict Skill")
    database.delete_all_by_field("skills", "skill_name", "Existing Skill")


def test_update_invalid_skill(database, skill_model, app, sample_skill):
    """Test update_skill method with invalid skill."""
    with app.app_context():
        with app.test_request_context():
            response = skill_model.update_skill(
                sample_skill["_id"], "Updated Skill", "Updated description"
            )
            assert response[1] == 404
            assert response[0].json["error"] == "Skill not found"

    database.delete_all_by_field("skills", "skill_name", "Invalid Skill")


def test_find_skill_return_none(skill_model, app):
    """Test find_skill method returns None for non-existent skill."""
    with app.app_context():
        with app.test_request_context():
            skill = skill_model.find_skill(skill_name="NonExistentSkill")
            assert skill is None

            skill = skill_model.find_skill(skill_id="nonexistentid")
            assert skill is None


def test_add_existing_skill(database, skill_model, app):
    """Test add_skill method with existing skill."""
    database.delete_all_by_field("skills", "skill_name", "Existing Skill")

    existing_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Existing Skill",
        "skill_description": "Existing description",
    }
    database.insert("skills", existing_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.add_skill(existing_skill)
            assert response[1] == 400
            assert response[0].json["error"] == "Skill already in database"

    database.delete_all_by_field("skills", "skill_name", "Existing Skill")


def test_delete_skill_with_students(database, skill_model, app):
    """Test delete_skill method with students having the skill."""
    database.delete_all_by_field("skills", "skill_name", "Skill to Delete")
    database.delete_all_by_field("students", "email", "student@example.com")

    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Skill to Delete",
        "skill_description": "Skill to be deleted",
    }
    database.insert("skills", sample_skill)

    sample_student = {
        "_id": uuid.uuid4().hex,
        "email": "student@example.com",
        "skills": [sample_skill["_id"]],
    }
    database.insert("students", sample_student)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.delete_skill(sample_skill["_id"])[0]
            assert response.status_code == 200
            assert database.get_one_by_id("skills", sample_skill["_id"]) is None
            updated_student = database.get_one_by_id("students", sample_student["_id"])
            assert sample_skill["_id"] not in updated_student["skills"]

    database.delete_all_by_field("skills", "skill_name", "Skill to Delete")
    database.delete_all_by_field("students", "email", "student@example.com")


def test_delete_nonexistent_skill(skill_model, app):
    """Test delete_skill method with non-existent skill."""
    with app.app_context():
        with app.test_request_context():
            response = skill_model.delete_skill("nonexistentid")
            assert response[1] == 404
            assert response[0].json["error"] == "Skill not found"


def test_get_skill_by_id_returns_none(skill_model, app):
    """Test get_skill_by_id method returns None for non-existent skill."""
    with app.app_context():
        with app.test_request_context():
            skill = skill_model.get_skill_by_id("nonexistentid")
            assert skill is None


def test_get_skill_name_by_id(database, skill_model, app):
    """Test get_skill_name_by_id method."""
    database.delete_all_by_field("skills", "skill_name", "Skill Name")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Skill Name",
        "skill_description": "Skill Description",
    }
    database.insert("skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            skill_name = skill_model.get_skill_name_by_id(sample_skill["_id"])
            assert skill_name == "Skill Name"

            skill_name = skill_model.get_skill_name_by_id("nonexistentid")
            assert skill_name is None

    database.delete_all_by_field("skills", "skill_name", "Skill Name")


def test_get_skills_map(database, skill_model, app):
    """Test get_skills_map method."""
    database.delete_all_by_field("skills", "skill_name", "Skill 1")
    database.delete_all_by_field("skills", "skill_name", "Skill 2")
    sample_skill_1 = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Skill 1",
        "skill_description": "Description 1",
    }
    sample_skill_2 = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Skill 2",
        "skill_description": "Description 2",
    }
    database.insert("skills", sample_skill_1)
    database.insert("skills", sample_skill_2)

    with app.app_context():
        with app.test_request_context():
            skills_map = skill_model.get_skills_map()
            assert sample_skill_1["_id"] in skills_map
            assert sample_skill_2["_id"] in skills_map
            assert skills_map[sample_skill_1["_id"]]["skill_name"] == "Skill 1"
            assert skills_map[sample_skill_2["_id"]]["skill_name"] == "Skill 2"

    database.delete_all_by_field("skills", "skill_name", "Skill 1")
    database.delete_all_by_field("skills", "skill_name", "Skill 2")


def test_attempt_add_existing_skill(database, skill_model, app):
    """Test attempt_add_skill method with existing skill."""
    database.delete_all_by_field(
        "attempted_skills", "skill_name", "Existing Attempted Skill"
    )
    existing_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Existing Attempted Skill",
        "used": 1,
    }
    database.insert("attempted_skills", existing_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.attempt_add_skill("Existing Attempted Skill")[0]
            assert response.status_code == 200
            updated_skill = database.get_one_by_field(
                "attempted_skills", "skill_name", "Existing Attempted Skill"
            )
            assert updated_skill["used"] == 2

    database.delete_all_by_field(
        "attempted_skills", "skill_name", "Existing Attempted Skill"
    )


def test_get_list_attempted_skills(database, skill_model, app):
    """Test get_list_attempted_skills method."""
    current_attempted_skills = database.get_all("attempted_skills")
    database.delete_all("attempted_skills")

    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill 1")
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill 2")

    sample_skill_1 = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Attempted Skill 1",
        "used": 1,
    }
    sample_skill_2 = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Attempted Skill 2",
        "used": 1,
    }
    database.insert("attempted_skills", sample_skill_1)
    database.insert("attempted_skills", sample_skill_2)

    with app.app_context():
        with app.test_request_context():
            attempted_skills = skill_model.get_list_attempted_skills()
            assert len(attempted_skills) == 2
            assert any(
                skill["skill_name"] == "Attempted Skill 1" for skill in attempted_skills
            )
            assert any(
                skill["skill_name"] == "Attempted Skill 2" for skill in attempted_skills
            )

    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill 1")
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill 2")

    for skill in current_attempted_skills:
        database.insert("attempted_skills", skill)


def test_get_attempted_skill_success(database, skill_model, app):
    """Test get_attempted_skill method success."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Attempted Skill",
        "used": 1,
    }
    database.insert("attempted_skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            skill = skill_model.get_attempted_skill(sample_skill["_id"])
            assert skill is not None
            assert skill["skill_name"] == "Attempted Skill"

    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")


def test_get_attempted_skill_failure(database, skill_model, app):
    """Test get_attempted_skill method failure."""
    with app.app_context():
        with app.test_request_context():
            skill = skill_model.get_attempted_skill("nonexistentid")
            assert skill is None


def test_approve_skill_updates_students(database, skill_model, app):
    """Test approve_skill method updates students."""
    database.delete_all_by_field("skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("students", "email", "student@example.com")

    attempted_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Approve Skill",
        "used": 1,
    }
    database.insert("attempted_skills", attempted_skill)

    sample_student = {
        "_id": uuid.uuid4().hex,
        "email": "student@example.com",
        "skills": [],
        "attempted_skills": [attempted_skill["_id"]],
    }
    database.insert("students", sample_student)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.approve_skill(
                attempted_skill["_id"], "Approved Description"
            )[0]
            assert response.status_code == 200
            assert database.get_one_by_id("skills", attempted_skill["_id"]) is not None

            updated_student = database.get_one_by_id("students", sample_student["_id"])
            assert attempted_skill["_id"] in updated_student["skills"]
            assert attempted_skill["_id"] not in updated_student["attempted_skills"]

    database.delete_all_by_field("skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")
    database.delete_all_by_field("students", "email", "student@example.com")


def test_approve_skill_empty_description(database, skill_model, app):
    """Test approve_skill method with empty description."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")
    attempted_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Approve Skill",
        "used": 1,
    }
    database.insert("attempted_skills", attempted_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.approve_skill(attempted_skill["_id"], "")
            assert response[1] == 400
            assert response[0].json["error"] == "Description is empty"

    database.delete_all_by_field("attempted_skills", "skill_name", "Approve Skill")


def test_approve_nonexistent_skill(skill_model, app):
    """Test approve_skill method with non-existent skill."""
    with app.app_context():
        with app.test_request_context():
            response = skill_model.approve_skill("nonexistentid", "Description")
            assert response[1] == 404
            assert response[0].json["error"] == "Attempted skill not found"


def test_reject_skill_updates_students(database, skill_model, app):
    """Test reject_skill method updates students."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Reject Skill")
    database.delete_all_by_field("students", "email", "student@example.com")

    attempted_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Reject Skill",
        "used": 1,
    }
    database.insert("attempted_skills", attempted_skill)

    sample_student = {
        "_id": uuid.uuid4().hex,
        "email": "student@example.com",
        "skills": [],
        "attempted_skills": [attempted_skill["_id"]],
    }
    database.insert("students", sample_student)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.reject_skill(attempted_skill["_id"])[0]
            assert response.status_code == 200
            assert (
                database.get_one_by_id("attempted_skills", attempted_skill["_id"])
                is None
            )

            updated_student = database.get_one_by_id("students", sample_student["_id"])
            assert attempted_skill["_id"] not in updated_student["attempted_skills"]

    database.delete_all_by_field("attempted_skills", "skill_name", "Reject Skill")
    database.delete_all_by_field("students", "email", "student@example.com")


def test_reject_nonexistent_skill(skill_model, app):
    """Test reject_skill method with non-existent skill."""
    with app.app_context():
        with app.test_request_context():
            response = skill_model.reject_skill("nonexistentid")
            assert response[1] == 404
            assert response[0].json["error"] == "Attempted skill not found"


def test_update_attempt_skill(database, skill_model, app):
    """Test update_attempt_skill method."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")
    sample_skill = {
        "_id": uuid.uuid4().hex,
        "skill_name": "Attempted Skill",
        "skill_description": "Old Description",
    }
    database.insert("attempted_skills", sample_skill)

    with app.app_context():
        with app.test_request_context():
            response = skill_model.update_attempt_skill(
                sample_skill["_id"], "Updated Skill", "Updated Description"
            )[0]
            assert response.status_code == 200
            updated_skill = database.get_one_by_id(
                "attempted_skills", sample_skill["_id"]
            )
            assert updated_skill["skill_name"] == "Updated Skill"
            assert updated_skill["skill_description"] == "Updated Description"

    database.delete_all_by_field("attempted_skills", "skill_name", "Updated Skill")


def test_update_attempt_skill_invalid_id(skill_model, app):
    """Test update_attempt_skill method with invalid skill ID."""
    with app.app_context():
        with app.test_request_context():
            response = skill_model.update_attempt_skill(
                "nonexistentid", "Updated Skill", "Updated Description"
            )
            assert response[1] == 404
            assert response[0].json["error"] == "Skill not found"
