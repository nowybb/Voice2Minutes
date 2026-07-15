from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import aiofiles
from fastapi import UploadFile


ALLOWED_EXTENSIONS = {
    ".mp3",
    ".m4a",
    ".mp4",
    ".wav",
    ".flac",
    ".amr",
}

MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

UPLOAD_DIR = Path("uploads")


class FileValidationError(ValueError):
    """업로드 파일 검증 실패 예외."""


def validate_file_extension(filename: str | None) -> str:
    if not filename:
        raise FileValidationError("파일명이 없습니다.")

    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise FileValidationError(
            "지원하지 않는 파일 형식입니다. "
            "MP3, M4A, MP4, WAV, FLAC, AMR 파일만 업로드할 수 있습니다."
        )

    return extension


async def validate_file_size(file: UploadFile) -> int:
    total_size = 0
    chunk_size = 1024 * 1024  # 1MB

    while chunk := await file.read(chunk_size):
        total_size += len(chunk)

        if total_size > MAX_FILE_SIZE:
            await file.seek(0)
            raise FileValidationError("파일 크기는 2GB 이하여야 합니다.")

    await file.seek(0)

    if total_size == 0:
        raise FileValidationError("빈 파일은 업로드할 수 없습니다.")

    return total_size


async def save_upload_file(file: UploadFile) -> dict[str, str | int]:
    extension = validate_file_extension(file.filename)
    file_size = await validate_file_size(file)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    stored_filename = f"{uuid4()}{extension}"
    stored_path = UPLOAD_DIR / stored_filename

    try:
        async with aiofiles.open(stored_path, "wb") as output_file:
            while chunk := await file.read(1024 * 1024):
                await output_file.write(chunk)
    except OSError as exc:
        stored_path.unlink(missing_ok=True)
        raise RuntimeError("파일 저장 중 오류가 발생했습니다.") from exc
    finally:
        await file.close()

    return {
        "original_name": file.filename or stored_filename,
        "stored_name": stored_filename,
        "stored_path": str(stored_path),
        "size": file_size,
    }


def delete_file(file_path: str | Path) -> None:
    Path(file_path).unlink(missing_ok=True)