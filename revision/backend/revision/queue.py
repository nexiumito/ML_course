"""Building review queues for every mode (SPEC §5.2, §5.4).

Stateless: each call recomputes the next item from the DB + content. A client-generated
`session_id` (stored in the review log) lets drill-type modes skip what this session already saw
and drives new/review interleaving.

Modes
- study : due learning/relearning → interleaved (due reviews, new items within daily limits).
          Filters (weeks/lectures/themes/origins/types/core) turn it into the "filtered" mode.
- exam  : study restricted to tf/mcq exam cards (official and/or unofficial);
          with `include_not_due`, a random drill over all unlocked exam items.
- weak  : introduced items ranked by weakness score, top N per session.
- drill : N random items from the filter, ignoring due dates.
"""

from __future__ import annotations

import hashlib
import sqlite3
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from revision.content import Content, LoadedCard
from revision.db import iso, parse_iso
from revision.scheduler import FsrsScheduler
from revision.settings import Settings

MODES = ("study", "exam", "weak", "drill")
EXAM_ORIGINS = {"exam_official", "exam_style"}
LEARNING_STATES = ("learning", "relearning")


class QueueError(ValueError):
    pass


@dataclass
class Filters:
    weeks: set[int] = field(default_factory=set)
    lectures: set[str] = field(default_factory=set)
    themes: set[str] = field(default_factory=set)
    origins: set[str] = field(default_factory=set)
    types: set[str] = field(default_factory=set)
    core_only: bool = False

    def match(self, lc: LoadedCard, content: Content) -> bool:
        c = lc.card
        if self.weeks and content.week_of(c) not in self.weeks:
            return False
        if self.lectures and c.lecture not in self.lectures:
            return False
        if self.themes and not self.themes.intersection(c.themes):
            return False
        if self.origins and c.origin not in self.origins:
            return False
        if self.types and c.type not in self.types:
            return False
        if self.core_only and c.priority != "core":
            return False
        return True


@dataclass
class QueueRequest:
    mode: str = "study"
    filters: Filters = field(default_factory=Filters)
    session_id: str | None = None
    exclude: str | None = None  # item just reviewed: avoid showing it twice in a row
    include_not_due: bool = False  # exam mode
    learn_ahead: bool = False  # take a learning item that is not yet due (user chose "continue")
    ignore_limits: bool = False  # "review anyway" past the daily review cap
    limit: int | None = None  # N for weak / drill


@dataclass
class QueueResult:
    item_id: str | None
    counts: dict[str, int]
    waiting_until: datetime | None = None
    limit_reached: bool = False
    done: bool = False


# ------------------------------------------------------------------ day boundaries


def day_bounds(now: datetime, tz_name: str, rollover_hour: int) -> tuple[datetime, datetime]:
    """UTC [start, end) of the current review day (a day starts at `rollover_hour` local time).
    Arithmetic is done on local wall-clock time, so DST days are 23 h / 25 h long."""
    local = now.astimezone(ZoneInfo(tz_name))
    start = local.replace(hour=rollover_hour, minute=0, second=0, microsecond=0)
    if local < start:
        start -= timedelta(days=1)
    end = start + timedelta(days=1)
    return start.astimezone(UTC), end.astimezone(UTC)


# ------------------------------------------------------------------ helpers


def _stable_rand(seed: str, item_id: str) -> str:
    return hashlib.sha1(f"{seed}|{item_id}".encode()).hexdigest()


def _session_item_ids(conn: sqlite3.Connection, session_id: str | None) -> set[str]:
    if not session_id:
        return set()
    return {r[0] for r in conn.execute("SELECT DISTINCT item_id FROM review_log WHERE session_id = ?", (session_id,))}


def eligible_rows(conn: sqlite3.Connection, content: Content, filters: Filters) -> list[tuple[sqlite3.Row, LoadedCard]]:
    """Non-suspended items whose card exists, is active and matches the filters."""
    out = []
    for row in conn.execute("SELECT * FROM items WHERE suspended = 0"):
        entry = content.items.get(row["item_id"])
        if entry is None:
            continue  # orphan
        lc = entry[0]
        if content.is_active(lc.card) and filters.match(lc, content):
            out.append((row, lc))
    return out


