from __future__ import annotations

import asyncio
import time
from typing import Any

from app.services.file_service import delete_file
from app.services.job_service import JobNotFoundError, job_service
from app.services.meeting_minutes_service import meeting_minutes_service
from app.services.rtzr.polling import (
    RTZRPollingError,
    rtzr_polling_service,
)
from app.services.rtzr.transcription import (
    RTZRTranscriptionError,
    rtzr_transcription_service,
)


POLL_INTERVAL_SECONDS = 5
POLL_TIMEOUT_SECONDS = 3600


async def process_transcription_job(job_id: str) -> None:
    """
    저장된 음성 파일을 RTZR에 전달하고,
    전사 완료 후 구조화된 회의록을 생성한다.

    상태 흐름:
    queued
        → transcribing
        → summarizing
        → completed

    오류 발생 시:
    queued / transcribing / summarizing
        → failed
    """

    stored_path: str | None = None

    try:
        job = job_service.get_internal_job(job_id)

        stored_path = str(job["file"]["stored_path"])
        options = dict(job["options"])

        job_service.update_job(
            job_id,
            status="transcribing",
            error=None,
        )

        rtzr_transcribe_id = (
            await rtzr_transcription_service.request_transcription(
                file_path=stored_path,
                options=options,
            )
        )

        job_service.update_job(
            job_id,
            status="transcribing",
            rtzr_transcribe_id=rtzr_transcribe_id,
        )

        delete_file(stored_path)
        stored_path = None

        transcript_result = await poll_transcription_result(
            job_id=job_id,
            rtzr_transcribe_id=rtzr_transcribe_id,
        )

        job_service.update_job(
            job_id,
            status="summarizing",
            error=None,
        )

        meeting_minutes = meeting_minutes_service.create_minutes(
            transcript_result=transcript_result,
        )

        job_service.update_job(
            job_id,
            status="completed",
            result={
                "raw_transcription": transcript_result,
                "meeting_minutes": meeting_minutes,
            },
            error=None,
        )

    except JobNotFoundError:
        return

    except RTZRTranscriptionError as exc:
        _mark_job_failed(
            job_id=job_id,
            code=exc.code or "RTZR_TRANSCRIPTION_ERROR",
            message=str(exc),
            status_code=exc.status_code,
        )

    except RTZRPollingError as exc:
        _mark_job_failed(
            job_id=job_id,
            code=exc.code or "RTZR_POLLING_ERROR",
            message=str(exc),
            status_code=exc.status_code,
        )

    except TimeoutError as exc:
        _mark_job_failed(
            job_id=job_id,
            code="TRANSCRIPTION_TIMEOUT",
            message=str(exc),
        )

    except Exception:
        _mark_job_failed(
            job_id=job_id,
            code="TRANSCRIPTION_PROCESS_FAILED",
            message="전사 및 회의록 생성 중 예상하지 못한 오류가 발생했습니다.",
        )

    finally:
        if stored_path:
            delete_file(stored_path)


async def poll_transcription_result(
    *,
    job_id: str,
    rtzr_transcribe_id: str,
) -> dict[str, Any]:
    """
    RTZR 전사 결과를 일정 간격으로 조회하고,
    완료된 원본 응답을 반환한다.
    """

    started_at = time.monotonic()

    while True:
        if time.monotonic() - started_at > POLL_TIMEOUT_SECONDS:
            raise TimeoutError(
                "RTZR 전사 결과 대기 시간이 초과되었습니다."
            )

        result = await rtzr_polling_service.get_transcription(
            rtzr_transcribe_id
        )

        rtzr_status = result.get("status")

        if rtzr_status == "completed":
            return result

        if rtzr_status == "failed":
            error = _extract_rtzr_error(result)

            job_service.update_job(
                job_id,
                status="failed",
                result=None,
                error=error,
            )

            raise RTZRPollingError(
                error["message"],
                code=error["code"],
            )

        if rtzr_status != "transcribing":
            raise RTZRPollingError(
                f"알 수 없는 RTZR 전사 상태입니다: {rtzr_status}"
            )

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


def _extract_rtzr_error(
    result: dict[str, Any],
) -> dict[str, Any]:
    error = result.get("error")

    if isinstance(error, dict):
        return {
            "code": error.get(
                "code",
                "RTZR_TRANSCRIPTION_FAILED",
            ),
            "message": error.get(
                "message",
                "RTZR 전사 작업에 실패했습니다.",
            ),
        }

    return {
        "code": "RTZR_TRANSCRIPTION_FAILED",
        "message": "RTZR 전사 작업에 실패했습니다.",
    }


def _mark_job_failed(
    *,
    job_id: str,
    code: str,
    message: str,
    status_code: int | None = None,
) -> None:
    error: dict[str, Any] = {
        "code": code,
        "message": message,
    }

    if status_code is not None:
        error["status_code"] = status_code

    try:
        job_service.update_job(
            job_id,
            status="failed",
            result=None,
            error=error,
        )
    except JobNotFoundError:
        pass