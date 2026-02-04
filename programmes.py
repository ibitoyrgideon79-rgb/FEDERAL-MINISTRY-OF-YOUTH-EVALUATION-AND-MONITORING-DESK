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

# helper to preload sample programmes
def preload_programmes(db: Session):
    samples = [
        {"name": "Youth Skills Accelerator", "department": "Education"},
        {"name": "Entrepreneurship Incubator", "department": "Commerce"},
        {"name": "Digital Literacy", "department": "ICT"},
    ]
    existing = db.query(Programme).count()
    if existing == 0:
        for s in samples:
            db.add(Programme(name=s["name"], department=s["department"]))
        db.commit()
