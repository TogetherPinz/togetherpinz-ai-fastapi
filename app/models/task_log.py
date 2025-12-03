from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID, uuid4

class TaskLog(SQLModel, table=True):
    __tablename__ = "task_log"

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True)
    username: str
    pin_title: str
    task_title: str
    start_date_time: datetime
    end_date_time: datetime
    context_text: Optional[str] = None
