from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class VehicleCreate(BaseModel):
    license_plate: str
    vehicle_info: Optional[str] = None
    notes: Optional[str] = None
    status: str = "normal"
    event_type: Optional[str] = None
    driver_full_name: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_phone: Optional[str] = None


class VehicleUpdate(BaseModel):
    license_plate: Optional[str] = None
    vehicle_info: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    event_type: Optional[str] = None
    driver_full_name: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_phone: Optional[str] = None


class VehicleRead(BaseModel):
    id: int
    license_plate: str
    vehicle_info: Optional[str] = None
    notes: Optional[str] = None
    status: str
    event_type: Optional[str] = None
    driver_full_name: Optional[str] = None
    driver_license_number: Optional[str] = None
    driver_phone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BatchStatusUpdate(BaseModel):
    ids: List[int]
    status: str


class VehicleListResponse(BaseModel):
    items: List[VehicleRead]
    limit: int
    next_cursor: Optional[int] = None
    has_more: bool
