from coverage_intel.logging_config import redact


def test_redaction_removes_sensitive_fields() -> None:
    event = redact(None, "event", {"event": "query", "question": "secret", "query_id": "q1"})
    assert event == {"event": "query", "query_id": "q1"}
