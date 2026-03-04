from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from app.models.alert import AlertStatus


class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: AlertStatus = AlertStatus.pending
    license_plate: Optional[str] = None


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AlertStatus] = None
    license_plate: Optional[str] = None
    is_resolved: Optional[bool] = None


class AlertRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: AlertStatus
    license_plate: Optional[str] = None
    is_resolved: bool
    is_deleted: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertListResponse(BaseModel):
    data: List[AlertRead]
    total: int
    skip: int
    limit: int
    pages: int
