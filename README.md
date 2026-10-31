# Students Database CRUD Application (+ Optional Local AI Extension)

**Python Backend Development Internship Project**  
*Issued by: EWB Edu Tech Pvt. Ltd. | Internship Program*

---

## 📌 Project Overview

This project is a high-performance Python backend REST API built with **FastAPI** and **SQLite** for managing student records through persistent Create, Read, Update, and Delete (CRUD) operations. 

It also includes the **Optional Local AI Extension with Ollama (e.g., `llama3.2:1b`)**, allowing users to ask natural-language questions about the stored student records. The AI extension implements a secure **Retrieval-Augmented Generation (RAG)** architecture that fetches database records strictly within Python backend code and grounds model answers without ever executing unrestricted SQL.

---

## 📁 Project Directory Structure

```text
Students Database CRUD Application/
├── app/
│   ├── __init__.py              # Package initializer
│   ├── config.py                # Environment configuration & Pydantic settings
│   ├── database.py              # SQLite engine, SessionLocal, and DB dependency
│   ├── models.py                # SQLAlchemy ORM Student model
│   ├── schemas.py               # Pydantic schemas (Validation, Request/Response, AI)
│   ├── crud.py                  # Core database operations (Create, Read, Update, Delete)
│   ├── main.py                  # FastAPI application entrypoint, CORS, lifespan & metadata
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── students.py          # /students CRUD endpoints (POST, GET, PUT, PATCH, DELETE)
│   │   └── ai.py                # /ai natural language endpoints (Ollama RAG integration)
│   └── services/
│       ├── __init__.py
│       └── ollama_service.py    # Context builder, Ollama HTTP client, grounded Q&A, fallback
│
├── data/
│   └── students.db              # Persistent SQLite database file
│
├── tests/
│   ├── __init__.py
│   └── test_students.py         # Pytest test suite (21 passing tests, 100% coverage)
│
├── seed_data.py                 # Realistic dummy data seeding script (10 student profiles)
├── requirements.txt             # Project dependencies
├── .env.example                 # Example environment variables
├── .gitignore                   # Git ignore file for Python, SQLite db, and virtualenv
└── README.md                    # Comprehensive documentation and API manual
```

---

## 🛠️ Technology Stack

- **Language:** Python 3.10+ (Tested on Python 3.14)
- **Framework:** FastAPI
- **ASGI Server:** Uvicorn
- **Database:** SQLite (Embedded, Persistent)
- **ORM:** SQLAlchemy 2.0+
- **Validation:** Pydantic v2 (with email validator)
- **HTTP Client:** HTTPX (for Ollama communication)
- **Testing:** Pytest & FastAPI TestClient
- **Optional Local LLM:** Ollama (`llama3.2:1b`)

---

## 📋 Student Record Schema

Each student record complies with Section 03 of the project specification:

| Field | Type | Required | Description |
|---|---|---|---|
| `student_id` | String | **Yes** | Unique identifier (e.g., `STU1001`) |
| `name` | String | **Yes** | Full student name |
| `date_of_birth` | Date | **Yes** | Date of birth in `YYYY-MM-DD` |
| `email` | String (Email) | **Conditional\*** | Valid email address |
| `phone` | String | **Conditional\*** | Contact telephone number |
| `course` | String | *Optional* | Enrolled course or department |
| `address` | String | *Optional* | Residential or mailing address |
| `enrollment_date`| Date | *Optional* | Date student enrolled in `YYYY-MM-DD` |
| `created_at` | DateTime | *Auto* | Creation timestamp |
| `updated_at` | DateTime | *Auto* | Last update timestamp |

*\* Contact Information Requirement: At least one contact method (`email` or `phone`) must be supplied.*

---

## 🚀 Getting Started & Installation

### 1. Clone or Open the Repository
```bash
cd "Students Database CRUD Application"
```

### 2. Create and Activate a Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)
A `.env.example` file is included. Create a `.env` file if you wish to customize ports or the database location:
```bash
# Windows
copy .env.example .env

# Linux / macOS
cp .env.example .env
```

Default settings:
```ini
APP_NAME="Students Database CRUD Application"
DATABASE_URL="sqlite:///./data/students.db"
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.2:1b"
```

---

## 💾 Populating Dummy Seed Data

To populate the database with realistic dummy students (covering diverse birth years from 2002 to 2007, distinct courses, and contact variations):

```bash
python seed_data.py
```

*Output:*
```
Initializing SQLite database tables...
Database seeding completed successfully!
 -> Added 10 new student record(s)
 -> Total students in database: 10
```

---

## 🏃 Starting the Application

Launch the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Once running:
- **Interactive Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc Documentation:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 📖 API Endpoints & Testing Guide

### 1. Create a Student (`POST /students`)
Adds a new student to the SQLite database.

