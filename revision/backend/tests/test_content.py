from __future__ import annotations

from pathlib import Path

import pytest

from revision.config import load_config
from revision.content import (
    ClozeError,
    ContentError,
    exam_label,
    load_content,
    parse_cloze,
    render_cloze,
)

from .conftest import write_content

# --------------------------------------------------------------------------- good fixture


def test_good_content_loads(content):
    assert len(content.cards) == 10
    assert "04a-cloze::c1" in content.items and "04a-cloze::c2" in content.items
    assert len(content.items) == 11
    assert content.is_active(content.by_id["04a-basic"].card)
    assert not content.is_active(content.by_id["05a-x"].card)
    assert not content.is_active(content.by_id["04a-needs-05a"].card)  # also_lectures inactive
    assert content.warnings == []


def test_real_repo_content_passes():
    """The committed content must always pass the checker."""
    cfg = load_config()
    content = load_content(cfg.content_dir, cfg.repo_root)
    assert content.cards


def test_card_hash_changes_with_content(content, cfg, tree):
    h = content.by_id["04a-basic"].hash
    tree["files"]["cards/04a.yaml"][0]["back"] = "The expected risk."
    write_content(cfg.content_dir, tree)
    assert load_content(cfg.content_dir, cfg.repo_root).by_id["04a-basic"].hash != h


# --------------------------------------------------------------------------- bad fixtures


def card(tree, file, idx):
    return tree["files"][file][idx]


