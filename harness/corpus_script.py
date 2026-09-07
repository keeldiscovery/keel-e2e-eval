"""The corpus becomes the script (spec 010 FR-001..FR-006, data-model.md §1-§3).

One corpus entry in; out come the three things a scenario needs to drive the whole product
deterministically:

1. a **keel-runtime scripted-executor script**, keyed by the screen names keel-cloud's own
   `context-keys.json` uses -- handed to the runtime as `KEEL_SCRIPT` and written into the run
   bundle as `runs/<id>/script.json`;
2. the **founder's typed inputs** -- the name, the market, the three statements and (S-001 only)
   the one correction;
3. **each person's typed inputs** -- the story text per written anchor, the tap, and one pick per
   selection their role is asked.

**One reader, one hash** (research R6). The corpus is opened through `instructions/corpus.py` and
never a second time: that module already opens the files read-only, hashes each on the way in,
offers `verify_unchanged()`, and knows the three places the corpus and the wire disagree. The tap
table is `instructions/context.py`'s, imported rather than copied, because it is the only place
the corpus's English and the wire's enum meet.

**It refuses rather than invents** (FR-004). Four refusals, each naming the entry and the field:
a belief whose `selection` is on no anchor of its own stage; a pick that names neither an option
nor an escape (nor an `other:` box); a tap outside the table; an anchoring the corpus does not
carry for an anchor a person wrote under. None is ever softened to a warning -- a generator that
guesses is a golden set that has stopped being golden.

**Nothing generated is committed** (spec judgement call 1). The script is written into the bundle,
so a run can never be green against a script that drifted from the corpus.

    python3 -m harness.corpus_script 01-countly     # prints the script it would write
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from instructions import corpus as corpus_reader
from instructions.context import TAP_ENUM, tap_enum

STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

# The corpus writes `statements: {problem: ...}`; the screens are named for the stage.
_STATEMENT_KEY = {"PROBLEM": "problem", "SOLUTION": "solution", "COMMERCIAL": "commercial"}
FRAME_SCREEN = {stage: f"{stage}_FRAME" for stage in STAGES}
ASSUMPTIONS_SCREEN = {stage: f"{stage}_ASSUMPTIONS" for stage in STAGES}
CORRECTION_SCREEN = {stage: f"{stage}_ASSUMPTIONS.correction" for stage in STAGES}

# contracts/vendored-wire-facts.md §V4: `assumptions` and `questionnaire.anchors` are each
# `maxItems: 8`. countly's PROBLEM stage is exactly 8 beliefs and 1 anchor -- at the cap, not over
# it, which is a fact worth a unit test rather than a coincidence to discover mid-run.
MAX_ITEMS = 8

# The wire's drift enum, upper-case; the corpus writes it lower. Reconciled in `drift_equal` and
# nowhere else, so no scenario carries the convention (spec edge case; research R10).
DRIFTS = ("NONE", "BELOW", "ABOVE", "BOTH")


class CorpusScriptError(RuntimeError):
    """A value the corpus does not carry. Named -- entry and field -- never invented (FR-004)."""


# ------------------------------------------------------------------------------------ the shapes

@dataclass(frozen=True)
class GeneratedScript:
    entry_id: str
    entry_sha256: str
    source: str
    screens: dict[str, list[dict]]

    def to_json(self) -> dict:
        """`runs/<id>/script.json` (contracts/generated-script-contract.md). The `_`-prefixed keys
        are metadata -- `ScriptedExecutor` skips them by rule -- and they are the whole provenance
        of the run."""
        out = {
            "_source": self.source,
            "_entry_id": self.entry_id,
            "_entry_sha256": self.entry_sha256,
            "_generated_by": "harness/corpus_script.py",
            "_generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        out.update(self.screens)
        return out


@dataclass(frozen=True)
class Market:
    country: str            # ISO alpha-2, "GB" / "US"
    region: str | None      # "TX", or None -- left empty on the screen, never the word "null"
    language: str           # "en-GB" / "en-US" -- asserted, never typed (the server derives it)


@dataclass(frozen=True)
class Correction:
    stage: str
    belief_id: str
    message: str
    expected_change: str


@dataclass(frozen=True)
class FounderInputs:
    project_name: str
    market: Market
    problem: str
    solution: str
    commercial: str
    correction: Correction | None = None

    def statement(self, stage: str) -> str:
        return {"PROBLEM": self.problem, "SOLUTION": self.solution,
                "COMMERCIAL": self.commercial}[stage]


@dataclass(frozen=True)
class AnchorAnswer:
    anchor_id: str
    text: str | None        # None where the corpus left it blank
    tap: str | None         # the ENUM name, via instructions.context.tap_enum


@dataclass(frozen=True)
class Pick:
    selection_id: str
    values: list[str]       # one for a single-select or a bucket; many for a multi-select
    is_escape: bool = False
    # Not in data-model.md §3's sketch, and added deliberately: S-004's box **B9** is the
    # *other, say what* reveal, and a scenario cannot fill a box it cannot tell apart from an
    # ordinary option. A pick is `other` when the selection offers `other: true` and the value is
    # in neither `options` nor `escape` -- which is also the only reading under which such a pick
    # is legal at all (FR-004's `unknown pick` refusal covers every other case).
    is_other: bool = False


@dataclass(frozen=True)
class PersonInputs:
    person: str
    role_id: str
    anchors: list[AnchorAnswer] = field(default_factory=list)
    picks: list[Pick] = field(default_factory=list)

    def written(self) -> list[AnchorAnswer]:
        return [a for a in self.anchors if (a.text or "").strip()]

    def pick(self, selection_id: str) -> Pick | None:
        return next((p for p in self.picks if p.selection_id == selection_id), None)


# ------------------------------------------------------------------------------------- reading in

def load(keel_cloud) -> corpus_reader.Corpus:
    """The corpus, through `instructions/corpus.py` and nothing else (research R6)."""
    return corpus_reader.load(keel_cloud)


def entry_from_file(path):
    """One corpus-*shaped* file, read by the same reader (FR-007): this repo's own
    `evals/payroll_exceptions.yaml`, which it owns and may edit.

    `instructions.corpus._entry` is reached by name on purpose. SC-008 forbids *writing* anything
    in `instructions/`, and a public wrapper there would be a write; a second parser here would be
    the second reader research R6 rejected, with a second chance to be wrong about the three
    places the corpus and the wire disagree. Importing a private name is the smaller of the three.
    """
    import yaml

    path = Path(path)
    digest = corpus_reader._sha256(path)
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    entry = corpus_reader._entry(raw, path, digest)
    return corpus_reader.Corpus(entries=[entry], directory=path.parent,
                                 hashes={str(path): digest}), entry


def entry_for(keel_cloud, entry_id: str):
    """One entry by id, refusing by name rather than returning `None` into an assertion."""
    corpus = load(keel_cloud)
    entry = corpus.by_id(entry_id)
    if entry is None:
        raise CorpusScriptError(
            f"no corpus entry {entry_id!r} in {corpus.directory} "
            f"(it holds {', '.join(e.id for e in corpus.entries)})")
    return corpus, entry


# ---------------------------------------------------------------------------------- the small folds

def expectation_of(entry, belief) -> dict:
    """The belief's `expectation`, **verbatim**, minus the keys the corpus writes as `null`.

    The corpus records an open-ended band as `lower: null` and a per-less measure as `per: null`;
    the wire's schema types those as an object and a string, so a null fails validation. An absent
    bound and a null bound are the same claim, so this changes no meaning -- and it is the only
    transformation made to an expectation anywhere in this module. keel-runtime's own
    `tools/generate_bundled_script.py` makes exactly the same one, for exactly the same reason.
    """
    raw = belief.expectation or {}
    if not raw:
        raise CorpusScriptError(f"{entry.id}: belief {belief.id} carries no expectation")
    out = {k: v for k, v in raw.items() if v is not None}
    measure = out.get("measure")
    if isinstance(measure, dict):
        out["measure"] = {k: v for k, v in measure.items() if v is not None}
    return out


def drift_equal(corpus_drift, wire_drift) -> bool:
    """The corpus writes `none|below|above|both`; the wire's enum is upper-case.

    One function, here, so no scenario remembers the convention. `drift_equal(None, "NONE")` is
    **False**: an absent drift and a `NONE` drift are different claims, and only the corpus
    decides which one it made.
    """
    if corpus_drift is None or wire_drift is None:
        return False
    return str(corpus_drift).strip().upper() == str(wire_drift).strip().upper()


def tap_of(entry, tap) -> str | None:
    """The enum name for a corpus tap, refusing one the table does not carry (FR-004)."""
    if tap is None:
        return None
    if str(tap).strip().lower() not in TAP_ENUM:
        raise CorpusScriptError(
            f"{entry.id}: unknown tap {tap!r} -- outside instructions/context.py's TAP_ENUM "
            f"({', '.join(sorted(TAP_ENUM))})")
    return tap_enum(tap)


def selections_for(entry, stage: str) -> dict[str, dict]:
    """Every selection this stage's own anchors offer, by id -- the set a belief may name."""
    offered: dict[str, dict] = {}
    for anchor in entry.anchors_for(stage):
        for selection in anchor.get("selections") or []:
            offered[selection["id"]] = selection
    return offered


