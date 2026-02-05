import base64
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

TOKEN_TTL_HOURS = int(os.getenv("FORM_TOKEN_TTL_HOURS", "72"))
FORM_TOKEN_ONE_TIME = os.getenv("FORM_TOKEN_ONE_TIME", "true").lower() in ("1", "true", "yes")
SECRET_KEY = os.getenv("SECRET_KEY", "")


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _require_secret() -> str:
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not configured")
    return SECRET_KEY


def generate_form_token(programme_id: int, recipient_email: str) -> tuple[str, datetime]:
    secret = _require_secret()
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
    payload = {
        "pid": programme_id,
        "email": recipient_email,
        "exp": int(expires_at.timestamp()),
        "nonce": os.urandom(8).hex(),
    }
    payload_bytes = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    signature = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    token = f"{_b64url_encode(payload_bytes)}.{_b64url_encode(signature)}"
    return token, expires_at


def verify_form_token(token: str) -> dict:
    secret = _require_secret()
    try:
        payload_b64, sig_b64 = token.split(".")
    except ValueError:
        raise ValueError("Invalid token format")

    payload_bytes = _b64url_decode(payload_b64)
    expected_sig = hmac.new(secret.encode("utf-8"), payload_bytes, hashlib.sha256).digest()
    actual_sig = _b64url_decode(sig_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("Invalid token signature")

    payload = json.loads(payload_bytes.decode("utf-8"))
    exp = payload.get("exp")
    if not exp or datetime.utcnow().timestamp() > exp:
        raise ValueError("Token expired")

    if "pid" not in payload or "email" not in payload:
        raise ValueError("Invalid token payload")

    return payload


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
