from __future__ import annotations

from typing import Any


class MarkdownService:
    """구조화된 회의록을 Markdown 문자열로 변환한다."""

    def generate(
        self,
        *,
        file_name: str,
        created_at: str,
        meeting_minutes: dict[str, Any],
    ) -> str:
        summary = str(
            meeting_minutes.get(
                "summary",
                "요약 정보가 없습니다.",
            )
        )

        decisions = meeting_minutes.get("decisions", [])
        action_items = meeting_minutes.get("action_items", [])
        keywords = meeting_minutes.get("keywords", [])
        transcript = meeting_minutes.get("transcript", {})

        decision_lines = self._build_decision_lines(decisions)
        action_item_lines = self._build_action_item_lines(action_items)
        keyword_text = self._build_keyword_text(keywords)
        transcript_text = self._build_transcript_text(transcript)

        markdown = (
            "# Voice2Minutes 회의록\n\n"
            "## 회의 정보\n\n"
            f"- 원본 파일: {file_name}\n"
            f"- 생성 시각: {created_at}\n\n"
            "## 핵심 요약\n\n"
            f"{summary}\n\n"
            "## 결정 사항\n\n"
            f"{decision_lines}\n\n"
            "## Action Items\n\n"
            f"{action_item_lines}\n\n"
            "## 주요 키워드\n\n"
            f"{keyword_text}\n\n"
            "## 전체 전사문\n\n"
            f"{transcript_text}\n"
        )

        return markdown

    @staticmethod
    def _build_decision_lines(
        decisions: list[dict[str, Any]],
    ) -> str:
        if not decisions:
            return "- 결정 사항이 없습니다."

        lines = [
            f"- {item.get('content', '')}"
            for item in decisions
            if item.get("content")
        ]

        return "\n".join(lines) or "- 결정 사항이 없습니다."

    @staticmethod
    def _build_action_item_lines(
        action_items: list[dict[str, Any]],
    ) -> str:
        if not action_items:
            return "- 실행 항목이 없습니다."

        lines: list[str] = []

        for item in action_items:
            task = str(item.get("task", "")).strip()

            if not task:
                continue

            assignee = item.get("assignee") or "미정"
            due_date = item.get("due_date") or "미정"

            lines.append(
                f"- [ ] {task} — 담당: {assignee}, 기한: {due_date}"
            )

        return "\n".join(lines) or "- 실행 항목이 없습니다."

    @staticmethod
    def _build_keyword_text(
        keywords: list[Any],
    ) -> str:
        values = [
            str(keyword).strip()
            for keyword in keywords
            if str(keyword).strip()
        ]

        return ", ".join(values) or "없음"

    def _build_transcript_text(
        self,
        transcript: dict[str, Any],
    ) -> str:
        utterances = transcript.get("utterances", [])

        if utterances:
            lines: list[str] = []

            for utterance in utterances:
                timestamp = self._format_timestamp(
                    int(utterance.get("start_ms", 0))
                )
                speaker = utterance.get("speaker", 1)
                text = str(
                    utterance.get("text", "")
                ).strip()

                if not text:
                    continue

                lines.append(
                    f"[{timestamp}] 화자 {speaker}: {text}"
                )

            if lines:
                return "\n".join(lines)

        return str(
            transcript.get("full_text", "")
        ).strip()

    @staticmethod
    def _format_timestamp(
        milliseconds: int,
    ) -> str:
        total_seconds = max(
            0,
            milliseconds // 1000,
        )

        minutes, seconds = divmod(
            total_seconds,
            60,
        )
        hours, minutes = divmod(
            minutes,
            60,
        )

        if hours > 0:
            return (
                f"{hours:02d}:"
                f"{minutes:02d}:"
                f"{seconds:02d}"
            )

        return f"{minutes:02d}:{seconds:02d}"


markdown_service = MarkdownService()