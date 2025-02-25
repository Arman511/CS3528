import os

# import sys
import threading
import uuid
from dotenv import load_dotenv
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from passlib.hash import pbkdf2_sha512
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from core.database_mongo_manager import DatabaseMongoManager
import sys
import logging

# sys.path.append(
#     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# )
os.environ["IS_TEST"] = "True"

load_dotenv()


@pytest.fixture()
def chrome_browser():
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    # Use this line instead if you wish to download the ChromeDriver binary on the fly
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope="module")
def flask_server():
    """Start the Flask app in a separate thread."""
    from app import app

    # Set up logging to print to console
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    yield
    # After the yield, kill the app
    if server_thread.is_alive():
        import signal

        os.kill(os.getpid(), signal.SIGINT)
    server_thread.join()


@pytest.fixture()
def database():
    """Fixture to create a test database."""
    DATABASE = DatabaseMongoManager(
        os.getenv("MONGO_URI"), os.getenv("MONGO_DB_TEST", "cs3528_testing")
    )

    yield DATABASE
    DATABASE.delete_all("modules")

    DATABASE.connection.close()


def test_base_page(chrome_browser, flask_server):
    chrome_browser.get("http://localhost:5000/students/login")
    assert chrome_browser.title == "SkillPilot - Student Login"


def test_student_login_page(chrome_browser, flask_server):
    chrome_browser.get("http://localhost:5000/students/login")
    assert chrome_browser.title == "SkillPilot - Student Login"


@pytest.fixture
def user(database):
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


def test_placement_team_login(chrome_browser, flask_server, database, user):
    chrome_browser.get("http://localhost:5000/user/login")
    chrome_browser.find_element(By.NAME, "email").send_keys("dummy@dummy.com")
    chrome_browser.find_element(By.NAME, "password").send_keys("dummy")
    chrome_browser.find_element(By.CSS_SELECTOR, "input[type='submit']").click()

    WebDriverWait(chrome_browser, 10).until(EC.url_to_be("http://localhost:5000/"))

    assert chrome_browser.current_url == "http://localhost:5000/"
