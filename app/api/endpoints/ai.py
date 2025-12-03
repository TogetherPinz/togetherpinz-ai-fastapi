from fastapi import APIRouter, Depends
from typing import List
from sqlmodel import Session

from app.core.database import get_db
from app.services.ai_service import AiRecommendationService
from app.schemas.ai import RecommendedTaskDto, UserFeedbackRequest

router = APIRouter()
ai_service = AiRecommendationService()

@router.get("/recommendations", response_model=List[RecommendedTaskDto])
def get_recommendations(username: str, db: Session = Depends(get_db)):
    return ai_service.get_recommendations(username, db)

@router.post("/feedback")
def save_feedback(request: UserFeedbackRequest, db: Session = Depends(get_db)):
    ai_service.process_feedback(request, db)
    return {"message": "피드백이 성공적으로 저장되었습니다."}
