from fastapi import APIRouter, Depends

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.repository import get_communications

router = APIRouter(prefix="/communications", tags=["Communications"])


@router.post("/history")
async def get_history(
    device_ids: list[str], db=Depends(get_db), user=Depends(get_current_user)
):
    return await get_communications(db, device_ids)
