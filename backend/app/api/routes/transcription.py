from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    Form,
    HTTPException,
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
from app.services.job_service import JobNotFoundError, job_service
from app.services.transcription_job_service import (
    process_transcription_job,
)


router = APIRouter(
    prefix="/transcriptions",
    tags=["Transcriptions"],
)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="음성 파일 전사 작업 생성",
    description=(
        "회의 음성 파일을 업로드하고 전사 작업을 생성합니다. "
        "RTZR 전사 요청은 백그라운드에서 처리됩니다."
    ),
)
async def create_transcription(
    background_tasks: BackgroundTasks,
    file: Annotated[
        UploadFile,
        File(description="전사할 회의 음성 파일"),
    ],
    use_diarization: Annotated[
        bool,
        Form(description="화자 분리 사용 여부"),
    ] = True,
    speaker_count: Annotated[
        int | None,
        Form(description="예상 화자 수"),
    ] = None,
    remove_disfluency: Annotated[
        bool,
        Form(description="간투어 제거 여부"),
    ] = True,
    split_paragraph: Annotated[
        bool,
        Form(description="문단 자동 분리 여부"),
    ] = True,
    keywords: Annotated[
        str | None,
        Form(description="쉼표로 구분한 인식 강화 키워드"),
    ] = None,
):
    saved_file: dict[str, str | int] | None = None

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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_OPTION",
                "message": "전사 옵션이 올바르지 않습니다.",
                "details": exc.errors(),
            },
        ) from exc

    except FileValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_FILE",
                "message": str(exc),
            },
        ) from exc

    except Exception as exc:
        if saved_file is not None:
            delete_file(str(saved_file["stored_path"]))

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "code": "FILE_UPLOAD_FAILED",
                "message": "파일 업로드 처리 중 오류가 발생했습니다.",
            },
        ) from exc


@router.get(
    "/{job_id}",
    summary="전사 작업 상태 조회",
    description="전사 작업의 현재 상태와 진행 정보를 조회합니다.",
)
async def get_transcription_status(job_id: str):
    try:
        job = job_service.get_job(job_id)

        progress_map = {
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
                "label": "전사 결과를 회의록으로 정리하고 있습니다.",
            },
            "completed": {
                "step": 4,
                "total_steps": 4,
                "label": "회의록 생성이 완료되었습니다.",
            },
            "failed": {
                "step": 0,
                "total_steps": 4,
                "label": "전사 작업에 실패했습니다.",
            },
        }

        progress = progress_map.get(
            job["status"],
            {
                "step": 0,
                "total_steps": 4,
                "label": "작업 상태를 확인할 수 없습니다.",
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

        return {
            "success": True,
            "data": data,
            "error": None,
        }

    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": "해당 전사 작업을 찾을 수 없습니다.",
            },
        ) from exc
        
@router.get(
    "/{job_id}/result",
    summary="전사 결과 조회",
    description="완료된 전사 작업의 전체 전사문과 화자별 발언을 조회합니다.",
)
async def get_transcription_result(job_id: str):
    try:
        job = job_service.get_internal_job(job_id)

        if job["status"] == "failed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "TRANSCRIPTION_FAILED",
                    "message": "전사 작업이 실패하여 결과를 조회할 수 없습니다.",
                    "error": job.get("error"),
                },
            )

        if job["status"] != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "RESULT_NOT_READY",
                    "message": "아직 전사 작업이 완료되지 않았습니다.",
                    "status": job["status"],
                },
            )

        result = job.get("result")

        if not isinstance(result, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "code": "RESULT_NOT_FOUND",
                    "message": "완료된 전사 결과를 찾을 수 없습니다.",
                },
            )

        rtzr_results = result.get("results", {})
        utterances = rtzr_results.get("utterances", [])

        formatted_utterances = []
        full_text_parts = []

        for utterance in utterances:
            text = str(utterance.get("msg", "")).strip()

            if not text:
                continue

            speaker_number = int(utterance.get("spk", 0)) + 1
            start_ms = int(utterance.get("start_at", 0))
            duration_ms = int(utterance.get("duration", 0))

            formatted_utterances.append(
                {
                    "speaker": speaker_number,
                    "start_ms": start_ms,
                    "duration_ms": duration_ms,
                    "text": text,
                }
            )

            full_text_parts.append(text)

        return {
            "success": True,
            "data": {
                "job_id": job["job_id"],
                "status": job["status"],
                "file": {
                    "name": job["file"]["name"],
                    "size": job["file"]["size"],
                },
                "transcript": {
                    "full_text": " ".join(full_text_parts),
                    "utterances": formatted_utterances,
                },
                "created_at": job["created_at"],
                "updated_at": job["updated_at"],
            },
            "error": None,
        }

    except JobNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "JOB_NOT_FOUND",
                "message": "해당 전사 작업을 찾을 수 없습니다.",
            },
        ) from exc