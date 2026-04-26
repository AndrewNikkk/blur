from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.db import delete_file_record, get_db, get_file_by_id, get_files_paginated, update_file
from app.model.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    DateFilter,
    FileResponse,
    FileSort,
    FileUpdate,
    PaginatedFileResponse,
    SizeFilter,
    UserResponse,
)


router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить профиль пользователя (требует авторизацию)"""
    return current_user


@router.get("/files", response_model=List[FileResponse])
async def get_profile_files(
    search: Optional[str] = Query(None, description="Поиск по названию файла"),
    date_filter: Optional[DateFilter] = Query(None, description="Фильтр по дате: today, week, month"),
    size_filter: Optional[SizeFilter] = Query(None, description="Фильтр по размеру"),
    sort: FileSort = Query(FileSort.DATE_DESC, description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=50, description="Количество элементов на странице"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Получить файлы пользователя с фильтрацией, поиском и пагинацией
    """
    files, total = get_files_paginated(
        db=db,
        user_id=current_user.id,
        search=search,
        date_filter=date_filter.value if date_filter else None,
        size_filter=size_filter.value if size_filter else None,
        sort=sort.value,
        page=page,
        per_page=per_page,
    )

    # Добавляем заголовки с информацией о пагинации
    return files


@router.get("/files/paginated", response_model=PaginatedFileResponse)
async def get_profile_files_paginated(
    search: Optional[str] = Query(None, description="Поиск по названию файла"),
    date_filter: Optional[DateFilter] = Query(None, description="Фильтр по дате: today, week, month"),
    size_filter: Optional[SizeFilter] = Query(None, description="Фильтр по размеру"),
    sort: FileSort = Query(FileSort.DATE_DESC, description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=50, description="Количество элементов на странице"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Получить файлы пользователя с фильтрацией, поиском и пагинацией (полный ответ с метаданными)
    """
    files, total = get_files_paginated(
        db=db,
        user_id=current_user.id,
        search=search,
        date_filter=date_filter.value if date_filter else None,
        size_filter=size_filter.value if size_filter else None,
        sort=sort.value,
        page=page,
        per_page=per_page,
    )

    total_pages = (total + per_page - 1) // per_page

    return PaginatedFileResponse(items=files, total=total, page=page, per_page=per_page, total_pages=total_pages)


@router.get("/files/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получить информацию о конкретном файле"""
    file = get_file_by_id(db, file_id)

    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверяем, что файл принадлежит текущему пользователю
    if file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return file


@router.patch("/files/{file_id}", response_model=FileResponse)
async def update_file_info(
    file_id: int,
    file_update: FileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновить информацию о файле (название)"""
    file = get_file_by_id(db, file_id)

    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверяем, что файл принадлежит текущему пользователю
    if file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Обновляем название если передано
    if file_update.original_filename is not None:
        file = update_file(db, file_id, original_filename=file_update.original_filename)

    return file


@router.delete("/files/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удалить файл"""
    file = get_file_by_id(db, file_id)

    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверяем, что файл принадлежит текущему пользователю
    if file.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Удаляем запись из БД
    delete_file_record(db, file_id)

    return None
