"""The curated proof run: `07-mulchrun`, end to end, with a **real model doing every reading**.

    .venv/bin/python -m evals.tools.curated_proof_run

**Why this is a tool and not a scenario.** Every other module under `evals/` asserts a corpus
entry's own `expected` section and its verdict is the finding. This one asserts almost nothing
about what the model concluded, on purpose: `keel-marketing/proof/README.md` records that frames
`05` (the overview) and `08` (the download) carry the referee's own placeholder where *What this
says* should be -- *"Scripted by the referee from corpus entry 07-mulchrun, not written by a
model."* -- and the only honest fix is to shoot those two frames from a run whose paragraph, whose
card summaries and whose nineteen readings are a real model's. A real model is **allowed** to land
different bands, different verdicts and a different median from the hand-worked corpus, so a run
that failed when it did would be measuring the weather. What comes out is recorded, not asserted.

**What is real here, and what is still the corpus's.** The founder is `Eval Founder` (the stub's
own founder A, the name the six kept frames already carry) and the nineteen participants are the
corpus's invented people answering their corpus answers verbatim -- both declared as example data
in `proof/README.md`. Everything the *product* produces is the model's: the three claims'
extraction (three jobs), every one of the nineteen readings, and the `BRIEF` paragraph keel-cloud
starts by itself once the last reading lands. That is one job more than the frames strictly need
-- the extraction could have been scripted -- and it is spent deliberately: a page that shows a
model's paragraph over a referee's questionnaire would be true in the small and false in the
large.

**The one hard problem: a model's questionnaire is not the corpus's questionnaire.**
`harness.browser.ParticipantPage.answer_as` matches the corpus's own anchor and selection prompts
against the rendered page, character for character, because with the scripted executor they *are*
the same strings. Against a real model they are not: the anchor reads *"Walk me through the last
mulch pickup"* where the corpus says *"Think of the last time you picked up mulch for a job…"*, and
a match on the corpus's words would skip every question on the page and submit nineteen empty
forms. So this module carries its own answering pass (`_answer_page`), and it resolves three
things by meaning rather than by string:

- **roles** -- the corpus's two role labels against the rendered role cards, so a person is
  invited as the kind of person the corpus asked them as;
- **anchors and selections** -- greedy one-to-one matching on prompt similarity, best pair first.
  A leftover *anchor* is filled (any story answers any "tell us what happened"); a leftover
  *selection* is not, because a yes/no forced into the nearest spare question is a wrong answer
  the aggregate then counts -- which is what happened, twelve times, on this tool's own first
  live run;
- **the picks themselves** -- *by value, not by label*. A bucket scale is computed by keel-cloud's
  own builder from whatever measure the model extracted, so its labels move when the band moves:
  the corpus's `35 min to 55 min` may render as `30 min to 60 min`. Each corpus pick is reduced to
  a number in a canonical unit (minutes, miles, feet, cubic yards, dollars) and placed in the
  offered band that **contains** it, so a crew lead who sat forty-five minutes in the line is
  recorded at forty-five minutes whatever the model called the band. Where there is no number,
  the same words, the same speaker (*me* is *I did*) or near-identical spelling settle it, and
  what is left goes to `_Translator` -- a model asked to carry one questionnaire's answer across
  to another's words, allowed only to choose among the options on the page or to choose nothing.
  It **translates and never invents**: `picked it up at the supply yard` is `I did`, not `the
  supply yard's truck`, which is what character similarity chose ten times on this tool's first
  live run and is how that run's overview came to say *"none of the 7 crew leads got the mulch to
  the site themselves"* about twelve people who mostly had. Every resolution -- and every one that
  could not be made -- is written into the bundle's `answering.json` and `option-map.json`, which
  is the only way a reader can tell a model that asked a different question from a harness that
  failed to find the same one.

**The money.** `KEEL_JOB_BUDGET_USD=1.00` and `KEEL_JOB_MAX_TURNS=8` ride into the runtime through
keel-connect-skill's own script (`env_extra`), which is the same door S-004 uses and the reason
`runs/DRIFT.md` #46 asks for the caps' *source* to travel with them. Roughly twenty-three jobs are
expected -- three extractions, nineteen readings, one brief -- and the whole run is stopped, hard,
if the envelopes ever total more than `--stop-at` (default $10). The envelopes are read from the
runtime's own `$KEEL_HOME/jobs/` through `harness.canary`, never estimated.

The two frames are written straight over `keel-marketing/proof/`'s own file names at the width the
existing frames were shot at (1280, full page). Nothing else in that repo is touched by this
module: the README rows are a person's edit, made from the `summary.json` this leaves behind.
"""

from __future__ import annotations

import argparse
import difflib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import sync_playwright

from evals.preludes import create_project
from harness import canary as canary_mod
from harness import corpus_script
from harness.browser import (Auth, Chat, Connect, Landing, Overview, ParticipantPage, People,
                             PrintPage, ReviewCard)
from harness.connect import start_runtime_via_skill, stop_runtime
from harness.evidence import finalize_run, new_run_dir, write_generated, write_versions
from harness.steps import Recorder
from stack import runtime as stack_runtime
from stack import web as stack_web
from stack.auth import FOUNDER_ONE
from stack.config import load_config
from stack.lifecycle import boot, quick_gates_pass, teardown
from stack.runtime import home_dir

ENTRY_ID = "07-mulchrun"
SLUG = "curated-proof-run"
STAGES = ("PROBLEM", "SOLUTION", "COMMERCIAL")

#: Where the landing page's frames live, and the two file names `proof/README.md` gives them.
#: The names are that README's, not this module's -- frame 05 is `05-the-overview-three-verdicts`
#: there, and a re-shoot that renamed it would orphan the row that describes it.
PROOF_DIR = Path("/Users/athulrajeev/Documents/projects/keel-marketing/proof")
FRAME_OVERVIEW = "05-the-overview-three-verdicts.png"
FRAME_DOWNLOAD = "08-the-download.png"

#: The window the existing eight frames were shot in: 1280 wide, full page (the PNGs are
#: 1280x731, 1280x1203, 1280x4472 -- one width, one page each, no crop).
VIEWPORT = {"width": 1280, "height": 800}

