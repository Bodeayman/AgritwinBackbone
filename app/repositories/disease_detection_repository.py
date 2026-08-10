from app.repositories.base import BaseRepository
from app.models.disease_detection import DiseaseDetection

class DiseaseDetectionRepository(BaseRepository[DiseaseDetection]):
    def __init__(self, db):
        super().__init__(DiseaseDetection, db)
