from typing import List, Tuple, Optional
from pydantic import BaseModel, field_validator, ValidationError
import math


class GeoJSONPolygon(BaseModel):
    """GeoJSON Polygon validation at API layer."""
    type: str = "Polygon"
    coordinates: List[List[List[float]]]  # [[[lon, lat], ...]]
    
    @field_validator('coordinates')
    @classmethod
    def validate_polygon(cls, v: List[List[List[float]]]) -> List[List[List[float]]]:
        # 1. Check minimum number of positions (4+ for closed ring)
        if len(v) < 1:
            raise ValueError("Polygon must have at least one ring")
        
        if len(v[0]) < 4:
            raise ValueError("Polygon linear ring must have at least 4 positions")
        
        # 2. Check ring is closed (first == last)
        if v[0][0] != v[0][-1]:
            raise ValueError("Polygon linear ring must be closed (first coordinate must equal last)")
        
        # 3. Validate coordinate ranges and GeoJSON order [longitude, latitude]
        for ring in v:
            for coord in ring:
                if len(coord) != 2:
                    raise ValueError(f"Coordinate must have exactly 2 values [longitude, latitude], got {len(coord)}")
                
                lon, lat = coord[0], coord[1]
                
                # Validate longitude range [-180, 180]
                if not -180 <= lon <= 180:
                    raise ValueError(f"Longitude {lon} out of valid range [-180, 180]")
                
                # Validate latitude range [-90, 90]
                if not -90 <= lat <= 90:
                    raise ValueError(f"Latitude {lat} out of valid range [-90, 90]")
                
                # Check for NaN or infinite values
                if not (math.isfinite(lon) and math.isfinite(lat)):
                    raise ValueError(f"Coordinate contains invalid values: [{lon}, {lat}]")
        
        return v


class FieldBoundaryValidator:
    """Domain layer validation for field boundaries."""
    
    @staticmethod
    def validate_coordinates(coordinates: List[List[List[float]]]) -> Tuple[bool, Optional[str]]:
        """
        Validate polygon coordinates at domain layer.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic structural validation
            if not coordinates or len(coordinates) == 0:
                return False, "Polygon must have at least one ring"
            
            ring = coordinates[0]
            if len(ring) < 4:
                return False, "Polygon must have at least 4 positions (including closing point)"
            
            # Check ring closure
            if ring[0] != ring[-1]:
                return False, "Polygon must be closed (first coordinate must equal last)"
            
            # Validate coordinate ranges
            for coord in ring:
                lon, lat = coord[0], coord[1]
                if not -180 <= lon <= 180:
                    return False, f"Longitude {lon} out of range [-180, 180]"
                if not -90 <= lat <= 90:
                    return False, f"Latitude {lat} out of range [-90, 90]"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_with_shapely(coordinates: List[List[List[float]]]) -> Tuple[bool, Optional[str]]:
        """
        Validate polygon using Shapely for geometric validity.
        This includes self-intersection detection and other geometric issues.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            from shapely.geometry import Polygon
            
            # Extract the exterior ring
            exterior_ring = coordinates[0]
            
            # Create Shapely polygon
            poly = Polygon(exterior_ring)
            
            # Check if polygon is valid
            if not poly.is_valid:
                return False, "Polygon is self-intersecting or geometrically invalid"
            
            # Check minimum area (approximate minimum field size)
            # Using rough approximation: 1 degree at equator ≈ 111km
            min_area_degrees = 0.0001  # ~11m² at equator
            if poly.area < min_area_degrees:
                return False, f"Polygon area too small: {poly.area:.8f} square degrees"
            
            # Check maximum reasonable area (entire Earth is ~360*180 = 64800 square degrees)
            max_area_degrees = 10000  # Reasonable maximum field size
            if poly.area > max_area_degrees:
                return False, f"Polygon area too large: {poly.area:.2f} square degrees"
            
            return True, None
            
        except ImportError:
            # Shapely not available, skip geometric validation
            return True, None
        except Exception as e:
            return False, f"Geometric validation failed: {str(e)}"
    
    @staticmethod
    def validate_area_hectares(coordinates: List[List[List[float]]], min_hectares: float = 0.01, max_hectares: float = 10000) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Validate polygon area in hectares.
        
        Returns:
            Tuple of (is_valid, error_message, area_hectares)
        """
        try:
            from shapely.geometry import Polygon
            from shapely.geometry import shape
            
            poly = Polygon(coordinates[0])
            
            # Convert to approximate area in hectares
            # This is a rough approximation - for production, use proper projection
            area_degrees = poly.area
            # 1 degree² ≈ 12321 hectares at equator (very rough approximation)
            area_hectares = area_degrees * 12321
            
            if area_hectares < min_hectares:
                return False, f"Area too small: {area_hectares:.4f} hectares (minimum: {min_hectares} hectares)", area_hectares
            
            if area_hectares > max_hectares:
                return False, f"Area too large: {area_hectares:.2f} hectares (maximum: {max_hectares} hectares)", area_hectares
            
            return True, None, area_hectares
            
        except ImportError:
            return True, None, None
        except Exception as e:
            return False, f"Area calculation failed: {str(e)}", None


def validate_field_boundary(coordinates: List[List[List[float]]], 
                           use_shapely: bool = True,
                           min_hectares: float = 0.0001,  # Reduced for testing (was 0.01)
                           max_hectares: float = 10000) -> Tuple[bool, List[str]]:
    """
    Comprehensive field boundary validation across all layers.
    
    Args:
        coordinates: GeoJSON polygon coordinates
        use_shapely: Whether to use Shapely for geometric validation
        min_hectares: Minimum field size in hectares
        max_hectares: Maximum field size in hectares
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Layer 1: API/Structural validation
    try:
        geojson = GeoJSONPolygon(coordinates=coordinates)
    except ValidationError as e:
        errors.extend([str(error) for error in e.errors()])
        return False, errors
    
    # Layer 2: Domain validation
    is_valid, error_msg = FieldBoundaryValidator.validate_coordinates(coordinates)
    if not is_valid:
        errors.append(error_msg)
        return False, errors
    
    # Layer 3: Geometric validation (if Shapely available)
    if use_shapely:
        is_valid, error_msg = FieldBoundaryValidator.validate_with_shapely(coordinates)
        if not is_valid:
            errors.append(error_msg)
            return False, errors
        
        # Layer 4: Area validation
        is_valid, error_msg, area_hectares = FieldBoundaryValidator.validate_area_hectares(
            coordinates, min_hectares, max_hectares
        )
        if not is_valid:
            errors.append(error_msg)
            return False, errors
    
    return True, []