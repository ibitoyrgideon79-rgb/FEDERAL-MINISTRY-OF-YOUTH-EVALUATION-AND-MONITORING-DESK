from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import date

class OTPRequest(BaseModel):
    email: EmailStr

class OTPVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)

class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True

class ProgrammeOut(BaseModel):
    id: int
    name: str
    department: str
    description: Optional[str] = None
    recipient_email: Optional[EmailStr] = None

    class Config:
        from_attributes = True

class ProgrammeUpdate(BaseModel):
    description: Optional[str] = None
    recipient_email: EmailStr

class FormLinkRequest(BaseModel):
    programme_id: int = Field(..., ge=1)

class PublicFormSubmission(BaseModel):
    programme_name: str
    focal_department: Optional[str]
    focal_aide_hm: Optional[str]
    focal_ministry_official: Optional[str]
    reporting_month: date
    programme_launch_date: Optional[date]
    total_youth_registered: int = Field(..., ge=0)
    youth_trained: int = Field(..., ge=0)
    youth_funded: int = Field(..., ge=0)
    youth_with_outcomes: int = Field(..., ge=0)
    partnerships: Optional[str]
    challenges: Optional[str]
    mitigation_strategies: Optional[str]
    scale_up_plans: Optional[str]
    success_story: Optional[str]

    @validator("youth_trained")
    def check_trained_not_more_than_registered(cls, v, values):
        if "total_youth_registered" in values and v > values["total_youth_registered"]:
            raise ValueError("youth_trained cannot exceed total_youth_registered")
        return v

class FormSubmissionOut(BaseModel):
    id: int
    programme_id: Optional[int]
    recipient_email: EmailStr
    form_data: dict
    submitted_at: Optional[str]

    class Config:
        from_attributes = True

class MonthlyReportCreate(BaseModel):
    programme_name: str
    focal_department: Optional[str]
    focal_aide_hm: Optional[str]
    focal_ministry_official: Optional[str]
    reporting_month: date
    programme_launch_date: Optional[date]
    total_youth_registered: int = Field(..., ge=0)
    youth_trained: int = Field(..., ge=0)
    youth_funded: int = Field(..., ge=0)
    youth_with_outcomes: int = Field(..., ge=0)
    partnerships: Optional[str]
    challenges: Optional[str]
    mitigation_strategies: Optional[str]
    scale_up_plans: Optional[str]
    success_story: Optional[str]

    @validator("youth_trained")
    def check_trained_not_more_than_registered(cls, v, values):
        if "total_youth_registered" in values and v > values["total_youth_registered"]:
            raise ValueError("youth_trained cannot exceed total_youth_registered")
        return v

class MonthlyReportOut(MonthlyReportCreate):
    id: int
    submitted_by: Optional[str]
    created_at: Optional[str]

    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    total_youth_registered: int
    total_trained: int
    training_percentage: float
    total_youth_funded: int
    total_youth_with_outcomes: int
    total_reports: int
