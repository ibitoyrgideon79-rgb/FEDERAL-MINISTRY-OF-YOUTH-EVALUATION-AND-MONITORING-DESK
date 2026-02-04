from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from sqlalchemy.orm import Session
from schemas import OTPRequest, OTPVerify, UserOut
from database import get_db
from models import OTP, User, Session as DBSession
from utils.email import send_email
from utils.security import generate_otp, generate_session_token, session_expiry, SESSION_EXPIRE_DAYS
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import os

load_dotenv()
OTP_EXP_MINUTES = int(os.getenv("OTP_EXP_MINUTES", 5))
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").lower()

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/request-otp")
def request_otp(payload: OTPRequest, db: Session = Depends(get_db)):
    code = generate_otp()
    expires = datetime.utcnow() + timedelta(minutes=OTP_EXP_MINUTES)
    otp = OTP(email=payload.email, code=code, expires_at=expires)
    db.add(otp)
    db.commit()
    db.refresh(otp)

    subject = "Your login OTP"
    body = f"Your OTP is {code}. It expires in {OTP_EXP_MINUTES} minutes."
    sent = send_email(payload.email, subject, body)
    if not sent:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send OTP email")

    return {"message": "OTP sent"}

@router.post("/verify-otp", response_model=UserOut)
def verify_otp(payload: OTPVerify, response: Response, db: Session = Depends(get_db)):
    # Fetch the OTP entry for this email with matching code that is not used and not expired
    otp_entry = db.query(OTP).filter(OTP.email == payload.email, OTP.code == payload.code).order_by(OTP.created_at.desc()).first()
    if not otp_entry:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
    if otp_entry.used:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP already used")
    if otp_entry.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP expired")

    # mark as used and persist immediately to prevent reuse
    otp_entry.used = True
    db.add(otp_entry)
    db.commit()

    # get or create user
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        role = "admin" if ADMIN_EMAIL and payload.email.lower() == ADMIN_EMAIL else "user"
        user = User(email=payload.email, role=role)
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # ensure admin role if email matches configured ADMIN_EMAIL
        if ADMIN_EMAIL and user.email.lower() == ADMIN_EMAIL and user.role != "admin":
            user.role = "admin"
            db.add(user)
            db.commit()
            db.refresh(user)

    # create session
    token = generate_session_token()
    expiry = session_expiry()
    session = DBSession(token=token, user_id=user.id, expires_at=expiry)
    db.add(session)
    db.commit()

    # set cookie with a max_age derived from SESSION_EXPIRE_DAYS
    max_age = SESSION_EXPIRE_DAYS * 24 * 60 * 60
    response.set_cookie("session_token", token, httponly=True, samesite="lax", max_age=max_age)

    return user

@router.post("/logout")
def logout(session_token: str = Cookie(None), db: Session = Depends(get_db)):
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    sess = db.query(DBSession).filter(DBSession.token == session_token).first()
    if sess:
        db.delete(sess)
        db.commit()
    return {"message": "Logged out"}
