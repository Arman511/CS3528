"""Email handler"""

import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv
import math
import random

from flask import session

load_dotenv()

SENDER: str = str(os.getenv("EMAIL"))
PASSWORD: str = str(os.getenv("EMAIL_PASSWORD"))


def generate_otp():
    """Makes an otp"""
    digits = "0123456789"
    otp = ""
    for i in range(6):
        otp += digits[math.floor(random.random() * 10)]

    return otp


def send_otp(recipient):
    """Sends an OTP"""
    otp = generate_otp()
    body = f"HERE IS YOUR OTP {otp}"
    msg = MIMEText(body)
    msg["Subject"] = "Skillpoint: OTP"
    msg["From"] = SENDER
    msg["To"] = recipient
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipient, msg.as_string())
    print("Message sent!")
    session["OTP"] = otp
