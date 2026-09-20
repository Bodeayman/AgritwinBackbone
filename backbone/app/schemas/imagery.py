from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime


class ImageryBase(BaseModel):
    field_id: Optional[int] = Field(None, examples=[1])
    storage_path: str = Field(..., examples=["fields/1/sat_20260808_143012_a3f9.tif"])
    storage_type: str = Field("local", examples=["s3", "minio", "local", "azure"])
    storage_bucket: Optional[str] = Field(None, examples=["agritwin-images"])
    file_name: str = Field(..., examples=["sat_20260808_143012_a3f9.tif"])
    file_extension: str = Field(..., examples=["tif", "jpg", "png"])
    file_size_bytes: Optional[int] = Field(None, examples=[1048576])
    mime_type: Optional[str] = Field(None, examples=["image/tiff"])
    image_type: str = Field("ground_photo", examples=["satellite", "drone", "ground_photo", "microscopic"])
    capture_time: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:00Z"])
    resolution_m: Optional[float] = Field(None, examples=[10.0])
    spectral_bands: Optional[Dict[str, Any]] = Field(None, examples=[{"B4": "Red", "B8": "NIR"}])
    width_pixels: Optional[int] = Field(None, examples=[1024])
    height_pixels: Optional[int] = Field(None, examples=[1024])
    source: Optional[str] = Field(None, examples=["Sentinel-2A", "DJI Phantom 4"])
    additional_metadata: Optional[Dict[str, Any]] = Field(None, examples=[{"cloud_cover": 0.1, "sun_azimuth": 45.3}])


class ImageryCreate(ImageryBase):
    pass


class ImageryUpdate(BaseModel):
    field_id: Optional[int] = Field(None, examples=[1])
    storage_path: Optional[str] = Field(None, examples=["fields/1/sat_20260808_143012_a3f9.tif"])
    storage_type: Optional[str] = Field(None, examples=["s3", "minio", "local", "azure"])
    storage_bucket: Optional[str] = Field(None, examples=["agritwin-images"])
    file_name: Optional[str] = Field(None, examples=["sat_20260808_143012_a3f9.tif"])
    file_extension: Optional[str] = Field(None, examples=["tif", "jpg", "png"])
    file_size_bytes: Optional[int] = Field(None, examples=[1048576])
    mime_type: Optional[str] = Field(None, examples=["image/tiff"])
    image_type: Optional[str] = Field(None, examples=["satellite", "drone", "ground_photo", "microscopic"])
    capture_time: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:00Z"])
    resolution_m: Optional[float] = Field(None, examples=[10.0])
    spectral_bands: Optional[Dict[str, Any]] = Field(None, examples=[{"B4": "Red", "B8": "NIR"}])
    width_pixels: Optional[int] = Field(None, examples=[1024])
    height_pixels: Optional[int] = Field(None, examples=[1024])
    source: Optional[str] = Field(None, examples=["Sentinel-2A", "DJI Phantom 4"])
    additional_metadata: Optional[Dict[str, Any]] = Field(None, examples=[{"cloud_cover": 0.1, "sun_azimuth": 45.3}])


class ImageryOut(ImageryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    uploaded_at: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:01Z"])
    created_at: Optional[datetime] = Field(None, examples=["2026-08-08T08:30:01Z"])
