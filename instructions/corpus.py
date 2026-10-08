"""The golden corpus at revision 3, read and never written (spec 029 FR-006/FR-012, data-model §2).

`canon/designs/measured-beliefs/corpus/*.yaml` in the keel-cloud checkout is the corpus. This
module opens those files, hashes them on the way in, and offers `verify_unchanged()` so the end of
a run can prove nothing here moved while it ran. **If an instruction cannot reach a golden, the
instruction is wrong** -- or the design is, and it goes back to step 1. Never the corpus.

**Revision 3 only.** `MARKS_VERSION` 9 reads the vector redesign's schema (marks-v9 §4): `context`,
`interpretations.problem`, `solution_mechanism`, `persona`, `founder_calibration` keyed by the
registry's 25 dimensions, the golden plan `respondent_questions`, people with a gate answer, a
story, a chip, a golden anchoring and picks by dimension, and `expected.standings` +
`expected.vector_verdicts`. A file at any other revision, or still carrying `beliefs`,
`questionnaire`, `expected.buckets`, `expected.stages` or a per-anchor answer, is a **refusal to
start** by entry and by key -- never a fallback, the same shape v8's scalar-`stage` refusal had.

**Where revision 3 is read from, until keel-cloud carries it** (the orchestrator's cross-track
arrangement of 2026-10-07). The seven r3 entries are this branch's to write, and they live in
keel-cloud's canon, which this branch may not touch. So they are recorded under
`tests/fixtures/corpus-r3/` with a README saying they are to be moved verbatim into keel-cloud's
canon at integration, and **`load()` reads that directory when the configured corpus directory
holds no revision-3 entry at all**. The moment keel-cloud's corpus carries one r3 file, the
configured directory is read and every r2 file left in it refuses by name. Nothing else about the
reader changes with the source: the same refusals, the same hash, the same `verify_unchanged()`.

Three things the r3 corpus says that the code has to carry:

1. **The plan is derived, and the file's own plan is a check on it** (call 30). `plan()` is the
   registry's keys asked in V1, by part, that the founder did not leave out; the file's
   `respondent_questions` must hold exactly those keys per part, or the file disagrees with the
   registry it is keyed by -- a refusal.
2. **The chipped story is a corpus fact, not a judgement** (call 33 amended, FR-017). `readable()` is
   the people who passed the gate, carry no chip and wrote a story; nobody else is ever shown to the
   reader, and a chip-carrying person's golden `GUESSED` is checked by `compare_correctness`.
3. **`no_leak`'s list is the corpus's** (call 32). `vocabulary()` stems the golden
   `solution_mechanism` and subtracts the problem's own words; the stems excluded only because the
   problem's world spells them with another inflection are kept beside it as the **inflection
   ledger**, because those -- and only those -- are the ties the judge is asked about.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, replace
from pathlib import Path

import yaml

from . import text as text_mod
from .registry import DEAL_BREAKERS, VECTORS, RecallWindow

REVISION = 3

STAGES = VECTORS

#: The eight `Status` words (registry-schema; marks §2.5).
STATUSES = ("HOLDING_UP", "NOT_HOLDING_UP", "PEOPLE_DISAGREE", "TOO_FEW_TO_CALL", "BAR_SET",
            "NOT_TESTED_BY_DESIGN", "NOT_ASKED_YET", "LEFT_OUT")

#: The drift words `expected.standings[*].drift` may carry (`null` beside them).
DRIFTS = ("above", "below", "both", "none")

CHIPS = ("cant_recall", "rather_not_say")
ANCHORINGS = ("ANCHORED", "GUESSED")

#: The keys revision 2 carried and revision 3 dropped (marks §4 *Dropped*).
R2_KEYS = ("beliefs", "questionnaire", "normalization_rationale")
R2_EXPECTED_KEYS = ("buckets", "stages")

#: The fixture directory read when keel-cloud's corpus holds no revision-3 entry (module docstring).
FIXTURE_DIR = Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "corpus-r3"


class CorpusError(RuntimeError):
    """The corpus could not be read, or moved while a run was in flight."""


#: The two links a person answers on (FR-010): the primary interview, and -- on a B2B entry -- the
#: decision-maker's Part 3 (`COMMERCIAL_B2B`: no gate, no context card, no reveal).
LINK_PRIMARY = "PRIMARY"
LINK_B2B = "COMMERCIAL_B2B"


@dataclass(frozen=True)
class Person:
    person: str
    recency: str | None        # "yes" | "no" -- the gate (problem.prevalence); None on the B2B link
    story: str | None
    chip: str | None
    anchoring: str | None      # golden; None when recency == "no"
    picks: dict
    pilot_opt_in: bool = False
    link: str = LINK_PRIMARY

    @property
    def gate_yes(self) -> bool:
        return self.link == LINK_PRIMARY and self.recency == "yes"

    @property
    def readable(self) -> bool:
        """Gate-yes, un-chipped, with a story typed -- the only people `INTERPRET` is shown."""
        return self.gate_yes and self.chip is None and bool((self.story or "").strip())


@dataclass(frozen=True)
class Entry:
    id: str
    title: str
    revision: int
    market: dict
    statements: dict
    roles: list
    context: dict
    interpretations: dict
    solution_mechanism: dict
    persona: dict
    founder_calibration: dict
    respondent_questions: dict
    answers: list
    expected: dict
    path: Path
    sha256: str
    registry: object = None

    # ------------------------------------------------------------------ the people

    def people(self) -> list[Person]:
        return [_person(raw) for raw in self.answers]

    def gate_yes(self) -> list[Person]:
        return [p for p in self.people() if p.gate_yes]

    def deciders(self) -> list[Person]:
        """The B2B entry's decision-makers, who answer Part 3 on their own link (FR-010)."""
        return [p for p in self.people() if p.link == LINK_B2B]

    def readable(self) -> list[Person]:
        return [p for p in self.people() if p.readable]

    def person(self, name: str) -> Person | None:
        return next((p for p in self.people() if p.person == name), None)

    def role(self, role_id: str) -> dict | None:
        return next((r for r in self.roles if r.get("id") == role_id), None)

    def b2b(self) -> bool:
        """Whether the decision-maker is a role of its own (FR-010) -- the `COMMERCIAL_B2B` link."""
        return isinstance((self.persona or {}).get("decision_maker"), dict)

    def decision_maker_role(self) -> str | None:
        maker = (self.persona or {}).get("decision_maker")
        return maker.get("role") if isinstance(maker, dict) else None

    # ---------------------------------------------------------------------- the plan

    def unsure(self, key: str) -> bool:
        return bool((self.founder_calibration.get(key) or {}).get("unsure"))

    def plan(self, registry=None) -> dict:
        """`{1: [key], 2: [key], 3: [key]}` (call 30): the registry's keys asked in V1, by part, the
        founder did not leave out, in order. Without a registry bound, the file's own golden plan
        (`respondent_questions`) by part, in file order -- the two are checked equal on load."""
        registry = registry if registry is not None else self.registry
        if registry is not None:
            return {part: registry.plan_keys(part, self.founder_calibration) for part in (1, 2, 3)}
        out = {1: [], 2: [], 3: []}
        for key, row in (self.respondent_questions or {}).items():
            part = (row or {}).get("part")
            if part in out:
                out[part].append(key)
        return out

    # ----------------------------------------------------------- the founder's labels

    def founder_option_codes(self, key: str) -> list:
        """The codes of the options the founder's calibration showed for a model-written set: the
        golden plan row's codes less the respondent-only rows code appends (call 38), keeping a
        founder-side `none` / `nothing` -- the founder saw it; code appends the respondent's."""
        return founder_codes_of((self.respondent_questions or {}).get(key) or {})

    def founder_labels(self, key: str) -> dict | None:
        """`{code: label}` -- the labels the founder saw (`founder_calibration[key].labels`, one per
        `founder_option_codes`, in order), what production's `founderOptions` carries; `None` where
        the entry records none."""
        labels = (self.founder_calibration.get(key) or {}).get("labels")
        if not labels:
            return None
        return dict(zip(self.founder_option_codes(key), labels))

    # ------------------------------------------------------------- the mechanism's words

    def _mechanism_texts(self) -> list[str]:
        mechanism = self.solution_mechanism or {}
        # Call 39: `mechanism`, `output`, `not_assumed` (and `mechanism_terms`, below) only --
        # never `trigger` (it describes the problem moment) nor `actor`.
        texts = [str(mechanism.get(k) or "") for k in ("mechanism", "output")]
        texts += [str(t) for t in mechanism.get("not_assumed") or []]
        return texts

    def _problem_texts(self) -> list[str]:
        texts = [str(v) for v in (self.context or {}).values() if v]
        texts.append(str((self.statements or {}).get("problem") or ""))
        texts.append(str((self.interpretations or {}).get("problem") or ""))
        # The gate stories only: a decision-maker's story on the B2B link is about a past purchase
        # -- platform fees, a tool they bought -- which is the commercial world, not the problem's.
        texts += [p.story for p in self.people() if p.story and p.link == LINK_PRIMARY]
        return texts

    def _problem_words(self) -> dict:
        """stem -> the problem-world spellings of it."""
        out = {}
        for chunk in self._problem_texts():
            for word in text_mod.content_words(chunk):
                out.setdefault(text_mod.stem(word), set()).add(word)
        return out

    def _mechanism_words(self) -> dict:
        out = {}
        for chunk in self._mechanism_texts():
            for word in text_mod.content_words(chunk):
                out.setdefault(text_mod.stem(word), set()).add(word)
        for term in (self.solution_mechanism or {}).get("mechanism_terms") or []:
            tokens = text_mod.content_words(term)
            if len(text_mod.words(term)) == 1 and tokens:
                out.setdefault(text_mod.stem(tokens[0]), set()).add(tokens[0])
        return out

    def vocabulary(self) -> set[str]:
        """The stems `no_leak`'s sweep A looks for (calls 32, 39): the content words of the golden
        mechanism's `mechanism`, `output` and `not_assumed` (never `trigger` or `actor`) and its
        single-word `mechanism_terms`, stemmed, less the stoplist and every stem of the
        problem's own words (`context`, `statements.problem`, `interpretations.problem`, every
        story). Multi-word terms are `mechanism_phrases()`."""
        problem = self._problem_words()
        return {s for s in self._mechanism_words() if s not in problem}

    def mechanism_phrases(self) -> list[tuple]:
        """The multi-word `mechanism_terms` (*most likely*), stemmed in order, matched as phrases."""
        out = []
        for term in (self.solution_mechanism or {}).get("mechanism_terms") or []:
            if len(text_mod.words(term)) > 1:
                out.append(tuple(text_mod.stem_sequence(term)))
        return out

    def inflection_ledger(self) -> dict:
        """`{stem: {"mechanism": [...], "problem": [...]}}` -- the stems excluded from the vocabulary
        **only** because the problem's world spells them with another inflection (*listens* in the
        mechanism, *listened* in a story). A hit on one is a tie, and a tie goes to the judge."""
        problem = self._problem_words()
        out = {}
        for stem, spellings in self._mechanism_words().items():
            if stem in problem and not (spellings & problem[stem]):
                out[stem] = {"mechanism": sorted(spellings), "problem": sorted(problem[stem])}
        return out

    def mechanism_one_liner(self) -> str:
        """The judge's clause (marks §2.3), composed by code from the golden mechanism's four
        fields -- never from a live `SOLUTION_MECHANISM` answer (call 32)."""
        m = self.solution_mechanism or {}
        return (f"{m.get('actor', '')}, {m.get('trigger', '')}, {m.get('mechanism', '')}; "
                f"it gives {m.get('output', '')}").strip()


