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

os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def client():
    """Fixture to create a test client."""
    from ...app import app  # pylint: disable=import-outside-toplevel

    app.config["TESTING"] = True
    return app.test_client()


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

    # Cleanup code

    DATABASE.connection.close()


@pytest.fixture()
def user_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a user."""
    database.add_table("users")
    database.delete_all_by_field("users", "email", "dummy@dummy.com")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha256.hash("dummy"),
    }

    database.insert("users", user)

    url = "/user/login"
    client.post(
        url,
        data={
            "email": "dummy@dummy.com",
            "password": "dummy",
        },
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    # Cleanup code
    database.delete_all_by_field("skills", "skill_name", "Test Skill")

    database.delete_all_by_field("users", "email", "dummy@dummy.com")


@pytest.fixture()
def student_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a student."""
    database.add_table("students")
    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": uuid.uuid4().hex,
        "first_name": "dummy",
        "last_name": "dummy",
        "email": "dummy@dummy.com",
        "student_id": "123456",
    }

    database.insert("students", student)

    url = "/students/login"

    client.post(
        url,
        data={
            "student_id": "123456",
            "password": student["_id"],
        },
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    # Cleanup code
    database.delete_all_by_field("skills", "skill_name", "Test Skill")

    database.delete_all_by_field("students", "email", "dummy@dummy.com")


@pytest.fixture()
def sample_skill(database):
    """Fixture to create a sample course."""
    yield {
        "_id": "123",
        "skill_name": "Test Skill",
        "skill_description": "Test Skill Description",
    }
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_add_skill(user_logged_in_client, database, sample_skill):
    """Test adding a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": sample_skill["skill_name"],
            "skill_description": sample_skill["skill_description"],
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    assert database.get_one_by_field("skills", "skill_name", "Test Skill") is not None
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_delete_skill(user_logged_in_client, database, sample_skill):
    """Test deleting a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "_id", "123")

    database.insert("skills", sample_skill)
    url = f"/skills/delete?skill_id={sample_skill['_id']}"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 200
    assert database.get_one_by_id("skills", sample_skill["_id"]) is None
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "_id", "123")


def test_delete_skill_nonexistent(user_logged_in_client):
    """Test deleting a nonexistent skill."""
    url = "/skills/delete?skill_id=nonexistent_id"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 404
    assert response.json["error"] == "Skill not found"


def test_add_skill_missing_name_field(user_logged_in_client, database):
    """Test adding a skill with missing fields."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")

    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "",
            "skill_description": "Programming language",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_add_skill_missing_description_field(user_logged_in_client, database):
    """Test adding a skill with missing fields."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "python",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_add_skill_missing_fields(user_logged_in_client, database):
    """Test adding a skill with missing fields."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_list_skills(user_logged_in_client, database, sample_skill):
    """Test listing skills."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.insert("skills", sample_skill)
    url = "/skills/search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200
    database.delete_all_by_field("skills", "skill_name", "Test Skill")


def test_add_skill_duplicate(user_logged_in_client, database, sample_skill):
    """Test adding a duplicate skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "_id", "123")

    database.insert("skills", sample_skill)
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": sample_skill["skill_name"],
            "skill_description": sample_skill["skill_description"],
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Skill already in database"
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "_id", "123")


def test_update_skill_nonexistent(user_logged_in_client, database):
    """Test updating a nonexistent skill."""
    url = "/skills/update"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_id": "nonexistent_id",
            "skill_name": "Nonexistent Skill",
            "skill_description": "Nonexistent description",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 404
    assert response.json["error"] == "Skill not found"


def test_list_skills_empty(user_logged_in_client, database):
    """Test listing skills when no skills exist."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    url = "/skills/search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_approve_skill_nonexistent(user_logged_in_client, database):
    """Test approving a nonexistent skill."""
    url = "/skills/approve_skill?attempt_skill_id=nonexistent_id"
    response = user_logged_in_client.post(
        url,
        json={"skill_description": "Approved description"},
        content_type="application/json",
    )
    assert response.status_code == 404
    assert response.json["error"] == "Attempted skill not found"


def test_reject_skill_nonexistent(user_logged_in_client, database):
    """Test rejecting a nonexistent skill."""
    url = "/skills/reject_skill?attempt_skill_id=nonexistent_id"
    response = user_logged_in_client.post(url)
    assert response.status_code == 404
    assert response.json["error"] == "Attempted skill not found"


