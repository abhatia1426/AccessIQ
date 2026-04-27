from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.models import Organization
from app.schemas.schemas import IngestResult
from app.services.ingest import ingest_csv, IngestError

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/{org_slug}", response_model=IngestResult)
async def upload_identity_csv(
    org_slug: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Organization).where(Organization.slug == org_slug)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail=f"Org '{org_slug}' not found")

    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    

    csv_bytes = await file.read()
    try:
        stats = await ingest_csv(db, org.id, csv_bytes)
    except IngestError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return IngestResult(
        success=True,
        message=f"Successfully ingested identity data for {org.name}",
        stats=stats,
    )