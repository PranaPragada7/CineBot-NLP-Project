from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass, field


@dataclass
class MetricsTracker:
    max_history: int = 1000
    total_requests: int = 0
    latency_ms: deque[float] = field(default_factory=lambda: deque(maxlen=1000))
    intent_counts: Counter = field(default_factory=Counter)
    faq_hits: int = 0
    vector_hits: int = 0
    tmdb_hits: int = 0

    def record(
        self,
        *,
        intent: str,
        latency: float,
        used_faq: bool = False,
        used_vector: bool = False,
        used_tmdb: bool = False,
    ) -> None:
        self.total_requests += 1
        self.latency_ms.append(latency * 1000.0)
        self.intent_counts[intent] += 1
        if used_faq:
            self.faq_hits += 1
        if used_vector:
            self.vector_hits += 1
        if used_tmdb:
            self.tmdb_hits += 1

    def summary(self) -> dict:
        avg_latency = sum(self.latency_ms) / len(self.latency_ms) if self.latency_ms else 0.0
        return {
            "total": self.total_requests,
            "avg_latency_ms": round(avg_latency, 2),
            "intents": dict(self.intent_counts),
            "faq_hits": self.faq_hits,
            "vector_hits": self.vector_hits,
            "tmdb_hits": self.tmdb_hits,
        }
