from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter
from app.database import create_db_tables
from app.routers import auth, vehicles
from seed import seed_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator:
    create_db_tables()
    seed_database(
        reset=False,
        if_empty_only=True,
        users_count=12,
        vehicles_count=100,
    )
    yield


app = FastAPI(
    title="SecUp API",
    description="API REST pour la gestion des infractions routières",
    version="0.1.0",
    lifespan=lifespan,
    redirect_slashes=False,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(GZipMiddleware, minimum_size=500)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehicles.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
