from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import UUID, uuid4


class JobNotFoundError(KeyError):
    """요청한 전사 작업을 찾을 수 없을 때 발생하는 예외."""


class JobService:
    """전사 작업 정보를 메모리에 저장하고 관리한다."""

    def __init__(self) -> None:
        self._jobs: dict[str, dict[str, Any]] = {}
        self._lock = Lock()

    def create_job(
        self,
        *,
        original_name: str,
        stored_path: str,
        file_size: int,
        options: dict[str, Any],
    ) -> dict[str, Any]:
        job_id = str(uuid4())
        now = datetime.now(timezone.utc).isoformat()

        job = {
            "job_id": job_id,
            "status": "queued",
            "file": {
                "name": original_name,
                "stored_path": stored_path,
                "size": file_size,
            },
            "options": options,
            "rtzr_transcribe_id": None,
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

        with self._lock:
            self._jobs[job_id] = job

        return self._public_job(job)

    def get_job(self, job_id: str) -> dict[str, Any]:
        self._validate_job_id(job_id)

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                raise JobNotFoundError(job_id)

            return self._public_job(job)

    def get_internal_job(self, job_id: str) -> dict[str, Any]:
        """서비스 내부 처리에 필요한 저장 경로까지 포함하여 조회한다."""
        self._validate_job_id(job_id)

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                raise JobNotFoundError(job_id)

            return dict(job)

    def update_job(
        self,
        job_id: str,
        **changes: Any,
    ) -> dict[str, Any]:
        self._validate_job_id(job_id)

        with self._lock:
            job = self._jobs.get(job_id)

            if job is None:
                raise JobNotFoundError(job_id)

            job.update(changes)
            job["updated_at"] = datetime.now(timezone.utc).isoformat()

            return self._public_job(job)

    def delete_job(self, job_id: str) -> dict[str, Any]:
        self._validate_job_id(job_id)

        with self._lock:
            job = self._jobs.pop(job_id, None)

            if job is None:
                raise JobNotFoundError(job_id)

            return dict(job)

    @staticmethod
    def _validate_job_id(job_id: str) -> None:
        try:
            UUID(job_id)
        except ValueError as exc:
            raise JobNotFoundError(job_id) from exc

    @staticmethod
    def _public_job(job: dict[str, Any]) -> dict[str, Any]:
        """응답에서 서버 내부 파일 경로를 제거한다."""
        public_file = {
            "name": job["file"]["name"],
            "size": job["file"]["size"],
        }

        return {
            "job_id": job["job_id"],
            "status": job["status"],
            "file": public_file,
            "options": job["options"],
            "error": job["error"],
            "created_at": job["created_at"],
            "updated_at": job["updated_at"],
        }


job_service = JobService()