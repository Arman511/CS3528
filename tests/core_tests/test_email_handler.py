"""Tests for email_handler.py"""

from email.mime.text import MIMEText
import os
import sys

import pytest

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core.email_handler import generate_otp, send_otp, send_email

os.environ["IS_TEST"] = "True"


@pytest.fixture
def app():
    from app import app

    app.config["TESTING"] = True
    return app


def test_generate_otp():
    otp = generate_otp()
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()


def test_send_otp(app):
    """Test send_otp function"""

    with app.app_context():
        with app.test_request_context():
            send_otp("test@example.com")


def test_send_email(app):
    """Test send_email function"""
    msg = MIMEText("<body>Test</body>", "html")
    recipients = ["test@example.com"]
    with app.app_context():
        with app.test_request_context():
            send_email(msg, recipients)
