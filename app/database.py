from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = "sqlite://"


class Base(DeclarativeBase):
    """Base class for SQLAlchemy database models."""


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

session_factory = sessionmaker(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session and close it afterward."""
    with session_factory() as session:
        yield session
