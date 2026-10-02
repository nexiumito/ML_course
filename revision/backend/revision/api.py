"""JSON API (SPEC §7.1). Mounted under /api by `app.create_app`."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, ValidationError

from revision import __version__, stats
from revision import reports as rep
from revision.content import Content, ContentError, exam_label, load_content
from revision.db import connect, export_all, iso, orphan_items, sync_items
from revision.grading import GradingError
from revision.queue import Filters, QueueError, QueueRequest, next_item
from revision.reviews import (
    NotFound,
    ReviewError,
    ReviewInput,
    apply_review,
    item_state,
    item_view,
    session_summary,
    set_suspended,
    source_view,
    undo_last,
)
from revision.scheduler import FsrsScheduler
from revision.settings import load_settings, update_settings
from revision.sources import SourceError, render_page

router = APIRouter(prefix="/api")


# --------------------------------------------------------------------------- dependencies


def get_conn(request: Request) -> Iterator[sqlite3.Connection]:
    conn = connect(request.app.state.cfg.db_path)
    try:
        yield conn
    finally:
        conn.close()


def get_content(request: Request) -> Content:
    return request.app.state.content


def get_now(request: Request) -> datetime:
    return request.app.state.clock()


Conn = Annotated[sqlite3.Connection, Depends(get_conn)]
ContentDep = Annotated[Content, Depends(get_content)]
Now = Annotated[datetime, Depends(get_now)]


def _sched(conn: sqlite3.Connection) -> FsrsScheduler:
    return FsrsScheduler(load_settings(conn))


def _csv(value: str | None) -> set[str]:
    return {v.strip() for v in value.split(",") if v.strip()} if value else set()


def _filters(weeks, lectures, themes, origins, types, core) -> Filters:
    try:
        week_set = {int(w) for w in _csv(weeks)}
    except ValueError as e:
        raise HTTPException(400, "weeks must be integers") from e
    return Filters(week_set, _csv(lectures), _csv(themes), _csv(origins), _csv(types), core)


# --------------------------------------------------------------------------- meta / health


@router.get("/health")
def health(conn: Conn, content: ContentDep):
    n_items = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
    return {
        "status": "ok",
        "version": __version__,
        "cards": len(content.cards),
        "items": n_items,
        "orphans": len(orphan_items(conn, content)),
    }


@router.get("/meta")
def meta(conn: Conn, content: ContentDep):
    per_lecture: dict[str, dict[str, int]] = {}
    for lc in content.cards:
        d = per_lecture.setdefault(lc.card.lecture, {"cards": 0, "items": 0, "exam_official": 0, "exam_style": 0})
        d["cards"] += 1
        d["items"] += len(lc.item_specs())
        if lc.card.origin != "concept":
            d[lc.card.origin] += 1
    course = content.course
    return {
        "lectures": [{**lec.model_dump(mode="json"), "counts": per_lecture.get(lec.id, {})} for lec in course.lectures],
        "weeks": sorted({lec.week for lec in course.lectures}),
        "themes": [t.model_dump() for t in course.themes],
        "exam_date": course.exam_date.isoformat() if course.exam_date else None,
        "timezone": course.timezone,
        "settings": load_settings(conn).model_dump(),
        "report_reasons": list(rep.REPORT_REASONS),
    }


@router.post("/admin/reload")
def reload_content(request: Request, conn: Conn, now: Now):
    cfg = request.app.state.cfg
    try:
        content = load_content(cfg.content_dir, cfg.repo_root)
    except ContentError as e:
        raise HTTPException(422, {"errors": e.errors, "warnings": e.warnings}) from e
    result = sync_items(conn, content, now)
    request.app.state.content = content
    return {**result, "cards": len(content.cards), "warnings": content.warnings}


# --------------------------------------------------------------------------- queue / review


@router.get("/queue")
def queue(
    conn: Conn,
    content: ContentDep,
    now: Now,
    mode: Literal["study", "exam", "weak", "drill"] = "study",
    weeks: str | None = None,
    lectures: str | None = None,
    themes: str | None = None,
    origins: str | None = None,
    types: str | None = None,
    core: bool = False,
    session_id: str | None = None,
    exclude: str | None = None,
    include_not_due: bool = False,
    learn_ahead: bool = False,
    ignore_limits: bool = False,
    limit: Annotated[int | None, Query(ge=1, le=1000)] = None,
):
    req = QueueRequest(
        mode,
        _filters(weeks, lectures, themes, origins, types, core),
        session_id,
        exclude,
        include_not_due,
        learn_ahead,
        ignore_limits,
        limit,
    )
    settings = load_settings(conn)
    sched = FsrsScheduler(settings)
    try:
        res = next_item(conn, content, settings, sched, req, now)
    except QueueError as e:
        raise HTTPException(400, str(e)) from e
    view = None
    if res.item_id:
        row = conn.execute("SELECT * FROM items WHERE item_id = ?", (res.item_id,)).fetchone()
        view = item_view(content, content.items[res.item_id][0], row, sched, now)
    return {
        "mode": mode,
        "item": view,
        "counts": res.counts,
        "waiting_until": iso(res.waiting_until) if res.waiting_until else None,
        "limit_reached": res.limit_reached,
        "done": res.done,
    }


class ReviewBody(BaseModel):
    item_id: str
    mode: Literal["study", "exam", "weak", "drill"] = "study"
    session_id: str | None = Field(default=None, max_length=100)
    rating: int | None = Field(default=None, ge=1, le=4)
    answer: bool | list[int] | None = None
    guessed: bool = False
    too_easy: bool = False
    duration_ms: int | None = Field(default=None, ge=0)


@router.post("/review")
def review(body: ReviewBody, conn: Conn, content: ContentDep, now: Now):
    try:
        return apply_review(conn, content, _sched(conn), ReviewInput(**body.model_dump()), now)
    except NotFound as e:
        raise HTTPException(404, str(e)) from e
    except (ReviewError, GradingError) as e:
        raise HTTPException(400, str(e)) from e


class UndoBody(BaseModel):
    session_id: str | None = None


@router.post("/undo")
def undo(body: UndoBody, conn: Conn):
    try:
        return undo_last(conn, body.session_id)
    except NotFound as e:
        raise HTTPException(404, str(e)) from e


@router.get("/session/{session_id}/summary")
def summary(session_id: str, conn: Conn):
    return session_summary(conn, session_id)


# --------------------------------------------------------------------------- browse


def _search_text(lc) -> str:
    c = lc.card
    parts = [c.id, c.front, c.back or "", c.explanation or "", c.trap or "", *(c.choices or [])]
    return "\n".join(parts).lower()


@router.get("/cards")
def list_cards(
    conn: Conn,
    content: ContentDep,
    q: str | None = None,
    weeks: str | None = None,
    lectures: str | None = None,
    themes: str | None = None,
    origins: str | None = None,
    types: str | None = None,
    core: bool = False,
    include_inactive: bool = True,
):
    f = _filters(weeks, lectures, themes, origins, types, core)
    rows = {r["item_id"]: r for r in conn.execute("SELECT * FROM items")}
    needle = (q or "").lower().strip()
    out = []
    for lc in content.cards:
        c = lc.card
        active = content.is_active(c)
        if (not include_inactive and not active) or not f.match(lc, content):
            continue
        if needle and needle not in _search_text(lc):
            continue
        items = []
        for spec in lc.item_specs():
            r = rows.get(spec.item_id)
            items.append(
                {
                    "item_id": spec.item_id,
                    "state": r["state"] if r else "new",
                    "due_utc": r["due_utc"] if r else None,
                    "suspended": bool(r["suspended"]) if r else False,
                }
            )
        out.append(
            {
                "id": c.id,
                "type": c.type,
                "origin": c.origin,
                "lecture": c.lecture,
                "week": content.week_of(c),
                "themes": c.themes,
                "priority": c.priority,
                "front": c.front,
                "exam_label": exam_label(c.id),
                "active": active,
                "file": lc.file,
                "items": items,
            }
        )
    return {"cards": out, "total": len(out)}


_HISTORY_FIELDS = ("id", "reviewed_utc", "rating", "auto_graded", "correct", "guessed", "duration_ms", "mode")


@router.get("/cards/{card_id}")
def card_detail(card_id: str, conn: Conn, content: ContentDep, now: Now):
    lc = content.by_id.get(card_id)
    if lc is None:
        raise HTTPException(404, f"unknown card '{card_id}'")
    sched = _sched(conn)
    items = []
    for spec in lc.item_specs():
        row = conn.execute("SELECT * FROM items WHERE item_id = ?", (spec.item_id,)).fetchone()
        if row is None:
            continue
        history = [
            {k: r[k] for k in _HISTORY_FIELDS}
            for r in conn.execute("SELECT * FROM review_log WHERE item_id = ? ORDER BY id", (spec.item_id,))
        ]
        items.append(
            {
                "view": item_view(content, lc, row, sched, now, with_answer=True),
                "state": item_state(row, sched, now),
                "history": history,
            }
        )
    card = lc.card.model_dump(mode="json")
    card["sources"] = [source_view(s) for s in lc.card.sources]
    return {
        "card": card,
        "file": lc.file,
        "position": lc.position,
        "hash": lc.hash,
        "active": content.is_active(lc.card),
        "exam_label": exam_label(card_id),
        "items": items,
    }


@router.post("/items/{item_id}/suspend")
def suspend(item_id: str, conn: Conn, content: ContentDep):
    try:
        return set_suspended(conn, content, item_id, True)
    except NotFound as e:
        raise HTTPException(404, str(e)) from e


@router.post("/items/{item_id}/unsuspend")
def unsuspend(item_id: str, conn: Conn, content: ContentDep):
    try:
        return set_suspended(conn, content, item_id, False)
    except NotFound as e:
        raise HTTPException(404, str(e)) from e


# --------------------------------------------------------------------------- reports


class ReportBody(BaseModel):
    card_id: str
    item_id: str | None = None
    reason: str
    comment: str = Field(default="", max_length=4000)


@router.post("/reports")
def create_report(body: ReportBody, conn: Conn, content: ContentDep, now: Now):
    try:
        rid = rep.create_report(
            conn, content, card_id=body.card_id, item_id=body.item_id, reason=body.reason, comment=body.comment, now=now
        )
    except rep.ReportError as e:
        raise HTTPException(400, str(e)) from e
    return {"id": rid}


@router.get("/reports")
def get_reports(conn: Conn, status: Literal["open", "resolved"] | None = None):
    return {"reports": rep.list_reports(conn, status)}


class ResolveBody(BaseModel):
    note: str = ""


@router.post("/reports/{report_id}/resolve")
def resolve(report_id: int, body: ResolveBody, conn: Conn, now: Now):
    try:
        return rep.resolve_report(conn, report_id, body.note, now)
    except rep.ReportError as e:
        raise HTTPException(400, str(e)) from e


# --------------------------------------------------------------------------- stats


@router.get("/stats/overview")
def stats_overview(conn: Conn, content: ContentDep, now: Now):
    settings = load_settings(conn)
    return stats.overview(conn, content, settings, FsrsScheduler(settings), now)


@router.get("/stats/calendar")
def stats_calendar(conn: Conn, content: ContentDep, now: Now, days: Annotated[int, Query(ge=1, le=730)] = 90):
    return {"days": stats.calendar(conn, content, now, days), "retention": stats.retention(conn, now)}


@router.get("/stats/forecast")
def stats_forecast(conn: Conn, content: ContentDep, now: Now, days: Annotated[int, Query(ge=1, le=365)] = 30):
    return {"days": stats.forecast(conn, content, now, days)}


@router.get("/stats/by-lecture")
def stats_by_lecture(conn: Conn, content: ContentDep, now: Now):
    return {"lectures": stats.by_lecture(conn, content, _sched(conn), now)}


@router.get("/stats/by-theme")
def stats_by_theme(conn: Conn, content: ContentDep, now: Now):
    return {"themes": stats.by_theme(conn, content, _sched(conn), now)}


@router.get("/stats/exam")
def stats_exam(conn: Conn, content: ContentDep):
    return stats.exam_stats(conn, content)


@router.get("/stats/weakest")
def stats_weakest(conn: Conn, content: ContentDep, now: Now, n: Annotated[int, Query(ge=1, le=200)] = 20):
    return {"items": stats.weakest(conn, content, _sched(conn), now, n)}


# --------------------------------------------------------------------------- sources, settings, export


@router.get("/source/page")
def source_page(
    request: Request, pdf: str, page: Annotated[int, Query(ge=1)], scale: Annotated[float, Query(ge=0.5, le=4.0)] = 2.0
):
    cfg = request.app.state.cfg
    try:
        path = render_page(cfg.repo_root, cfg.page_cache_dir, pdf, page, scale)
    except SourceError as e:
        raise HTTPException(404, str(e)) from e
    return FileResponse(path, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})


@router.get("/settings")
def get_settings(conn: Conn):
    return load_settings(conn).model_dump()


@router.put("/settings")
def put_settings(patch: dict, conn: Conn):
    try:
        return update_settings(conn, patch).model_dump()
    except ValidationError as e:
        raise HTTPException(422, e.errors(include_url=False, include_context=False)) from e


@router.get("/export")
def export(conn: Conn, now: Now):
    data = export_all(conn)
    data["exported_utc"] = iso(now)
    return data
