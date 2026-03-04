from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class DriverCreate(BaseModel):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    license_number: str
    license_category: Optional[str] = None
    license_expiry: Optional[date] = None
    national_id: Optional[str] = None


class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    license_number: Optional[str] = None
    license_category: Optional[str] = None
    license_expiry: Optional[date] = None
    national_id: Optional[str] = None


class DriverRead(BaseModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    city: Optional[str] = None
    phone: Optional[str] = None
    license_number: str
    license_category: Optional[str] = None
    license_expiry: Optional[date] = None
    national_id: Optional[str] = None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
