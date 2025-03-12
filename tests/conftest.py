"""This file contains the fixtures for the tests."""

import logging
import sys
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pytest

SERVER_THREAD = None


@pytest.fixture(scope="session")
def flask_server():
    """Start the Flask app in a separate thread."""
    from app import app

    # Set up logging to print to console
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    global SERVER_THREAD
    SERVER_THREAD = threading.Thread(
        target=lambda: app.run(
            port=5000, host="localhost", debug=False, use_reloader=False
        )
    )
    SERVER_THREAD.daemon = True
    SERVER_THREAD.start()
    yield
    # After the yield, kill the app

    server_thread.join(timeout=1)


@pytest.fixture()
def chrome_browser():
    """Start a Chrome browser session."""
    options = Options()
    options.add_argument("--headless")  # Run Chrome in headless mode
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    driver = webdriver.Chrome(options=options)

    # Use this line instead if you wish to download the ChromeDriver binary on the fly
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    driver.implicitly_wait(10)
    yield driver
    driver.quit()
