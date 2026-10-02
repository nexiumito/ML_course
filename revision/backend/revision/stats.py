"""Statistics for the Stats page (SPEC §7.2)."""

from __future__ import annotations

import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from revision.content import Content, exam_year
from revision.db import iso, parse_iso
from revision.queue import (
    Filters,
    QueueRequest,
    day_bounds,
    eligible_rows,
    next_item,
    recent_again_items,
    weakness_score,
)
from revision.scheduler import FsrsScheduler
from revision.settings import Settings

MATURE_DAYS = 21


def review_day(ts: datetime, content: Content) -> date:
    """Local 'review day' of a UTC timestamp (days start at day_rollover_hour)."""
    local = ts.astimezone(ZoneInfo(content.course.timezone))
    return (local - timedelta(hours=content.course.day_rollover_hour)).date()


def _interval_days(row) -> float | None:
    due, last = parse_iso(row["due_utc"]), parse_iso(row["last_review_utc"])
    if due is None or last is None:
        return None
    return (due - last).total_seconds() / 86400


def _active_rows(conn, content: Content):
    return eligible_rows(conn, content, Filters())


def overview(conn: sqlite3.Connection, content: Content, settings: Settings, sched: FsrsScheduler, now: datetime):
    rows = _active_rows(conn, content)
    by_state: dict[str, int] = defaultdict(int)
    for r, _ in rows:
        by_state[r["state"]] += 1
    suspended = conn.execute("SELECT COUNT(*) FROM items WHERE suspended = 1").fetchone()[0]
    queue = next_item(conn, content, settings, sched, QueueRequest(mode="study"), now)
    start, _ = day_bounds(now, content.course.timezone, content.course.day_rollover_hour)
    today = conn.execute(
        "SELECT COUNT(*) n, COALESCE(SUM(duration_ms), 0) ms, SUM(auto_graded) auto, SUM(correct) ok"
        " FROM review_log WHERE reviewed_utc >= ?",
        (iso(start),),
    ).fetchone()
    new_today = conn.execute("SELECT COUNT(*) FROM items WHERE introduced_utc >= ?", (iso(start),)).fetchone()[0]
    days = {review_day(parse_iso(r[0]), content) for r in conn.execute("SELECT reviewed_utc FROM review_log")}
    streak, d = 0, review_day(now, content)
    if d not in days:
        d -= timedelta(days=1)
    while d in days:
        streak += 1
        d -= timedelta(days=1)
    exam = content.course.exam_date
    return {
        "cards": sum(1 for c in content.cards if content.is_active(c.card)),
        "items": len(rows),
        "by_state": {s: by_state.get(s, 0) for s in ("new", "learning", "review", "relearning")},
        "suspended": suspended,
        "due": queue.counts,
        "today": {
            "reviews": today["n"],
            "new": new_today,
            "minutes": round(today["ms"] / 60000, 1),
            "auto_graded": today["auto"] or 0,
            "auto_correct": today["ok"] or 0,
        },
        "streak": streak,
        "exam_date": exam.isoformat() if exam else None,
        "days_to_exam": (exam - review_day(now, content)).days if exam else None,
    }


