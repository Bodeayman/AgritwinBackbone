"""
Script to insert realistic mock data for testing the yield prediction endpoint.
Run this with: python insert_mock_data.py
"""

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.base import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.field import Field
from app.models.crop_cycle import CropCycle
from app.models.sensor_reading import SensorReading
from app.models.weather import Weather
from app.models.satellite import Satellite
from app.models.imagery import Imagery
from app.models.satellite_observation import SatelliteObservation
from app.models.ai_model import AIModel
from shapely.geometry import Point
import geoalchemy2

# Database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

def clear_existing_data():
    """Clear existing test data to avoid duplicates"""
    print("Clearing existing test data...")
    db.query(SatelliteObservation).delete()
    db.query(Imagery).delete()
    db.query(SensorReading).delete()
    db.query(Weather).delete()
    db.query(CropCycle).delete()
    db.query(Field).delete()
    db.query(Farm).delete()
    db.query(User).delete()
    db.query(Satellite).delete()
    db.query(AIModel).delete()
    db.commit()
    print("✓ Cleared existing data")

def insert_base_data():
    """Insert base entities (users, farms, satellites, AI models)"""
    print("Inserting base entities...")
    
    # User
    user = User(
        email="farmer@example.com",
        username="farmer",
        hashed_password="$2b$12$example_hash",  # Mock password
        full_name="Test Farmer",
        is_active=True
    )
    db.add(user)
    db.flush()
    
    # Farm
    farm = Farm(
        user_id=user.id,
        name="Green Valley Farm",
        location=geoalchemy2.shape.from_shape(Point(31.2357, 30.0444)),  # Cairo coordinates
        address="Cairo, Egypt",
        total_area_hectares=50.0
    )
    db.add(farm)
    db.flush()
    
    # Satellite
    satellite = Satellite(
        name="Sentinel-2A",
        operator="ESA",
        launch_date=datetime(2015, 6, 23),
        status="active",
        resolution_m=10.0,
        revisit_days=5,
        spectral_bands=["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B9", "B10", "B11", "B12"]
    )
    db.add(satellite)
    db.flush()
    
    # AI Model
    ai_model = AIModel(
        name="Vegetation_Extractor_v1",
        version="1.0.0",
        model_type="vegetation_analysis",
        description="Sentinel-2 vegetation index extraction model",
        accuracy=0.92,
        status="active"
    )
    db.add(ai_model)
    db.flush()
    
    print(f"✓ Created user: {user.username}")
    print(f"✓ Created farm: {farm.name}")
    print(f"✓ Created satellite: {satellite.name}")
    print(f"✓ Created AI model: {ai_model.name}")
    
    return user, farm, satellite, ai_model

def insert_field_with_crop_cycle(farm, satellite, ai_model):
    """Insert field with active crop cycle"""
    print("Inserting field with crop cycle...")
    
    # Field with polygon geometry (1 hectare square in Cairo)
    from shapely.geometry import Polygon
    polygon_coords = [(31.23, 30.04), (31.24, 30.04), (31.24, 30.05), (31.23, 30.05), (31.23, 30.04)]
    field = Field(
        farm_id=farm.id,
        name="North Field",
        location=geoalchemy2.shape.from_shape(Polygon(polygon_coords)),
        area_hectares=1.0,
        soil_type="clay_loam",
        irrigation_type="drip"
    )
    db.add(field)
    db.flush()
    
    # Active crop cycle
    crop_cycle = CropCycle(
        field_id=field.id,
        crop="Maize",
        planting_date=datetime(2024, 1, 15),
        expected_harvest_date=datetime(2024, 5, 15),
        status="active",
        planted_at=datetime(2024, 1, 15)
    )
    db.add(crop_cycle)
    db.flush()
    
    print(f"✓ Created field: {field.name} (ID: {field.id})")
    print(f"✓ Created crop cycle: {crop_cycle.crop}")
    
    return field, crop_cycle

