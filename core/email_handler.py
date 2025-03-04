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

    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 20px; background-color: #f4f4f4;">
        <div style="max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1);">
            <h2 style="color: #2c3e50;">Skillpilot OTP Verification</h2>
            <p style="font-size: 16px; color: #333;">Use the OTP below to verify your identity:</p>
            <div style="font-size: 24px; font-weight: bold; color: #3498db; padding: 10px; background: #ecf0f1; border-radius: 5px; display: inline-block; margin: 10px 0;">
                {otp}
            </div>
            <p style="font-size: 14px; color: #777;">This OTP is valid for a limited time. Do not share it with anyone.</p>
            <hr style="border: 0; height: 1px; background: #ddd; margin: 20px 0;">
            <p style="font-size: 14px; color: #777;">If you didn't request this OTP, please ignore this email.</p>
            <p style="font-size: 14px; color: #555;"><strong>Best Regards,</strong><br>Skillpilot Team</p>
        </div>
    </body>
    </html>
    """

    # Set up email headers
    msg = MIMEText(body, "html")
    msg["Subject"] = "Skillpilot: OTP Verification"
    msg["From"] = SENDER
    msg["To"] = recipient

    # Send the email
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipient, msg.as_string())

    print(f"Styled OTP email sent to {recipient}")


def send_email(msg, recipients):
    """Sends an email"""
    if os.getenv("IS_TEST") == "True":
        return
    msg["From"] = SENDER
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipients, msg.as_string())

    print(f"Email sent to {recipients}")
