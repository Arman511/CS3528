"""Tests for email_handler.py"""

import os
import sys

# flake8: noqa: F811

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from core.email_handler import generate_otp


def test_generate_otp():
    otp = generate_otp()
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()
