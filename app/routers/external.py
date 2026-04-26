from fastapi import APIRouter

from app.schemas.schemas import ExternalTipResponse
from app.services.external_tip_service import fetch_privacy_tip


router = APIRouter(prefix="/external", tags=["external"])


@router.get("/privacy-tip", response_model=ExternalTipResponse)
async def get_privacy_tip():
    return fetch_privacy_tip()
