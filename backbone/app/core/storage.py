import io
from datetime import timedelta
from typing import Generator
from minio import Minio
from minio.error import S3Error
from app.core.config import settings

# Initialize MinIO client
minio_client = Minio(
    settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)


def init_storage() -> None:
    """
    Ensures that the default bucket exists on startup.
    """
    try:
        bucket = settings.MINIO_BUCKET_NAME
        if not minio_client.bucket_exists(bucket):
            minio_client.make_bucket(bucket)
            print(f"Bucket '{bucket}' created successfully.")
        else:
            print(f"Bucket '{bucket}' already exists.")
    except Exception as e:
        print(f"Failed to initialize MinIO bucket: {e}")


class StorageService:
    def __init__(self, client: Minio = minio_client, bucket_name: str = settings.MINIO_BUCKET_NAME):
        self.client = client
        self.bucket_name = bucket_name

    def upload_file(self, object_name: str, data: io.BytesIO, length: int, content_type: str = "application/octet-stream") -> str:
        """
        Uploads an object to MinIO and returns its object name.
        """
        try:
            self.client.put_object(
                self.bucket_name,
                object_name,
                data,
                length,
                content_type=content_type,
            )
            return object_name
        except S3Error as err:
            print(f"MinIO Upload Error: {err}")
            raise err

    def get_download_url(self, object_name: str, expires_delta_hours: int = 24) -> str:
        """
        Generates a pre-signed URL to download/view the file.
        """
        try:
            return self.client.get_presigned_url(
                "GET",
                self.bucket_name,
                object_name,
                expires=timedelta(hours=expires_delta_hours),
            )
        except S3Error as err:
            print(f"MinIO Get Presigned URL Error: {err}")
            raise err

    def delete_file(self, object_name: str) -> None:
        """
        Deletes an object from MinIO.
        """
        try:
            self.client.remove_object(self.bucket_name, object_name)
        except S3Error as err:
            print(f"MinIO Delete Error: {err}")
            raise err


def get_storage() -> Generator[StorageService, None, None]:
    """
    Dependency injection generator for storage operations.
    """
    yield StorageService()
