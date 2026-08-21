from __future__ import annotations

from typing import Any


class ResponseGenerator:
    @staticmethod
    def welcome() -> str:
        return (
            "Hi! I can help you discover movies, check directors, review what is "
            "trending, and find similar titles."
        )

    @staticmethod
    def help_text() -> str:
        return (
            "Ask about a movie, request titles similar to one you enjoyed, check who "
            "directed a film, or ask what is trending."
        )

    @staticmethod
    def missing_title(action: str) -> str:
        return f"Which movie should I use to {action}? Include the title in your message."

    @staticmethod
    def movie_info(movie: dict[str, Any]) -> str:
        year = str(movie.get("release_date") or "")[:4] or "release year unavailable"
        rating = movie.get("vote_average") or 0
        genres = ", ".join(movie.get("genres") or [])
        details = [f"**{movie['title']}** ({year})"]
        if genres:
            details.append(genres)
        if rating:
            details.append(f"TMDB rating: {rating:.1f}/10")
        header = " · ".join(details)
        return f"{header}\n\n{movie.get('overview') or 'No overview is available.'}"

    @staticmethod
    def director(movie: dict[str, Any]) -> str:
        director = movie.get("director")
        if not director:
            return f"I found **{movie['title']}**, but its director was not available."
        return f"**{movie['title']}** was directed by **{director}**."

    @staticmethod
    def movie_list(heading: str, movies: list[dict[str, Any]]) -> str:
        if not movies:
            return "I could not find matching movies right now."
        rows = []
        for movie in movies:
            year = str(movie.get("release_date") or "")[:4]
            suffix = f" ({year})" if year else ""
            score = movie.get("match_score")
            match = f" · {score:.0%} match" if isinstance(score, float) else ""
            rows.append(f"- **{movie['title']}**{suffix}{match}")
        return heading + "\n\n" + "\n".join(rows)

    @staticmethod
    def not_found(title: str) -> str:
        return f"I could not find a confident match for **{title}**. Try the full movie title."

    @staticmethod
    def fallback() -> str:
        return (
            "I did not recognize that as a movie request. Ask for movie details, a "
            "director, recommendations, upcoming releases, or trending titles."
        )
