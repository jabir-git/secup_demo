framework=FastAPI
orm=SQLAlchemy 2.0 (DeclarativeBase, Mapped, mapped_column)
migrations=Alembic
schemas=Pydantic v2 (separate from ORM models, from_attributes=True)
auth=JWT via python-jose + bcrypt direct (no passlib) — access (60min) + refresh (7days) + in-memory blacklist
package-manager=UV
