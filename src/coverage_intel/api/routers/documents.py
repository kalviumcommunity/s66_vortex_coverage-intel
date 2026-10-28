"""Document Management & Ingestion router — /documents endpoints."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, Header, HTTPException, UploadFile

from ...config import get_settings
from ...services.document_service import process_document_upload
from ...services.indexing_service import parse_header_metadata
from ..schemas import UploadAccepted, UploadMetadata
from ..security import verify_access_key

router = APIRouter(tags=["Documents"])


@router.get("/documents")
async def list_documents() -> list[dict]:
    """Return the list of actual documents present in the corpus and indexed."""
    settings = get_settings()
    corpus_dir = Path(settings.corpus_dir)
    results = []

    if corpus_dir.exists():
        for file_path in corpus_dir.iterdir():
            if file_path.is_file() and not file_path.name.startswith("."):
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                meta = parse_header_metadata(content)
                title = file_path.stem
                for line in content.splitlines()[:5]:
                    if "FORM" in line.upper() or "POLICY" in line.upper() or "GUIDELINE" in line.upper():
                        title = line.strip()
                        break

                results.append({
                    "id": meta.get("policy_id") or file_path.stem,
                    "filename": file_path.name,
                    "title": title,
                    "form": meta.get("policy_id") or file_path.stem,
                    "jurisdiction": meta.get("jurisdiction") or "US-ALL",
                    "version": meta.get("version") or "2024.1",
                    "effective_from": meta.get("effective_from") or "2024-01-01",
                    "effective_to": meta.get("effective_to") or "2025-12-31",
                    "category": "policy" if "POL" in file_path.name else ("endorsement" if "END" in file_path.name else "guideline"),
                    "size_bytes": file_path.stat().st_size,
                    "status": "active",
                    "status_label": "Indexed & Active",
                })

    return results


@router.get("/documents/{document_id}")
async def get_document(document_id: str) -> dict:
    """Retrieve full document text and clause content."""
    settings = get_settings()
    corpus_dir = Path(settings.corpus_dir)

    target_file = None
    if corpus_dir.exists():
        for file_path in corpus_dir.iterdir():
            if file_path.stem == document_id or file_path.name == document_id:
                target_file = file_path
                break
        if not target_file:
            for file_path in corpus_dir.iterdir():
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                meta = parse_header_metadata(content)
                if meta.get("policy_id") == document_id:
                    target_file = file_path
                    break

    if not target_file:
        raise HTTPException(status_code=404, detail=f"Document {document_id} not found in corpus")

    text = target_file.read_text(encoding="utf-8", errors="ignore")
    header = parse_header_metadata(text)
    return {
        "id": header.get("policy_id") or target_file.stem,
        "filename": target_file.name,
        "text": text,
        "metadata": header,
        "size_bytes": target_file.stat().st_size,
    }


@router.post("/documents", response_model=UploadAccepted, status_code=202)
async def register_document(metadata: UploadMetadata) -> UploadAccepted:
    """Accept validated source metadata for asynchronous ingestion."""
    document_id = metadata.document_id or str(uuid4())
    return UploadAccepted(
        document_id=document_id,
        message="Document accepted for ingestion.",
    )


@router.post("/documents/upload", response_model=UploadAccepted, status_code=202)
async def upload_document(
    file: UploadFile = File(...),
    x_upload_access_key: str | None = Header(default=None, alias="X-Upload-Access-Key"),
    document_id: str | None = Form(None),
    category: str = Form("policy"),
    version: str | None = Form(None),
    effective_from: date | None = Form(None),
    effective_to: date | None = Form(None),
    jurisdiction: str | None = Form(None),
    linked_policy_id: str | None = Form(None),
) -> UploadAccepted:
    """Accept a document upload, ingest, embed, and index it at runtime (FR-16)."""
    verify_access_key(x_upload_access_key)

    return process_document_upload(
        file_stream=file.file,
        filename=file.filename or "upload",
        document_id=document_id,
        category=category,
        version=version,
        effective_from=effective_from,
        effective_to=effective_to,
        jurisdiction=jurisdiction,
        linked_policy_id=linked_policy_id,
    )
