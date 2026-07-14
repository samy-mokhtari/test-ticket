from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import engine, get_db, session_factory


def test_database_uses_sqlite_in_memory() -> None:
    assert engine.url.drivername == "sqlite"
    assert engine.url.database is None


def test_database_accepts_queries() -> None:
    with session_factory() as session:
        result = session.scalar(text("SELECT 1"))

    assert result == 1


def test_get_db_provides_working_session() -> None:
    dependency = get_db()
    session = next(dependency)

    try:
        assert isinstance(session, Session)
        assert session.scalar(text("SELECT 1")) == 1
    finally:
        dependency.close()
