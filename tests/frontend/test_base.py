# import os
# import sys
import threading
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# from selenium.webdriver.chrome.service import Service as ChromeService
# from webdriver_manager.chrome import ChromeDriverManager
from app import app

# sys.path.append(
#     os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# )


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
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    yield


def test_title(chrome_browser, flask_server):
    chrome_browser.get("http://localhost:5000")
    assert chrome_browser.title == "SkillPilot - Student Login"
