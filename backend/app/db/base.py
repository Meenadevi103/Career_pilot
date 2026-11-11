"""SQLAlchemy DeclarativeBase declaration."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy 2.0 ORM models.

    All future database entities will inherit from this Base,
    allowing Alembic to auto-discover models for schema migrations.
    """

    pass
