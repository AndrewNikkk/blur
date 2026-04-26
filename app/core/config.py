import os
from typing import List


class Settings:
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # JWT
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Password reset
    RESET_TOKEN_EXPIRE_HOURS = int(os.getenv("RESET_TOKEN_EXPIRE_HOURS", "24"))
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # S3/MinIO настройки (localhost, так как FastAPI на хосте)
    S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "file-processor")
    S3_SECURE = os.getenv("S3_SECURE", "false").lower() == "true"
    S3_REGION = os.getenv("S3_REGION", "us-east-1")

    # Ограничения файлов
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "52428800"))  # 50 MB
    ALLOWED_FILE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "text/plain",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ]

    # Pre-signed URL
    PRESIGNED_URL_EXPIRY = int(os.getenv("PRESIGNED_URL_EXPIRY", "3600"))

    # External API integration (API Ninjas)
    EXTERNAL_TIP_API_URL = os.getenv("EXTERNAL_TIP_API_URL", "https://api.api-ninjas.com/v1/facts")
    EXTERNAL_TIP_API_KEY = os.getenv("EXTERNAL_TIP_API_KEY", "mX09DflII1RMH5kSo6qpo7QJ1fltzivjkQRLTA2A")
    EXTERNAL_TIP_TIMEOUT_SEC = float(os.getenv("EXTERNAL_TIP_TIMEOUT_SEC", "3.0"))
    EXTERNAL_TIP_MAX_RETRIES = int(os.getenv("EXTERNAL_TIP_MAX_RETRIES", "2"))
    EXTERNAL_TIP_RATE_LIMIT_PER_MIN = int(os.getenv("EXTERNAL_TIP_RATE_LIMIT_PER_MIN", "30"))
    EXTERNAL_TIP_CACHE_TTL_SEC = int(os.getenv("EXTERNAL_TIP_CACHE_TTL_SEC", "300"))

    # Debug
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"


settings = Settings()
