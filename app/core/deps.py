from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_token, is_blacklisted
from app.database import get_session
from app.models.user import User

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
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return user


# Typed aliases for cleaner route signatures
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentToken = Annotated[str, Depends(get_current_token)]
DbSession = Annotated[Session, Depends(get_session)]
