"""Email handler"""

import smtplib
from email.mime.text import MIMEText
import os
import math
import random
from dotenv import load_dotenv
from flask import session
from itsdangerous.url_safe import URLSafeSerializer

load_dotenv()

SENDER: str = str(os.getenv("EMAIL"))
PASSWORD: str = str(os.getenv("EMAIL_PASSWORD"))
SMTP: str = str(os.getenv("SMTP"))


def generate_otp():
    """Makes an otp"""
    digits = "0123456789"
    otp = ""
    for _i in range(6):
        otp += digits[math.floor(random.random() * 10)]

    return otp


def send_otp(recipient):
    """Sends an OTP"""
    otp_serializer = URLSafeSerializer(str(os.getenv("SECRET_KEY", "secret")))
    otp = generate_otp()
    print(f"Generated OTP: {otp}")
    session["OTP"] = otp_serializer.dumps(otp)

    if os.getenv("IS_TEST") == "True":
        return

    body = f"HERE IS YOUR OTP {otp}"
    msg = MIMEText(body)
    msg["Subject"] = "Skillpoint: OTP"
    msg["From"] = SENDER
    msg["To"] = recipient
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipient, msg.as_string())

    print(f"Email sent to {recipient}")


def send_email(msg, recipients):
    """Sends an email"""
    if os.getenv("IS_TEST") == "True":
        return
    msg["From"] = SENDER
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipients, msg.as_string())

    print(f"Email sent to {recipients}")
