import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestSession()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "user@example.com",
        "password": "password123"
    })

    assert response.status_code == 201

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def sample_student(client, auth_headers):
    response = client.post(
        "/students",
        headers=auth_headers,
        json={
            "name": "Test Name",
            "email": "test@email.com",
            "grade_level": 12,
            "gpa": 4.0,
            "is_enrolled": True
        }
    )

    assert response.status_code == 201
    return response.json()