@dataclass
class Corpus:
    entries: list
    directory: Path
    hashes: dict = field(default_factory=dict)

    def verify_unchanged(self) -> None:
        """Re-hash every file. A difference is a failed run, not a warning.

        The corpus is the reviewer, not the subject: quietly adjusting it is exactly what freezing
        it exists to prevent, and a run that could have done so proves nothing.
        """
        for path, digest in self.hashes.items():
            current = _sha256(Path(path))
            if current != digest:
                raise CorpusError(
                    f"{path} changed while the run was in flight: {digest} -> {current}. "
                    "The corpus is frozen (keel-cloud spec 029 SC-009); this run has measured "
                    "nothing.")

    def by_id(self, entry_id: str):
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None

    def bind(self, registry) -> "Corpus":
        """Every entry checked against the registry the export carried, and bound to it -- the
        key refusals that need the registry (data-model §2) are taken here, before a case is
        built."""
        bound = []
        for entry in self.entries:
            _check_keys(entry, registry)
            bound.append(replace(entry, registry=registry))
        self.entries = bound
        return self


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_dir(keel_cloud: Path) -> Path:
    return Path(keel_cloud) / "canon" / "designs" / "measured-beliefs" / "corpus"


def _revision_of(path: Path):
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return None
    return raw.get("revision") if isinstance(raw, dict) else None