BAD_CASES = [
    # (name, mutation, expected error substring)
    ("duplicate id", lambda t: card(t, "cards/04b.yaml", 0).update(id="04a-basic", lecture="04a"), "duplicate id"),
    ("unknown lecture", lambda t: card(t, "cards/04a.yaml", 0).update(also_lectures=["99z"]), "unknown lecture '99z'"),
    ("unknown theme", lambda t: card(t, "cards/04a.yaml", 0).update(themes=["nope"]), "unknown theme 'nope'"),
    ("no theme", lambda t: card(t, "cards/04a.yaml", 0).update(themes=[]), "at least one theme"),
    ("basic without back", lambda t: card(t, "cards/04a.yaml", 0).pop("back"), "requires 'back'"),
    ("basic with answer", lambda t: card(t, "cards/04a.yaml", 0).update(answer=True), "'answer' is not allowed"),
    ("cloze without deletion", lambda t: card(t, "cards/04a.yaml", 1).update(front="no deletion"), "no '{{c1::"),
    ("cloze gap", lambda t: card(t, "cards/04a.yaml", 1).update(front="{{c1::a}} {{c3::b}}"), "without gaps"),
    ("cloze starts at 2", lambda t: card(t, "cards/04a.yaml", 1).update(front="{{c2::a}}"), "without gaps"),
    ("cloze unterminated", lambda t: card(t, "cards/04a.yaml", 1).update(front="{{c1::$x$"), "unterminated"),
    ("cloze malformed", lambda t: card(t, "cards/04a.yaml", 1).update(front="{{c1::a}} {{c2:b}}"), "malformed"),
    ("cloze half math", lambda t: card(t, "cards/04a.yaml", 1).update(front="$a = {{c1::b$}}"), "unbalanced '$'"),
    ("tf non-bool", lambda t: card(t, "cards/04a.yaml", 2).update(answer="yes"), "field 'answer'"),
    ("tf missing answer", lambda t: card(t, "cards/04a.yaml", 2).pop("answer"), "requires 'answer: true|false'"),
    ("mcq index out of range", lambda t: card(t, "exams/04a.yaml", 1).update(answer=[4]), "out of range"),
    ("mcq empty answer", lambda t: card(t, "exams/04a.yaml", 1).update(answer=[]), "non-empty list"),
    ("mcq one choice", lambda t: card(t, "exams/04a.yaml", 1).update(choices=["a"], answer=[0]), "2–10 choices"),
    ("mcq 2 answers not multi", lambda t: card(t, "exams/04a.yaml", 1).update(answer=[0, 1]), "exactly one answer"),
    ("mcq scalar answer", lambda t: card(t, "exams/04a.yaml", 1).update(answer=0), "field 'answer'"),
    (
        "official must be tf/mcq",
        lambda t: card(t, "exams/04a.yaml", 0).update(type="basic", back="x", answer=None),
        "must be tf or mcq",
    ),
    (
        "exam card without explanation",
        lambda t: card(t, "cards/04a.yaml", 3).pop("explanation"),
        "require an explanation",
    ),
    ("bad official id", lambda t: card(t, "exams/04a.yaml", 0).update(id="exam-23-q30"), "official exam ids"),
    ("bad style id", lambda t: card(t, "cards/04a.yaml", 3).update(id="style-x"), "must start with 'style-04a-'"),
    ("bad concept id", lambda t: card(t, "cards/04a.yaml", 0).update(id="04b-basic"), "must start with '04a-'"),
    ("uppercase id", lambda t: card(t, "cards/04a.yaml", 0).update(id="04a-Basic"), "kebab-case"),
    (
        "wrong file",
        lambda t: card(t, "cards/04b.yaml", 0).update(lecture="04a", id="04a-moved"),
        "does not match file name",
    ),
    (
        "official in cards/",
        lambda t: t["files"]["cards/04a.yaml"].append(t["files"]["exams/04a.yaml"].pop(0)),
        "belong in exams/",
    ),
    (
        "missing image",
        lambda t: card(t, "exams/04a.yaml", 1)["images"][0].update(src="img/missing.png"),
        "image not found",
    ),
    ("image outside img/", lambda t: card(t, "exams/04a.yaml", 1)["images"][0].update(src="../x.png"), "under img/"),
    (
        "missing pdf",
        lambda t: card(t, "cards/04a.yaml", 0)["sources"].__setitem__(
            0, {"kind": "lecture", "pdf": "lectures/04/nope.pdf", "page": 1, "label": "x"}
        ),
        "file not found",
    ),
    (
        "page beyond count",
        lambda t: card(t, "cards/04a.yaml", 0)["sources"].__setitem__(
            0, {"kind": "lecture", "pdf": "lectures/04/lecture04a.pdf", "page": 6, "label": "x"}
        ),
        "page 6 > page count 5",
    ),
    (
        "page zero",
        lambda t: card(t, "cards/04a.yaml", 0)["sources"].__setitem__(
            0, {"kind": "lecture", "pdf": "lectures/04/lecture04a.pdf", "page": 0, "label": "x"}
        ),
        "field 'sources.0.page'",
    ),
    (
        "path traversal",
        lambda t: card(t, "cards/04a.yaml", 0)["sources"].__setitem__(
            0, {"kind": "lecture", "pdf": "lectures/../secret.txt", "page": 1, "label": "x"}
        ),
        "unsafe path",
    ),
    ("no sources", lambda t: card(t, "cards/04a.yaml", 0).update(sources=[]), "at least one source"),
    (
        "official without exam source",
        lambda t: card(t, "exams/04a.yaml", 0).update(
            sources=[{"kind": "lecture", "pdf": "lectures/04/lecture04a.pdf", "page": 1, "label": "x"}]
        ),
        "needs an exam source",
    ),
    ("leftover TODO", lambda t: card(t, "cards/04a.yaml", 0).update(back="TODO check"), "leftover TODO in back"),
    ("unbalanced dollar", lambda t: card(t, "cards/04a.yaml", 0).update(front="cost $O(N"), "unbalanced '$' in front"),
    ("unknown field", lambda t: card(t, "cards/04a.yaml", 0).update(colour="red"), "field 'colour'"),
    ("bad date", lambda t: card(t, "cards/04a.yaml", 0).update(added="yesterday"), "field 'added'"),
    ("multi on tf", lambda t: card(t, "cards/04a.yaml", 2).update(multi=True), "only applies to mcq"),
    ("course unknown tz", lambda t: t["course"].update(timezone="Mars/Olympus"), "unknown timezone"),
    (
        "course missing lecture pdf",
        lambda t: t["course"]["lectures"][0].update(pdf="lectures/04/zz.pdf"),
        "file not found",
    ),
    (
        "course duplicate lecture",
        lambda t: t["course"]["lectures"].append(dict(t["course"]["lectures"][0])),
        "duplicate lecture id",
    ),
    ("course out of order", lambda t: t["course"]["lectures"].reverse(), "course order"),
    ("index missing", lambda t: t.update(index=None), "exam-index.yaml: missing"),
    (
        "official card not added in index",
        lambda t: t["index"]["questions"][0].update(status="pending"),
        "index status is 'pending'",
    ),
    ("official card not indexed", lambda t: t["index"]["questions"].pop(1), "has no index entry"),
    (
        "index added without card",
        lambda t: t["index"]["questions"][2].update(status="added"),
        "no exam_official card 'exam-2023-q31'",
    ),
    ("index type mismatch", lambda t: t["index"]["questions"][0].update(type="mcq"), "but card 'exam-2023-q30' is tf"),
    ("index unknown area", lambda t: t["index"]["questions"][2].update(areas=["zzz"]), "unknown area 'zzz'"),
    ("index unknown lecture", lambda t: t["index"]["questions"][2].update(lectures=["99z"]), "unknown lecture '99z'"),
    ("index page too far", lambda t: t["index"]["questions"][2].update(page=9), "page 9 > page count 3"),
    ("index open not excluded", lambda t: t["index"]["questions"][3].update(status="pending"), "must be open-excluded"),
    (
        "index duplicate entry",
        lambda t: t["index"]["questions"].append(dict(t["index"]["questions"][2])),
        "duplicate entry",
    ),
    ("index duplicate without target", lambda t: t["index"]["questions"][2].update(status="duplicate"), "need same_as"),
]


