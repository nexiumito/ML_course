"""Thin wrapper around py-fsrs (v6). Never reimplement FSRS: only adapt it to our storage.

py-fsrs 6 has no "New" state (a fresh Card starts in Learning, step 0); "new" is tracked by us
(`items.state = 'new'`, `introduced_utc IS NULL`) until the first review.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import UTC, datetime

from fsrs import Card, Rating, ReviewLog, Scheduler, State

from revision.settings import Settings

STATE_NAMES = {State.Learning: "learning", State.Review: "review", State.Relearning: "relearning"}
RATINGS = {1: Rating.Again, 2: Rating.Hard, 3: Rating.Good, 4: Rating.Easy}


def fsrs_card_id(item_id: str) -> int:
    return int(hashlib.sha1(item_id.encode()).hexdigest()[:12], 16)


def new_fsrs_card_json(item_id: str, now: datetime | None = None) -> str:
    return Card(card_id=fsrs_card_id(item_id), due=now or datetime.now(UTC)).to_json()


@dataclass
class ReviewOutcome:
    card: Card
    log: ReviewLog
    state: str
    lapse: bool


class FsrsScheduler:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._sched = Scheduler(desired_retention=settings.desired_retention, enable_fuzzing=True)
        # previews use the same parameters without fuzz, so the buttons show stable intervals
        self._preview = Scheduler(desired_retention=settings.desired_retention, enable_fuzzing=False)

    def review(self, card_json: str, rating: int, now: datetime, duration_ms: int | None = None) -> ReviewOutcome:
        card = Card.from_json(card_json)
        prev_state = card.state
        new_card, log = self._sched.review_card(card, RATINGS[rating], review_datetime=now, review_duration=duration_ms)
        lapse = prev_state == State.Review and rating == 1
        return ReviewOutcome(new_card, log, STATE_NAMES[new_card.state], lapse)

    def previews(self, card_json: str, now: datetime) -> dict[int, float]:
        """Seconds until the next due date for each rating (1..4)."""
        out: dict[int, float] = {}
        for r, rating in RATINGS.items():
            card = Card.from_json(card_json)
            if card.last_review is None:
                card.due = now
            new_card, _ = self._preview.review_card(card, rating, review_datetime=now)
            out[r] = max(0.0, (new_card.due - now).total_seconds())
        return out

    def retrievability(self, card_json: str, now: datetime) -> float | None:
        card = Card.from_json(card_json)
        if card.last_review is None:
            return None
        return float(self._sched.get_card_retrievability(card, current_datetime=now))
