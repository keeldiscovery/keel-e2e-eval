"""The founder types like a person (spec 126): deterministic typos in the founder's typed texts, and the leak check.

The founder, 2026-11-01: *"A normal human being will have a lot of errors, especially typos, when they write their
problem statement ... If the person introduces typos while they are writing the problem statement, it should not
percolate to the respondent's question."* keel-cloud 195 (*spelling corrected, words kept*) is the product's answer;
this module makes the quality cycle test it on every entry, every cycle.

- **FR-1 the typist** -- `typos(text, seed)` -> `(typed, [Typo])`: about one typo every twelve words and at least one in
  any field of four words or more, deterministic from `seed` (`"<entry id>:<field>"`, hashed; no `random`). The kinds
  are the ones people make: an adjacent transposition (*every* -> *evrey*), a dropped letter (*without* -> *withot*),
  a doubled letter (*running* -> *runnning*), the ie / ei swap where the word has one (*receive* -> *recieve*). Only a
  lower-case word of five letters or more with no digit is typed wrong; **never its first letter** (keel-cloud 195's
  guard), one edit a word, never a capitalised word, a currency or a unit, a word of the entry's idea name or offer name
  (`keep`) -- the corpus records no `product_words` or brand list, so the idea name, the offer name and the short name
  stand for it --, and never a typed form that is itself a word of the entry's own material (`avoid`: it would read
  as that word, not as a typo). Every typo is one `instructions.spelling.same_word` reads as its word. Punctuation and
  spacing are kept.
- **FR-2 where the founder types** -- `type_founder(entry, founder)`: `FounderInputs`' `problem_seed`, `solution_seed`
  and the four `context_fields`; nothing else (the project name, the idea name, the decider, the calibration answers and
  the window are typed as recorded). Wired into the quality walk only (`make backtest TYPOS=1`, which `make
  quality-walk` passes unless `TYPOS=0`); a golden journey, `make gallery` and a plain `make backtest` never type one.
- **FR-3 the leak check** -- `leaks(bundle, typed)`: every served text the walk already captured in `backtest.json`
  (the founder's screens less what he typed on them, the respondents' served interviews and drawn screens, the screens
  after the answers, the report) searched for each typed form as a whole word, case-insensitively. A hit is a leak
  `{screen, field, meant, typed, text}`; a served text that spells the word right is the expected outcome and is not
  reported. The walk never stops on a leak and never retypes: the leak is the finding.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import replace
from typing import NamedTuple

from instructions import spelling

#: The founder's typed fields the typist types through, in the order the founder types them.
CONTEXT_FIELDS = ("actor", "job", "circumstance", "segment")
FIELDS = (*CONTEXT_FIELDS, "problem_seed", "solution_seed")
#: One typo about every twelve words.
WORDS_PER_TYPO = 12
#: A field of this many words or more carries at least one typo.
AT_LEAST_ONE_FROM = 4
#: Words under five letters are never typed wrong.
MIN_LETTERS = 5
KINDS = ("transposed", "dropped", "doubled", "ie/ei")
#: Currencies and units stand as typed: a number's word is never a typo (keel-cloud 195: a number is never corrected).
UNITS = frozenset("""
    dollar dollars euro euros pound pounds pence cents rupee rupees franc francs krona kronor kroner rand reais
    percent percentage
    second seconds minute minutes hours weeks month months years quarter quarters nights shifts
    meter meters metre metres kilometer kilometers kilometre kilometres miles grams kilogram kilograms kilos
    liter liters litre litres tonne tonnes pounds ounces gallons inches
