from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class InterventionCreate(BaseModel):
    title: str
    description: Optional[str] = None
    license_plate: Optional[str] = None


class InterventionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    license_plate: Optional[str] = None


class InterventionRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    license_plate: Optional[str] = None
    is_deleted: bool
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InterventionListResponse(BaseModel):
    items: List[InterventionRead]
    limit: int
    next_cursor: Optional[int] = None
    has_more: bool
