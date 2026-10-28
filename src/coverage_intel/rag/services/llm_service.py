"""LLM Service — xAI Grok client using the official OpenAI SDK architecture.

Points to the xAI API base URL (https://api.x.ai/v1 or https://x.ai) and enforces
strict grounding constraints and low-temperature parameters.
"""

from __future__ import annotations

import logging
from typing import Any

from openai import OpenAI

from ..exceptions import GrokServiceError
from ..models import Citation, ScoredRecord

logger = logging.getLogger("coverage-intel.rag.llm")

GROK_SYSTEM_PROMPT = """You are an expert Insurance Coverage Intelligence Assistant.
Your task is to provide strict, factual, decision-support answers based ONLY on the provided policy evidence excerpts.

CRITICAL OPERATIONAL RULES:
1. Strict Grounding: Every statement you make MUST be directly supported by the provided excerpts.
2. Citation Requirement: Whenever you state a policy condition, peril rule, exclusion, or threshold, immediately reference the evidence chunk index in brackets, e.g., [1] or [2].
3. No Hallucinations: If the provided excerpts do NOT contain sufficient information to answer the question, explicitly state: "Based on the retrieved policy evidence, there is insufficient documentation to confirm coverage." Do NOT assume or invent coverage terms.
4. Neutral Decision Support: You do not approve or deny claims or calculate payouts. You verify and cite policy facts for adjusters.
"""


class LlmService:
    """Service handling natural language generation and grounded synthesis via xAI Grok."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.x.ai/v1",
        model: str = "grok-2-latest",
        temperature: float = 0.1,
        timeout: float = 30.0,
        openai_client: OpenAI | None = None,
    ) -> None:
        """Initialize the xAI Grok LLM Service.

        Args:
            api_key: xAI Grok API Key.
            base_url: Base URL for xAI endpoint (defaults to https://api.x.ai/v1).
            model: Target Grok model identifier (e.g. grok-2-latest).
            temperature: Sampling temperature (kept low for factual stability).
            timeout: Network request timeout in seconds.
            openai_client: Optional injected OpenAI client (for unit testing / mocking).
        """
        self._model = model
        self._temperature = temperature
        self._timeout = timeout

        clean_base_url = base_url.rstrip("/")
        # Normalize base URL if https://x.ai is passed without /v1
        if clean_base_url == "https://x.ai":
            clean_base_url = "https://api.x.ai/v1"

        self._client = openai_client or OpenAI(
            api_key=api_key,
            base_url=clean_base_url,
            timeout=timeout,
        )

    @property
    def model_name(self) -> str:
        """Return the active Grok model identifier."""
        return self._model

    def generate_grounded_answer(
        self,
        query: str,
        context_chunks: list[ScoredRecord],
    ) -> tuple[str, list[Citation]]:
        """Synthesize a grounded answer from retrieved policy chunks using xAI Grok.

        Args:
            query: The user's coverage inquiry.
            context_chunks: Scored policy passages retrieved from Pinecone.

        Returns:
            A tuple of (generated_answer_text, list_of_citations).

        Raises:
            GrokServiceError: If the xAI API encounters network or generation errors.
        """
        if not query or not query.strip():
            raise GrokServiceError("Query cannot be empty for answer generation.", retryable=False)

        # Build numbered citations and compilation block
        citations: list[Citation] = []
        evidence_blocks: list[str] = []

        for idx, record in enumerate(context_chunks, start=1):
            citation = Citation(
                index=idx,
                document_id=record.document_id or str(record.metadata.get("document_id", "Unknown")),
                chunk_id=record.id,
                score=round(record.score, 4),
                excerpt=record.text,
            )
            citations.append(citation)

            meta_details = []
            if "section" in record.metadata:
                meta_details.append(f"Section: {record.metadata['section']}")
            if "page" in record.metadata:
                meta_details.append(f"Page: {record.metadata['page']}")
            meta_str = f" ({', '.join(meta_details)})" if meta_details else ""

            evidence_blocks.append(
                f"[Evidence Chunk {idx}] Document: {citation.document_id}{meta_str}\n"
                f"Content: {record.text}\n"
            )

        compiled_context = "\n---\n".join(evidence_blocks)
        user_prompt = (
            f"QUESTION:\n{query.strip()}\n\n"
            f"RELEVANT POLICY EVIDENCE EXCERPTS:\n{compiled_context}\n\n"
            "INSTRUCTIONS:\n"
            "Synthesize a clear, grounded answer addressing the question above. "
            "Cite every assertion with the corresponding [Evidence Chunk index] (e.g. [1]). "
            "If evidence is inconclusive or missing, state that clearly."
        )

        try:
            logger.info(
                "Dispatching completion to xAI Grok (%s) with %d context chunks (temp=%.2f)",
                self._model,
                len(context_chunks),
                self._temperature,
            )
            response: Any = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": GROK_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self._temperature,
            )

            if not response.choices or not response.choices[0].message.content:
                raise GrokServiceError("xAI Grok returned an empty completion response.", retryable=True)

            answer_text = response.choices[0].message.content.strip()
            return answer_text, citations

        except GrokServiceError:
            raise
        except Exception as exc:
            logger.error("xAI Grok API call failed: %s", exc, exc_info=True)
            raise GrokServiceError(f"Failed to generate answer via xAI Grok ({self._model}): {exc}") from exc

