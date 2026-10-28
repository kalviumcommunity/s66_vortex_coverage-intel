"""RAG Pipeline Orchestrator — End-to-end coordinator managing the RAG lifecycle.

Coordinates: Query -> Pinecone Inference Embedding -> Pinecone Vector Query ->
Context Compilation -> xAI Grok Grounded Generation.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from pinecone import Pinecone

from .config import RagSettings, get_rag_settings
from .models import Citation, DocumentChunk, RagResponse, ScoredRecord
from .repositories.vector_repository import VectorRepository
from .services.embedding_service import EmbeddingService
from .services.llm_service import LlmService

logger = logging.getLogger("coverage-intel.rag.orchestrator")


class RagOrchestrator:
    """Main pipeline coordinator managing retrieval, grounding, and synthesis."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        vector_repository: VectorRepository,
        llm_service: LlmService,
        settings: RagSettings | None = None,
    ) -> None:
        """Initialize the orchestrator with injected service and repository dependencies.

        Args:
            embedding_service: Service generating embeddings via Pinecone inference.
            vector_repository: Repository managing vector index queries and upserts.
            llm_service: Service communicating with xAI Grok.
            settings: Runtime configuration settings.
        """
        self.embedding_service = embedding_service
        self.vector_repository = vector_repository
        self.llm_service = llm_service
        self.settings = settings or get_rag_settings()

    def ask(
        self,
        query: str,
        filters: dict[str, Any] | None = None,
        top_k: int | None = None,
        namespace: str = "",
    ) -> RagResponse:
        """Execute the complete enterprise RAG pipeline for a user question.

        1. Query -> Generate asymmetric query embedding using Pinecone inference.
        2. Vector -> Query Pinecone for the top_k most similar policy passages.
        3. Filter -> Prune records falling below the relevance similarity threshold.
        4. Context -> If evidence is insufficient, return structured refusal.
        5. Grok -> Invoke xAI Grok to synthesize a grounded, cited determination.

        Args:
            query: The user's coverage inquiry.
            filters: Optional metadata filtering criteria (Pinecone syntax).
            top_k: Optional override for candidate count.
            namespace: Optional Pinecone index namespace.

        Returns:
            A fully populated RagResponse DTO.
        """
        start_time = time.perf_counter()
        target_k = top_k or self.settings.top_k

        logger.info("Executing RAG inquiry: '%s' (top_k=%d)", query, target_k)

        # Step 1: Generate query embedding via Pinecone Inference (multilingual-e5-large)
        query_vector = self.embedding_service.embed_query(query)

        # Step 2: Retrieve candidate records from Pinecone Vector DB
        candidates: list[ScoredRecord] = self.vector_repository.query_similar(
            vector=query_vector,
            top_k=target_k,
            filter_dict=filters,
            namespace=namespace,
        )

        # Step 3: Enforce relevance similarity threshold
        relevant_records = [
            r for r in candidates if r.score >= self.settings.similarity_threshold
        ]

        logger.info(
            "Retrieved %d candidates, %d above similarity threshold (%.2f)",
            len(candidates),
            len(relevant_records),
            self.settings.similarity_threshold,
        )

        # Step 4: Handle insufficient evidence refusal defensively
        if not relevant_records:
            total_latency = (time.perf_counter() - start_time) * 1000.0
            return RagResponse(
                query=query,
                answer=(
                    "Based on the retrieved policy evidence, there is insufficient documentation "
                    "or no matching policy provisions found to confirm coverage."
                ),
                status="insufficient_evidence",
                citations=[],
                model=self.llm_service.model_name,
                retrieval_count=0,
                latency_ms=round(total_latency, 2),
            )

        # Step 5: Synthesize grounded response using xAI Grok
        answer_text, citations = self.llm_service.generate_grounded_answer(
            query=query,
            context_chunks=relevant_records,
        )

        total_latency = (time.perf_counter() - start_time) * 1000.0

        return RagResponse(
            query=query,
            answer=answer_text,
            status="grounded",
            citations=citations,
            model=self.llm_service.model_name,
            retrieval_count=len(relevant_records),
            latency_ms=round(total_latency, 2),
        )

    def index_document_chunks(
        self,
        chunks: list[DocumentChunk],
        namespace: str = "",
        batch_size: int = 100,
    ) -> int:
        """Batch ingest document passages: embed via Pinecone inference and upsert to index.

        Args:
            chunks: List of DocumentChunk domain models.
            namespace: Optional Pinecone namespace.
            batch_size: Network batch size.

        Returns:
            Number of indexed vectors.
        """
        if not chunks:
            return 0

        logger.info("Starting ingestion of %d chunks into index '%s'", len(chunks), self.vector_repository.index_name)

        # Generate embeddings via Pinecone inference (passage input_type)
        texts = [c.text for c in chunks]
        embeddings = self.embedding_service.embed_texts(texts, input_type="passage")

        # Upsert into Pinecone
        count = self.vector_repository.upsert_chunks(
            chunks=chunks,
            embeddings=embeddings,
            namespace=namespace,
            batch_size=batch_size,
        )

        logger.info("Successfully completed ingestion of %d vectors", count)
        return count


def create_rag_orchestrator(settings: RagSettings | None = None) -> RagOrchestrator:
    """Factory creating a fully wired RagOrchestrator using Dependency Injection.

    Shares a single instantiated Pinecone client connection between the
    EmbeddingService and the VectorRepository.
    """
    cfg = settings or get_rag_settings()
    cfg.assert_credentials_present()

    logger.info("Initializing Pinecone client (Dependency Injection)...")
    pinecone_client = Pinecone(api_key=cfg.pinecone_api_key)

    # Inject shared Pinecone client into EmbeddingService
    embedding_service = EmbeddingService(
        pinecone_client=pinecone_client,
        model=cfg.pinecone_embed_model,
    )

    # Inject shared Pinecone client into VectorRepository
    vector_repository = VectorRepository(
        pinecone_client=pinecone_client,
        index_name=cfg.pinecone_index_name,
    )

    # Initialize LlmService with xAI Grok settings
    llm_service = LlmService(
        api_key=cfg.xai_grok_api_key,
        base_url=cfg.xai_grok_base_url,
        model=cfg.xai_grok_model,
        temperature=cfg.generation_temperature,
        timeout=cfg.network_timeout_seconds,
    )

    return RagOrchestrator(
        embedding_service=embedding_service,
        vector_repository=vector_repository,
        llm_service=llm_service,
        settings=cfg,
    )

