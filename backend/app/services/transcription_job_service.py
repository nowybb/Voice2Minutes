from __future__ import annotations

from app.services.file_service import delete_file
from app.services.job_service import JobNotFoundError, job_service
from app.services.rtzr.transcription import (
    RTZRTranscriptionError,
    rtzr_transcription_service,
)


async def process_transcription_job(job_id: str) -> None:
    """
    저장된 음성 파일을 RTZR에 전달하고 작업 상태를 갱신한다.

    처리 흐름:
    queued
        → transcribing
        → RTZR 전사 작업 ID 저장

    오류 발생 시:
    queued 또는 transcribing
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

    except JobNotFoundError:
        # 작업 자체가 삭제된 경우에는 별도 상태 갱신이 불가능하다.
        return

    except RTZRTranscriptionError as exc:
        job_service.update_job(
            job_id,
            status="failed",
            error={
                "code": exc.code or "RTZR_TRANSCRIPTION_ERROR",
                "message": str(exc),
                "status_code": exc.status_code,
            },
        )

    except Exception:
        job_service.update_job(
            job_id,
            status="failed",
            error={
                "code": "TRANSCRIPTION_REQUEST_FAILED",
                "message": "전사 작업 요청 중 예상하지 못한 오류가 발생했습니다.",
            },
        )

    finally:
        if stored_path:
            delete_file(stored_path)