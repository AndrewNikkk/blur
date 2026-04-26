import logging
from typing import BinaryIO, Optional

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError, EndpointConnectionError
from fastapi import HTTPException, status

from app.core.config import settings


logger = logging.getLogger(__name__)


class LazyS3Client:
    """Клиент с ленивой инициализацией — подключается только при первом использовании"""

    def __init__(self):
        self._client: Optional[boto3.client] = None
        self.bucket = settings.S3_BUCKET_NAME

    @property
    def client(self) -> boto3.client:
        if self._client is None:
            logger.info(f"🔌 Initializing S3 connection to {settings.S3_ENDPOINT}...")
            try:
                self._client = boto3.client(
                    "s3",
                    endpoint_url=settings.S3_ENDPOINT,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    use_ssl=settings.S3_SECURE,
                    config=Config(
                        signature_version="s3v4",
                        s3={"addressing_style": "path"},
                        connect_timeout=5,
                        read_timeout=30,
                        retries={"max_attempts": 2},
                    ),
                    region_name=settings.S3_REGION,
                )
                self._ensure_bucket_exists()
                logger.info("✅ S3 connection established")
            except EndpointConnectionError as e:
                logger.error(f"❌ Connection failed: {e}")
                raise RuntimeError(
                    f"Cannot connect to MinIO at {settings.S3_ENDPOINT}. "
                    "Check that MinIO is running and port 9000 is accessible."
                ) from e
        return self._client

    def _ensure_bucket_exists(self) -> None:
        try:
            self._client.head_bucket(Bucket=self.bucket)
            logger.debug(f"✅ Bucket '{self.bucket}' exists")
        except ClientError as e:
            code = e.response.get("Error", {}).get("Code")
            if code in ("403", "404"):
                logger.info(f"📦 Creating bucket: {self.bucket}")
                self._client.create_bucket(Bucket=self.bucket)
                logger.info(f"✅ Bucket '{self.bucket}' created")
            else:
                logger.error(f"❌ Bucket check failed: {code}")
                raise

    def upload_file(self, file_data: BinaryIO, object_name: str, content_type: str) -> str:
        try:
            logger.info(f"📤 Uploading: {self.bucket}/{object_name} ({content_type})")

            self.client.upload_fileobj(file_data, self.bucket, object_name, ExtraArgs={"ContentType": content_type})

            logger.info(f"✅ Uploaded: {object_name}")
            return object_name

        except EndpointConnectionError as e:
            logger.error(f"❌ Network error: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Storage service unavailable. Please try again later.",
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"❌ S3 error [{error_code}]: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"S3 upload failed: {error_msg}"
            )
        except Exception as e:
            logger.error(f"❌ Unexpected upload error: {e}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Upload failed: {str(e)}")

    def get_presigned_url(
        self,
        object_name: str,
        expires_in: int = None,
        response_content_disposition: str | None = None,
    ) -> str:
        if expires_in is None:
            expires_in = settings.PRESIGNED_URL_EXPIRY
        try:
            params = {"Bucket": self.bucket, "Key": object_name}
            if response_content_disposition:
                # Forces the browser to treat the response as a download.
                # Supported by S3-compatible storages like MinIO.
                params["ResponseContentDisposition"] = response_content_disposition
            url = self.client.generate_presigned_url("get_object", Params=params, ExpiresIn=expires_in)
            return url
        except ClientError as e:
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"❌ Presigned URL error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to generate download link: {error_msg}",
            )

    def delete_file(self, object_name: str) -> bool:
        try:
            logger.info(f"🗑️ Deleting: {self.bucket}/{object_name}")
            self.client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code == "NoSuchKey":
                logger.warning(f"⚠️ File already deleted: {object_name}")
                return True
            error_msg = e.response.get("Error", {}).get("Message", str(e))
            logger.error(f"❌ Delete error: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete file: {error_msg}"
            )


# Ленивый синглтон
s3_client = LazyS3Client()
