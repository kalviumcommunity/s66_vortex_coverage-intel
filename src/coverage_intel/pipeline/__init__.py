"""End-to-end RAG orchestration.

Stage order is fixed:
  ingestion -> embeddings -> vectorstore -> query -> retrieval -> rerank
  -> applicability -> context -> generation -> citations/guardrails -> response

Spec: AGENTS.md §5
"""
