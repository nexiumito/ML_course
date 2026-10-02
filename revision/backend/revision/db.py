"""SQLite storage (SPEC §6): connection, migrations, content -> items sync, small query helpers.

All datetimes are stored as fixed-width UTC strings (`YYYY-MM-DDTHH:MM:SS.ffffffZ`) so that
lexicographic order == chronological order in SQL comparisons.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from revision.content import Content

_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


def iso(d: datetime) -> str:
    if d.tzinfo is None:
        raise ValueError("naive datetime")
    return d.astimezone(UTC).strftime(_FMT)


def parse_iso(s: str | None) -> datetime | None:
    if s is None:
        return None
    return datetime.strptime(s, _FMT).replace(tzinfo=UTC)


REPORT_REASONS = ("wrong", "unclear", "typo", "too-long", "duplicate", "bad-source", "other")

MIGRATIONS: list[str] = [
    # v1
    f"""
    CREATE TABLE items (
        item_id         TEXT PRIMARY KEY,
        card_id         TEXT NOT NULL,
        cloze_index     INTEGER,
        fsrs_card_json  TEXT NOT NULL,
        state           TEXT NOT NULL DEFAULT 'new'
                        CHECK (state IN ('new', 'learning', 'review', 'relearning')),
        due_utc         TEXT,
        stability       REAL,
        difficulty      REAL,
        reps            INTEGER NOT NULL DEFAULT 0,
        lapses          INTEGER NOT NULL DEFAULT 0,
        last_review_utc TEXT,
        suspended       INTEGER NOT NULL DEFAULT 0,
        introduced_utc  TEXT,
        created_utc     TEXT NOT NULL
    );
    CREATE INDEX items_card ON items(card_id);
    CREATE INDEX items_due ON items(due_utc);

    CREATE TABLE review_log (
        id                   INTEGER PRIMARY KEY AUTOINCREMENT,
        item_id              TEXT NOT NULL REFERENCES items(item_id),
        card_id              TEXT NOT NULL,
        reviewed_utc         TEXT NOT NULL,
        rating               INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 4),
        auto_graded          INTEGER NOT NULL,
        correct              INTEGER,
        guessed              INTEGER NOT NULL DEFAULT 0,
        answer_json          TEXT,
        duration_ms          INTEGER,
        mode                 TEXT NOT NULL,
        session_id           TEXT,
        card_hash            TEXT NOT NULL,
        prev_state           TEXT NOT NULL,
        prev_item_json       TEXT NOT NULL,
        fsrs_review_log_json TEXT NOT NULL
    );
    CREATE INDEX review_log_time ON review_log(reviewed_utc);
    CREATE INDEX review_log_item ON review_log(item_id);
    CREATE INDEX review_log_session ON review_log(session_id);

    CREATE TABLE reports (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        card_id         TEXT NOT NULL,
        item_id         TEXT,
        reason          TEXT NOT NULL CHECK (reason IN ({", ".join(repr(r) for r in REPORT_REASONS)})),
        comment         TEXT NOT NULL DEFAULT '',
        created_utc     TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved')),
        resolved_utc    TEXT,
        resolution_note TEXT
    );

    CREATE TABLE settings (
        key        TEXT PRIMARY KEY,
        value_json TEXT NOT NULL
    );
    """,
]


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10, isolation_level=None, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    return conn


def migrate(conn: sqlite3.Connection) -> int:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL)")
    row = conn.execute("SELECT version FROM schema_version").fetchone()
    version = row["version"] if row else 0
    if row is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (0)")
    for v, script in enumerate(MIGRATIONS, start=1):
        if v <= version:
            continue
        conn.execute("BEGIN IMMEDIATE")
        try:
            for stmt in script.split(";"):
                if stmt.strip():
                    conn.execute(stmt)
            conn.execute("UPDATE schema_version SET version = ?", (v,))
            conn.execute("COMMIT")
        except Exception:
            conn.execute("ROLLBACK")
            raise
        version = v
    return version


def open_db(path: Path) -> sqlite3.Connection:
    conn = connect(path)
    migrate(conn)
    return conn


def sync_items(conn: sqlite3.Connection, content: Content, now: datetime) -> dict[str, int]:
    """Create `items` rows for review items that appeared in the content. Rows whose card or cloze
    disappeared are kept (orphans: progress is never deleted) and simply ignored by the queue."""
    from revision.scheduler import new_fsrs_card_json

    existing = {r["item_id"] for r in conn.execute("SELECT item_id FROM items")}
    added = 0
    conn.execute("BEGIN IMMEDIATE")
    try:
        for item_id, (_lc, spec) in content.items.items():
            if item_id in existing:
                continue
            conn.execute(
                "INSERT INTO items (item_id, card_id, cloze_index, fsrs_card_json, state, created_utc)"
                " VALUES (?, ?, ?, ?, 'new', ?)",
                (item_id, spec.card_id, spec.cloze_index, new_fsrs_card_json(item_id), iso(now)),
            )
            added += 1
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    orphans = len(existing - set(content.items))
    return {"added": added, "orphans": orphans, "total": len(existing) + added}


def orphan_items(conn: sqlite3.Connection, content: Content) -> list[sqlite3.Row]:
    rows = conn.execute("SELECT * FROM items ORDER BY item_id").fetchall()
    return [r for r in rows if r["item_id"] not in content.items]


def row_dict(row: sqlite3.Row | None) -> dict | None:
    return dict(row) if row is not None else None


def dumps(obj) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def backup(conn: sqlite3.Connection, backup_dir: Path, now: datetime, keep: int = 30) -> Path:
    """Online backup to backups/revision-YYYYMMDD-HHMM.db; keeps the `keep` most recent."""
    backup_dir.mkdir(parents=True, exist_ok=True)
    out = backup_dir / f"revision-{now.astimezone(UTC).strftime('%Y%m%d-%H%M')}.db"
    dst = sqlite3.connect(out)
    try:
        conn.backup(dst)
    finally:
        dst.close()
    files = sorted(backup_dir.glob("revision-*.db"))
    for old in files[:-keep] if keep > 0 else []:
        old.unlink()
    return out


def export_all(conn: sqlite3.Connection) -> dict:
    out: dict = {"schema_version": conn.execute("SELECT version FROM schema_version").fetchone()[0]}
    for table in ("items", "review_log", "reports", "settings"):
        out[table] = [dict(r) for r in conn.execute(f"SELECT * FROM {table}")]  # noqa: S608 (fixed names)
    return out
