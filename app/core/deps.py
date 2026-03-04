from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, is_blacklisted
from app.database import get_session
from app.models.user import User, UserRole

bearer = HTTPBearer()


def get_current_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)],
) -> str:
    return credentials.credentials


def get_current_user(
    token: Annotated[str, Depends(get_current_token)],
    session: Annotated[Session, Depends(get_session)],
) -> User:
    if is_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
        )

    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = session.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


def require_supervisor(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role not in (UserRole.supervisor, UserRole.admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Supervisor or admin required"
        )
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    if user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin required"
        )
    return user


# Typed aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentToken = Annotated[str, Depends(get_current_token)]
SupervisorUser = Annotated[User, Depends(require_supervisor)]
AdminUser = Annotated[User, Depends(require_admin)]
DbSession = Annotated[Session, Depends(get_session)]
