from coverage_intel.pipeline.audit import AuditTrail


def test_audit_trail_records_only_operational_fields() -> None:
    trail = AuditTrail()
    event = trail.record("q1", "retrieval", "completed")
    assert event.query_id == "q1"
    assert event.stage == "retrieval"
    assert trail.snapshot() == (event,)
