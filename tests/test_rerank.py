from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.retrieval.rerank import LexicalReranker
from coverage_intel.retrieval.semantic import RetrievedEvidence


def test_lexical_reranker_prioritizes_query_terms() -> None:
    def item(chunk_id: str, text: str) -> RetrievedEvidence:
        return RetrievedEvidence(
            chunk=Chunk(
                chunk_id=chunk_id,
                document_id="d",
                text=text,
                token_count=1,
                category=SourceCategory.POLICY,
            ),
            semantic_score=0.5,
            hybrid_score=0.5,
        )

    result = LexicalReranker().rerank(
        "water damage", [item("a", "water damage exclusion"), item("b", "fire")], 2
    )
    assert result[0].chunk.chunk_id == "a"
    assert result[0].rerank_score == 2
