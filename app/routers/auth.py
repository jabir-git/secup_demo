from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.core.deps import CurrentToken, CurrentUser, DbSession
from app.core.security import (
    blacklist_token,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserProfile,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _build_token_response(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
        user_id=user.id,
        username=user.username,
        email=user.email,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, session: DbSession) -> TokenResponse:
    if session.execute(select(User).where(User.username == body.username)).scalars().first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if session.execute(select(User).where(User.email == body.email)).scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _build_token_response(user)


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, session: DbSession) -> TokenResponse:
    user: User | None = None
    if body.username:
        user = session.execute(select(User).where(User.username == body.username)).scalars().first()
    elif body.email:
        user = session.execute(select(User).where(User.email == body.email)).scalars().first()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Account is disabled")

    return _build_token_response(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, session: DbSession) -> TokenResponse:
    payload = decode_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = session.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found")

    return _build_token_response(user)


@router.post("/logout")
def logout(token: CurrentToken, _user: CurrentUser) -> dict:
    blacklist_token(token)
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserProfile)
def get_me(user: CurrentUser) -> User:
    return user


@router.put("/me", response_model=UserProfile)
def update_me(body: UpdateProfileRequest, user: CurrentUser, session: DbSession) -> User:
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