def source_dir(keel_cloud: Path) -> Path:
    """The directory `load()` reads: keel-cloud's corpus once it holds a revision-3 entry, else
    this branch's recorded revision 3 under `tests/fixtures/corpus-r3/` (module docstring)."""
    directory = corpus_dir(keel_cloud)
    if directory.is_dir() and any(_revision_of(p) == REVISION
                                  for p in sorted(directory.glob("*.yaml"))):
        return directory
    return FIXTURE_DIR


def load(keel_cloud: Path, *, registry=None) -> Corpus:
    """Every `NN-name.yaml` in the corpus directory, in filename order, each at revision 3."""
    directory = source_dir(keel_cloud)
    if not directory.is_dir():
        raise CorpusError(
            f"no corpus at {directory} -- this eval reads keel-cloud's own golden set, and "
            "cannot invent one")
    files = sorted(p for p in directory.glob("*.yaml"))
    if not files:
        raise CorpusError(f"{directory} holds no *.yaml entries")
    entries, hashes = [], {}
    for path in files:
        entry = load_file(path, registry=registry)
        hashes[str(path)] = entry.sha256
        entries.append(entry)
    return Corpus(entries=entries, directory=directory, hashes=hashes)


def load_file(path, *, registry=None) -> Entry:
    """One revision-3 file, checked; bound to `registry` (and checked against it) when given."""
    path = Path(path)
    digest = _sha256(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    entry = _entry(raw, path, digest)
    if registry is not None:
        _check_keys(entry, registry)
        entry = replace(entry, registry=registry)
    return entry


# ------------------------------------------------------------------------------- the refusals

def _refuse(entry_id, message, path) -> CorpusError:
    return CorpusError(f"{entry_id}: {message} (spec 029 FR-006; marks-v9 §4). {path}")


def _check_revision(raw: dict, path: Path) -> None:
    entry_id = raw.get("id") or path.name
    revision = raw.get("revision")
    if revision != REVISION:
        raise _refuse(entry_id, f"revision is {revision if revision is not None else 'absent'}; "
                                f"this eval reads revision {REVISION} only", path)
    for key in R2_KEYS:
        if key in raw:
            raise _refuse(entry_id, f"carries `{key}`, which revision 3 dropped", path)
    for key in R2_EXPECTED_KEYS:
        if key in (raw.get("expected") or {}):
            raise _refuse(entry_id, f"carries `expected.{key}`, which revision 3 dropped", path)
    for person in raw.get("answers") or []:
        if "anchors" in (person or {}):
            raise _refuse(entry_id, f"{person.get('person')} carries `anchors`; a revision-3 "
                                    "person answers one gate story", path)


def founder_codes_of(row: dict) -> list:
    """`Entry.founder_option_codes` on a plan row."""
    from .registry import RESPONDENT_ESCAPES                  # noqa: PLC0415
    return [c for c in (row or {}).get("codes") or []
            if c not in RESPONDENT_ESCAPES or c in FOUNDER_NONE]


#: The founder's own *none of these* option (Existing sacrifice's `none`; r3 spells it `nothing`):
#: shown to the founder, so it has a label; on the respondent screen code appends it.
FOUNDER_NONE = ("none", "nothing")


def _check_shape(raw: dict, path: Path) -> None:
    entry_id = raw.get("id") or path.name
    # `context.recall_window: {count, unit}` (founder decision 42; keel-cloud 058 `cb0422a`):
    # optional -- an entry without one reads the default, 7 nights -- and refused when unreadable.
    try:
        RecallWindow.read((raw.get("context") or {}).get("recall_window"))
    except ValueError as why:
        raise _refuse(entry_id, f"context.recall_window: {why}", path) from None
    for key, value in (raw.get("founder_calibration") or {}).items():
        if not isinstance(value, dict) or not ("answer" in value or value.get("unsure") is True):
            raise _refuse(entry_id, f"founder_calibration[{key}] carries neither `answer` nor "
                                    "`unsure: true`", path)
        labels = value.get("labels")
        if labels is not None:
            codes = founder_codes_of((raw.get("respondent_questions") or {}).get(key) or {})
            if (not isinstance(labels, list) or not all(isinstance(x, str) and x.strip()
                                                         for x in labels)
                    or len(labels) != len(codes)):
                raise _refuse(entry_id, f"founder_calibration[{key}].labels must be one label per "
                                        f"founder option {codes}", path)
    b2b = isinstance((raw.get("persona") or {}).get("decision_maker"), dict)
    for person in raw.get("answers") or []:
        name = person.get("person")
        recency = person.get("recency")
        link = person.get("link", LINK_PRIMARY)
        if link not in (LINK_PRIMARY, LINK_B2B):
            raise _refuse(entry_id, f"{name}'s link is {link!r}", path)
        if link == LINK_B2B:
            if not b2b:
                raise _refuse(entry_id, f"{name} answers on the B2B link of an entry whose "
                                        "decision-maker is the same person", path)
            if recency is not None:
                raise _refuse(entry_id, f"{name} answers on the B2B link and carries a gate "
                                        "answer; the decision-maker is never asked the gate", path)
            if person.get("anchoring") not in ANCHORINGS:
                raise _refuse(entry_id, f"{name}'s anchoring is {person.get('anchoring')!r}", path)
            foreign = [k for k in person.get("picks") or {} if not str(k).startswith("commercial.")]
            if foreign:
                raise _refuse(entry_id, f"{name} answers on the B2B link and picks {foreign[0]}; "
                                        "the link is Part 3 only", path)
            continue
        if recency not in ("yes", "no"):
            raise _refuse(entry_id, f"{name}'s recency is {recency!r}; the gate is yes or no", path)
        if recency == "no":
            for key in ("story", "chip", "anchoring"):
                if person.get(key) not in (None, ""):
                    raise _refuse(entry_id, f"{name} answered No at the gate and carries `{key}`; "
                                            "a gate-No answers nothing more", path)
            if person.get("picks"):
                raise _refuse(entry_id, f"{name} answered No at the gate and carries picks; a "
                                        "gate-No answers nothing more", path)
            continue
        chip = person.get("chip")
        if chip is not None and chip not in CHIPS:
            raise _refuse(entry_id, f"{name}'s chip is {chip!r}; the chips are {CHIPS}", path)
        anchoring = person.get("anchoring")
        if anchoring not in ANCHORINGS:
            raise _refuse(entry_id, f"{name}'s anchoring is {anchoring!r}", path)
        if chip is not None and anchoring != "GUESSED":
            raise _refuse(entry_id, f"{name} carries the chip {chip} and is {anchoring}; a chipped "
                                    "story is GUESSED by code (call 33 amended)", path)
    maker = (raw.get("persona") or {}).get("decision_maker")
    if isinstance(maker, dict):
        role_ids = {r.get("id") for r in raw.get("roles") or []}
        if maker.get("role") not in role_ids:
            raise _refuse(entry_id, f"persona.decision_maker names the role {maker.get('role')!r}, "
                                    f"which is not in roles ({', '.join(sorted(map(str, role_ids)))})",
                          path)
    elif maker != "same_person":
        raise _refuse(entry_id, f"persona.decision_maker is {maker!r}; it is same_person or "
                                "{role: <id>}", path)
    expected = raw.get("expected") or {}
    for key, standing in (expected.get("standings") or {}).items():
        status = (standing or {}).get("status")
        if status not in STATUSES:
            raise _refuse(entry_id, f"expected.standings[{key}].status is {status!r}, outside "
                                    "Status", path)
        drift = (standing or {}).get("drift")
        if drift is not None and drift not in DRIFTS:
            raise _refuse(entry_id, f"expected.standings[{key}].drift is {drift!r}", path)
    for vector, verdict in (expected.get("vector_verdicts") or {}).items():
        if vector not in VECTORS:
            raise _refuse(entry_id, f"expected.vector_verdicts names {vector!r}", path)
        if (verdict or {}).get("verdict") not in STATUSES:
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].verdict is "
                                    f"{(verdict or {}).get('verdict')!r}, outside Status", path)
        deciding = (verdict or {}).get("deciding")
        if deciding not in DEAL_BREAKERS[vector]:
            raise _refuse(entry_id, f"expected.vector_verdicts[{vector}].deciding is {deciding!r}, "
                                    f"not a DEAL_BREAKER of {vector}", path)


