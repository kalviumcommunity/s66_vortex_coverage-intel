from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.retrieval.hybrid import fuse
from coverage_intel.retrieval.semantic import RetrievedEvidence


def _evidence(chunk_id: str, score: float) -> RetrievedEvidence:
    return RetrievedEvidence(
        chunk=Chunk(
            chunk_id=chunk_id,
            document_id="d",
            text=chunk_id,
            token_count=1,
            category=SourceCategory.POLICY,
        ),
        semantic_score=score,
    )


def test_fuse_combines_unique_chunks_and_reranks() -> None:
    result = fuse(
        [_evidence("a", 1.0)],
        [_evidence("a", 0.0), _evidence("b", 0.0)],
        alpha=0.5,
        k=2,
    )
    assert [item.chunk.chunk_id for item in result] == ["a", "b"]
    assert [item.rank for item in result] == [1, 2]
