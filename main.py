from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from app.core.security import hash_password
from app.database import create_db_tables, get_session
from app.models import (  # noqa: F401 — populate Base.metadata
    Alert,
    Driver,
    Intervention,
    User,
    UserRole,
    Vehicle,
)
from app.routers import alerts, auth, drivers, interventions, vehicles

_TEST_ACCOUNTS = [
    {
        "username": "admin",
        "email": "admin@secup.gn",
        "password": "Admin@2026!",
        "role": UserRole.admin,
    },
    {
        "username": "supervisor",
        "email": "supervisor@secup.gn",
        "password": "Super@2026!",
        "role": UserRole.supervisor,
    },
    {
        "username": "agent1",
        "email": "agent1@secup.gn",
        "password": "Agent1@2026!",
        "role": UserRole.agent,
    },
]


def _seed_db() -> None:
    with next(get_session()) as session:
        for account in _TEST_ACCOUNTS:
            exists = (
                session.execute(
                    select(User).where(User.username == account["username"])
                )
                .scalars()
                .first()
            )
            if not exists:
                user = User(
                    username=account["username"],
                    email=account["email"],
                    hashed_password=hash_password(account["password"]),
                    role=account["role"],
                )
                session.add(user)
        session.commit()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    create_db_tables()
    _seed_db()
    yield


app = FastAPI(
    title="SecUp API",
    description="API REST pour la gestion des infractions routières",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehicles.router)
app.include_router(drivers.router)
app.include_router(alerts.router)
app.include_router(interventions.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