#: The caps the runtime runs under, carried in explicitly so `harness.canary.cap_sources` reports
#: `env KEEL_JOB_BUDGET_USD` rather than "whatever this shell happened to hold" (DRIFT #46).
JOB_BUDGET_USD = "1.00"
JOB_MAX_TURNS = "8"

#: Benign follow-ups, per stage, for the case a live model answers a claim with a question rather
#: than a confirmation card. Spec 008's own allowance ("`NEEDS_INPUT` passes US1") walked the way
#: S-004 walks it: ordinary sentences about the same ordinary idea, never anything new, bounded at
#: three a stage so a model that will not land a claim costs a known number of real jobs.
FOLLOW_UPS = {
    "PROBLEM": [
        "Crew leads running crews for small landscaping companies in the Dallas suburbs — Plano, "
        "Frisco, McKinney, Allen. They pick up their own mulch at supply yards.",
        "It happens every working day through the spring. Today they drive to the yard, wait in "
        "the line to be loaded, then drive to the job and wheelbarrow the mulch to the beds.",
        "That is everything I have — please write up what you have understood.",
    ],
    "SOLUTION": [
        "The crew lead orders the mulch on their phone the night before, by the cubic yard, and a "
        "supplier drops it at the curb of the job site at a scheduled hour.",
        "It replaces the trip to the supply yard: the crew drives straight to the job in the "
        "morning and the pile is already there when they arrive.",
        "That is everything I have — please write up what you have understood.",
    ],
    "COMMERCIAL": [
        "The crew owner pays $3.50 per cubic yard delivered, on top of what the material costs.",
        "That is about what they already pay per yard in delivery fees, or in fuel and the crew's "
        "time when they haul it themselves. The owner sets it up without anyone else's say-so.",
        "That is everything I have — please write up what you have understood.",
    ],
}


class BudgetStop(RuntimeError):
    """The envelopes total more than `--stop-at`. Raised rather than reported, because the whole
    point of a ceiling is that nothing after it is spent."""


# --------------------------------------------------------------------------- matching by meaning

def _norm(text: Any) -> str:
    return " ".join(str(text or "").split()).strip()


def _fold(text: Any) -> str:
    return _norm(text).casefold()


def _sim(left: Any, right: Any) -> float:
    return difflib.SequenceMatcher(None, _fold(left), _fold(right)).ratio()


#: Words that carry no subject matter, so two questions sharing only these share nothing. Not a
#: general stop-word list -- it is the grammar of a questionnaire, and every domain word (mulch,
#: yard, curb, pile, phone, order, paid) is deliberately outside it.
_GRAMMAR = frozenset("""
a an the this that those these it its there here and or but if so as than then of to in on at for
from by with about into over per any all no not you your yours we our us they them their i me my
mine he she his her was were is are be been being do does did done have has had will would can
could may might must how what when where who whom why which much many long far more most less
one two three thing things get got go went come came take took make made say said tell told think
thought last first next time times ago back out up down off before after
""".split())


def _content(text: Any) -> set[str]:
    return {word for word in re.findall(r"[a-z0-9$.]+", _fold(text)) if word not in _GRAMMAR}


def _prompt_sim(left: Any, right: Any) -> float:
    """How alike two *questions* are -- half spelling, half subject matter.

    A character ratio alone reads *"Was there room at the curb for a truck to drop a pile?"* and
    *"Was that in the last twelve months?"* as 0.42 alike, because questionnaire English is mostly
    grammar; the words that decide what a question is about are the handful of nouns in it. So the
    two halves are weighed together: the spelling ratio keeps near-identical wordings at the top,
    and the overlap of subject words is what tells two questions in the same grammar apart. It is
    used for pairing questions and story boxes, never for placing an answer inside one -- that is
    `_resolve_option`'s job and it has its own rules.
    """
    left_words, right_words = _content(left), _content(right)
    union = left_words | right_words
    overlap = len(left_words & right_words) / len(union) if union else 0.0
    return 0.5 * _sim(left, right) + 0.5 * overlap


def _pair_up(wanted: list, offered: list, *, key_w, key_o, floor: float = 0.0,
             fill_leftovers: bool = True, score=None) -> tuple[list[tuple], list]:
    """Greedy one-to-one matching, **best pair first**, optionally handing out the leftovers.

    Best-first rather than in-order because the first corpus anchor is not necessarily the first
    rendered one: a model may put the commercial anchor ahead of the problem anchor on a page that
    asks both. Pairing the strongest match first and removing both sides stops one confident match
    from being spent on a weak partner.

    **`fill_leftovers` is true for anchors and false for selections**, and the difference is a
    finding rather than a taste. An anchor is a story box: a model that asks for one more story
    than the corpus wrote should still be handed the person's own words, and any story is a
    truthful answer to any *"tell us what happened"*. A selection is a question with a meaning,
    and forcing a leftover across is how twelve people came to answer *"Was there room at the
    curb?"* into *"Who had to okay leaving material out front?"* on the first live run of this
    tool -- a yes/no dropped into a question about permissions, counted by the aggregate, and
    invisible on the screen afterwards. Below `floor` there is no pair at all, which is the
    honest answer when a model asked something the corpus never did.

    Returns `([(wanted, offered|None), ...] in `wanted` order, [offered never paired])`.
    """
    scores = sorted(
        (((score or _sim)(key_w(w), key_o(o)), i, j)
         for i, w in enumerate(wanted) for j, o in enumerate(offered)),
        key=lambda row: (-row[0], row[1], row[2]))
    taken_w: dict[int, int] = {}
    taken_o: set[int] = set()
    for score, i, j in scores:
        if i in taken_w or j in taken_o or score < floor:
            continue
        taken_w[i] = j
        taken_o.add(j)
    if fill_leftovers:
        spare = [j for j in range(len(offered)) if j not in taken_o]
        for i in range(len(wanted)):
            if i not in taken_w and spare:
                taken_w[i] = spare.pop(0)
                taken_o.add(taken_w[i])
    pairs = [(w, offered[taken_w[i]] if i in taken_w else None) for i, w in enumerate(wanted)]
    return pairs, [offered[j] for j in range(len(offered)) if j not in taken_o]


