from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import ValidationError

from app.schemas.transcription import TranscriptionOptions
from app.services.file_service import (
    FileValidationError,
    delete_file,
    save_upload_file,
)
from app.services.job_service import job_service


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
        "실제 음성 전사는 이후 백그라운드 작업에서 처리합니다."
    ),
)
async def create_transcription(
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