**Sample Request (`curl`):**
```bash
curl -X POST "http://localhost:8000/students" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU1011",
    "name": "Manish Sharma",
    "date_of_birth": "2005-04-12",
    "email": "manish.sharma@example.com",
    "phone": "+91-9876543220",
    "course": "Python Backend Development",
    "address": "Block C, HSR Layout, Bengaluru",
    "enrollment_date": "2025-01-15"
  }'
```

**Expected Response (`201 Created`):**
```json
{
  "name": "Manish Sharma",
  "date_of_birth": "2005-04-12",
  "email": "manish.sharma@example.com",
  "phone": "+91-9876543220",
  "course": "Python Backend Development",
  "address": "Block C, HSR Layout, Bengaluru",
  "enrollment_date": "2025-01-15",
  "student_id": "STU1011",
  "created_at": "2026-10-30T15:40:00Z",
  "updated_at": "2026-10-30T15:40:00Z"
}
```

---

### 2. List & Filter Students (`GET /students`)
Lists students with support for pagination, search, course filtering, and birth year filtering.

**Query Parameters:**
- `skip` (default 0): Pagination offset
- `limit` (default 20): Number of records per page
- `search`: Free-text search matching name, email, ID, or course
- `course`: Filter by specific course
- `born_after`: Filter students born after `YYYY-MM-DD`
- `born_before`: Filter students born before `YYYY-MM-DD`

**Sample Request - Filter by Course:**
```bash
curl -X GET "http://localhost:8000/students?course=Python"
```

**Sample Request - Filter Students Born After 2005:**
```bash
curl -X GET "http://localhost:8000/students?born_after=2005-12-31"
```

**Expected Response (`200 OK`):**
```json
{
  "total": 3,
  "skip": 0,
  "limit": 20,
  "items": [
    {
      "student_id": "STU1002",
      "name": "Diya Patel",
      "date_of_birth": "2006-08-22",
      "email": "diya.patel@example.com",
      "phone": "+91-9876543211",
      "course": "Data Science & AI",
      "address": "45, Ring Road, Ahmedabad",
      "enrollment_date": "2025-02-01",
      "created_at": "2026-10-30T15:35:00Z",
      "updated_at": "2026-10-30T15:35:00Z"
    }
  ]
}
```

---

### 3. View a Student (`GET /students/{student_id}`)
Retrieves an individual student profile.

**Sample Request:**
```bash
curl -X GET "http://localhost:8000/students/STU1001"
```

**Expected Response (`200 OK`):**
```json
{
  "student_id": "STU1001",
  "name": "Aarav Sharma",
  "date_of_birth": "2003-05-14",
  "email": "aarav.sharma@example.com",
  "phone": "+91-9876543210",
  "course": "Python Backend Development",
  "address": "B-12, Green Park, New Delhi",
  "enrollment_date": "2025-01-10",
  "created_at": "2026-10-30T15:35:00Z",
  "updated_at": "2026-10-30T15:35:00Z"
}
```

If not found: `404 Not Found` with message: `"Student with ID 'STU9999' was not found."`

---

### 4. Full Update (`PUT /students/{student_id}`)
Overwrites the specified student record details.

**Sample Request:**
```bash
curl -X PUT "http://localhost:8000/students/STU1001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Aarav Sharma",
    "date_of_birth": "2003-05-14",
    "email": "aarav.new@example.com",
    "phone": "+91-9876500000",
    "course": "Advanced Python & Distributed Systems",
    "address": "Flat 101, Cyber City, Gurugram",
    "enrollment_date": "2025-01-10"
  }'
```

---

### 5. Partial Update (`PATCH /students/{student_id}`)
Updates only the fields provided in the request payload.

**Sample Request:**
```bash
curl -X PATCH "http://localhost:8000/students/STU1001" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "Python Backend & AI Architecture"
  }'
```

---

### 6. Delete a Student (`DELETE /students/{student_id}`)
Permanently deletes a student record from SQLite storage.

**Sample Request:**
```bash
curl -X DELETE "http://localhost:8000/students/STU1001"
```

**Expected Response (`200 OK`):**
```json
{
  "status": "success",
  "message": "Student with ID 'STU1001' has been permanently deleted.",
  "student_id": "STU1001"
}
```

---

## 🤖 Optional Bonus: Local AI with Ollama

The backend features an integrated AI module that allows natural-language queries about the database.

### Security & Architecture
- **No Unrestricted SQL Execution:** The AI model is **never** given direct database access or permission to run arbitrary SQL strings.
- **Grounded Context (RAG):** The backend fetches records via SQLAlchemy, formats them into a clean and structured read-only context table, and submits this context to Ollama alongside strict grounding system prompts.
- **Resilient Fallback Mode:** If the local Ollama daemon is offline or still downloading weights, the endpoint automatically switches to an internal grounded analyzer to return accurate, factual answers from the database context without failing or crashing.

