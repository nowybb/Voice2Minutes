from __future__ import annotations

from typing import Any

import httpx

from app.services.rtzr.auth import RTZRAuthService, rtzr_auth_service
from app.services.rtzr.client import RTZRClient


class RTZRPollingError(RuntimeError):
    """RTZR 전사 결과 조회에 실패했을 때 발생하는 예외."""

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


class RTZRPollingService:
    """RTZR 전사 작업 상태와 결과를 조회한다."""

    def __init__(
        self,
        client: RTZRClient | None = None,
        auth_service: RTZRAuthService | None = None,
    ) -> None:
        self._client = client or RTZRClient(timeout=60)
        self._auth_service = auth_service or rtzr_auth_service

    async def get_transcription(
        self,
        transcribe_id: str,
    ) -> dict[str, Any]:
        access_token = await self._auth_service.get_access_token()

        try:
            response = await self._client.get(
                f"/v1/transcribe/{transcribe_id}",
                headers={
                    "Accept": "application/json",
                    "Authorization": f"Bearer {access_token}",
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise RTZRPollingError(
                "RTZR 전사 결과 조회 시간이 초과되었습니다."
            ) from exc

        except httpx.HTTPStatusError as exc:
            raise self._convert_http_error(exc.response) from exc

        except httpx.RequestError as exc:
            raise RTZRPollingError(
                "RTZR 전사 결과 조회 서버에 연결할 수 없습니다."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RTZRPollingError(
                "RTZR 전사 결과를 JSON으로 해석할 수 없습니다."
            ) from exc

        status_value = payload.get("status")

        if not status_value:
            raise RTZRPollingError(
                "RTZR 응답에 전사 상태가 없습니다."
            )

        return payload

    @staticmethod
    def _convert_http_error(
        response: httpx.Response,
    ) -> RTZRPollingError:
        try:
            payload = response.json()
        except ValueError:
            payload = {}

        code = payload.get("code")
        message = (
            payload.get("msg")
            or payload.get("message")
            or "RTZR 전사 결과 조회에 실패했습니다."
        )

        return RTZRPollingError(
            str(message),
            code=str(code) if code else None,
            status_code=response.status_code,
        )

    async def close(self) -> None:
        await self._client.close()


rtzr_polling_service = RTZRPollingService()