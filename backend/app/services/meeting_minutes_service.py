from __future__ import annotations

import re
from collections import Counter
from typing import Any


DECISION_KEYWORDS = (
    "결정",
    "확정",
    "하기로",
    "진행하기로",
    "사용하기로",
    "채택",
    "합의",
)

ACTION_KEYWORDS = (
    "담당",
    "준비",
    "작성",
    "개발",
    "확인",
    "검토",
    "공유",
    "전달",
    "수정",
    "제출",
    "완료",
    "까지",
    "해주세요",
    "해 주세요",
)

STOPWORDS = {
    "그리고",
    "그러면",
    "그런데",
    "하지만",
    "저희",
    "우리",
    "오늘",
    "이번",
    "관련",
    "대한",
    "위해",
    "있는",
    "하는",
    "합니다",
    "했습니다",
    "것으로",
    "같습니다",
    "회의",
    "내용",
    "부분",
    "이제",
    "정도",
}


class MeetingMinutesService:
    """RTZR 전사 결과를 구조화된 회의록으로 변환한다."""

    def create_minutes(
        self,
        *,
        transcript_result: dict[str, Any],
    ) -> dict[str, Any]:
        utterances = self._extract_utterances(transcript_result)
        sentences = self._extract_sentences(utterances)
        full_text = " ".join(sentences)

        return {
            "summary": self._create_summary(sentences),
            "decisions": self._extract_decisions(sentences),
            "action_items": self._extract_action_items(sentences),
            "keywords": self._extract_keywords(full_text),
            "transcript": {
                "full_text": full_text,
                "utterances": utterances,
            },
        }

    @staticmethod
    def _extract_utterances(
        transcript_result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        results = transcript_result.get("results", {})
        raw_utterances = results.get("utterances", [])

        formatted_utterances: list[dict[str, Any]] = []

        for utterance in raw_utterances:
            text = str(utterance.get("msg", "")).strip()

            if not text:
                continue

            formatted_utterances.append(
                {
                    "speaker": int(utterance.get("spk", 0)) + 1,
                    "start_ms": int(utterance.get("start_at", 0)),
                    "duration_ms": int(utterance.get("duration", 0)),
                    "text": text,
                }
            )

        return formatted_utterances

    @staticmethod
    def _extract_sentences(
        utterances: list[dict[str, Any]],
    ) -> list[str]:
        sentences: list[str] = []

        for utterance in utterances:
            text = str(utterance["text"]).strip()

            parts = re.split(
                r"(?<=[.!?。])\s+|\n+",
                text,
            )

            sentences.extend(
                part.strip()
                for part in parts
                if part.strip()
            )

        return sentences

    @staticmethod
    def _create_summary(
        sentences: list[str],
        limit: int = 3,
    ) -> str:
        if not sentences:
            return "요약할 전사 내용이 없습니다."

        scored_sentences: list[tuple[int, int, str]] = []

        for index, sentence in enumerate(sentences):
            score = 0

            if any(
                keyword in sentence
                for keyword in DECISION_KEYWORDS
            ):
                score += 4

            if any(
                keyword in sentence
                for keyword in ACTION_KEYWORDS
            ):
                score += 2

            if 20 <= len(sentence) <= 150:
                score += 1

            # 회의 앞부분 문장에 약간의 가중치를 준다.
            score += max(0, 3 - index // 5)

            scored_sentences.append(
                (score, index, sentence)
            )

        selected = sorted(
            scored_sentences,
            key=lambda item: (-item[0], item[1]),
        )[:limit]

        selected.sort(key=lambda item: item[1])

        return " ".join(
            sentence
            for _, _, sentence in selected
        )

    @staticmethod
    def _extract_decisions(
        sentences: list[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        decisions: list[dict[str, Any]] = []

        for sentence in sentences:
            if any(
                keyword in sentence
                for keyword in DECISION_KEYWORDS
            ):
                decisions.append(
                    {
                        "id": len(decisions) + 1,
                        "content": sentence,
                    }
                )

            if len(decisions) >= limit:
                break

        return decisions

    @staticmethod
    def _extract_action_items(
        sentences: list[str],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        action_items: list[dict[str, Any]] = []

        for sentence in sentences:
            if any(
                keyword in sentence
                for keyword in ACTION_KEYWORDS
            ):
                action_items.append(
                    {
                        "id": len(action_items) + 1,
                        "task": sentence,
                        "assignee": None,
                        "due_date": None,
                        "status": "pending",
                    }
                )

            if len(action_items) >= limit:
                break

        return action_items

    @staticmethod
    def _extract_keywords(
        text: str,
        limit: int = 8,
    ) -> list[str]:
        tokens = re.findall(
            r"[가-힣A-Za-z][가-힣A-Za-z0-9_-]{1,}",
            text,
        )

        filtered_tokens = [
            token
            for token in tokens
            if token not in STOPWORDS
            and len(token) >= 2
        ]

        frequency = Counter(filtered_tokens)

        return [
            keyword
            for keyword, _ in frequency.most_common(limit)
        ]


meeting_minutes_service = MeetingMinutesService()