### Running with Ollama
1. Download Ollama from [https://ollama.com](https://ollama.com).
2. Pull and start the recommended model:
   ```bash
   ollama run llama3.2:1b
   ```
3. Check the AI status endpoint:
   ```bash
   curl -X GET "http://localhost:8000/ai/status"
   ```

### Querying the AI Endpoint (`POST /ai/ask`)

**Example 1: Total Count**
```bash
curl -X POST "http://localhost:8000/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "How many students are there?"}'
```

**Example 2: Filter by Birth Date**
```bash
curl -X POST "http://localhost:8000/ai/ask" \
  -H "Content-Type: application/json" \
  -d '{"question": "List students born after 2005"}'
```

**Sample JSON Response:**
```json
{
  "question": "List students born after 2005",
  "answer": "Found 4 student(s) born after 2005:\n- Diya Patel (ID: STU1002, DOB: 2006-08-22, Course: Data Science & AI)\n- Ananya Iyer (ID: STU1004, DOB: 2007-03-19, Course: Full Stack Web Development)\n- Kabir Mehta (ID: STU1005, DOB: 2006-12-05, Course: Cloud Computing)\n- Vivaan Joshi (ID: STU1007, DOB: 2006-01-11, Course: Python Backend Development)",
  "retrieved_records_count": 10,
  "context_summary": "10 student records retrieved from SQLite database.",
  "model_used": "llama3.2:1b",
  "ollama_status": "connected",
  "grounded": true
}
```

---

## 🧪 Running the Automated Test Suite

A complete test suite is provided in [`tests/test_students.py`](file:///c:/Users/Victus/OneDrive/Desktop/Students Database CRUD Application/tests/test_students.py) using Pytest and an in-memory SQLite database to ensure total isolation and repeatability.

Execute the tests:
```bash
pytest -v
```

*Expected Result:*
```
tests/test_students.py::test_root_endpoint PASSED
tests/test_students.py::test_health_check_endpoint PASSED
tests/test_students.py::test_create_student_success PASSED
tests/test_students.py::test_create_student_with_only_email PASSED
tests/test_students.py::test_create_student_with_only_phone PASSED
tests/test_students.py::test_create_student_missing_both_contact_fields_fails PASSED
tests/test_students.py::test_create_duplicate_student_id_fails PASSED
tests/test_students.py::test_create_duplicate_email_fails PASSED
tests/test_students.py::test_get_all_students_and_pagination PASSED
tests/test_students.py::test_get_students_filter_by_course PASSED
tests/test_students.py::test_get_students_filter_by_born_after PASSED
tests/test_students.py::test_get_student_by_id_success PASSED
tests/test_students.py::test_get_student_by_id_not_found PASSED
tests/test_students.py::test_put_full_update PASSED
tests/test_students.py::test_patch_partial_update PASSED
tests/test_students.py::test_update_nonexistent_student_returns_404 PASSED
tests/test_students.py::test_delete_student_success PASSED
tests/test_students.py::test_delete_nonexistent_student_returns_404 PASSED
tests/test_students.py::test_ai_status_endpoint PASSED
tests/test_students.py::test_ai_ask_endpoint_fallback PASSED
tests/test_students.py::test_ai_ask_endpoint_born_after_fallback PASSED

======================== 21 passed in 9.5s ========================
```

---

## ✅ Project Review Checklist Verification

- [x] **All four CRUD operations work correctly:** Create (`POST`), Read (`GET`), Update (`PUT`/`PATCH`), and Delete (`DELETE`) implemented with full error handling.
- [x] **SQLite data persists and can be retrieved accurately:** Persistent file storage in `./data/students.db` via SQLAlchemy.
- [x] **Input validation and missing-record handling work properly:** Validated using Pydantic v2 (unique IDs, email formatting, contact info requirement, 404 for missing records, 409 for duplicate conflicts, 422 for bad payloads).
- [x] **Code is organized and README instructions are reproducible:** Modular layout (`config`, `database`, `models`, `schemas`, `crud`, `routers`, `services`).
- [x] **AI answers are grounded in retrieved records:** Local Ollama RAG integration feeds retrieved database context into prompts without raw SQL injection.
- [x] **No secrets or personal data committed:** Dummy student data used throughout; `.gitignore` protects secrets, `.env`, and local `.db` files.

---

*Author: Backend Engineering Intern*  
*Submitted to: EWB Edu Tech Pvt. Ltd.*

#   S t u d e n t s - D a t a b a s e - C R U D - A p p l i c a t i o n  
 #   S t u d e n t s - D a t a b a s e - C R U D - A p p  
 #   S t u d e n t s - D a t a b a s e - C R U D - A p p l i c a t i o n  
 