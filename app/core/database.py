from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# 테스트용
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args=connect_args,
    echo=True
)

def get_db():
    with Session(engine) as session:
        yield session

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
