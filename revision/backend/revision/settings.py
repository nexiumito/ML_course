"""User settings (stored in the `settings` table, editable in the UI)."""

from __future__ import annotations

import json
import sqlite3
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Settings(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # scheduler
    desired_retention: float = Field(default=0.90, ge=0.80, le=0.97)
    new_per_day: int = Field(default=20, ge=0, le=500)
    max_reviews_per_day: int = Field(default=200, ge=1, le=5000)
    new_order: Literal["course", "random"] = "course"
    interleave_ratio: int = Field(default=4, ge=1, le=20)  # ≈ 1 new item per N reviews
    learn_ahead_minutes: int = Field(default=20, ge=0, le=120)
    # modes
    weak_points_n: int = Field(default=30, ge=1, le=500)
    drill_n: int = Field(default=20, ge=1, le=500)
    # UI
    theme: Literal["system", "light", "dark"] = "system"
    font_size: Literal["sm", "md", "lg", "xl"] = "md"
    swipe: bool = False


def load_settings(conn: sqlite3.Connection) -> Settings:
    stored = {r["key"]: json.loads(r["value_json"]) for r in conn.execute("SELECT key, value_json FROM settings")}
    known = {k: v for k, v in stored.items() if k in Settings.model_fields}
    return Settings.model_validate(known)


def update_settings(conn: sqlite3.Connection, patch: dict) -> Settings:
    """Validate the merged settings, then persist only the patched keys."""
    current = load_settings(conn).model_dump()
    merged = Settings.model_validate({**current, **patch})
    conn.execute("BEGIN IMMEDIATE")
    try:
        for key in patch:
            conn.execute(
                "INSERT INTO settings (key, value_json) VALUES (?, ?)"
                " ON CONFLICT(key) DO UPDATE SET value_json = excluded.value_json",
                (key, json.dumps(getattr(merged, key))),
            )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return merged
