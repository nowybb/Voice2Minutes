from __future__ import annotations

import json
import mimetypes
from pathlib import Path
from typing import Any

import httpx

from app.services.rtzr.auth import RTZRAuthService, rtzr_auth_service
from app.services.rtzr.client import RTZRClient


class RTZRTranscriptionError(RuntimeError):
    """RTZR 파일 전사 요청이 실패했을 때 발생하는 예외."""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status_code = status_code


class RTZRTranscriptionService:
    """RTZR 일반 STT 파일 전사 요청을 처리한다."""

    def __init__(
        self,
        client: RTZRClient | None = None,
        auth_service: RTZRAuthService | None = None,
    ) -> None:
        self._client = client or RTZRClient(timeout=300)
        self._auth_service = auth_service or rtzr_auth_service

    async def request_transcription(
        self,
        *,
        file_path: str,
        options: dict[str, Any],
    ) -> str:
        """
        음성 파일을 RTZR에 전달하고 전사 작업 ID를 반환한다.
        """

        path = Path(file_path)

        if not path.exists():
            raise RTZRTranscriptionError(
                "전사할 음성 파일을 찾을 수 없습니다."
            )

        if not path.is_file():
            raise RTZRTranscriptionError(
                "전사 요청 경로가 파일이 아닙니다."
            )

        access_token = await self._auth_service.get_access_token()
        config = self._build_config(options)

        mime_type = (
            mimetypes.guess_type(path.name)[0]
            or "application/octet-stream"
        )

        try:
            with path.open("rb") as audio_file:
                response = await self._client.post(
                    "/v1/transcribe",
                    headers={
                        "Accept": "application/json",
                        "Authorization": f"Bearer {access_token}",
                    },
                    data={
                        "config": json.dumps(
                            config,
                            ensure_ascii=False,
                        )
                    },
                    files={
                        "file": (
                            path.name,
                            audio_file,
                            mime_type,
                        )
                    },
                )

            response.raise_for_status()

        except OSError as exc:
            raise RTZRTranscriptionError(
                "음성 파일을 읽는 중 오류가 발생했습니다."
            ) from exc

        except httpx.TimeoutException as exc:
            raise RTZRTranscriptionError(
                "RTZR 전사 요청 시간이 초과되었습니다."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise self._convert_http_error(exc.response) from exc

        except httpx.RequestError as exc:
            raise RTZRTranscriptionError(
                "RTZR 전사 서버에 연결할 수 없습니다."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RTZRTranscriptionError(
                "RTZR 전사 응답을 JSON으로 해석할 수 없습니다."
            ) from exc

        transcribe_id = payload.get("id")

        if not transcribe_id:
            raise RTZRTranscriptionError(
                "RTZR 응답에 전사 작업 ID가 없습니다."
            )

        return str(transcribe_id)

    @staticmethod
    def _build_config(
        options: dict[str, Any],
    ) -> dict[str, Any]:
        config: dict[str, Any] = {
            "model_name": "sommers",
            "language": "ko",
            "domain": "GENERAL",
            "use_diarization": bool(
                options.get("use_diarization", True)
            ),
            "use_disfluency_filter": bool(
                options.get("remove_disfluency", True)
            ),
            "use_paragraph_splitter": bool(
                options.get("split_paragraph", True)
            ),
        }

        if config["use_diarization"]:
            speaker_count = options.get("speaker_count")

            if speaker_count is not None:
                config["diarization"] = {
                    "spk_count": int(speaker_count)
                }

        if config["use_paragraph_splitter"]:
            config["paragraph_splitter"] = {
                "max": 80
            }

        keywords = RTZRTranscriptionService._parse_keywords(
            options.get("keywords")
        )

        if keywords:
            config["keywords"] = keywords

        return config

    @staticmethod
    def _parse_keywords(
        keywords: Any,
    ) -> list[str]:
        if not keywords:
            return []

        if isinstance(keywords, list):
            values = keywords
        else:
            values = str(keywords).split(",")

        return [
            str(keyword).strip()
            for keyword in values
            if str(keyword).strip()
        ]

    @staticmethod
    def _convert_http_error(
        response: httpx.Response,
    ) -> RTZRTranscriptionError:
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        code = payload.get("code")
        message = (
            payload.get("msg")
            or payload.get("message")
            or "RTZR 전사 요청에 실패했습니다."
        )

        return RTZRTranscriptionError(
            message,
            code=str(code) if code else None,
            status_code=response.status_code,
        )

    async def close(self) -> None:
        await self._client.close()


rtzr_transcription_service = RTZRTranscriptionService()