def anchor_of_selection(entry, selection_id: str) -> dict | None:
    for anchor in (entry.questionnaire.get("anchors") or []):
        for selection in anchor.get("selections") or []:
            if selection["id"] == selection_id:
                return anchor
    return None


def role_of_anchor(entry, anchor_id: str) -> str | None:
    """Which role is asked this anchor -- read off the `askedOf` edge of the beliefs whose
    selections live on it, because a corpus anchor records no role of its own.

    Matched against **this anchor's own stage** (design decision 18, DRIFT #37): a selection id is
    unique only within one stage's own questionnaire, so a belief on another stage naming the same
    bare id is not a reader of this anchor, even though the id string matches.
    """
    anchor = entry.anchor(anchor_id) or {}
    stage = anchor.get("stage")
    ids = {s["id"] for s in anchor.get("selections") or []}
    for belief in entry.beliefs:
        if belief.stage == stage and belief.selection in ids and belief.asked_of:
            return belief.asked_of
    return None


def anchors_for_role(entry, role_id: str) -> list[str]:
    """The anchor ids a role is asked, in the questionnaire's own order. A person offered an
    anchor their role is not asked is a refusal, not a shrug (spec edge case)."""
    return [a["id"] for a in (entry.questionnaire.get("anchors") or [])
            if role_of_anchor(entry, a["id"]) == role_id]


