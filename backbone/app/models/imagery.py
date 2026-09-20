from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Imagery(Base):
    """
    Centralized entity for image/file management across the system.

    Provides consistent representation of images associated with fields and
    other entities. Supports multiple image types including ground photos,
    drone imagery, and satellite imagery. Stores metadata such as source,
    capture time, type, resolution, and storage information.

    Attributes:
        id: Primary key, auto-incrementing integer.
        field_id: Foreign key to fields.id (SET NULL on field deletion).
        storage_path: Path or key to the image in storage system.
        storage_type: Type of storage (local, minio, s3, etc.).
        storage_bucket: Bucket or container name for cloud storage.
        file_name: Original filename of the uploaded image.
        file_extension: File extension (jpg, png, tif, etc.).
        file_size_bytes: Size of the file in bytes.
        mime_type: MIME type of the file (image/jpeg, image/png, etc.).
        image_type: Type of imagery (ground_photo, drone, satellite, etc.).
        capture_time: Timestamp when the image was captured.
        resolution_m: Spatial resolution in meters (if applicable).
        spectral_bands: JSON field for spectral band information.
        width_pixels: Image width in pixels.
        height_pixels: Image height in pixels.
        source: Source of the image (drone_id, satellite_name, etc.).
        additional_metadata: JSON field for additional custom metadata.
        uploaded_at: Timestamp when the image was uploaded to storage.
        created_at: Timestamp when the imagery record was created.

    Relationships:
        field: Field this imagery is associated with (SET NULL on field deletion).
        satellite_observations: Observations that reference this imagery.
        diagnoses: Diagnoses that use this imagery.

    Cascade Behavior:
        Deleting a field sets field_id to NULL (imagery is preserved).
        Deleting imagery cascades to satellite_observations and diagnoses
        that reference it (SET NULL on those foreign keys).

    Indexes:
        field_id: Indexed for efficient field lookup.
        ix_imagery_field_type_capture: Composite index for field imagery queries.
        ix_imagery_type_created: Composite index for type-based queries.

    Storage:
        Images are stored in MinIO (S3-compatible) or local disk.
        storage_path contains the object key or file path.
        Use StorageService to upload, download, and delete images.

    Image Types:
        - ground_photo: Photos taken on the ground (field level)
        - drone: Aerial imagery from drones/UAVs
        - satellite: Satellite imagery from platforms
        - other: Custom imagery types
    """

    __tablename__ = "imagery"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int | None] = mapped_column(ForeignKey("fields.id", ondelete="SET NULL"), nullable=True, index=True)
    storage_path: Mapped[str] = mapped_column(String(512), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(50), nullable=False, default="local")
    storage_bucket: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_extension: Mapped[str] = mapped_column(String(50), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Float, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    image_type: Mapped[str] = mapped_column(String(50), nullable=False, default="ground_photo")
    capture_time: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    resolution_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    spectral_bands: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    width_pixels: Mapped[int | None] = mapped_column(Float, nullable=True)
    height_pixels: Mapped[int | None] = mapped_column(Float, nullable=True)
    source: Mapped[str | None] = mapped_column(String(255), nullable=True)
    additional_metadata: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    field = relationship("Field", backref="imagery_records")

    __table_args__ = (
        Index("ix_imagery_field_type_capture", "field_id", "image_type", "capture_time"),
        Index("ix_imagery_type_created", "image_type", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Imagery(id={self.id}, field_id={self.field_id}, image_type={self.image_type}, file_name={self.file_name})>"
