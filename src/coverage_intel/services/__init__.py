"""Services layer — business logic decoupled from HTTP frameworks."""

from .coverage_service import ask_coverage
from .document_service import process_document_upload
from .indexing_service import ensure_corpus_indexed, index_files, parse_header_metadata

__all__ = [
    "ask_coverage",
    "ensure_corpus_indexed",
    "index_files",
    "parse_header_metadata",
    "process_document_upload",
]

