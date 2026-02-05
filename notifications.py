from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from database import get_db
from models import User, MonthlyReport
from utils.email import send_email

router = APIRouter(prefix="/notifications", tags=["notifications"])

# Keep track of notifications in memory (in production, use database)
notifications_store = {}

@router.get("/", response_model=list)
async def get_notifications(db: Session = Depends(get_db)):
    """
    Get all notifications for the current user
    Placeholder - returns empty for now
    """
    return []

@router.post("/send-reminders")
async def send_report_reminders(db: Session = Depends(get_db)):
    """
    Send reminders to users who haven't submitted reports for current month.
    This should be called by a scheduled task (e.g., cron job)
    """
    try:
        current_month = datetime.now().strftime("%Y-%m")
        
        # Get all users
        users = db.query(User).all()
        
        reminders_sent = 0
        
        for user in users:
            if user.role == "admin":
                continue
                
            # Check if user has submitted a report for current month
            existing_report = db.query(MonthlyReport).filter(
                MonthlyReport.submitted_by == user.id,
                func.strftime("%Y-%m", MonthlyReport.reporting_month) == current_month
            ).first()
            
            if not existing_report:
                # Send reminder email
                subject = f"Monthly Report Reminder - {current_month}"
                body = f"""
                Hello,

                This is a reminder that you haven't submitted your monthly report for {current_month} yet.

                Please visit your dashboard and submit your report as soon as possible.

                Dashboard Link: http://localhost:8000/dashboard.html

                Thank you!
                """
                
                try:
                    send_email(user.email, subject, body)
                    reminders_sent += 1
                except Exception as e:
                    print(f"Failed to send reminder to {user.email}: {e}")
        
        return {
            "status": "success",
            "reminders_sent": reminders_sent,
            "message": f"Sent {reminders_sent} reminder(s)"
        }
    
    except Exception as e:
        print(f"Error sending reminders: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders"
        )

@router.post("/notify-challenges")
async def notify_on_challenges(db: Session = Depends(get_db)):
    """
    Send notifications to admins when challenges are reported.
    This should be called when a report with significant challenges is submitted.
    """
    try:
        # Get all admins
        admins = db.query(User).filter(User.role == "admin").all()
        
        # Get recent reports with challenges
        one_week_ago = datetime.now() - timedelta(days=7)
        reports_with_challenges = db.query(MonthlyReport).filter(
            MonthlyReport.created_at >= one_week_ago,
            MonthlyReport.challenges.isnot(None)
        ).all()
        
        notifications_sent = 0
        
        for admin in admins:
            if reports_with_challenges:
                subject = f"Alert: {len(reports_with_challenges)} reports with challenges submitted"
                
                challenges_summary = "\n".join([
                    f"- {r.programme_name}: {r.challenges[:100]}..."
                    for r in reports_with_challenges[:5]
                ])
                
                body = f"""
                Hello Admin,

                {len(reports_with_challenges)} reports with challenges have been submitted this week:

                {challenges_summary}

                Please review these reports and provide necessary support.

                Admin Dashboard: http://localhost:8000/admin.html

                Thank you!
                """
                
                try:
                    send_email(admin.email, subject, body)
                    notifications_sent += 1
                except Exception as e:
                    print(f"Failed to send notification to {admin.email}: {e}")
        
        return {
            "status": "success",
            "notifications_sent": notifications_sent,
            "message": f"Sent {notifications_sent} notification(s)"
        }
    
    except Exception as e:
        print(f"Error sending challenge notifications: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notifications"
        )

@router.post("/notify-report-submitted")
async def notify_report_submitted(report_id: int, db: Session = Depends(get_db)):
    """
    Send notification to admins when a new report is submitted.
    """
    try:
        report = db.query(MonthlyReport).filter(MonthlyReport.id == report_id).first()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Get all admins
        admins = db.query(User).filter(User.role == "admin").all()
        
        notifications_sent = 0
        
        for admin in admins:
            subject = f"New Report Submitted: {report.programme_name}"
            body = f"""
            Hello Admin,

            A new monthly report has been submitted:

            Programme: {report.programme_name}
            Department: {report.focal_department}
            Month: {report.reporting_month}
            Youth Registered: {report.total_youth_registered}
            Youth Trained: {report.youth_trained}

            Please review this report and provide feedback if necessary.

            Admin Dashboard: http://localhost:8000/admin.html

            Thank you!
            """
            
            try:
                send_email(admin.email, subject, body)
                notifications_sent += 1
            except Exception as e:
                print(f"Failed to send notification to {admin.email}: {e}")
        
        return {
            "status": "success",
            "notifications_sent": notifications_sent,
            "message": f"Notified {notifications_sent} admin(s)"
        }
    
    except Exception as e:
        print(f"Error sending report submitted notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send notification"
        )
