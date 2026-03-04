from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.vehicle import VehicleStatus, VehicleType


class VehicleCreate(BaseModel):
    license_plate: str
    make: str
    model: str
    year: int
    color: str
    vin: Optional[str] = None
    vehicle_type: VehicleType = VehicleType.voiture
    driver_id: Optional[int] = None
    is_wanted: bool = False


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    color: Optional[str] = None
    vin: Optional[str] = None
    vehicle_type: Optional[VehicleType] = None
    driver_id: Optional[int] = None
    is_wanted: Optional[bool] = None


class VehicleRead(BaseModel):
    id: int
    license_plate: str
    make: str
    model: str
    year: int
    color: str
    vin: Optional[str] = None
    vehicle_type: VehicleType
    status: VehicleStatus
    seizure_reason: Optional[str] = None
    seizure_date: Optional[datetime] = None
    seizure_location: Optional[str] = None
    release_date: Optional[datetime] = None
    driver_id: Optional[int] = None
    seized_by_user_id: Optional[int] = None
    is_wanted: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SeizeRequest(BaseModel):
    seizure_reason: str
    seizure_location: str
