import json
import os
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Programme, FormToken, FormSubmission
from schemas import FormLinkRequest, PublicFormSubmission, FormSubmissionOut
from utils.auth_utils import require_admin
from utils.email import send_email
from utils.form_tokens import (
    FORM_TOKEN_ONE_TIME,
    generate_form_token,
    hash_token,
    verify_form_token,
)

router = APIRouter(prefix="/forms", tags=["forms"])


def _utc_now():
    return datetime.now(timezone.utc)


def _is_expired(ts: datetime) -> bool:
    if ts.tzinfo is None:
        return ts < datetime.utcnow()
    return ts < _utc_now()


def _validate_token(programme_id: int, token: str, db: Session):
    # Validate signature/expiry, then enforce programme + recipient email lock.
    try:
        payload = verify_form_token(token)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if payload["pid"] != programme_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token does not match programme")

    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    if not programme.recipient_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Programme has no recipient email")

    if programme.recipient_email.lower() != payload["email"].lower():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token email mismatch")

    token_row = None
    if FORM_TOKEN_ONE_TIME:
        # One-time mode requires a stored token record and blocks re-use.
        token_row = db.query(FormToken).filter(FormToken.token_hash == hash_token(token)).first()
        if not token_row:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unknown token")
        if _is_expired(token_row.expires_at):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token expired")
        if token_row.used:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token already used")

    return programme, payload["email"], token_row


def _build_form_link(
    programme_id: int,
    recipient_email: str,
    request: Request,
    db: Session,
) -> tuple[str, datetime]:
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")
    normalized_email = recipient_email.strip().lower()
    if not normalized_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipient email is required")
    if programme.recipient_email != normalized_email:
        programme.recipient_email = normalized_email
        db.add(programme)
        db.commit()
        db.refresh(programme)

    try:
        token, expires_at = generate_form_token(programme.id, programme.recipient_email)
        if FORM_TOKEN_ONE_TIME:
            token_entry = FormToken(
                token_hash=hash_token(token),
                programme_id=programme.id,
                recipient_email=programme.recipient_email,
                expires_at=expires_at,
                used=False,
            )
            db.add(token_entry)
            db.commit()
    except Exception as exc:
        print(f"Error generating form token: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to generate token")

    base_url = os.getenv("APP_BASE_URL") or str(request.base_url).rstrip("/")
    form_link = f"{base_url}/forms/{programme.id}?token={token}"
    return form_link, expires_at


@router.post("/admin/send-link")
def send_form_link(
    payload: FormLinkRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    programme = db.query(Programme).filter(Programme.id == payload.programme_id).first()
    if not programme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    form_link, expires_at = _build_form_link(
        programme_id=programme.id,
        recipient_email=payload.recipient_email,
        request=request,
        db=db,
    )

    subject = f"Form Submission Link: {programme.name}"
    body = (
        "Hello,\n\n"
        f"You have been invited to submit a form for the programme: {programme.name}.\n\n"
        f"Please use this secure link to submit your form:\n{form_link}\n\n"
        "This link is unique to your email address and may expire.\n\n"
        "Thank you."
    )

    sent, error = send_email(programme.recipient_email, subject, body)
    if not sent:
        print(f"Failed to send email to {programme.recipient_email}: {error}")
        detail = f"Failed to send email: {error}" if error else "Failed to send email"
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

    return {"message": "Form link sent", "expires_at": expires_at.isoformat()}


@router.post("/admin/create-link")
def create_form_link(
    payload: FormLinkRequest,
    request: Request,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    programme = db.query(Programme).filter(Programme.id == payload.programme_id).first()
    if not programme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    form_link, expires_at = _build_form_link(
        programme_id=programme.id,
        recipient_email=payload.recipient_email,
        request=request,
        db=db,
    )

    return {
        "message": "Form link generated",
        "form_link": form_link,
        "expires_at": expires_at.isoformat(),
        "programme_name": programme.name,
        "recipient_email": programme.recipient_email,
    }


@router.get("/{programme_id}")
def render_form(programme_id: int, token: str, db: Session = Depends(get_db)):
    _validate_token(programme_id, token, db)
    return FileResponse("frontend/public-form.html")


@router.get("/{programme_id}/info")
def form_info(programme_id: int, token: str, db: Session = Depends(get_db)):
    programme, recipient_email, _ = _validate_token(programme_id, token, db)
    return {
        "programme_id": programme.id,
        "programme_name": programme.name,
        "description": programme.description,
        "recipient_email": recipient_email,
    }


@router.post("/{programme_id}/submit", response_model=FormSubmissionOut)
def submit_form(
    programme_id: int,
    payload: PublicFormSubmission,
    token: str,
    db: Session = Depends(get_db),
):
    programme, recipient_email, token_row = _validate_token(programme_id, token, db)

    if payload.programme_name != programme.name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Programme name mismatch")

    try:
        submission = FormSubmission(
            programme_id=programme.id,
            recipient_email=recipient_email,
            form_data=json.dumps(payload.dict(), default=str),
        )
        db.add(submission)
        if FORM_TOKEN_ONE_TIME and token_row:
            # Prevent token reuse after successful submission.
            token_row.used = True
            db.add(token_row)
        db.commit()
        db.refresh(submission)
    except Exception as exc:
        print(f"Error saving form submission: {exc}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save submission")

    try:
        admin_email = os.getenv("ADMIN_EMAIL", "")
        if admin_email:
            subject = f"New Form Submission: {programme.name}"
            body = (
                "Hello Admin,\n\n"
                f"A new form submission has been received for {programme.name}.\n"
                f"Submitted at: {submission.submitted_at}\n\n"
                "Please review it in the admin dashboard.\n"
            )
            send_email(admin_email, subject, body)
    except Exception as exc:
        print(f"Failed to notify admin: {exc}")

    return {
        "id": submission.id,
        "programme_id": submission.programme_id,
        "recipient_email": submission.recipient_email,
        "form_data": json.loads(submission.form_data),
        "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
    }


@router.get("/admin/summary")
def admin_summary(db: Session = Depends(get_db), admin_user=Depends(require_admin)):
    programmes = db.query(Programme).all()
    counts = {
        row.programme_id: {"count": row.count, "last": row.last_submitted_at}
        for row in db.query(
            FormSubmission.programme_id.label("programme_id"),
            func.count(FormSubmission.id).label("count"),
            func.max(FormSubmission.submitted_at).label("last_submitted_at"),
        ).group_by(FormSubmission.programme_id)
    }

    result = []
    for programme in programmes:
        stats = counts.get(programme.id, {"count": 0, "last": None})
        result.append(
            {
                "programme_id": programme.id,
                "programme_name": programme.name,
                "recipient_email": programme.recipient_email,
                "submission_count": stats["count"],
                "last_submitted_at": stats["last"].isoformat() if stats["last"] else None,
            }
        )
    return result


@router.get("/admin/submissions", response_model=list[FormSubmissionOut])
def admin_submissions(
    programme_id: int | None = None,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    query = db.query(FormSubmission).order_by(FormSubmission.submitted_at.desc())
    if programme_id:
        query = query.filter(FormSubmission.programme_id == programme_id)
    submissions = query.all()

    response = []
    for submission in submissions:
        response.append(
            {
                "id": submission.id,
                "programme_id": submission.programme_id,
                "recipient_email": submission.recipient_email,
                "form_data": json.loads(submission.form_data),
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
            }
        )
    return response
