"""Applying reviews, undo, suspend, and the JSON view of a review item."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote

from revision.content import Content, LoadedCard, exam_label, render_cloze
from revision.db import dumps, iso, row_dict
from revision.grading import grade
from revision.scheduler import FsrsScheduler


class ReviewError(ValueError):
    pass


class NotFound(ReviewError):
    pass


@dataclass
class ReviewInput:
    item_id: str
    mode: str = "study"
    session_id: str | None = None
    rating: int | None = None
    answer: bool | list[int] | None = None
    guessed: bool = False
    too_easy: bool = False
    duration_ms: int | None = None


MAX_DURATION_MS = 5 * 60 * 1000


def _get_item(conn: sqlite3.Connection, content: Content, item_id: str) -> tuple[sqlite3.Row, LoadedCard]:
    row = conn.execute("SELECT * FROM items WHERE item_id = ?", (item_id,)).fetchone()
    entry = content.items.get(item_id)
    if row is None or entry is None:
        raise NotFound(f"unknown item '{item_id}'")
    return row, entry[0]


def apply_review(conn: sqlite3.Connection, content: Content, sched: FsrsScheduler, inp: ReviewInput, now: datetime):
    row, lc = _get_item(conn, content, inp.item_id)
    if row["suspended"]:
        raise ReviewError("item is suspended")
    g = grade(lc.card, rating=inp.rating, answer=inp.answer, guessed=inp.guessed, too_easy=inp.too_easy)
    duration = None if inp.duration_ms is None else max(0, min(int(inp.duration_ms), MAX_DURATION_MS))
    out = sched.review(row["fsrs_card_json"], g.rating, now, duration)
    card = out.card
    conn.execute("BEGIN IMMEDIATE")
    try:
        conn.execute(
            "UPDATE items SET fsrs_card_json = ?, state = ?, due_utc = ?, stability = ?, difficulty = ?,"
            " reps = reps + 1, lapses = lapses + ?, last_review_utc = ?, introduced_utc = COALESCE(introduced_utc, ?)"
            " WHERE item_id = ?",
            (
                card.to_json(),
                out.state,
                iso(card.due),
                card.stability,
                card.difficulty,
                int(out.lapse),
                iso(now),
                iso(now),
                inp.item_id,
            ),
        )
        cur = conn.execute(
            "INSERT INTO review_log (item_id, card_id, reviewed_utc, rating, auto_graded, correct, guessed,"
            " answer_json, duration_ms, mode, session_id, card_hash, prev_state, prev_item_json, fsrs_review_log_json)"
            " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                inp.item_id,
                lc.card.id,
                iso(now),
                g.rating,
                int(g.auto_graded),
                None if g.correct is None else int(g.correct),
                int(inp.guessed and g.auto_graded),
                None if g.answer is None else dumps(g.answer),
                duration,
                inp.mode,
                inp.session_id,
                lc.hash,
                row["state"],
                dumps(dict(row)),
                out.log.to_json(),
            ),
        )
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return {
        "log_id": cur.lastrowid,
        "item_id": inp.item_id,
        "rating": g.rating,
        "auto_graded": g.auto_graded,
        "correct": g.correct,
        "correct_answer": g.correct_answer,
        "state": out.state,
        "due": iso(card.due),
        "interval_seconds": max(0.0, (card.due - now).total_seconds()),
        "explanation": lc.card.explanation,
        "trap": lc.card.trap,
    }


_ITEM_COLUMNS = (
    "fsrs_card_json",
    "state",
    "due_utc",
    "stability",
    "difficulty",
    "reps",
    "lapses",
    "last_review_utc",
    "suspended",
    "introduced_utc",
)


def undo_last(conn: sqlite3.Connection, session_id: str | None = None) -> dict:
    """Undo the most recent review (of `session_id` when given): restore the item, delete the log row."""
    q = "SELECT * FROM review_log" + (" WHERE session_id = ?" if session_id else "") + " ORDER BY id DESC LIMIT 1"
    log = conn.execute(q, (session_id,) if session_id else ()).fetchone()
    if log is None:
        raise NotFound("nothing to undo")
    prev = json.loads(log["prev_item_json"])
    conn.execute("BEGIN IMMEDIATE")
    try:
        sets = ", ".join(f"{c} = ?" for c in _ITEM_COLUMNS)
        conn.execute(f"UPDATE items SET {sets} WHERE item_id = ?", (*[prev[c] for c in _ITEM_COLUMNS], log["item_id"]))
        conn.execute("DELETE FROM review_log WHERE id = ?", (log["id"],))
        conn.execute("COMMIT")
    except Exception:
        conn.execute("ROLLBACK")
        raise
    return {"item_id": log["item_id"], "undone_log_id": log["id"]}


def set_suspended(conn: sqlite3.Connection, content: Content, item_id: str, suspended: bool) -> dict:
    _get_item(conn, content, item_id)
    conn.execute("UPDATE items SET suspended = ? WHERE item_id = ?", (int(suspended), item_id))
    return {"item_id": item_id, "suspended": suspended}


def session_summary(conn: sqlite3.Connection, session_id: str) -> dict:
    rows = conn.execute("SELECT * FROM review_log WHERE session_id = ? ORDER BY id", (session_id,)).fetchall()
    auto = [r for r in rows if r["auto_graded"]]
    again = sorted({r["item_id"] for r in rows if r["rating"] == 1})
    return {
        "session_id": session_id,
        "reviews": len(rows),
        "items": len({r["item_id"] for r in rows}),
        "new": sum(1 for r in rows if r["prev_state"] == "new"),
        "auto_graded": len(auto),
        "auto_correct": sum(1 for r in auto if r["correct"]),
        "ratings": {str(k): sum(1 for r in rows if r["rating"] == k) for k in (1, 2, 3, 4)},
        "duration_ms": sum(r["duration_ms"] or 0 for r in rows),
        "again_items": again,
    }


# --------------------------------------------------------------------------- views


def source_view(s) -> dict:
    d = s.model_dump()
    if s.pdf:
        d["page_url"] = f"/api/source/page?pdf={quote(s.pdf)}&page={s.page}"
        d["file_url"] = f"/files/{quote(s.pdf)}#page={s.page}"
    return d


def item_state(row: sqlite3.Row, sched: FsrsScheduler, now: datetime) -> dict:
    d = row_dict(row)
    d.pop("fsrs_card_json")
    d["retrievability"] = sched.retrievability(row["fsrs_card_json"], now)
    return d


def item_view(
    content: Content,
    lc: LoadedCard,
    row: sqlite3.Row,
    sched: FsrsScheduler,
    now: datetime,
    *,
    with_answer: bool = False,
) -> dict:
    """Everything the Review screen needs. tf/mcq answers are withheld unless `with_answer`
    (they come back from POST /api/review)."""
    c = lc.card
    lec = content.lectures[c.lecture]
    idx = row["cloze_index"]
    if c.type == "cloze":
        front, back = render_cloze(c.front, idx, reveal=False), render_cloze(c.front, idx, reveal=True)
    else:
        front, back = c.front, c.back
    view = {
        "item_id": row["item_id"],
        "card_id": c.id,
        "cloze_index": idx,
        "type": c.type,
        "origin": c.origin,
        "exam_label": exam_label(c.id) if c.origin == "exam_official" else None,
        "lecture": c.lecture,
        "lecture_title": lec.title,
        "week": lec.week,
        "also_lectures": c.also_lectures,
        "themes": [{"id": t, "label": content.themes[t].label} for t in c.themes],
        "priority": c.priority,
        "front": front,
        "back": back,
        "choices": c.choices,
        "multi": c.multi,
        "shuffle": c.shuffle,
        "explanation": c.explanation,
        "trap": c.trap,
        "images": [{"url": f"/content-img/{quote(im.src)}", "alt": im.alt} for im in c.images],
        "sources": [source_view(s) for s in c.sources],
        "state": row["state"],
        "is_new": row["state"] == "new",
        "previews": {str(k): v for k, v in sched.previews(row["fsrs_card_json"], now).items()},
        "hash": lc.hash,
    }
    if c.type in ("tf", "mcq"):
        view["answer"] = c.answer if with_answer else None
        if not with_answer:
            # the explanation/trap give the answer away: sent with the grading result instead
            view["explanation"] = None
            view["trap"] = None
    return view