#: Every time word the corpus and keel-cloud's builder use, in minutes. A duration scale can mix
#: units in one label (`55 min to 1 h`), so each number carries its own.
_TIME_MINUTES = {
    "sec": 1 / 60, "secs": 1 / 60, "second": 1 / 60, "seconds": 1 / 60,
    "min": 1.0, "mins": 1.0, "minute": 1.0, "minutes": 1.0,
    "h": 60.0, "hr": 60.0, "hrs": 60.0, "hour": 60.0, "hours": 60.0,
    "day": 1440.0, "days": 1440.0, "week": 10080.0, "weeks": 10080.0,
    "month": 43800.0, "months": 43800.0, "year": 525600.0, "years": 525600.0,
}


def _family(label: str) -> str | None:
    """Which scale a label is on, or `None` for a plain option list. Order matters: *cubic yards*
    is read before *miles* and *feet* because a yard is a length word too, and money is read
    first because `$3.50 a yard` carries both."""
    folded = _fold(label)
    if "$" in folded or "dollar" in folded or "usd" in folded or "cent" in folded:
        return "money"
    if "yard" in folded:
        return "cubic_yards"
    if "mile" in folded:
        return "miles"
    if "feet" in folded or "foot" in folded or re.search(r"\bft\b", folded):
        return "feet"
    if any(re.search(rf"\b{re.escape(word)}\b", folded) for word in _TIME_MINUTES):
        return "time"
    return None


def _numbers(label: str, family: str) -> list[float]:
    """Every number in a label, in the family's canonical unit (minutes / miles / feet / cubic
    yards / dollars)."""
    folded = _fold(label).replace(",", "")
    out: list[float] = []
    for match in re.finditer(r"(\d+(?:\.\d+)?)\s*([a-z]*)", folded):
        value = float(match.group(1))
        if family == "time":
            factor = _TIME_MINUTES.get(match.group(2))
            if factor is None:
                after = [w for w in re.findall(r"[a-z]+", folded[match.end():]) if w in _TIME_MINUTES]
                anywhere = [w for w in re.findall(r"[a-z]+", folded) if w in _TIME_MINUTES]
                factor = _TIME_MINUTES[(after or anywhere or ["min"])[0]]
            value *= factor
        out.append(value)
    return out


def _span(label: str, family: str) -> tuple[float, float] | None:
    """`(low, high)` for one label on a scale -- `under X` opens at zero, `more than X` runs to
    infinity, `X to Y` is itself, a bare number is a point."""
    numbers = _numbers(label, family)
    if not numbers:
        return None
    folded = _fold(label)
    if folded.startswith(("under", "less than", "up to", "below", "fewer than")):
        return (0.0, numbers[0])
    if folded.startswith(("more than", "over", "at least", "above", "longer ago than")) \
            or "more than" in folded:
        return (numbers[0], math.inf)
    if len(numbers) >= 2:
        return (min(numbers[0], numbers[1]), max(numbers[0], numbers[1]))
    return (numbers[0], numbers[0])


def _representative(span: tuple[float, float]) -> float:
    low, high = span
    if high == math.inf:
        return low * 1.5 if low else 1.0
    if low == 0:
        return high / 2
    return (low + high) / 2


#: Ways a person says *the person answering this*. A corpus pick of `me` against a model's option
#: list of `I did / another owner / the office / the customer` is the same answer in another
#: grammar, and character similarity cannot see it: `me` scores 0.29 against `I did` and the pick
#: was simply dropped, five times, on the first live run of this tool.
_SELF_REFERENCE = {
    "me", "i", "i did", "i do", "i did it", "myself", "my call", "my own", "my own call",
    "we", "us", "we did", "we do", "mine", "i set it up", "i arranged it",
}

#: Above this, two labels saying the same thing in slightly different words is the likeliest
#: reading (`built into the material price` / `rolled into the material price`). Below it, a
#: character ratio is guessing, and the run asks a model instead -- `picked it up at the supply
#: yard` scores 0.56 against **`the supply yard's truck`**, which is the opposite answer, and it
#: was taken ten times before this floor existed.
_WORDING_FLOOR = 0.82


def _is_self_reference(text: str) -> bool:
    return _fold(text).strip(" .!") in _SELF_REFERENCE


def _resolve_option(value: str, options: list[str], *,
                    oracle: "_Translator | None" = None,
                    asked: str = "", corpus_question: str = "") -> tuple[str | None, str]:
    """One corpus pick against the labels this page actually offered. Returns `(label, how)`.

    Passes, in falling order of confidence: the same words; the same **speaker** (a self-reference
    against a self-reference); the same **number**, placed in the band that contains it, or the
    end of the scale it runs off; near-identical wording; and, for anything left, a model asked to
    carry one questionnaire's answer across to another's words. Anything the last pass will not
    place is left unanswered, which is the truthful record of a model that asked something the
    corpus never did.
    """
    if not options:
        return None, "nothing offered"
    folded = {_fold(option): option for option in options}
    if _fold(value) in folded:
        return folded[_fold(value)], "same words"
    if _is_self_reference(value):
        same_speaker = [option for option in options if _is_self_reference(option)]
        if len(same_speaker) == 1:
            return same_speaker[0], "the same person speaking"

    family = _family(value)
    if family:
        wanted_span = _span(value, family)
        scaled = [(option, _span(option, family)) for option in options
                  if _family(option) == family]
        scaled = [(option, span) for option, span in scaled if span]
        if wanted_span and scaled:
            point = _representative(wanted_span)
            covering = [(option, span) for option, span in scaled
                        if span[0] <= point <= span[1]]
            if covering:
                # The narrowest band that holds the number: a scale that offers both `1 to 2 h`
                # and `more than 1 h` means the tighter of the two.
                option, _span_of = min(covering, key=lambda row: (row[1][1] - row[1][0]))
                return option, f"same number ({point:g})"
            # Off the end of the model's scale: take the scale's own end, in the order the page
            # drew it, rather than the nearest *numbered* band. The bottom row of a scale is
            # often the one with no number in it at all (`today or yesterday`), and a person who
            # picked up mulch this morning belongs there and not in `2 to 7 days ago`.
            finite = [span[1] for _o, span in scaled if span[1] != math.inf]
            if point < min(span[0] for _o, span in scaled):
                return options[0], f"the bottom of the scale ({point:g})"
            if finite and point > max(finite):
                return options[-1], f"the top of the scale ({point:g})"
            nearest = min(scaled, key=lambda row: min(abs(point - row[1][0]),
                                                      abs(point - min(row[1][1], 1e18))))
            return nearest[0], f"nearest band to {point:g}"

    best, score = None, 0.0
    for option in options:
        ratio = _sim(option, value)
        if ratio > score:
            best, score = option, ratio
    if best is not None and score >= _WORDING_FLOOR:
        return best, f"the same words differently spelled ({score:.2f})"
    if oracle is not None:
        carried, how = oracle.carry_across(corpus_question, value, asked, options)
        if carried is not None:
            return carried, how
    return None, f"no match (closest was {best!r} at {score:.2f})"


