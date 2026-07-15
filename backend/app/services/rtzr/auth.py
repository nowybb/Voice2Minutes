from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from app.core.config import get_settings
from app.services.rtzr.client import RTZRClient


class RTZRAuthenticationError(RuntimeError):
    """RTZR 인증 토큰 발급에 실패했을 때 발생하는 예외."""


class RTZRAuthService:
    """RTZR 인증 토큰을 발급하고 만료 전까지 재사용한다."""

    TOKEN_REFRESH_BUFFER_SECONDS = 300  # 만료 5분 전 갱신

    def __init__(self, client: RTZRClient | None = None) -> None:
        self._client = client or RTZRClient()
        self._access_token: str | None = None
        self._expire_at: int = 0
        self._lock = asyncio.Lock()

    async def get_access_token(self) -> str:
        """사용 가능한 토큰을 반환하고, 필요하면 새로 발급한다."""
        if self._is_token_valid():
            return self._access_token  # type: ignore[return-value]

        async with self._lock:
            # Lock 대기 중 다른 요청이 토큰을 갱신했을 수 있으므로 재확인한다.
            if self._is_token_valid():
                return self._access_token  # type: ignore[return-value]

            token_data = await self._request_access_token()

            self._access_token = token_data["access_token"]
            self._expire_at = int(token_data["expire_at"])

            return self._access_token

    async def _request_access_token(self) -> dict[str, Any]:
        settings = get_settings()

        try:
            response = await self._client.post(
                "/v1/authenticate",
                headers={
                    "Accept": "application/json",
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                data={
                    "client_id": settings.RTZR_CLIENT_ID,
                    "client_secret": settings.RTZR_CLIENT_SECRET,
                },
            )

            response.raise_for_status()

        except httpx.TimeoutException as exc:
            raise RTZRAuthenticationError(
                "RTZR 인증 요청 시간이 초과되었습니다."
            ) from exc

        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code

            raise RTZRAuthenticationError(
                f"RTZR 인증에 실패했습니다. HTTP 상태 코드: {status_code}"
            ) from exc

        except httpx.RequestError as exc:
            raise RTZRAuthenticationError(
                "RTZR 인증 서버에 연결할 수 없습니다."
            ) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise RTZRAuthenticationError(
                "RTZR 인증 응답을 JSON으로 해석할 수 없습니다."
            ) from exc

        access_token = payload.get("access_token")
        expire_at = payload.get("expire_at")

        if not access_token or expire_at is None:
            raise RTZRAuthenticationError(
                "RTZR 인증 응답에 access_token 또는 expire_at이 없습니다."
            )

        return {
            "access_token": str(access_token),
            "expire_at": int(expire_at),
        }

    def _is_token_valid(self) -> bool:
        if not self._access_token:
            return False

        refresh_threshold = (
            self._expire_at - self.TOKEN_REFRESH_BUFFER_SECONDS
        )

        return int(time.time()) < refresh_threshold

    async def close(self) -> None:
        await self._client.close()


rtzr_auth_service = RTZRAuthService()