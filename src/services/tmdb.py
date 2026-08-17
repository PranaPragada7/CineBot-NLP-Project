from __future__ import annotations

import logging
import os
from typing import Any

import requests
from rapidfuzz import fuzz, process

from src.catalog import OFFLINE_MOVIES

LOGGER = logging.getLogger(__name__)


class TMDbClient:
    """Small TMDB client with a deterministic offline fallback catalog."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        session: requests.Session | None = None,
        timeout: float = 8.0,
    ) -> None:
        configured_key = os.getenv("TMDB_API_KEY") if api_key is None else api_key
        self.api_key = configured_key.strip() if configured_key else None
        self.base_url = "https://api.themoviedb.org/3"
        self.session = session or requests.Session()
        self.timeout = timeout

    @property
    def is_live(self) -> bool:
        return bool(self.api_key)

    @property
    def source_label(self) -> str:
        return "TMDB live data" if self.is_live else "built-in offline catalog"

    @property
    def known_titles(self) -> list[str]:
        return [movie["title"] for movie in OFFLINE_MOVIES]

    def _get(self, path: str, **params: Any) -> dict[str, Any] | None:
        if not self.api_key:
            return None

        params["api_key"] = self.api_key
        try:
            response = self.session.get(
                f"{self.base_url}/{path.lstrip('/')}",
                params=params,
                timeout=self.timeout,
            )
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, dict) else None
        except (requests.RequestException, ValueError) as exc:
            LOGGER.warning("TMDB request failed for %s: %s", path, exc)
            return None

    @staticmethod
    def _normalize(movie: dict[str, Any]) -> dict[str, Any]:
        genres = movie.get("genres") or movie.get("genre_names") or []
        normalized_genres = [
            genre.get("name", "") if isinstance(genre, dict) else str(genre) for genre in genres
        ]
        return {
            "id": movie.get("id"),
            "title": movie.get("title") or movie.get("original_title") or "Untitled",
            "release_date": movie.get("release_date") or "",
            "overview": movie.get("overview") or "No overview is available.",
            "vote_average": float(movie.get("vote_average") or 0),
            "genres": [genre for genre in normalized_genres if genre],
            "director": movie.get("director"),
        }

    @staticmethod
    def _offline_by_id(movie_id: int) -> dict[str, Any] | None:
        return next((dict(movie) for movie in OFFLINE_MOVIES if movie["id"] == movie_id), None)

    def _offline_search(self, query: str) -> dict[str, Any] | None:
        match = process.extractOne(
            query,
            self.known_titles,
            scorer=fuzz.WRatio,
            score_cutoff=55,
        )
        if not match:
            return None
        title = match[0]
        return next(dict(movie) for movie in OFFLINE_MOVIES if movie["title"] == title)

    def search_movie(self, query: str) -> dict[str, Any] | None:
        query = query.strip()
        if not query:
            return None

        payload = self._get("search/movie", query=query, include_adult="false")
        results = payload.get("results", []) if payload else []
        if results:
            best = max(
                results[:10],
                key=lambda movie: fuzz.WRatio(
                    query,
                    movie.get("title") or movie.get("original_title") or "",
                ),
            )
            return self._normalize(best)
        return self._offline_search(query)

    def movie_details(self, movie_id: int) -> dict[str, Any] | None:
        payload = self._get(f"movie/{movie_id}", append_to_response="credits")
        if payload:
            movie = self._normalize(payload)
            crew = payload.get("credits", {}).get("crew", [])
            director = next(
                (member.get("name") for member in crew if member.get("job") == "Director"),
                None,
            )
            movie["director"] = director
            return movie
        return self._offline_by_id(movie_id)

    def similar_movies(self, movie_id: int, limit: int = 5) -> list[dict[str, Any]]:
        payload = self._get(f"movie/{movie_id}/similar")
        results = payload.get("results", []) if payload else []
        if results:
            return [self._normalize(movie) for movie in results[:limit]]

        seed = self._offline_by_id(movie_id)
        if not seed:
            return []
        seed_genres = set(seed["genres"])
        candidates = [movie for movie in OFFLINE_MOVIES if movie["id"] != movie_id]
        candidates.sort(
            key=lambda movie: (
                len(seed_genres.intersection(movie["genres"])),
                movie["vote_average"],
            ),
            reverse=True,
        )
        return [dict(movie) for movie in candidates[:limit]]

    def upcoming_movies(self, limit: int = 5) -> list[dict[str, Any]]:
        payload = self._get("movie/upcoming", language="en-US", region="US")
        results = payload.get("results", []) if payload else []
        if results:
            return [self._normalize(movie) for movie in results[:limit]]
        return [dict(movie) for movie in OFFLINE_MOVIES[:limit]]

    def trending_movies(self, limit: int = 5) -> list[dict[str, Any]]:
        payload = self._get("trending/movie/week", language="en-US")
        results = payload.get("results", []) if payload else []
        if results:
            return [self._normalize(movie) for movie in results[:limit]]
        return [
            dict(movie)
            for movie in sorted(
                OFFLINE_MOVIES,
                key=lambda item: item["vote_average"],
                reverse=True,
            )[:limit]
        ]
