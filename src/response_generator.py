from __future__ import annotations

from typing import Any, Dict, List


class ResponseGenerator:
    """
    Generates user-friendly text responses from structured data.
    """

    def generate(self, intent: str, data: Any) -> str:
        """
        Selects the appropriate generation method based on the intent.
        """
        method_name = f"_generate_{intent}"
        generator_method = getattr(self, method_name, self._generate_fallback)
        return generator_method(data)

    def _generate_fallback(self, data: Any) -> str:
        return "I'm not sure how to help with that. You can ask me about new releases, movie directors, or for recommendations."

    def _generate_upcoming_releases(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "I couldn't find any upcoming movies right now."

        movie_titles = [f"- {movie['title']} (releasing on {movie['release_date']})" for movie in data]
        return "Here are some of the latest upcoming releases:\n" + "\n".join(movie_titles)

    def _generate_who_directed(self, data: Dict[str, Any]) -> str:
        if not data or "director" not in data:
            return "I couldn't find the director for that movie. Please make sure you've spelled the title correctly."

        movie_title = data["movie"]["title"]
        director_name = data["director"]
        return f"The director of '{movie_title}' is {director_name}."

    def _generate_recommend(self, data: List[Dict[str, Any]]) -> str:
        if not data:
            return "I couldn't find any recommendations for that movie. It might be too obscure or new."

        movie_titles = [f"- {movie['title']}" for movie in data]
        return "Based on your request, you might like these movies:\n" + "\n".join(movie_titles)
