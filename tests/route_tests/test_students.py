"""Test for the students route."""

# pylint: disable=redefined-outer-name
# flake8: noqa: F811

import os
import sys
import uuid
from unittest.mock import patch
from itsdangerous import URLSafeSerializer
import pytest
from dotenv import load_dotenv

# Add the root directory to the Python path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core import shared
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

    database = DatabaseMongoManager(
        shared.getenv("MONGO_URI"), shared.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    collections = {
        "deadline": database.get_all("deadline"),
        "students": database.get_all("students"),
        "courses": database.get_all("courses"),
        "modules": database.get_all("modules"),
        "skills": database.get_all("skills"),
        "attempted_skills": database.get_all("attempted_skills"),
        "employers": database.get_all("employers"),
        "opportunities": database.get_all("opportunities"),
    }

    for collection in collections:
        database.delete_all(collection)

    yield database

    for collection, items in collections.items():
        database.delete_all(collection)
        for item in items:
            database.insert(collection, item)

    # Cleanup code
    database.connection.close()


@pytest.fixture()
def student_logged_in_client(client, database: DatabaseMongoManager):
    """Fixture to login a student."""
    database.add_table("students")
    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": uuid.uuid1().hex,
        "first_name": "Dummy",
        "last_name": "Student",
        "email": "dummy@dummy.com",
        "student_id": "11111111",
        "modules": [],
    }

    database.insert("students", student)
    url = "/students/login"

    client.post(
        url,
        data={
            "student_id": "11111111",
        },
        content_type="application/x-www-form-urlencoded",
    )
    otp_serializer = URLSafeSerializer(str(shared.getenv("SECRET_KEY", "secret")))

    with client.session_transaction() as session:
        otp = otp_serializer.loads(session["OTP"])

    client.post(
        "/students/otp",
        data={"otp": otp},
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    database.delete_all_by_field("students", "email", "dummy@dummy.com")


@pytest.fixture()
def student_logged_in_client_after_details(client, database: DatabaseMongoManager):
    """Fixture to login a student."""
    database.add_table("students")
    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": uuid.uuid1().hex,
        "first_name": "Dummy",
        "last_name": "Student",
        "email": "dummy@dummy.com",
        "student_id": "11111111",
        "attempted_skills": ["cc4e7ecc9a0e11ef8a1a43569002b932"],
        "comments": "Test attempt",
        "course": "G401",
        "has_car": "false",
        "modules": [
            "BI1012",
            "BI1512",
        ],
        "placement_duration": [
            "1_day",
            "1_month",
            "1_week",
            "12_months",
            "3_months",
            "6_months",
        ],
        "skills": [
            "015d0008994611ef8360bec4b589d035",
            "f087df2893d211ef84b1bbe7a6a5be1f",
        ],
    }

    module1 = {
        "_id": "BI1012",
        "module_id": "BI1012",
        "module_name": "Module 1",
        "module_description": "Module 1 description",
    }

    module2 = {
        "_id": "BI1512",
        "module_id": "BI1512",
        "module_name": "Module 2",
        "module_description": "Module 2 description",
    }

    database.insert("modules", module1)
    database.insert("modules", module2)

    course = {
        "_id": "G401",
        "course_id": "G401",
        "course_name": "Course 1",
        "course_description": "Course 1 description",
    }

    database.insert("courses", course)

    skill1 = {
        "_id": "015d0008994611ef8360bec4b589d035",
        "skill_name": "Skill 1",
        "skill_description": "Skill 1 description",
    }

    skill2 = {
        "_id": "f087df2893d211ef84b1bbe7a6a5be1f",
        "skill_name": "Skill 2",
        "skill_description": "Skill 2 description",
    }

    database.insert("skills", skill1)
    database.insert("skills", skill2)

    attempted_skill = {
        "_id": "cc4e7ecc9a0e11ef8a1a43569002b932",
        "skill_name": "Attempted Skill",
        "skill_description": "Attempted Skill description",
        "used": 5,
    }

    database.insert("attempted_skills", attempted_skill)

    database.insert("students", student)
    url = "/students/login"

    client.post(
        url,
        data={
            "student_id": "11111111",
        },
        content_type="application/x-www-form-urlencoded",
    )
    otp_serializer = URLSafeSerializer(str(shared.getenv("SECRET_KEY", "secret")))

    with client.session_transaction() as session:
        otp = otp_serializer.loads(session["OTP"])

    client.post(
        "/students/otp",
        data={"otp": otp},
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("modules", "module_id", "BI1012")
    database.delete_all_by_field("modules", "module_id", "BI1512")
    database.delete_all_by_field("courses", "course_id", "G401")
    database.delete_all_by_field("skills", "skill_name", "Skill 1")
    database.delete_all_by_field("skills", "skill_name", "Skill 2")
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")


@pytest.fixture()
def student_logged_in_client_after_preferences(client, database: DatabaseMongoManager):
    """Fixture to login a student."""
    database.add_table("students")
    database.delete_all_by_field("students", "email", "dummy@dummy.com")

    student = {
        "_id": uuid.uuid1().hex,
        "first_name": "Dummy",
        "last_name": "Student",
        "email": "dummy@dummy.com",
        "student_id": "11111111",
        "attempted_skills": ["cc4e7ecc9a0e11ef8a1a43569002b932"],
        "comments": "Test attempt",
        "course": "G401",
        "has_car": "false",
        "modules": [
            "BI1012",
            "BI1512",
        ],
        "placement_duration": [
            "1_day",
            "1_month",
            "1_week",
            "12_months",
            "3_months",
            "6_months",
        ],
        "skills": [
            "015d0008994611ef8360bec4b589d035",
            "f087df2893d211ef84b1bbe7a6a5be1f",
        ],
        "preferences": [
            "a7f0c09bb90841f783836c6c9e369f6e",
            "c9ac8f2a59224cfb95a043dcf4937f91",
            "8bf8ddf3383240bea1e78f7a3fec36cf",
            "f57b251588c8498cbb9ab3e0fe76846e",
        ],
    }

    modules = [
        {
            "_id": "BI1012",
            "module_id": "BI1012",
            "module_name": "Module 1",
            "module_description": "Module 1 description",
        },
        {
            "_id": "BI1512",
            "module_id": "BI1512",
            "module_name": "Module 2",
            "module_description": "Module 2 description",
        },
    ]

    courses = [
        {
            "_id": "G401",
            "course_id": "G401",
            "course_name": "Course 1",
            "course_description": "Course 1 description",
        }
    ]

    skills = [
        {
            "_id": "015d0008994611ef8360bec4b589d035",
            "skill_name": "Skill 1",
            "skill_description": "Skill 1 description",
        },
        {
            "_id": "f087df2893d211ef84b1bbe7a6a5be1f",
            "skill_name": "Skill 2",
            "skill_description": "Skill 2 description",
        },
    ]

    attempted_skills = [
        {
            "_id": "cc4e7ecc9a0e11ef8a1a43569002b932",
            "skill_name": "Attempted Skill",
            "skill_description": "Attempted Skill description",
            "used": 5,
        }
    ]

    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "Company 1",
        "email": "dummy@dummy.com",
    }

    opportunities = [
        {
            "_id": "a7f0c09bb90841f783836c6c9e369f6e",
            "title": "Opportunity 1",
            "description": "Assist customers with inquiries, complaints, and product information.",
            "url": "www.anatomyassistant.com",
            "employer_id": employer["_id"],
            "location": "909 Health Sciences Blvd",
            "modules_required": [],
            "courses_required": [
                "H205",
                "WV63",
                "G401",
                "M1N4",
                "C901",
                "LL63",
                "WX33",
                "G403",
            ],
            "spots_available": 7,
            "duration": "1_month",
        },
        {
            "_id": "c9ac8f2a59224cfb95a043dcf4937f91",
            "title": "Opportunity 2",
            "description": "Assist customers with inquiries, complaints, and product information.",
            "url": "www.anatomyassistant.com",
            "employer_id": employer["_id"],
            "location": "909 Health Sciences Blvd",
            "modules_required": [],
            "courses_required": [
                "H205",
                "WV63",
                "G401",
            ],
            "spots_available": 7,
            "duration": "1_month",
        },
        {
            "_id": "8bf8ddf3383240bea1e78f7a3fec36cf",
            "title": "Opportunity 3",
            "description": "Assist customers with inquiries, complaints, and product information.",
            "url": "www.anatomyassistant.com",
            "employer_id": employer["_id"],
            "location": "909 Health Sciences Blvd",
            "modules_required": [],
            "courses_required": [
                "H205",
                "WV63",
                "G401",
            ],
            "spots_available": 7,
            "duration": "1_month",
        },
        {
            "_id": "f57b251588c8498cbb9ab3e0fe76846e",
            "title": "Opportunity 4",
            "description": "Assist customers with inquiries, complaints, and product information.",
            "url": "www.anatomyassistant.com",
            "employer_id": employer["_id"],
            "location": "909 Health Sciences Blvd",
            "modules_required": [],
            "courses_required": [
                "H205",
                "WV63",
                "G401",
            ],
            "spots_available": 7,
            "duration": "1_month",
        },
    ]

    for module in modules:
        database.insert("modules", module)

    for course in courses:
        database.insert("courses", course)

    for skill in skills:
        database.insert("skills", skill)

    for attempted_skill in attempted_skills:
        database.insert("attempted_skills", attempted_skill)

    database.insert("employers", employer)

    for opportunity in opportunities:
        database.insert("opportunities", opportunity)

    database.insert("students", student)
    url = "/students/login"

    client.post(
        url,
        data={
            "student_id": "11111111",
        },
        content_type="application/x-www-form-urlencoded",
    )
    otp_serializer = URLSafeSerializer(str(shared.getenv("SECRET_KEY", "secret")))

    with client.session_transaction() as session:
        otp = otp_serializer.loads(session["OTP"])

    client.post(
        "/students/otp",
        data={"otp": otp},
        content_type="application/x-www-form-urlencoded",
    )

    yield client

    database.delete_all_by_field("students", "email", "dummy@dummy.com")
    database.delete_all_by_field("modules", "module_id", "BI1012")
    database.delete_all_by_field("modules", "module_id", "BI1512")
    database.delete_all_by_field("courses", "course_id", "G401")
    database.delete_all_by_field("skills", "skill_name", "Skill 1")
    database.delete_all_by_field("skills", "skill_name", "Skill 2")
    database.delete_all_by_field("attempted_skills", "skill_name", "Attempted Skill")
    database.delete_all_by_field("employers", "email", "dummy@dummy.com")
    database.delete_all_by_field("opportunities", "title", "Opportunity 1")
    database.delete_all_by_field("opportunities", "title", "Opportunity 2")
    database.delete_all_by_field("opportunities", "title", "Opportunity 3")
    database.delete_all_by_field("opportunities", "title", "Opportunity 4")


