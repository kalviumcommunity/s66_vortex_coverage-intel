from coverage_intel.generation.guardrails import WarningKind, evaluate


def test_guardrails_block_empty_evidence() -> None:
    result = evaluate([])
    assert result.blocked is True
    assert result.warnings[0].kind is WarningKind.INSUFFICIENT_EVIDENCE