def _check_keys(entry: Entry, registry) -> None:
    """The refusals that need the registry: every dimension-keyed map keyed by it, and the file's
    own plan equal to the one the registry derives (data-model §2-§3)."""
    keys = set(registry.keys())
    calibrated = set(entry.founder_calibration)
    if calibrated != keys:
        missing, foreign = sorted(keys - calibrated), sorted(calibrated - keys)
        raise _refuse(entry.id, "founder_calibration is not exactly the registry's 25 keys"
                      + (f"; missing {', '.join(missing)}" if missing else "")
                      + (f"; outside the registry {', '.join(foreign)}" if foreign else ""),
                      entry.path)
    for person in entry.answers:
        for key in (person.get("picks") or {}):
            if key not in keys:
                raise _refuse(entry.id, f"{person.get('person')} picks {key}, which is not a "
                                        "registry key", entry.path)
    for key in entry.respondent_questions or {}:
        if key not in keys:
            raise _refuse(entry.id, f"respondent_questions carries {key}, which is not a registry "
                                    "key", entry.path)
    for key in (entry.expected.get("standings") or {}):
        if key not in keys:
            raise _refuse(entry.id, f"expected.standings carries {key}, which is not a registry "
                                    "key", entry.path)
    derived = {part: registry.plan_keys(part, entry.founder_calibration) for part in (1, 2, 3)}
    for part, plan_keys in derived.items():
        recorded = [k for k, row in (entry.respondent_questions or {}).items()
                    if (row or {}).get("part") == part]
        if sorted(recorded) != sorted(plan_keys):
            raise _refuse(entry.id, f"respondent_questions part {part} holds "
                                    f"{', '.join(recorded) or 'nothing'}; the registry plans "
                                    f"{', '.join(plan_keys) or 'nothing'} (call 30)", entry.path)


