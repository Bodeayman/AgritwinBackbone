import os
import io
import pytest
from fastapi import UploadFile, HTTPException
from app.core.local_storage import LocalDiskImageStorage, ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES


def test_local_disk_image_storage_save_valid(tmp_path):
    storage = LocalDiskImageStorage(base_path=str(tmp_path))

    file_bytes = b"fake-jpeg-image-binary-data"
    upload_file = UploadFile(
        filename="leaf_sample.jpg",
        file=io.BytesIO(file_bytes)
    )

    rel_path = storage.save_image(upload_file, category="diagnoses", field_id=42)
    assert "diagnoses/42" in rel_path.replace("\\", "/")
    assert rel_path.endswith(".jpg")

    # Verify file was actually saved to disk inside tmp_path
    saved_files = list((tmp_path / "diagnoses" / "42").glob("*.jpg"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == file_bytes


def test_local_disk_image_storage_invalid_extension(tmp_path):
    storage = LocalDiskImageStorage(base_path=str(tmp_path))

    upload_file = UploadFile(
        filename="malicious_script.exe",
        file=io.BytesIO(b"binary-content")
    )

    with pytest.raises(HTTPException) as exc_info:
        storage.save_image(upload_file, category="fields", field_id=1)
    assert exc_info.value.status_code == 400
    assert "Unsupported file type" in exc_info.value.detail


def test_local_disk_image_storage_oversized_file(tmp_path):
    storage = LocalDiskImageStorage(base_path=str(tmp_path))

    # File size exceeding max 20MB limit
    huge_bytes = b"X" * (MAX_FILE_SIZE_BYTES + 1024)
    upload_file = UploadFile(
        filename="huge_satellite.tif",
        file=io.BytesIO(huge_bytes)
    )

    with pytest.raises(HTTPException) as exc_info:
        storage.save_image(upload_file, category="fields", field_id=1)
    assert exc_info.value.status_code == 400
    assert "File size exceeds maximum allowed limit" in exc_info.value.detail