# -------------------------------------------------------------------------------- the script itself

def introducing_stage(entry) -> dict[str, str]:
    """Which stage each role is **new** on -- the first stage, in the walk's own order, whose
    beliefs name it.

    This is the one fact a per-stage generator cannot work out from its own stage. A role
    introduced on PROBLEM already exists on the project by the time the SOLUTION screen answers,
    and keel-cloud refuses a second `role.new` with the same label by name:

        result.assumptions[0].role.new.label: a role labeled 'A payroll manager' already exists
        on this project

    Live-confirmed on the first run of the rewritten smoke (`runs/20260907T142617Z-s001-smoke`,
    `SOLUTION_ASSUMPTIONS` -> `RESULT_INVALID`). keel-runtime's own bundled-script generator never
    met it because it writes one stage and stops; this one writes three, so it has to know.
    """
    first: dict[str, str] = {}
    for stage in STAGES:
        for belief in entry.beliefs_for(stage):
            if belief.asked_of and belief.asked_of not in first:
                first[belief.asked_of] = stage
    return first


def _role_field(entry, belief, introduced: set[str], first_stage: dict[str, str]) -> dict:
    """The wire has **no `askedOf`** (vendored fact V4). A corpus `askedOf` is a role *id*; the
    first belief **in the whole entry** to name a role emits `role.new` with its label, roleType
    and about, and every later one -- on that stage or any later one -- emits `role.reuse`."""
    role = entry.role(belief.asked_of)
    if role is None:
        raise CorpusScriptError(
            f"{entry.id}: belief {belief.id} is askedOf {belief.asked_of!r}, which the entry's "
            f"`roles` does not carry")
    if belief.asked_of in introduced or first_stage.get(belief.asked_of) != belief.stage:
        return {"reuse": role["label"]}
    introduced.add(belief.asked_of)
    new = {"label": role["label"], "roleType": role["roleType"], "about": role["about"]}
    if role.get("market"):
        new["market"] = role["market"]
    return {"new": new}


