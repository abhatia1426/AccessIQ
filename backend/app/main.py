from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import get_settings
from app.api.routes import ingest, users

settings = get_settings()

app = FastAPI(
    title="AccessIQ API",
    description="AI-powered identity risk and entitlement analyzer",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")

@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}