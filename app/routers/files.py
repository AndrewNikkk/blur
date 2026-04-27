import logging
import re
import uuid
from datetime import datetime, timedelta
from io import BytesIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import (
    create_file,
    delete_file_record,
    get_db,
    get_file_by_id,
    get_files_by_session,
    get_files_paginated,
    update_file,
    update_file_status,
)
from app.core.s3 import s3_client
from app.model.models import User
from app.routers.auth import get_current_user
from app.schemas.schemas import (
    DateFilter,
    FileResponse,
    FileSort,
    PaginatedFileResponse,
    PresignedUrlResponse,
    SizeFilter,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])
security = HTTPBearer(auto_error=False)


def process_image_with_yolo(image_bytes: bytes):
    """Lazy proxy for processor import to keep startup lightweight and testable."""
    from app.core.processor import process_image_with_yolo as _process_image_with_yolo

    return _process_image_with_yolo(image_bytes)


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


def validate_file(file: UploadFile) -> tuple[str, int]:
    """Валидация типа и размера файла"""
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    if file_size > settings.MAX_FILE_SIZE:
        max_size_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        logger.warning(f"❌ File too large: {file_size} bytes (max: {settings.MAX_FILE_SIZE})")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"File too large. Max size: {max_size_mb:.0f}MB"
        )

    if file.content_type not in settings.ALLOWED_FILE_TYPES:
        logger.warning(f"❌ File type not allowed: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file.content_type}' not allowed. Allowed: {settings.ALLOWED_FILE_TYPES}",
        )

    return file.content_type, file_size


def generate_s3_key(filename: str) -> str:
    """Генерирует безопасный S3 ключ"""
    safe_filename = re.sub(r"[^\x00-\x7F]+", "_", filename or "unknown")
    file_extension = safe_filename.split(".")[-1] if "." in safe_filename else ""

    if file_extension:
        return f"uploads/{uuid.uuid4()}.{file_extension}"
    return f"uploads/{uuid.uuid4()}"


