from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Programme
from schemas import ProgrammeOut, ProgrammeUpdate
from utils.auth_utils import require_admin

router = APIRouter(prefix="/programmes", tags=["programmes"])

@router.get("/", response_model=list[ProgrammeOut])
def list_programmes(db: Session = Depends(get_db), admin_user=Depends(require_admin)):
    programmes = db.query(Programme).all()
    return programmes


@router.put("/{programme_id}", response_model=ProgrammeOut)
def update_programme(
    programme_id: int,
    payload: ProgrammeUpdate,
    db: Session = Depends(get_db),
    admin_user=Depends(require_admin),
):
    programme = db.query(Programme).filter(Programme.id == programme_id).first()
    if not programme:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Programme not found")

    programme.description = payload.description
    programme.recipient_email = payload.recipient_email.lower()
    db.add(programme)
    db.commit()
    db.refresh(programme)
    return programme

# predefined programmes (if requested i should make this updatable via admin interface....ka eleyi o)
def preload_programmes(db: Session):
    flagship_programmes = [
        {"name": "NIYA", "department": ""},
        {"name": "Green House Initiatives with State Government", "department": ""},
        {"name": "Nig Help Desk", "department": ""},
        {"name": "National Youth Confab", "department": ""},
        {"name": "NYSC Reform Committee", "department": ""},
        {"name": "Youth Data Protection", "department": ""},
        {"name": "Waste to Wealth / Recycling Training", "department": ""},
        {"name": "Bambo Initiative", "department": ""},
        {"name": "SMEDAN Partnership/Youth Start Up", "department": ""},
        {"name": "Security and Exchange Commission MOU", "department": ""},
        {"name": "Financial Literacy and Wealth Creation Training (Forex and Gold Commodity Trading)", "department": ""},
        {"name": "Yo Health", "department": ""},
        {"name": "Bank of Industry Training for NIYA", "department": ""},
        {"name": "Youth Credit Initiative", "department": ""},
        {"name": "Nigerian Youth Investment Fund", "department": ""},
        {"name": "Youth Skills Accelerator", "department": ""},
        {"name": "Entrepreneurship Incubator", "department": ""},
        {"name": "Digital Literacy", "department": ""},
    ]
    existing = db.query(Programme).count()
    if existing == 0:
        for s in flagship_programmes:
            db.add(Programme(name=s["name"], department=s["department"]))
        db.commit()