def recent_again_items(conn: sqlite3.Connection, now: datetime, days: int = 7) -> set[str]:
    """Items whose latest review, within the last `days`, was rated Again."""
    return {
        r[0]
        for r in conn.execute(
            "SELECT item_id FROM review_log l WHERE reviewed_utc >= ? AND rating = 1 AND id = "
            "(SELECT MAX(id) FROM review_log WHERE item_id = l.item_id)",
            (iso(now - timedelta(days=days)),),
        )
    }


def weakness_score(row: sqlite3.Row, retrievability: float | None, again_recent: bool) -> float:
    r = retrievability if retrievability is not None else 1.0
    return row["lapses"] * 2 + (1 - r) * 3 + (row["difficulty"] or 0) / 10 + (2 if again_recent else 0)


def _effective(req: QueueRequest) -> QueueRequest:
    if req.mode not in MODES:
        raise QueueError(f"unknown mode '{req.mode}'")
    if req.mode != "exam":
        return req
    f = req.filters
    origins = (f.origins & EXAM_ORIGINS) if f.origins else set(EXAM_ORIGINS)
    types = (f.types & {"tf", "mcq"}) if f.types else {"tf", "mcq"}
    if not origins or not types:
        raise QueueError("exam mode needs tf/mcq exam cards (official and/or unofficial)")
    filters = Filters(f.weeks, f.lectures, f.themes, origins, types, f.core_only)
    return QueueRequest(**{**req.__dict__, "filters": filters})


# ------------------------------------------------------------------ main entry


def next_item(
    conn: sqlite3.Connection,
    content: Content,
    settings: Settings,
    sched: FsrsScheduler,
    req: QueueRequest,
    now: datetime,
) -> QueueResult:
    req = _effective(req)
    rows = eligible_rows(conn, content, req.filters)
    if req.mode == "weak":
        return _weak(conn, rows, settings, sched, req, now)
    if req.mode == "drill" or (req.mode == "exam" and req.include_not_due):
        n = req.limit if req.limit is not None else (settings.drill_n if req.mode == "drill" else None)
        return _drill(conn, rows, req, n)
    return _study(conn, content, rows, settings, req, now)


def _drill(conn, rows, req: QueueRequest, n: int | None) -> QueueResult:
    seen = _session_item_ids(conn, req.session_id)
    seed = req.session_id or "no-session"
    pool = sorted(rows, key=lambda rl: _stable_rand(seed, rl[0]["item_id"]))
    total = len(pool) if n is None else min(n, len(pool))
    done = len(seen & {r["item_id"] for r, _ in pool})
    remaining = [r for r, _ in pool if r["item_id"] not in seen]
    left = max(0, total - done)
    if left == 0 or not remaining:
        return QueueResult(None, {"remaining": 0, "done": done, "total": total}, done=True)
    return QueueResult(remaining[0]["item_id"], {"remaining": left, "done": done, "total": total})


def _weak(conn, rows, settings: Settings, sched: FsrsScheduler, req: QueueRequest, now: datetime) -> QueueResult:
    n = req.limit if req.limit is not None else settings.weak_points_n
    seen = _session_item_ids(conn, req.session_id)
    again_recent = recent_again_items(conn, now)
    scored = []
    for row, _lc in rows:
        if row["introduced_utc"] is None:
            continue
        score = weakness_score(row, sched.retrievability(row["fsrs_card_json"], now), row["item_id"] in again_recent)
        scored.append((score, row["item_id"]))
    scored.sort(key=lambda s: (-s[0], s[1]))
    total = min(n, len(scored) + len(seen))
    done = len(seen & {i for _, i in scored})
    remaining = [i for _, i in scored if i not in seen]
    left = max(0, total - done)
    if left == 0 or not remaining:
        return QueueResult(None, {"remaining": 0, "done": done, "total": total}, done=True)
    return QueueResult(remaining[0], {"remaining": left, "done": done, "total": total})


