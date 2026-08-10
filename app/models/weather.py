from datetime import datetime
from sqlalchemy import String, DateTime, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base

class Weather(Base):
    __tablename__ = "weather"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=True)
    humidity: Mapped[float] = mapped_column(Float, nullable=True)
    rainfall: Mapped[float] = mapped_column(Float, nullable=True)
    forecast_rain: Mapped[float] = mapped_column(Float, nullable=True)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