def test_update_skill(user_logged_in_client, database, sample_skill):
    """Test updating a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "skill_name", "Python updated")
    database.insert("skills", sample_skill)
    url = "/skills/update"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_id": sample_skill["_id"],
            "skill_name": "Python Updated",
            "skill_description": "Updated description",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    updated_skill = database.get_one_by_id("skills", sample_skill["_id"])
    assert updated_skill["skill_name"] == "Python updated"
    assert updated_skill["skill_description"] == "Updated description"

    database.delete_by_id("skills", sample_skill["_id"])


def test_already_has_description_approve_skill(user_logged_in_client, database):
    """Test approving a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test skill",
            "skill_description": "Programming language",
            "used": 6,
        },
    )
    url = f"/skills/approve_skill?attempt_skill_id={attempt_skill_id}"
    response = user_logged_in_client.post(
        url,
        json={"skill_description": "Approved description"},
        content_type="application/json",
    )
    assert response.status_code == 200
    approved_skill = database.get_one_by_id("skills", attempt_skill_id)
    assert approved_skill is not None
    assert approved_skill["skill_description"] == "Approved description"
    database.delete_by_id("skills", attempt_skill_id)
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")


def test_already_has_no_description_approve_skill(user_logged_in_client, database):
    """Test approving a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test skill",
            "used": 6,
        },
    )
    url = f"/skills/approve_skill?attempt_skill_id={attempt_skill_id}"
    response = user_logged_in_client.post(
        url,
        json={"skill_description": "Approved description"},
        content_type="application/json",
    )
    assert response.status_code == 200
    approved_skill = database.get_one_by_id("skills", attempt_skill_id)
    assert approved_skill is not None
    assert approved_skill["skill_description"] == "Approved description"
    database.delete_by_id("skills", attempt_skill_id)
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")


def test_reject_skill(user_logged_in_client, database):
    """Test rejecting a skill."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test Skill",
            "skill_description": "Programming language",
        },
    )
    url = f"/skills/reject_skill?attempt_skill_id={attempt_skill_id}"
    response = user_logged_in_client.post(url)
    assert response.status_code == 200
    rejected_skill = database.get_one_by_id("attempted_skills", attempt_skill_id)
    assert rejected_skill is None

    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")
    database.delete_by_id("skills", attempt_skill_id)


def test_update_attempted_skill_get(user_logged_in_client, database):
    """Test GET request to update attempted skill."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test Skill",
            "skill_description": "Test description",
        },
    )

    url = f"/skills/update_attempted_skill?attempt_skill_id={attempt_skill_id}"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200
    assert b"Test Skill" in response.data

    database.delete_by_id("attempted_skills", attempt_skill_id)


def test_update_attempted_skill_post(user_logged_in_client, database):
    """Test POST request to update attempted skill."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Updated Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test Skill",
            "skill_description": "Test description",
        },
    )

    url = "/skills/update_attempted_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_id": attempt_skill_id,
            "skill_name": "Updated Skill",
            "skill_description": "Updated description",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 200
    updated_skill = database.get_one_by_id("attempted_skills", attempt_skill_id)
    assert updated_skill is not None
    assert updated_skill["skill_name"] == "updated skill"
    assert updated_skill["skill_description"] == "Updated description"

    database.delete_by_id("attempted_skills", attempt_skill_id)
    database.delete_all_by_field("attempted_skills", "skill_name", "Updated Skill")
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")
    database.delete_all_by_field("skills", "skill_name", "Updated Skill")


def test_update_attempted_skill_post_missing_fields(user_logged_in_client, database):
    """Test updating an attempted skill with missing fields."""
    url = "/skills/update_attempted_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_id": "some_id",
            "skill_name": "",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"


def test_update_attempted_skill_get_nonexistent(user_logged_in_client):
    """Test GET request for a nonexistent attempted skill."""
    url = "/skills/update_attempted_skill?attempt_skill_id=nonexistent_id"
    response = user_logged_in_client.get(url, follow_redirects=True)
    assert response.status_code == 404