def test_student_update_successful(student_logged_in_client):
    """Test student update success route."""
    url = "/students/update_success"

    response = student_logged_in_client.get(url)

    assert response.status_code == 200


def test_past_deadline(student_logged_in_client):
    """Test student update route."""
    url = "/students/passed_deadline"

    response = student_logged_in_client.get(url)

    assert response.status_code == 200


def test_student_details_wrong_student_redirect(student_logged_in_client):
    """Test redirect if student tries to access another student's details."""
    url = "/students/details/123"  # Trying to access details for student 123

    response = student_logged_in_client.get(url)

    assert response.status_code == 302  # Redirect response


def test_student_details_deadline_redirects(student_logged_in_client):
    """Test redirects if deadlines have passed."""
    url = "/students/details/11111111"

    with patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=True
    ):
        response = student_logged_in_client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/students/passed_deadline")

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=True):
        response = student_logged_in_client.get(url, follow_redirects=False)
        assert response.status_code == 302
        assert response.headers["Location"].endswith(
            "/students/rank_preferences/11111111"
        )


def test_student_details_update_post(student_logged_in_client):
    """Test updating student details."""
    url = "/students/details/11111111"

    student_update_data = {
        "comments": "Updated comment",
        "skills": ["Python", "C++"],
        "attempted_skills": ["Django"],
        "has_car": True,
        "placement_duration": ["6_months"],
        "modules": ["AI"],
        "course": "CS",
    }

    response = student_logged_in_client.post(
        url,
        data=student_update_data,
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code == 200


def test_student_details_update_get(student_logged_in_client):
    """Test updating student details."""
    url = "/students/details/11111111"

    with patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=False
    ), patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = student_logged_in_client.get(url)

    assert response.status_code == 200


