"""Card content: pydantic models, YAML loader and validator (SPEC §4).

Content lives in git under `revision/content/`:
- `course.yaml`              lecture registry + theme vocabulary
- `cards/<lecture>.yaml`     concept cards + unofficial exam-style cards
- `exams/<lecture>.yaml`     official past-exam questions

`load_content()` parses and validates everything and raises `ContentError` listing *all* problems.
"""

from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictInt, ValidationError

from revision.sources import is_allowed_path, pdf_page_count

CardType = Literal["basic", "cloze", "tf", "mcq"]
Origin = Literal["concept", "exam_official", "exam_style"]
Priority = Literal["core", "detail"]
SourceKind = Literal["lecture", "exam", "lab", "doc"]

FRONT_WARN_CHARS = 400
BACK_WARN_CHARS = 300

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$")
EXAM_FINAL_ID_RE = re.compile(r"^exam-(\d{4})-q(\d{1,2})$")
EXAM_MOCK_ID_RE = re.compile(r"^mock-(\d{4})-q(\d{1,2})([a-z]?)$")
TODO_RE = re.compile(r"\bTODO\b")


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)


# --------------------------------------------------------------------------- models


class Source(_Strict):
    kind: SourceKind
    pdf: str | None = None
    page: int | None = Field(default=None, ge=1)
    path: str | None = None  # kind=doc only: repo-relative non-PDF file (e.g. a docs/ sheet)
    label: str = Field(min_length=1)


class Image(_Strict):
    src: str = Field(min_length=1)
    alt: str = Field(min_length=1)


class Card(_Strict):
    id: str
    type: CardType
    origin: Origin
    lecture: str
    also_lectures: list[str] = Field(default_factory=list)
    themes: list[str]
    priority: Priority
    front: str = Field(min_length=1)
    back: str | None = None
    choices: list[str] | None = None
    answer: StrictBool | list[StrictInt] | None = None
    multi: bool = False
    shuffle: bool = True
    explanation: str | None = None
    trap: str | None = None
    images: list[Image] = Field(default_factory=list)
    sources: list[Source]
    added: dt.date
    notes: str | None = None


class Lecture(_Strict):
    id: str
    week: int = Field(ge=1)
    title: str
    date: dt.date | None = None
    pdf: str
    annotated_pdf: str | None = None
    sheet: str | None = None
    active: bool = True


class Theme(_Strict):
    id: str
    label: str


class Course(_Strict):
    exam_date: dt.date | None = None
    timezone: str = "Europe/Zurich"
    day_rollover_hour: int = Field(default=4, ge=0, le=23)
    lectures: list[Lecture]
    themes: list[Theme]


# --------------------------------------------------------------------------- cloze


class ClozeError(ValueError):
    pass


@dataclass(frozen=True)
class ClozeSpan:
    index: int
    answer: str
    hint: str | None
    start: int  # offset of "{{"
    end: int  # offset just after "}}"


_CLOZE_OPEN_RE = re.compile(r"\{\{c(\d+)::")


def parse_cloze(text: str) -> list[ClozeSpan]:
    """Parse `{{cN::answer}}` / `{{cN::answer::hint}}` deletions.

    Brace-aware: LaTeX inside the answer may contain `}}` (e.g. `\\frac{a}{b}}`), so the closing `}}`
    is the first one at brace depth 0. `\\{` / `\\}` are literal braces and do not change the depth.
    """
    spans: list[ClozeSpan] = []
    pos = 0
    while True:
        m = _CLOZE_OPEN_RE.search(text, pos)
        if not m:
            break
        index = int(m.group(1))
        i = m.end()
        depth = 0
        sep: int | None = None
        while True:
            if i >= len(text):
                raise ClozeError(f"unterminated cloze c{index} (missing '}}}}')")
            ch = text[i]
            if ch == "\\":
                i += 2
                continue
            if ch == "{":
                if text.startswith("{{c", i) and _CLOZE_OPEN_RE.match(text, i):
                    raise ClozeError(f"nested cloze inside c{index}")
                depth += 1
            elif ch == "}":
                if depth > 0:
                    depth -= 1
                elif text.startswith("}}", i):
                    break
                else:
                    raise ClozeError(f"unbalanced '}}' in cloze c{index}")
            elif ch == ":" and depth == 0 and sep is None and text.startswith("::", i):
                sep = i
                i += 2
                continue
            i += 1
        body_end = i
        if sep is None:
            answer, hint = text[m.end() : body_end], None
        else:
            answer, hint = text[m.end() : sep], text[sep + 2 : body_end]
        if not answer.strip():
            raise ClozeError(f"empty answer in cloze c{index}")
        if hint is not None and not hint.strip():
            raise ClozeError(f"empty hint in cloze c{index}")
        spans.append(ClozeSpan(index, answer, hint, m.start(), body_end + 2))
        pos = body_end + 2
    bounds = zip([0] + [s.end for s in spans], [s.start for s in spans] + [len(text)], strict=True)
    outside = "".join(text[a:b] for a, b in bounds)
    if "{{c" in outside:
        raise ClozeError("malformed cloze marker (expected '{{cN::answer}}' or '{{cN::answer::hint}}')")
    return spans


