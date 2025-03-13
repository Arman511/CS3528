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
    submit_button.click()

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

    

def test_superuser_add_user(superuser_logged_in_browser, database):
   superuser_logged_in_browser.get("http://127.0.0.1:5000/user/register")
   
   user_name = superuser_logged_in_browser.find_element(By.NAME, "name")
   user_email = superuser_logged_in_browser.find_element(By.NAME, "email")
   user_password = superuser_logged_in_browser.find_element(By.NAME, "password")
   user_confirm_password = superuser_logged_in_browser.find_element(By.NAME, "confirm_password")

   user_name.clear()
   user_email.clear()
   user_password.clear()
   user_confirm_password.clear()  

   user_name.send_keys("test_user")
   user_email.send_keys("test_user@email.com") 
   user_password.send_keys("password")
   user_confirm_password.send_keys("password")
   
   submit_button = WebDriverWait(superuser_logged_in_browser, 10).until(
       EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type='submit']"))
    )

#def test_superuser_update_user(superuser_logged_in_browser, database):
 #   superuser_logged_in_browser.get("http://127.0.0.1:5000/user/register")

#def test_superuser_change_user_password(superuser_logged_in_browser, database):
 #   superuser_logged_in_browser.get("http://127.0.0.1:5000/user/register")

#def test_superuser_delete_user(superuser_logged_in_browser, database):
 #   superuser_logged_in_browser.get("http://127.0.0.1:5000/user/register")