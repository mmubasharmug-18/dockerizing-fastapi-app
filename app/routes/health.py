from datetime import datetime, timezone

from fastapi import APIRouter

from app.models import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut, summary="Health check")
def health():
    return HealthOut(status="ok", timestamp=datetime.now(timezone.utc))
