import uuid
from datetime import datetime
from sqlalchemy import (
    String, Boolean, Integer, SmallInteger, Numeric, Text,
    ForeignKey, UniqueConstraint, Index,
    DateTime, Date, BigInteger
)
from sqlalchemy.dialects.mysql import CHAR, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base


def gen_uuid():
    return str(uuid.uuid4())


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="org")
    applications: Mapped[list["Application"]] = relationship(back_populates="org")
    roles: Mapped[list["Role"]] = relationship(back_populates="org")
    sod_rules: Mapped[list["SodRule"]] = relationship(back_populates="org")
    scans: Mapped[list["Scan"]] = relationship(back_populates="org")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("org_id", "email"),
        Index("idx_users_org_dept", "org_id", "department"),
    )

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100))
    job_title: Mapped[str | None] = mapped_column(String(100))
    employee_type: Mapped[str] = mapped_column(String(50), default="employee")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hire_date: Mapped[datetime | None] = mapped_column(Date)
    last_login: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    org: Mapped["Organization"] = relationship(back_populates="users")
    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="user")
    risk_scores: Mapped[list["UserRiskScore"]] = relationship(back_populates="user")
    violations: Mapped[list["SodViolation"]] = relationship(back_populates="user")


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("org_id", "name"),)

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    app_type: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    org: Mapped["Organization"] = relationship(back_populates="applications")
    permissions: Mapped[list["Permission"]] = relationship(back_populates="app")
    roles: Mapped[list["Role"]] = relationship(back_populates="app")


class Permission(Base):
    __tablename__ = "permissions"
    __table_args__ = (UniqueConstraint("app_id", "name"),)

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    app_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("applications.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    risk_level: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    app: Mapped["Application"] = relationship(back_populates="permissions")
    role_permissions: Mapped[list["RolePermission"]] = relationship(back_populates="permission")


class Role(Base):
    __tablename__ = "roles"
    __table_args__ = (UniqueConstraint("org_id", "app_id", "name"),)

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    app_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("applications.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_privileged: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    org: Mapped["Organization"] = relationship(back_populates="roles")
    app: Mapped["Application"] = relationship(back_populates="roles")
    role_permissions: Mapped[list["RolePermission"]] = relationship(back_populates="role")
    assignments: Mapped[list["UserRoleAssignment"]] = relationship(back_populates="role")


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)

    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")


class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    __table_args__ = (UniqueConstraint("user_id", "role_id"),)

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    role_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("roles.id", ondelete="CASCADE"))
    assigned_by: Mapped[str | None] = mapped_column(CHAR(36))
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime)
    justification: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")

    user: Mapped["User"] = relationship(back_populates="role_assignments", foreign_keys=[user_id])
    role: Mapped["Role"] = relationship(back_populates="assignments")


class SodRule(Base):
    __tablename__ = "sod_rules"
    __table_args__ = (UniqueConstraint("org_id", "permission_a_id", "permission_b_id"),)

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    permission_a_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("permissions.id"))
    permission_b_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("permissions.id"))
    severity: Mapped[str] = mapped_column(String(20), default="high")
    compliance_standard: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    org: Mapped["Organization"] = relationship(back_populates="sod_rules")
    permission_a: Mapped["Permission"] = relationship(foreign_keys=[permission_a_id])
    permission_b: Mapped["Permission"] = relationship(foreign_keys=[permission_b_id])


class Scan(Base):
    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    org_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("organizations.id", ondelete="CASCADE"))
    triggered_by: Mapped[str | None] = mapped_column(CHAR(36))
    status: Mapped[str] = mapped_column(String(20), default="running")
    users_scanned: Mapped[int | None] = mapped_column(Integer)
    violations_found: Mapped[int | None] = mapped_column(Integer)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    org: Mapped["Organization"] = relationship(back_populates="scans")
    risk_scores: Mapped[list["UserRiskScore"]] = relationship(back_populates="scan")
    violations: Mapped[list["SodViolation"]] = relationship(back_populates="scan")
    ai_reports: Mapped[list["AiReport"]] = relationship(back_populates="scan")


class UserRiskScore(Base):
    __tablename__ = "user_risk_scores"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    scan_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("scans.id", ondelete="CASCADE"))
    overall_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    overprov_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    sod_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    privileged_score: Mapped[float | None] = mapped_column(Numeric(5, 2))
    permission_count: Mapped[int | None] = mapped_column(Integer)
    peer_avg_permissions: Mapped[float | None] = mapped_column(Numeric(8, 2))
    sod_violation_count: Mapped[int] = mapped_column(Integer, default=0)
    risk_label: Mapped[str | None] = mapped_column(String(20))
    computed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="risk_scores")
    scan: Mapped["Scan"] = relationship(back_populates="risk_scores")


class SodViolation(Base):
    __tablename__ = "sod_violations"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    scan_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("scans.id", ondelete="CASCADE"))
    user_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("users.id", ondelete="CASCADE"))
    rule_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("sod_rules.id"))
    permission_a_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("permissions.id"))
    permission_b_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("permissions.id"))
    via_role_a_id: Mapped[str | None] = mapped_column(CHAR(36))
    via_role_b_id: Mapped[str | None] = mapped_column(CHAR(36))
    status: Mapped[str] = mapped_column(String(20), default="open")
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="violations")
    scan: Mapped["Scan"] = relationship(back_populates="violations")
    rule: Mapped["SodRule"] = relationship()
    permission_a: Mapped["Permission"] = relationship(foreign_keys=[permission_a_id])
    permission_b: Mapped["Permission"] = relationship(foreign_keys=[permission_b_id])


class AiReport(Base):
    __tablename__ = "ai_reports"

    id: Mapped[str] = mapped_column(CHAR(36), primary_key=True, default=gen_uuid)
    scan_id: Mapped[str] = mapped_column(CHAR(36), ForeignKey("scans.id", ondelete="CASCADE"))
    user_id: Mapped[str | None] = mapped_column(CHAR(36), ForeignKey("users.id"))
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    model_used: Mapped[str | None] = mapped_column(String(100))
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    scan: Mapped["Scan"] = relationship(back_populates="ai_reports")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    org_id: Mapped[str] = mapped_column(CHAR(36), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(CHAR(36))
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100))
    entity_id: Mapped[str | None] = mapped_column(CHAR(36))
    old_value: Mapped[dict | None] = mapped_column(JSON)
    new_value: Mapped[dict | None] = mapped_column(JSON)
    ip_address: Mapped[str | None] = mapped_column(String(45))
    occurred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)