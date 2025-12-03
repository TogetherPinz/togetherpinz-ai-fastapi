import json
import logging
from datetime import datetime, timedelta, date
from typing import List
from zoneinfo import ZoneInfo
from sqlmodel import Session, select, desc

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import settings
from app.models.task_log import TaskLog
from app.models.feedback import RecommendationFeedback
from app.schemas.ai import RecommendedTaskDto, UserFeedbackRequest, RecommendationResponse, FeedbackItem

logger = logging.getLogger(__name__)

class AiRecommendationService:
    def __init__(self):
        self.llm = ChatGroq(
            model=settings.GROQ_MODEL,
            temperature=0.1,
            api_key=settings.GROQ_API_KEY,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """당신은 친절하고 유익한 AI 조수입니다. 사용자의 과거 할 일 기록과 피드백을 기반으로 오늘 할 일을 추천합니다.
            당신은 반드시 유효한 JSON만 출력해야 합니다."""),
            ("human", """오늘 ({today}) 할 일 3개를 추천해주세요.
            과거 기록:
            {history}

            피드백:
            {feedback}

            사용 가능한 핀 목록:
            {available_pins}

            규칙:
            - pinTitle은 위 핀 목록에서만 선택 (필수)
            - taskTitle또한 필수
            - ({today}) 이후의 할 일만 추천
            - startDateTime, endDateTime은 ISO 8601 형식 ("YYYY-MM-DDTHH:mm:ss.SSSZ")
            - reasoning에는 추천 이유 (응답 언어: 한국어, 한글) (필수)
            - taskDetails에는 '학교'에서 '수업 복습'을 추천합니다. 등의 형식 (응답 언어: 한국어, 한글) (필수)

            JSON 형식으로만 반환:
            {{"recommendations":[{{"taskTitle":"","pinTitle":"","reasoning":"","taskDetails":"","startDateTime":""YYYY-MM-DDTHH:mm:ss.SSSZ"","endDateTime":"YYYY-MM-DDTHH:mm:ss.SSSZ"}}]}}""")
        ])

    def get_recommendations(self, username: str, db: Session) -> List[RecommendedTaskDto]:
        try:
            return self._get_recommendations_sync(username, db)
        except Exception as e:
            logger.error(f"AI Service error: {e}")
            return self.get_fallback_recommendations()

    def _get_recommendations_sync(self, username: str, db: Session) -> List[RecommendedTaskDto]:
        tasks_from_db = db.exec(
            select(TaskLog)
            .where(TaskLog.username == username)
            .order_by(desc(TaskLog.start_date_time))
            .limit(50)
        ).all()

        logger.info(f"Fetched {len(tasks_from_db)} tasks from database")

        feedbacks = db.exec(
            select(RecommendationFeedback)
            .where(RecommendationFeedback.username == username)
            .order_by(desc(RecommendationFeedback.created_at))
        ).all()

        logger.info(f"Fetched {len(feedbacks)} feedbacks from database")

        available_pins = list(set(t.pin_title for t in tasks_from_db))
        available_pins_str = ", ".join(available_pins)

        simple_history = self._convert_tasks_to_simple_string(tasks_from_db)
        feedback_context = self._convert_feedback_to_string(feedbacks)

        today = datetime.now(ZoneInfo("Asia/Seoul")).isoformat()
        chain = self.prompt_template | self.llm

        # 4. Call LLM
        response = chain.invoke({
            "today": today,
            "history": simple_history,
            "feedback": feedback_context,
            "available_pins": available_pins_str,
        })

        content = response.content
        logger.info(f"LLM response length: {len(content)} characters")

        json_str = self._extract_json_string(content)
        if json_str:
            try:
                data = json.loads(json_str)

                if isinstance(data, dict) and "recommendations" in data:
                    recommendations = data["recommendations"]
                elif isinstance(data, list):
                    recommendations = data
                else:
                    logger.warning("Invalid JSON structure. Returning fallback.")
                    return self.get_fallback_recommendations()

                return [RecommendedTaskDto(**rec) for rec in recommendations]
            except json.JSONDecodeError as e:
                logger.error(f"JSON parse error at position {e.pos}: {e.msg}")
                logger.error(f"Problematic JSON string (first 500 chars): {json_str[:500]}")
                return self.get_fallback_recommendations()
            except Exception as e:
                logger.error(f"Error processing recommendations: {e}")
                logger.error(f"JSON string (first 500 chars): {json_str[:500]}")
                return self.get_fallback_recommendations()

        return self.get_fallback_recommendations()

    def process_feedback(self, request: UserFeedbackRequest, db: Session):
        feedback_objects = []
        for item in request.acceptedItems:
            feedback_objects.append(RecommendationFeedback(
                username=request.username,
                task_title=item.taskTitle,
                pin_title=item.pinTitle,
                is_accepted=True
            ))
        for item in request.rejectedItems:
            feedback_objects.append(RecommendationFeedback(
                username=request.username,
                task_title=item.taskTitle,
                pin_title=item.pinTitle,
                is_accepted=False
            ))

        for obj in feedback_objects:
            db.add(obj)
        db.commit()
        logger.info("Feedback saved successfully")

    def get_fallback_recommendations(self) -> List[RecommendedTaskDto]:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        to = now + timedelta(hours=1)
        fmt = "%Y-%m-%dT%H:%M:%S.%f"
        now_str = now.strftime(fmt)[:-3] + "Z"
        to_str = to.strftime(fmt)[:-3] + "Z"

        return [
            RecommendedTaskDto(
                taskTitle="할 일 정리하기",
                pinTitle="집",
                reasoning="기본 추천입니다. 잠시 후 다시 시도해주세요.",
                taskDetails="밀린 일정을 점검해보세요.",
                startDateTime=now_str,
                endDateTime=to_str
            ),
            RecommendedTaskDto(
                taskTitle="잠시 휴식",
                pinTitle="집",
                reasoning="기본 추천입니다.",
                taskDetails="가벼운 스트레칭을 해보세요.",
                startDateTime=now_str,
                endDateTime=to_str
            )
        ]

    def _convert_tasks_to_simple_string(self, tasks: List[TaskLog]) -> str:
        if not tasks:
            return "기록 없음"
        return "\n".join([f"- {t.pin_title}: {t.task_title}" for t in tasks])

    def _convert_feedback_to_string(self, feedbacks: List[RecommendationFeedback]) -> str:
        if not feedbacks:
            return ""
        accepted = [f.task_title for f in feedbacks if f.is_accepted][:3]
        rejected = [f.task_title for f in feedbacks if not f.is_accepted][:3]
        acc_str = ", ".join(accepted)
        rej_str = ", ".join(rejected)
        return f"선호: [{acc_str}], 비선호: [{rej_str}]"

    def _extract_json_string(self, text: str) -> str:
        try:
            s = text.index("{")
            e = text.rindex("}")
            json_str = text[s : e + 1]

            json_str = json_str.strip()

            return json_str
        except ValueError:
            logger.error(f"Could not find JSON object in response: {text[:200]}")
            return None
