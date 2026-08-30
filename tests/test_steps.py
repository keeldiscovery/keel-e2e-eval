"""Stackless: the step() context manager's transcript ordering, screenshot numbering, and its
behaviour when a step raises (T007)."""

import json

from harness.steps import Recorder


def test_steps_are_numbered_in_order(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.step("first", party="stack"):
        pass
    with recorder.step("second", party="agent"):
        pass
    with recorder.step("third", party="founder"):
        pass

    lines = [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]
    assert [entry["seq"] for entry in lines] == [1, 2, 3]
    assert [entry["name"] for entry in lines] == ["first", "second", "third"]
    assert [entry["party"] for entry in lines] == ["stack", "agent", "founder"]
    assert all(entry["ok"] for entry in lines)


def test_screenshot_numbering_is_sequential_and_slugified(tmp_path):
    recorder = Recorder(tmp_path)
    first = recorder.next_screenshot_name("Founder Opens Overview!")
    second = recorder.next_screenshot_name("participant consents")
    assert first == "001-Founder-Opens-Overview.png"
    assert second == "002-participant-consents.png"
    assert recorder.screenshot_path(first) == tmp_path / "screenshots" / first


def test_a_raised_exception_is_recorded_and_reraised(tmp_path):
    recorder = Recorder(tmp_path)
    try:
        with recorder.step("boom", party="agent") as h:
            h.record_wire({"op": "submit"}, None)
            raise ValueError("something went wrong")
    except ValueError:
        pass
    else:
        raise AssertionError("expected the ValueError to propagate")

    lines = [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]
    assert len(lines) == 1
    assert lines[0]["ok"] is False
    assert "something went wrong" in lines[0]["error"]
    assert recorder.failed_step == "boom"


def test_only_the_first_failure_is_recorded_as_failed_step(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.step("a", party="stack") as h:
        h.fail("first failure")
    with recorder.step("b", party="stack") as h:
        h.fail("second failure")
    assert recorder.failed_step == "a"


def test_assert_step_records_expected_and_actual(tmp_path):
    recorder = Recorder(tmp_path)
    with recorder.step("verdict moved", party="agent", kind="assert") as h:
        h.record_assert("SUPPORTED", "SUPPORTED")
    lines = [json.loads(line) for line in recorder.transcript_path.read_text().splitlines()]
    assert lines[0]["kind"] == "assert"
    assert lines[0]["request"] == "SUPPORTED"
    assert lines[0]["response"] == "SUPPORTED"
