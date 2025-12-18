"""Event bus scaffold reflecting messaging responsibilities."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Dict, List, Optional


@dataclass
class Message:
    topic: str
    payload: Dict[str, object]
    retries: int = 0


@dataclass
class DeadLetter:
    message: Message
    reason: str


class EventBus:
    def __init__(self, max_retries: int = 3) -> None:
        self.max_retries = max_retries
        self.topics: Dict[str, List[Callable[[Message], None]]] = {}
        self.queue: Deque[Message] = deque()
        self.dead_letters: List[DeadLetter] = []
        self.metrics: Dict[str, int] = {"published": 0, "consumed": 0, "dead_letter": 0}

    def subscribe(self, topic: str, handler: Callable[[Message], None]) -> None:
        self.topics.setdefault(topic, []).append(handler)

    def publish(self, message: Message) -> None:
        """Publish with ordering preserved via queue."""
        self.queue.append(message)
        self.metrics["published"] += 1

    def process(self) -> None:
        while self.queue:
            message = self.queue.popleft()
            handlers = self.topics.get(message.topic, [])
            if not handlers:
                self._dead_letter(message, "no_handlers")
                continue
            for handler in handlers:
                try:
                    handler(message)
                    self.metrics["consumed"] += 1
                except Exception as exc:  # noqa: BLE001 - surface handler issues
                    message.retries += 1
                    if message.retries > self.max_retries:
                        self._dead_letter(message, f"failed_after_{self.max_retries}_retries: {exc}")
                    else:
                        self.queue.append(message)

    def _dead_letter(self, message: Message, reason: str) -> None:
        self.dead_letters.append(DeadLetter(message=message, reason=reason))
        self.metrics["dead_letter"] += 1

    def latest_backlog(self) -> int:
        return len(self.queue)

    def latest_latency_indicator(self) -> Optional[int]:
        """Return a dummy latency proxy equal to queue depth if backlog exists."""
        if not self.queue:
            return None
        return len(self.queue)
