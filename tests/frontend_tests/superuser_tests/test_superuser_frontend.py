import os
import uuid

import pytest
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
        "password": pbkdf2_sha512.hash("dummy"),
        "role": "superuser"
    }
    database.insert("users", user)
    yield user
    database.delete_all("users")
    for user in users:
        database.insert("users", user)

@pytest.fixture
def superuser_logged_in_browser(chrome_browser, flask_server, database, superuser):
    chrome_browser.get("http://127.0.0.1:5000/user/login")
    chrome_browser.find_element(By.NAME, "email").send_keys("superuser@dummy.com")
    chrome_browser.find_element(By.NAME, "password").send_keys("dummy")
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/admin/dashboard")
    )

    assert chrome_browser.current_url == "http://127.0.0.1:5000/admin/dashboard"
    yield chrome_browser

def test_superuser_manage_config(superuser_logged_in_browser):
    superuser_logged_in_browser.get("http://127.0.0.1:5000/admin/config")
    
    config_input = superuser_logged_in_browser.find_element(By.NAME, "max_users")
    config_input.clear()
    config_input.send_keys("100")
    
    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()
    
    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    alert.accept()
    
    assert "Configuration updated successfully" in superuser_logged_in_browser.page_source

def test_superuser_manage_users(superuser_logged_in_browser, database):
    superuser_logged_in_browser.get("http://127.0.0.1:5000/admin/users")
    
    add_user_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.ID, "add-user-button"))
    )
    add_user_button.click()
    
    superuser_logged_in_browser.find_element(By.NAME, "name").send_keys("newuser")
    superuser_logged_in_browser.find_element(By.NAME, "email").send_keys("newuser@dummy.com")
    superuser_logged_in_browser.find_element(By.NAME, "password").send_keys("password")
    
    submit_button = superuser_logged_in_browser.find_element(By.CSS_SELECTOR, "input[type='submit']")
    submit_button.click()
    
    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    alert.accept()
    
    assert "User added successfully" in superuser_logged_in_browser.page_source
