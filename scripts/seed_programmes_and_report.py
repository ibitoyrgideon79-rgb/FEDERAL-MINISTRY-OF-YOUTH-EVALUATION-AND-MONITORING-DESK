"""Seed script for DMT project

- Loads env via dotenv
- Connects to the existing DB via SessionLocal
- Adds missing programmes (idempotent)
- Adds a sample monthly report for one programme (idempotent)

Run: python scripts/seed_programmes_and_report.py
"""
from dotenv import load_dotenv
load_dotenv()

from database import SessionLocal
from models import Programme, MonthlyReport
from datetime import date
import sys

PROGRAMMES = [
    ("NIYA", "Flagship"),
    ("Green House Initiatives with State Government", "Flagship"),
    ("Nig Help Desk", "Flagship"),
    ("National Youth Confab", "Flagship"),
    ("NYSC Reform Committee", "Flagship"),
    ("Youth Data Protection", "Flagship"),
    ("Waste to Wealth / Recycling Training", "Flagship"),
    ("Bambo Initiative", "Flagship"),
    ("SMEDAN Partnership / Youth Start Up", "Flagship"),
    ("Security and Exchange Commission MOU", "Flagship"),
    ("Financial Literacy and Wealth Creation Training", "Flagship"),
    ("Yo Health", "Flagship"),
    ("Bank of Industry Training for NIYA", "Flagship"),
    ("Youth Credit Initiative", "Flagship"),
    ("Nigerian Youth Investment Fund", "Flagship"),
]

SAMPLE_REPORT = {
    "programme_name": "NIYA",
    "focal_department": "Youth Affairs",
    "focal_aide_hm": "Aide HM Example",
    "focal_ministry_official": "Ministry Official Name",
    "reporting_month": date(2026, 2, 1),
    "programme_launch_date": date(2025, 6, 15),
    "total_youth_registered": 120,
    "youth_trained": 95,
    "youth_funded": 40,
    "youth_with_outcomes": 30,
    "partnerships": "Local NGOs, Private sector partners",
    "challenges": "Limited transport, occasional funding delays",
    "mitigation_strategies": "Allocate travel stipends, diversify funding sources",
    "scale_up_plans": "Pilot to 3 more states next quarter",
    "success_story": "Several youths started micro-enterprises after training",
}


def seed():
    db = SessionLocal()
    try:
        print("Seeding programmes...")
        for name, dept in PROGRAMMES:
            existing = db.query(Programme).filter(Programme.name == name).first()
            if existing:
                print(f"- Programme already exists: {name}")
            else:
                p = Programme(name=name, department=dept)
                db.add(p)
                db.commit()
                db.refresh(p)
                print(f"+ Added programme: {p.name} ({dept})")

        # Submit sample report if not present
        pm_name = SAMPLE_REPORT["programme_name"]
        reporting_month = SAMPLE_REPORT["reporting_month"]
        existing_report = (
            db.query(MonthlyReport)
            .filter(MonthlyReport.programme_name == pm_name, MonthlyReport.reporting_month == reporting_month)
            .first()
        )
        if existing_report:
            print(f"- Sample report for {pm_name} {reporting_month} already exists (id={existing_report.id})")
        else:
            report = MonthlyReport(**SAMPLE_REPORT)
            db.add(report)
            db.commit()
            db.refresh(report)
            print(f"+ Sample report submitted: id={report.id} for programme {report.programme_name} (reporting_month={report.reporting_month})")

        print("Seeding complete.")
    except Exception as exc:
        print("Error while seeding:", exc, file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
