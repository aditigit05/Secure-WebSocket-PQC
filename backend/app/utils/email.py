import smtplib
from email.message import EmailMessage
import os 

from app.config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_HOST, SMTP_PORT

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

print("SMTP CONFIG:", SMTP_EMAIL, SMTP_HOST, SMTP_PORT)

def send_otp_email(to_email: str, otp: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Secure Chat OTP"
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email
    
    msg.set_content(
        f"""
your One-Time Password (OTP) is:

{otp}

This OTP will be valid for 5 minutes
Do not share it with anyone.
"""
    )
    
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
    
    # try:
    #     with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
    #         server.starttls()
    #         server.login(SMTP_EMAIL, SMTP_PASSWORD)
    #         server.send_message(msg)
    #         print(f"Email successfully sent to {to_email}")
    # except Exception as e:
    #     print(f"Failed to send email: {e}")
        