def test_search_attempt_skills(user_logged_in_client, database):
    """Test searching for attempted skills."""
    url = "/skills/attempted_skill_search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_search_attempt_skills_empty(user_logged_in_client, database):
    """Test searching for attempted skills when none exist."""
    current_attempted_skills = database.get_all("attempted_skills")
    database.delete_all("attempted_skills")

    url = "/skills/attempted_skill_search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200

    for skill in current_attempted_skills:
        database.insert("attempted_skills", skill)


def test_search_attempt_skills(user_logged_in_client, database):
    """Test searching for attempted skills."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    attempt_skill_id = uuid.uuid4().hex
    database.insert(
        "attempted_skills",
        {
            "_id": attempt_skill_id,
            "skill_name": "Test Skill",
            "skill_description": "Test description",
        },
    )

    url = "/skills/attempted_skill_search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200
    assert b"Test Skill" in response.data

    database.delete_by_id("attempted_skills", attempt_skill_id)


def test_search_attempt_skills_empty(user_logged_in_client, database):
    """Test searching for attempted skills when none exist."""
    database.delete_all_by_field("attempted_skills", "skill_name", "Test Skill")

    url = "/skills/attempted_skill_search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_update_skill_get(user_logged_in_client, database):
    """Test GET request for updating a skill."""
    database.delete_all_by_field("skills", "skill_name", "Test Skill")

    skill_id = uuid.uuid4().hex
    database.insert(
        "skills",
        {
            "_id": skill_id,
            "skill_name": "Test Skill",
            "skill_description": "Test description",
        },
    )

    url = f"/skills/update?skill_id={skill_id}"
    response = user_logged_in_client.get(url)
    print(response.data)
    assert response.status_code == 200
    assert b"Test Skill" in response.data

    database.delete_by_id("skills", skill_id)


def test_update_skill_post_missing_fields(user_logged_in_client):
    """Test updating a skill with missing fields."""
    url = "/skills/update"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_id": "some_id",
            "skill_name": "",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Missing fields"


def test_update_skill_get_nonexistent(user_logged_in_client):
    """Test GET request for a nonexistent skill."""
    url = "/skills/update?skill_id=nonexistent_id"
    response = user_logged_in_client.get(url, follow_redirects=True)
    assert response.status_code == 404


def test_attempt_add_skill_student(student_logged_in_client, database):
    """Test attempting to add a skill to a student."""
    database.delete_all_by_field("attempted_skills", "skill_name", "test skill")

    url = "/skills/attempt_add_skill_student"
    response = student_logged_in_client.post(
        url,
        json={"skill_name": "Test Skill"},
        content_type="application/json",
    )
    assert response.status_code == 200
    attempted_skill = database.get_one_by_field(
        "attempted_skills", "skill_name", "test skill"
    )
    assert attempted_skill is not None

    database.delete_all_by_field("attempted_skills", "skill_name", "test skill")


def test_attempt_add_skill_student_missing_fields(student_logged_in_client):
    """Test attempting to add a skill to a student with missing fields."""
    url = "/skills/attempt_add_skill_student"
    response = student_logged_in_client.post(
        url,
        json={"skill_name": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.json["error"] == "Missing skill name"


def test_get_skill_page(user_logged_in_client):
    """Test getting the skill page."""
    url = "/skills/add_skill"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_get_skills_page(user_logged_in_client):
    """Test getting the skill page."""
    url = "/skills/search"
    response = user_logged_in_client.get(url)
    assert response.status_code == 200


def test_delete_skill_no_skill_id(user_logged_in_client):
    """Test deleting a skill without providing skill ID."""
    url = "/skills/delete"
    response = user_logged_in_client.delete(url)
    assert response.status_code == 400
    assert response.json["error"] == "Missing skill ID"


def test_one_empty_field_add_skill(user_logged_in_client):
    """Test adding a skill with one empty field."""
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "Test Skill",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"

    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "",
            "skill_description": "Test Skill Description",
        },
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"


def test_empty_field_add_skill(user_logged_in_client):
    """Test adding a skill with empty fields."""
    url = "/skills/add_skill"
    response = user_logged_in_client.post(
        url,
        data={
            "skill_name": "",
            "skill_description": "",
        },
        content_type="application/x-www-form-urlencoded",
    )
    assert response.status_code == 400
    assert response.json["error"] == "One of the inputs is blank"
