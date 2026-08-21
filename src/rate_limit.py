from __future__ import annotations

import os
from threading import RLock
from time import monotonic
from typing import Any

import redis
from redis.exceptions import RedisError


class RateLimiter:
    """Fixed-window limiter backed by Redis with an in-process fallback."""

    def __init__(
        self,
        redis_url: str | None = None,
        *,
        limit: int | None = None,
        window_seconds: int | None = None,
        require_redis: bool | None = None,
    ) -> None:
        self.limit = limit or int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
        self.window_seconds = window_seconds or int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
        self.require_redis = (
            require_redis
            if require_redis is not None
            else os.getenv("REQUIRE_REDIS", "false").casefold() == "true"
        )
        self._redis_url = redis_url if redis_url is not None else os.getenv("REDIS_URL")
        self._redis: redis.Redis | None = None
        self._fallback: dict[str, tuple[float, int]] = {}
        self._lock = RLock()
        self._connect()

    def _connect(self) -> None:
        if not self._redis_url:
            return
        try:
            client = redis.from_url(
                self._redis_url,
                decode_responses=True,
                socket_connect_timeout=0.5,
                socket_timeout=0.5,
            )
            client.ping()
            self._redis = client
        except RedisError:
            self._redis = None

    @property
    def backend(self) -> str:
        return "redis" if self._redis is not None else "memory"

    def allow(self, key: str) -> tuple[bool, int]:
        if self._redis is not None:
            try:
                redis_key = f"cinebot:rate:{key}"
                count, ttl = self._redis.eval(
                    """
                    local count = redis.call('INCR', KEYS[1])
                    if count == 1 then
                        redis.call('EXPIRE', KEYS[1], ARGV[1])
                    end
                    return {count, redis.call('TTL', KEYS[1])}
                    """,
                    1,
                    redis_key,
                    self.window_seconds,
                )
                return int(count) <= self.limit, max(1, int(ttl))
            except RedisError:
                self._redis = None
        return self._allow_in_memory(key)

    def _allow_in_memory(self, key: str) -> tuple[bool, int]:
        now = monotonic()
        with self._lock:
            if len(self._fallback) > 10_000:
                self._fallback = {
                    existing_key: value
                    for existing_key, value in self._fallback.items()
                    if now - value[0] < self.window_seconds
                }
            started_at, count = self._fallback.get(key, (now, 0))
            if now - started_at >= self.window_seconds:
                started_at, count = now, 0
            count += 1
            self._fallback[key] = (started_at, count)
            retry_after = max(1, int(self.window_seconds - (now - started_at)))
            return count <= self.limit, retry_after

    def health(self) -> dict[str, Any]:
        if self._redis is not None:
            try:
                self._redis.ping()
                return {"status": "ok", "backend": "redis"}
            except RedisError:
                self._redis = None
        status = "unavailable" if self.require_redis else "degraded"
        return {"status": status, "backend": "memory"}
