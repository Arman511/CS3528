import logging
import os
import sys
import threading

import pytest


@pytest.fixture(scope="session")
def flask_server():
    """Start the Flask app in a separate thread."""
    from app import app

    # Set up logging to print to console
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if os.name != "nt":
        os.system("fuser -k 5000/tcp")
    global server_thread
    server_thread = threading.Thread(
        target=lambda: app.run(port=5000, debug=False, use_reloader=False)
    )
    server_thread.daemon = True
    server_thread.start()
    yield
    # After the yield, kill the app

    server_thread.join(timeout=1)
