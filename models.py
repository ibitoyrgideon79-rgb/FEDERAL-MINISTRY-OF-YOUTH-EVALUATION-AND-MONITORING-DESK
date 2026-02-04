from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, default="user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class OTP(Base):
    __tablename__ = "otps"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True, nullable=False)
    code = Column(String(6), nullable=False)
    used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Session(Base):
    __tablename__ = "sessions"
    token = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

class Programme(Base):
    __tablename__ = "programmes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    department = Column(String, nullable=False)

class MonthlyReport(Base):
    __tablename__ = "monthly_reports"
    id = Column(Integer, primary_key=True, index=True)
    programme_name = Column(String, nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    submitter = relationship("User", backref="reports")
    focal_department = Column(String, nullable=True)
    focal_aide_hm = Column(String, nullable=True)
    focal_ministry_official = Column(String, nullable=True)
    reporting_month = Column(Date, nullable=False)
    programme_launch_date = Column(Date, nullable=True)
    total_youth_registered = Column(Integer, nullable=False, default=0)
    youth_trained = Column(Integer, nullable=False, default=0)
    youth_funded = Column(Integer, nullable=False, default=0)
    youth_with_outcomes = Column(Integer, nullable=False, default=0)
    partnerships = Column(Text, nullable=True)
    challenges = Column(Text, nullable=True)
    mitigation_strategies = Column(Text, nullable=True)
    scale_up_plans = Column(Text, nullable=True)
    success_story = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