def insert_time_series_data(field, satellite, ai_model, days=30):
    """Insert time series data for multiple days"""
    print(f"Inserting {days} days of time series data...")
    
    base_date = datetime(2024, 1, 15, 8, 0, 0)  # Start from Jan 15, 2024
    
    # Create imagery records first
    imagery_records = []
    for day in range(days):
        capture_date = base_date + timedelta(days=day)
        imagery = Imagery(
            field_id=field.id,
            storage_path=f"fields/{field.id}/imagery/satellite_image_{day:03d}.tif",
            storage_type="s3",
            storage_bucket="agritwin-bucket",
            file_name=f"satellite_image_{day:03d}.tif",
            file_extension="tif",
            file_size_bytes=1024000 + (day * 1000),
            mime_type="image/tiff",
            image_type="satellite",
            capture_time=capture_date,
            resolution_m=10.0,
            spectral_bands=["B4", "B8"],  # Red and NIR for NDVI
            width_pixels=10980,
            height_pixels=10980,
            source="Sentinel-2",
            additional_metadata={"cloud_cover": 5.0 + (day % 20)}
        )
        db.add(imagery)
        db.flush()
        imagery_records.append(imagery)
    
    # Insert sensor readings, weather, and satellite observations
    for day in range(days):
        current_date = base_date + timedelta(days=day)
        
        # Sensor reading (realistic values for maize)
        sensor = SensorReading(
            field_id=field.id,
            sensor_id=1,
            recorded_at=current_date,
            soil_moisture=45.0 + (day % 10) - 5.0,  # 40-50%
            soil_temperature=18.0 + (day % 5) + (current_date.month - 1),  # Seasonal variation
            air_temperature=20.0 + (day % 8) + (current_date.month - 1) * 2,
            humidity=60.0 + (day % 20),
            soil_ph=6.5 + (day % 3) * 0.1,
            electrical_conductivity=1.2 + (day % 5) * 0.1,
            n_level=40.0 + (day % 10),
            p_level=30.0 + (day % 8),
            k_level=35.0 + (day % 7)
        )
        db.add(sensor)
        
        # Weather data
        weather = Weather(
            field_id=field.id,
            temperature=22.0 + (day % 10) - 5.0,
            humidity=55.0 + (day % 30),
            rainfall=10.0 + (day % 15) if day % 3 == 0 else 0.0,  # Rain every 3 days
            forecast_rain=5.0 + (day % 10) if day % 4 == 0 else 0.0,
            pressure=1013.0 + (day % 10),
            recorded_at=current_date
        )
        db.add(weather)
        
        # Satellite observation with vegetation indices
        # Realistic NDVI values for maize (0.3-0.8)
        ndvi = 0.5 + (day % 40) * 0.01  # Gradual increase over time
        sat_obs = SatelliteObservation(
            field_id=field.id,
            satellite_id=satellite.id,
            model_id=ai_model.id,
            imagery_id=imagery_records[day].id,
            observation_type="processed",
            cloud_cover_pct=5.0 + (day % 15),
            ndvi=ndvi,
            ndmi=0.3 + ndvi * 0.4,  # Correlated with NDVI
            evi=0.4 + ndvi * 0.5,
            status="processed",
            captured_at=current_date,
            additional_metadata={
                "gndvi": ndvi - 0.05,
                "ndwi": 0.2 + ndvi * 0.3,
                "savi": 0.4 + ndvi * 0.4,
                "sun_azimuth": 45.0 + (day % 180),
                "sun_elevation": 30.0 + (day % 60)
            }
        )
        db.add(sat_obs)
    
    db.commit()
    print(f"✓ Inserted {days} sensor readings")
    print(f"✓ Inserted {days} weather records")
    print(f"✓ Inserted {days} satellite observations")
    print(f"✓ Inserted {days} imagery records")

def main():
    """Main function to insert all mock data"""
    print("=" * 50)
    print("INSERTING MOCK DATA FOR YIELD PREDICTION")
    print("=" * 50)
    
    try:
        # Clear existing data
        clear_existing_data()
        
        # Insert base entities
        user, farm, satellite, ai_model = insert_base_data()
        
        # Insert field with crop cycle
        field, crop_cycle = insert_field_with_crop_cycle(farm, satellite, ai_model)
        
        # Insert time series data (30 days)
        insert_time_series_data(field, satellite, ai_model, days=30)
        
        print("\n" + "=" * 50)
        print("✅ MOCK DATA INSERTION COMPLETE")
        print("=" * 50)
        print(f"\nField ID: {field.id}")
        print(f"Field Name: {field.name}")
        print(f"Crop: {crop_cycle.crop}")
        print(f"Data Range: 2024-01-15 to 2024-02-14")
        print(f"\nTest the endpoint:")
        print(f"GET http://localhost:8000/api/fields/{field.id}/yield-prediction-data?latest=true")
        print(f"GET http://localhost:8000/api/fields/{field.id}/yield-prediction-data?timestamp=2024-01-20T08:00:00Z")
        print(f"GET http://localhost:8000/api/fields/{field.id}/yield-prediction-data?from=2024-01-15T00:00:00Z&to=2024-01-31T23:59:59Z")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()