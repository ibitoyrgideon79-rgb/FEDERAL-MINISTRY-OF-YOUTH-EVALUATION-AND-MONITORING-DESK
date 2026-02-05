from datetime import datetime, timezone
from fastapi import Depends, HTTPException, status, Cookie
from sqlalchemy.orm import Session
from database import get_db
from models import Session as DBSession, User


def _utc_now():
    return datetime.now(timezone.utc)


def _is_expired(ts: datetime) -> bool:
    if ts.tzinfo is None:
        return ts < datetime.utcnow()
    return ts < _utc_now()


def get_current_user(session_token: str = Cookie(None), db: Session = Depends(get_db)) -> User:
    if not session_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    sess = db.query(DBSession).filter(DBSession.token == session_token).first()
    if not sess:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    if _is_expired(sess.expires_at):
        db.delete(sess)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired")
    user = db.query(User).filter(User.id == sess.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user