def _person(raw: dict) -> Person:
    return Person(person=raw.get("person"), recency=raw.get("recency"),
                  story=raw.get("story") or None, chip=raw.get("chip"),
                  anchoring=raw.get("anchoring"), picks=dict(raw.get("picks") or {}),
                  pilot_opt_in=bool(raw.get("pilot_opt_in")),
                  link=raw.get("link", LINK_PRIMARY))


def _entry(raw: dict, path: Path, digest: str) -> Entry:
    if not isinstance(raw, dict):
        raise CorpusError(f"{path} is not a corpus entry")
    _check_revision(raw, path)
    _check_shape(raw, path)
    return Entry(
        id=raw["id"],
        title=raw.get("title", ""),
        revision=raw["revision"],
        market=raw.get("market") or {},
        statements=raw.get("statements") or {},
        roles=raw.get("roles") or [],
        context=raw.get("context") or {},
        interpretations=raw.get("interpretations") or {},
        solution_mechanism=raw.get("solution_mechanism") or {},
        persona=raw.get("persona") or {},
        founder_calibration=raw.get("founder_calibration") or {},
        respondent_questions=raw.get("respondent_questions") or {},
        answers=raw.get("answers") or [],
        expected=raw.get("expected") or {},
        path=path,
        sha256=digest,
    )
