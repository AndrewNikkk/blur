import uuid

from fastapi import APIRouter, Depends
from fastapi import File as FastAPIFile
from fastapi import HTTPException, Request, UploadFile, status
from fastapi.responses import FileResponse as FastAPIFileResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import (
    create_file,
    delete_file_record,
    get_db,
    get_file_by_id,
    get_files_by_session,
    get_files_by_user,
    update_file_status,
)
from app.core.processor import process_file
from app.core.storage import delete_file, get_file_path, save_uploaded_file
from app.model.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import FileResponse


router = APIRouter(prefix="/files", tags=["files"])
security = HTTPBearer(auto_error=False)  # auto_error=False для опциональной авторизации


def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """Получить пользователя, если авторизован, иначе None"""
    if not credentials:
        return None
    try:
        return get_current_user(credentials, db)
    except Exception:
        return None


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = FastAPIFile(...),
    request: Request = None,  # ДОБАВИТЬ - для получения заголовков
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Загрузка файла (доступно всем - авторизованным и неавторизованным)"""
    try:
        file_content = await file.read()
        file_size = len(file_content)

        if file_size == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

        # Сохраняем файл на диск
        filename, file_path = save_uploaded_file(file_content, file.filename)

        # Определяем session_id для неавторизованных
        # Проверяем заголовок X-Session-ID, если нет - генерируем новый
        if current_user:
            session_id = None
        else:
            session_id = request.headers.get("X-Session-ID") if request else None
            if not session_id:
                session_id = str(uuid.uuid4())

        # Создаем запись в БД
        db_file = create_file(
            db=db,
            filename=filename,
            original_filename=file.filename or "unknown",
            file_path=file_path,
            file_size=file_size,
            mime_type=file.content_type or "application/octet-stream",
            user_id=current_user.id if current_user else None,
            session_id=session_id,
        )

        return db_file

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error uploading file: {str(e)}")


@router.get("", response_model=list[FileResponse])
async def get_files(
    request: Request = None,  # ДОБАВИТЬ
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Получить список файлов"""
    if current_user:
        files = get_files_by_user(db, current_user.id)
    else:
        # Для неавторизованных получаем session_id из заголовка
        session_id = request.headers.get("X-Session-ID") if request else None
        if session_id:
            files = get_files_by_session(db, session_id)
        else:
            files = []

    return files


@router.get("/{file_id}", response_model=FileResponse)
async def get_file_info(
    file_id: int,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Получить информацию о файле"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверка доступа
    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        # Для неавторизованных получаем session_id из заголовка
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return file_record


@router.post("/{file_id}/process", response_model=FileResponse)
async def process_file_endpoint(
    file_id: int,
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Обработать файл"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверка доступа
    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if file_record.status != "uploaded":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File already processed. Current status: {file_record.status}",
        )

    # Обновляем статус на "processing"
    update_file_status(db, file_id, "processing")

    try:
        # Обрабатываем файл
        processed_path = process_file(file_record.file_path)

        if not processed_path:
            update_file_status(db, file_id, "uploaded")  # Откатываем статус
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process file")

        # Обновляем статус на "processed"
        updated_file = update_file_status(db, file_id, "processed", processed_path)

        return updated_file

    except HTTPException:
        raise
    except Exception as e:
        update_file_status(db, file_id, "uploaded")  # Откатываем статус при ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error processing file: {str(e)}"
        )


@router.post("/{file_id}/save", response_model=FileResponse)
async def save_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # Требует авторизацию
):
    """Сохранить обработанный файл (только для авторизованных)"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if file_record.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if file_record.status != "processed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is not processed. Current status: {file_record.status}",
        )

    updated_file = update_file_status(db, file_id, "saved")
    return updated_file


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Скачать файл"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверка доступа
    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Определяем путь к файлу
    if file_record.status == "processed" and file_record.processed_file_path:
        file_path = get_file_path(file_record.processed_file_path)
        download_filename = f"processed_{file_record.original_filename}"
    else:
        file_path = get_file_path(file_record.file_path)
        download_filename = file_record.original_filename

    if not file_path or not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found on disk")

    return FastAPIFileResponse(path=str(file_path), filename=download_filename, media_type=file_record.mime_type)


@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: int,
    session_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    """Удалить файл"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    # Проверка доступа
    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Удаляем файлы с диска
    if file_record.file_path:
        delete_file(file_record.file_path)
    if file_record.processed_file_path:
        delete_file(file_record.processed_file_path)

    # Удаляем запись из БД
    delete_file_record(db, file_id)

    return {"message": "File deleted successfully"}
