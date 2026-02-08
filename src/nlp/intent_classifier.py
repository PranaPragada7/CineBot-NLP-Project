from __future__ import annotations

from typing import Any

from transformers import pipeline


class IntentClassifier:
    def __init__(
        self,
        model_name: str = "facebook/bart-large-mnli",
        candidate_labels: list[str] | None = None,
        confidence_threshold: float = 0.5,
    ) -> None:
        self.labels = candidate_labels or [
            "greet",
            "movie_info",
            "who_directed",
            "recommend",
            "filmography",
            "faq",
            "emotion_check",
            "upcoming_releases",
            "fallback",
        ]
        self.threshold = confidence_threshold
        self._pipe = None
        self._model_name = model_name

    def _ensure_pipeline(self) -> None:
        if self._pipe is None:
            try:
                self._pipe = pipeline("zero-shot-classification", model=self._model_name)
            except Exception:
                self._pipe = None

    def predict(self, text: str, context: dict[str, Any] | None = None) -> tuple[str, float]:
        context = context or {}
        self._ensure_pipeline()

        if self._pipe is None:
            s = text.lower()
            if any(g in s for g in ("hi", "hello", "hey")):
                return "greet", 0.6
            if "who directed" in s:
                return "who_directed", 0.7
            if any(k in s for k in ("recommend", "suggest")):
                return "recommend", 0.7
            if any(k in s for k in ("tell me about", "plot", "info")):
                return "movie_info", 0.7
            return "fallback", 0.5

        prompt = text if not context else f"{context.get('last_intent', '')} [SEP] {text}"
        result = self._pipe(prompt, self.labels)
        label = result["labels"][0]
        score = float(result["scores"][0])
        if score < self.threshold:
            label = "fallback"
        return label, score
