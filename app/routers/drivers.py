from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.core.deps import CurrentUser, DbSession, SupervisorUser
from app.models.driver import Driver
from app.schemas.driver import DriverCreate, DriverRead, DriverUpdate

router = APIRouter(prefix="/api/drivers", tags=["drivers"])


def _get_driver_or_404(driver_id: int, session: DbSession) -> Driver:
    driver = session.get(Driver, driver_id)
    if not driver or driver.is_deleted:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.post("/", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
def create_driver(body: DriverCreate, _user: CurrentUser, session: DbSession) -> Driver:
    if (
        session.execute(
            select(Driver).where(Driver.license_number == body.license_number)
        )
        .scalars()
        .first()
    ):
        raise HTTPException(status_code=400, detail="License number already exists")
    driver = Driver(**body.model_dump())
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver


@router.get("/search", response_model=List[DriverRead])
def search_drivers(q: str, _user: CurrentUser, session: DbSession) -> list[Driver]:
    stmt = (
        select(Driver)
        .where(
            Driver.is_deleted == False,  # noqa: E712
            or_(
                Driver.first_name.contains(q),
                Driver.last_name.contains(q),
                Driver.license_number.contains(q),
                Driver.national_id.contains(q),
            ),
        )
        .limit(10)
    )
    return list(session.execute(stmt).scalars().all())


@router.get("/by-license/{license_number}", response_model=DriverRead)
def get_by_license(
    license_number: str, _user: CurrentUser, session: DbSession
) -> Driver:
    driver = (
        session.execute(
            select(Driver).where(
                Driver.license_number == license_number, Driver.is_deleted == False
            )  # noqa: E712
        )
        .scalars()
        .first()
    )
    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")
    return driver


@router.get("/{driver_id}", response_model=DriverRead)
def get_driver(driver_id: int, _user: CurrentUser, session: DbSession) -> Driver:
    return _get_driver_or_404(driver_id, session)


@router.put("/{driver_id}", response_model=DriverRead)
def update_driver(
    driver_id: int,
    body: DriverUpdate,
    _user: CurrentUser,
    session: DbSession,
) -> Driver:
    driver = _get_driver_or_404(driver_id, session)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(driver, field, value)
    driver.updated_at = datetime.now(timezone.utc)
    session.add(driver)
    session.commit()
    session.refresh(driver)
    return driver


@router.delete("/{driver_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_driver(driver_id: int, _user: SupervisorUser, session: DbSession) -> None:
    driver = _get_driver_or_404(driver_id, session)
    driver.is_deleted = True
    driver.updated_at = datetime.now(timezone.utc)
    session.add(driver)
    session.commit()
