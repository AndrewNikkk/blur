from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, validator


# Существующие модели (оставляем без изменений)
class UserRegister(BaseModel):
    login: str = Field(..., example="Bobor")
    password: str = Field(..., min_length=8, example="password123")


class UserLogin(BaseModel):
    login: str = Field(..., example="Bobor")
    password: str = Field(..., min_length=8, example="password123")


class UserResponse(BaseModel):
    id: int
    login: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshToken(BaseModel):
    refresh_token: str


class PasswordReset(BaseModel):
    login: str = Field(..., example="Bobor")


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8, example="newpassword123")


class FileUpload(BaseModel):
    filename: str
    size: int


class FileResponse(BaseModel):
    id: int
    filename: str
    original_filename: str
    file_size: int
    mime_type: str
    status: str
    user_id: Optional[int] = None
    session_id: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None  # Добавьте это поле
    processed_file_path: Optional[str] = None  # Добавьте это поле

    model_config = ConfigDict(from_attributes=True)


class FileProcess(BaseModel):
    file_id: int


class FileEdit(BaseModel):
    content: dict


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: int
    content: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    id: int
    user_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatWithMessages(BaseModel):
    id: int
    user_id: int | None
    created_at: datetime
    messages: list[MessageResponse]

    class Config:
        from_attributes = True


# ========== НОВЫЕ МОДЕЛИ ДЛЯ ФИЛЬТРАЦИИ И CRUD ==========


class FileStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    SAVED = "saved"


class DateFilter(str, Enum):
    TODAY = "today"
    WEEK = "week"
    MONTH = "month"


class SizeFilter(str, Enum):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class FileSort(str, Enum):
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    NAME_ASC = "name_asc"
    NAME_DESC = "name_desc"
    SIZE_DESC = "size_desc"
    SIZE_ASC = "size_asc"


class FileUpdate(BaseModel):
    original_filename: Optional[str] = Field(None, description="Новое название файла")

    @validator("original_filename")
    def validate_filename(cls, v):
        if v is not None:
            if len(v) > 255:
                raise ValueError("Filename too long (max 255 characters)")
            if any(char in v for char in '<>:"/\\|?*'):
                raise ValueError("Filename contains invalid characters")
        return v


class FileQueryParams(BaseModel):
    search: Optional[str] = Field(None, description="Поиск по названию файла")
    date_filter: Optional[DateFilter] = Field(None, description="Фильтр по дате")
    size_filter: Optional[SizeFilter] = Field(None, description="Фильтр по размеру")
    sort: FileSort = Field(FileSort.DATE_DESC, description="Сортировка")
    page: int = Field(1, ge=1, description="Номер страницы")
    per_page: int = Field(10, ge=1, le=50, description="Элементов на странице")


class PaginatedFileResponse(BaseModel):
    items: List[FileResponse]
    total: int
    page: int
    per_page: int
    total_pages: int

    class Config:
        from_attributes = True


class PresignedUrlResponse(BaseModel):
    url: str
    filename: str
    expires_in: int


class ExternalTipResponse(BaseModel):
    title: str
    content: str
    source: str
    fetched_at: datetime
    fallback: bool = False
