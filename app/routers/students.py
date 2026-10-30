from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import StudentCreate, StudentUpdate, StudentResponse, StudentListResponse
from app import crud

router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


@router.post(
    "",
    response_model=StudentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new student",
    description="Add a new student record to SQLite database with required ID, name, date of birth, and contact information."
)
def create_student(student_in: StudentCreate, db: Session = Depends(get_db)):
    # Check if student with same student_id already exists
    existing_student = crud.get_student(db, student_id=student_in.student_id)
    if existing_student:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A student with ID '{student_in.student_id}' already exists."
        )

    # Check if email is provided and already taken
    if student_in.email:
        existing_email = crud.get_student_by_email(db, email=student_in.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A student with email '{student_in.email}' is already registered."
            )

    return crud.create_student(db=db, student_in=student_in)


@router.get(
    "",
    response_model=StudentListResponse,
    status_code=status.HTTP_200_OK,
    summary="List or filter students",
    description="Retrieve all students with support for pagination, search, course filter, and birth date range."
)
def list_students(
    skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    search: Optional[str] = Query(None, description="Free text search across ID, name, email, or course"),
    course: Optional[str] = Query(None, description="Filter by course name"),
    born_after: Optional[date] = Query(None, description="Filter students born strictly after this date (YYYY-MM-DD)"),
    born_before: Optional[date] = Query(None, description="Filter students born strictly before this date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    items, total = crud.get_students(
        db=db,
        skip=skip,
        limit=limit,
        search=search,
        course=course,
        born_after=born_after,
        born_before=born_before
    )
    return StudentListResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items
    )


@router.get(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="View student profile",
    description="Retrieve detailed profile information for a specific student by student_id."
)
def get_student(student_id: str, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )
    return student


@router.put(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update student details (Full update)",
    description="Completely update an existing student's details by their unique student_id."
)
def update_student_full(student_id: str, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )

    # If updating email, check for uniqueness conflict
    if student_update.email and student_update.email != student.email:
        existing_email = crud.get_student_by_email(db, email=student_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_update.email}' is already in use by another student."
            )

    updated = crud.update_student(db=db, db_student=student, student_update=student_update, partial=False)
    return updated


@router.patch(
    "/{student_id}",
    response_model=StudentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update student details (Partial update)",
    description="Partially modify one or more fields of an existing student's record."
)
def update_student_partial(student_id: str, student_update: StudentUpdate, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )

    # If updating email, check for uniqueness conflict
    if student_update.email and student_update.email != student.email:
        existing_email = crud.get_student_by_email(db, email=student_update.email)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{student_update.email}' is already in use by another student."
            )

    updated = crud.update_student(db=db, db_student=student, student_update=student_update, partial=True)
    return updated


@router.delete(
    "/{student_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a student",
    description="Remove a student record permanently from SQLite storage."
)
def delete_student(student_id: str, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id=student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID '{student_id}' was not found."
        )
    crud.delete_student(db=db, db_student=student)
    return {
        "status": "success",
        "message": f"Student with ID '{student_id}' has been permanently deleted.",
        "student_id": student_id
    }
