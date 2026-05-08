from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional

from app.db.session import get_db
from app.models.models import User, Organization, UserRiskScore
from app.schemas.schemas import UserOut, RiskScoreOut


router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{org_slug}")
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
    rows = result.fetchall()

    return [
        {
            "id": str(r[0]),
            "email": r[1],
            "full_name": r[2],
            "department": r[3],
            "job_title": r[4],
            "employee_type": r[5],
            "is_active": bool(r[6]),
            "overall_score": float(r[7]) if r[7] else None,
            "sod_violation_count": r[8] or 0,
            "risk_label": r[9],
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