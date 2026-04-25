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

    query = select(User).where(User.org_id == org.id, User.is_active == True)
    if department:
        query = query.where(User.department == department)
    
    result = await db.execute(query)
    return result.scalars().all()


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