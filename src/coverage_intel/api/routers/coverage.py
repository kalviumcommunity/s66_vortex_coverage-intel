"""Coverage Inquiry router — POST /ask."""

from __future__ import annotations

from fastapi import APIRouter

from ...services.coverage_service import ask_coverage
from ..schemas import AskRequest

router = APIRouter(tags=["Coverage"])


@router.post("/ask")
async def ask(request: AskRequest) -> object:
    """Answer a coverage question through the verified RAG pipeline."""
    return ask_coverage(
        question=request.question,
        scenario=request.scenario,
    )

