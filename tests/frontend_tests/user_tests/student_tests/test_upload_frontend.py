import os
import uuid

import pytest
from core import shared
from core.database_mongo_manager import DatabaseMongoManager
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha512

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

load_dotenv()
os.environ["IS_TEST"] = "True"


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        shared.getenv("MONGO_URI"),
        shared.getenv("MONGO_DB_TEST", "cs3528_testing"),
    )

    yield DATABASE

    DATABASE.connection.close()


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
def user_logged_in_browser(chrome_browser, flask_server, database, placement_member):
    chrome_browser.get("http://127.0.0.1:5000/user/login")
    chrome_browser.find_element(By.NAME, "email").send_keys("dummy@dummy.com")
    chrome_browser.find_element(By.NAME, "password").send_keys("dummy")
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/user/home")
    )

    assert chrome_browser.current_url == "http://127.0.0.1:5000/user/home"

    yield chrome_browser


@pytest.fixture
def students_collection(database):
    students = database.get_all("students")
    database.delete_all("students")

    yield

    database.delete_all("students")
    for student in students:
        database.insert("students", student)


def test_successful_upload(user_logged_in_browser, students_collection):
    user_logged_in_browser.get("http://127.0.0.1:5000/students/upload")
    with open("tests/data/valid_students.xlsx", "rb") as f:
        file_input = user_logged_in_browser.find_element(By.NAME, "file")
        file_input.send_keys(os.path.abspath(f.name))
    os.environ["BASE_EMAIL_FOR_STUDENTS"] = "dummy.com"
    submit_button = WebDriverWait(user_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()

    # user_logged_in_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(user_logged_in_browser, 10).until(EC.alert_is_present())
    alert = user_logged_in_browser.switch_to.alert
    alert.accept()

    WebDriverWait(user_logged_in_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/students/search")
    )
    assert user_logged_in_browser.current_url == "http://127.0.0.1:5000/students/search"


def test_failure_email_upload(user_logged_in_browser, students_collection):
    user_logged_in_browser.get("http://127.0.0.1:5000/students/upload")
    with open("tests/data/Invalid_students_email.xlsx", "rb") as f:
        file_input = user_logged_in_browser.find_element(By.NAME, "file")
        file_input.send_keys(os.path.abspath(f.name))
    os.environ["BASE_EMAIL_FOR_STUDENTS"] = "dummy.com"
    submit_button = WebDriverWait(user_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()
    # user_logged_in_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(user_logged_in_browser, 20).until(EC.alert_is_present())
    alert = user_logged_in_browser.switch_to.alert
    alert.accept()

    WebDriverWait(user_logged_in_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/students/upload")
    )
    assert user_logged_in_browser.current_url == "http://127.0.0.1:5000/students/upload"
