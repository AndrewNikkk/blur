from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db, get_files_by_user
from app.model.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import FileResponse, UserResponse


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить профиль пользователя (требует авторизацию)"""
    return current_user


@router.get("/files", response_model=list[FileResponse])
async def get_profile_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить файлы пользователя (требует авторизацию)"""
    files = get_files_by_user(db, current_user.id)
    return files
