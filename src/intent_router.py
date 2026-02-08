from __future__ import annotations

from typing import Any

from .services.tmdb import TMDbClient
from .store.memory import MemoryStore


class IntentRouter:
    def __init__(self, tmdb_client: TMDbClient, store: MemoryStore):
        self.tmdb_client = tmdb_client
        self.store = store
        # This threshold is for the semantic similarity score
        self.intent_confidence_threshold = 0.45

    def route(self, nlp_result: dict) -> Any:
        """
        Routes the NLP result to the correct method and returns structured data.
        """
        intent = nlp_result.get("intent")
        confidence = nlp_result.get("intent_confidence", 0)

        if confidence < self.intent_confidence_threshold:
            return None  # Indicates fallback

        entities = nlp_result.get("entities", {})
        movie_title = entities.get("movie_title")

        if intent == "upcoming_releases":
            return self.tmdb_client.get_upcoming_movies()

        elif intent == "who_directed":
            if not movie_title:
                return None  # Not enough info
            movie = self.tmdb_client.search_movie(movie_title)
            if not movie:
                return None
            director = self.tmdb_client.get_director(movie["id"])
            return {"movie": movie, "director": director}

        elif intent == "recommend":
            if not movie_title:
                return None  # Not enough info

            # Use the vector store to find similar movies
            similar_movies_ids = self.store.search_similar_movies(movie_title, top_k=5)
            if not similar_movies_ids:
                return None

            # Get full movie details from TMDb
            recommended_movies = [self.tmdb_client.get_movie_details(movie_id) for movie_id in similar_movies_ids]
            return [movie for movie in recommended_movies if movie]  # Filter out any None results

        return None
