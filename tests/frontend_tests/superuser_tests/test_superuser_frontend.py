import os
import uuid

import pytest
from core.database_mongo_manager import DatabaseMongoManager
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha512

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, NoSuchElementException, UnexpectedAlertPresentException

import random
import string

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
def superuser_logged_in_browser(chrome_browser, flask_server, database):
    """ Fixture to log in a superuser. """
    superuser_email = os.getenv("SUPERUSER_EMAIL")
    superuser_password = os.getenv("SUPERUSER_PASSWORD")
    chrome_browser.get("http://127.0.0.1:5000/user/login")
    chrome_browser.find_element(By.NAME, "email").send_keys(superuser_email)
    chrome_browser.find_element(By.NAME, "password").send_keys(superuser_password)
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 10).until(
        EC.url_to_be("http://127.0.0.1:5000/user/search")
    )

    assert chrome_browser.current_url == "http://127.0.0.1:5000/user/search"
    yield chrome_browser

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def delete_user_if_exists(browser, name, email):
    browser.get("http://127.0.0.1:5000/user/search")
    
    search_input_name = browser.find_element(By.NAME, "name")
    search_input_email = browser.find_element(By.NAME, "email")
    
    search_input_name.clear()
    search_input_email.clear()

    search_input_name.send_keys(name)
    search_input_email.send_keys(email)

    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "user-table"))
    )

    user_table = browser.find_element(By.ID, "user-table")
    if name in user_table.text:
        delete_button = user_table.find_element(By.XPATH, f"//tr[td[text()='{name}']]/td/button[text()='Delete']")
        delete_button.click()
        WebDriverWait(browser, 10).until(EC.alert_is_present())
        alert = browser.switch_to.alert
        alert.accept()

def test_superuser_configure(superuser_logged_in_browser):
    superuser_logged_in_browser.get("http://127.0.0.1:5000/superuser/configure")
    
    config_input_skills = superuser_logged_in_browser.find_element(By.NAME, "max_skills")
    config_input_rank = superuser_logged_in_browser.find_element(By.NAME, "min_num_ranking_student_to_opportunity")
    
    current_max_skills = config_input_skills.get_attribute("value")
    current_min_num_ranking_student_to_opportunity = config_input_rank.get_attribute("value")
    
    config_input_skills.clear()
    config_input_rank.clear()

    config_input_skills.send_keys("100")
    config_input_rank.send_keys("160")
    
    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    submit_button.click()
    
    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    assert alert.text == "Configuration updated successfully"
    alert.accept()

    assert config_input_skills.get_attribute("value") == "100"
    assert config_input_rank.get_attribute("value") == "160"

    config_input_skills.clear()
    config_input_rank.clear()

    config_input_skills.send_keys(current_max_skills)
    config_input_rank.send_keys(current_min_num_ranking_student_to_opportunity)

    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(   
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    superuser_logged_in_browser.execute_script("arguments[0].click();", submit_button)

    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    alert.accept()


def test_superuser_search_users(superuser_logged_in_browser, database):
    superuser_logged_in_browser.get("http://127.0.0.1:5000/user/search")
    
    search_input_name = superuser_logged_in_browser.find_element(By.NAME, "name")
    search_input_email = superuser_logged_in_browser.find_element(By.NAME, "email")
    
    search_input_name.clear()
    search_input_email.clear()

    search_input_name.send_keys("test")
    search_input_email.send_keys("test@email.com")

    # Verify that the search results contain the expected user
    WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.presence_of_element_located((By.ID, "user-table"))
    )
    user_table = superuser_logged_in_browser.find_element(By.ID, "user-table")
    assert "test_user" not in user_table.text

def test_superuser_register_user(superuser_logged_in_browser, database):
    # Generate random user details
    random_name = generate_random_string()
    random_email = f"{random_name}@example.com"
    random_password = generate_random_string()

    # Delete the user if it exists before registration
    delete_user_if_exists(superuser_logged_in_browser, random_name, random_email)

    # Register the user
    superuser_logged_in_browser.get("http://127.0.0.1:5000/user/register")
   
    user_name = superuser_logged_in_browser.find_element(By.NAME, "name")
    user_email = superuser_logged_in_browser.find_element(By.NAME, "email")
    user_password = superuser_logged_in_browser.find_element(By.NAME, "password")
    user_confirm_password = superuser_logged_in_browser.find_element(By.NAME, "confirm_password")

    user_name.clear()
    user_email.clear()
    user_password.clear()
    user_confirm_password.clear()  

    user_name.send_keys(random_name)
    user_email.send_keys(random_email)
    user_password.send_keys(random_password)
    user_confirm_password.send_keys(random_password)
   
    submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )
    superuser_logged_in_browser.execute_script("arguments[0].click();", submit_button)

    # Refresh the page and check if the user was registered
    superuser_logged_in_browser.refresh()
    delete_user_if_exists(superuser_logged_in_browser, random_name, random_email)


