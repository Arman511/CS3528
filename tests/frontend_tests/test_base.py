import os
import uuid
from dotenv import load_dotenv
import pytest
from selenium.webdriver.common.by import By
from passlib.hash import pbkdf2_sha512
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from core import shared
from core.database_mongo_manager import DatabaseMongoManager

# sys.path.append(
#     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# )
os.environ["IS_TEST"] = "True"

load_dotenv()

PORT = 5000


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        shared.getenv("MONGO_URI"),
        shared.getenv("MONGO_DB_TEST", "cs3528_testing"),
    )

    yield DATABASE

    DATABASE.connection.close()


def test_base_page(chrome_browser, flask_server):
    chrome_browser.get("http://127.0.0.1:5000/students/login")
    assert chrome_browser.title == "SkillPilot - Student Login"


def test_student_login_page(chrome_browser, flask_server):
    chrome_browser.get("http://127.0.0.1:5000/students/login")
    assert chrome_browser.title == "SkillPilot - Student Login"


@pytest.fixture
def placement_member(database):
    users = database.get_all("users")
    database.delete_all("users")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "dummy",
        "email": "dummy@dummy.com",
        "password": pbkdf2_sha512.hash("dummy"),
    }
    database.insert("users", user)
    yield user
    database.delete_all("users")
    for user in users:
        database.insert("users", user)


@pytest.fixture
def student_member(database):
    students = database.get_all("students")
    database.delete_all("students")
    modules = database.get_all("modules")
    database.delete_all("modules")
    skills = database.get_all("skills")
    database.delete_all("skills")
    opportunities = database.get_all("opportunities")
    database.delete_all("opportunities")
    employers = database.get_all("employers")
    database.delete_all("employers")
    courses = database.get_all("courses")
    database.delete_all("courses")

    student = {
        "_id": uuid.uuid4().hex,
        "first_name": "Olivia",
        "last_name": "Brown",
        "email": "dummy@example.com",
        "student_id": "12345678",
        "attempted_skills": [],
        "comments": "",
        "course": "DU78",
        "has_car": "false",
        "modules": ["DUMMY1", "DUMMY2"],
        "placement_duration": [
            "6_months",
            "1_month",
            "12_months",
        ],
        "skills": [
            "9a5f8be14beb4b138ca5376d295d2abc",
            "f71a49ed9614404380b34b69083b21cf",
        ],
        "preferences": [
            "c31519139b2e4497912c73b4a1ecf86d",
            "ea7dd8d0c2394885a78fe761ae64ea1e",
        ],
    }
    database.insert("students", student)
    module1 = {
        "module_id": "DUMMY1",
        "module_name": "DUMMY",
        "module_description": "DUMMY",
    }
    database.insert("modules", module1)
    module2 = {
        "module_id": "DUMMY2",
        "module_name": "DUMMY",
        "module_description": "DUMMY",
    }
    database.insert("modules", module2)
    skill1 = {
        "skill_id": "9a5f8be14beb4b138ca5376d295d2abc",
        "skill_name": "DUMMY2",
        "skill_description": "DUMMY",
    }
    database.insert("skills", skill1)
    skill2 = {
        "skill_id": "f71a49ed9614404380b34b69083b21cf",
        "skill_name": "DUMMY2",
        "skill_description": "DUMMY",
    }
    database.insert("skills", skill2)
    preference1 = {
        "_id": "c31519139b2e4497912c73b4a1ecf86d",
        "title": "DUMMY1",
        "description": "DUMMY",
        "url": "DUMMY",
        "employer_id": "DUMMY",
        "location": "DUMMY",
        "modules_required": ["DUMMY1", "DUMMY2"],
        "courses_required": ["DU78", "DU79"],
        "spots_available": 1,
        "duration": "6_months",
    }
    database.insert("opportunities", preference1)
    preference2 = {
        "_id": "ea7dd8d0c2394885a78fe761ae64ea1e",
        "title": "DUMMY2",
        "description": "DUMMY",
        "url": "DUMMY",
        "employer_id": "DUMMY",
        "location": "DUMMY",
        "modules_required": ["DUMMY1", "DUMMY2"],
        "courses_required": ["DU78", "DU79"],
        "spots_available": 1,
        "duration": "6_months",
    }
    database.insert("opportunities", preference2)
    employer = {
        "_id": "DUMMY",
        "company_name": "DUMMY",
        "email": "DUMMY",
    }
    database.insert("employers", employer)
    course = {
        "_id": "DU78",
        "course_id": "DU78",
        "course_name": "DUMMY",
        "course_description": "DUMMY",
    }
    database.insert("courses", course)
    yield student

    database.delete_all("students")
    database.delete_all("modules")
    database.delete_all("skills")
    database.delete_all("opportunities")
    database.delete_all("employers")
    database.delete_all("courses")
    for student in students:
        database.insert("students", student)
    for module in modules:
        database.insert("modules", module)
    for skill in skills:
        database.insert("skills", skill)
    for opportunity in opportunities:
        database.insert("opportunities", opportunity)
    for employer in employers:
        database.insert("employers", employer)
    for course in courses:
        database.insert("courses", course)


@pytest.fixture
def employer_member(database):
    employers = database.get_all("employers")
    database.delete_all("employers")

    employer = {
        "_id": uuid.uuid4().hex,
        "company_name": "dummy",
        "email": "dummy@dummy.com",
    }

    database.insert("employers", employer)
    yield employer

    database.delete_all("employers")
    for employer in employers:
        database.insert("employers", employer)


def test_placement_team_login(chrome_browser, flask_server, database, placement_member):
    chrome_browser.get("http://127.0.0.1:5000/user/login")
    chrome_browser.find_element(By.ID, "agree-btn").click()
    chrome_browser.find_element(By.NAME, "email").send_keys("dummy@dummy.com")
    chrome_browser.find_element(By.NAME, "password").send_keys("dummy")
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/user/home")
    )

    assert chrome_browser.current_url == "http://127.0.0.1:5000/user/home"
