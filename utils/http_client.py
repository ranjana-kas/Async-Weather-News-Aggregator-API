import httpx
from typing import Optional

class AsyncClientWrapper:
    # We use None initially and create the client when the app starts
    client: Optional[httpx.AsyncClient] = None

    @classmethod
    def get_client(cls) -> httpx.AsyncClient:
        if cls.client is None:
            # Limits help prevent the API from being overwhelmed
            limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
            cls.client = httpx.AsyncClient(timeout=10.0, limits=limits)
        return cls.client

    @classmethod
    async def close_client(cls):
        if cls.client:
            await cls.client.aclose()
            cls.client = None