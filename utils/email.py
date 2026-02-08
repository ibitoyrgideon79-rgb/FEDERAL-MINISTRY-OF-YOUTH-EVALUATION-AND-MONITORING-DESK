import json
import os
import smtplib
import urllib.request
import urllib.error
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
EMAILJS_SERVICE_ID = os.getenv("EMAILJS_SERVICE_ID")
EMAILJS_TEMPLATE_ID = os.getenv("EMAILJS_TEMPLATE_ID")
EMAILJS_PUBLIC_KEY = os.getenv("EMAILJS_PUBLIC_KEY")
EMAILJS_PRIVATE_KEY = os.getenv("EMAILJS_PRIVATE_KEY")


def _send_resend(to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
    if not RESEND_API_KEY:
        return False, "RESEND_API_KEY is not configured"
    if not RESEND_FROM:
        return False, "RESEND_FROM is not configured"
    if not to_email:
        return False, "Recipient email is missing"

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
            if 200 <= resp.status < 300:
                return True, None
            try:
                detail = resp.read().decode("utf-8", errors="ignore")
            except Exception:
                detail = ""
            return False, f"Resend API responded with status {resp.status}{': ' + detail if detail else ''}"
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            detail = ""
        return False, f"Resend API error {exc.code}{': ' + detail if detail else ''}"
    except Exception as exc:
        return False, str(exc)


def _send_emailjs(to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
    if not EMAILJS_SERVICE_ID:
        return False, "EMAILJS_SERVICE_ID is not configured"
    if not EMAILJS_TEMPLATE_ID:
        return False, "EMAILJS_TEMPLATE_ID is not configured"
    if not EMAILJS_PUBLIC_KEY:
        return False, "EMAILJS_PUBLIC_KEY is not configured"
    if not to_email:
        return False, "Recipient email is missing"

    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": to_email,
            "subject": subject,
            "message": body,
        },
    }
    if EMAILJS_PRIVATE_KEY:
        payload["accessToken"] = EMAILJS_PRIVATE_KEY

    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.emailjs.com/api/v1.0/email/send",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if 200 <= resp.status < 300:
                return True, None
            try:
                detail = resp.read().decode("utf-8", errors="ignore")
            except Exception:
                detail = ""
            return False, f"EmailJS API responded with status {resp.status}{': ' + detail if detail else ''}"
    except urllib.error.HTTPError as exc:
        try:
            detail = exc.read().decode("utf-8", errors="ignore")
        except Exception:
            detail = ""
        return False, f"EmailJS API error {exc.code}{': ' + detail if detail else ''}"
    except Exception as exc:
        return False, str(exc)


def send_email(to_email: str, subject: str, body: str) -> tuple[bool, str | None]:
    """Send an email using the configured backend."""
    if EMAIL_BACKEND == "console":
        print(f"--- EMAIL to: {to_email} ---\nSubject: {subject}\n\n{body}\n--- END EMAIL ---")
        return True, None

    if EMAIL_BACKEND == "resend":
        return _send_resend(to_email, subject, body)

    if EMAIL_BACKEND in ("emailjs", "http"):
        return _send_emailjs(to_email, subject, body)

    if EMAIL_BACKEND != "smtp":
        return False, f"Unsupported EMAIL_BACKEND '{EMAIL_BACKEND}'"

    if not SMTP_HOST:
        return False, "SMTP_HOST is not configured"
    if not to_email:
        return False, "Recipient email is missing"

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
