"""FastAPI app factory: loads content (fatal on error), migrates + syncs the DB, serves API, files and SPA."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from revision import __version__
from revision.api import router
from revision.config import Config, load_config
from revision.content import load_content
from revision.db import open_db, sync_items
from revision.sources import SourceError, resolve_allowed


def utcnow() -> datetime:
    return datetime.now(UTC)


def create_app(config: Config | None = None, clock: Callable[[], datetime] = utcnow) -> FastAPI:
    cfg = config or load_config()
    cfg.ensure_dirs()
    content = load_content(cfg.content_dir, cfg.repo_root)  # raises ContentError: refuse to start
    conn = open_db(cfg.db_path)
    try:
        sync_items(conn, content, clock())
    finally:
        conn.close()

    app = FastAPI(title="CS-433 Review", version=__version__, docs_url="/api/docs", openapi_url="/api/openapi.json")
    app.state.cfg = cfg
    app.state.content = content
    app.state.clock = clock
    app.include_router(router)

    @app.get("/files/{path:path}", include_in_schema=False)
    def raw_file(path: str):
        try:
            full = resolve_allowed(cfg.repo_root, path)
        except SourceError as e:
            raise HTTPException(404, str(e)) from e
        return FileResponse(full)

    @app.get("/content-img/{path:path}", include_in_schema=False)
    def content_img(path: str):
        pp = PurePosixPath(path)
        full = (cfg.content_dir / path).resolve()
        if pp.is_absolute() or ".." in pp.parts or not path.startswith("img/") or not full.is_file():
            raise HTTPException(404, "image not found")
        return FileResponse(full)

    _mount_spa(app, cfg.frontend_dist)
    return app


def _mount_spa(app: FastAPI, dist: Path) -> None:
    """Serve the built frontend: real files when they exist, index.html for client-side routes."""
    index = dist / "index.html"

    @app.get("/{path:path}", include_in_schema=False)
    def spa(path: str):
        if path.startswith("api/"):
            raise HTTPException(404, "unknown API route")
        if not index.is_file():
            raise HTTPException(503, "frontend not built: run `npm run build` in revision/frontend")
        if path:
            pp = PurePosixPath(path)
            candidate = (dist / path).resolve()
            if ".." not in pp.parts and dist.resolve() in candidate.parents and candidate.is_file():
                headers = {"Cache-Control": "public, max-age=31536000, immutable"} if path.startswith("assets/") else {}
                return FileResponse(candidate, headers=headers)
        return FileResponse(index, headers={"Cache-Control": "no-cache"})
