"""keel-cloud's own reading of the corpus: the composed respondent wording and the brief's facts, per entry
(spec 040 FR-005 / FR-006; keel-cloud 088 *The composed wording*, 089 FR-001 / FR-005).

**Nothing here composes or counts.** keel-cloud composes every respondent item from the lock by code
(`RespondentItems`, the frames, `InterviewComposer.spokenFormOf`) and assembles the brief's facts by the same
functions a project's are (`StandingsAssembler`, `BriefFacts.of`). Two of its corpus tests write what they built
for a reader -- `SpokenGuidelinesCorpusTest` writes `build/spoken-corpus.txt` (every entry's items and spoken
blocks) and `BriefFactsCorpusTest` writes `build/brief-facts/<entry>.json` (each entry's whole facts) -- and this
module asks for both the way `compare.py` asks the engine: it shells `./gradlew -q test --rerun --tests <the two>`
in the keel-cloud checkout, once, and reads the files back. Running keel-cloud's tests spends nothing.

What the eval does with them: the **spoken-form marks** (`instructions/spoken.py`) test the composed record once
against the guidelines (§8: "The marks test the record once; the renderings are code and are tested as code"); the
**brief-facts compare** (`instructions/brief_facts.py`) holds keel-cloud's cards and pilot to this repository's own
reading of the corpus (`DRY=1`); and a `BRIEF` case is handed keel-cloud's facts as production would hand them
(judgement call 84).

**A cloud that cannot be asked leaves both marks unmeasured, by name** (call 13): a missing `gradlew`, a non-zero
exit or a missing file is a `CloudCorpusUnavailable` naming the prerequisite, never a zero.

`spoken-corpus.txt` is a reader's text, not a contract (its option lists are Java's `List.toString`, and a label may
carry a comma). It is parsed here with the labels the item can carry -- the registry's fixed answers and the
entry's own lists -- so "Yes, easily" stays one option; anything else is split on ", " (Price's bands and Relative
advantage's three carry none). A structured `build/spoken-corpus.json` is a keel-cloud follow-up (spec 040).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

#: The two keel-cloud corpus tests whose files are read (088, 089).
TESTS = ("com.keeldiscovery.cloud.corpus.SpokenGuidelinesCorpusTest",
         "com.keeldiscovery.cloud.corpus.BriefFactsCorpusTest")
SPOKEN_FILE = Path("build") / "spoken-corpus.txt"
FACTS_DIR = Path("build") / "brief-facts"

PREREQUISITE = ("keel-cloud 088's SpokenGuidelinesCorpusTest (build/spoken-corpus.txt) and 089's "
                "BriefFactsCorpusTest (build/brief-facts/<entry>.json), run by `./gradlew test`")


class CloudCorpusUnavailable(RuntimeError):
    """keel-cloud could not be asked for its composed wording or its facts -- unmeasured, never a score."""


@dataclass(frozen=True)
class ComposedItem:
    """One respondent item as keel-cloud composed it for one corpus entry (the gate aside: its clause is the
    model's, judgement call 13 of keel-cloud 088)."""

    entry: str
    key: str
    part: int
    question: str
    options: tuple
    escape: str | None
    anchor: str | None
    stem: str
    count_line: str | None
    options_line: str
    escape_line: str | None
    transform: str


@dataclass
class CloudCorpus:
    items: dict = field(default_factory=dict)        # entry id -> [ComposedItem]
    facts: dict = field(default_factory=dict)        # entry id -> BriefFacts as JSON
    spoken_text: str = ""
    source: str = ""

    def items_of(self, entry_id: str) -> list:
        return list(self.items.get(entry_id) or [])


def _null(value: str):
    value = value.strip()
    return None if value == "null" else value


def split_options(inner: str, known=()) -> list:
    """`[a, b, c]` read back: at each place, the longest run of ", "-joined pieces that is a label the item can
    carry, else one piece."""
    inner = inner.strip()
    if not inner:
        return []
    pieces = inner.split(", ")
    known = {str(k) for k in known if k}
    out, i = [], 0
    while i < len(pieces):
        best = i + 1
        for j in range(len(pieces), i + 1, -1):
            if ", ".join(pieces[i:j]) in known:
                best = j
                break
        out.append(", ".join(pieces[i:best]))
        i = best
    return out


def parse_spoken(text: str, known_labels=None) -> dict:
    """`build/spoken-corpus.txt` -> `{entry: [ComposedItem]}`. `known_labels(entry, key)` returns the labels an
    item can carry (to keep a comma inside one); `None` splits on every ", "."""
    out, entry, current = {}, None, None
    for line in text.splitlines():
        if line.startswith("== "):
            entry = line[3:].strip()
            out.setdefault(entry, [])
            continue
        if not line.strip() or entry is None:
            continue
        if not line.startswith("  "):
            key, _, rest = line.partition(" [part ")
            current = {"entry": entry, "key": key.strip(), "part": int(rest.rstrip("]").strip() or 0)}
            continue
        label, _, value = line.strip().partition(": ")
        if label == "Q":
            current["question"] = value
        elif label == "options":
            known = known_labels(entry, current["key"]) if known_labels else ()
            current["options"] = tuple(split_options(value.strip()[1:-1], known))
        elif label == "escape":
            current["escape"] = _null(value)
        elif label == "spoken":
            fields = {}
            for part in value.split(" | "):
                name, _, said = part.partition("=")
                fields[name.strip()] = _null(said)
            out[entry].append(ComposedItem(
                entry=entry, key=current["key"], part=current["part"], question=current.get("question", ""),
                options=current.get("options", ()), escape=current.get("escape"), anchor=fields.get("anchor"),
                stem=fields.get("stem") or "", count_line=fields.get("count"),
                options_line=fields.get("options") or "", escape_line=fields.get("escape"),
                transform=fields.get("transform") or ""))
    return out


def known_labels_for(corpus, registry):
    """The labels an entry's item can carry: the registry's fixed answers, Relative advantage's three, the
    entry's own list labels."""
    def known(entry_id, key):
        labels = []
        if registry is not None and registry.has(key):
            labels += [a.get("label") for a in registry.by_key(key).fixed_answers]
        entry = corpus.by_id(entry_id) if corpus is not None else None
        saved = entry.founder_list(key) if entry is not None else None
        labels += [i.get("label") for i in (saved or {}).get("items") or []]
        return labels
    return known


def read(keel_cloud: Path, *, corpus=None, registry=None, entry_ids=None) -> CloudCorpus:
    """The two files, already written -- no Gradle. A missing one is a refusal naming the prerequisite."""
    keel_cloud = Path(keel_cloud)
    spoken = keel_cloud / SPOKEN_FILE
    facts_dir = keel_cloud / FACTS_DIR
    if not spoken.is_file() or not facts_dir.is_dir():
        raise CloudCorpusUnavailable(f"no {spoken} or {facts_dir} -- spoken_form and brief_facts need "
                                     f"{PREREQUISITE}")
    text = spoken.read_text(encoding="utf-8")
    facts = {}
    for path in sorted(facts_dir.glob("*.json")):
        if entry_ids is None or path.stem in entry_ids:
            facts[path.stem] = json.loads(path.read_text(encoding="utf-8"))
    return CloudCorpus(items=parse_spoken(text, known_labels_for(corpus, registry)), facts=facts,
                       spoken_text=text, source=str(keel_cloud))


def produce(keel_cloud: Path, *, corpus=None, registry=None, timeout_s: float = 900.0) -> CloudCorpus:
    """Runs keel-cloud's two corpus tests (`--rerun`, so the files are today's) and reads them back."""
    keel_cloud = Path(keel_cloud)
    gradlew = keel_cloud / "gradlew"
    if not gradlew.is_file():
        raise CloudCorpusUnavailable(f"no {gradlew} -- spoken_form and brief_facts need {PREREQUISITE}")
    argv = [str(gradlew), "-q", "test", "--rerun"]
    for test in TESTS:
        argv += ["--tests", test]
    try:
        done = subprocess.run(argv, cwd=str(keel_cloud), capture_output=True, text=True, timeout=timeout_s)
    except (OSError, subprocess.SubprocessError) as exc:
        raise CloudCorpusUnavailable(f"could not run keel-cloud's corpus tests: {exc}; needs {PREREQUISITE}") from exc
    if done.returncode != 0:
        tail = (done.stderr.strip() or done.stdout.strip())[-2000:]
        raise CloudCorpusUnavailable(f"keel-cloud's corpus tests exited {done.returncode} -- spoken_form and "
                                     f"brief_facts are UNMEASURED until {PREREQUISITE} pass.\n{tail}")
    return read(keel_cloud, corpus=corpus, registry=registry)


def copy_into(run_dir: Path, keel_cloud: Path) -> Path:
    """The two files, kept in the bundle (`cloud-corpus/`) so a re-score reads what the run read."""
    target = Path(run_dir) / "cloud-corpus"
    (target / "brief-facts").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(keel_cloud) / SPOKEN_FILE, target / "spoken-corpus.txt")
    for path in sorted((Path(keel_cloud) / FACTS_DIR).glob("*.json")):
        shutil.copyfile(path, target / "brief-facts" / path.name)
    return target


def read_bundle(run_dir: Path, *, corpus=None, registry=None) -> CloudCorpus:
    """`copy_into`'s files, read back as `read` reads keel-cloud's (a re-score asks no Gradle)."""
    target = Path(run_dir) / "cloud-corpus"
    spoken = target / "spoken-corpus.txt"
    if not spoken.is_file():
        raise CloudCorpusUnavailable(f"{run_dir} keeps no cloud-corpus/ -- the run did not read {PREREQUISITE}")
    text = spoken.read_text(encoding="utf-8")
    facts = {p.stem: json.loads(p.read_text(encoding="utf-8"))
             for p in sorted((target / "brief-facts").glob("*.json"))}
    return CloudCorpus(items=parse_spoken(text, known_labels_for(corpus, registry)), facts=facts,
                       spoken_text=text, source=str(target))
