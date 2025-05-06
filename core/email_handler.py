"""Email handler"""

import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
from flask import session
from itsdangerous.url_safe import URLSafeSerializer

from core import shared
import uuid
import requests

load_dotenv()

SENDER: str = str(shared.getenv("EMAIL"))
PASSWORD: str = str(shared.getenv("EMAIL_PASSWORD"))
SMTP: str = str(shared.getenv("SMTP"))
COMPANY_NAME: str = str(shared.getenv("COMPANY_NAME"))
EMAIL_VERIFICATION: bool = shared.getenv("EMAIL_VERIFICATION", "False") == "True"


def generate_otp():
    """Generates an OTP using UUID"""
    return str(uuid.uuid4().int)[:6]


def send_otp(recipient):
    """Sends an OTP"""
    otp_serializer = URLSafeSerializer(str(shared.getenv("SECRET_KEY", "secret")))
    otp = generate_otp()
    print(f"Generated OTP: {otp}")
    session["OTP"] = otp_serializer.dumps(otp)

    if shared.getenv("IS_TEST") == "True":
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
    msg["From"] = f"{COMPANY_NAME} <{SENDER}>"
    msg["To"] = recipient

    # Send the email
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipient, msg.as_string())

    print(f"Styled OTP email sent to {recipient}")


def send_email(msg, recipients):
    """Sends an email"""
    if shared.getenv("IS_TEST") == "True":
        return
    msg["From"] = f"{COMPANY_NAME} <{SENDER}>"
    with smtplib.SMTP_SSL(SMTP, 465) as smtp_server:
        smtp_server.login(SENDER, PASSWORD)
        smtp_server.sendmail(SENDER, recipients, msg.as_string())

    print(f"Email sent to {recipients}")


def verify_email_batch(emails: list[str]):
    """Verify a batch of emails using the Kickbox API."""
    if shared.getenv("IS_TEST") == "True" or not EMAIL_VERIFICATION:
        return True
    API_KEY = shared.getenv("KICKBOX_API_KEY")
    if not API_KEY:
        print("Kickbox API key is not configured.")
        return False, None

    endpoint = "https://api.kickbox.com/v2/verify"
    for i, email in enumerate(emails):
        try:
            response = requests.get(
                endpoint, params={"email": email, "apikey": API_KEY}, timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if data.get("result") != "deliverable":
                print(
                    f"Invalid email: {email}, reason: {data.get('reason')}, position: {i}"
                )
                return False, i, data.get("reason")
        except requests.RequestException as e:
            print(f"Error verifying email {email}: {e}")
            return False, i, e
    return True, None, None


def verify_email(email: str):
    """Verify a of emails using the Kickbox API."""
    if shared.getenv("IS_TEST") == "True" or not EMAIL_VERIFICATION:
        return True, None

    API_KEY = shared.getenv("KICKBOX_API_KEY")
    if not API_KEY:
        print("Kickbox API key is not configured.")
        return False, None

    endpoint = "https://api.kickbox.com/v2/verify"
    try:
        response = requests.get(
            endpoint, params={"email": email, "apikey": API_KEY}, timeout=10
        )
        response.raise_for_status()
        data = response.json()
        if data.get("result") != "deliverable":
            print(f"Invalid email: {email}, reason: {data.get('reason')}")
            return False, data.get("reason")
    except requests.RequestException as e:
        print(f"Error verifying email {email}: {e}")
        return False, e
    return True, None