def _assumption(entry, belief, offered: dict[str, dict], introduced: set[str],
                first_stage: dict[str, str]) -> dict:
    if belief.selection not in offered:
        raise CorpusScriptError(
            f"{entry.id}: belief {belief.id} names selection {belief.selection!r}, which no "
            f"{belief.stage} anchor offers (it offers {', '.join(sorted(offered)) or 'none'})")
    assumption = {
        "heading": belief.heading,
        "statement": belief.statement,
        "risk": belief.risk,
        "mark": belief.mark,
        "expectation": expectation_of(entry, belief),
        "selection": belief.selection,
        "role": _role_field(entry, belief, introduced, first_stage),
    }
    if belief.founder_phrase:
        # Optional on the schema and always emitted: scoring it is half of why spec 029 put it
        # on the wire at all, and `absent_hops` needs it to prove the participant never sees it.
        assumption["founderPhrase"] = belief.founder_phrase
    return assumption


def _questionnaire_anchors(entry, stage: str) -> list[dict]:
    anchors = []
    for anchor in entry.anchors_for(stage):
        written = {
            "id": anchor["id"],
            "prompt": anchor["prompt"],
            # A corpus anchor carries a `stage`; the wire's questionnaire does not (the screen
            # emits one stage's). `instructions/corpus.py`'s own note 3.
            "selections": [{k: v for k, v in s.items() if k != "stage"}
                           for s in anchor.get("selections") or []],
        }
        if anchor.get("taps"):
            written["taps"] = [tap_of(entry, t) for t in anchor["taps"]]
        anchors.append(written)
    return anchors


def introduction_for(entry) -> str:
    """`questionnaire.introduction` is `required` on the wire and has a `minLength`, so it is
    never absent and never empty (contract rule 5). Where the entry gives one, it is the entry's;
    where it does not, a fixed sentence naming the entry -- never an invented claim about it."""
    given = (entry.questionnaire or {}).get("introduction")
    if given:
        return str(given)
    who = entry.title.split("—")[0].split("-")[0].strip() or entry.id
    # §2.1's four honest lines, in one sentence: who is asking, and what it is about. The wording
    # is fixed and names the entry (contract rule 5) -- and it says *asked if you'd answer*,
    # because that is the moment the journey names and `ORI-P1` scores.
    return (f"{who} has asked if you'd answer a few questions about something that happened "
            "recently. There are no right answers, and you can skip anything.")


def normalization_rationale_for(entry) -> str:
    given = (entry.expected or {}).get("normalization_rationale")
    if given:
        return str(given)
    return ("Every line is measured against what the founder said, in the units this market uses. "
            f"Taken verbatim from the frozen corpus entry {entry.id}.")


