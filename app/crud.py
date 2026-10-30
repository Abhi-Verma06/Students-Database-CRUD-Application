from datetime import date
from typing import Optional, List, Tuple
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session
from app.models import Student
from app.schemas import StudentCreate, StudentUpdate


def get_student(db: Session, student_id: str) -> Optional[Student]:
    """Retrieve a single student by their unique student_id."""
    return db.query(Student).filter(Student.student_id == student_id).first()


def get_student_by_email(db: Session, email: str) -> Optional[Student]:
    """Retrieve a student by email address."""
    if not email:
        return None
    return db.query(Student).filter(Student.email == email).first()


def get_students(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None
) -> Tuple[List[Student], int]:
    """
    Retrieve students with optional filtering, search, and pagination.
    Returns a tuple of (students list, total count matching filter).
    """
    query = db.query(Student)

    # General search across ID, name, email, and course
    if search and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Student.student_id.ilike(term),
                Student.name.ilike(term),
                Student.email.ilike(term),
                Student.course.ilike(term)
            )
        )

    # Specific course filter
    if course and course.strip():
        query = query.filter(Student.course.ilike(f"%{course.strip()}%"))

    # Date of birth filters
    if born_after:
        query = query.filter(Student.date_of_birth > born_after)

    if born_before:
        query = query.filter(Student.date_of_birth < born_before)

    total = query.count()
    students = query.order_by(Student.student_id.asc()).offset(skip).limit(limit).all()

    return students, total


def create_student(db: Session, student_in: StudentCreate) -> Student:
    """Create a new student record in the database."""
    student_data = student_in.model_dump()
    db_student = Student(**student_data)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update_student(
    db: Session,
    db_student: Student,
    student_update: StudentUpdate,
    partial: bool = False
) -> Student:
    """
    Update an existing student record.
    If partial is True (PATCH), only fields explicitly passed in the request are updated.
    If partial is False (PUT), all defined fields in the payload are updated.
    """
    update_data = student_update.model_dump(exclude_unset=partial)

    for field, value in update_data.items():
        if hasattr(db_student, field):
            # If partial is True, skip None unless explicitly provided; for PUT, update as sent
            setattr(db_student, field, value)

    db.commit()
    db.refresh(db_student)
    return db_student


def delete_student(db: Session, db_student: Student) -> None:
    """Delete a student record from the database."""
    db.delete(db_student)
    db.commit()


def get_all_students(db: Session) -> List[Student]:
    """Retrieve all student records without pagination (used for AI grounding context)."""
    return db.query(Student).order_by(Student.student_id.asc()).all()

