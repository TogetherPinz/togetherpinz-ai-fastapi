from pydantic_settings import BaseSettings
from os import environ

class Settings(BaseSettings):
    PROJECT_NAME: str = "Together Pins AI Recommender"
    API_STR: str = "/api"
    
    GROQ_API_KEY: str = environ.get("GROQ_API_KEY")
    GROQ_MODEL: str = environ.get("GROQ_MODEL")
    DATABASE_URL: str = environ.get("DATABASE_URL")

    class Config:
        env_file = ".env"

settings = Settings()
