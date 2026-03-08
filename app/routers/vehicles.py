from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import or_, select

from app.core.deps import CurrentUser, DbSession
from app.models.vehicle import Vehicle
from app.schemas.vehicle import BatchStatusUpdate, VehicleCreate, VehicleListResponse, VehicleRead, VehicleUpdate

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


def _get_vehicle_or_404(vehicle_id: int, session: DbSession) -> Vehicle:
    vehicle = session.execute(
        select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.deleted_at.is_(None))
    ).scalars().first()
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.get("", response_model=VehicleListResponse)
def list_vehicles(
    _user: CurrentUser,
    session: DbSession,
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    cursor: Optional[int] = None,
    limit: int = 20,
) -> VehicleListResponse:
    stmt = select(Vehicle).where(Vehicle.deleted_at.is_(None)).order_by(Vehicle.id.desc())
    if status is not None:
        stmt = stmt.where(Vehicle.status == status)
    if event_type is not None:
        stmt = stmt.where(Vehicle.event_type == event_type)
    if cursor is not None:
        stmt = stmt.where(Vehicle.id < cursor)

    items = list(session.execute(stmt.limit(limit + 1)).scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    return VehicleListResponse(
        items=[VehicleRead.model_validate(v) for v in items],
        limit=limit,
        next_cursor=items[-1].id if has_more and items else None,
        has_more=has_more,
    )


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    body: VehicleCreate, _user: CurrentUser, session: DbSession
) -> Vehicle:
    if body.driver_license_number and session.execute(
        select(Vehicle).where(
            Vehicle.driver_license_number == body.driver_license_number,
            Vehicle.deleted_at.is_(None),
        )
    ).scalars().first():
        raise HTTPException(status_code=400, detail="License number already exists")
    vehicle = Vehicle(**body.model_dump())
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.get("/search", response_model=List[VehicleRead])
def search_vehicles(
    q: str,
    _user: CurrentUser,
    session: DbSession,
) -> list[Vehicle]:
    stmt = (
        select(Vehicle)
        .where(
            Vehicle.deleted_at.is_(None),
            or_(
                Vehicle.license_plate.contains(q),
                Vehicle.driver_full_name.contains(q),
                Vehicle.driver_license_number.contains(q),
            ),
        )
        .limit(10)
    )
    return list(session.execute(stmt).scalars().all())


@router.get("/by-license/{license_number}", response_model=VehicleRead)
def get_by_license(
    license_number: str, _user: CurrentUser, session: DbSession
) -> Vehicle:
    vehicle = (
        session.execute(
            select(Vehicle).where(
                Vehicle.driver_license_number == license_number,
                Vehicle.deleted_at.is_(None),
            )
        )
        .scalars()
        .first()
    )
    if not vehicle:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.patch("/batch-status", response_model=List[VehicleRead])
def batch_set_status(
    body: BatchStatusUpdate,
    _user: CurrentUser,
    session: DbSession,
) -> list[Vehicle]:
    vehicles = list(
        session.execute(
            select(Vehicle).where(
                Vehicle.id.in_(body.ids),
                Vehicle.deleted_at.is_(None),
            )
        ).scalars().all()
    )
    now = datetime.now(timezone.utc)
    for v in vehicles:
        v.status = body.status
        v.updated_at = now
        session.add(v)
    session.commit()
    for v in vehicles:
        session.refresh(v)
    return vehicles


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(vehicle_id: int, _user: CurrentUser, session: DbSession) -> Vehicle:
    return _get_vehicle_or_404(vehicle_id, session)


@router.put("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    vehicle_id: int,
    body: VehicleUpdate,
    _user: CurrentUser,
    session: DbSession,
) -> Vehicle:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(vehicle, field, value)
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(vehicle_id: int, _user: CurrentUser, session: DbSession) -> None:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    vehicle.deleted_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()


@router.patch("/{vehicle_id}/status", response_model=VehicleRead)
def set_status(
    vehicle_id: int,
    _user: CurrentUser,
    session: DbSession,
    status: str = Query(...),
) -> Vehicle:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    vehicle.status = status
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle
