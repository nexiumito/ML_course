from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from revision.content import load_content
from revision.db import sync_items
from revision.queue import Filters, QueueError, QueueRequest, day_bounds, next_item
from revision.reviews import ReviewInput, apply_review, set_suspended
from revision.scheduler import FsrsScheduler
from revision.settings import load_settings, update_settings

from .conftest import write_content

ACTIVE_ITEMS = {
    "04a-basic",
    "04a-cloze::c1",
    "04a-cloze::c2",
    "04a-tf",
    "style-04a-k",
    "04a-multi",
    "exam-2023-q30",
    "exam-2025-q24",
    "04b-noise",
}


def nxt(conn, content, clock, **kw):
    settings = load_settings(conn)
    return next_item(conn, content, settings, FsrsScheduler(settings), QueueRequest(**kw), clock())


def answer_for(content, item_id, correct=True):
    card = content.items[item_id][0].card
    if card.type == "tf":
        return {"answer": card.answer if correct else not card.answer}
    if card.type == "mcq":
        return {"answer": card.answer if correct else [i for i in range(len(card.choices)) if i not in card.answer][:1]}
    return {"rating": 3 if correct else 1}


def rev(conn, content, clock, item_id, rating=None, correct=True, **kw):
    settings = load_settings(conn)
    card = content.items[item_id][0].card
    extra = answer_for(content, item_id, correct)
    if rating is not None and card.type in ("basic", "cloze"):
        extra = {"rating": rating}
    if rating == 4 and card.type in ("tf", "mcq"):
        extra["too_easy"] = True
    return apply_review(conn, content, FsrsScheduler(settings), ReviewInput(item_id=item_id, **extra, **kw), clock())


def drain(conn, content, clock, max_steps=100, **kw) -> list[str]:
    seen = []
    for _ in range(max_steps):
        res = nxt(conn, content, clock, **kw)
        if res.item_id is None:
            return seen
        seen.append(res.item_id)
        rev(conn, content, clock, res.item_id, rating=4, mode=kw.get("mode", "study"), session_id=kw.get("session_id"))
    raise AssertionError("queue did not terminate")


# --------------------------------------------------------------------------- day boundaries


def test_day_bounds_rollover():
    # 01:30 local (CEST, UTC+2) on Oct 5 still belongs to the Oct 4 review day
    start, end = day_bounds(datetime(2026, 10, 4, 23, 30, tzinfo=UTC), "Europe/Zurich", 4)
    assert start == datetime(2026, 10, 4, 2, 0, tzinfo=UTC)
    assert end == datetime(2026, 10, 5, 2, 0, tzinfo=UTC)


def test_day_bounds_dst_end_is_25h():
    # DST ends 2026-10-25 03:00 CEST -> 02:00 CET
    start, end = day_bounds(datetime(2026, 10, 24, 12, 0, tzinfo=UTC), "Europe/Zurich", 4)
    assert end - start == timedelta(hours=25)


# --------------------------------------------------------------------------- study mode


def test_new_items_in_course_order_with_cloze_siblings_buried(conn, content, clock):
    res = nxt(conn, content, clock)
    assert res.item_id == "04a-basic"
    assert res.counts == {"new": 8, "learning": 0, "review": 0}  # 9 active items, c2 buried
    order = drain(conn, content, clock)
    assert set(order) == ACTIVE_ITEMS - {"04a-cloze::c2"}
    # concept cards of 04a, then 04a exam-style, then 04a official, then 04b
    pos = order.index
    assert pos("04a-multi") < pos("style-04a-k") < pos("exam-2023-q30") < pos("04b-noise")
    # next day the buried sibling shows up
    clock.advance(days=1)
    assert nxt(conn, content, clock).item_id == "04a-cloze::c2"


def test_inactive_lectures_and_orphans_excluded(conn, content, clock, cfg, tree):
    drained = drain(conn, content, clock)
    assert "05a-x" not in drained and "04a-needs-05a" not in drained
    # remove a card from content: its item becomes an orphan, kept in DB but never queued
    tree["files"]["cards/04b.yaml"] = []
    write_content(cfg.content_dir, tree)
    content2 = load_content(cfg.content_dir, cfg.repo_root)
    assert sync_items(conn, content2, clock())["orphans"] == 1
    clock.advance(days=400)
    assert "04b-noise" not in drain(conn, content2, clock, ignore_limits=True)


def test_new_per_day_limit(conn, content, clock):
    update_settings(conn, {"new_per_day": 2})
    assert drain(conn, content, clock) == ["04a-basic", "04a-cloze::c1"]
    res = nxt(conn, content, clock)
    assert res.done and res.counts["new"] == 0
    clock.advance(days=1)
    assert nxt(conn, content, clock).counts["new"] == 2


def test_learning_wait_and_learn_ahead(conn, content, clock):
    update_settings(conn, {"new_per_day": 1})
    rev(conn, content, clock, "04a-basic", rating=1)  # Again -> due in 1 min
    res = nxt(conn, content, clock)
    assert res.item_id is None and res.waiting_until == clock() + timedelta(minutes=1)
    assert not res.done and res.counts["learning"] == 1
    assert nxt(conn, content, clock, learn_ahead=True).item_id == "04a-basic"
    clock.advance(minutes=2)
    assert nxt(conn, content, clock).item_id == "04a-basic"


def test_exclude_last_item_unless_alone(conn, content, clock):
    first = nxt(conn, content, clock).item_id
    assert nxt(conn, content, clock, exclude=first).item_id != first
    assert nxt(conn, content, clock, filters=Filters(lectures={"04b"}), exclude="04b-noise").item_id == "04b-noise"


def test_review_cap_and_review_anyway(conn, content, clock):
    for item in ("04a-basic", "04a-tf", "04b-noise"):
        rev(conn, content, clock, item, rating=4)
    update_settings(conn, {"max_reviews_per_day": 2, "new_per_day": 0})
    clock.advance(days=200)
    res = nxt(conn, content, clock)
    assert res.counts["review"] == 2 and res.limit_reached
    drained = drain(conn, content, clock)
    assert len(drained) == 2
    res = nxt(conn, content, clock)
    assert res.item_id is None and res.limit_reached and not res.done
    assert nxt(conn, content, clock, ignore_limits=True).item_id is not None


def test_interleave_new_among_reviews(conn, content, clock):
    for item in ("04a-basic", "04a-tf", "04b-noise"):
        rev(conn, content, clock, item, rating=4)
    clock.advance(days=200)
    update_settings(conn, {"interleave_ratio": 1})
    s = "sess-1"
    kinds = []
    for _ in range(4):
        res = nxt(conn, content, clock, session_id=s)
        row = conn.execute("SELECT state FROM items WHERE item_id = ?", (res.item_id,)).fetchone()
        kinds.append(row["state"])
        rev(conn, content, clock, res.item_id, rating=4, session_id=s)
    assert kinds == ["review", "new", "review", "new"]


def test_suspended_items_skipped(conn, content, clock):
    set_suspended(conn, content, "04a-basic", True)
    assert nxt(conn, content, clock).item_id != "04a-basic"
    set_suspended(conn, content, "04a-basic", False)
    assert nxt(conn, content, clock).item_id == "04a-basic"


@pytest.mark.parametrize(
    "filters,expected",
    [
        (Filters(lectures={"04b"}), {"04b-noise"}),
        (Filters(weeks={4}), ACTIVE_ITEMS),
        (Filters(weeks={5}), set()),
        (Filters(themes={"bias-variance"}), {"04b-noise"}),
        (Filters(origins={"exam_official"}), {"exam-2023-q30", "exam-2025-q24"}),
        (Filters(types={"cloze"}), {"04a-cloze::c1", "04a-cloze::c2"}),
        (Filters(core_only=True), ACTIVE_ITEMS - {"04a-cloze::c1", "04a-cloze::c2"}),
    ],
)
def test_filters(conn, content, clock, filters, expected):
    got = set()
    for _ in range(3):  # day 1 + following days to reveal buried cloze siblings
        got |= set(drain(conn, content, clock, filters=filters))
        clock.advance(days=1)
    assert got == expected


# --------------------------------------------------------------------------- other modes


EXAM_ITEMS = {"style-04a-k", "exam-2023-q30", "exam-2025-q24"}


def test_exam_mode_only_exam_cards(conn, content, clock):
    assert set(drain(conn, content, clock, mode="exam")) == EXAM_ITEMS
    only_official = Filters(origins={"exam_official"})
    clock.advance(days=400)
    assert set(drain(conn, content, clock, mode="exam", filters=only_official, ignore_limits=True)) <= EXAM_ITEMS - {
        "style-04a-k"
    }
    with pytest.raises(QueueError):
        nxt(conn, content, clock, mode="exam", filters=Filters(origins={"concept"}))


def test_exam_mode_include_not_due_drills_everything_once(conn, content, clock):
    for item in EXAM_ITEMS:
        rev(conn, content, clock, item, rating=4)  # nothing due any more
    assert nxt(conn, content, clock, mode="exam").item_id is None
    got = drain(conn, content, clock, mode="exam", include_not_due=True, session_id="drill")
    assert sorted(got) == sorted(EXAM_ITEMS)


def test_drill_n_random_items_ignoring_due(conn, content, clock):
    a = nxt(conn, content, clock, mode="drill", session_id="A", limit=3)
    assert a.counts == {"remaining": 3, "done": 0, "total": 3}
    assert nxt(conn, content, clock, mode="drill", session_id="A", limit=3).item_id == a.item_id  # stable
    got = drain(conn, content, clock, mode="drill", session_id="A", limit=3)
    assert len(got) == len(set(got)) == 3
    res = nxt(conn, content, clock, mode="drill", session_id="A", limit=3)
    assert res.done and res.counts["done"] == 3


def test_weak_points_ranking(conn, content, clock):
    for item in ("04a-basic", "04a-tf", "04b-noise"):
        rev(conn, content, clock, item, rating=4)
    clock.advance(days=30)
    rev(conn, content, clock, "04a-tf", correct=False)  # lapse + recent Again
    res = nxt(conn, content, clock, mode="weak", session_id="W")
    assert res.item_id == "04a-tf"
    assert res.counts["total"] == 3  # only introduced items
    got = drain(conn, content, clock, mode="weak", session_id="W", limit=2)
    assert got[0] == "04a-tf" and len(got) == 2
