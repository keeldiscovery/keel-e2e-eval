"""The bounded tie-breaker (spec 009 FR-010, T025), and — since the founder's decision of
2026-09-06 — the reader of option lists.

**What the judge may do.** It sees two short pieces of text and answers one of a fixed set of
words. It can never assert a pair the structure rejected on a *measurable* ground: an interval pair
whose kinds differ or whose bands cannot overlap never reaches it, because that is arithmetic and
arithmetic does not need an opinion. What does need one is meaning, and there are exactly three
places it is asked for:

1. **A tie** — two or more goldens at the top score for one produced belief. It answers *this one*,
   *that one* or *no match*.
2. **An option list** — whether two lists describe the same answer space (judgement call 11). The
   corpus's option words are one reasonable phrasing; `Q2` requires a belief's list to equal *its
   own selection's* list and never the corpus's, so *"a member of staff"* and *"Signed for it
   without opening anything"* may be the same question asked in two registers, and only a reader
   can say.
3. **An expected option** — whether two expected options mean the same thing, which is what
   exact-match on a Choice became once (2) was true.

**Why it is bounded, and why the fraction is reported.** Every call is one small prompt with two
strings in it, the answers are cached within a run so the same question is never paid for twice,
and the number of calls cannot exceed the number of goldens plus the number of matched Choice
pairs. Every call, its input and its answer are recorded, and `judged_fraction` goes in the
scorecard and on the report — so a reader can discount a score by exactly the amount a model
decided (judgement call 14). Buying recall with a judge costs determinism, and this is the price
tag rather than a hidden subsidy.

**It is not the executor.** These calls are this repo's own, not production's: no nonce fence, no
response contract, no `build_prompt`. Nothing the judge reads is a founder's or a stranger's text —
it is corpus prose and model prose, both already in this bundle.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field

# Cheap, short, and closed: one question, one word back.
_ARGV = ["claude", "-p", "--tools", "", "--strict-mcp-config", "--setting-sources", "",
         "--no-session-persistence", "--max-turns", "1", "--output-format", "json"]

_SAME = "SAME"
_DIFFERENT = "DIFFERENT"


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

    # ------------------------------------------------------------------ the three questions

    def same_answer_space(self, golden_options, produced_options, *, context: str = "") -> bool:
        """Do these two option lists offer the same answers, in different words?"""
        return self._same(
            "answer_space",
            "Two multiple-choice questions were written for the same interview, by two authors.\n"
            "Do these two option lists offer the SAME set of possible answers, allowing for "
            "different wording, register and length?\n"
            "Answer SAME if a person picking from one could pick the corresponding option in the "
            "other. Answer DIFFERENT if they are asking about different things.\n\n"
            f"List A: {json.dumps(list(golden_options))}\n"
            f"List B: {json.dumps(list(produced_options))}\n",
            context)

    def same_expected_option(self, golden_expected, produced_expected, *,
                             context: str = "") -> bool:
        """Do these two expected options name the same answer?"""
        return self._same(
            "expected_option",
            "Two authors each wrote the answer they expect a person to give to the same "
            "interview question.\n"
            "Do these two name the SAME answer, allowing for different wording and register?\n\n"
            f"Answer A: {json.dumps(golden_expected)}\n"
            f"Answer B: {json.dumps(produced_expected)}\n",
            context)

    def pick(self, produced_statement: str, candidates: list) -> int | None:
        """Which of these goldens, if any, is the produced belief? Returns an index, or `None`.

        The one place the judge decides a pair rather than a field. It is offered only goldens the
        structure already accepted as candidates and that tied at the top score, so it is choosing
        between equals, never overruling arithmetic.
        """
        if not self.available() or not candidates:
            return None
        listed = "\n".join(f"{i}. {c}" for i, c in enumerate(candidates))
        answer = self._ask(
            "pick",
            "A model wrote a belief about a founder's business. Below it are numbered beliefs a "
            "reference set holds. Which ONE of them is the same belief, if any?\n"
            "Reply with the number alone, or NONE if the model's belief is not among them.\n\n"
            f"The model's belief: {produced_statement}\n\nThe reference beliefs:\n{listed}\n",
            context=produced_statement[:80])
        if answer is None:
            return None
        for token in answer.replace(".", " ").split():
            if token.isdigit() and int(token) < len(candidates):
                return int(token)
        return None

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
                                  timeout=self.timeout_s)
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
    """A judge that is never available — for unit tests, and for `--no-judge`.

    With it, Choice matching falls back to the structural rule alone, which is what every number
    before MARKS_VERSION 2 was measured under.
    """

    def available(self) -> bool:
        return False
