from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession, SupervisorUser
from app.models.vehicle import Vehicle
from app.schemas.vehicle import SeizeRequest, VehicleCreate, VehicleRead, VehicleUpdate

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


def _get_vehicle_or_404(vehicle_id: int, session: DbSession) -> Vehicle:
    vehicle = session.get(Vehicle, vehicle_id)
    if not vehicle or vehicle.is_deleted:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return vehicle


@router.post("/", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(body: VehicleCreate, _user: CurrentUser, session: DbSession) -> Vehicle:
    vehicle = Vehicle(**body.model_dump())
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.get("/search", response_model=List[VehicleRead])
def search_vehicles(
    plate: str,
    _user: CurrentUser,
    session: DbSession,
) -> list[Vehicle]:
    stmt = (
        select(Vehicle)
        .where(Vehicle.license_plate.contains(plate), Vehicle.is_deleted == False)  # noqa: E712
        .limit(10)
    )
    return list(session.execute(stmt).scalars().all())


@router.get("/wanted", response_model=List[VehicleRead])
def list_wanted(
    _user: CurrentUser,
    session: DbSession,
) -> list[Vehicle]:
    stmt = select(Vehicle).where(Vehicle.is_wanted == True, Vehicle.is_deleted == False)  # noqa: E712
    return list(session.execute(stmt).scalars().all())


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
    vehicle.is_deleted = True
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()


@router.post("/{vehicle_id}/seize", response_model=VehicleRead)
def seize_vehicle(
    vehicle_id: int,
    body: SeizeRequest,
    user: CurrentUser,
    session: DbSession,
) -> Vehicle:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    vehicle.status = "seized"
    vehicle.seizure_reason = body.seizure_reason
    vehicle.seizure_location = body.seizure_location
    vehicle.seizure_date = datetime.now(timezone.utc)
    vehicle.seized_by_user_id = user.id
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.post("/{vehicle_id}/release", response_model=VehicleRead)
def release_vehicle(
    vehicle_id: int,
    _user: SupervisorUser,
    session: DbSession,
) -> Vehicle:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    if vehicle.status != "seized":
        raise HTTPException(status_code=400, detail="Vehicle is not seized")
    vehicle.status = "released"
    vehicle.release_date = datetime.now(timezone.utc)
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle


@router.patch("/{vehicle_id}/wanted", response_model=VehicleRead)
def mark_wanted(
    vehicle_id: int,
    is_wanted: bool = Query(...),
    _user: SupervisorUser = None,
    session: DbSession = None,
) -> Vehicle:
    vehicle = _get_vehicle_or_404(vehicle_id, session)
    vehicle.is_wanted = is_wanted
    vehicle.updated_at = datetime.now(timezone.utc)
    session.add(vehicle)
    session.commit()
    session.refresh(vehicle)
    return vehicle