def cloze_indices(text: str) -> list[int]:
    return sorted({s.index for s in parse_cloze(text)})


def render_cloze(text: str, index: int, reveal: bool) -> str:
    """Markdown for the review of cloze `index`: that deletion blanked (or highlighted when revealed),
    all other deletions shown in full."""
    out: list[str] = []
    last = 0
    for s in parse_cloze(text):
        out.append(text[last : s.start])
        if s.index != index:
            out.append(s.answer)
        elif reveal:
            out.append(f"**{s.answer}**")
        else:
            out.append(f"**[{s.hint}]**" if s.hint else "**[…]**")
        last = s.end
    out.append(text[last:])
    return "".join(out)


# --------------------------------------------------------------------------- helpers


def exam_label(card_id: str) -> str | None:
    """'exam-2023-q30' -> 'Final 2023 Q30'; 'mock-2017-q3b' -> 'Mock midterm 2017 Q3b'."""
    if m := EXAM_FINAL_ID_RE.match(card_id):
        return f"Final {m.group(1)} Q{int(m.group(2))}"
    if m := EXAM_MOCK_ID_RE.match(card_id):
        return f"Mock midterm {m.group(1)} Q{int(m.group(2))}{m.group(3)}"
    return None


def exam_year(card_id: str) -> int | None:
    m = EXAM_FINAL_ID_RE.match(card_id) or EXAM_MOCK_ID_RE.match(card_id)
    return int(m.group(1)) if m else None


def card_hash(card: Card) -> str:
    payload = json.dumps(card.model_dump(mode="json"), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode()).hexdigest()[:12]


def _unbalanced_dollars(text: str) -> bool:
    return text.replace("\\$", "").count("$") % 2 == 1


def _safe_rel_path(p: str) -> bool:
    pp = PurePosixPath(p)
    return not pp.is_absolute() and ".." not in pp.parts and "\\" not in p and p.strip() == p and p != ""


# --------------------------------------------------------------------------- loaded content


@dataclass
class ItemSpec:
    item_id: str
    card_id: str
    cloze_index: int | None


@dataclass
class LoadedCard:
    card: Card
    file: str  # relative to the content dir, e.g. "cards/04a.yaml"
    position: int  # index within the file
    hash: str
    cloze: list[int] = field(default_factory=list)

    def item_specs(self) -> list[ItemSpec]:
        if self.card.type == "cloze":
            return [ItemSpec(f"{self.card.id}::c{i}", self.card.id, i) for i in self.cloze]
        return [ItemSpec(self.card.id, self.card.id, None)]


@dataclass
class Content:
    course: Course
    cards: list[LoadedCard]
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.by_id: dict[str, LoadedCard] = {c.card.id: c for c in self.cards}
        self.lectures: dict[str, Lecture] = {lec.id: lec for lec in self.course.lectures}
        self.lecture_rank: dict[str, int] = {lec.id: i for i, lec in enumerate(self.course.lectures)}
        self.themes: dict[str, Theme] = {t.id: t for t in self.course.themes}
        self.items: dict[str, tuple[LoadedCard, ItemSpec]] = {}
        for lc in self.cards:
            for spec in lc.item_specs():
                self.items[spec.item_id] = (lc, spec)

    def is_active(self, card: Card) -> bool:
        return all(self.lectures[lid].active for lid in [card.lecture, *card.also_lectures])

    def week_of(self, card: Card) -> int:
        return self.lectures[card.lecture].week

    def course_order_key(self, lc: LoadedCard) -> tuple:
        """New-card order: week -> lecture order in course.yaml -> concept before exam -> file position."""
        origin_rank = {"concept": 0, "exam_style": 1, "exam_official": 2}[lc.card.origin]
        lec = self.lectures[lc.card.lecture]
        return (lec.week, self.lecture_rank[lec.id], origin_rank, lc.file, lc.position)


