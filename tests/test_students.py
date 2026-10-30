import pytest
from datetime import date
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Student

# Use an in-memory SQLite database for isolated test execution
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    """Create all tables before each test and drop them after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


# -------------------------------------------------------------
# Root & Health Endpoints Tests
# -------------------------------------------------------------
def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "project" in data
    assert data["company"] == "EWB Edu Tech Pvt. Ltd."
    assert "documentation" in data


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


# -------------------------------------------------------------
# Create (POST) Endpoint Tests
# -------------------------------------------------------------
def test_create_student_success():
    payload = {
        "student_id": "STU101",
        "name": "Priya Sharma",
        "date_of_birth": "2004-06-15",
        "email": "priya.sharma@example.com",
        "phone": "+91-9123456789",
        "course": "Python Backend Development",
        "address": "404 Tech Park, Sector 5",
        "enrollment_date": "2025-01-10"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU101"
    assert data["name"] == "Priya Sharma"
    assert data["email"] == "priya.sharma@example.com"
    assert data["course"] == "Python Backend Development"
    assert "created_at" in data


def test_create_student_with_only_email():
    payload = {
        "student_id": "STU102",
        "name": "Amit Kumar",
        "date_of_birth": "2003-01-10",
        "email": "amit.kumar@example.com"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU102"
    assert data["email"] == "amit.kumar@example.com"
    assert data["phone"] is None


def test_create_student_with_only_phone():
    payload = {
        "student_id": "STU103",
        "name": "Sunita Rao",
        "date_of_birth": "2005-09-20",
        "phone": "+91-9988776655"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["student_id"] == "STU103"
    assert data["phone"] == "+91-9988776655"
    assert data["email"] is None


def test_create_student_missing_both_contact_fields_fails():
    # Both email and phone omitted should trigger 422 Unprocessable Entity
    payload = {
        "student_id": "STU104",
        "name": "Invalid Student",
        "date_of_birth": "2004-04-04"
    }
    response = client.post("/students", json=payload)
    assert response.status_code == 422
    assert "Contact information required" in response.text


def test_create_duplicate_student_id_fails():
    payload = {
        "student_id": "STU-DUP",
        "name": "Student One",
        "date_of_birth": "2003-03-03",
        "email": "student1@example.com"
    }
    resp1 = client.post("/students", json=payload)
    assert resp1.status_code == 201

    payload_dup = {
        "student_id": "STU-DUP",
        "name": "Student Two",
        "date_of_birth": "2004-04-04",
        "email": "student2@example.com"
    }
    resp2 = client.post("/students", json=payload_dup)
    assert resp2.status_code == 409
    assert "already exists" in resp2.json()["detail"]


def test_create_duplicate_email_fails():
    payload1 = {
        "student_id": "STU201",
        "name": "Student One",
        "date_of_birth": "2003-03-03",
        "email": "duplicate@example.com"
    }
    client.post("/students", json=payload1)

    payload2 = {
        "student_id": "STU202",
        "name": "Student Two",
        "date_of_birth": "2004-04-04",
        "email": "duplicate@example.com"
    }
    resp = client.post("/students", json=payload2)
    assert resp.status_code == 409
    assert "already registered" in resp.json()["detail"]


# -------------------------------------------------------------
# Read (GET) Endpoint Tests
# -------------------------------------------------------------
def test_get_all_students_and_pagination():
    # Seed 3 students
    for i in range(1, 4):
        client.post("/students", json={
            "student_id": f"STU00{i}",
            "name": f"Student {i}",
            "date_of_birth": f"200{i}-01-01",
            "email": f"stu{i}@example.com"
        })

    # Retrieve all
    response = client.get("/students")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 3
    assert len(data["items"]) == 3

    # Test limit and offset
    resp_page = client.get("/students?skip=1&limit=1")
    assert resp_page.status_code == 200
    page_data = resp_page.json()
    assert page_data["total"] == 3
    assert len(page_data["items"]) == 1
    assert page_data["items"][0]["student_id"] == "STU002"


def test_get_students_filter_by_course():
    client.post("/students", json={
        "student_id": "CS1",
        "name": "Dev One",
        "date_of_birth": "2003-02-02",
        "email": "dev1@example.com",
        "course": "Python Backend"
    })
    client.post("/students", json={
        "student_id": "CS2",
        "name": "Dev Two",
        "date_of_birth": "2004-02-02",
        "email": "dev2@example.com",
        "course": "Cloud Computing"
    })

    response = client.get("/students?course=Python")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["student_id"] == "CS1"


def test_get_students_filter_by_born_after():
    client.post("/students", json={
        "student_id": "BORN01",
        "name": "Older Student",
        "date_of_birth": "2002-05-10",
        "email": "older@example.com"
    })
    client.post("/students", json={
        "student_id": "BORN02",
        "name": "Younger Student",
        "date_of_birth": "2006-11-15",
        "email": "younger@example.com"
    })

    # Query students born after 2005-01-01
    response = client.get("/students?born_after=2005-01-01")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["student_id"] == "BORN02"


def test_get_student_by_id_success():
    client.post("/students", json={
        "student_id": "STU999",
        "name": "Target Student",
        "date_of_birth": "2003-08-08",
        "email": "target@example.com"
    })

    response = client.get("/students/STU999")
    assert response.status_code == 200
    assert response.json()["student_id"] == "STU999"
    assert response.json()["name"] == "Target Student"


def test_get_student_by_id_not_found():
    response = client.get("/students/NONEXISTENT")
    assert response.status_code == 404
    assert "was not found" in response.json()["detail"]


# -------------------------------------------------------------
# Update (PUT & PATCH) Endpoint Tests
# -------------------------------------------------------------
def test_put_full_update():
    client.post("/students", json={
        "student_id": "UPDATE01",
        "name": "Original Name",
        "date_of_birth": "2003-01-01",
        "email": "orig@example.com",
        "course": "Original Course"
    })

    put_payload = {
        "name": "Fully Updated Name",
        "date_of_birth": "2003-01-01",
        "email": "new.email@example.com",
        "phone": "+91-9999999999",
        "course": "Updated Course",
        "address": "New Address",
        "enrollment_date": "2025-05-01"
    }
    response = client.put("/students/UPDATE01", json=put_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Fully Updated Name"
    assert data["email"] == "new.email@example.com"
    assert data["course"] == "Updated Course"
    assert data["address"] == "New Address"


def test_patch_partial_update():
    client.post("/students", json={
        "student_id": "PATCH01",
        "name": "Stable Name",
        "date_of_birth": "2004-02-02",
        "email": "stable@example.com",
        "course": "Initial Course"
    })

    patch_payload = {
        "course": "Advanced Python Development"
    }
    response = client.patch("/students/PATCH01", json=patch_payload)
    assert response.status_code == 200
    data = response.json()
    # Name and email remain intact
    assert data["name"] == "Stable Name"
    assert data["email"] == "stable@example.com"
    # Course is updated
    assert data["course"] == "Advanced Python Development"


def test_update_nonexistent_student_returns_404():
    response = client.patch("/students/GHOST", json={"name": "Ghost Name"})
    assert response.status_code == 404


# -------------------------------------------------------------
# Delete (DELETE) Endpoint Tests
# -------------------------------------------------------------
def test_delete_student_success():
    client.post("/students", json={
        "student_id": "DEL01",
        "name": "Delete Me",
        "date_of_birth": "2003-03-03",
        "email": "del@example.com"
    })

    # Delete
    del_response = client.delete("/students/DEL01")
    assert del_response.status_code == 200
    assert "permanently deleted" in del_response.json()["message"]

    # Verify student is gone
    get_response = client.get("/students/DEL01")
    assert get_response.status_code == 404


def test_delete_nonexistent_student_returns_404():
    response = client.delete("/students/DEL_NOT_FOUND")
    assert response.status_code == 404


# -------------------------------------------------------------
# Optional AI Extension Endpoint Tests
# -------------------------------------------------------------
def test_ai_status_endpoint():
    response = client.get("/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "configured_model" in data


def test_ai_ask_endpoint_fallback():
    # Insert students to ground the AI query
    client.post("/students", json={
        "student_id": "AI01",
        "name": "Grounded Student One",
        "date_of_birth": "2006-03-10",
        "email": "ai1@example.com"
    })
    client.post("/students", json={
        "student_id": "AI02",
        "name": "Grounded Student Two",
        "date_of_birth": "2007-07-20",
        "email": "ai2@example.com"
    })

    # Ask question
    response = client.post("/ai/ask", json={"question": "How many students are there?"})
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "How many students are there?"
    assert data["retrieved_records_count"] == 2
    assert data["grounded"] is True
    assert "2 student(s)" in data["answer"] or "2" in data["answer"]


def test_ai_ask_endpoint_born_after_fallback():
    client.post("/students", json={
        "student_id": "AI03",
        "name": "Old Student",
        "date_of_birth": "2002-01-01",
        "email": "old@example.com"
    })
    client.post("/students", json={
        "student_id": "AI04",
        "name": "Young Student",
        "date_of_birth": "2007-06-15",
        "email": "young@example.com"
    })

    response = client.post("/ai/ask", json={"question": "List students born after 2005"})
    assert response.status_code == 200
    data = response.json()
    assert data["retrieved_records_count"] == 2
    assert "Young Student" in data["answer"]
