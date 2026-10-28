"""Document Service — handles document uploads, parsing, and runtime indexing (FR-16)."""

from __future__ import annotations

import logging
import time
from datetime import date, datetime
from pathlib import Path
from shutil import copyfileobj
from tempfile import NamedTemporaryFile
from typing import BinaryIO

from ..api.schemas import UploadAccepted
from ..config import get_settings
from ..embeddings.encoder import get_embedder
from ..errors import EmbeddingError, ExtractionError, UnsupportedDocumentType
from ..ingestion.chunking import chunk
from ..ingestion.loaders import ExtractedDocument
from ..ingestion.metadata import SourceCategory, SourceDocument, attach_metadata
from ..ingestion.validation import prepare_corpus
from ..vectorstore.index import get_vector_store

logger = logging.getLogger("coverage-intel.document")


def process_document_upload(
    file_stream: BinaryIO,
    filename: str,
    document_id: str | None = None,
    category: str = "policy",
    version: str | None = None,
    effective_from: date | None = None,
    effective_to: date | None = None,
    jurisdiction: str | None = None,
    linked_policy_id: str | None = None,
) -> UploadAccepted:
    """Accept a document upload stream, ingest, embed, and index it at runtime (FR-16).

    Runs the full pipeline: load -> clean -> chunk -> attach provenance metadata -> embed -> upsert.
    """
    suffix = Path(filename or "upload").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt"}:
        raise UnsupportedDocumentType(f"Unsupported document type: {suffix or '<none>'}")

    tmp_path: Path | None = None
    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            copyfileobj(file_stream, tmp)
            tmp_path = Path(tmp.name)

        # Persist a permanent copy in the active corpus directory
        settings = get_settings()
        corpus_path = Path(settings.corpus_dir)
        corpus_path.mkdir(parents=True, exist_ok=True)
        dest_filename = filename or f"{document_id or 'upload'}{suffix}"
        dest_file = corpus_path / dest_filename
        with open(tmp_path, "rb") as sf, open(dest_file, "wb") as df:
            copyfileobj(sf, df)

        docs, _report = prepare_corpus([tmp_path])
        if not docs:
            raise ExtractionError("No usable text extracted from uploaded document")

        extracted: ExtractedDocument = docs[0]

        cat_str = str(category or "policy").lower().strip()
        if cat_str in {"policy_form", "policy"}:
            resolved_category = SourceCategory.POLICY
        elif "endorsement" in cat_str:
            resolved_category = SourceCategory.ENDORSEMENT
        elif "guideline" in cat_str:
            resolved_category = SourceCategory.CLAIM_GUIDELINE
        elif "manual" in cat_str:
            resolved_category = SourceCategory.UNDERWRITING_MANUAL
        else:
            try:
                resolved_category = SourceCategory(cat_str)
            except Exception:
                resolved_category = SourceCategory.POLICY

        resolved_linked_policy = linked_policy_id
        if resolved_category is SourceCategory.ENDORSEMENT and not resolved_linked_policy:
            resolved_linked_policy = "POL-HO3-2024"

        source_doc = SourceDocument(
            document_id=document_id or extracted.document_id,
            title=filename or "uploaded-document",
            category=resolved_category,
            file_type=extracted.file_type,
            version=version,
            effective_from=effective_from,
            effective_to=effective_to,
            jurisdiction=jurisdiction,
            linked_policy_id=resolved_linked_policy,
            checksum="",
            ingested_at=datetime.utcnow(),
        )

        raw_chunks = chunk(
            extracted.blocks,
            document_id=source_doc.document_id,
            category=source_doc.category,
        )
        final_chunks = [attach_metadata(c, source_doc) for c in raw_chunks]

        embedder = get_embedder(settings)
        texts = [c.text for c in final_chunks]

        vectors = None
        last_error = None
        for attempt in range(3):
            try:
                vectors = embedder.embed_documents(texts)
                break
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                wait = 2**attempt
                logger.warning(
                    "Upload embedding attempt %d failed: %s (retrying in %ds)",
                    attempt + 1,
                    exc,
                    wait,
                )
                time.sleep(wait)
        if vectors is None:
            raise EmbeddingError(f"Embedding failed after 3 attempts: {last_error}")

        dimensions = len(vectors[0]) if vectors else 0
        store = get_vector_store(dimensions=dimensions)
        store.upsert(final_chunks, vectors)

        return UploadAccepted(
            document_id=source_doc.document_id,
            message="Document accepted, ingested, and indexed.",
        )
    finally:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
