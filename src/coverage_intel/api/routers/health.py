"""Service health check router — GET /health."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health() -> dict[str, str]:
    """Report process health without making external provider calls."""
    return {"status": "ok", "service": "coverage-intel"}

