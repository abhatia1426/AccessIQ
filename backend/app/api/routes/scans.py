from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Organization, Scan
from app.schemas.schemas import ScanOut
from app.services.analysis import run_scan


router = APIRouter(prefix="/scans", tags=["scans"])

@router.post("/{org_slug}/run", response_model=ScanOut)
async def trigger_scan(
    org_slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Trigger a full governence scan for an org.
    Runs SoD detection, peer analysis, and risk scoring
    for every user in the org.
    """
    result = await db.execute(
        select(Organization).where(Organization.slug == org_slug)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")

    scan = await run_scan(db, org.id)
    return scan


@router.get("/{org_slug}", response_model=list[ScanOut])
async def list_scans(
    org_slug: str,
    db: AsyncSession = Depends(get_db),
):
    """ Get all past scans for an org, most recent first."""
    result = await db.execute(
        select(Organization).where(Organization.slug == org_slug)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    
    result = await db.execute(
        select(Scan)
        .where(Scan.org_id == org.id)
        .order_by(Scan.started_at.desc())
    )

    return result.scalars().all()