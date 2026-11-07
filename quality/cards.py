"""The dimension cards (spec 131 FR-1, FR-1a, FR-1b): `quality/readers/dimensions.md`, read.

One card per dimension of keel-cloud's registry, thirteen, each between its two markers
(`<!-- card:<key>:begin -->` ... `<!-- card:<key>:end -->`). This module is how the rest of the repository reads them:

- `card(key)` -- the whole card between its markers, as the readers are sent it (FR-2: after the persona, before the
  screen, on every screen whose dimension is set) and the adviser is handed it for the row it advises (FR-4);
  `card_for(dimension)` the same, or None where the screen has no dimension or the registry no such row;
- `keys()` -- the cards' keys, in the file's order (the registry's);
- the card's labelled lines, read for the test that holds every card to its registry row (FR-1b,
  `tests/test_dimension_cards_131.py`): `registry_line`, `meaning`, `section`, `sides` (the **For** / **Against** /
  **Neither** lines by code), `escape_line`, `fixed_answer_codes`, `codes`.

The cards are hand-written and reviewed by the founder; nothing here writes them. When the registry moves, the card
moves in the same commit, and the test says which.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

CARDS_PATH = Path(__file__).resolve().parent / "readers" / "dimensions.md"

_BEGIN = re.compile(r"<!-- card:([a-z_.]+):begin -->")
_CODE = re.compile(r"`([a-z][a-z0-9_]*)`")
#: A range of positional codes said in words: `outcome_3` to `outcome_5`.
_RANGE = re.compile(r"`([a-z_]+?)_(\d+)` to `\1_(\d+)`")
_BOLD_LABEL = re.compile(r"\*\*([^*]+?):\*\*")


class CardError(ValueError):
    """The cards file is not what this module reads (a missing marker, a card twice, a section missing)."""


def cards_text(path: Path | None = None) -> str:
    path = Path(path) if path else CARDS_PATH
    if not path.is_file():
        raise CardError(f"no dimension cards at {path} (spec 131 FR-1)")
    return path.read_text(encoding="utf-8")


def keys(text: str | None = None) -> list[str]:
    """Every card's key, in the file's order."""
    return _BEGIN.findall(text if text is not None else cards_text())


def card(key: str, text: str | None = None) -> str:
    """The whole card of `key`: the text between its two markers, stripped -- what a reader and the adviser are sent."""
    text = text if text is not None else cards_text()
    begin, end = f"<!-- card:{key}:begin -->", f"<!-- card:{key}:end -->"
    if text.count(begin) != 1 or text.count(end) != 1 or text.index(begin) > text.index(end):
        raise CardError(f"quality/readers/dimensions.md must carry one `card:{key}:begin` marker and one "
                        f"`card:{key}:end` after it (spec 131 FR-1)")
    return text.split(begin, 1)[1].split(end, 1)[0].strip()


def card_for(dimension: str | None, text: str | None = None) -> str | None:
    """The card a screen of `dimension` is sent (FR-2), or None: a screen with no dimension (context, idea, send, the
    stage page, the Insights screen) gets none, and so does a dimension no card names."""
    if not dimension:
        return None
    text = text if text is not None else cards_text()
    return card(dimension, text) if dimension in keys(text) else None


#: Spec 144 FR-3: the suffix of a Check's second founder shot, taken after the review's band (`check-{dim}-reviewed`,
#: `harness/vectors_screens.REVIEWED_SUFFIX`) -- a screen of its dimension, sent that dimension's card.
REVIEWED_SUFFIX = "-reviewed"


def fold_reviewed(dimension: str | None) -> str | None:
    """Spec 144 FR-3: a screen's dimension with the second shot's suffix taken off (`problem.importance-reviewed` ->
    `problem.importance`), so the reviewed Check is read, carded and tabled as its dimension's; as given otherwise."""
    if isinstance(dimension, str) and dimension.endswith(REVIEWED_SUFFIX):
        return dimension[: -len(REVIEWED_SUFFIX)]
    return dimension


