from __future__ import annotations

import logging
import os
from typing import Any

import requests
from rapidfuzz import fuzz

TMDB_API_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")


class TMDbClient:
    def __init__(self, api_key: str | None = None, ttl_seconds: int = 300) -> None:
        self.api_key = api_key or TMDB_API_KEY
        self.base_url = "https://api.themoviedb.org/3"
        if not self.api_key:
            # This is the error you are seeing
            raise ValueError("TMDB_API_KEY is not set.")
        self.session = requests.Session()
        self.cache: dict[tuple[str, tuple[tuple[str, str], ...]], tuple[float, dict]] = {}
        self.ttl = ttl_seconds

    def _get(self, path: str, params: dict[str, Any] | None = None, limit: int = -1) -> list[dict[str, Any]]:
        if params is None:
            params = {}
        params["api_key"] = self.api_key
        try:
            resp = requests.get(f"{self.base_url}/{path}", params=params)
            resp.raise_for_status()
            data = resp.json()
            # For single-item gets that don't have a 'results' key
            if "results" not in data:
                return [data] if isinstance(data, dict) else []
            results = data.get("results", [])
            if limit > 0 and results:
                return results[:limit]
            return results
        except requests.HTTPError as e:
            # Log specific HTTP errors, especially for authentication
            logging.error(f"TMDb API request failed with status {e.response.status_code}: {e.response.text}")
            return []
        except requests.RequestException as e:
            print(f"Error searching for movie '{query}': {e}")
            return None

    def search_movie(self, query: str, min_ratio: int = 70) -> dict | None:
        data = self._get("/search/movie", query=query, include_adult=False)
        results = data.get("results", [])
        if not results:
            return None
        best = None
        best_score = -1
        for r in results[:10]:
            title = r.get("title") or r.get("original_title") or ""
            score = fuzz.ratio(query.lower(), title.lower())
            if score > best_score:
                best_score = score
                best = r
        return best if best_score >= min_ratio else (results[0] if results else None)

    def movie_details(self, movie_id: int) -> dict:
        return self._get(f"/movie/{movie_id}", append_to_response="credits,similar")

    def similar_movies(self, movie_id: int, limit: int = 5) -> list[dict[str, Any]]:
        return self._get(f"movie/{movie_id}/similar", limit=limit)

    def upcoming_movies(self, limit: int = 5) -> list[dict[str, Any]]:
        return self._get("movie/upcoming", limit=limit)

    def trending_movies(self, limit: int = 5) -> list[dict[str, Any]]:
        data = self._get("/trending/movie/week")
        return data.get("results", [])[:limit]

    def popular_movies(self, limit: int = 5) -> list[dict[str, Any]]:
        data = self._get("/movie/popular")
        return data.get("results", [])[:limit]

    def search_person(self, name: str) -> dict | None:
        data = self._get("/search/person", query=name, include_adult=False)
        results = data.get("results", [])
        if not results:
            return None
        best = None
        best_score = -1
        for r in results[:10]:
            nm = r.get("name", "")
            score = fuzz.ratio(name.lower(), nm.lower())
            if score > best_score:
                best_score = score
                best = r
        return best or (results[0] if results else None)

    def person_credits(self, person_id: int, limit: int = 10) -> list[dict[str, Any]]:
        data = self._get(f"person/{person_id}/movie_credits")
        movies = [c for c in data.get("cast", []) if c.get("media_type") == "movie"]
        movies.sort(key=lambda x: (x.get("vote_count", 0), x.get("popularity", 0)), reverse=True)
        return movies[:limit]

    def get_all_movies_for_vector_store(self, num_pages: int = 20) -> list:
        """
        Fetches multiple pages of popular movies to build a comprehensive list
        for the vector store and entity recognizer.
        """
        print(f"Fetching {num_pages} pages of popular movies from TMDb...")
        all_movies = []
        for page in range(1, num_pages + 1):
            try:
                url = f"{self.base_url}/movie/popular?api_key={self.api_key}&page={page}"
                response = requests.get(url)
                response.raise_for_status()
                movies = response.json().get("results", [])
                for movie in movies:
                    # We only need essential info for the store
                    all_movies.append(
                        {
                            "id": movie.get("id"),
                            "title": movie.get("title"),
                            "overview": movie.get("overview"),
                        }
                    )
            except requests.RequestException as e:
                print(f"Error fetching page {page} of popular movies: {e}")
                break  # Stop if a page fails

        print(f"Fetched a total of {len(all_movies)} movies.")
        return all_movies

    def get_upcoming_movies(self) -> list:
        """Fetches a list of upcoming movies."""
        try:
            data = self._get("movie/upcoming", limit=5)
            return data.get("results", [])
        except requests.RequestException as e:
            logging.error(f"Error fetching upcoming movies: {e}")
            return []
