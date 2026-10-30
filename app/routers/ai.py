from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AIQueryRequest, AIQueryResponse
from app.services.ollama_service import ollama_service

router = APIRouter(
    prefix="/ai",
    tags=["Ollama AI Extension"]
)


@router.post(
    "/ask",
    response_model=AIQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask natural language questions about student data",
    description=(
        "Accept natural language queries (e.g., 'How many students are there?', 'List students born after 2005'). "
        "Securely retrieves database records in Python backend code, grounds the context, and uses local Ollama (e.g., llama3.2:1b) "
        "to return an accurate, human-readable response without raw SQL injection."
    )
)
async def ask_question(request: AIQueryRequest, db: Session = Depends(get_db)):
    result = await ollama_service.query(
        db=db,
        question=request.question,
        model_override=request.model
    )
    return AIQueryResponse(**result)


@router.get(
    "/status",
    status_code=status.HTTP_200_OK,
    summary="Check local Ollama AI status",
    description="Inspect if the local Ollama daemon is reachable and which models are pulled/available."
)
async def check_ai_status():
    return await ollama_service.check_health()

