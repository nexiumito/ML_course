"""Source viewer support: path whitelist, PDF page counts, PDF page -> PNG rendering with a disk cache.

PDFium is not thread-safe, so every pypdfium2 call goes through `_PDFIUM_LOCK`.
"""

from __future__ import annotations

import hashlib
import re
import threading
from functools import lru_cache
from pathlib import Path, PurePosixPath

import pypdfium2 as pdfium

_PDFIUM_LOCK = threading.Lock()

# Repo-relative paths the app may serve (raw file or rendered page).
_ALLOWED = [
    re.compile(r"^lectures/[^/]+(/[^/]+)*\.pdf$"),
    re.compile(r"^exam/[^/]+(/[^/]+)*\.pdf$"),
    re.compile(r"^labs/[^/]+/exercise[^/]*\.pdf$"),
    re.compile(r"^revision/content/img/[^/]+(/[^/]+)*$"),
]

MIN_SCALE, MAX_SCALE = 0.5, 4.0


class SourceError(ValueError):
    pass


def is_allowed_path(rel: str) -> bool:
    pp = PurePosixPath(rel)
    if not rel or pp.is_absolute() or ".." in pp.parts or "\\" in rel or "//" in rel:
        return False
    return any(rx.match(rel) for rx in _ALLOWED)


def resolve_allowed(repo_root: Path, rel: str) -> Path:
    """Resolve a whitelisted repo-relative path to an existing file, or raise SourceError."""
    if not is_allowed_path(rel):
        raise SourceError(f"path not allowed: {rel!r}")
    full = (repo_root / rel).resolve()
    root = repo_root.resolve()
    if root not in full.parents or not full.is_file():
        raise SourceError(f"file not found: {rel!r}")
    return full


@lru_cache(maxsize=256)
def _page_count_cached(path: str, mtime_ns: int) -> int:
    with _PDFIUM_LOCK:
        doc = pdfium.PdfDocument(path)
        try:
            return len(doc)
        finally:
            doc.close()


def pdf_page_count(path: Path) -> int:
    return _page_count_cached(str(path), path.stat().st_mtime_ns)


def render_page(repo_root: Path, cache_dir: Path, rel: str, page: int, scale: float = 2.0) -> Path:
    """Render 1-based `page` of a whitelisted PDF to PNG; cached on disk (invalidated by PDF mtime)."""
    full = resolve_allowed(repo_root, rel)
    if not rel.lower().endswith(".pdf"):
        raise SourceError("not a PDF")
    scale = round(min(max(scale, MIN_SCALE), MAX_SCALE), 2)
    n = pdf_page_count(full)
    if not 1 <= page <= n:
        raise SourceError(f"page {page} out of range 1..{n}")
    mtime = full.stat().st_mtime_ns
    key = hashlib.sha1(f"{rel}|{mtime}".encode()).hexdigest()[:16]
    out = cache_dir / f"{key}-p{page}-s{scale}.png"
    if out.is_file():
        return out
    cache_dir.mkdir(parents=True, exist_ok=True)
    with _PDFIUM_LOCK:
        doc = pdfium.PdfDocument(str(full))
        try:
            pg = doc[page - 1]
            image = pg.render(scale=scale).to_pil()
            pg.close()
        finally:
            doc.close()
    tmp = out.with_suffix(".tmp")
    image.save(tmp, format="PNG", optimize=True)
    tmp.replace(out)
    return out
