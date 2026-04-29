from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.db.session import get_db
from app.models.models import User, Organization, UserRiskScore
from app.schemas.schemas import UserOut, RiskScoreOut


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{org_slug}", response_model=list[UserOut])
async def list_users(
    org_slug: str,
    department: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute (
        select(Organization).where(Organization.slug == org_slug)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    query = """
        SELECT
            u.id, u.email, u.full_name, u.department, u.job_title, 
            u.employee_type, u.is_active,
            rs.overall_score, rs.sod_violation_count, rs.risk_label
        From users u
        LEFT JOIN (
            SELECT user_id, overall_score, sod_violation_count, risk_label
            FROM user_risk_scores
            WHERE (user_id, computed_at) IN (
                SELECT user_id, MAX(computed_at)
                FROM user_risk_scores
                GROUP BY user_id
            )
        ) rs ON rs.user_id = u.id
        WHERE u.org_id = :org_id AND u.is_active = TRUE
        ORDER BY rs.overall_score DESC
    """
    

    if department:
        query = query.replace(
            "ORDER BY", f"AND u.department = '{department}' ORDER BY"
        )

    result = await db.execute(text(query), {"org_id": org.id})
    return result.fetchall()

    return [
        {
            "id": str(r.id),
            "email": r.email,
            "full_name": r.full_name,
            "department": r.department,
            "job_title": r.job_title,
            "employee_type": r.employee_type,
            "is_active": r.is_active,
            "overall_score": float(r.overall_score) if r.overall_score else None,
            "sod_violation_count": r.sod_violation_count or 0,
            "risk_label": r.risk_label,
        }
        for r in rows
    ]


@router.get("/{org_slug}/{user_id}/risk", response_model=RiskScoreOut)
async def get_user_risk(
    org_slug: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserRiskScore)
        .where(UserRiskScore.user_id == user_id)
        .order_by(UserRiskScore.computed_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()
    if not score:
         raise HTTPException(status_code=404, detail="No risk score found for this user")
    return score