@pytest.mark.parametrize("name,mutate,expected", BAD_CASES, ids=[c[0] for c in BAD_CASES])
def test_bad_fixture_fails_clearly(cfg, tree, name, mutate, expected):
    mutate(tree)
    write_content(cfg.content_dir, tree)
    with pytest.raises(ContentError) as exc:
        load_content(cfg.content_dir, cfg.repo_root)
    joined = "\n".join(exc.value.errors)
    assert expected in joined, joined


def test_mark_added_in_index(cfg, tree):
    from revision.content import mark_added_in_index

    tree["index"]["questions"][0]["status"] = "pending"
    write_content(cfg.content_dir, tree)
    assert mark_added_in_index(cfg.content_dir) == ["exam-2023-q30"]
    load_content(cfg.content_dir, cfg.repo_root)  # consistent again


def test_unlockable_exam_questions(content):
    assert [e.card_id for e in content.unlockable_exam_questions()] == ["exam-2023-q31"]


def test_yaml_syntax_error_reported(cfg):
    (cfg.content_dir / "cards" / "04a.yaml").write_text("- id: [unclosed\n")
    with pytest.raises(ContentError) as exc:
        load_content(cfg.content_dir, cfg.repo_root)
    assert "YAML parse error" in exc.value.errors[0]


def test_all_errors_reported_at_once(cfg, tree):
    card(tree, "cards/04a.yaml", 0).update(themes=["nope"])
    card(tree, "cards/04b.yaml", 0).update(back="TODO")
    write_content(cfg.content_dir, tree)
    with pytest.raises(ContentError) as exc:
        load_content(cfg.content_dir, cfg.repo_root)
    assert len(exc.value.errors) == 2


def test_long_front_is_a_warning(cfg, tree):
    card(tree, "cards/04a.yaml", 0).update(front="x" * 500)
    write_content(cfg.content_dir, tree)
    content = load_content(cfg.content_dir, cfg.repo_root)
    assert any("long front" in w for w in content.warnings)


# --------------------------------------------------------------------------- cloze


def test_cloze_braces_inside_latex():
    text = r"$\le$ {{c1::$\sqrt{\frac{(b-a)^2 \ln(2/\delta)}{2|S_\text{test}|}}$}} end"
    [s] = parse_cloze(text)
    assert s.answer == r"$\sqrt{\frac{(b-a)^2 \ln(2/\delta)}{2|S_\text{test}|}}$"
    assert text[s.end :] == " end"


def test_cloze_hint_and_escaped_braces():
    [a, b] = parse_cloze(r"{{c1::$\{x\}$::a set}} and {{c2::y}}")
    assert (a.index, a.answer, a.hint) == (1, r"$\{x\}$", "a set")
    assert (b.index, b.answer, b.hint) == (2, "y", None)


def test_cloze_same_index_twice():
    spans = parse_cloze("{{c1::a}} and {{c1::b}}")
    assert [s.index for s in spans] == [1, 1]
    assert render_cloze("{{c1::a}} and {{c1::b}}", 1, reveal=False) == "\ue000[…]\ue001 and \ue000[…]\ue001"


@pytest.mark.parametrize("bad", ["{{c1::}}", "{{c1::a::}}", "{{c1::a {{c2::b}} }}", "{{c1::a}"])
def test_cloze_errors(bad):
    with pytest.raises(ClozeError):
        parse_cloze(bad)


def test_render_cloze():
    text = "A {{c1::x::hint}} B {{c2::y}}"
    assert render_cloze(text, 1, reveal=False) == "A \ue000[hint]\ue001 B y"
    assert render_cloze(text, 1, reveal=True) == "A \ue000x\ue001 B y"
    assert render_cloze(text, 2, reveal=False) == "A x B \ue000[…]\ue001"


def test_exam_label():
    assert exam_label("exam-2023-q30") == "Final 2023 Q30"
    assert exam_label("exam-2016-q05") == "Final 2016 Q5"
    assert exam_label("mock-2017-q3b") == "Mock midterm 2017 Q3b"
    assert exam_label("04a-x") is None


def test_content_dir_missing_course(tmp_path: Path, repo):
    with pytest.raises(ContentError):
        load_content(tmp_path / "empty", repo)
