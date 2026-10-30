"""
Seed script to populate SQLite database with realistic dummy student data.
Complies with EWB assignment specifications:
- Unique Student IDs
- Name, Date of Birth, Contact Information (email and/or phone)
- Optional course, address, and enrollment date
- Mix of birth years (2002-2007) to test queries like 'students born after 2005'
"""

import sys
from datetime import date
from sqlalchemy.orm import Session

from app.database import SessionLocal, Base, engine
from app.models import Student

DUMMY_STUDENTS = [
    {
        "student_id": "STU1001",
        "name": "Aarav Sharma",
        "date_of_birth": date(2003, 5, 14),
        "email": "aarav.sharma@example.com",
        "phone": "+91-9876543210",
        "course": "Python Backend Development",
        "address": "B-12, Green Park, New Delhi",
        "enrollment_date": date(2025, 1, 10),
    },
    {
        "student_id": "STU1002",
        "name": "Diya Patel",
        "date_of_birth": date(2006, 8, 22),
        "email": "diya.patel@example.com",
        "phone": "+91-9876543211",
        "course": "Data Science & AI",
        "address": "45, Ring Road, Ahmedabad",
        "enrollment_date": date(2025, 2, 1),
    },
    {
        "student_id": "STU1003",
        "name": "Rohan Verma",
        "date_of_birth": date(2004, 11, 3),
        "email": "rohan.verma@example.com",
        "phone": None,
        "course": "Python Backend Development",
        "address": "Flat 302, Lake View Apts, Bengaluru",
        "enrollment_date": date(2024, 9, 15),
    },
    {
        "student_id": "STU1004",
        "name": "Ananya Iyer",
        "date_of_birth": date(2007, 3, 19),
        "email": None,
        "phone": "+91-9876543213",
        "course": "Full Stack Web Development",
        "address": "12/4, Anna Nagar, Chennai",
        "enrollment_date": date(2025, 3, 1),
    },
    {
        "student_id": "STU1005",
        "name": "Kabir Mehta",
        "date_of_birth": date(2006, 12, 5),
        "email": "kabir.mehta@example.com",
        "phone": "+91-9876543214",
        "course": "Cloud Computing",
        "address": "78, Marine Drive, Mumbai",
        "enrollment_date": date(2025, 1, 20),
    },
    {
        "student_id": "STU1006",
        "name": "Sneha Roy",
        "date_of_birth": date(2002, 7, 30),
        "email": "sneha.roy@example.com",
        "phone": "+91-9876543215",
        "course": "Data Science & AI",
        "address": "22, Salt Lake, Kolkata",
        "enrollment_date": date(2024, 8, 10),
    },
    {
        "student_id": "STU1007",
        "name": "Vivaan Joshi",
        "date_of_birth": date(2006, 1, 11),
        "email": "vivaan.joshi@example.com",
        "phone": "+91-9876543216",
        "course": "Python Backend Development",
        "address": "90, Shivaji Nagar, Pune",
        "enrollment_date": date(2025, 2, 15),
    },
    {
        "student_id": "STU1008",
        "name": "Isha Nair",
        "date_of_birth": date(2005, 9, 27),
        "email": "isha.nair@example.com",
        "phone": "+91-9876543217",
        "course": "Full Stack Web Development",
        "address": "15, MG Road, Kochi",
        "enrollment_date": date(2024, 11, 1),
    },
    {
        "student_id": "STU1009",
        "name": "Aditya Kulkarni",
        "date_of_birth": date(2007, 4, 18),
        "email": "aditya.k@example.com",
        "phone": "+91-9876543218",
        "course": "Cloud Computing",
        "address": "55, Mall Road, Jaipur",
        "enrollment_date": date(2025, 3, 5),
    },
    {
        "student_id": "STU1010",
        "name": "Pooja Deshmukh",
        "date_of_birth": date(2003, 10, 8),
        "email": "pooja.d@example.com",
        "phone": "+91-9876543219",
        "course": "Python Backend Development",
        "address": "33, Civil Lines, Nagpur",
        "enrollment_date": date(2024, 7, 1),
    }
]


def seed_database():
    """Initializes tables and seeds dummy student records."""
    print("Initializing SQLite database tables...")
    Base.metadata.create_all(bind=engine)

    db: Session = SessionLocal()
    try:
        inserted_count = 0
        skipped_count = 0

        for student_data in DUMMY_STUDENTS:
            existing = db.query(Student).filter(Student.student_id == student_data["student_id"]).first()
            if not existing:
                student = Student(**student_data)
                db.add(student)
                inserted_count += 1
            else:
                skipped_count += 1

        db.commit()
        print(f"Database seeding completed successfully!")
        print(f" -> Added {inserted_count} new student record(s)")
        print(f" -> Skipped {skipped_count} existing record(s)")
        print(f" -> Total students in database: {db.query(Student).count()}")
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}", file=sys.stderr)
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()

