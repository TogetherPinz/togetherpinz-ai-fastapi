# Together Pins AI Backend (FastAPI)

This project is a migration of the original Kotlin/Spring Boot backend to Python/FastAPI. It provides AI-powered task recommendations using Groq API via LangChain.

## Tech Stack
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Database**: SQLModel (SQLAlchemy + Pydantic)
- **AI**: LangChain + Groq (Llama 3)
- **Package Manager**: uv (or pip)

## Project Structure
```
app/
├── api/            # API Endpoints
├── core/           # Configuration & DB Setup
├── models/         # SQLModel Database Tables
├── schemas/        # Pydantic DTOs
├── services/       # Business Logic (AI Service)
└── main.py         # Application Entry Point
```

## Setup

1.  **Install Dependencies**
    ```bash
    uv sync
    # or
    pip install -r requirements.txt
    ```

2.  **Environment Variables**
    Create a `.env` file in the root directory:
    ```env
    GROQ_API_KEY=your_groq_api_key
    DATABASE_URL=sqlite:///./app.db
    # For PostgreSQL:
    # DATABASE_URL=postgresql://user:password@localhost:5432/db_name
    ```

3.  **Run Server**
    ```bash
    uvicorn app.main:app --reload
    ```

## API Endpoints

-   **Swagger UI**: `http://localhost:8000/docs`
-   **Get Recommendations**: `GET /api/ai/recommendations?userId={userId}`
-   **Save Feedback**: `POST /api/ai/feedback`

## Key Features
-   **AI Recommendations**: Generates 3 task recommendations based on user history and feedback.
-   **Feedback System**: Stores user acceptance/rejection of recommendations.
-   **Fallback Mechanism**: Returns default recommendations if AI service fails.