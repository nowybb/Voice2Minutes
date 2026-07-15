from __future__ import annotations

import asyncio
from typing import Any

from google import genai
from google.genai import types
from pydantic import BaseModel, Field

from app.core.config import get_settings


class DecisionItem(BaseModel):
    """회의에서 실제로 확정되거나 합의된 사항."""

    content: str = Field(
        description="회의에서 실제로 결정되거나 합의된 내용"
    )


class ActionItem(BaseModel):
    """회의 이후 수행해야 하는 구체적인 업무."""

    task: str = Field(
        description="회의 이후 수행해야 하는 구체적인 업무"
    )
    assignee: str | None = Field(
        default=None,
        description="담당자. 확인할 수 없으면 null",
    )
    due_date: str | None = Field(
        default=None,
        description="마감 기한. 확인할 수 없으면 null",
    )


class MeetingAnalysis(BaseModel):
    """Gemini Structured Output으로 받을 회의 분석 결과."""

    summary: str = Field(
        description="회의 목적과 주요 논의를 정리한 3~5문장 요약"
    )
    decisions: list[DecisionItem] = Field(
        default_factory=list,
        description="실제로 확정되거나 합의된 결정 사항",
    )
    action_items: list[ActionItem] = Field(
        default_factory=list,
        description="회의 이후 수행해야 할 실행 항목",
    )
    keywords: list[str] = Field(
        default_factory=list,
        description="회의를 대표하는 핵심 키워드 3~8개",
    )


