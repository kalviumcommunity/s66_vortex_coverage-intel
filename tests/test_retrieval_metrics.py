from coverage_intel.evaluation.metrics import reciprocal_rank, retrieval_precision_at_k


def test_retrieval_precision_and_reciprocal_rank() -> None:
    retrieved = ["wrong", "expected", "other"]
    assert retrieval_precision_at_k(["expected"], retrieved, 2) == 0.5
    assert reciprocal_rank(["expected"], retrieved) == 0.5
