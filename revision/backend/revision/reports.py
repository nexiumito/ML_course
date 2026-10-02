"""Card reports ("flag this card", SPEC §5.5)."""

from __future__ import annotations

import sqlite3
from datetime import datetime

from revision.content import Content
from revision.db import REPORT_REASONS, iso


class ReportError(ValueError):
    pass


def create_report(
    conn: sqlite3.Connection,
    content: Content,
    *,
    card_id: str,
    item_id: str | None,
    reason: str,
    comment: str,
    now: datetime,
) -> int:
    if card_id not in content.by_id:
        raise ReportError(f"unknown card '{card_id}'")
    if item_id is not None and (item_id not in content.items or content.items[item_id][1].card_id != card_id):
        raise ReportError(f"unknown item '{item_id}' for card '{card_id}'")
    if reason not in REPORT_REASONS:
        raise ReportError(f"reason must be one of {', '.join(REPORT_REASONS)}")
    cur = conn.execute(
        "INSERT INTO reports (card_id, item_id, reason, comment, created_utc) VALUES (?, ?, ?, ?, ?)",
        (card_id, item_id, reason, comment.strip(), iso(now)),
    )
    return int(cur.lastrowid)


def list_reports(conn: sqlite3.Connection, status: str | None = None) -> list[dict]:
    if status not in (None, "open", "resolved"):
        raise ReportError("status must be open or resolved")
    q = "SELECT * FROM reports" + (" WHERE status = ?" if status else "") + " ORDER BY id"
    return [dict(r) for r in conn.execute(q, (status,) if status else ())]


def resolve_report(conn: sqlite3.Connection, report_id: int, note: str, now: datetime) -> dict:
    row = conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
    if row is None:
        raise ReportError(f"no report #{report_id}")
    if row["status"] == "resolved":
        raise ReportError(f"report #{report_id} is already resolved")
    conn.execute(
        "UPDATE reports SET status = 'resolved', resolved_utc = ?, resolution_note = ? WHERE id = ?",
        (iso(now), note.strip(), report_id),
    )
    return dict(conn.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone())


def reports_markdown(reports: list[dict], content: Content | None) -> str:
    """Markdown listing for `revision reports list` (read by Claude at the start of a content session)."""
    if not reports:
        return "No reports.\n"
    out = []
    for r in reports:
        lc = content.by_id.get(r["card_id"]) if content else None
        where = f"`{lc.file}` #{lc.position}" if lc else "(card no longer in content)"
        out.append(f"## #{r['id']} — {r['reason']} — `{r['card_id']}` ({r['status']})")
        out.append(f"- created: {r['created_utc']} · item: {r['item_id'] or '—'} · file: {where}")
        if r["comment"]:
            out.append(f"- comment: {r['comment']}")
        if lc:
            front = lc.card.front.strip().replace("\n", "\n  > ")
            out.append(f"- front:\n  > {front}")
        if r["status"] == "resolved":
            out.append(f"- resolved {r['resolved_utc']}: {r['resolution_note']}")
        out.append("")
    return "\n".join(out)
