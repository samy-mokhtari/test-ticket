from sqlalchemy import text

from app.database import engine, session_factory


def test_database_uses_sqlite_in_memory() -> None:
    assert engine.url.drivername == "sqlite"
    assert engine.url.database is None


def test_database_accepts_queries() -> None:
    with session_factory() as session:
        result = session.scalar(text("SELECT 1"))

    assert result == 1
