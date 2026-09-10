import os

os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["JWT_SECRET_KEY"] = "test-secret-at-least-thirty-two-bytes-long"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.config import get_settings
from backend.database.session import Base, get_db
from backend.main import app


@pytest.fixture()
def db(tmp_path):
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    get_settings().upload_dir = tmp_path / "uploads"
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post("/auth/signup", json={"email": "person@example.com", "password": "strong-pass"})
    response = client.post("/auth/login", data={"username": "person@example.com", "password": "strong-pass"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
