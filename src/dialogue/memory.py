from typing import Any


class Memory:
    def __init__(self):
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, session_id: str) -> dict[str, Any]:
        return self._store.get(session_id, {})

    def update(self, session_id: str, data: dict[str, Any]) -> None:
        ctx = self._store.get(session_id, {})
        ctx.update(data)
        self._store[session_id] = ctx

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