@router.post("/upload", response_model=FileResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Загрузка файла в S3/MinIO"""
    try:
        logger.info(
            f"📥 Upload request: filename={file.filename}, user={current_user.id if current_user else 'anonymous'}"
        )

        content_type, file_size = validate_file(file)
        file.file.seek(0)
        file_content = await file.read()
        logger.debug(f"📦 File read: {len(file_content)} bytes")

        session_id = None
        if not current_user:
            session_id = request.headers.get("X-Session-ID") if request else None
            if not session_id:
                session_id = str(uuid.uuid4())
                logger.debug(f"🆔 Generated new session_id: {session_id}")

        file_path = generate_s3_key(file.filename)
        logger.debug(f"🔑 Generated file_path: {file_path}")

        file_stream = BytesIO(file_content)
        s3_client.upload_file(file_data=file_stream, object_name=file_path, content_type=content_type)

        db_file = create_file(
            db=db,
            filename=file_path.split("/")[-1],
            original_filename=file.filename or "unknown",
            file_size=file_size,
            mime_type=content_type,
            file_path=file_path,
            user_id=current_user.id if current_user else None,
            session_id=session_id,
            status="uploaded",
        )

        logger.info(f"✅ File uploaded successfully: {db_file.id}")
        return db_file

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected upload error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")


@router.get("", response_model=List[FileResponse])
async def list_files(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    date_filter: Optional[DateFilter] = Query(None, description="Фильтр по дате"),
    size_filter: Optional[SizeFilter] = Query(None, description="Фильтр по размеру"),
    sort: FileSort = Query(FileSort.DATE_DESC, description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=50, description="Размер страницы"),
):
    """Получить список файлов пользователя с пагинацией"""
    try:
        if current_user:
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
        else:
            session_id = request.headers.get("X-Session-ID")
            if not session_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Session ID required for anonymous access"
                )
            files = get_files_by_session(db, session_id)
            if search:
                search_term = search.lower().strip()
                files = [f for f in files if search_term in (f.original_filename or "").lower()]
            if date_filter:
                now = datetime.now()
                today = datetime(now.year, now.month, now.day)
                if date_filter == DateFilter.TODAY:
                    files = [f for f in files if f.created_at and f.created_at >= today]
                elif date_filter == DateFilter.WEEK:
                    week_ago = today - timedelta(days=7)
                    files = [f for f in files if f.created_at and f.created_at >= week_ago]
                elif date_filter == DateFilter.MONTH:
                    month_ago = today - timedelta(days=30)
                    files = [f for f in files if f.created_at and f.created_at >= month_ago]
            if size_filter:
                if size_filter == SizeFilter.SMALL:
                    files = [f for f in files if f.file_size < 100 * 1024]
                elif size_filter == SizeFilter.MEDIUM:
                    files = [f for f in files if 100 * 1024 <= f.file_size < 1024 * 1024]
                elif size_filter == SizeFilter.LARGE:
                    files = [f for f in files if f.file_size >= 1024 * 1024]

            reverse = sort in (FileSort.DATE_DESC, FileSort.NAME_DESC, FileSort.SIZE_DESC)
            if sort in (FileSort.DATE_ASC, FileSort.DATE_DESC):
                files = sorted(files, key=lambda f: f.created_at or datetime.min, reverse=reverse)
            elif sort in (FileSort.NAME_ASC, FileSort.NAME_DESC):
                files = sorted(files, key=lambda f: (f.original_filename or "").lower(), reverse=reverse)
            else:
                files = sorted(files, key=lambda f: f.file_size or 0, reverse=reverse)

            total = len(files)
            start = (page - 1) * per_page
            end = start + per_page
            files = files[start:end]

        logger.info(f"✅ Listed {len(files)} files (total: {total})")
        return files

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error listing files: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to list files: {str(e)}")


@router.get("/paginated", response_model=PaginatedFileResponse)
async def list_files_paginated(
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
    search: Optional[str] = Query(None, description="Поиск по названию"),
    date_filter: Optional[DateFilter] = Query(None, description="Фильтр по дате"),
    size_filter: Optional[SizeFilter] = Query(None, description="Фильтр по размеру"),
    sort: FileSort = Query(FileSort.DATE_DESC, description="Сортировка"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(10, ge=1, le=50, description="Размер страницы"),
):
    """Получить список файлов с фильтрацией и метаданными пагинации"""
    files = await list_files(
        request=request,
        db=db,
        current_user=current_user,
        search=search,
        date_filter=date_filter,
        size_filter=size_filter,
        sort=sort,
        page=page,
        per_page=per_page,
    )

    if current_user:
        _, total = get_files_paginated(
            db=db,
            user_id=current_user.id,
            search=search,
            date_filter=date_filter.value if date_filter else None,
            size_filter=size_filter.value if size_filter else None,
            sort=sort.value,
            page=1,
            per_page=1,
        )
    else:
        session_id = request.headers.get("X-Session-ID")
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session ID required for anonymous access",
            )
        anon_files = get_files_by_session(db, session_id)
        # Reuse same filtering by asking first page with huge limit is unnecessary; do in-memory.
        if search:
            search_term = search.lower().strip()
            anon_files = [f for f in anon_files if search_term in (f.original_filename or "").lower()]
        if date_filter:
            now = datetime.now()
            today = datetime(now.year, now.month, now.day)
            if date_filter == DateFilter.TODAY:
                anon_files = [f for f in anon_files if f.created_at and f.created_at >= today]
            elif date_filter == DateFilter.WEEK:
                week_ago = today - timedelta(days=7)
                anon_files = [f for f in anon_files if f.created_at and f.created_at >= week_ago]
            elif date_filter == DateFilter.MONTH:
                month_ago = today - timedelta(days=30)
                anon_files = [f for f in anon_files if f.created_at and f.created_at >= month_ago]
        if size_filter:
            if size_filter == SizeFilter.SMALL:
                anon_files = [f for f in anon_files if f.file_size < 100 * 1024]
            elif size_filter == SizeFilter.MEDIUM:
                anon_files = [f for f in anon_files if 100 * 1024 <= f.file_size < 1024 * 1024]
            elif size_filter == SizeFilter.LARGE:
                anon_files = [f for f in anon_files if f.file_size >= 1024 * 1024]
        total = len(anon_files)

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return PaginatedFileResponse(
        items=files,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{file_id}", response_model=FileResponse)
async def get_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Получить информацию о файле"""
    file_record = get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return file_record


@router.post("/{file_id}/save", response_model=FileResponse)
async def save_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Пометить файл как сохраненный (после обработки)"""
    file_record = get_file_by_id(db, file_id)
    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    # Можно сохранять только обработанные файлы
    if not file_record.processed_file_path or file_record.status not in ("processed", "saved"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be processed before saving",
        )

    updated_file = update_file(
        db=db,
        file_id=file_id,
        status="saved",
    )
    if not updated_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return updated_file


@router.get("/{file_id}/download-url", response_model=PresignedUrlResponse)
async def get_download_url(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Получить pre-signed URL для скачивания файла"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        logger.warning(f"❌ File not found: id={file_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if current_user:
        if file_record.user_id != current_user.id:
            logger.warning(f"❌ Access denied: user={current_user.id}, file_owner={file_record.user_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            logger.warning("❌ Access denied: invalid session for anonymous user")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    file_path = file_record.file_path
    filename = file_record.original_filename

    if file_record.processed_file_path and file_record.status in ["processed", "saved"]:
        file_path = file_record.processed_file_path
        filename = f"processed_{file_record.original_filename}"

    if not file_path:
        logger.error(f"❌ No file_path for file {file_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")

    # Минимальная санитаризация для заголовка Content-Disposition.
    safe_filename = (filename or "file").replace('"', "'").replace("\n", " ").replace("\r", " ")
    content_disposition = f'attachment; filename="{safe_filename}"'

    url = s3_client.get_presigned_url(
        file_path,
        settings.PRESIGNED_URL_EXPIRY,
        response_content_disposition=content_disposition,
    )
    logger.info(f"✅ Generated download URL for file {file_id}")

    return PresignedUrlResponse(url=url, filename=filename, expires_in=settings.PRESIGNED_URL_EXPIRY)


@router.get("/{file_id}/view-url", response_model=PresignedUrlResponse)
async def get_view_url(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Получить pre-signed URL для просмотра файла (без attachment)"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        logger.warning(f"❌ File not found: id={file_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if current_user:
        if file_record.user_id != current_user.id:
            logger.warning(f"❌ Access denied: user={current_user.id}, file_owner={file_record.user_id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            logger.warning("❌ Access denied: invalid session for anonymous user")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    file_path = file_record.file_path
    filename = file_record.original_filename

    if file_record.processed_file_path and file_record.status in ["processed", "saved"]:
        file_path = file_record.processed_file_path
        filename = f"processed_{file_record.original_filename}"

    if not file_path:
        logger.error(f"❌ No file_path for file {file_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found in storage")

    url = s3_client.get_presigned_url(file_path, settings.PRESIGNED_URL_EXPIRY)
    logger.info(f"✅ Generated view URL for file {file_id}")

    return PresignedUrlResponse(
        url=url,
        filename=filename,
        expires_in=settings.PRESIGNED_URL_EXPIRY,
    )


@router.get("/{file_id}/download")
async def download_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Скачать файл (редирект на pre-signed URL)"""
    url_response = await get_download_url(file_id, request, db, current_user)
    return RedirectResponse(url=url_response.url)


@router.post("/{file_id}/process", response_model=FileResponse)
async def process_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Запустить обработку файла YOLO моделью"""
    try:
        file_record = get_file_by_id(db, file_id)

        if not file_record:
            raise HTTPException(status_code=404, detail="File not found")

        # Проверка прав доступа
        if current_user:
            if file_record.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
        else:
            session_id = request.headers.get("X-Session-ID")
            if not session_id or file_record.session_id != session_id:
                raise HTTPException(status_code=403, detail="Access denied")

        # Проверка, что файл изображение
        if not file_record.mime_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files can be processed with YOLO blur")

        # Обновляем статус на "processing"
        logger.info(f"⚙️ Starting processing for file: {file_id}")
        update_file_status(db=db, file_id=file_id, status="processing")

        # Получаем файл из MinIO
        logger.info(f"📥 Downloading file from MinIO: {file_record.file_path}")
        file_obj = BytesIO()
        s3_client.client.download_fileobj(Bucket=s3_client.bucket, Key=file_record.file_path, Fileobj=file_obj)
        file_obj.seek(0)

        # Обрабатываем изображение
        logger.info("🔍 Processing image with YOLO...")
        processed_content = process_image_with_yolo(file_obj.getvalue())

        if processed_content is None:
            raise Exception("Failed to process image")

        # Сохраняем обработанный файл в MinIO
        processed_key = f"processed/{uuid.uuid4()}_{file_record.original_filename}"
        logger.info(f"📤 Uploading processed file to MinIO: {processed_key}")

        processed_stream = BytesIO(processed_content)
        s3_client.upload_file(file_data=processed_stream, object_name=processed_key, content_type=file_record.mime_type)

        # Обновляем запись в БД
        updated_file = update_file(
            db=db,
            file_id=file_id,
            status="processed",
            processed_file_path=processed_key,
            processed_at=datetime.now(),
        )

        logger.info(f"✅ File {file_id} processed successfully")
        return updated_file

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error processing file {file_id}: {e}", exc_info=True)
        # Откат статуса при ошибке
        update_file_status(db=db, file_id=file_id, status="failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing failed: {str(e)}")


@router.delete("/{file_id}")
async def delete_file_endpoint(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    """Удалить файл из S3 и БД"""
    file_record = get_file_by_id(db, file_id)

    if not file_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    if current_user:
        if file_record.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    else:
        session_id = request.headers.get("X-Session-ID") if request else None
        if not session_id or file_record.session_id != session_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    if file_record.file_path:
        try:
            s3_client.delete_file(file_record.file_path)
        except HTTPException as e:
            logger.warning(f"⚠️ Failed to delete original file from S3: {e.detail}")

    if file_record.processed_file_path:
        try:
            s3_client.delete_file(file_record.processed_file_path)
        except HTTPException as e:
            logger.warning(f"⚠️ Failed to delete processed file from S3: {e.detail}")

    delete_file_record(db, file_id)
    logger.info(f"✅ File {file_id} deleted successfully")

    return {"message": "File deleted successfully"}
