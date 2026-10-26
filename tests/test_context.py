from coverage_intel.generation.context import assemble
from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.retrieval.semantic import RetrievedEvidence


def test_context_preserves_source_ids_and_records_truncation() -> None:
    evidence = [
        RetrievedEvidence(
            chunk=Chunk(
                chunk_id="one",
                document_id="d",
                text="first evidence",
                token_count=2,
                category=SourceCategory.POLICY,
            ),
            semantic_score=1.0,
        ),
        RetrievedEvidence(
            chunk=Chunk(
                chunk_id="two",
                document_id="d",
                text="second evidence",
                token_count=2,
                category=SourceCategory.POLICY,
            ),
            semantic_score=0.9,
        ),
    ]
    context = assemble(evidence, budget=6)
    assert "[one]" in context.text
    assert context.truncated is True