def calendar(conn: sqlite3.Connection, content: Content, now: datetime, days: int = 90):
    since = now - timedelta(days=days + 1)
    counts: dict[str, int] = defaultdict(int)
    for (ts,) in conn.execute("SELECT reviewed_utc FROM review_log WHERE reviewed_utc >= ?", (iso(since),)):
        counts[review_day(parse_iso(ts), content).isoformat()] += 1
    today = review_day(now, content)
    out = []
    for i in range(days - 1, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        out.append({"day": d, "reviews": counts.get(d, 0)})
    return out


def forecast(conn: sqlite3.Connection, content: Content, now: datetime, days: int = 30):
    today = review_day(now, content)
    buckets = [0] * days
    for r, _ in _active_rows(conn, content):
        if r["state"] == "new" or r["due_utc"] is None:
            continue
        offset = max(0, (review_day(parse_iso(r["due_utc"]), content) - today).days)
        if offset < days:
            buckets[offset] += 1
    return [{"day": (today + timedelta(days=i)).isoformat(), "due": n} for i, n in enumerate(buckets)]


def retention(conn: sqlite3.Connection, now: datetime):
    """True retention = share of passed (rating > 1) reviews of items that were in review state."""
    out = {}
    for window in (7, 30):
        rows = conn.execute(
            "SELECT auto_graded, rating FROM review_log WHERE prev_state = 'review' AND reviewed_utc >= ?",
            (iso(now - timedelta(days=window)),),
        ).fetchall()
        res = {}
        for name, sel in (("all", rows), ("self", [r for r in rows if not r[0]]), ("auto", [r for r in rows if r[0]])):
            n = len(sel)
            res[name] = {"n": n, "retention": (sum(1 for r in sel if r[1] > 1) / n) if n else None}
        out[f"{window}d"] = res
    return out


def _mastery(groups: dict[str, list], sched: FsrsScheduler, now: datetime):
    out = []
    for key, rows in groups.items():
        introduced = [r for r in rows if r["introduced_utc"] is not None]
        rs = [sched.retrievability(r["fsrs_card_json"], now) for r in introduced]
        rs = [x for x in rs if x is not None]
        mature = sum(1 for r in introduced if r["state"] == "review" and (_interval_days(r) or 0) >= MATURE_DAYS)
        out.append(
            {
                "key": key,
                "items": len(rows),
                "seen": len(introduced),
                "mature": mature,
                "mean_retrievability": (sum(rs) / len(rs)) if rs else None,
                "lapses": sum(r["lapses"] for r in rows),
            }
        )
    return out


def by_lecture(conn, content: Content, sched: FsrsScheduler, now: datetime):
    groups: dict[str, list] = {lec.id: [] for lec in content.course.lectures if lec.active}
    for r, lc in _active_rows(conn, content):
        groups.setdefault(lc.card.lecture, []).append(r)
    res = _mastery(groups, sched, now)
    for g in res:
        lec = content.lectures[g["key"]]
        g.update(title=lec.title, week=lec.week)
    return res


def by_theme(conn, content: Content, sched: FsrsScheduler, now: datetime):
    groups: dict[str, list] = defaultdict(list)
    for r, lc in _active_rows(conn, content):
        for t in lc.card.themes:
            groups[t].append(r)
    res = _mastery(dict(groups), sched, now)
    for g in res:
        g["label"] = content.themes[g["key"]].label
    return sorted(res, key=lambda g: g["key"])


def exam_stats(conn, content: Content):
    """Accuracy of auto-graded reviews on exam cards, by year / theme / origin."""
    by_year, by_theme, by_origin = (defaultdict(lambda: [0, 0]) for _ in range(3))
    for r in conn.execute("SELECT card_id, correct FROM review_log WHERE auto_graded = 1"):
        lc = content.by_id.get(r["card_id"])
        if lc is None or lc.card.origin == "concept":
            continue
        ok = 1 if r["correct"] else 0
        by_origin[lc.card.origin][0] += ok
        by_origin[lc.card.origin][1] += 1
        if (y := exam_year(lc.card.id)) is not None:
            by_year[str(y)][0] += ok
            by_year[str(y)][1] += 1
        for t in lc.card.themes:
            by_theme[t][0] += ok
            by_theme[t][1] += 1

    def fmt(d):
        return [{"key": k, "correct": v[0], "n": v[1], "accuracy": v[0] / v[1]} for k, v in sorted(d.items())]

    return {"by_year": fmt(by_year), "by_theme": fmt(by_theme), "by_origin": fmt(by_origin)}


def weakest(conn, content: Content, sched: FsrsScheduler, now: datetime, n: int = 20):
    again_recent = recent_again_items(conn, now)
    out = []
    for r, lc in _active_rows(conn, content):
        if r["introduced_utc"] is None:
            continue
        ret = sched.retrievability(r["fsrs_card_json"], now)
        out.append(
            {
                "item_id": r["item_id"],
                "card_id": lc.card.id,
                "lecture": lc.card.lecture,
                "score": round(weakness_score(r, ret, r["item_id"] in again_recent), 3),
                "lapses": r["lapses"],
                "retrievability": ret,
            }
        )
    out.sort(key=lambda x: (-x["score"], x["item_id"]))
    return out[:n]
