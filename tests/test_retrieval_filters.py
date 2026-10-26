from coverage_intel.ingestion.metadata import Chunk, SourceCategory
from coverage_intel.vectorstore.memory import InMemoryVectorStore
from coverage_intel.vectorstore.schema import CollectionSpec


def test_metadata_filters_apply_before_vector_scoring() -> None:
    store = InMemoryVectorStore(CollectionSpec("chunks", dimensions=2))
    chunks = [
        Chunk(
            chunk_id="policy",
            document_id="d",
            text="p",
            token_count=1,
            category=SourceCategory.POLICY,
        ),
        Chunk(
            chunk_id="guide",
            document_id="d",
            text="g",
            token_count=1,
            category=SourceCategory.CLAIM_GUIDELINE,
        ),
    ]
    store.upsert(chunks, [[0.0, 1.0], [1.0, 0.0]])
    results = store.search([1.0, 0.0], 5, {"category": SourceCategory.POLICY})
    assert [item.chunk.chunk_id for item in results] == ["policy"]
