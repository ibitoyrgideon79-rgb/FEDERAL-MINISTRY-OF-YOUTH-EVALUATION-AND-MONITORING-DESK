from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Programme
from schemas import ProgrammeOut

router = APIRouter(prefix="/programmes", tags=["programmes"])

@router.get("/", response_model=list[ProgrammeOut])
def list_programmes(db: Session = Depends(get_db)):
    programmes = db.query(Programme).all()
    return programmes

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
