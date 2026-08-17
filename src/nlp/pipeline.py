from __future__ import annotations

import re
from typing import Any


class NLPPipeline:
    """Fast, deterministic intent and entity extraction for movie questions."""

    POSITIVE_WORDS = {
        "amazing",
        "best",
        "enjoyed",
        "excellent",
        "great",
        "love",
        "loved",
        "liked",
    }
    NEGATIVE_WORDS = {"awful", "bad", "boring", "dislike", "hate", "poor", "worst"}

    def __init__(self, known_titles: list[str] | None = None) -> None:
        self.known_titles = sorted(known_titles or [], key=len, reverse=True)

    @staticmethod
    def _intent(text: str) -> tuple[str, float]:
        lowered = text.casefold()
        if re.search(r"\b(hi|hello|hey)\b", lowered):
            return "greet", 0.98
        if "who directed" in lowered or "director of" in lowered:
            return "who_directed", 0.99
        if any(term in lowered for term in ("recommend", "suggest", "similar to", "movies like")):
            return "recommend", 0.96
        if any(term in lowered for term in ("upcoming", "coming soon", "new releases")):
            return "upcoming_releases", 0.96
        if any(term in lowered for term in ("trending", "popular right now", "what is popular")):
            return "trending", 0.96
        if any(
            term in lowered for term in ("tell me about", "movie info", "details about", "plot of")
        ):
            return "movie_info", 0.92
        if any(term in lowered for term in ("what can you do", "help", "commands")):
            return "help", 0.95
        return "fallback", 0.35

    def _movie_title(self, text: str) -> str | None:
        lowered = text.casefold()
        for title in self.known_titles:
            if title.casefold() in lowered:
                return title

        quoted = re.search(r"[\"']([^\"']{2,80})[\"']", text)
        if quoted:
            return quoted.group(1).strip()

        patterns = (
            r"(?:who\s+directed|director\s+of)\s+(.+)",
            r"(?:similar\s+to|movies?\s+like)\s+(.+)",
            r"(?:tell\s+me\s+about|details\s+about|plot\s+of|movie\s+info\s+for)\s+(.+)",
        )
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                candidate = match.group(1).strip(' .?!,"')
                if candidate and candidate.casefold() not in {
                    "a movie",
                    "it",
                    "movies",
                    "something",
                    "that movie",
                    "that one",
                }:
                    return candidate
        return None

    def _sentiment(self, text: str) -> dict[str, Any]:
        tokens = set(re.findall(r"[a-z']+", text.casefold()))
        positive = len(tokens.intersection(self.POSITIVE_WORDS))
        negative = len(tokens.intersection(self.NEGATIVE_WORDS))
        if positive > negative:
            label = "positive"
        elif negative > positive:
            label = "negative"
        else:
            label = "neutral"
        return {"label": label, "score": round((positive - negative) / max(len(tokens), 1), 3)}

    def run(self, text: str, ctx: dict[str, Any] | None = None) -> dict[str, Any]:
        del ctx
        intent, confidence = self._intent(text)
        return {
            "intent": intent,
            "intent_confidence": confidence,
            "movie_title": self._movie_title(text),
            "sentiment": self._sentiment(text),
        }
