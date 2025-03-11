import os
import uuid
import pandas as pd
from io import BytesIO

import pytest
from core.database_mongo_manager import DatabaseMongoManager
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha512

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

load_dotenv()
os.environ["IS_TEST"] = "True"

@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE

    DATABASE.connection.close()

@pytest.fixture
def superuser(database):
    users = database.get_all("users")
    database.delete_all("users")

    user = {
        "_id": uuid.uuid4().hex,
        "name": "superuser",
        "email": "superuser@dummy.com",
        "password": pbkdf2_sha512.hash("superuser"),
        "role": "superuser"
    }
    database.insert("users", user)
    yield user
    database.delete_all("users")
    for user in users:
        database.insert("users", user)

@pytest.fixture
def superuser_logged_in_browser(chrome_browser, flask_server, database, superuser):
    chrome_browser.get("http://127.0.0.1:5000/superuser/login")

    # Wait for the email input field to be present
    try:
        WebDriverWait(chrome_browser, 20).until(
            EC.presence_of_element_located((By.NAME, "email"))
        )
    except TimeoutException:
        print("TimeoutException: Email input field not found on the login page.")
        raise

    chrome_browser.find_element(By.NAME, "email").send_keys("superuser@dummy.com")
    chrome_browser.find_element(By.NAME, "password").send_keys("superuser")
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 20).until(
        EC.url_to_be("http://127.0.0.1:5000/superuser/home")
    )

    assert chrome_browser.current_url == "http://127.0.0.1:5000/superuser/home"

    yield chrome_browser

def test_superuser_successful_login(superuser_logged_in_browser):
    """Test successful login for superuser."""
    assert superuser_logged_in_browser.current_url == "http://127.0.0.1:5000/superuser/home"

def test_superuser_upload_data(superuser_logged_in_browser, database):
    """Test uploading data as superuser."""
    superuser_logged_in_browser.get("http://127.0.0.1:5000/superuser/upload")
    df = pd.DataFrame([
        {"Company_name": "TechCorp", "Email": "contact@techcorp.com"}
    ])
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_input = superuser_logged_in_browser.find_element(By.NAME, "file")
    file_input.send_keys(os.path.abspath("tests/data/valid_employers.xlsx"))
    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()

    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    alert.accept()

    WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/superuser/home")
    )
    assert superuser_logged_in_browser.current_url == "http://127.0.0.1:5000/superuser/home"

def test_superuser_failure_upload(superuser_logged_in_browser, database):
    """Test failure upload as superuser."""
    superuser_logged_in_browser.get("http://127.0.0.1:5000/superuser/upload")
    df = pd.DataFrame([
        {"Company_name": "TechCorp", "Email": "invalid-email"}
    ])
    excel_buffer = BytesIO()
    df.to_excel(excel_buffer, index=False)
    excel_buffer.seek(0)
    file_input = superuser_logged_in_browser.find_element(By.NAME, "file")
    file_input.send_keys(excel_buffer.getvalue())
    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()

    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    alert.accept()

    WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/superuser/upload")
    )
    assert superuser_logged_in_browser.current_url == "http://127.0.0.1:5000/superuser/upload"