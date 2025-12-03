from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from uuid import UUID, uuid4

def get_kst_now():
    return datetime.now(ZoneInfo("Asia/Seoul"))

class RecommendationFeedback(SQLModel, table=True):
    __tablename__ = "recommendation_feedback"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username: str
    task_title: str
    pin_title: str
    is_accepted: bool
    created_at: datetime = Field(default_factory=get_kst_now)
