"""The golden corpus, read and never written (spec 009 FR-001, data-model.md §1).

`canon/designs/measured-beliefs/corpus/*.yaml` in the keel-cloud checkout froze at the end of
step 3 of the design's §10. This module opens those files, hashes them on the way in, and offers
`verify_unchanged()` so the end of a run can prove nothing here moved while it ran. **If an
instruction cannot reach a golden belief, the instruction is wrong** -- or the design is, and it
goes back to step 1. Never the corpus.

Three things the corpus says differently from the wire, and this package has to carry:

1. **`founderPhrase` now has somewhere to go.** keel-cloud spec 029 put it on the wire beside the
   band (design §8.1 step 4), so a corpus belief's own phrase has something to be compared with.
   It is a scored field, and `score.py` reads it beside the band because a right band from a
   phrase the founder never used is a different fault from a wrong band.
2. **Taps are English here and enum names on the wire.** The corpus writes *hasn't happened*; the
   contract wants `HASNT_HAPPENED`. That table lives in `context.py`, deliberately in one place.
3. **A corpus anchor carries a `stage`; the aggregate's questionnaire does not.** A corpus
   questionnaire is the whole project's, and a screen emits one stage's -- so a stage's expected
   questionnaire is the anchors whose `stage` matches, and their selections.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import yaml

STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")


class CorpusError(RuntimeError):
    """The corpus could not be read, or moved while a run was in flight."""


@dataclass(frozen=True)
class GoldenBelief:
    id: str
    stage: str
    heading: str
    statement: str
    founder_phrase: str | None
    risk: str
    asked_of: str
    mark: str
    expectation: dict
    selection: str
    group: str | None

    @property
    def type(self) -> str:
        return self.expectation.get("type", "")

    @property
    def measure(self) -> dict:
        return self.expectation.get("measure") or {}


@dataclass(frozen=True)
class Person:
    person: str
    anchors: dict          # anchorId -> {text, tap?, anchoring}
    picks: dict

    def written(self) -> list[tuple[str, dict]]:
        """The anchors this person actually wrote something under, in corpus order.

        A blank one is omitted, because `ScreenContextBuilder.anchorsWritten` omits it: the
        aggregate already knows nothing under it counts, so the reader is never shown it and it
        can never appear in any denominator.
        """
        return [(k, v) for k, v in self.anchors.items() if (v.get("text") or "").strip()]


@dataclass(frozen=True)
class Entry:
    id: str
    title: str
    market: dict
    statements: dict
    roles: list
    beliefs: list
    questionnaire: dict
    answers: list
    expected: dict
    path: Path
    sha256: str

    def beliefs_for(self, stage: str) -> list:
        return [b for b in self.beliefs if b.stage == stage]

    def role(self, role_id: str) -> dict | None:
        for role in self.roles:
            if role.get("id") == role_id:
                return role
        return None

    def anchors_for(self, stage: str) -> list:
        """This stage's own anchors -- note 3 above: the corpus's questionnaire is the project's."""
        return [a for a in (self.questionnaire.get("anchors") or []) if a.get("stage") == stage]

    def anchor(self, anchor_id: str) -> dict | None:
        for anchor in self.questionnaire.get("anchors") or []:
            if anchor.get("id") == anchor_id:
                return anchor
        return None

    def people(self) -> list[Person]:
        return [Person(person=a["person"], anchors=a.get("anchors") or {},
                       picks=a.get("picks") or {}) for a in self.answers]


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


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corpus_dir(keel_cloud: Path) -> Path:
    return Path(keel_cloud) / "canon" / "designs" / "measured-beliefs" / "corpus"


def load(keel_cloud: Path) -> Corpus:
    """Every `NN-name.yaml` in the corpus directory, in filename order."""
    directory = corpus_dir(keel_cloud)
    if not directory.is_dir():
        raise CorpusError(
            f"no corpus at {directory} -- this eval reads keel-cloud's own frozen golden set, and "
            "cannot invent one")
    files = sorted(p for p in directory.glob("*.yaml"))
    if not files:
        raise CorpusError(f"{directory} holds no *.yaml entries")

    entries, hashes = [], {}
    for path in files:
        digest = _sha256(path)
        hashes[str(path)] = digest
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        entries.append(_entry(raw, path, digest))
    return Corpus(entries=entries, directory=directory, hashes=hashes)


def _entry(raw: dict, path: Path, digest: str) -> Entry:
    beliefs = [
        GoldenBelief(
            id=b["id"],
            stage=b["stage"],
            heading=b.get("heading", ""),
            statement=b.get("statement", ""),
            founder_phrase=b.get("founderPhrase"),
            risk=b.get("risk", ""),
            asked_of=b.get("askedOf", ""),
            mark=b.get("mark", ""),
            expectation=b.get("expectation") or {},
            selection=b.get("selection", ""),
            group=b.get("group"),
        )
        for b in raw.get("beliefs") or []
    ]
    return Entry(
        id=raw["id"],
        title=raw.get("title", ""),
        market=raw.get("market") or {},
        statements=raw.get("statements") or {},
        roles=raw.get("roles") or [],
        beliefs=beliefs,
        questionnaire=raw.get("questionnaire") or {},
        answers=raw.get("answers") or [],
        expected=raw.get("expected") or {},
        path=path,
        sha256=digest,
    )
