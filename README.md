# Together Pins AI (FastAPI)

투게더핀즈 AI 파트 FastAPI 코드

## 기술 스택
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Database**: SQLModel (SQLAlchemy + Pydantic)
- **AI**: LangChain + Groq (Llama 3)
- **Package Manager**: uv (or pip)

## Project Structure
```
app/
├── api/            # API 엔드포인트
├── core/           # 기본 설정
├── models/         # DB 테이블
├── schemas/        # DTO들
├── services/       # 비즈니스 로직
└── main.py         # 메인 앱 진입
```