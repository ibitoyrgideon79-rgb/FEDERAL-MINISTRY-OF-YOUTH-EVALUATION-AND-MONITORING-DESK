import secrets
import uuid
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
load_dotenv()

SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", 30))


def generate_otp() -> str:
    return str(secrets.randbelow(900000) + 100000)


def generate_session_token() -> str:
    return uuid.uuid4().hex


def session_expiry() -> datetime:
    return datetime.utcnow() + timedelta(days=SESSION_EXPIRE_DAYS)