def test_superuser_update_user(superuser_logged_in_browser, database):
    def register_user(browser, name, email, password):
        browser.get("http://127.0.0.1:5000/user/register")
       
        user_name = browser.find_element(By.NAME, "name")
        user_email = browser.find_element(By.NAME, "email")
        user_password = browser.find_element(By.NAME, "password")
        user_confirm_password = browser.find_element(By.NAME, "confirm_password")

        user_name.clear()
        user_email.clear()
        user_password.clear()
        user_confirm_password.clear()  

        user_name.send_keys(name)
        user_email.send_keys(email)
        user_password.send_keys(password)
        user_confirm_password.send_keys(password)
       
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        browser.execute_script("arguments[0].click();", submit_button)

        WebDriverWait(browser, 10).until(EC.alert_is_present())
        alert = browser.switch_to.alert
        assert alert.text == "User registered successfully"
        alert.accept()

    def delete_user(browser, name, email):
        browser.get("http://127.0.0.1:5000/user/search")
        
        search_input_name = browser.find_element(By.NAME, "name")
        search_input_email = browser.find_element(By.NAME, "email")
        
        search_input_name.clear()
        search_input_email.clear()

        search_input_name.send_keys(name)
        search_input_email.send_keys(email)

        WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.ID, "user-table"))
        )

        user_table = browser.find_element(By.ID, "user-table")
        if name in user_table.text:
            delete_button = user_table.find_element(By.XPATH, f"//tr[td[text()='{name}']]/td/button[text()='Delete']")
            delete_button.click()
            WebDriverWait(browser, 10).until(EC.alert_is_present())
            alert = browser.switch_to.alert
            alert.accept()

    # Generate random user details
    random_name = generate_random_string()
    random_email = f"{random_name}@example.com"
    random_password = generate_random_string()

    superuser_logged_in_browser.get("http://127.0.0.1:5000/user/search")

    # Find a random user to update
    user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.presence_of_element_located((By.ID, "user-table"))
    )
    rows = user_table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 2:
        # No users available to update, so add a random user first
        register_user(superuser_logged_in_browser, random_name, random_email, random_password)

        # Refresh the page to see the newly added user
        superuser_logged_in_browser.refresh()
        user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
            EC.presence_of_element_located((By.ID, "user-table"))
        )
        rows = user_table.find_elements(By.TAG_NAME, "tr")

    # Select a random user (excluding the header row)
    random_user_row = random.choice(rows[1:])
    update_button = random_user_row.find_element(By.XPATH, ".//a[contains(text(), 'Update')]")
    superuser_logged_in_browser.execute_script("arguments[0].click();", update_button)

    for _ in range(3):
        try:
            # Update the user's name and email on the update page
            user_name = WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.presence_of_element_located((By.NAME, "name"))
            )
            user_email = superuser_logged_in_browser.find_element(By.NAME, "email")

            user_name.clear()
            user_email.clear()

            user_name.send_keys(random_name)
            user_email.send_keys(random_email)

            # Click the update button on the update page
            submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            )
            superuser_logged_in_browser.execute_script("arguments[0].click();", submit_button)

            # Wait for the alert and accept it
            WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
            alert = superuser_logged_in_browser.switch_to.alert
            assert alert.text == "User updated successfully"
            alert.accept()

            # Verify that the user is redirected back to the search page
            WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.url_to_be("http://127.0.0.1:5000/user/search")
            )

            # Verify that the user's name and email have been updated
            search_input_name = superuser_logged_in_browser.find_element(By.NAME, "name")
            search_input_email = superuser_logged_in_browser.find_element(By.NAME, "email")

            search_input_name.clear()
            search_input_email.clear()

            search_input_name.send_keys(random_name)
            search_input_email.send_keys(random_email)

            WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.presence_of_element_located((By.ID, "user-table"))
            )
            user_table = superuser_logged_in_browser.find_element(By.ID, "user-table")
            assert random_name in user_table.text
            assert random_email in user_table.text

            # Delete the test user after verification
            delete_user(superuser_logged_in_browser, random_name, random_email)
            break
        except (TimeoutException, NoSuchElementException):
            superuser_logged_in_browser.refresh()
        except UnexpectedAlertPresentException:
            alert = superuser_logged_in_browser.switch_to.alert
            alert.accept()

