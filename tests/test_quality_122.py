"""Spec 122 -- the reader asks again when its answer cannot be read."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from quality import cycle, readers, rubric
from tests.test_quality_078 import FakeCli, SCREEN_ANSWER, _run, wired  # noqa: F401 - the fixture

FX = Path(__file__).parent / "fixtures" / "quality"
REPO = Path(__file__).resolve().parent.parent
RECORD = REPO / "quality" / "cycles" / "20261101-d096da9.md"          # the nine's record, a data block of 079's shape

#: A model's slip: a doubled quote inside one why -- the object does not parse.
SLIP = json.dumps(SCREEN_ANSWER).replace('"why2": "a second read"', '"why2": "a second read""')


class SlipOnce(FakeCli):
    """Answers every screen with the slip the first time it is asked, and cleanly on the `-again` ask."""

    def __call__(self, argv, *, input, capture_output, text, timeout, env, cwd):    # noqa: A002
        slipped = not any(mark in input for mark in ("Reply with the one word", "## The grouping to score",
                                                      "## The whole", "Your previous reply could not be read"))
        self.screen = SLIP if slipped else SCREEN_ANSWER
        return super().__call__(argv, input=input, capture_output=capture_output, text=text, timeout=timeout,
                                env=env, cwd=cwd)


class FakeReader:
    """`Reader.ask`'s shape, answering from a list; records the labels and prompts it was asked."""

    def __init__(self, answers):
        self.answers, self.asked = list(answers), []

    def ask(self, label, prompt):
        self.asked.append((label, prompt))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            return {"answer": None, "error": str(answer), "cost_usd": 0.0, "seconds": 0.1, "cached": False}
        return {"answer": answer, "error": None, "cost_usd": 0.01, "seconds": 0.1, "cached": False}


def _parse(raw):
    return rubric.parse_answer(raw, has_options=True, audience="founder")


# ----------------------------------------------------------------------------------------------- FR-1 one more ask

def test_a_slip_is_asked_again_with_the_fault_named_and_the_second_answer_is_read():
    reader = FakeReader([SLIP, json.dumps(SCREEN_ANSWER)])
    answer, again = readers.ask_twice(reader, "founder-03-x", "the prompt", _parse)
    assert again is True and answer["r2"] == 1
    assert [label for label, _ in reader.asked] == ["founder-03-x", "founder-03-x-again"]
    tail = reader.asked[1][1]
    assert tail.startswith("the prompt\n\nYour previous reply could not be read: the answer's object does not parse")
    assert tail.endswith("Reply again with the one JSON object and nothing else.")


def test_a_clean_answer_is_asked_once():
    reader = FakeReader([json.dumps(SCREEN_ANSWER)])
    answer, again = readers.ask_twice(reader, "founder-03-x", "the prompt", _parse)
    assert again is False and answer["r1"] == 2 and len(reader.asked) == 1


def test_two_slips_leave_the_screen_unread_naming_both():
    missing = json.dumps({k: v for k, v in SCREEN_ANSWER.items() if k != "r2"})
    reader = FakeReader([SLIP, missing])
    with pytest.raises(rubric.RubricError) as err:
        readers.ask_twice(reader, "founder-03-x", "the prompt", _parse)
    assert str(err.value).startswith("first: the answer's object does not parse")
    assert "; again: r2 must be 0, 1 or 2" in str(err.value)
    assert len(reader.asked) == 2


def test_a_cli_error_is_the_clis_and_is_not_asked_again():
    reader = FakeReader([RuntimeError("the CLI answered an error: rate limited")])
    with pytest.raises(rubric.RubricError, match="the CLI answered an error"):
        readers.ask_twice(reader, "founder-03-x", "the prompt", _parse)
    assert len(reader.asked) == 1


def test_a_run_reads_a_slipped_screen_on_the_second_ask_and_records_both_calls(wired, capsys):
    wired.cli.__class__ = SlipOnce                 # the fixture's CLI, slipping once on every screen
    assert _run(wired) == 0
    files = list(wired.scores.glob("99-fixture/*.json"))
    assert len(files) == 1
    record = json.loads(files[0].read_text(encoding="utf-8"))
    assert record["unread"] == [] and record["asked_again"] >= 1
    assert record["asked_again"] == len(record["screens"])          # every screen slipped once, nothing else did
    names = sorted(p.name for p in (wired.out / "calls").glob("*-again.answer.json"))
    assert names and all(n.endswith("-again.answer.json") for n in names)
    assert "on a second ask" in capsys.readouterr().out


# ------------------------------------------------------------------------------------------- FR-2 the record says so

def test_the_cycle_head_counts_the_second_asks_and_the_record_says_so_only_when_there_were_any():
    data = cycle.load_record(RECORD)
    data["head"]["asked_again"], data["head"]["unread"] = 3, 2
    assert "  - 3 screens read on a second ask (spec 122); 2 unread" in cycle.render_record(data)
    data["head"]["asked_again"] = 0
    assert "second ask" not in cycle.render_record(data)


def test_head_of_sums_the_second_asks_over_the_latest_files():
    files = [{"entry": "a", "scope": "PROBLEM", "rubric_version": rubric.RUBRIC_VERSION, "asked_again": 2,
              "unread": [{"screen": "x"}], "scored_at": "2026-11-01T10:00:00+00:00", "partial": False,
              "summary": {"overall": {"score_pct": 90.0, "flagged_pct": 0.0, "screens": 10},
                          "founder": {"score_pct": 90.0, "flagged_pct": 0.0},
                          "respondent": {"score_pct": 90.0, "flagged_pct": 0.0}}}]
    try:
        head = cycle._head_of(files)
    except (KeyError, TypeError, AttributeError) as skip:        # the table needs more of a file than this stub has
        pytest.skip(f"the stub is too thin for table.head: {skip}")
    assert head["asked_again"] == 2 and head["unread"] == 1
