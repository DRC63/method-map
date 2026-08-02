import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app
from app.seed import seed


@pytest.fixture
def client(tmp_path, monkeypatch):
    """A TestClient backed by an isolated per-test SQLite DB. Seeds only PRINCE2
    (FRAMEWORK_KEY), mirroring a real single-framework deployment, so these
    PRINCE2-specific assertions are unaffected by other bundled frameworks (MSP).
    Never touches the real methodmap.db."""
    monkeypatch.setenv("FRAMEWORK_KEY", "prince2-7")
    url = f"sqlite:///{tmp_path / 'test.db'}"
    engine = create_engine(url, connect_args={"check_same_thread": False})
    TestingSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with TestingSession() as db:
        seed(db)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


ADMIN = {"X-Admin-Password": "change-me"}
