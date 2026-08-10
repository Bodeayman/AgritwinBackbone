from typing import Generic, Type, TypeVar, List, Optional, Any
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Base Repository pattern to encapsulate basic database operations.
        """
        self.model = model
        self.db = db

    def get(self, id: Any) -> Optional[ModelType]:
        """
        Get a record by its primary key ID.
        """
        return self.db.get(self.model, id)

    def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get multiple records with offset and limit pagination.
        """
        statement = select(self.model).offset(skip).limit(limit)
        return list(self.db.scalars(statement).all())

    def create(self, db_obj: ModelType) -> ModelType:
        """
        Persist a new record to the database.
        """
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, update_data: dict) -> ModelType:
        """
        Update fields on an existing record.
        """
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def remove(self, id: Any) -> Optional[ModelType]:
        """
        Remove a record by ID.
        """
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
