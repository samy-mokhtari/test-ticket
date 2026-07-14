from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.database import Base, engine
from app.main import app


def test_health_check() -> None:
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ticket_table_is_created_on_startup() -> None:
    Base.metadata.drop_all(bind=engine)

    assert not inspect(engine).has_table("tickets")

    with TestClient(app):
        assert inspect(engine).has_table("tickets")

    Base.metadata.drop_all(bind=engine)
