from __future__ import annotations

from datetime import timedelta

import pytest

from revision.grading import AGAIN, EASY, GOOD, HARD, GradingError, grade
from revision.scheduler import FsrsScheduler, new_fsrs_card_json
from revision.settings import Settings

from .conftest import T0


def test_new_card_good_goes_to_learning_then_review():
    s = FsrsScheduler(Settings())
    out = s.review(new_fsrs_card_json("x", T0), GOOD, T0)
    assert out.state == "learning" and not out.lapse
    out2 = s.review(out.card.to_json(), GOOD, out.card.due)
    assert out2.state == "review"
    assert out2.card.due - out.card.due >= timedelta(days=1)


def test_lapse_counts_only_from_review_state():
    s = FsrsScheduler(Settings())
    c = s.review(new_fsrs_card_json("x", T0), EASY, T0)
    assert c.state == "review"
    lapse = s.review(c.card.to_json(), AGAIN, c.card.due)
    assert lapse.lapse and lapse.state == "relearning"
    again_in_relearning = s.review(lapse.card.to_json(), AGAIN, lapse.card.due)
    assert not again_in_relearning.lapse


def test_previews_are_monotonic_and_stable():
    s = FsrsScheduler(Settings())
    card = new_fsrs_card_json("x", T0)
    p = s.previews(card, T0)
    assert p[1] <= p[2] <= p[3] <= p[4]
    assert p == s.previews(card, T0)  # no fuzz in previews
    assert p[1] == 60 and p[3] == 600  # py-fsrs default learning steps 1 min / 10 min


def test_retrievability():
    s = FsrsScheduler(Settings())
    card = new_fsrs_card_json("x", T0)
    assert s.retrievability(card, T0) is None
    out = s.review(card, EASY, T0)
    r_now = s.retrievability(out.card.to_json(), T0)
    r_later = s.retrievability(out.card.to_json(), T0 + timedelta(days=30))
    assert r_now == pytest.approx(1.0) and r_later < r_now


def test_higher_retention_gives_shorter_intervals():
    lo, hi = FsrsScheduler(Settings(desired_retention=0.8)), FsrsScheduler(Settings(desired_retention=0.95))
    card = new_fsrs_card_json("x", T0)
    assert lo.previews(card, T0)[4] > hi.previews(card, T0)[4]


# --------------------------------------------------------------------------- grading


def test_grade_self_graded(content):
    c = content.by_id["04a-basic"].card
    assert grade(c, rating=HARD, answer=None).rating == HARD
    with pytest.raises(GradingError):
        grade(c, rating=None, answer=None)


def test_grade_tf(content):
    c = content.by_id["exam-2023-q30"].card  # answer False
    assert grade(c, rating=None, answer=False).rating == GOOD
    assert grade(c, rating=None, answer=False, guessed=True).rating == HARD
    assert grade(c, rating=None, answer=False, too_easy=True).rating == EASY
    wrong = grade(c, rating=None, answer=True, too_easy=True)
    assert (wrong.rating, wrong.correct, wrong.correct_answer) == (AGAIN, False, False)
    with pytest.raises(GradingError):
        grade(c, rating=None, answer=[0])


def test_grade_mcq_single(content):
    c = content.by_id["exam-2025-q24"].card
    assert grade(c, rating=None, answer=[0]).correct
    assert grade(c, rating=None, answer=[2]).rating == AGAIN
    for bad in ([0, 1], [], [7], [True], "0"):
        with pytest.raises(GradingError):
            grade(c, rating=None, answer=bad)


def test_grade_mcq_multi_exact_set(content):
    c = content.by_id["04a-multi"].card  # answer [0, 1]
    assert grade(c, rating=None, answer=[1, 0]).correct
    assert not grade(c, rating=None, answer=[0]).correct
    assert not grade(c, rating=None, answer=[0, 1, 2]).correct
    assert not grade(c, rating=None, answer=[]).correct
