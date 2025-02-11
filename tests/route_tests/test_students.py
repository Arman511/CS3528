"""Test for the students route."""

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
from unittest.mock import patch
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

    deadlines = DATABASE.get_all("deadline")
    DATABASE.delete_all("deadline")

    students = DATABASE.get_all("students")
    DATABASE.delete_all("students")

    courses = DATABASE.get_all("courses")
    DATABASE.delete_all("courses")

    modules = DATABASE.get_all("modules")
    DATABASE.delete_all("modules")

    skills = DATABASE.get_all("skills")
    DATABASE.delete_all("skills")

    employers = DATABASE.get_all("employers")
    DATABASE.delete_all("employers")

    opportunities = DATABASE.get_all("opportunities")
    DATABASE.delete_all("opportunities")

    yield DATABASE

    DATABASE.delete_all("deadline")
    for deadline in deadlines:
        DATABASE.insert("deadline", deadline)
    DATABASE.delete_all("students")

    for student in students:
        DATABASE.insert("students", student)

    DATABASE.delete_all("courses")
    for course in courses:
        DATABASE.insert("courses", course)

    DATABASE.delete_all("modules")
    for module in modules:
        DATABASE.insert("modules", module)

    DATABASE.delete_all("skills")
    for skill in skills:
        DATABASE.insert("skills", skill)

    DATABASE.delete_all("employers")
    for employer in employers:
        DATABASE.insert("employers", employer)

    DATABASE.delete_all("opportunities")
    for opportunity in opportunities:
        DATABASE.insert("opportunities", opportunity)

    # Cleanup code
    DATABASE.connection.close()


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
    }

    database.insert("students", student)
    data = {"student_id": "11111111", "password": student["_id"]}

    url = "/students/login"
    client.post(
        url,
        data=data,
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
    data = {"student_id": "11111111", "password": student["_id"]}

    url = "/students/login"
    client.post(
        url,
        data=data,
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

    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "Company 1",
        "email": "dummy@dummy.com",
    }

    database.insert("employers", employer)

    opportunity1 = {
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
    }

    opportunity2 = {
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
    }

    opportunity3 = {
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
    }

    opportunity4 = {
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
    }

    database.insert("opportunities", opportunity1)
    database.insert("opportunities", opportunity2)
    database.insert("opportunities", opportunity3)
    database.insert("opportunities", opportunity4)

    database.insert("students", student)
    data = {"student_id": "11111111", "password": student["_id"]}

    url = "/students/login"
    client.post(
        url,
        data=data,
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
