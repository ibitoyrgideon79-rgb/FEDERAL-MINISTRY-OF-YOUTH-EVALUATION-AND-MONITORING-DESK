from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import MonthlyReportCreate, MonthlyReportOut, DashboardResponse
from models import MonthlyReport, User
from utils.auth_utils import get_current_user, require_admin

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=MonthlyReportOut)
def submit_report(payload: MonthlyReportCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # validate numeric fields are handled by Pydantic
        report_data = payload.dict()
        report_data["submitted_by"] = current_user.id
        report = MonthlyReport(**report_data)
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Trigger notification to admins (non-blocking, can be async in production)
        # Wrap in separate try-catch so errors don't prevent report submission
        try:
            from utils.email import send_email
            try:
                admins = db.query(User).filter(User.role == "admin").all()
                if admins:
                    for admin in admins:
                        subject = f"New Report Submitted: {report.programme_name}"
                        body = f"""Hello Admin,

A new monthly report has been submitted:

Programme: {report.programme_name}
Department: {report.focal_department}
Month: {report.reporting_month}
Youth Registered: {report.total_youth_registered}
Youth Trained: {report.youth_trained}

Please review this report and provide feedback if necessary.

Admin Dashboard: http://localhost:8000/admin.html

Thank you!"""
                        try:
                            send_email(admin.email, subject, body)
                        except Exception as e:
                            print(f"Failed to send notification to admin {admin.email}: {e}")
            except Exception as e:
                print(f"Error querying admins: {e}")
        except Exception as e:
            print(f"Error in notification process: {e}")
        
        return report
    except Exception as e:
        print(f"Error submitting report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit report: {str(e)}"
        )

@router.get("/", response_model=list[MonthlyReportOut])
def list_reports(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        reports = db.query(MonthlyReport).order_by(MonthlyReport.created_at.desc()).all()
    else:
        reports = db.query(MonthlyReport).filter(MonthlyReport.submitted_by == current_user.id).order_by(MonthlyReport.created_at.desc()).all()
    return reports

@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), admin_user=Depends(require_admin)):
    reports = db.query(MonthlyReport).all()
    total_registered = sum(r.total_youth_registered for r in reports)
    total_trained = sum(r.youth_trained for r in reports)
    total_funded = sum(r.youth_funded for r in reports)
    total_outcomes = sum(r.youth_with_outcomes for r in reports)
    total_reports = len(reports)
    training_percentage = (total_trained / total_registered * 100) if total_registered > 0 else 0.0
    return {
        "total_youth_registered": total_registered,
        "total_trained": total_trained,
        "training_percentage": round(training_percentage, 2),
        "total_youth_funded": total_funded,
        "total_youth_with_outcomes": total_outcomes,
        "total_reports": total_reports,
    }