class _WebWatchdog(threading.Thread):
    """Brings keel-web back up if it goes down while the run is in flight, and says so.

    keel-web is a **vite dev server on a shared development machine**, and twice in one evening it
    went away underneath this run -- once mid-`SOLUTION`, once mid-`PROBLEM` -- taking three real
    model jobs with it each time, because the app stops polling when its own server stops
    answering and a review that has already landed on the wire never opens itself. Nothing about
    the product was wrong either time; the referee's own web server had been killed by whatever
    else was running on the machine.

    `stack.web.up` is idempotent and vite comes back in about a fifth of a second, so this is the
    cheapest possible fix: look every ten seconds, restart if it is gone, and **record every
    restart in the bundle**, because a run that quietly repaired its own stack and did not say so
    would be evidence of nothing. It is deliberately not a general stack watchdog: keel-cloud
    holds the state and postgres holds keel-cloud's, and either of those going down is a finding
    to report rather than a blip to paper over.
    """

    def __init__(self, config, *, every_s: float = 10.0) -> None:
        super().__init__(daemon=True, name="keel-web-watchdog")
        self.config = config
        self.every_s = every_s
        self.restarts: list[str] = []
        self._stop = threading.Event()

    def run(self) -> None:
        while not self._stop.wait(self.every_s):
            try:
                if stack_web.is_up(self.config):
                    continue
                stack_web.up(self.config)
                stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                self.restarts.append(stamp)
                print(f"[proof] keel-web had gone; restarted it at {stamp}", flush=True)
            except Exception as exc:  # noqa: BLE001 - a watchdog never takes the run down
                self.restarts.append(f"could not restart keel-web: {exc}")

    def stop(self) -> None:
        self._stop.set()


class _Translator:
    """Carries one questionnaire's answer across to another questionnaire's words, by asking a
    model -- **the referee's own `claude -p`, not the product's runtime**.

    This is the last pass of `_resolve_option` and it exists because the four before it are
    spelling rules, and the thing that defeats them is meaning. The corpus person answered *"how
    did the mulch get to the job?"* with *"picked it up at the supply yard"*; the model's own form
    asks *"who got the mulch to the site that time?"* and offers *I did · someone on my crew · the
    supply yard's truck · an outside hauler*. The right answer is **I did** and the closest
    spelling is **the supply yard's truck** -- the opposite answer, taken ten times before this
    class existed, which is what made the first live run's overview read *"none of the 7 crew
    leads got the mulch to the site themselves"* about twelve people who mostly had.

    **It translates; it never invents.** It is only ever shown a question the corpus asked, the
    answer the corpus recorded, and the options this page offers, and it may only answer with one
    of those options or with nothing. A question the corpus never asked is never put to it, and no
    participant's words are ever composed here: a blank line on the overview is the correct
    record of a model that asked something this corpus cannot answer, and filling it would be
    inventing a person's answer, which is the one thing a proof frame must not contain.

    Every call is cached on its own question/answer/options triple -- nineteen people share about
    a dozen of them -- and every mapping it makes is written into the bundle's `option-map.json`
    beside the answers, so a reader can check the translation the same way they check the picks.
    """

    def __init__(self, *, model_cli: str = "claude") -> None:
        self.cli = shutil.which(model_cli)
        self.cache: dict[tuple, dict[str, Any]] = {}
        self.calls = 0
        self.cost_usd = 0.0

    def available(self) -> bool:
        return self.cli is not None

    def carry_across(self, corpus_question: str, answer: str, asked: str,
                     options: list[str]) -> tuple[str | None, str]:
        if not self.available():
            return None, "no model to ask"
        key = (_norm(corpus_question), _norm(answer), _norm(asked), tuple(options))
        if key in self.cache:
            hit = self.cache[key]
            return hit["option"], f"{hit['how']} (cached)"
        prompt = (
            "A person answered one questionnaire. They are now being shown a different "
            "questionnaire that asks about the same thing in its own words. Carry their answer "
            "across.\n\n"
            f"They were asked: {_norm(corpus_question) or '(question not recorded)'}\n"
            f"They answered: {_norm(answer)}\n\n"
            f"The new question is: {_norm(asked)}\n"
            "Its options are:\n"
            + "\n".join(f"{n}. {option}" for n, option in enumerate(options, start=1))
            + "\n\nWhich of these options best stands for what they said? Take the closest "
              "one -- it does not have to be worded the same way, only to mean the same thing "
              "about them. Reply with 0 only if their answer is about something none of these "
              "options covers at all. Reply with the number alone and nothing else.")
        try:
            done = subprocess.run(
                [self.cli, "-p", "--tools", "", "--max-turns", "1", "--output-format", "json",
                 "--no-session-persistence", prompt],
                capture_output=True, text=True, timeout=120)
            body = json.loads(done.stdout.strip().splitlines()[-1]) if done.stdout.strip() else {}
        except Exception as exc:  # noqa: BLE001 - a translator that cannot answer leaves a blank
            self.cache[key] = {"option": None, "how": f"the model could not be asked: {exc}"}
            return None, self.cache[key]["how"]
        self.calls += 1
        self.cost_usd += float(body.get("total_cost_usd") or 0.0)
        picked = re.search(r"-?\d+", str(body.get("result") or ""))
        index = int(picked.group(0)) if picked else 0
        if body.get("is_error") or not 1 <= index <= len(options):
            self.cache[key] = {"option": None, "how": "the model placed it nowhere"}
        else:
            self.cache[key] = {"option": options[index - 1], "how": "carried across by a model"}
        return self.cache[key]["option"], self.cache[key]["how"]

    def to_json(self) -> list[dict[str, Any]]:
        return [{"they_were_asked": key[0], "they_answered": key[1], "this_page_asks": key[2],
                 "offered": list(key[3]), "carried_to": hit["option"], "how": hit["how"]}
                for key, hit in self.cache.items()]


