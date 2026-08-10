# Placeholder LocationService
# In a full implementation this would handle geolocation logic for farms/fields.
# For now we provide a minimal class to satisfy imports.

class LocationService:
    def __init__(self, db, storage):
        self.db = db
        self.storage = storage

    # Example method signatures
    def get_location(self, location_id: str):
        """Retrieve location details (not implemented)."""
        raise NotImplementedError("LocationService.get_location is not implemented")

    def create_location(self, data):
        """Create a new location (not implemented)."""
        raise NotImplementedError("LocationService.create_location is not implemented")
