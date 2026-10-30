from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict, model_validator


class StudentBase(BaseModel):
    """Base schema containing shared student attributes."""
    name: str = Field(..., min_length=1, max_length=100, description="Full name of the student", examples=["Aarav Sharma"])
    date_of_birth: date = Field(..., description="Student's date of birth in YYYY-MM-DD format", examples=["2003-05-14"])
    email: Optional[EmailStr] = Field(None, description="Valid email address", examples=["aarav.sharma@example.com"])
    phone: Optional[str] = Field(None, min_length=5, max_length=30, description="Contact phone number", examples=["+91-9876543210"])
    course: Optional[str] = Field(None, max_length=100, description="Enrolled course", examples=["Python Backend Development"])
    address: Optional[str] = Field(None, max_length=255, description="Residential or mailing address", examples=["B-12, Green Park, New Delhi"])
    enrollment_date: Optional[date] = Field(None, description="Date of enrollment", examples=["2025-01-15"])


class StudentCreate(StudentBase):
    """Schema for creating a new student record."""
    student_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Unique student identifier (alphanumeric, dashes, underscores)",
        examples=["STU-1001"]
    )

    @model_validator(mode="after")
    def validate_contact_information(self) -> "StudentCreate":
        """Ensure at least one contact method (email or phone) is provided."""
        has_email = bool(self.email and str(self.email).strip())
        has_phone = bool(self.phone and str(self.phone).strip())
        if not (has_email or has_phone):
            raise ValueError("Contact information required: please provide at least an email or a phone number.")
        return self


class StudentUpdate(BaseModel):
    """Schema for updating student record details (PUT and PATCH)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=30)
    course: Optional[str] = Field(None, max_length=100)
    address: Optional[str] = Field(None, max_length=255)
    enrollment_date: Optional[date] = None


class StudentResponse(StudentBase):
    """Schema for returning student information."""
    student_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class StudentListResponse(BaseModel):
    """Paginated list response for students."""
    total: int
    skip: int
    limit: int
    items: List[StudentResponse]


class AIQueryRequest(BaseModel):
    """Request schema for Ollama AI natural language queries."""
    question: str = Field(
        ...,
        min_length=2,
        max_length=500,
        description="Natural language question about student data",
        examples=["How many students are there?", "List students born after 2005", "Which students are enrolled in Python Backend Development?"]
    )
    model: Optional[str] = Field(
        None,
        description="Optional model identifier override (defaults to server config: llama3.2:1b)"
    )


class AIQueryResponse(BaseModel):
    """Response schema for Ollama AI queries grounded in student data."""
    question: str
    answer: str
    retrieved_records_count: int
    context_summary: Optional[str] = None
    model_used: str
    ollama_status: str
    grounded: bool