def card_sha(key: str, text: str | None = None) -> str:
    """The sha256 of one card as sent -- what a score file can name beside the key."""
    return hashlib.sha256(card(key, text).encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------------------- the labelled lines

def registry_line(body: str) -> str:
    """The card's **Registry:** line, whole (to its **Screens:** line), one space between words."""
    match = re.search(r"\*\*Registry:\*\*(.*?)\*\*Screens:\*\*", body, re.S)
    if not match:
        raise CardError("a card without its **Registry:** line")
    return " ".join(match.group(1).split())


def section(body: str, number: int) -> str:
    """Section `number` of a card (`#### 1. What it measures` ... `#### 6. Pitfalls ...`), whole to the next `#### `."""
    match = re.search(rf"^#### {number}\.[^\n]*$", body, re.M)
    if not match:
        raise CardError(f"a card without its section {number}")
    rest = body[match.end():]
    stop = re.search(r"^#### ", rest, re.M)
    return rest[:stop.start() if stop else len(rest)].strip()


def meaning(body: str) -> str:
    """Section 1, *What it measures*: the registry's `meaning`, one line."""
    return " ".join(section(body, 1).split())


def codes(text: str) -> list[str]:
    """The registry codes a stretch of card text carries in backticks, in order; a positional range said in words
    (`outcome_3` to `outcome_5`) read as every code in it."""
    text = _RANGE.sub(lambda m: " ".join(f"`{m.group(1)}_{i}`" for i in range(int(m.group(2)), int(m.group(3)) + 1)),
                      text)
    return _CODE.findall(text)


def _bullets(text: str) -> list[str]:
    out: list[str] = []
    for line in text.splitlines():
        if line.startswith("- "):
            out.append(line[2:])
        elif out and line.startswith("  "):
            out[-1] += " " + line.strip()
    return out


def sides(body: str) -> dict:
    """Section 3's **For** / **Against** / **Neither** lines, by code: `{(variant, side): [codes]}`. A bullet's bold
    labels say the side (*For*, *Against*, *Neither*) and the variant -- what the label names beside the side (*A role
    tested*, *(budget, business)*, *(budget, consumer)*); a label that names no side keeps the one before it (Ability
    to pay's *(budget, consumer)* after its *For (budget, business)*), and a label that names only its side keeps the
    variant before it in the bullet (Buyer and payer's *Against:* after *A role tested -- For:*). The variant of a plain
    **For:** (and of Current solution's **For the belief:**) is `''`."""
    out: dict = {}
    for bullet in _bullets(section(body, 3)):
        labels = list(_BOLD_LABEL.finditer(bullet))
        if not labels or not re.search(r"\b(For|Against|Neither)\b", labels[0].group(1)):
            continue
        side, variant = None, ""
        for i, label in enumerate(labels):
            name = label.group(1)
            found = re.search(r"\b(For|Against|Neither)\b", name)
            if found:
                side = found.group(1).lower()
                named = re.sub(r"\b(For|Against|Neither)\b", "", name).replace("--", " ")
                named = " ".join(re.sub(r"^\s*the belief\b", "", named).split()).strip()
                variant = named or (variant if i else "")      # *Against:* after *A role tested -- For:* is its own
            else:
                variant = " ".join(name.split())
            if "/" in name and side:                      # *For / against on the derived readings*: no codes
                side = None
            stop = labels[i + 1].start() if i + 1 < len(labels) else len(bullet)
            if side:
                out.setdefault((variant, side), []).extend(codes(bullet[label.end():stop]))
    return out


def escape_line(body: str) -> str:
    """Section 4's **Escape:** line, whole, one space between words."""
    match = re.search(r"\*\*Escape:\*\*(.*)", section(body, 4), re.S)
    if not match:
        raise CardError("a card without its **Escape:** line")
    return " ".join(match.group(1).split())


def fixed_answer_codes(body: str) -> list[str]:
    """The codes of the card's **Fixed answers** line (section 2), in order -- its bullet whole, up to the escape the
    line names after them (*then the escape*, *Then *I can't tell**); `[]` where the card names none."""
    for bullet in _bullets(section(body, 2)):
        at = bullet.find("**Fixed answers")
        if at < 0:
            continue
        said = bullet[at:]
        said = re.split(r"[;.]\s+[Tt]hen\b", said, maxsplit=1)[0]
        return list(dict.fromkeys(codes(said)))           # a code said again under a sub-bullet is the same answer
    return []
