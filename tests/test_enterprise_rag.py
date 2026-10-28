"""Unit tests for the Enterprise RAG pipeline (xAI Grok + Pinecone Inference & Vector DB).

Validates Service-Repository patterns, Dependency Injection, and defensive error handling
using isolated mocks without external network dependencies.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from pinecone import Pinecone

from coverage_intel.rag import (
    Citation,
    ConfigurationError,
    DocumentChunk,
    EmbeddingInferenceError,
    EmbeddingService,
    GrokServiceError,
    LlmService,
    RagOrchestrator,
    RagResponse,
    RagSettings,
    ScoredRecord,
    VectorRepository,
    VectorRepositoryError,
    create_rag_orchestrator,
)


@pytest.fixture
def test_settings() -> RagSettings:
    """Fixture providing valid RAG test settings."""
    return RagSettings(
        PINECONE_API_KEY="pc-test-key-12345",
        PINECONE_INDEX_NAME="insurance-coverage-test",
        PINECONE_EMBED_MODEL="multilingual-e5-large",
        XAI_GROK_API_KEY="xai-test-key-67890",
        XAI_GROK_BASE_URL="https://api.x.ai/v1",
        XAI_GROK_MODEL="grok-2-latest",
        similarity_threshold=0.35,
        top_k=3,
    )


class TestRagSettings:
    """Tests configuration validation and credentials enforcement."""

    def test_settings_validation_passes_when_all_credentials_present(self, test_settings: RagSettings) -> None:
        test_settings.assert_credentials_present()

    def test_settings_validation_fails_when_keys_missing(self) -> None:
        settings = RagSettings(PINECONE_API_KEY="", PINECONE_INDEX_NAME="", XAI_GROK_API_KEY="")
        with pytest.raises(ConfigurationError) as exc_info:
            settings.assert_credentials_present()
        assert "PINECONE_API_KEY" in str(exc_info.value)
        assert "PINECONE_INDEX_NAME" in str(exc_info.value)
        assert "XAI_GROK_API_KEY" in str(exc_info.value)


class TestEmbeddingService:
    """Tests the Pinecone hosted inference embedding service."""

    def test_embed_texts_calls_pinecone_inference(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_item1 = MagicMock()
        mock_item1.values = [0.1, 0.2, 0.3]
        mock_item2 = MagicMock()
        mock_item2.values = [0.4, 0.5, 0.6]
        mock_pc.inference.embed.return_value = [mock_item1, mock_item2]

        service = EmbeddingService(pinecone_client=mock_pc, model="multilingual-e5-large")
        vectors = service.embed_texts(["Section 1 clause", "Section 2 exclusion"], input_type="passage")

        assert len(vectors) == 2
        assert vectors[0] == [0.1, 0.2, 0.3]
        assert vectors[1] == [0.4, 0.5, 0.6]
        mock_pc.inference.embed.assert_called_once_with(
            model="multilingual-e5-large",
            inputs=["Section 1 clause", "Section 2 exclusion"],
            parameters={"input_type": "passage", "truncate": "END"},
        )

    def test_embed_query_uses_query_input_type(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_item = MagicMock()
        mock_item.values = [0.9, 0.8, 0.7]
        mock_pc.inference.embed.return_value = [mock_item]

        service = EmbeddingService(pinecone_client=mock_pc, model="multilingual-e5-large")
        vector = service.embed_query("Is frozen pipe water damage covered?")

        assert vector == [0.9, 0.8, 0.7]
        mock_pc.inference.embed.assert_called_once_with(
            model="multilingual-e5-large",
            inputs=["Is frozen pipe water damage covered?"],
            parameters={"input_type": "query", "truncate": "END"},
        )

    def test_embed_texts_wraps_exceptions(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_pc.inference.embed.side_effect = RuntimeError("Pinecone Gateway Timeout")

        service = EmbeddingService(pinecone_client=mock_pc)
        with pytest.raises(EmbeddingInferenceError) as exc_info:
            service.embed_texts(["Valid passage"])
        assert "Gateway Timeout" in str(exc_info.value)
        assert exc_info.value.retryable is True


class TestVectorRepository:
    """Tests the Pinecone VectorRepository Data Access Object."""

    def test_upsert_chunks_batches_records_correctly(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_index = MagicMock()
        mock_pc.Index.return_value = mock_index

        repo = VectorRepository(pinecone_client=mock_pc, index_name="test-index")
        chunks = [
            DocumentChunk(
                id="c-1",
                text="Peril 12 water damage clause",
                document_id="POL-HO3-2024",
                metadata={"page": 34, "section": "Perils"},
            )
        ]
        vectors = [[0.11, 0.22, 0.33]]

        count = repo.upsert_chunks(chunks=chunks, embeddings=vectors, namespace="claims")

        assert count == 1
        mock_pc.Index.assert_called_once_with("test-index")
        mock_index.upsert.assert_called_once()
        call_kwargs = mock_index.upsert.call_args.kwargs
        assert call_kwargs["namespace"] == "claims"
        assert len(call_kwargs["vectors"]) == 1
        assert call_kwargs["vectors"][0]["id"] == "c-1"
        assert call_kwargs["vectors"][0]["values"] == [0.11, 0.22, 0.33]
        assert call_kwargs["vectors"][0]["metadata"]["document_id"] == "POL-HO3-2024"
        assert call_kwargs["vectors"][0]["metadata"]["text"] == "Peril 12 water damage clause"

    def test_query_similar_maps_pinecone_matches_to_domain_models(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_index = MagicMock()
        mock_pc.Index.return_value = mock_index

        match1 = MagicMock()
        match1.id = "doc#c-1"
        match1.score = 0.885
        match1.metadata = {
            "text": "Accidental discharge covered if heat >= 55F",
            "document_id": "POL-HO3",
            "section": "12. Water",
        }
        mock_index.query.return_value = MagicMock(matches=[match1])

        repo = VectorRepository(pinecone_client=mock_pc, index_name="test-index")
        results = repo.query_similar(vector=[0.1, 0.2, 0.3], top_k=5, filter_dict={"document_id": "POL-HO3"})

        assert len(results) == 1
        record = results[0]
        assert isinstance(record, ScoredRecord)
        assert record.id == "doc#c-1"
        assert record.score == 0.885
        assert record.text == "Accidental discharge covered if heat >= 55F"
        assert record.document_id == "POL-HO3"
        assert record.metadata["section"] == "12. Water"
        assert "text" not in record.metadata

    def test_query_similar_wraps_network_errors(self) -> None:
        mock_pc = MagicMock(spec=Pinecone)
        mock_index = MagicMock()
        mock_index.query.side_effect = ConnectionResetError("Socket aborted")
        mock_pc.Index.return_value = mock_index

        repo = VectorRepository(pinecone_client=mock_pc, index_name="test-index")
        with pytest.raises(VectorRepositoryError) as exc_info:
            repo.query_similar(vector=[0.1, 0.2])
        assert "Socket aborted" in str(exc_info.value)


class TestLlmService:
    """Tests the xAI Grok LLM client integration."""

    def test_generate_grounded_answer_invokes_grok_with_citations(self) -> None:
        mock_openai_client = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Water damage is covered subject to heat maintenance [1]."
        mock_openai_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        service = LlmService(
            api_key="test-key",
            base_url="https://api.x.ai/v1",
            model="grok-2-latest",
            openai_client=mock_openai_client,
        )

        records = [
            ScoredRecord(
                id="chunk-1",
                score=0.92,
                text="Heat must be maintained at or above 55 degrees Fahrenheit.",
                document_id="POL-HO3",
                metadata={"page": 34},
            )
        ]

        answer_text, citations = service.generate_grounded_answer("Is heat required?", records)

        assert "Water damage is covered" in answer_text
        assert len(citations) == 1
        assert citations[0].index == 1
        assert citations[0].chunk_id == "chunk-1"
        assert citations[0].document_id == "POL-HO3"
        assert citations[0].score == 0.92

        # Verify chat completion payload sent to Grok
        mock_openai_client.chat.completions.create.assert_called_once()
        kwargs = mock_openai_client.chat.completions.create.call_args.kwargs
        assert kwargs["model"] == "grok-2-latest"
        assert kwargs["temperature"] == 0.1
        messages = kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "Insurance Coverage Intelligence Assistant" in messages[0]["content"]
        assert "[Evidence Chunk 1]" in messages[1]["content"]

    def test_generate_answer_wraps_grok_errors(self) -> None:
        mock_openai_client = MagicMock()
        mock_openai_client.chat.completions.create.side_effect = RuntimeError("xAI API 500 Internal Error")

        service = LlmService(api_key="key", openai_client=mock_openai_client)
        with pytest.raises(GrokServiceError) as exc_info:
            service.generate_grounded_answer(
                "query",
                [ScoredRecord(id="c1", score=1.0, text="txt", document_id="d1")],
            )
        assert "500 Internal Error" in str(exc_info.value)


class TestRagOrchestrator:
    """Tests the complete end-to-end RAG orchestrator."""

    def test_orchestrator_successful_grounded_flow(self, test_settings: RagSettings) -> None:
        mock_embedding = MagicMock(spec=EmbeddingService)
        mock_embedding.embed_query.return_value = [0.1, 0.2, 0.3]

        mock_repo = MagicMock(spec=VectorRepository)
        mock_repo.query_similar.return_value = [
            ScoredRecord(id="c1", score=0.85, text="Freezing coverage applies above 55F", document_id="POL-HO3")
        ]

        mock_llm = MagicMock(spec=LlmService)
        mock_llm.model_name = "grok-2-latest"
        mock_llm.generate_grounded_answer.return_value = (
            "Yes, freezing coverage applies if heat is kept at or above 55°F [1].",
            [Citation(index=1, document_id="POL-HO3", chunk_id="c1", score=0.85, excerpt="Freezing coverage applies")],
        )

        orchestrator = RagOrchestrator(
            embedding_service=mock_embedding,
            vector_repository=mock_repo,
            llm_service=mock_llm,
            settings=test_settings,
        )

        response = orchestrator.ask("Is frozen pipe damage covered?")

        assert isinstance(response, RagResponse)
        assert response.status == "grounded"
        assert "55°F [1]" in response.answer
        assert response.retrieval_count == 1
        assert len(response.citations) == 1
        assert response.model == "grok-2-latest"
        assert response.latency_ms > 0

        mock_embedding.embed_query.assert_called_once_with("Is frozen pipe damage covered?")
        mock_repo.query_similar.assert_called_once_with(
            vector=[0.1, 0.2, 0.3],
            top_k=3,
            filter_dict=None,
            namespace="",
        )
        mock_llm.generate_grounded_answer.assert_called_once()

    def test_orchestrator_refuses_when_similarity_score_below_threshold(self, test_settings: RagSettings) -> None:
        mock_embedding = MagicMock(spec=EmbeddingService)
        mock_embedding.embed_query.return_value = [0.5, 0.5]

        mock_repo = MagicMock(spec=VectorRepository)
        # Score 0.20 is below similarity_threshold of 0.35
        mock_repo.query_similar.return_value = [
            ScoredRecord(id="c-irrelevant", score=0.20, text="Unrelated text", document_id="DOC-99")
        ]

        mock_llm = MagicMock(spec=LlmService)
        mock_llm.model_name = "grok-2-latest"

        orchestrator = RagOrchestrator(
            embedding_service=mock_embedding,
            vector_repository=mock_repo,
            llm_service=mock_llm,
            settings=test_settings,
        )

        response = orchestrator.ask("Does the policy cover meteor strikes?")

        assert response.status == "insufficient_evidence"
        assert "insufficient documentation" in response.answer
        assert response.retrieval_count == 0
        assert len(response.citations) == 0
        mock_llm.generate_grounded_answer.assert_not_called()  # Grok skipped on refusal

    def test_orchestrator_index_document_chunks(self, test_settings: RagSettings) -> None:
        mock_embedding = MagicMock(spec=EmbeddingService)
        mock_embedding.embed_texts.return_value = [[0.1, 0.2], [0.3, 0.4]]

        mock_repo = MagicMock(spec=VectorRepository)
        mock_repo.index_name = "insurance-coverage-test"
        mock_repo.upsert_chunks.return_value = 2

        mock_llm = MagicMock(spec=LlmService)
        mock_llm.model_name = "grok-2-latest"

        orchestrator = RagOrchestrator(
            embedding_service=mock_embedding,
            vector_repository=mock_repo,
            llm_service=mock_llm,
            settings=test_settings,
        )

        chunks = [
            DocumentChunk(id="c1", text="Clause 1", document_id="P1"),
            DocumentChunk(id="c2", text="Clause 2", document_id="P1"),
        ]

        indexed_count = orchestrator.index_document_chunks(chunks)

        assert indexed_count == 2
        mock_embedding.embed_texts.assert_called_once_with(["Clause 1", "Clause 2"], input_type="passage")
        mock_repo.upsert_chunks.assert_called_once_with(
            chunks=chunks,
            embeddings=[[0.1, 0.2], [0.3, 0.4]],
            namespace="",
            batch_size=100,
        )

    def test_create_rag_orchestrator_dependency_injection(self, test_settings: RagSettings) -> None:
        with patch("coverage_intel.rag.orchestrator.Pinecone") as mock_pinecone_cls:
            mock_pc_instance = MagicMock()
            mock_pinecone_cls.return_value = mock_pc_instance

            orchestrator = create_rag_orchestrator(test_settings)

            # Verify that Pinecone was instantiated once with the configured API key
            mock_pinecone_cls.assert_called_once_with(api_key="pc-test-key-12345")

            # Verify that the EXACT SAME Pinecone connection was injected into both EmbeddingService and VectorRepository
            assert orchestrator.embedding_service._client is mock_pc_instance
            assert orchestrator.vector_repository._client is mock_pc_instance
            assert orchestrator.vector_repository.index_name == "insurance-coverage-test"
            assert orchestrator.embedding_service.model_name == "multilingual-e5-large"
            assert orchestrator.llm_service.model_name == "grok-2-latest"

