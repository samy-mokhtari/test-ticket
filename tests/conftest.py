from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_test_session_factory = sessionmaker(bind=_test_engine)


@pytest.fixture()
def testing_session_factory() -> Generator[
    sessionmaker[Session],
    None,
    None,
]:
    """Provide a clean database schema for one test."""
    Base.metadata.drop_all(bind=_test_engine)
    Base.metadata.create_all(bind=_test_engine)

    yield _test_session_factory

    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture()
def db_session(
    testing_session_factory: sessionmaker[Session],
) -> Generator[Session, None, None]:
    """Provide a database session for one test."""
    with testing_session_factory() as session:
        yield session


@pytest.fixture()
def client(
    testing_session_factory: sessionmaker[Session],
) -> Generator[TestClient, None, None]:
    """Provide an API client connected to the test database."""

    def override_get_db() -> Generator[Session, None, None]:
        with testing_session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