def _assumptions_result(entry, stage: str) -> dict:
    offered = selections_for(entry, stage)
    introduced: set[str] = set()
    first_stage = introducing_stage(entry)
    beliefs = entry.beliefs_for(stage)
    assumptions = [_assumption(entry, b, offered, introduced, first_stage) for b in beliefs]
    anchors = _questionnaire_anchors(entry, stage)
    if len(assumptions) > MAX_ITEMS or len(anchors) > MAX_ITEMS:
        raise CorpusScriptError(
            f"{entry.id}: {stage} has {len(assumptions)} beliefs and {len(anchors)} anchors; the "
            f"wire caps each at maxItems {MAX_ITEMS} (vendored fact V4)")
    return {
        "assumptions": assumptions,
        "questionnaire": {"introduction": introduction_for(entry), "anchors": anchors},
        "normalization_rationale": normalization_rationale_for(entry),
    }


def _interpret_entries(entry) -> list[dict]:
    """One entry per person, **in `entry.answers` order** (contract rule 2) -- the scripted
    executor consumes them in order, one per job, per process, so the run must read people in
    that order too.

    A blank anchor is **absent** (rule 3): `ScreenContextBuilder.anchorsWritten` skips it, so an
    `anchorId` for one is an id the context does not carry and keel-runtime refuses it.
    `invitationId` is **not written** (rule 4) -- only the running stack knows the real one, and
    keel-runtime fills it from the job's own context (RT-002).

    Every anchoring also carries **`stage`** (keel-cloud measured-beliefs decision 18, `Q7`, DRIFT
    #37): an anchor id is unique only within one stage's own questionnaire and free to repeat on
    another, because a link can carry occasions from more than one approved stage and every one of
    them calls its first occasion `A1`. The pair is what the wire now requires and what the reader
    hands back, keyed by `(stage, anchorId)` and never by the bare id -- the frozen corpus numbers
    its ids across the whole entry (still valid; nothing here changes for it), but the script must
    not assume a future entry, or a live model, will.
    """
    entries = []
    for person in entry.people():
        anchorings = []
        for anchor_id, written in person.written():
            anchoring = (written or {}).get("anchoring")
            if anchoring not in ("ANCHORED", "GUESSED"):
                raise CorpusScriptError(
                    f"{entry.id}: {person.person!r} wrote under anchor {anchor_id} but the corpus "
                    f"records anchoring {anchoring!r} -- neither ANCHORED nor GUESSED")
            anchor = entry.anchor(anchor_id)
            if anchor is None or not anchor.get("stage"):
                raise CorpusScriptError(
                    f"{entry.id}: {person.person!r} wrote under anchor {anchor_id!r}, which the "
                    "entry's own questionnaire carries no stage for")
            anchorings.append({"stage": anchor["stage"], "anchorId": anchor_id,
                               "anchoring": anchoring})
        if not anchorings:
            # **A person who wrote nothing is not a reading.** `05-paidly`'s Yara Haddad leaves
            # both translator anchors blank and taps *hasn't happened* on the third, so keel-cloud
            # queues no reading job for her at all ("Nothing new to read", live-confirmed
            # `runs/20260907T151344Z-s006-paidly`). An entry for her would sit in the cursor and
            # hand every later person the wrong judgement -- which is a worse failure than the
            # contract's own "one entry per person" is a promise worth keeping. The order that
            # matters is the order of *readings*, and this is it.
            continue
        entries.append({"outcome": "COMPLETED",
                        "result": {"anchorings": anchorings, "unprompted": [], "flags": []}})
    return entries


