from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.retrieval.semantic import top_k_search
from coverage_intel.vectorstore.memory import InMemoryVectorStore
from coverage_intel.vectorstore.schema import CollectionSpec


def test_top_k_search_returns_score_order_and_trace() -> None:
    store = InMemoryVectorStore(CollectionSpec("chunks", dimensions=2))
    chunks = [
        Chunk(
            chunk_id="a",
            document_id="d",
            text="a",
            token_count=1,
            category=SourceCategory.POLICY,
        ),
        Chunk(
            chunk_id="b",
            document_id="d",
            text="b",
            token_count=1,
            category=SourceCategory.POLICY,
        ),
    ]
    store.upsert(chunks, [[0.6, 0.8], [1.0, 0.0]])

    results = top_k_search(store, [1.0, 0.0], k=2, trace_id="trace-1")

    assert [item.chunk.chunk_id for item in results] == ["b", "a"]
    assert [item.rank for item in results] == [1, 2]
    assert all(item.retrieval_trace_id == "trace-1" for item in results)
