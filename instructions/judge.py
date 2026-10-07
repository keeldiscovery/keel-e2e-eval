"""The bounded tie-breaker (spec 009 FR-010), narrowed at `MARKS_VERSION` 9 to one question (spec
029 FR-005/FR-015, research R8; judgement calls 29 and 32).

**What the judge may do.** It sees one question a model wrote for a founder or a stranger, and the
golden mechanism in one line, and answers one word: does this question tell a stranger what the
proposed solution is -- `SAME` (it reveals it: the fault) or `DIFFERENT`. That is the only place
`no_leak` needs a reading rather than a rule: a hit on a stem the problem's own world spells with
another inflection (*listens* in the mechanism, *listened* in a story) might be the problem's word
or the solution's, and only a reader can say (decision 17: inflection collisions only). Every other
`no_leak` hit is a fault by code, and nothing else in the rubric asks a judge at all.

At v8 the judge read option lists, expected options and ties between beliefs. All three retired with
`align.py` (call 29): a calibration answer is a typed pick against the registry, and there is
nothing left to align by meaning.

**Why it is bounded, and why the fraction is reported.** Every call is one small prompt, the answers
are cached within a run so the same question is never paid for twice, and every call, its input and
its answer are recorded. `judged_fraction` -- the share of `no_leak` hits the judge decided -- goes
in the scorecard and on the report (call 14), so a reader can discount the mark by exactly the
amount a model decided.

**It is not the executor.** These calls are this repo's own, not production's: no nonce fence, no
response contract, no `build_prompt`. Nothing the judge reads is a founder's or a stranger's text --
it is a model's question and the corpus's mechanism, both already in the bundle.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field

# Cheap, short, and closed: one question, one word back.
_ARGV = ["claude", "-p", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
         "--no-session-persistence", "--max-turns", "1", "--output-format", "json"]

_SAME = "SAME"
_DIFFERENT = "DIFFERENT"

#: Names that would move the ruler rather than the thing measured. A subject pinned to an effort
#: level asks for it through the environment -- `CLAUDE_CODE_EFFORT_LEVEL`, the form
#: keel-runtime's `_build_env` allow-lists through to the CLI -- and `subprocess.run` inherits the
#: parent environment when it is given no `env=`. So a run launched at one effort level would have
#: scored itself at that level too, silently: 392 judge calls on the run of record's shape, at
#: whatever the subject was set to. The judge is this repo's ruler and always answers at the CLI's
#: own default, so these are **stripped** rather than overridden -- there is no value of
#: `CLAUDE_CODE_EFFORT_LEVEL` that means "the default", and the only way to ask for the default is
#: to say nothing.
JUDGE_UNSET_ENV = ("CLAUDE_CODE_EFFORT_LEVEL", "CLAUDE_CODE_ALWAYS_ENABLE_EFFORT",
                   "CLAUDE_CODE_MAX_EFFORT_REMINDER")


def judge_env(environ=None) -> dict:
    """The environment a judge call runs in: the parent's, minus every knob above.

    Everything else is passed through untouched -- `PATH` finds the CLI, `HOME` finds its
    credentials, and a judge that could not authenticate would answer `None` to every question and
    quietly cost the run its recall.
    """
    source = os.environ if environ is None else environ
    return {name: value for name, value in source.items() if name not in JUDGE_UNSET_ENV}


@dataclass
class Judge:
    """Answers meaning questions, records every one, and can be switched off entirely."""

    enabled: bool = True
    timeout_s: float = 60.0
    calls: list = field(default_factory=list)
    _cache: dict = field(default_factory=dict)

    @property
    def call_count(self) -> int:
        return len(self.calls)

    def available(self) -> bool:
        return self.enabled and shutil.which("claude") is not None

    # ------------------------------------------------------------------------ the one question

    def reveals_solution(self, question_text: str, mechanism_one_liner: str, *,
                         context: str = "") -> bool:
        """Does this question tell a stranger what the proposed solution is? marks-v9 §2.3's
        closed question, verbatim in substance: `SAME` means it reveals the solution, and that is
        the fault; `DIFFERENT`, or no answer at all, is not."""
        return self._same(
            "reveals_solution",
            "A question will be put to a stranger before they are told anything about a proposed "
            "solution.\n"
            "Does this question tell a stranger what the proposed solution is: "
            f"{mechanism_one_liner}?\n\n"
            "Answer SAME if a stranger reading the question would learn what the solution is or "
            "how it works. Answer DIFFERENT if the question only asks about the problem as they "
            "lived it, even where it shares a word with the solution.\n\n"
            f"The question: {question_text}\n",
            context)

    # ------------------------------------------------------------------------------ plumbing

    def _same(self, kind: str, question: str, context: str) -> bool:
        if not self.available():
            return False
        answer = self._ask(kind, question + f"\nReply with one word: {_SAME} or {_DIFFERENT}.",
                           context)
        return answer is not None and _SAME in answer.upper()

    def _ask(self, kind: str, question: str, context: str) -> str | None:
        key = (kind, question)
        if key in self._cache:
            return self._cache[key]
        try:
            done = subprocess.run(_ARGV, input=question, capture_output=True, text=True,
                                  timeout=self.timeout_s, env=judge_env())
            body = json.loads(done.stdout.strip().splitlines()[-1]) if done.stdout.strip() else {}
            answer = None if body.get("is_error") else str(body.get("result") or "").strip()
        except Exception as exc:                  # noqa: BLE001 - a judge that fails answers None
            answer = None
            self.calls.append({"kind": kind, "context": context, "error": str(exc)})
            self._cache[key] = answer
            return answer
        self.calls.append({"kind": kind, "context": context, "question": question,
                           "answer": answer})
        self._cache[key] = answer
        return answer


class NoJudge(Judge):
    """A judge that is never available -- for unit tests, and for `--no-judge`.

    With it an inflection tie is asked of nobody and answers no (`reveals_solution` is `False` on
    no answer), so the run's `leak_judged` and `judge_calls` say exactly how many ties went
    undecided.
    """

    def available(self) -> bool:
        return False