def correction_result(entry, correction: Correction) -> dict:
    """`<STAGE>_ASSUMPTIONS.correction` (contract rule 7): the whole card again, plus `reply` and
    `changes[] {heading, before, after}` -- keel-cloud's `correctionContract` requires both.

    The card is re-emitted unchanged except for the one line the founder named: a questionnaire is
    only valid as a whole, so re-emitting the set is what keeps it checkable at confirm, and
    `changes` is what tells the founder that only that line moved.
    """
    result = _assumptions_result(entry, correction.stage)
    target = next((b for b in entry.beliefs_for(correction.stage)
                   if b.id == correction.belief_id), None)
    if target is None:
        raise CorpusScriptError(
            f"{entry.id}: the correction names belief {correction.belief_id!r}, which is not on "
            f"{correction.stage}")
    before = target.statement
    after = correction.expected_change
    for assumption in result["assumptions"]:
        if assumption["heading"] == target.heading:
            assumption["statement"] = after
    result["reply"] = (
        f"Understood — you meant {after} Line “{target.heading}” is redone; "
        "nothing else on this card moved.")
    result["changes"] = [{"heading": target.heading, "before": before, "after": after}]
    return result


def generate(entry, *, correction: Correction | None = None) -> GeneratedScript:
    """The runtime script for one entry (FR-001..FR-003, data-model.md §1).

    A screen the entry cannot produce is **absent, not empty** (contract rule 6): a
    `ScriptedExecutor` with no entry for a screen refuses it by name, which is a better failure
    than answering the wrong shape.
    """
    screens: dict[str, list[dict]] = {}
    for stage in STAGES:
        statement = (entry.statements or {}).get(_STATEMENT_KEY[stage])
        if statement:
            screens[FRAME_SCREEN[stage]] = [
                {"outcome": "COMPLETED", "result": {"statement": str(statement).strip()}}]
        if entry.beliefs_for(stage):
            screens[ASSUMPTIONS_SCREEN[stage]] = [
                {"outcome": "COMPLETED", "result": _assumptions_result(entry, stage)}]
    if correction is not None:
        screens[CORRECTION_SCREEN[correction.stage]] = [
            {"outcome": "COMPLETED", "result": correction_result(entry, correction)}]
    interpret = _interpret_entries(entry)
    if interpret:
        screens["INTERPRET"] = interpret
    return GeneratedScript(
        entry_id=entry.id,
        entry_sha256=entry.sha256,
        source=f"keel-cloud canon/designs/measured-beliefs/corpus/{entry.path.name}",
        screens=screens,
    )


# --------------------------------------------------------------------------------- the typed inputs

def founder_inputs(entry, *, correction: Correction | None = None) -> FounderInputs:
    """What the founder types (data-model.md §2). `language` is recorded and **never typed** --
    `CreateProjectRequest.market` carries only `{country, region}` and the server derives the rest
    (vendored fact V7)."""
    market = entry.market or {}
    statements = entry.statements or {}
    missing = [k for k in ("problem", "solution", "commercial") if not statements.get(k)]
    if missing:
        raise CorpusScriptError(f"{entry.id}: no {', '.join(missing)} statement")
    return FounderInputs(
        project_name=entry.title,
        market=Market(country=market.get("country") or "GB",
                      region=market.get("region"),
                      language=market.get("language") or "en-GB"),
        problem=str(statements["problem"]).strip(),
        solution=str(statements["solution"]).strip(),
        commercial=str(statements["commercial"]).strip(),
        correction=correction,
    )


def _pick(entry, person_name: str, selection: dict, raw) -> Pick:
    values = [str(v) for v in raw] if isinstance(raw, list) else [str(raw)]
    options = [str(o) for o in (selection.get("options") or [])]
    escape = [str(e) for e in (selection.get("escape") or [])]
    # A BUCKETS selection carries no `options` in the corpus -- the buckets are derived from the
    # band by keel-cloud's own builder -- so the entry's own `expected.buckets` is the only list
    # there is to check against, and where it gives none there is nothing to check.
    buckets = [str(b) for b in ((entry.expected or {}).get("buckets") or {}).get(selection["id"], [])]
    known = set(options) | set(escape) | set(buckets)
    is_escape = all(v in escape for v in values) and bool(values)
    is_other = False
    for value in values:
        if value in known:
            continue
        if selection.get("other"):
            is_other = True
            continue
        raise CorpusScriptError(
            f"{entry.id}: {person_name!r} picked {value!r} for selection {selection['id']}, which "
            f"is neither an option ({', '.join(options) or 'none'}) nor an escape "
            f"({', '.join(escape) or 'none'})"
            + (f" nor a bucket ({', '.join(buckets)})" if buckets else "")
            + " and the selection offers no `other` box")
    return Pick(selection_id=selection["id"], values=values, is_escape=is_escape, is_other=is_other)