""".split())
_VOWELS = set("aeiou")
#: A token of the founder's text: letters, with an inner apostrophe or hyphen (*hotel's*, *seven-figure*), or a run of
#: anything else that holds a digit or a currency sign. Only a plain lower-case run of letters is ever typed wrong.
_TOKEN = re.compile(r"[^\W\d_]+(?:['’\-][^\W\d_]+)*|\S*\d\S*")
_PLAIN = re.compile(r"^[a-z]+$")


class Typo(NamedTuple):
    """One typo: the word the founder meant, as he typed it, and how."""
    meant: str
    typed: str
    kind: str


def _hash(*parts) -> int:
    return int.from_bytes(hashlib.sha256("\x1f".join(str(p) for p in parts).encode("utf-8")).digest()[:8], "big")


def word_count(text: str) -> int:
    return len(str(text or "").split())


def owed(text: str) -> int:
    """How many typos a field of `text` is owed: about one every twelve words, at least one from four words."""
    n = word_count(text)
    if n < AT_LEAST_ONE_FROM:
        return 0
    return max(1, int(n / WORDS_PER_TYPO + 0.5))


def _words_of(*texts) -> set[str]:
    return {w.lower() for t in texts for w in re.findall(r"[^\W\d_]+", str(t or ""))}


def typeable(word: str, *, keep=frozenset()) -> bool:
    """Whether `word` may be typed wrong: plain lower-case letters, five or more, no unit or currency, not kept."""
    return (bool(_PLAIN.match(word)) and len(word) >= MIN_LETTERS and word not in UNITS
            and word not in keep)


def edits(word: str) -> list[tuple[str, str]]:
    """Every one-edit typo of `word` the typist makes, `(kind, typed)`, in a fixed order -- the first letter never
    touched. The ie / ei swap alone where the word carries one."""
    out = []
    for i in range(1, len(word) - 1):
        if word[i:i + 2] in ("ie", "ei"):
            out.append(("ie/ei", word[:i] + word[i + 1] + word[i] + word[i + 2:]))
    if out:
        return out
    for i in range(1, len(word) - 1):                          # an adjacent transposition, never the first letter
        if word[i] != word[i + 1]:
            out.append(("transposed", word[:i] + word[i + 1] + word[i] + word[i + 2:]))
    for i in range(1, len(word) - 1):                          # a dropped inner letter
        out.append(("dropped", word[:i] + word[i + 1:]))
    for i in range(1, len(word)):                              # a doubled consonant
        if word[i] not in _VOWELS:
            out.append(("doubled", word[:i + 1] + word[i] + word[i + 1:]))
    seen, kept = set(), []
    for kind, typed in out:
        if typed != word and typed not in seen:
            seen.add(typed)
            kept.append((kind, typed))
    return kept


def typos(text: str, seed: str, *, keep=frozenset(), avoid=frozenset()) -> tuple[str, list[Typo]]:
    """FR-1: `text` as the founder types it, and its typos -- deterministic from `seed`. `keep` are words never typed
    wrong (the entry's names); `avoid` are words a typo must never land on (the entry's own material, and the text's)."""
    text = str(text or "")
    keep = frozenset(w.lower() for w in keep)
    avoid = frozenset(w.lower() for w in avoid) | _words_of(text)
    tokens = list(_TOKEN.finditer(text))
    candidates = [(i, m) for i, m in enumerate(tokens) if typeable(m.group(0), keep=keep)]
    want = owed(text)
    order = sorted(candidates, key=lambda c: (_hash(seed, "word", c[0], c[1].group(0)), c[0]))
    chosen: dict[int, Typo] = {}
    for i, m in order:
        if len(chosen) >= want:
            break
        word = m.group(0)
        options = [(k, t) for k, t in edits(word) if t not in avoid and spelling.same_word(word, t)]
        if not options:
            continue
        kinds = sorted({k for k, _ in options}, key=KINDS.index)
        kind = kinds[_hash(seed, "kind", i, word) % len(kinds)]
        of_kind = [t for k, t in options if k == kind]
        chosen[i] = Typo(word, of_kind[_hash(seed, "where", i, word) % len(of_kind)], kind)
    out, at = [], 0
    for i, m in enumerate(tokens):
        if i in chosen:
            out += [text[at:m.start()], chosen[i].typed]
            at = m.end()
    out.append(text[at:])
    return "".join(out), [chosen[i] for i in sorted(chosen)]


def marked(text: str, typed: list[Typo]) -> str:
    """The typed text with each typo marked, `withot[without]` -- the DRY run's line."""
    text, out, at = str(text or ""), [], 0
    for t in typed:                                         # in text order: each mark after the one before it
        m = re.compile(rf"(?<![^\W\d_]){re.escape(t.typed)}(?![^\W\d_])").search(text, at)
        if m is None:
            continue
        out += [text[at:m.start()], f"{t.typed}[{t.meant}]"]
        at = m.end()
    return "".join(out) + text[at:]


# ------------------------------------------------------------------------------------------------ FR-2 the founder

def kept_words(entry) -> frozenset:
    """The words that stand as typed by design: the idea name the founder types, the offer name and the short name (the
    corpus records no `product_words` or brand list; these are the entry's names)."""
    from harness import vectors_script as vs                                # noqa: PLC0415
    names = [getattr(entry, "idea_name", None), (getattr(entry, "interpretations", None) or {}).get("offer_name"),
             (getattr(entry, "solution_mechanism", None) or {}).get("short_name")]
    try:
        names.append(vs.founder_idea_name(entry))
    except Exception:                                    # noqa: BLE001 - an entry with no name keeps the others
        pass
    return frozenset(_words_of(*names))


def avoided_words(entry) -> frozenset:
    """The words of the entry's own material (its yaml, every value): a typo that lands on one would read as that word."""
    path = getattr(entry, "path", None)
    try:
        return frozenset(_words_of(open(path, encoding="utf-8").read())) if path else frozenset()
    except OSError:
        return frozenset()


def field_texts(founder) -> dict:
    """The six typed fields of a `FounderInputs`, by name."""
    return {**{k: str((founder.context_fields or {}).get(k) or "") for k in CONTEXT_FIELDS},
            "problem_seed": founder.problem_seed, "solution_seed": founder.solution_seed}


def type_founder(entry, founder) -> tuple[object, list[dict]]:
    """FR-2: `founder` with its six typed fields typed through the typist (seeded `<entry id>:<field>`), and every typo
    as `{field, meant, typed, kind}` in the order typed."""
    keep, avoid = kept_words(entry), avoided_words(entry)
    typed, out = {}, []
    for name, text in field_texts(founder).items():
        typed[name], found = typos(text, f"{entry.id}:{name}", keep=keep, avoid=avoid)
        out += [{"field": name, "meant": t.meant, "typed": t.typed, "kind": t.kind} for t in found]
    context = {**founder.context_fields, **{k: typed[k] for k in CONTEXT_FIELDS if k in (founder.context_fields or {})}}
    return replace(founder, context_fields=context, problem_seed=typed["problem_seed"],
                   solution_seed=typed["solution_seed"]), out


def dry_lines(entry, founder) -> list[str]:
    """The DRY run's lines: every typed field as it will be typed, each typo marked `typed[meant]`."""
    typed, found = type_founder(entry, founder)
    by_field: dict = {}
    for t in found:
        by_field.setdefault(t["field"], []).append(Typo(t["meant"], t["typed"], t["kind"]))
    texts = field_texts(typed)
    lines = []
    for name in FIELDS:
        marks = by_field.get(name) or []
        lines.append(f"    {name} ({len(marks)} typo{'s' if len(marks) != 1 else ''}): {marked(texts[name], marks)}")
    return lines


def as_meant(founder: dict | None, typed: list | None) -> dict:
    """`inputs.json`'s `founder` with each typo put back as the word meant -- for a reader of the founder's words (the
    gallery's), never for the walk. Unchanged where nothing was typed wrong."""
    founder = dict(founder or {})
    if not typed:
        return founder
    context = dict(founder.get("context_fields") or {})
    for t in typed:
        pattern = rf"(?<![^\W\d_]){re.escape(t['typed'])}(?![^\W\d_])"
        if t["field"] in CONTEXT_FIELDS and t["field"] in context:
            context[t["field"]] = re.sub(pattern, t["meant"], str(context[t["field"]]), count=1)
        elif t["field"] in founder:
            founder[t["field"]] = re.sub(pattern, t["meant"], str(founder[t["field"]]), count=1)
    if context:
        founder["context_fields"] = context
    return founder


# ------------------------------------------------------------------------------------------------ FR-3 the leaks

#: A founder screen's slug -> the typed fields the founder typed on it (where the walk recorded the screen, he typed them).
TYPED_ON = {"context": CONTEXT_FIELDS, "problem-seed": ("problem_seed",), "solution-seed": ("solution_seed",)}
#: What a recorded screen keeps that is not served: the founder's own answer, the shot's file and address, the order.
_NOT_SERVED = frozenset({"answer", "file", "url", "n", "order", "answered", "back", "continue_before", "continue_after",
                         "outside", "screens", "person"})


def walked(bundle: dict, typed: list[dict]) -> list[dict]:
    """The typos on fields the walk typed: a field is typed where the bundle records its founder screen (a PROBLEM study
    never reaches the solution seed)."""
    on = {f for s in bundle.get("founder_screens") or [] for f in TYPED_ON.get(str(s.get("screen") or ""), ())}
    return [t for t in typed or [] if t.get("field") in on]


def _strings(value, skip=_NOT_SERVED):
    if isinstance(value, str):
        if value.strip():
            yield value
    elif isinstance(value, dict):
        for k, v in value.items():
            if k not in skip:
                yield from _strings(v, skip)
    elif isinstance(value, (list, tuple)):
        for v in value:
            yield from _strings(v, skip)


def served_texts(bundle: dict) -> list[tuple[str, str]]:
    """`(screen, text)` for every served text the bundle captured, in the walk's order: the founder's screens (never
    what he typed on them), each link's served interview and drawn screens, the screens after the answers, the report."""
    out = []
    for s in bundle.get("founder_screens") or []:
        out += [(f"founder {s.get('screen')}", t) for t in _strings(s)]
    for link, r in (bundle.get("respondents") or {}).items():
        served = r.get("served") or {}
        for key in ("condition", "idea", "gate", "reveal"):
            out += [(f"respondent {link} {key}", t) for t in _strings(served.get(key))]
        for part in served.get("parts") or []:
            for item in part.get("items") or []:
                out += [(f"respondent {link} item {item.get('dimension')}", t) for t in _strings(item)]
            out += [(f"respondent {link} part {part.get('part')}", t) for t in _strings(part.get("kicker"))]
        for d in r.get("drawn") or []:
            what = d.get("screen")
            label = f"respondent {link} {what}" + (f" {d['dimension']}" if d.get("dimension") else "")
            out += [(label, t) for t in _strings(d)]
    for s in bundle.get("after_screens") or []:
        out += [(f"after {s.get('screen') or s.get('kind')}" + (f" {s['dimension']}" if s.get("dimension") else ""), t)
                for t in _strings(s)]
    out += [("brief", t) for t in _strings(bundle.get("brief"))]
    return out


def _sentence_with(text: str, start: int, end: int, most: int = 240) -> str:
    """The sentence of `text` around `[start, end)`, at most `most` characters."""
    left = max(text.rfind(c, 0, start) for c in ".?!\n") + 1
    rights = [i for i in (text.find(c, end) for c in ".?!\n") if i >= 0]
    right = (min(rights) + 1) if rights else len(text)
    said = " ".join(text[left:right].split())
    return said if len(said) <= most else said[:most - 3] + "..."


def leaks(bundle: dict, typed: list[dict]) -> list[dict]:
    """FR-3: every served text holding a typed form as a whole word, case-insensitively -- `{screen, field, meant,
    typed, text}`, one a (screen, typed form, sentence). A word spelt right is the expected outcome, never a leak."""
    out, seen = [], set()
    texts = served_texts(bundle)
    for t in typed or []:
        pattern = re.compile(rf"(?<![^\W\d_]){re.escape(t['typed'])}(?![^\W\d_])", re.I)
        for screen, text in texts:
            for m in pattern.finditer(text):
                said = _sentence_with(text, m.start(), m.end())
                key = (screen, t["typed"].lower(), said)
                if key in seen:
                    continue
                seen.add(key)
                out.append({"screen": screen, "field": t["field"], "meant": t["meant"], "typed": t["typed"],
                            "text": said})
    return out


def _where(screen: str) -> str:
    """A leak's place in the founder's words: *the PROBLEM question*, *the founder's problem-card screen*."""
    parts = screen.split()
    if parts[:1] == ["respondent"] and len(parts) >= 4 and parts[2] == "item":
        return f"the {parts[3].split('.')[0].upper()} question"
    if parts[:1] == ["respondent"] and len(parts) >= 4 and parts[3].count("."):
        return f"the {parts[3].split('.')[0].upper()} {parts[2]} screen"
    if parts[:1] == ["respondent"] and len(parts) >= 3:
        return f"the respondent's {parts[2]} screen ({parts[1]})"
    if parts[:1] == ["founder"] and len(parts) >= 2:
        return f"the founder's {parts[1]} screen"
    if parts[:1] == ["after"] and len(parts) >= 2:
        return f"the {' '.join(parts[1:])} page"
    return f"the {screen}"


def leak_line(leak: dict) -> str:
    """The cycle record's defect line: *typo leak: "withot" (meant "without") reached the PROBLEM question "..."*."""
    return (f"typo leak: \"{leak['typed']}\" (meant \"{leak['meant']}\") reached {_where(leak['screen'])} "
            f"\"{leak['text']}\"")


# ------------------------------------------------------------------------------------- spec 128: held as spelt

#: A text's words and the runs between them, as `instructions.spelling.words` splits them (the runs kept, so the
#: punctuation is held too).
_RUNS = re.compile(r"([^\w'’\-]+|_+)")


def _runs(text: str) -> list[str]:
    """`text`'s words at the even places and the runs between them at the odd ones, spaces collapsed, ends trimmed."""
    return [" ".join(p.split()) if i % 2 and p.strip() else (" " if i % 2 else p)
            for i, p in enumerate(_RUNS.split(" ".join(str(text).split())))]


def as_spelt(typed, served) -> bool:
    """Spec 128 FR-1: whether `served` is the founder's `typed` text read as spelt -- word by word through 125's mirror
    of keel-cloud's `Spelling.sameWord` (`instructions.spelling.same_word`): the same words in the same number, each
    served word equal to the typed one or within its edit allowance (one at four letters, two from five, none under
    four or with a digit, the first letter the same), the punctuation between them the same. Since keel-cloud 196 the
    cloud serves the typed text respelled (*rcord* -> *record*), which is the fix working; a served word that is another
    word, or a word dropped or added, is still a fault. A value that is not text is held exactly."""
    if not isinstance(typed, str) or not isinstance(served, str):
        return typed == served
    a, b = _runs(typed), _runs(served)
    if len(a) != len(b):
        return False
    return all(x == y if i % 2 else (x == y or spelling.same_word(x, y)) for i, (x, y) in enumerate(zip(a, b)))


def spelt_faults(typed_fields: dict, served_fields: dict, *, whole: bool = False) -> list[dict]:
    """FR-1: `{field, typed, served}` for each typed field the served one does not read as spelt (`as_spelt`); `whole`
    holds the key sets equal too (a served field the founder never typed is a fault), as a dict compare did. `[]` when
    every field holds."""
    typed_fields, served_fields = dict(typed_fields or {}), dict(served_fields or {})
    keys = list(typed_fields) + ([k for k in served_fields if k not in typed_fields] if whole else [])
    return [{"field": k, "typed": typed_fields.get(k), "served": served_fields.get(k)} for k in keys
            if k not in typed_fields or k not in served_fields or not as_spelt(typed_fields[k], served_fields[k])]


def respelled(typed_fields: dict, served_fields: dict) -> list[dict]:
    """FR-2: `{field, typed, served}` for each word the cloud served spelt otherwise than the founder typed it, in the
    fields' order -- the typos keel-cloud 196 corrected. A field whose words do not line up (a fault `spelt_faults`
    names) is given whole."""
    out = []
    for k, typed in (typed_fields or {}).items():
        served = (served_fields or {}).get(k)
        if not isinstance(typed, str) or not isinstance(served, str) or typed == served:
            continue
        a, b = _runs(typed), _runs(served)
        if len(a) != len(b):
            out.append({"field": k, "typed": typed, "served": served})
            continue
        out += [{"field": k, "typed": x, "served": y} for i, (x, y) in enumerate(zip(a, b)) if not i % 2 and x != y]
    return out
