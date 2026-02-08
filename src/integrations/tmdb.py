import os

import httpx


class AsyncTMDb:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.getenv("TMDB_API_KEY")
        self.base = "https://api.themoviedb.org/3"

    async def _get(self, path: str, params: dict) -> dict:
        if not self.api_key:
            raise RuntimeError("TMDB_API_KEY not configured.")
        q = {"api_key": self.api_key, **params}
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(f"{self.base}{path}", params=q)
            r.raise_for_status()
            return r.json()

    async def search_first(self, query: str) -> dict | None:
        data = await self._get("/search/movie", {"query": query})
        results = data.get("results", [])
        return results[0] if results else None

    async def get_movie_details(self, movie_id: int) -> dict:
        return await self._get(f"/movie/{movie_id}", {"language": "en-US"})

    async def get_movie_credits(self, movie_id: int) -> dict:
        return await self._get(f"/movie/{movie_id}/credits", {"language": "en-US"})

    async def get_trending(self) -> list[dict]:
        data = await self._get("/trending/movie/week", {})
        return data.get("results", [])

    async def get_similar(self, movie_id: int) -> list[dict]:
        data = await self._get(f"/movie/{movie_id}/similar", {"language": "en-US"})
        return data.get("results", [])
