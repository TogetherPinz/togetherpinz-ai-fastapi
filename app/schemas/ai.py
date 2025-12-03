from pydantic import BaseModel
from typing import List, Optional

class RecommendedTaskDto(BaseModel):
    taskTitle: str
    pinTitle: str
    reasoning: str
    taskDetails: Optional[str] = None
    startDateTime: str
    endDateTime: str

class FeedbackItem(BaseModel):
    taskTitle: str
    pinTitle: str

class UserFeedbackRequest(BaseModel):
    username: str
    acceptedItems: List[FeedbackItem]
    rejectedItems: List[FeedbackItem]

class RecommendationResponse(BaseModel):
    recommendations: List[RecommendedTaskDto]
