from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.database import Base, engine
from app.routers import students, ai

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Initializes SQLite database tables on startup.
    """
    # Create SQLite database tables if they do not exist
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup actions on shutdown (if any)


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "**Students Database CRUD Application (+ Optional AI Extension)**\n\n"
        "Python Backend Development Internship Project for **EWB Edu Tech Pvt. Ltd.**\n\n"
        "Features:\n"
        "- Complete CRUD operations for Student records\n"
        "- Persistent SQLite storage with SQLAlchemy\n"
        "- Robust input validation & error handling\n"
        "- Optional Local Ollama AI RAG extension for natural-language querying\n"
        "- Fully reproducible test suite with Pytest"
    ),
    lifespan=lifespan
)

# Enable CORS for frontend integration and browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(students.router)
app.include_router(ai.router)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
    summary="Application Welcome & Metadata"
)
def root():
    return {
        "project": settings.APP_NAME,
        "company": "EWB Edu Tech Pvt. Ltd.",
        "status": "online",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
            "openapi_spec": "/openapi.json"
        },
        "endpoints": {
            "students_crud": "/students",
            "ai_natural_language_query": "/ai/ask",
            "ai_status": "/ai/status",
            "health": "/health"
        }
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Application Health Check"
)
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "SQLite connected",
        "version": settings.APP_VERSION
    }

