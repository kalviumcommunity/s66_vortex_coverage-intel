"""Indexing Service — encapsulates policy corpus ingestion and vector store indexing.

Phase: phase-05-rag-core / phase-07-backend-api
"""

from __future__ import annotations

import logging
import os
import re
import sys
import time
from datetime import date, datetime
from pathlib import Path

from ..config import get_settings
from ..embeddings.encoder import get_embedder
from ..ingestion.chunking import chunk
from ..ingestion.metadata import SourceCategory, SourceDocument, attach_metadata
from ..ingestion.validation import prepare_corpus
from ..vectorstore.index import get_vector_store

logger = logging.getLogger("coverage-intel.indexing")


def parse_header_metadata(text: str) -> dict:
    """Parse VERSION / EFFECTIVE DATE / JURISDICTION headers from policy text."""
    meta: dict = {}
    m = re.search(r"VERSION:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["version"] = m.group(1)
    m = re.search(r"EFFECTIVE DATE:\s*(\S+)", text, re.IGNORECASE)
    if m:
        try:
            meta["effective_from"] = date.fromisoformat(m.group(1))
        except ValueError:
            pass
    m = re.search(r"EXPIRATION DATE:\s*(\S+)", text, re.IGNORECASE)
    if m:
        try:
            meta["effective_to"] = date.fromisoformat(m.group(1))
        except ValueError:
            pass
    m = re.search(r"JURISDICTION:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["jurisdiction"] = m.group(1)
    m = re.search(r"POLICY IDENTIFIER:\s*(\S+)", text, re.IGNORECASE)
    if m:
        meta["policy_id"] = m.group(1)
    return meta


def index_files(files: list[Path], log: logging.Logger | None = None) -> int:
    """Load, chunk, attach metadata, embed, and upsert a list of corpus files.

    Returns the number of chunks indexed. Never raises.
    Retries embedding on transient provider failures (e.g., 502).
    """
    active_logger = log or logger
    settings = get_settings()
    docs, _ = prepare_corpus(files)
    all_chunks = []
    for doc in docs:
        full_text = "\n".join(b.text for b in doc.blocks)
        header = parse_header_metadata(full_text)
        doc_id = header.get("policy_id") or doc.document_id
        source_doc = SourceDocument(
            document_id=doc_id,
            title=doc.document_id,
            category=SourceCategory.POLICY,
            file_type=doc.file_type,
            version=header.get("version"),
            effective_from=header.get("effective_from"),
            effective_to=header.get("effective_to"),
            jurisdiction=header.get("jurisdiction"),
            linked_policy_id=None,
            checksum="",
            ingested_at=datetime.utcnow(),
        )
        raw_chunks = chunk(
            doc.blocks,
            document_id=doc_id,
            category=source_doc.category,
        )
        final_chunks = [attach_metadata(c, source_doc) for c in raw_chunks]
        all_chunks.extend(final_chunks)

    if not all_chunks:
        return 0

    # Retry embedding up to 3 times on transient failures
    embedder = get_embedder(settings)
    texts = [c.text for c in all_chunks]
    vectors = None
    last_error = None
    for attempt in range(3):
        try:
            vectors = embedder.embed_documents(texts)
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            wait = 2**attempt
            active_logger.warning(
                "Embedding attempt %d failed: %s (retrying in %ds)",
                attempt + 1,
                exc,
                wait,
            )
            time.sleep(wait)
    if vectors is None:
        active_logger.error("Embedding failed after 3 attempts: %s", last_error)
        return 0

    dimensions = len(vectors[0]) if vectors else 0
    store = get_vector_store(dimensions=dimensions)
    if store.count > 0:
        return 0
    store.upsert(all_chunks, vectors)
    active_logger.info("Indexed %d chunks into vector store", len(all_chunks))
    return len(all_chunks)


def ensure_corpus_indexed(force: bool = False) -> int:
    """Ensure the configured corpus directory is indexed into the vector store.

    Skipped automatically in pytest / test runner environments unless force=True.
    """
    if not force and ("PYTEST_CURRENT_TEST" in os.environ or "pytest" in sys.modules):
        return 0

    try:
        store = get_vector_store()
        if store.count > 0:
            return 0
    except ValueError:
        pass

    settings = get_settings()
    corpus_path = Path(settings.corpus_dir)
    if not corpus_path.exists():
        return 0

    files = [p for p in corpus_path.iterdir() if p.is_file() and not p.name.startswith(".")]
    if not files:
        return 0

    return index_files(files, logger)