def person_inputs(entry) -> list[PersonInputs]:
    """What each stranger types (data-model.md §3), keyed by their role's own anchors.

    A person is only ever offered the anchors their role is asked; being offered another role's is
    a refusal, not a shrug -- so this raises rather than quietly widening the set.
    """
    people: list[PersonInputs] = []
    for person in entry.people():
        role_ids = {role_of_anchor(entry, anchor_id) for anchor_id in person.anchors}
        role_ids.discard(None)
        if len(role_ids) != 1:
            raise CorpusScriptError(
                f"{entry.id}: {person.person!r} answers anchors belonging to "
                f"{sorted(role_ids) or 'no'} role(s) -- a person answers exactly one role's set")
        role_id = role_ids.pop()
        offered = set(anchors_for_role(entry, role_id))
        strays = sorted(set(person.anchors) - offered)
        if strays:
            raise CorpusScriptError(
                f"{entry.id}: {person.person!r} is role {role_id!r} and was offered anchor(s) "
                f"{', '.join(strays)}, which that role is not asked")

        # Scoped to this role's own anchors, never the whole entry (design decision 18, DRIFT
        # #37): a selection id is unique only within one stage's own questionnaire, and another
        # role, on another stage, may reuse it. Built fresh per person rather than once for the
        # entry, so a reused id on a role this person is not asked never shadows their own.
        by_selection = {s["id"]: s
                        for anchor in (entry.questionnaire.get("anchors") or [])
                        if anchor.get("id") in offered
                        for s in anchor.get("selections") or []}

        anchors = []
        for anchor_id, written in person.anchors.items():
            written = written or {}
            text = (written.get("text") or "").strip() or None
            anchors.append(AnchorAnswer(anchor_id=anchor_id, text=text,
                                        tap=tap_of(entry, written.get("tap"))))
            if text and written.get("anchoring") not in ("ANCHORED", "GUESSED"):
                raise CorpusScriptError(
                    f"{entry.id}: {person.person!r} wrote under anchor {anchor_id} but the corpus "
                    f"records anchoring {written.get('anchoring')!r}")

        picks = []
        for selection_id, raw in (person.picks or {}).items():
            selection = by_selection.get(selection_id)
            if selection is None:
                raise CorpusScriptError(
                    f"{entry.id}: {person.person!r} picked for selection {selection_id!r}, which "
                    "no anchor offers")
            picks.append(_pick(entry, person.person, selection, raw))
        people.append(PersonInputs(person=person.person, role_id=role_id,
                                    anchors=anchors, picks=picks))
    return people


def inputs_json(entry, founder: FounderInputs, people: list[PersonInputs]) -> dict:
    """`runs/<id>/inputs.json` (contracts/generated-script-contract.md)."""
    return {
        "_entry_id": entry.id,
        "founder": {
            "project_name": founder.project_name,
            "market": asdict(founder.market),
            "problem": founder.problem,
            "solution": founder.solution,
            "commercial": founder.commercial,
            "correction": asdict(founder.correction) if founder.correction else None,
        },
        "people": [asdict(p) for p in people],
    }


# ------------------------------------------------------------------------------------------- main

def _main(argv: list[str]) -> int:
    from stack.config import load_config

    if not argv:
        print(__doc__)
        return 2
    config = load_config(validate=False)
    _, entry = entry_for(config.keel_cloud, argv[0])
    print(json.dumps(generate(entry).to_json(), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":  # pragma: no cover - a developer's five-minute check (quickstart.md)
    import sys

    raise SystemExit(_main(sys.argv[1:]))
