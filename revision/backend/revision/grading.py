"""Auto-grading of tf/mcq cards and rating derivation (SPEC §5.3)."""

from __future__ import annotations

from dataclasses import dataclass

from revision.content import Card

AGAIN, HARD, GOOD, EASY = 1, 2, 3, 4


class GradingError(ValueError):
    pass


@dataclass
class GradeResult:
    rating: int
    auto_graded: bool
    correct: bool | None
    correct_answer: bool | list[int] | None
    answer: bool | list[int] | None


def grade(card: Card, *, rating: int | None, answer, guessed: bool = False, too_easy: bool = False) -> GradeResult:
    """Self-graded (basic/cloze): `rating` 1..4 is required.
    Auto-graded (tf/mcq): `answer` is required; wrong ⇒ Again, correct ⇒ Good,
    correct + guessed ⇒ Hard, correct + too easy ⇒ Easy. mcq is graded by exact set match."""
    if card.type in ("basic", "cloze"):
        if rating not in (AGAIN, HARD, GOOD, EASY):
            raise GradingError("self-graded card requires rating 1..4")
        return GradeResult(rating, False, None, None, None)

    if card.type == "tf":
        if not isinstance(answer, bool):
            raise GradingError("tf card requires a boolean answer")
        correct = answer is card.answer
        given: bool | list[int] = answer
    else:  # mcq
        if not isinstance(answer, list) or not all(isinstance(a, int) and not isinstance(a, bool) for a in answer):
            raise GradingError("mcq card requires a list of choice indices")
        n = len(card.choices or [])
        if any(not 0 <= a < n for a in answer) or len(set(answer)) != len(answer):
            raise GradingError("invalid choice index")
        if not card.multi and len(answer) != 1:
            raise GradingError("single-answer mcq: select exactly one choice")
        correct = set(answer) == set(card.answer or [])
        given = sorted(answer)

    if not correct:
        derived = AGAIN
    elif too_easy:
        derived = EASY
    elif guessed:
        derived = HARD
    else:
        derived = GOOD
    return GradeResult(derived, True, correct, card.answer, given)