def test_rank_preference_different_student_id(student_logged_in_client):
    """Test rank preferences route when student is not in session."""
    url = "/students/rank_preferences/123"

    response = student_logged_in_client.get(url)

    assert response.status_code == 302


def test_rank_preferences_deadline_redirects(student_logged_in_client):
    """Test redirects if ranking deadline has passed."""
    url = "/students/rank_preferences/11111111"

    with patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=True
    ):
        response = student_logged_in_client.get(url, follow_redirects=False)
        assert response.status_code == 302


def test_rank_preferences_details_deadline_redirect(student_logged_in_client):
    """Test redirect if student has not completed details."""
    url = "/students/rank_preferences/11111111"

    with patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=False):
        response = student_logged_in_client.get(url, follow_redirects=False)
        assert response.status_code == 302


def test_rank_preferences_update_post(
    student_logged_in_client_after_preferences, database
):
    """Test updating student rank preferences."""
    url = "/students/rank_preferences/11111111"

    with patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=False
    ), patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=True):
        response = student_logged_in_client_after_preferences.post(
            url,
            data={"ranks": "rank_opp3,rank_opp2,rank_opp1"},
            content_type="application/x-www-form-urlencoded",
        )

    assert response.status_code == 200
    assert database.get_one_by_field("students", "student_id", "11111111")[
        "preferences"
    ] == ["opp3", "opp2", "opp1"]
    database.delete_all_by_field("students", "student_id", "11111111")