# ----------------------------------------------------------------------------------- the walking

def _connect(page, config, recorder, *, executor: str, script_path: Path | None = None) -> dict:
    env_extra = {"KEEL_JOB_BUDGET_USD": JOB_BUDGET_USD, "KEEL_JOB_MAX_TURNS": JOB_MAX_TURNS}
    if script_path is not None:
        # `--executor scripted` is the free rehearsal (`--executor scripted` on the command line):
        # it walks every screen this tool touches, costs nothing, and proves the plumbing before
        # a run that spends real money on the same path. It is never how a frame is shot -- a
        # scripted paragraph is the exact thing `proof/README.md` refuses to ship.
        env_extra["KEEL_SCRIPT"] = str(script_path)
    result = start_runtime_via_skill(
        config, recorder, executor=executor, env_extra=env_extra)
    if result.get("outcome") == "authorization_started":
        connect = Connect(page, recorder)
        connect.open(result["verification_uri"])
        connect.approve()
        connect.wait_for_connected(timeout_s=60)
        connect.go_to_projects()
    return result


def _walk_stage_live(page, recorder, web_base: str, project_id: str, stage: str, statement: str,
                     *, turn_timeout_s: float) -> dict[str, Any]:
    """One stage, against a live model: send the claim, answer a question if one comes back,
    save whatever the agent understood, wait for the review, **approve it as it stands**.

    Deliberately not `evals.preludes.walk_stage`: that one asserts the confirmation card reads
    the founder's statement *verbatim*, which is true of a scripted executor answering from the
    corpus and false of any model writing in its own words. Approving as-is is the run's own
    instruction -- the frames are supposed to show what the product produced, not what the
    referee would have preferred.
    """
    chat = Chat(page, recorder)
    chat.send(statement)
    chat.wait_for_agent_turn(timeout_s=turn_timeout_s)
    card = chat.confirmation_card()
    asked = 0
    for follow_up in FOLLOW_UPS[stage]:
        if card is not None:
            break
        chat.send(follow_up)
        chat.wait_for_agent_turn(timeout_s=turn_timeout_s)
        card = chat.confirmation_card()
        asked += 1
    if card is None:
        raise AssertionError(
            f"the {stage} claim never reached a confirmation card after {asked} benign "
            "follow-ups; there is nothing to approve and no questionnaire to invite anyone to")
    chat.save_confirmation()
    try:
        chat.wait_for_review(project_id, stage, timeout_s=turn_timeout_s)
    except TimeoutError:
        # **The review not opening itself is not the same as the beliefs not landing.** keel-web
        # is a dev server on a shared machine and it died under two runs of this tool; when it
        # does, the app stops polling and the card that is already on the wire never appears. The
        # watchdog puts the server back, and this goes and looks -- rather than throwing away
        # three real model jobs because a dev server blinked. `ReviewCard.open` navigates afresh
        # and waits on its own, so a stage that genuinely has no card still fails, one step later
        # and for the right reason.
        recorder.note(f"the {stage} review card never opened itself; going to look for it",
                      party="stack", ok=True)
        page.wait_for_timeout(5_000)
    review = ReviewCard(page, recorder, web_base)
    review.open(project_id, stage)
    lines = review.lines()
    review.approve()
    review.continue_onward()
    return {"stage": stage, "understood": card["claim"], "follow_ups": asked,
            "lines": [line["heading"] for line in lines]}


def _match_roles(entry, rendered: list[dict]) -> dict[str, str]:
    """`{corpus role id: the label on the founder's own People screen}`.

    **Not one-to-one, and that is the point.** How many kinds of person an idea depends on is the
    model's finding, not the corpus's: `07-mulchrun` separates the crew lead who fetches the mulch
    from the owner who pays for it, and a live run that read the commercial claim as *"the crew
    owner is both who gets the mulch and who pays"* produced **one** role card for both. Refusing
    that is a referee insisting a model reach its own conclusion; the honest thing is to invite
    each corpus person as the nearest kind of person this project actually has, and to record
    which card that was. Two corpus roles may therefore land on one card, and a card the corpus
    has nobody for is simply never invited.
    """
    if not rendered:
        raise AssertionError("the People screen shows no kind of person at all; nobody can be "
                             "invited to anything")
    out: dict[str, str] = {}
    for role in entry.roles or []:
        wanted = f"{role.get('label')} {role.get('about')}"
        card = max(rendered, key=lambda c: _sim(f"{c.get('label')} {c.get('about')}", wanted))
        out[role["id"]] = card["label"]
    return out


