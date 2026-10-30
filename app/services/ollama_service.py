import re
from datetime import date
from typing import List, Dict, Any, Optional, Tuple
import httpx
from sqlalchemy.orm import Session
from app.config import get_settings
from app.models import Student
from app.crud import get_all_students

settings = get_settings()


class OllamaService:
    """
    Service to handle natural language querying of student records using a local Ollama LLM.
    Implements secure Retrieval-Augmented Generation (RAG) by fetching structured database records
    and feeding them as context into the prompt, without executing unrestricted SQL.
    """

    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> Dict[str, Any]:
        """Check if local Ollama daemon is reachable and list installed models."""
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    return {
                        "status": "online",
                        "base_url": self.base_url,
                        "available_models": models,
                        "configured_model": self.default_model,
                        "is_configured_model_available": any(self.default_model in m for m in models)
                    }
        except Exception as e:
            return {
                "status": "offline",
                "base_url": self.base_url,
                "error": str(e),
                "configured_model": self.default_model,
                "hint": f"Start the Ollama server and run: ollama run {self.default_model}"
            }
        return {"status": "offline", "configured_model": self.default_model}

    def build_records_context(self, students: List[Student]) -> Tuple[str, str]:
        """
        Convert student database records into secure, structured plain-text context for LLM.
        Returns a tuple of (full_context_text, summary_text).
        """
        if not students:
            return "No student records found in the database.", "0 students in database."

        lines = [
            f"Total Students in Database: {len(students)}",
            "Student Records Table:",
            "ID | Name | Date of Birth | Course | Email | Phone | Enrollment Date"
        ]

        for s in students:
            dob = s.date_of_birth.isoformat() if s.date_of_birth else "N/A"
            enroll = s.enrollment_date.isoformat() if s.enrollment_date else "N/A"
            email = s.email or "N/A"
            phone = s.phone or "N/A"
            course = s.course or "N/A"
            lines.append(f"{s.student_id} | {s.name} | {dob} | {course} | {email} | {phone} | {enroll}")

        summary = f"{len(students)} student records retrieved from SQLite database."
        return "\n".join(lines), summary

    def _fallback_rule_based_answer(self, question: str, students: List[Student]) -> str:
        """
        Fallback logic to answer common query intents directly from database records
        when the local Ollama daemon is offline or still downloading models.
        """
        q_lower = question.lower().strip()

        # Intent 1: "How many students are there?" / count
        if any(keyword in q_lower for keyword in ["how many", "count", "number of student", "total student"]):
            # Check if filtered by course
            courses = set(s.course for s in students if s.course)
            matched_course = next((c for c in courses if c.lower() in q_lower), None)
            if matched_course:
                course_students = [s for s in students if s.course and s.course.lower() == matched_course.lower()]
                return f"There are {len(course_students)} student(s) enrolled in '{matched_course}' out of {len(students)} total students."
            return f"There are currently {len(students)} student(s) registered in the database."

        # Intent 2: "List students born after [year]" / "born before [year]"
        year_match = re.search(r"born\s+(after|before|in)\s+(\d{4})", q_lower)
        if year_match:
            op, year_str = year_match.groups()
            year = int(year_str)
            if op == "after":
                filtered = [s for s in students if s.date_of_birth and s.date_of_birth.year > year]
                desc = f"born after {year}"
            elif op == "before":
                filtered = [s for s in students if s.date_of_birth and s.date_of_birth.year < year]
                desc = f"born before {year}"
            else:
                filtered = [s for s in students if s.date_of_birth and s.date_of_birth.year == year]
                desc = f"born in {year}"

            if not filtered:
                return f"No students found {desc}."
            
            names_and_ids = [f"{s.name} (ID: {s.student_id}, DOB: {s.date_of_birth}, Course: {s.course or 'N/A'})" for s in filtered]
            return f"Found {len(filtered)} student(s) {desc}:\n- " + "\n- ".join(names_and_ids)

        # Intent 3: List all courses
        if "course" in q_lower and ("list" in q_lower or "what" in q_lower or "available" in q_lower):
            courses = sorted(list(set(s.course for s in students if s.course)))
            if courses:
                return "The available courses with registered students are:\n- " + "\n- ".join(courses)
            return "No courses are currently assigned to any students."

        # Default fallback summary
        if students:
            sample = [f"{s.name} ({s.student_id})" for s in students[:5]]
            return (
                f"There are {len(students)} students in the database. Sample students: {', '.join(sample)}... "
                f"(Start Ollama with 'ollama run {self.default_model}' for complex natural-language reasoning)."
            )
        return "The database currently has no student records."

    async def query(
        self,
        db: Session,
        question: str,
        model_override: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a natural language question grounded in the current database records.
        """
        # Step 1: Securely fetch current student records in Python backend code (No direct SQL injection)
        students = get_all_students(db)
        context_text, context_summary = self.build_records_context(students)

        model_to_use = model_override or self.default_model

        system_prompt = (
            "You are a helpful and precise assistant for a Student Database Management System.\n"
            "CRITICAL INSTRUCTIONS:\n"
            "1. Answer user questions ONLY based on the provided student records context below.\n"
            "2. Ground every single claim in the facts given in the context.\n"
            "3. If information is not in the context, truthfully say it cannot be found in the database.\n"
            "4. Never hallucinate or assume student information not present in the table.\n"
            "5. Keep responses concise, clear, and professional."
        )

        user_prompt = (
            f"Here is the current student database context:\n"
            f"\"\"\"\n{context_text}\n\"\"\"\n\n"
            f"User Question: {question}\n\n"
            f"Answer grounded in the data above:"
        )

        # Step 2: Attempt to call Ollama
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": model_to_use,
                    "prompt": user_prompt,
                    "system": system_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2  # Low temperature for deterministic, factual responses
                    }
                }
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("response", "").strip()
                    if answer:
                        return {
                            "question": question,
                            "answer": answer,
                            "retrieved_records_count": len(students),
                            "context_summary": context_summary,
                            "model_used": model_to_use,
                            "ollama_status": "connected",
                            "grounded": True
                        }
        except Exception:
            # Ollama not reachable, offline, or timed out
            pass

        # Step 3: Graceful fallback grounded in database records
        fallback_answer = self._fallback_rule_based_answer(question, students)
        notice = (
            f"[Note: Local Ollama daemon at {self.base_url} is currently offline or unreachable. "
            f"Response generated via backend grounded analyzer. To use Ollama LLM, run: 'ollama run {model_to_use}']\n\n"
            f"{fallback_answer}"
        )

        return {
            "question": question,
            "answer": notice,
            "retrieved_records_count": len(students),
            "context_summary": context_summary,
            "model_used": f"{model_to_use} (offline fallback)",
            "ollama_status": "offline_fallback",
            "grounded": True
        }


ollama_service = OllamaService()

