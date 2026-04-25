from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class OrgCreate(BaseModel):
    name: str
    slug: str

class OrgOut(BaseModel):
    id: str
    name: str
    slug: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    id: str
    email:str
    full_name: str
    department: Optional[str]
    job_title: Optional[str]
    employee_type: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class IngestResult(BaseModel):
    success: bool
    message: str
    stats: dict

class RiskScoreOut(BaseModel):
    user_id: str
    overall_score: float
    overprov_score: Optional[float]
    sod_score: Optional[float]
    permission_count: Optional[int]
    peer_avg_score: Optional[float]
    sod_violation_count: int
    risk_label: Optional[str]
    computed_at: datetime

    class Config:
        from_attributes = True


class ViolationOut(BaseModel):
    id: str
    user_id: str
    rule_name: Optional[str] = None
    permission_a_name: Optional[str] = None
    permission_b_name: Optional[str] = None
    severity: Optional[str] = None
    status: str
    detected_at: datetime

    class Config:
        from_attributes = True


class ScanOut(BaseModel):
    id: str
    status: str
    users_scanned: Optional[int]
    violtions_found: Optional[int]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AiReportOut(BaseModel):
    id: str
    report_type: str
    content: str
    created_at: datetime


    class Config:
        from_attributes: True