def _answer_page(participant: ParticipantPage, person, entry, *,
                 oracle: _Translator | None = None) -> dict[str, Any]:
    """One corpus person's whole answer, typed into whatever questions the model asked.

    See this module's docstring for why `ParticipantPage.answer_as` cannot be used here. Two
    things in the shape of this function are scars, and both are worth reading before changing it:

    **A story box is matched on the questions under it, by subject.** Corpus `A1` opens *"Think of
    the last time you picked up mulch for a job…"* and a live model's two story boxes opened
    *"Think back to the last job you ran where mulch went down…"* and *"Think of the last job where
    you spread mulch…"*. On the opening line alone the second one wins on spelling, and the run put
    the pickup story under the box about spreading. Every story box opens with the same *"think of
    the last…"* grammar, so the opening line cannot tell them apart at all; the questions
    underneath can, and `_prompt_sim` weighs their subject words rather than their grammar.

    **The picks are matched across the whole page, not inside their anchor's block.** Even with the
    better key, a story box paired one place out drags every question under it out of reach, and
    the failure is silent: `runs/20260910T032541Z` placed eighteen picks out of a hundred and
    thirty-six and produced an overview reading *"nobody has described a real mulch run"* about
    nineteen people who all had. A question means what it asks whichever box it sits under, so
    *"How long were you at the yard?"* is matched against every question the page asks and then
    typed into the block that owns it. The anchor pairing now decides only where each **story**
    goes.
    """
    rendered = _sectioned_blocks(participant)
    corpus_anchors = [(answer, entry.anchor(answer.anchor_id) or {}) for answer in person.anchors]

    def corpus_block(row) -> str:
        _answer, anchor = row
        return " ".join(s.get("prompt") or "" for s in anchor.get("selections") or [])

    def rendered_block(block) -> str:
        return " ".join(block.get("selections") or [])

    # Within the stage first, and only across stages when the page has no sections to go by: the
    # solution's story belongs in the solution's box even on a run whose solution questions
    # happen to spell like the commercial ones.
    def rank_of(anchor: dict):
        return STAGES.index(anchor["stage"]) if anchor.get("stage") in STAGES else None

    pairs: list[tuple] = []
    used: list[dict] = []
    for rank in sorted({rank_of(a[1]) for a in corpus_anchors}, key=lambda r: (r is None, r)):
        mine = [a for a in corpus_anchors if rank_of(a[1]) == rank]
        free = [b for b in rendered if b not in used]
        candidates = [b for b in free if b.get("rank") == rank] or free
        paired, _spare = _pair_up(mine, candidates, key_w=corpus_block,
                                  key_o=rendered_block, score=_prompt_sim)
        pairs.extend(paired)
        used.extend(block for _w, block in paired if block is not None)

    record: dict[str, Any] = {"person": person.person, "anchors": [], "picks": [], "unmatched": []}
    hidden: set[str] = set()
    for (answer, _corpus_anchor), block in pairs:
        if block is None:
            record["unmatched"].append({"anchor": answer.anchor_id,
                                        "why": "the page has no story box left for it"})
            continue
        participant.tell_story(block["prompt"], answer.text, tap=answer.tap)
        record["anchors"].append({"anchor": answer.anchor_id, "asked": block["prompt"],
                                  "wrote": bool(answer.text), "tap": answer.tap})
        if answer.tap == "HASNT_HAPPENED":
            # The product hides that anchor's picks entirely behind the tap; there is nothing to
            # fill, and trying would be the harness arguing with the design.
            hidden.add(block["prompt"])

    wanted = []
    for answer in person.anchors:
        anchor = entry.anchor(answer.anchor_id) or {}
        for selection in anchor.get("selections") or []:
            pick = person.pick(selection["id"])
            if pick is not None:
                wanted.append((pick, selection))
    offered = [(block["prompt"], prompt) for block in rendered
               if block["prompt"] not in hidden
               for prompt in block.get("selections") or []]

    sel_pairs, _left = _pair_up(wanted, offered,
                                key_w=lambda row: row[1].get("prompt") or "",
                                key_o=lambda row: row[1],
                                floor=0.48, fill_leftovers=False)
    for (pick, selection), where in sel_pairs:
        if where is None:
            record["unmatched"].append({"selection": selection["id"],
                                        "asked_by_the_corpus": selection.get("prompt"),
                                        "why": "the model's own form asks nothing like it"})
            continue
        anchor_prompt, asked = where
        options = participant.options_for(asked, anchor_prompt=anchor_prompt)
        chosen: list[str] = []
        hows: list[str] = []
        for value in pick.values:
            label, how = _resolve_option(value, options, oracle=oracle, asked=asked,
                                         corpus_question=selection.get("prompt") or "")
            hows.append(f"{value!r} -> {label!r} ({how})")
            if label is not None:
                chosen.append(label)
        if not chosen:
            record["unmatched"].append({"selection": selection["id"], "asked": asked,
                                        "wanted": pick.values, "offered": options,
                                        "why": "nothing offered carries that answer"})
            continue
        roughly = None
        if chosen[-1].endswith("say roughly"):
            family = _family(pick.values[-1])
            span = _span(pick.values[-1], family) if family else None
            roughly = f"{_representative(span):g}" if span else None
        participant.pick(asked, chosen, roughly=roughly, anchor_prompt=anchor_prompt)
        record["picks"].append({"selection": selection["id"], "asked": asked,
                                "picked": chosen, "how": hows})
    return record


#: The stranger's page, block by block, **with the section each block sits under**. The page
#: object reads the blocks (`ParticipantPage.anchors`) and never the sections they are grouped
#: into, and the sections are what say which stage a story belongs to -- keel-web renders one
#: `.sect` per stage, in stage order, and the story boxes follow theirs. Mirrors the page object's
#: own selectors exactly (`div.q:has(> textarea.box)`, and `.picks` as the block's *sibling*), and
#: the caller falls back to `anchors()` if it ever reads a different set.
_BLOCKS_WITH_SECTIONS = r"""
() => {
  const out = [];
  let section = "";
  for (const el of Array.from(document.querySelectorAll(".sect, div.q"))) {
    if (el.classList.contains("sect")) { section = (el.innerText || "").trim(); continue; }
    if (!el.querySelector(":scope > textarea.box")) continue;
    const prompt = el.querySelector(":scope > p");
    const next = el.nextElementSibling;
    const picks = next && next.classList.contains("picks") ? next : null;
    out.push({
      section: section,
      prompt: prompt ? prompt.innerText.trim() : "",
      selections: picks
        ? Array.from(picks.querySelectorAll(":scope > div.q > p")).map((n) => n.innerText.trim())
        : [],
    });
  }
  return out;
}
"""


def _sectioned_blocks(participant: ParticipantPage) -> list[dict[str, Any]]:
    """`anchors()`, plus each block's section and that section's rank on the page.

    A page with three sections in stage order is the ordinary case, and the rank is then the
    stage: a story about the last mulch pickup belongs in section 1 whatever the box's opening
    line says. Where the read disagrees with the page object about how many story boxes there are
    -- a keel-web change this tool has not seen -- the sections are dropped and every block
    becomes rank `None`, which is the same as not constraining at all.
    """
    blocks = participant.anchors()
    try:
        read = participant.page.evaluate(_BLOCKS_WITH_SECTIONS)
    except Exception:  # noqa: BLE001 - a section read is an optimisation, never a requirement
        read = []
    if len(read) != len(blocks):
        return [{**block, "rank": None} for block in blocks]
    order: list[str] = []
    for row in read:
        if row["section"] and row["section"] not in order:
            order.append(row["section"])
    return [{**block, "section": row["section"],
             "rank": order.index(row["section"]) if row["section"] in order else None}
            for block, row in zip(blocks, read)]


