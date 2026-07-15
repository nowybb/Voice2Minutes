from __future__ import annotations

from typing import Any

import httpx


class RTZRClient:
    """
    ReturnZero STT API Client

    모든 HTTP 통신을 담당한다.
    """

    BASE_URL = "https://openapi.vito.ai"

    def __init__(self, timeout: int = 60):
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
        )

    async def get(
        self,
        url: str,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        return await self.client.get(
            url,
            headers=headers,
        )

    async def post(
        self,
        url: str,
        headers: dict[str, str] | None = None,
        data: Any = None,
        files: Any = None,
        json: Any = None,
    ) -> httpx.Response:

        return await self.client.post(
            url,
            headers=headers,
            data=data,
            files=files,
            json=json,
        )

    async def close(self):
        await self.client.aclose()