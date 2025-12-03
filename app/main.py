from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.endpoints import ai
from app.core.config import settings
from app.core.database import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_STR}/openapi.json",
    lifespan=lifespan
)

app.include_router(ai.router, prefix=f"{settings.API_STR}/ai", tags=["ai"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Together Pins AI Backend"}
