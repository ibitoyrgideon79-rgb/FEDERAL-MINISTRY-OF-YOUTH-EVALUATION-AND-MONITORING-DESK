import json
import os
import smtplib
import urllib.request
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "console").lower()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM", FROM_EMAIL)


def _send_resend(to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
    if not RESEND_API_KEY:
        return False, "RESEND_API_KEY is not configured"
    if not RESEND_FROM:
        return False, "RESEND_FROM is not configured"

    payload = {
        "from": RESEND_FROM,
        "to": [to_email],
        "subject": subject,
        "text": body,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=data,
        method="POST",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status >= 200 and resp.status < 300:
                return True, None
            return False, f"Resend API responded with status {resp.status}"
    except Exception as exc:
        return False, str(exc)


def send_email(to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
    """Send an email using the configured backend."""
    if EMAIL_BACKEND == "console":
        print(f"--- EMAIL to: {to_email} ---\nSubject: {subject}\n\n{body}\n--- END EMAIL ---")
        return True, None

    if EMAIL_BACKEND == "resend":
        return _send_resend(to_email, subject, body)

    if EMAIL_BACKEND != "smtp":
        return False, f"Unsupported EMAIL_BACKEND '{EMAIL_BACKEND}'"

    if not SMTP_HOST:
        return False, "SMTP_HOST is not configured"

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
            smtp.send_message(msg)
        return True, None
    except Exception as exc:
        print("Failed to send email:", exc)
        return False, str(exc)