def _cost(keel_home: Path) -> dict[str, Any]:
    rows = canary_mod.read_envelopes(keel_home)
    finished = [row for row in rows if row["envelope"]]
    return {
        "jobs_started": len(rows),
        "jobs_finished": len(finished),
        "total_cost_usd": canary_mod.total_cost(finished),
        "errored": [row["job_id"] for row in finished
                    if (row["envelope"] or {}).get("is_error")],
    }


def _guard(keel_home: Path, stop_at: float, where: str) -> dict[str, Any]:
    spent = _cost(keel_home)
    if spent["total_cost_usd"] > stop_at:
        raise BudgetStop(
            f"the run has spent ${spent['total_cost_usd']:.2f} over {spent['jobs_finished']} jobs "
            f"by {where}, past the ${stop_at:.2f} ceiling -- stopping rather than spending more")
    return spent


def _shoot(page, path: Path, *, label: str) -> dict[str, Any]:
    """One frame, at the width the existing eight were shot at, over its own file name."""
    try:
        page.evaluate("document.fonts.ready")
    except Exception:  # noqa: BLE001 - a font wait must never be the reason a frame is missing
        pass
    page.wait_for_timeout(600)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=True)
    size = page.evaluate(
        "() => ({w: document.documentElement.scrollWidth, h: document.documentElement.scrollHeight})")
    return {"frame": label, "path": str(path), "bytes": path.stat().st_size,
            "page_css_px": size}


# --------------------------------------------------------------------------------------- the run