class GeminiMinutesError(RuntimeError):
    """Gemini 회의록 생성에 실패했을 때 발생하는 예외."""

    def __init__(
        self,
        message: str,
        *,
        code: str = "GEMINI_MINUTES_ERROR",
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class GeminiMinutesService:
    """RTZR 전사 결과를 Gemini로 분석해 구조화된 회의록을 생성한다."""

    def __init__(
        self,
        client: genai.Client | None = None,
    ) -> None:
        self._client = client

    @property
    def is_configured(self) -> bool:
        settings = get_settings()
        return bool(settings.GEMINI_API_KEY)

    def _get_client(self) -> genai.Client:
        if self._client is not None:
            return self._client

        settings = get_settings()

        if not settings.GEMINI_API_KEY:
            raise GeminiMinutesError(
                "GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.",
                code="GEMINI_API_KEY_MISSING",
            )

        self._client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )
        return self._client

    async def create_minutes(
        self,
        *,
        transcript_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        RTZR 전사 결과를 분석하여 구조화된 회의록을 생성한다.

        반환 항목:
        - summary
        - decisions
        - action_items
        - keywords
        - transcript
        - generation_method
        """

        utterances = self._extract_utterances(
            transcript_result
        )
        full_text = self._build_full_text(
            utterances
        )

        if not full_text:
            raise GeminiMinutesError(
                "분석할 전사 내용이 없습니다.",
                code="EMPTY_TRANSCRIPT",
            )

        settings = get_settings()
        client = self._get_client()
        prompt = self._build_prompt(utterances)

        response = await self._generate_with_retry(
            client=client,
            model=settings.GEMINI_MODEL,
            prompt=prompt,
        )

        analysis = response.parsed

        if analysis is None:
            try:
                analysis = MeetingAnalysis.model_validate_json(
                    response.text
                )
            except Exception as exc:
                raise GeminiMinutesError(
                    (
                        "Gemini 응답에서 회의록 결과를 "
                        "해석할 수 없습니다."
                    ),
                    code="GEMINI_INVALID_RESPONSE",
                ) from exc

        if not isinstance(analysis, MeetingAnalysis):
            analysis = MeetingAnalysis.model_validate(
                analysis
            )

        return {
            "summary": analysis.summary.strip(),
            "decisions": [
                {
                    "id": index,
                    "content": item.content.strip(),
                }
                for index, item in enumerate(
                    analysis.decisions,
                    start=1,
                )
                if item.content.strip()
            ],
            "action_items": [
                {
                    "id": index,
                    "task": item.task.strip(),
                    "assignee": (
                        item.assignee.strip()
                        if item.assignee
                        else None
                    ),
                    "due_date": (
                        item.due_date.strip()
                        if item.due_date
                        else None
                    ),
                    "status": "pending",
                }
                for index, item in enumerate(
                    analysis.action_items,
                    start=1,
                )
                if item.task.strip()
            ],
            "keywords": self._normalize_keywords(
                analysis.keywords
            ),
            "transcript": {
                "full_text": full_text,
                "utterances": utterances,
            },
            "generation_method": "gemini",
        }

    async def _generate_with_retry(
        self,
        *,
        client: genai.Client,
        model: str,
        prompt: str,
    ) -> Any:
        """
        Gemini의 일시적 서버 오류와 사용량 제한에 대해
        지수 백오프 방식으로 최대 4회 재시도한다.
        """

        max_attempts = 4
        delay_seconds = 2

        for attempt in range(1, max_attempts + 1):
            try:
                return await asyncio.wait_for(
                    client.aio.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            system_instruction=(
                                "당신은 한국어 회의록을 작성하는 전문 비서입니다. "
                                "전사문에 없는 내용을 추측하거나 만들어내지 마세요. "
                                "결정 사항과 실행 항목은 실제 발언에서 확인되는 "
                                "경우에만 추출하세요."
                            ),
                            response_mime_type="application/json",
                            response_schema=MeetingAnalysis,
                            temperature=0.2,
                        ),
                    ),
                    timeout=120,
                )

            except TimeoutError as exc:
                if attempt == max_attempts:
                    raise GeminiMinutesError(
                        "Gemini 회의록 생성 시간이 120초를 초과했습니다.",
                        code="GEMINI_TIMEOUT",
                    ) from exc

            except Exception as exc:
                if (
                    not self._is_retryable_error(exc)
                    or attempt == max_attempts
                ):
                    raise self._convert_api_error(exc) from exc

            await asyncio.sleep(delay_seconds)
            delay_seconds *= 2

        raise GeminiMinutesError(
            "Gemini 회의록 생성에 실패했습니다.",
            code="GEMINI_API_ERROR",
        )

    @staticmethod
    def _is_retryable_error(exc: Exception) -> bool:
        status_code = (
            getattr(exc, "status_code", None)
            or getattr(exc, "code", None)
        )
        error_text = str(exc).lower()

        return (
            status_code in {429, 500, 502, 503, 504}
            or "429" in error_text
            or "500" in error_text
            or "502" in error_text
            or "503" in error_text
            or "504" in error_text
            or "unavailable" in error_text
            or "high demand" in error_text
            or "temporarily" in error_text
        )

    @staticmethod
    def _convert_api_error(
        exc: Exception,
    ) -> GeminiMinutesError:
        status_code = (
            getattr(exc, "status_code", None)
            or getattr(exc, "code", None)
        )
        error_text = str(exc).strip()
        error_type = type(exc).__name__

        if status_code == 429 or "429" in error_text:
            return GeminiMinutesError(
                (
                    "Gemini API 사용 한도를 초과했습니다: "
                    f"{error_text}"
                ),
                code="GEMINI_RATE_LIMIT",
                status_code=429,
            )

        if status_code == 503 or "503" in error_text:
            return GeminiMinutesError(
                (
                    "Gemini 서버가 일시적으로 혼잡합니다: "
                    f"{error_text}"
                ),
                code="GEMINI_UNAVAILABLE",
                status_code=503,
            )

        if (
            status_code in {401, 403}
            or "API_KEY_INVALID" in error_text
            or "permission" in error_text.lower()
        ):
            return GeminiMinutesError(
                (
                    "Gemini API 인증에 실패했습니다: "
                    f"{error_text}"
                ),
                code="GEMINI_AUTH_ERROR",
                status_code=status_code,
            )

        if (
            status_code == 404
            or "not found" in error_text.lower()
        ):
            return GeminiMinutesError(
                (
                    "Gemini 모델을 찾을 수 없습니다: "
                    f"{error_text}"
                ),
                code="GEMINI_MODEL_NOT_FOUND",
                status_code=status_code,
            )

        return GeminiMinutesError(
            (
                "Gemini 회의록 생성 중 오류가 발생했습니다. "
                f"[{error_type}] {error_text}"
            ),
            code="GEMINI_API_ERROR",
            status_code=status_code,
        )

    @staticmethod
    def _extract_utterances(
        transcript_result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        results = transcript_result.get(
            "results",
            {},
        )
        raw_utterances = results.get(
            "utterances",
            [],
        )

        if not isinstance(raw_utterances, list):
            return []

        utterances: list[dict[str, Any]] = []

        for utterance in raw_utterances:
            if not isinstance(utterance, dict):
                continue

            text = str(
                utterance.get("msg", "")
            ).strip()

            if not text:
                continue

            utterances.append(
                {
                    "speaker": (
                        int(utterance.get("spk", 0))
                        + 1
                    ),
                    "start_ms": int(
                        utterance.get("start_at", 0)
                    ),
                    "duration_ms": int(
                        utterance.get("duration", 0)
                    ),
                    "text": text,
                }
            )

        return utterances

    @staticmethod
    def _build_full_text(
        utterances: list[dict[str, Any]],
    ) -> str:
        return " ".join(
            str(utterance["text"]).strip()
            for utterance in utterances
            if str(utterance["text"]).strip()
        )

    @staticmethod
    def _build_prompt(
        utterances: list[dict[str, Any]],
    ) -> str:
        transcript = "\n".join(
            (
                f"화자 {utterance['speaker']}: "
                f"{utterance['text']}"
            )
            for utterance in utterances
        )

        return f"""
다음은 회의 음성의 전사 결과입니다.

아래 기준에 따라 회의 내용을 분석하세요.

1. 핵심 요약
- 회의 목적과 주요 논의를 3~5문장으로 정리합니다.
- 중복된 내용은 제거합니다.
- 전사 오류가 일부 있더라도 전체 문맥을 바탕으로 자연스럽게 정리합니다.

2. 결정 사항
- 실제로 결정, 확정 또는 합의된 내용만 추출합니다.
- 단순한 제안, 질문, 개인 의견은 포함하지 않습니다.
- 결정 사항이 없으면 빈 목록을 반환합니다.

3. Action Items
- 회의 이후 수행해야 할 구체적인 업무만 추출합니다.
- 담당자와 기한이 명확하면 함께 기록합니다.
- 확인할 수 없는 값은 null로 둡니다.
- 실행 항목이 없으면 빈 목록을 반환합니다.

4. 핵심 키워드
- 회의를 대표하는 고유 명사와 핵심 주제를 3~8개 추출합니다.
- '지금', '우리', '때문에', '있습니다' 같은 일반적인 표현은 제외합니다.
- 의미가 비슷하거나 중복되는 키워드는 하나로 통합합니다.

5. 주의 사항
- 전사문에 없는 내용을 추측하지 않습니다.
- 불확실한 내용을 사실처럼 작성하지 않습니다.
- 결과는 반드시 한국어로 작성합니다.

[전사문]
{transcript}
""".strip()

    @staticmethod
    def _normalize_keywords(
        keywords: list[str],
    ) -> list[str]:
        normalized: list[str] = []
        seen: set[str] = set()

        for keyword in keywords:
            value = str(keyword).strip()

            if not value:
                continue

            key = value.casefold()

            if key in seen:
                continue

            seen.add(key)
            normalized.append(value)

            if len(normalized) >= 8:
                break

        return normalized


gemini_minutes_service = GeminiMinutesService()