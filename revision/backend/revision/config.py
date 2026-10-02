"""Paths and runtime configuration.

Everything is derived from the location of this file unless overridden by environment variables:
- REVISION_REPO_ROOT    course repo root (default: parent of `revision/`)
- REVISION_CONTENT_DIR  card content (default: `revision/content`)
- REVISION_DATA_DIR     SQLite db, caches, backups (default: `revision/data`, gitignored)
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

_APP_ROOT = Path(__file__).resolve().parents[2]  # .../revision

DEFAULT_PORT = 8433


@dataclass(frozen=True)
class Config:
    repo_root: Path
    content_dir: Path
    data_dir: Path
    frontend_dist: Path

    @property
    def db_path(self) -> Path:
        return self.data_dir / "revision.db"

    @property
    def page_cache_dir(self) -> Path:
        return self.data_dir / "cache" / "pages"

    @property
    def backup_dir(self) -> Path:
        return self.data_dir / "backups"

    def ensure_dirs(self) -> None:
        for d in (self.data_dir, self.page_cache_dir, self.backup_dir):
            d.mkdir(parents=True, exist_ok=True)


def load_config() -> Config:
    app_root = _APP_ROOT
    repo_root = Path(os.environ.get("REVISION_REPO_ROOT", app_root.parent)).resolve()
    content_dir = Path(os.environ.get("REVISION_CONTENT_DIR", app_root / "content")).resolve()
    data_dir = Path(os.environ.get("REVISION_DATA_DIR", app_root / "data")).resolve()
    return Config(
        repo_root=repo_root,
        content_dir=content_dir,
        data_dir=data_dir,
        frontend_dist=app_root / "frontend" / "dist",
    )
