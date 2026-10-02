"""Shared fixtures: a tiny fake course repo (PDFs + content) built in tmp_path, and a controllable clock."""

from __future__ import annotations

import copy
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pypdfium2 as pdfium
import pytest
import yaml

from revision.config import Config
from revision.content import load_content
from revision.db import open_db, sync_items

T0 = datetime(2026, 10, 5, 8, 0, tzinfo=UTC)  # Monday 10:00 Europe/Zurich


def make_pdf(path: Path, pages: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = pdfium.PdfDocument.new()
    for _ in range(pages):
        doc.new_page(200, 150)
    doc.save(str(path))
    doc.close()


SRC_LEC = {"kind": "lecture", "pdf": "lectures/04/lecture04a.pdf", "page": 3, "label": "04a slide 3"}
SRC_EXAM = {"kind": "exam", "pdf": "exam/final-exam-2023-solutions.pdf", "page": 2, "label": "Final 2023 Q30"}


def good_content() -> dict:
    """A valid content tree: {"course": {...}, "files": {"cards/04a.yaml": [...], ...}}."""
    course = {
        "exam_date": None,
        "timezone": "Europe/Zurich",
        "day_rollover_hour": 4,
        "lectures": [
            {"id": "04a", "week": 4, "title": "Generalization", "pdf": "lectures/04/lecture04a.pdf"},
            {"id": "04b", "week": 4, "title": "Bias-variance", "pdf": "lectures/04/lecture04b.pdf"},
            {"id": "05a", "week": 5, "title": "Classification", "pdf": "lectures/05/lecture05a.pdf", "active": False},
        ],
        "themes": [
            {"id": "generalization", "label": "Generalization"},
            {"id": "bias-variance", "label": "BV"},
            {"id": "classification", "label": "Classification"},
        ],
    }
    base = {"themes": ["generalization"], "priority": "core", "sources": [SRC_LEC], "added": "2026-10-02"}
    cards_04a = [
        {
            **base,
            "id": "04a-basic",
            "type": "basic",
            "origin": "concept",
            "lecture": "04a",
            "front": "What is $L_\\mathcal{D}(f)$?",
            "back": "The true risk.",
        },
        {
            **base,
            "id": "04a-cloze",
            "type": "cloze",
            "origin": "concept",
            "lecture": "04a",
            "priority": "detail",
            "front": "Bound: {{c1::$\\sqrt{\\frac{(b-a)^2 \\ln(2/\\delta)}{2|S|}}$}}, "
            "rate {{c2::$O(1/\\sqrt{N})$::rate}}.",
        },
        {
            **base,
            "id": "04a-tf",
            "type": "tf",
            "origin": "concept",
            "lecture": "04a",
            "front": "Training error is optimistic.",
            "answer": True,
        },
        {
            **base,
            "id": "style-04a-k",
            "type": "tf",
            "origin": "exam_style",
            "lecture": "04a",
            "front": "Cost of K models grows like $\\sqrt{K}$.",
            "answer": False,
            "explanation": "Only ln K.",
            "trap": "ln K",
        },
        {
            **base,
            "id": "04a-multi",
            "type": "mcq",
            "origin": "concept",
            "lecture": "04a",
            "multi": True,
            "front": "Which are hyperparameters?",
            "choices": ["$\\lambda$", "degree $d$", "$w$"],
            "answer": [0, 1],
        },
        {
            **base,
            "id": "04a-needs-05a",
            "type": "basic",
            "origin": "concept",
            "lecture": "04a",
            "also_lectures": ["05a"],
            "front": "Cross-lecture card",
            "back": "inactive until 05a is active",
        },
    ]
    exams_04a = [
        {
            **base,
            "id": "exam-2023-q30",
            "type": "tf",
            "origin": "exam_official",
            "lecture": "04a",
            "front": "Hoeffding bounds the training error.",
            "answer": False,
            "explanation": "Test error only.",
            "sources": [SRC_EXAM, SRC_LEC],
        },
        {
            **base,
            "id": "exam-2025-q24",
            "type": "mcq",
            "origin": "exam_official",
            "lecture": "04a",
            "themes": ["generalization"],
            "front": "5 lambdas x 5 folds?",
            "choices": ["25", "1", "5", "10"],
            "answer": [0],
            "explanation": "5 x 5.",
            "sources": [SRC_EXAM],
            "images": [{"src": "img/exam-2025-q24.png", "alt": "a figure"}],
        },
    ]
    cards_04b = [
        {
            **base,
            "id": "04b-noise",
            "type": "basic",
            "origin": "concept",
            "lecture": "04b",
            "themes": ["bias-variance"],
            "front": "Which term is independent of the algorithm?",
            "back": "Noise.",
        },
    ]
    cards_05a = [
        {
            **base,
            "id": "05a-x",
            "type": "basic",
            "origin": "concept",
            "lecture": "05a",
            "themes": ["classification"],
            "front": "Inactive lecture card",
            "back": "hidden",
        },
    ]
    index = {
        "areas": {"generalization": "04a", "cv": "04a"},
        "questions": [
            {
                "exam": "final-2023",
                "q": "30",
                "type": "tf",
                "topic": "Hoeffding",
                "areas": ["generalization"],
                "lectures": ["04a"],
                "status": "added",
                "page": 2,
            },
            {
                "exam": "final-2025",
                "q": "24",
                "type": "mcq",
                "topic": "CV cost",
                "areas": ["cv"],
                "lectures": ["04a"],
                "status": "added",
                "page": 1,
            },
            {
                "exam": "final-2023",
                "q": "31",
                "type": "tf",
                "topic": "selection",
                "areas": ["generalization"],
                "lectures": ["04a"],
                "status": "pending",
                "page": 3,
            },
            {
                "exam": "final-2023",
                "q": "40",
                "type": "open",
                "topic": "open",
                "areas": [],
                "status": "open-excluded",
                "page": 3,
            },
        ],
    }
    return {
        "course": course,
        "index": index,
        "files": {
            "cards/04a.yaml": cards_04a,
            "exams/04a.yaml": exams_04a,
            "cards/04b.yaml": cards_04b,
            "cards/05a.yaml": cards_05a,
        },
    }


def write_content(content_dir: Path, tree: dict) -> None:
    for sub in ("cards", "exams"):
        d = content_dir / sub
        d.mkdir(parents=True, exist_ok=True)
        for f in d.glob("*.yaml"):
            f.unlink()
    (content_dir / "course.yaml").write_text(yaml.safe_dump(tree["course"], sort_keys=False, allow_unicode=True))
    idx = content_dir / "exam-index.yaml"
    if tree.get("index") is None:
        idx.unlink(missing_ok=True)
    else:
        idx.write_text(yaml.safe_dump(tree["index"], sort_keys=False, allow_unicode=True))
    for rel, cards in tree["files"].items():
        (content_dir / rel).write_text(yaml.safe_dump(cards, sort_keys=False, allow_unicode=True))


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    make_pdf(root / "lectures/04/lecture04a.pdf", 5)
    make_pdf(root / "lectures/04/lecture04b.pdf", 4)
    make_pdf(root / "lectures/05/lecture05a.pdf", 4)
    make_pdf(root / "exam/final-exam-2023-solutions.pdf", 3)
    make_pdf(root / "exam/final-exam-2025-solutions.pdf", 2)
    make_pdf(root / "labs/ex04/exercise04.pdf", 1)
    (root / "secret.txt").write_text("not served")
    img = root / "revision/content/img/exam-2025-q24.png"
    img.parent.mkdir(parents=True, exist_ok=True)
    from PIL import Image

    Image.new("RGB", (4, 4), "white").save(img)
    write_content(root / "revision/content", good_content())
    return root


@pytest.fixture
def cfg(repo: Path, tmp_path: Path) -> Config:
    return Config(
        repo_root=repo,
        content_dir=repo / "revision/content",
        data_dir=tmp_path / "data",
        frontend_dist=tmp_path / "no-dist",
    )


@pytest.fixture
def content(cfg: Config):
    return load_content(cfg.content_dir, cfg.repo_root)


class Clock:
    def __init__(self, now: datetime = T0):
        self.now = now

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kw) -> datetime:
        self.now += timedelta(**kw)
        return self.now


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def conn(cfg: Config, content, clock):
    cfg.ensure_dirs()
    c = open_db(cfg.db_path)
    sync_items(c, content, clock())
    yield c
    c.close()


@pytest.fixture
def tree() -> dict:
    return copy.deepcopy(good_content())
