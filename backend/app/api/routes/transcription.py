from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
    Response,
    UploadFile,
    status,
)
from pydantic import ValidationError

from app.schemas.transcription import TranscriptionOptions
from app.services.file_service import (
    FileValidationError,
    delete_file,
    save_upload_file,
)
from app.services.job_service import (
    JobNotFoundError,
    job_service,
)
from app.services.markdown_service import (
    markdown_service,
)
from app.services.transcription_job_service import (
    process_transcription_job,
)

router = APIRouter(
    prefix="/transcriptions",
    tags=["Transcriptions"],
)

PROGRESS_MAP = {
    "queued": {
        "step": 1,
        "total_steps": 4,
        "label": "전사 작업을 준비하고 있습니다.",
    },
    "transcribing": {
        "step": 2,
        "total_steps": 4,
        "label": "음성을 텍스트로 변환하고 있습니다.",
    },
    "summarizing": {
        "step": 3,
        "total_steps": 4,
        "label": "회의록을 생성하고 있습니다.",
    },
    "completed": {
        "step": 4,
        "total_steps": 4,
        "label": "회의록 생성이 완료되었습니다.",
    },
    "failed": {
        "step": 0,
        "total_steps": 4,
        "label": "작업이 실패했습니다.",
    },
}


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="음성 파일 전사",
)
async def create_transcription(
    background_tasks: BackgroundTasks,
    file: Annotated[
        UploadFile,
        File(description="회의 음성 파일"),
    ],
    use_diarization: Annotated[
        bool,
        Form(),
    ] = True,
    speaker_count: Annotated[
        int | None,
        Form(),
    ] = None,
    remove_disfluency: Annotated[
        bool,
        Form(),
    ] = True,
    split_paragraph: Annotated[
        bool,
        Form(),
    ] = True,
    keywords: Annotated[
        str | None,
        Form(),
    ] = None,
):
    saved_file = None

    try:
        options = TranscriptionOptions(
            use_diarization=use_diarization,
            speaker_count=speaker_count,
            remove_disfluency=remove_disfluency,
            split_paragraph=split_paragraph,
            keywords=keywords,
        )

        saved_file = await save_upload_file(file)

        job = job_service.create_job(
            original_name=str(saved_file["original_name"]),
            stored_path=str(saved_file["stored_path"]),
            file_size=int(saved_file["size"]),
            options=options.model_dump(),
        )

        background_tasks.add_task(
            process_transcription_job,
            job["job_id"],
        )

        return {
            "success": True,
            "data": job,
            "error": None,
        }

    except ValidationError as exc:
        raise HTTPException(
            status_code=422,
            detail=exc.errors(),
        )

    except FileValidationError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception:
        if saved_file:
            delete_file(
                str(saved_file["stored_path"])
            )

        raise HTTPException(
            status_code=500,
            detail="파일 업로드 실패",
        )
        
@router.get(
    "/{job_id}",
    summary="전사 작업 상태 조회",
)
async def get_transcription_status(job_id: str):
    try:
        job = job_service.get_job(job_id)

        progress = PROGRESS_MAP.get(
            job["status"],
            {
                "step": 0,
                "total_steps": 4,
                "label": "상태를 확인할 수 없습니다.",
            },
        )

        data = {
            **job,
            "progress": progress,
        }

        if job["status"] == "completed":
            data["result_url"] = (
                f"/api/v1/transcriptions/{job_id}/result"
            )
            data["markdown_url"] = (
                f"/api/v1/transcriptions/{job_id}/markdown"
            )

        return {
            "success": True,
            "data": data,
            "error": None,
        }

    except JobNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )


@router.get(
    "/{job_id}/result",
    summary="회의록 결과 조회",
)
async def get_transcription_result(job_id: str):
    try:
        job = job_service.get_internal_job(job_id)

        meeting_minutes = _get_completed_meeting_minutes(job)

        return {
            "success": True,
            "data": {
                "job_id": job["job_id"],
                "status": job["status"],
                "file": {
                    "name": job["file"]["name"],
                    "size": job["file"]["size"],
                },
                "summary": meeting_minutes.get(
                    "summary",
                    "",
                ),
                "decisions": meeting_minutes.get(
                    "decisions",
                    [],
                ),
                "action_items": meeting_minutes.get(
                    "action_items",
                    [],
                ),
                "keywords": meeting_minutes.get(
                    "keywords",
                    [],
                ),
                "transcript": meeting_minutes.get(
    "transcript",
    {},
),
"generation_method": meeting_minutes.get(
    "generation_method",
    "unknown",
),
"fallback_reason": meeting_minutes.get(
    "fallback_reason",
),
"created_at": job["created_at"],
"updated_at": job["updated_at"],
            },
            "error": None,
        }

    except JobNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Job not found.",
        )
        
@router.get(
    "/{job_id}/markdown",
    summary="Markdown 회의록 다운로드",
    description="완료된 회의록을 Markdown 파일로 내려받습니다.",
    response_class=Response,
)
async def download_markdown(job_id: str) -> Response:
    try:
        job = job_service.get_internal_job(job_id)

        meeting_minutes = _get_completed_meeting_minutes(job)

        markdown = markdown_service.generate(
            file_name=job["file"]["name"],
            created_at=job["created_at"],
            meeting_minutes=meeting_minutes,
        )

        filename = _build_download_filename(
            job["file"]["name"]
        )

        encoded_filename = quote(filename)

        return Response(
            content=markdown,
            media_type="text/markdown; charset=utf-8",
            headers={
                "Content-Disposition": (
                    'attachment; filename="meeting_minutes.md"; '
                    f"filename*=UTF-8''{encoded_filename}"
                )
            },
        )

    except JobNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": "해당 작업을 찾을 수 없습니다.",
            },
        )


def _get_completed_meeting_minutes(
    job: dict[str, Any],
) -> dict[str, Any]:
    if job["status"] == "failed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "TRANSCRIPTION_FAILED",
                "message": (
                    "전사 작업이 실패하여 "
                    "결과를 조회할 수 없습니다."
                ),
                "error": job.get("error"),
            },
        )

    if job["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "RESULT_NOT_READY",
                "message": (
                    "아직 회의록 생성이 "
                    "완료되지 않았습니다."
                ),
                "status": job["status"],
            },
        )

    result = job.get("result")

    if not isinstance(result, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "RESULT_NOT_FOUND",
                "message": (
                    "완료된 회의록 결과를 "
                    "찾을 수 없습니다."
                ),
            },
        )

    meeting_minutes = result.get("meeting_minutes")

    if not isinstance(meeting_minutes, dict):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "MEETING_MINUTES_NOT_FOUND",
                "message": (
                    "구조화된 회의록 결과를 "
                    "찾을 수 없습니다."
                ),
            },
        )

    return meeting_minutes


def _build_download_filename(
    original_name: str,
) -> str:
    stem = Path(original_name).stem

    safe_name = "".join(
        character
        if character.isalnum()
        or character in {"-", "_"}
        else "_"
        for character in stem
    ).strip("_")

    if not safe_name:
        safe_name = "meeting"

    return f"{safe_name}_minutes.md"