from coverage_intel.generation.answer import AnswerStatus
from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.pipeline.rag import answer_question
from coverage_intel.retrieval.semantic import RetrievedEvidence


def test_pipeline_connects_retrieval_context_and_generation() -> None:
    evidence = RetrievedEvidence(
        chunk=Chunk(
            chunk_id="c1",
            document_id="d",
            text="Coverage wording",
            token_count=2,
            category=SourceCategory.POLICY,
        ),
        semantic_score=1.0,
    )

    answer = answer_question(
        "What is covered?",
        retriever=lambda _question, _scenario: [evidence],
        query_id="q-1",
    )

    assert answer.query_id == "q-1"
    assert answer.status in {AnswerStatus.WEAK_EVIDENCE, AnswerStatus.GROUNDED}
    assert answer.evidence[0].chunk.chunk_id == "c1"
