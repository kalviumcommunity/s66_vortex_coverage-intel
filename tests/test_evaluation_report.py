from coverage_intel.evaluation.metrics import build_retrieval_report


def test_build_retrieval_report_aggregates_cases() -> None:
    report = build_retrieval_report([(["a"], ["a", "b"]), (["z"], ["x", "z"])], k=2)
    assert report.recall_at_k == 1.0
    assert report.precision_at_k == 0.5
    assert report.mean_reciprocal_rank == 0.75
