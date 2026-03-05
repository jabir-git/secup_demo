from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentUser, DbSession
from app.models.intervention import Intervention
from app.models.user import UserRole
from app.schemas.intervention import (
    InterventionCreate,
    InterventionListResponse,
    InterventionRead,
    InterventionUpdate,
)

router = APIRouter(prefix="/api/interventions", tags=["interventions"])


def _get_intervention_or_404(
    intervention_id: int, user: CurrentUser, session: DbSession
) -> Intervention:
    item = session.get(Intervention, intervention_id)
    if not item or item.is_deleted:
        raise HTTPException(status_code=404, detail="Intervention not found")
    if user.role == UserRole.agent and item.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return item


@router.get("/", response_model=InterventionListResponse)
def list_interventions(
    user: CurrentUser,
    session: DbSession,
    cursor: Optional[int] = None,
    limit: int = 10,
) -> InterventionListResponse:
    stmt = (
        select(Intervention)
        .where(~Intervention.is_deleted)
        .order_by(Intervention.id.desc())
    )
    if user.role == UserRole.agent:
        stmt = stmt.where(Intervention.user_id == user.id)
    if cursor is not None:
        stmt = stmt.where(Intervention.id < cursor)

    items = list(session.execute(stmt.limit(limit + 1)).scalars().all())
    has_more = len(items) > limit
    if has_more:
        items = items[:limit]

    next_cursor = items[-1].id if has_more and items else None

    return InterventionListResponse(
        items=[InterventionRead.model_validate(i) for i in items],
        limit=limit,
        next_cursor=next_cursor,
        has_more=has_more,
    )


@router.post("/", response_model=InterventionRead, status_code=status.HTTP_201_CREATED)
def create_intervention(
    body: InterventionCreate, user: CurrentUser, session: DbSession
) -> Intervention:
    item = Intervention(**body.model_dump(), user_id=user.id)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.patch("/{intervention_id}", response_model=InterventionRead)
def update_intervention(
    intervention_id: int,
    body: InterventionUpdate,
    user: CurrentUser,
    session: DbSession,
) -> Intervention:
    item = _get_intervention_or_404(intervention_id, user, session)
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(item, field, value)
    item.updated_at = datetime.now(timezone.utc)
    session.add(item)
    session.commit()
    session.refresh(item)
    return item


@router.delete("/{intervention_id}")
def delete_intervention(
    intervention_id: int, user: CurrentUser, session: DbSession
) -> dict:
    item = _get_intervention_or_404(intervention_id, user, session)
    item.is_deleted = True
    item.updated_at = datetime.now(timezone.utc)
    session.add(item)
    session.commit()
    return {"message": "intervention deleted"}
