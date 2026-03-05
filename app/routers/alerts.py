import math
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select

from app.core.deps import CurrentUser, DbSession
from app.models.alert import Alert
from app.models.user import UserRole
from app.schemas.alert import AlertCreate, AlertListResponse, AlertRead, AlertUpdate

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


def _get_alert_or_404(alert_id: int, user: CurrentUser, session: DbSession) -> Alert:
    alert = session.get(Alert, alert_id)
    if not alert or alert.is_deleted:
        raise HTTPException(status_code=404, detail="Alert not found")
    if user.role == UserRole.agent and alert.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return alert


@router.get("/", response_model=AlertListResponse)
def list_alerts(
    user: CurrentUser,
    session: DbSession,
    skip: int = 0,
    limit: int = 10,
    license_plate: Optional[str] = None,
) -> AlertListResponse:
    base = select(Alert).where(~Alert.is_deleted)
    if user.role == UserRole.agent:
        base = base.where(Alert.user_id == user.id)
    if license_plate:
        base = base.where(Alert.license_plate.contains(license_plate))

    total = session.execute(select(func.count()).select_from(base.subquery())).scalar_one()
    items = list(session.execute(base.offset(skip).limit(limit)).scalars().all())

    return AlertListResponse(
        data=[AlertRead.model_validate(a) for a in items],
        total=total,
        skip=skip,
        limit=limit,
        pages=math.ceil(total / limit) if limit else 1,
    )


@router.post("/", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
def create_alert(body: AlertCreate, user: CurrentUser, session: DbSession) -> Alert:
    alert = Alert(**body.model_dump(), user_id=user.id)
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.patch("/{alert_id}", response_model=AlertRead)
def update_alert(
    alert_id: int,
    body: AlertUpdate,
    user: CurrentUser,
    session: DbSession,
) -> Alert:
    alert = _get_alert_or_404(alert_id, user, session)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(alert, field, value)
    alert.updated_at = datetime.now(timezone.utc)
    session.add(alert)
    session.commit()
    session.refresh(alert)
    return alert


@router.delete("/{alert_id}")
def delete_alert(alert_id: int, user: CurrentUser, session: DbSession) -> dict:
    alert = _get_alert_or_404(alert_id, user, session)
    alert.is_deleted = True
    alert.updated_at = datetime.now(timezone.utc)
    session.add(alert)
    session.commit()
    return {"message": "alert deleted"}