class ContentError(Exception):
    def __init__(self, errors: list[str], warnings: list[str] | None = None):
        self.errors = errors
        self.warnings = warnings or []
        super().__init__("\n".join(errors))


# --------------------------------------------------------------------------- loading / validation


def _fmt_pydantic(prefix: str, e: ValidationError) -> list[str]:
    out: list[str] = []
    for err in e.errors():
        if err["loc"] and err["loc"][0] == "answer":  # union bool | list[int]: one readable message
            msg = f"{prefix}: field 'answer': must be true/false (tf) or a list of 0-based choice indices (mcq)"
        else:
            loc = ".".join(str(x) for x in err["loc"]) or "(root)"
            msg = f"{prefix}: field '{loc}': {err['msg']}"
        if msg not in out:
            out.append(msg)
    return out


def _read_yaml(path: Path, rel: str, errors: list[str]):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        errors.append(f"{rel}: YAML parse error: {e}")
    except OSError as e:
        errors.append(f"{rel}: cannot read: {e}")
    return None


class _Validator:
    def __init__(self, repo_root: Path, content_dir: Path):
        self.repo_root = repo_root
        self.content_dir = content_dir
        self.errors: list[str] = []
        self.warnings: list[str] = []

    # -- files
    def check_repo_file(self, where: str, rel: str, *, pdf: bool) -> int | None:
        """Check a repo-relative path; return the PDF page count when `pdf`."""
        if not _safe_rel_path(rel):
            self.errors.append(f"{where}: unsafe path '{rel}' (must be repo-relative, no '..')")
            return None
        full = self.repo_root / rel
        if not full.is_file():
            self.errors.append(f"{where}: file not found: {rel}")
            return None
        if not pdf:
            return None
        if not rel.lower().endswith(".pdf"):
            self.errors.append(f"{where}: '{rel}' is not a PDF")
            return None
        if not is_allowed_path(rel):
            self.errors.append(f"{where}: '{rel}' is outside the source-viewer whitelist")
        try:
            return pdf_page_count(full)
        except Exception as e:  # pdfium raises its own error types
            self.errors.append(f"{where}: cannot open PDF '{rel}': {e}")
            return None

    # -- course
    def check_course(self) -> Course | None:
        rel = "course.yaml"
        raw = _read_yaml(self.content_dir / rel, rel, self.errors)
        if raw is None:
            if not self.errors:
                self.errors.append(f"{rel}: missing or empty")
            return None
        try:
            course = Course.model_validate(raw)
        except ValidationError as e:
            self.errors.extend(_fmt_pydantic(rel, e))
            return None
        try:
            ZoneInfo(course.timezone)
        except (ZoneInfoNotFoundError, ValueError):
            self.errors.append(f"{rel}: unknown timezone '{course.timezone}'")
        seen: set[str] = set()
        for lec in course.lectures:
            where = f"{rel}: lecture '{lec.id}'"
            if lec.id in seen:
                self.errors.append(f"{where}: duplicate lecture id")
            seen.add(lec.id)
            self.check_repo_file(where, lec.pdf, pdf=True)
            if lec.annotated_pdf:
                self.check_repo_file(where, lec.annotated_pdf, pdf=True)
            if lec.sheet:
                self.check_repo_file(where, lec.sheet, pdf=False)
        weeks = [lec.week for lec in course.lectures]
        if weeks != sorted(weeks):
            self.errors.append(f"{rel}: lectures must be listed in course order (weeks non-decreasing)")
        seen = set()
        for t in course.themes:
            if t.id in seen:
                self.errors.append(f"{rel}: duplicate theme id '{t.id}'")
            if not ID_RE.match(t.id):
                self.errors.append(f"{rel}: theme id '{t.id}' must be lowercase kebab-case")
            seen.add(t.id)
        return course

    # -- cards
    def check_card(self, card: Card, rel: str, course: Course) -> list[int]:
        where = f"{rel}: card '{card.id}'"
        err = self.errors.append
        lectures = {lec.id for lec in course.lectures}
        themes = {t.id for t in course.themes}
        stem = PurePosixPath(rel).stem
        folder = PurePosixPath(rel).parts[0]

        # id conventions
        if not ID_RE.match(card.id):
            err(f"{where}: id must be lowercase kebab-case ([a-z0-9-])")
        if card.origin == "exam_official":
            if not (EXAM_FINAL_ID_RE.match(card.id) or EXAM_MOCK_ID_RE.match(card.id)):
                err(f"{where}: official exam ids are 'exam-<year>-q<N>' or 'mock-<year>-q<N>[sub]'")
        elif card.origin == "exam_style":
            if not card.id.startswith(f"style-{card.lecture}-"):
                err(f"{where}: unofficial exam-style ids must start with 'style-{card.lecture}-'")
        elif not card.id.startswith(f"{card.lecture}-"):
            err(f"{where}: concept card ids must start with '{card.lecture}-'")

        # placement
        if card.lecture != stem:
            err(f"{where}: lecture '{card.lecture}' does not match file name '{stem}.yaml'")
        if card.origin == "exam_official" and folder != "exams":
            err(f"{where}: official exam questions belong in exams/")
        if card.origin != "exam_official" and folder != "cards":
            err(f"{where}: only official exam questions belong in exams/")

        # references
        for lid in [card.lecture, *card.also_lectures]:
            if lid not in lectures:
                err(f"{where}: unknown lecture '{lid}' (not in course.yaml)")
        if card.lecture in card.also_lectures:
            err(f"{where}: also_lectures repeats the primary lecture")
        if not card.themes:
            err(f"{where}: needs at least one theme")
        for t in card.themes:
            if t not in themes:
                err(f"{where}: unknown theme '{t}' (add it to course.yaml themes)")

        # per type / origin
        cloze: list[int] = []
        if card.origin == "exam_official" and card.type not in ("tf", "mcq"):
            err(f"{where}: exam_official cards must be tf or mcq")
        if card.origin in ("exam_official", "exam_style") and not (card.explanation or "").strip():
            err(f"{where}: exam cards require an explanation")
        if card.type == "basic":
            if not (card.back or "").strip():
                err(f"{where}: basic card requires 'back'")
            self._forbid(where, card, "choices", "answer")
        elif card.type == "cloze":
            self._forbid(where, card, "back", "choices", "answer")
            try:
                spans = parse_cloze(card.front)
            except ClozeError as e:
                err(f"{where}: {e}")
            else:
                cloze = sorted({s.index for s in spans})
                if not cloze:
                    err(f"{where}: cloze card has no '{{{{c1::...}}}}' deletion")
                elif cloze != list(range(1, len(cloze) + 1)):
                    err(f"{where}: cloze numbering must start at c1 without gaps (found {cloze})")
                for s in spans:
                    if _unbalanced_dollars(s.answer):
                        err(f"{where}: cloze c{s.index} answer has unbalanced '$' (wrap whole math spans)")
        elif card.type == "tf":
            self._forbid(where, card, "back", "choices")
            if not isinstance(card.answer, bool):
                err(f"{where}: tf card requires 'answer: true|false'")
        elif card.type == "mcq":
            self._forbid(where, card, "back")
            n = len(card.choices or [])
            if not 2 <= n <= 6:
                err(f"{where}: mcq needs 2–6 choices (got {n})")
            if not isinstance(card.answer, list) or not card.answer:
                err(f"{where}: mcq requires 'answer' = non-empty list of 0-based choice indices")
            else:
                if any(not 0 <= a < n for a in card.answer):
                    err(f"{where}: mcq answer index out of range 0..{n - 1}: {card.answer}")
                if len(set(card.answer)) != len(card.answer):
                    err(f"{where}: mcq answer has duplicate indices")
                if not card.multi and len(card.answer) != 1:
                    err(f"{where}: single-answer mcq must have exactly one answer (or set multi: true)")
            if card.choices and len(set(card.choices)) != len(card.choices):
                err(f"{where}: duplicate choices")
        if card.type not in ("mcq",):
            if card.multi:
                err(f"{where}: 'multi' only applies to mcq")
            if not card.shuffle:
                err(f"{where}: 'shuffle' only applies to mcq")

        # shown text: TODO, $ balance, length
        shown = {"front": card.front, "back": card.back, "explanation": card.explanation, "trap": card.trap}
        for i, ch in enumerate(card.choices or []):
            shown[f"choices[{i}]"] = ch
        for i, im in enumerate(card.images):
            shown[f"images[{i}].alt"] = im.alt
        for name, text in shown.items():
            if text is None:
                continue
            if TODO_RE.search(text):
                err(f"{where}: leftover TODO in {name}")
            if _unbalanced_dollars(text):
                err(f"{where}: unbalanced '$' in {name}")
            if not text.strip():
                err(f"{where}: empty {name}")
        # official stems are verbatim: their length is not ours to fix
        if card.origin != "exam_official" and len(card.front) > FRONT_WARN_CHARS:
            self.warnings.append(f"{where}: long front ({len(card.front)} chars > {FRONT_WARN_CHARS})")
        if card.back and len(card.back) > BACK_WARN_CHARS:
            self.warnings.append(f"{where}: long back ({len(card.back)} chars > {BACK_WARN_CHARS})")

        # images
        for im in card.images:
            if not _safe_rel_path(im.src) or not im.src.startswith("img/"):
                err(f"{where}: image path '{im.src}' must be relative to content/ and under img/")
            elif not (self.content_dir / im.src).is_file():
                err(f"{where}: image not found: {im.src}")

        # sources
        if not card.sources:
            err(f"{where}: needs at least one source")
        for i, s in enumerate(card.sources):
            sw = f"{where}: sources[{i}]"
            if s.kind == "doc":
                if s.pdf is not None or s.page is not None:
                    err(f"{sw}: doc sources use 'path', not 'pdf'/'page'")
                if not s.path:
                    err(f"{sw}: doc source requires 'path'")
                else:
                    self.check_repo_file(sw, s.path, pdf=False)
                continue
            if s.path is not None:
                err(f"{sw}: 'path' is only for doc sources")
            if not s.pdf or s.page is None:
                err(f"{sw}: {s.kind} source requires 'pdf' and 'page'")
                continue
            if s.kind == "exam" and not s.pdf.startswith("exam/"):
                err(f"{sw}: exam source must point into exam/")
            if s.kind == "lecture" and not s.pdf.startswith("lectures/"):
                err(f"{sw}: lecture source must point into lectures/")
            n_pages = self.check_repo_file(sw, s.pdf, pdf=True)
            if n_pages is not None and s.page > n_pages:
                err(f"{sw}: page {s.page} > page count {n_pages} of {s.pdf}")
        if card.origin == "exam_official" and not any(s.kind == "exam" for s in card.sources):
            err(f"{where}: official exam card needs an exam source")
        return cloze

    def _forbid(self, where: str, card: Card, *names: str) -> None:
        for n in names:
            if getattr(card, n) is not None:
                self.errors.append(f"{where}: field '{n}' is not allowed for type {card.type}")

    def load_cards(self, course: Course) -> list[LoadedCard]:
        loaded: list[LoadedCard] = []
        seen: dict[str, str] = {}
        for folder in ("cards", "exams"):
            d = self.content_dir / folder
            if not d.is_dir():
                continue
            for path in sorted(d.iterdir()):
                if path.name.startswith("."):
                    continue
                rel = f"{folder}/{path.name}"
                if path.suffix != ".yaml":
                    self.errors.append(f"{rel}: card files must end in .yaml")
                    continue
                raw = _read_yaml(path, rel, self.errors)
                if raw is None:
                    continue
                if not isinstance(raw, list):
                    self.errors.append(f"{rel}: must be a YAML list of cards")
                    continue
                for pos, entry in enumerate(raw):
                    cid = entry.get("id", f"#{pos}") if isinstance(entry, dict) else f"#{pos}"
                    try:
                        card = Card.model_validate(entry)
                    except ValidationError as e:
                        self.errors.extend(_fmt_pydantic(f"{rel}: card '{cid}'", e))
                        continue
                    if card.id in seen:
                        self.errors.append(f"{rel}: card '{card.id}': duplicate id (also in {seen[card.id]})")
                        continue
                    seen[card.id] = rel
                    cloze = self.check_card(card, rel, course)
                    loaded.append(LoadedCard(card, rel, pos, card_hash(card), cloze))
        return loaded


def load_content(content_dir: Path, repo_root: Path) -> Content:
    """Load and validate all content. Raises ContentError (with every error found) on failure."""
    v = _Validator(repo_root, content_dir)
    course = v.check_course()
    if course is None:
        raise ContentError(v.errors, v.warnings)
    cards = v.load_cards(course)
    if v.errors:
        raise ContentError(v.errors, v.warnings)
    return Content(course=course, cards=cards, warnings=v.warnings)
