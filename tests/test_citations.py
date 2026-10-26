from coverage_intel.generation.citations import build_citations
from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.retrieval.semantic import RetrievedEvidence


def test_citations_copy_evidence_text_verbatim() -> None:
    evidence = [
        RetrievedEvidence(
            chunk=Chunk(
                chunk_id="c1",
                document_id="doc",
                text="Exact policy wording.",
                token_count=3,
                category=SourceCategory.POLICY,
            ),
            semantic_score=1.0,
        )
    ]
    citations = build_citations(evidence, {"statements": [{"citation_indices": [0]}]})
    assert citations[0].excerpt == "Exact policy wording."
    assert citations[0].chunk_id == "c1"