def test_superuser_change_user_password(superuser_logged_in_browser, database):
    def register_user(browser, name, email, password):
        browser.get("http://127.0.0.1:5000/user/register")
       
        user_name = browser.find_element(By.NAME, "name")
        user_email = browser.find_element(By.NAME, "email")
        user_password = browser.find_element(By.NAME, "password")
        user_confirm_password = browser.find_element(By.NAME, "confirm_password")

        user_name.clear()
        user_email.clear()
        user_password.clear()
        user_confirm_password.clear()  

        user_name.send_keys(name)
        user_email.send_keys(email)
        user_password.send_keys(password)
        user_confirm_password.send_keys(password)
       
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        browser.execute_script("arguments[0].click();", submit_button)

    # Generate random user details
    random_name = generate_random_string()
    random_email = f"{random_name}@example.com"
    random_password = generate_random_string()

    # Navigate to the user search page
    superuser_logged_in_browser.get("http://127.0.0.1:5000/user/search")

    # Find a random user to change the password
    user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.presence_of_element_located((By.ID, "user-table"))
    )
    rows = user_table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 2:
        # No users available to update, so add a random user first
        register_user(superuser_logged_in_browser, random_name, random_email, random_password)

        # Refresh the page to see the newly added user
        superuser_logged_in_browser.refresh()
        user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
            EC.presence_of_element_located((By.ID, "user-table"))
        )
        rows = user_table.find_elements(By.TAG_NAME, "tr")

    # Select a random user (excluding the header row)
    random_user_row = random.choice(rows[1:])
    change_password_button = random_user_row.find_element(By.XPATH, ".//a[contains(text(), 'Change Password')]")
    superuser_logged_in_browser.execute_script("arguments[0].click();", change_password_button)

    # Retry logic to handle potential TimeoutException
    for _ in range(3):
        try:
            # Change the user's password on the change password page
            new_password = WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.presence_of_element_located((By.NAME, "new_password"))
            )
            confirm_password = superuser_logged_in_browser.find_element(By.NAME, "confirm_password")

            new_password.clear()
            confirm_password.clear()

            new_password.send_keys("new_password")
            confirm_password.send_keys("new_password")

            # Click the update button on the change password page
            submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
            )
            superuser_logged_in_browser.execute_script("arguments[0].click();", submit_button)

            # Wait for the alert and accept it
            WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
            alert = superuser_logged_in_browser.switch_to.alert
            assert alert.text == "Password changed successfully"
            alert.accept()
            break
        except (TimeoutException, NoSuchElementException):
            superuser_logged_in_browser.refresh()

def test_superuser_delete_user(superuser_logged_in_browser, database):
    def register_user(browser, name, email, password):
        browser.get("http://127.0.0.1:5000/user/register")
       
        user_name = browser.find_element(By.NAME, "name")
        user_email = browser.find_element(By.NAME, "email")
        user_password = browser.find_element(By.NAME, "password")
        user_confirm_password = browser.find_element(By.NAME, "confirm_password")

        user_name.clear()
        user_email.clear()
        user_password.clear()
        user_confirm_password.clear()  

        user_name.send_keys(name)
        user_email.send_keys(email)
        user_password.send_keys(password)
        user_confirm_password.send_keys(password)
       
        submit_button = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
        )
        browser.execute_script("arguments[0].click();", submit_button)

    # Generate random user details
    random_name = generate_random_string()
    random_email = f"{random_name}@example.com"
    random_password = generate_random_string()

    # Navigate to the user search page
    superuser_logged_in_browser.get("http://127.0.0.1:5000/user/search")

    # Find a random user to delete
    user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
        EC.presence_of_element_located((By.ID, "user-table"))
    )
    rows = user_table.find_elements(By.TAG_NAME, "tr")
    if len(rows) < 2:
        # No users available to delete, so add a random user first
        register_user(superuser_logged_in_browser, random_name, random_email, random_password)

        # Refresh the page to see the newly added user
        superuser_logged_in_browser.refresh()
        user_table = WebDriverWait(superuser_logged_in_browser, 10).until(
            EC.presence_of_element_located((By.ID, "user-table"))
        )
        rows = user_table.find_elements(By.TAG_NAME, "tr")

    # Select a random user (excluding the header row)
    random_user_row = random.choice(rows[1:])
    delete_button = random_user_row.find_element(By.XPATH, ".//a[contains(text(), 'Delete')]")
    user_name = random_user_row.find_element(By.XPATH, ".//td[2]").text.strip()

    # Confirm the deletion
    superuser_logged_in_browser.execute_script("arguments[0].click();", delete_button)
    WebDriverWait(superuser_logged_in_browser, 10).until(EC.alert_is_present())
    alert = superuser_logged_in_browser.switch_to.alert
    assert alert.text == f"Are you sure you want to delete the user \"{user_name}\"?"
    alert.accept()

    # Verify that the user has been deleted
    superuser_logged_in_browser.refresh()

    # Retry logic to handle potential StaleElementReferenceException
    for _ in range(3):
        try:
            search_input_name = superuser_logged_in_browser.find_element(By.NAME, "name")
            search_input_email = superuser_logged_in_browser.find_element(By.NAME, "email")

            search_input_name.clear()
            search_input_email.clear()

            search_input_name.send_keys(user_name)
            search_input_email.send_keys(random_user_row.find_element(By.XPATH, ".//td[3]").text.strip())

            WebDriverWait(superuser_logged_in_browser, 10).until(
                EC.presence_of_element_located((By.ID, "user-table"))
            )
            user_table = superuser_logged_in_browser.find_element(By.ID, "user-table")
            assert user_name not in user_table.text
            break
        except StaleElementReferenceException:
            superuser_logged_in_browser.refresh()