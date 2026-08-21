from redis.exceptions import RedisError

from src.rate_limit import RateLimiter


class FakeRedis:
    def __init__(self) -> None:
        self.count = 0

    def ping(self) -> bool:
        return True

    def eval(self, *args):
        del args
        self.count += 1
        return [self.count, 60]


class UnavailableRedis:
    def ping(self) -> bool:
        raise RedisError("not available")


def test_redis_backend_enforces_shared_limit(monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr("src.rate_limit.redis.from_url", lambda *args, **kwargs: fake_redis)
    limiter = RateLimiter("redis://example", limit=1, require_redis=True)

    assert limiter.health() == {"status": "ok", "backend": "redis"}
    assert limiter.allow("client") == (True, 60)
    assert limiter.allow("client") == (False, 60)


def test_required_redis_reports_unavailable_and_uses_fallback(monkeypatch):
    monkeypatch.setattr("src.rate_limit.redis.from_url", lambda *args, **kwargs: UnavailableRedis())
    limiter = RateLimiter("redis://example", limit=1, require_redis=True)

    assert limiter.health() == {"status": "unavailable", "backend": "memory"}
    assert limiter.allow("client")[0] is True
    assert limiter.allow("client")[0] is False
