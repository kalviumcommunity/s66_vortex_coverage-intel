"""UI Static Files & Navigation Router."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


def mount_ui(app: FastAPI) -> None:
    """Mount frontend UI files and root navigation."""
    repo_root = Path(__file__).resolve().parents[4]
    frontend_dir = repo_root / "frontend"
    dist_dir = frontend_dir / "dist"

    serve_dir = dist_dir if dist_dir.exists() else (frontend_dir if frontend_dir.exists() else None)

    if serve_dir and serve_dir.exists():
        app.mount("/ui", StaticFiles(directory=str(serve_dir), html=True), name="ui")

        assets_dir = serve_dir / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        @app.get("/", include_in_schema=False)
        async def root():
            index_file = serve_dir / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            return RedirectResponse(url="/ui/")