def run(*, executor: str, stop_at: float, turn_timeout_s: float, read_timeout_s: float,
        proof_dir: Path, keep_stack: bool) -> int:
    config = load_config(profile="eval")
    if not quick_gates_pass(config):
        print("[proof] the eval stack is not up; booting it (this is `make up`)")
        boot(config)
    else:
        print("[proof] attaching to the eval stack already up")

    run_dir = new_run_dir(SLUG)
    write_versions(run_dir, config)
    recorder = Recorder(run_dir)
    keel_home = home_dir(config)
    web_base = f"http://localhost:{config.web_port}"
    cloud_base = f"http://localhost:{config.cloud_port}"
    started = time.monotonic()
    print(f"[proof] run bundle: {run_dir}")

    watchdog = _WebWatchdog(config)
    watchdog.start()

    corpus, entry = corpus_script.entry_for(config.keel_cloud, ENTRY_ID)
    founder = corpus_script.founder_inputs(entry)
    people_inputs = corpus_script.person_inputs(entry)
    write_generated(run_dir, inputs=corpus_script.inputs_json(entry, founder, people_inputs))
    script_path: Path | None = None
    if executor == "scripted":
        write_generated(run_dir, script=corpus_script.generate(entry).to_json())
        script_path = run_dir / "script.json"

    summary: dict[str, Any] = {
        "entry": ENTRY_ID, "founder": FOUNDER_ONE.name, "executor": executor,
        "caps": {"budget_usd": JOB_BUDGET_USD, "max_turns": JOB_MAX_TURNS},
        "run_dir": str(run_dir), "stages": [], "frames": [],
    }
    answering: list[dict[str, Any]] = []
    oracle = _Translator()
    if not oracle.available():
        print("[proof] no `claude` on PATH: a pick whose wording the page does not share will be "
              "left unanswered rather than translated")
    passed = False

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(viewport=dict(VIEWPORT))

        def get(path: str) -> dict:
            return context.request.get(f"{cloud_base}{path}", timeout=20_000).json()

        try:
            page = context.new_page()
            Auth(page, recorder, web_base).sign_in(FOUNDER_ONE)

            # ------------------------------------------------- the runtime, on the real executor
            # The same mechanism S-004 uses to go live, and the only one this repo has: a runtime
            # another session left running is holding another session's executor, so it is asked
            # to go first and the skill's own script starts the new one.
            if stack_runtime.status(config).get("running"):
                stop_runtime(config, recorder)
            _connect(page, config, recorder, executor=executor, script_path=script_path)
            caps = canary_mod.cap_sources(config.keel_runtime, keel_home,
                                          {"KEEL_JOB_BUDGET_USD": JOB_BUDGET_USD,
                                           "KEEL_JOB_MAX_TURNS": JOB_MAX_TURNS})
            print(f"[proof] runtime up on the {executor} executor; caps from {caps}")

            landing = Landing(page, recorder, web_base)
            landing.visit()

            # ------------------------------------------------------- the project, and the claims
            project_id = create_project(page, recorder, web_base, founder)
            print(f"[proof] project {project_id}: {founder.project_name!r}")
            for stage in STAGES:
                walked = _walk_stage_live(page, recorder, web_base, project_id, stage,
                                          founder.statement(stage),
                                          turn_timeout_s=turn_timeout_s)
                summary["stages"].append(walked)
                spent = _guard(keel_home, stop_at, f"the {stage} card")
                print(f"[proof] {stage} approved: {walked['understood'][:70]!r} "
                      f"({len(walked['lines'])} lines, {walked['follow_ups']} follow-ups; "
                      f"${spent['total_cost_usd']:.2f} so far)")

            # ------------------------------------------------------------------ the nineteen
            people = People(page, recorder, web_base)
            people.open(project_id)
            if page.locator(".role").count() == 0:
                people.switch_to_kinds_tab()
            labels = _match_roles(entry, people.role_cards())
            about_of = {role["id"]: _norm(role.get("about")) for role in entry.roles or []}
            summary["roles"] = labels
            print(f"[proof] roles: {labels}")

            urls: dict[str, str] = {}
            for person in people_inputs:
                if page.locator(".role").count() == 0:
                    people.switch_to_kinds_tab()
                people.open_send_popup(labels[person.role_id])
                people.fill_who(person.person, about=about_of.get(person.role_id) or None)
                people.go_to_preview()
                urls[person.person] = people.generate_link(person.person.split()[0])
                people.close_popup()
            print(f"[proof] invited {len(urls)} people")

            for index, person in enumerate(people_inputs, start=1):
                stranger = browser.new_context(viewport=dict(VIEWPORT))
                try:
                    stranger_page = stranger.new_page()
                    participant = ParticipantPage(stranger_page, recorder)
                    participant.open(urls[person.person])
                    answering.append(_answer_page(participant, person, entry, oracle=oracle))
                    participant.submit()
                finally:
                    stranger.close()
                print(f"[proof] {index}/{len(people_inputs)} {person.person} answered")
            (run_dir / "answering.json").write_text(
                json.dumps(answering, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            (run_dir / "option-map.json").write_text(
                json.dumps(oracle.to_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            summary["translations"] = {"calls": oracle.calls,
                                       "referee_cost_usd": round(oracle.cost_usd, 4),
                                       "distinct": len(oracle.cache)}
            unplaced = [u for row in answering for u in row["unmatched"]]
            summary["unanswered_picks"] = len(unplaced)
            print(f"[proof] {oracle.calls} translations "
                  f"(${oracle.cost_usd:.2f} of the referee's own), "
                  f"{len(unplaced)} picks left unanswered")

            # ---------------------------------------------------------------------- the reading
            people.open(project_id)
            people.switch_to_who_tab()
            state = people.read_action_state()
            summary["read_button"] = state
            print(f"[proof] {state['label']!r}")
            with recorder.step("founder has the agent read every new answer",
                               party="founder", kind="browser") as handle:
                handle.record_wire(None, state)
                page.get_by_role("button", name=re.compile("have your agent read", re.I)).click()
                page.wait_for_timeout(2_000)

            # The BRIEF job keel-cloud starts by itself once the last reading lands
            # (`ReadingBatchService.sayWhatThisSays`) is the signal that *every* reading is done,
            # so the paragraph's arrival is what is waited on -- not a toast, which a twenty-
            # minute batch of real jobs outlives.
            deadline = time.monotonic() + read_timeout_s
            paragraph = None
            while True:
                wire = get(f"/v2/projects/{project_id}/overview") or {}
                paragraph = wire.get("whatThisSays")
                if paragraph:
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError(
                        f"no *What this says* paragraph after {read_timeout_s:.0f}s of reading; "
                        f"the wire still offers only its note: {wire.get('whatThisSaysNote')!r}")
                spent = _guard(keel_home, stop_at, "the reading")
                print(f"[proof] reading… {spent['jobs_finished']} jobs done, "
                      f"${spent['total_cost_usd']:.2f}", flush=True)
                time.sleep(20)
            print(f"[proof] *What this says* landed: {paragraph[:90]!r}")

            # ------------------------------------------------------------------------ the frames
            overview = Overview(page, recorder, web_base)
            overview.open(project_id)
            summary["overview"] = {
                "evidence_line": overview.evidence_line(),
                "people_line": overview.people_line(),
                "legend": overview.legend(),
                "what_this_says": overview.what_this_says_paragraph(),
                "cards": overview.stage_cards(),
            }
            summary["frames"].append(_shoot(page, proof_dir / FRAME_OVERVIEW, label="05 overview"))
            shutil.copyfile(proof_dir / FRAME_OVERVIEW, run_dir / FRAME_OVERVIEW)

            print_page = PrintPage(page, recorder, web_base)
            print_page.open(project_id)
            summary["download"] = {
                "title_page": print_page.title_page(),
                "headings": print_page.headings(),
                "sheets": len(print_page.sheets()),
                "quotes": print_page.quotes()[:6],
            }
            summary["frames"].append(_shoot(page, proof_dir / FRAME_DOWNLOAD, label="08 download"))
            shutil.copyfile(proof_dir / FRAME_DOWNLOAD, run_dir / FRAME_DOWNLOAD)

            summary["spend"] = _cost(keel_home)
            summary["cap_sources"] = caps
            summary["corpus_expected_standings"] = entry.expected.get("standings") or {}
            passed = True
        finally:
            watchdog.stop()
            summary["web_restarts"] = watchdog.restarts
            summary["duration_s"] = round(time.monotonic() - started, 1)
            (run_dir / "summary.json").write_text(
                json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            if answering and not (run_dir / "answering.json").exists():
                (run_dir / "answering.json").write_text(
                    json.dumps(answering, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            context.close()
            browser.close()
            finalize_run(run_dir, slug=SLUG, facts=None, passed=passed,
                         failed_step=None if passed else recorder.failed_step,
                         duration_s=time.monotonic() - started)

    if not keep_stack:
        print("[proof] tearing the stack down (`make down`)")
        teardown(config)
    left = subprocess.run(["pgrep", "-fl", "keel_runtime"], capture_output=True, text=True)
    print(f"[proof] pgrep -fl keel_runtime -> {left.stdout.strip() or '(nothing)'}")

    print(json.dumps({key: summary[key] for key in ("run_dir", "spend", "frames", "overview")
                      if key in summary}, indent=2, ensure_ascii=False))
    return 0 if passed else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evals.tools.curated_proof_run",
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--executor", default="claude", choices=("claude", "scripted"),
                        help="the executor the runtime is started on. `claude` is the run of "
                             "record; `scripted` is the free rehearsal, and its paragraph is the "
                             "placeholder this whole exercise exists to replace (default: claude)")
    parser.add_argument("--stop-at", type=float, default=10.0,
                        help="stop the whole run once the envelopes total more than this many "
                             "dollars (default: 10)")
    parser.add_argument("--turn-timeout", type=float, default=420.0,
                        help="seconds to wait on one live agent turn (default: 420)")
    parser.add_argument("--read-timeout", type=float, default=3600.0,
                        help="seconds to wait for every reading and the BRIEF paragraph "
                             "(default: 3600)")
    parser.add_argument("--proof-dir", type=Path, default=PROOF_DIR,
                        help=f"where the two frames are written (default: {PROOF_DIR})")
    parser.add_argument("--keep-stack", action="store_true",
                        help="leave the stack up at the end instead of tearing it down")
    args = parser.parse_args(argv)
    try:
        return run(executor=args.executor, stop_at=args.stop_at, turn_timeout_s=args.turn_timeout,
                   read_timeout_s=args.read_timeout, proof_dir=args.proof_dir,
                   keep_stack=args.keep_stack)
    except BudgetStop as stop:
        print(f"[proof] STOPPED: {stop}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
