from sqlalchemy import Column, String, Date, DateTime, func
from app.database import Base


class Student(Base):
    """
    SQLAlchemy model representing a student in the database.
    
    Fields:
      - student_id: Unique identifier for the student (Primary Key)
      - name: Full name of the student
      - date_of_birth: Student's date of birth (YYYY-MM-DD)
      - email: Student's email address (Optional if phone provided)
      - phone: Student's phone number (Optional if email provided)
      - course: Enrolled academic course or program (Optional)
      - address: Residential/mailing address (Optional)
      - enrollment_date: Date student enrolled (Optional)
      - created_at: Timestamp when record was created
      - updated_at: Timestamp when record was last updated
    """
    __tablename__ = "students"

    student_id = Column(String(50), primary_key=True, index=True, nullable=False)
    name = Column(String(100), nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    email = Column(String(150), nullable=True, index=True)
    phone = Column(String(30), nullable=True)
    course = Column(String(100), nullable=True, index=True)
    address = Column(String(255), nullable=True)
    enrollment_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return f"<Student(student_id='{self.student_id}', name='{self.name}', course='{self.course}')>"