def test_rank_preferences_update_post_one_ranking(student_logged_in_client, database):
    """Test updating student rank preferences."""
    url = "/students/rank_preferences/11111111"

    mock_opportunities = [
        {"_id": "opp1"},
        {"_id": "opp2"},
        {"_id": "opp3"},
        {"_id": "opp4"},
        {"_id": "opp5"},
        {"_id": "opp6"},
    ]

    with patch(
        "students.routes_student.Student.get_opportunities_by_student",
        return_value=mock_opportunities,
    ), patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=False
    ), patch(
        "app.DEADLINE_MANAGER.is_past_details_deadline", return_value=True
    ):

        response = student_logged_in_client.post(
            url,
            data={"ranks": "rank_opp1"},
            content_type="application/x-www-form-urlencoded",
        )

    assert response.status_code == 400
    assert response.json == {"error": "Please rank at least 5 opportunities"}

    database.delete_all_by_field("students", "student_id", "11111111")


def test_rank_preferences_update_get(student_logged_in_client_after_details):
    """Test updating student rank preferences."""
    url = "/students/rank_preferences/11111111"

    with patch(
        "app.DEADLINE_MANAGER.is_past_student_ranking_deadline", return_value=False
    ), patch("app.DEADLINE_MANAGER.is_past_details_deadline", return_value=True):
        response = student_logged_in_client_after_details.get(url)

    assert response.status_code == 200
