import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "console")


def send_email(to_email: str, subject: str, body: str):
    """Send an email via SMTP. If EMAIL_BACKEND is 'console' it will print instead.
    """
    if EMAIL_BACKEND == "console":
        print(f"--- EMAIL to: {to_email} ---\nSubject: {subject}\n\n{body}\n--- END EMAIL ---")
        return True

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        print("Failed to send email:", e)
        return False