def _study(conn, content: Content, rows, settings: Settings, req: QueueRequest, now: datetime) -> QueueResult:
    course = content.course
    day_start, day_end = day_bounds(now, course.timezone, course.day_rollover_hour)
    now_s, day_start_s, day_end_s = iso(now), iso(day_start), iso(day_end)
    ahead_s = iso(now + timedelta(minutes=settings.learn_ahead_minutes))

    learning_due, learning_later, review_due, new = [], [], [], []
    for row, lc in rows:
        st = row["state"]
        if st == "new":
            new.append((row, lc))
        elif st in LEARNING_STATES:
            (learning_due if row["due_utc"] <= now_s else learning_later).append(row)
        elif row["due_utc"] < day_end_s:
            review_due.append(row)

    # daily limits (global, all modes)
    new_today = conn.execute("SELECT COUNT(*) FROM items WHERE introduced_utc >= ?", (day_start_s,)).fetchone()[0]
    reviews_today = conn.execute(
        "SELECT COUNT(*) FROM review_log WHERE reviewed_utc >= ? AND prev_state = 'review'", (day_start_s,)
    ).fetchone()[0]
    new_left = max(0, settings.new_per_day - new_today)
    review_left = len(review_due) if req.ignore_limits else max(0, settings.max_reviews_per_day - reviews_today)

    # new items: course order (or stable random), siblings of a card reviewed today are buried
    touched_cards = {
        r[0] for r in conn.execute("SELECT DISTINCT card_id FROM review_log WHERE reviewed_utc >= ?", (day_start_s,))
    }
    new = [(r, lc) for r, lc in new if lc.card.id not in touched_cards or lc.card.type != "cloze"]
    if settings.new_order == "random":
        new.sort(key=lambda rl: _stable_rand("new", rl[0]["item_id"]))
    else:
        new.sort(key=lambda rl: (content.course_order_key(rl[1]), rl[0]["cloze_index"] or 0))
    # bury: at most one new cloze sibling per card per day
    seen_cards: set[str] = set()
    new_rows = []
    for r, lc in new:
        if lc.card.type == "cloze":
            if lc.card.id in seen_cards:
                continue
            seen_cards.add(lc.card.id)
        new_rows.append(r)
    new_rows = new_rows[:new_left]

    learning_due.sort(key=lambda r: r["due_utc"])
    learning_later.sort(key=lambda r: r["due_utc"])
    review_due.sort(key=lambda r: (r["due_utc"], r["item_id"]))
    limit_reached = len(review_due) > review_left
    review_rows = review_due[:review_left]

    learning_today = [r for r in learning_later if r["due_utc"] < day_end_s]
    counts = {"new": len(new_rows), "learning": len(learning_due) + len(learning_today), "review": len(review_rows)}

    def pick(lst):
        for r in lst:
            if r["item_id"] != req.exclude:
                return r
        return None

    chosen = pick(learning_due)
    if chosen is None:
        rev, nw = pick(review_rows), pick(new_rows)
        if rev is not None and nw is not None:
            n_rev, n_new = 0, 0
            if req.session_id:
                n_rev, n_new = conn.execute(
                    "SELECT COALESCE(SUM(prev_state = 'review'), 0), COALESCE(SUM(prev_state = 'new'), 0)"
                    " FROM review_log WHERE session_id = ?",
                    (req.session_id,),
                ).fetchone()
            chosen = nw if n_rev >= settings.interleave_ratio * (n_new + 1) else rev
        else:
            chosen = rev or nw
    if chosen is None:
        soon = [r for r in learning_later if r["due_utc"] <= ahead_s]
        if soon:
            if req.learn_ahead:
                chosen = soon[0]
            else:
                wait = parse_iso(soon[0]["due_utc"])
                return QueueResult(None, counts, waiting_until=wait, limit_reached=limit_reached)
    if chosen is None and req.exclude:
        # only the excluded item is left: show it anyway
        for lst in (learning_due, review_rows, new_rows):
            if any(r["item_id"] == req.exclude for r in lst):
                chosen = next(r for r in lst if r["item_id"] == req.exclude)
                break
    if chosen is None:
        return QueueResult(None, counts, limit_reached=limit_reached, done=not limit_reached)
    return QueueResult(chosen["item_id"], counts, limit_reached=limit_reached)
