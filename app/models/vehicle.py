from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class VehicleType(str, Enum):
    voiture = "voiture"
    moto = "moto"
    camion = "camion"
    bus = "bus"
    taxi = "taxi"


class VehicleStatus(str, Enum):
    active = "active"
    seized = "seized"
    released = "released"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    license_plate: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    color: Mapped[str] = mapped_column(String(50), nullable=False)
    vin: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    vehicle_type: Mapped[VehicleType] = mapped_column(default=VehicleType.voiture, nullable=False)
    status: Mapped[VehicleStatus] = mapped_column(default=VehicleStatus.active, nullable=False)
    seizure_reason: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    seizure_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    seizure_location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    release_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    driver_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("drivers.id"), nullable=True)
    seized_by_user_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    is_wanted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
