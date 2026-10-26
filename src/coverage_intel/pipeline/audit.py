"""Privacy-safe audit events for pipeline observability."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True, slots=True)
class AuditEvent:
    """An operational event containing identifiers, never claim text."""

    query_id: str
    stage: str
    outcome: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class AuditTrail:
    """In-memory audit sink suitable for request-scoped tests."""

    def __init__(self) -> None:
        self._events: list[AuditEvent] = []

    def record(self, query_id: str, stage: str, outcome: str) -> AuditEvent:
        event = AuditEvent(query_id=query_id, stage=stage, outcome=outcome)
        self._events.append(event)
        return event

    def snapshot(self) -> tuple[AuditEvent, ...]:
        """Return an immutable view of recorded events."""
        return tuple(self._events)
