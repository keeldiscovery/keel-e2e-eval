"""Spec 152 FR-5: the copilot prototype, offline -- the server's routes against `FakeClients`, no key, no call.

A founder turn maps and advances; a respondent turn files; a founder verdict echoed on the respondent's line still
files; an empty transcript is heard as nothing; every key does what FR-1 says and `Z` undoes; a slow turn still lands
and holds nothing up; a WAV made the way the page makes it decodes; the run folder's files and shapes; the refusal
without both keys; `frames.json` keyed by the fixture's ids; and the page references only what the server serves. The
page's JavaScript is read, not run: no browser, no new dependency.
"""

from __future__ import annotations

import json
import re
import struct
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

from evals.copilot import questionnaire as qmod
from evals.copilot.fakes import FakeClients
from evals.copilot.prototype import server as srv
from evals.copilot.stacks import base, turn_by_turn
from stack.config import REPO_ROOT

PROTO = REPO_ROOT / "evals" / "copilot" / "prototype"


@pytest.fixture(scope="module")
def q() -> dict:
    return qmod.load()


def page_wav(samples: list[float], rate: int = 24000) -> bytes:
    """A WAV byte for byte as `copilot.js` `encodeWav` writes it: RIFF, PCM 1, mono, 16-bit little-endian."""
    data = b"".join(struct.pack("<h", max(-32768, min(32767, round(s * (0x8000 if s < 0 else 0x7FFF)))))
                    for s in samples)
    header = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 36 + len(data), b"WAVE", b"fmt ", 16, 1, 1, rate, rate * 2,
                         2, 16, b"data", len(data))
    return header + data


WAV = page_wav([0.0, 0.25, -0.25, 0.5] * 2400)


def fake(turns: list[tuple]) -> FakeClients:
    """`turns`: (who, heard, reply or None); a None reply is a turn the classifier is not called on."""
    script = {"turns": [{"who": w, "text": h, "truth": {}} for w, h, _ in turns]}
    return FakeClients(script, events=[r for _, h, r in turns if r is not None], heard=[h for _, h, _ in turns])


def session(q, tmp_path, turns, **kw) -> srv.Session:
    return srv.Session(q, fake(turns), tmp_path / "run", **kw)


def post(s: srv.Session, who: str, seq: int, **kw) -> dict:
    return s.turn(who=who, seq=seq, wav=WAV, started_at=1000.0 + seq, ended_at=1001.0 + seq, mode="rehearsal", **kw)


ASK_Q2 = ("founder", "And what would it be worth to you a month, per site?",
          {"q": "q2", "verdict": "same_meaning", "option": None, "tier": None, "state": "listening"})
ANSWER_Q2 = ("them", "Somewhere between five and eight hundred, if it saved an hour a day.",
             {"q": "q2", "verdict": None, "option": {"picks": [2]}, "tier": "likely", "state": "answered"})


# ------------------------------------------------------------------------------------------------ turns

def test_a_founder_turn_maps_and_advances_through_stack_1_as_the_bench_ran_it(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2])
    out = post(s, "founder", 1)
    assert (out["q"], out["verdict"], out["tier"], out["option"]) == ("q2", "same_meaning", None, None)
    assert out["card"]["current"] == "q2" and out["card"]["n"] == 2 and out["card"]["N"] == 6
    assert out["heard"] == ASK_Q2[1] and out["seq"] == 1 and out["who"] == "founder"
    assert set(out["parts"]) >= {"transcribe", "classify"} and out["reply"]["q"] == "q2"
    tr, msg = s.clients.requests
    assert tr["keywords"] == base.keywords(q, None) and tr["prompt"] == turn_by_turn.TRANSCRIBE_PROMPT
    assert msg == base.haiku_body(base.instruction("copilot-match.md"),
                                  turn_by_turn.match_prompt(q, None, "listening", "founder", ASK_Q2[1]))


def test_a_respondent_turn_files_against_the_question_the_founder_moved_to(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ANSWER_Q2])
    post(s, "founder", 1)
    out = post(s, "them", 2)
    assert "Current question: q2" in s.clients.requests[-1]["messages"][0]["content"]
    assert s.clients.requests[-2]["keywords"] == base.keywords(q, "q2")
    assert out["option"] == {"picks": [2]} and out["tier"] == "likely"
    row = out["filed_row"]
    assert row["kind"] == "likely" and row["q"] == "q2" and row["filing"]["label"] == "$500 to under $800"
    assert row["filing"]["by"] == "box" and row["filing"]["frame"] == ["a month", "per site"]
    assert out["card"]["counts"]["filed_by_box"] == 1


def test_a_founder_verdict_echoed_on_the_respondents_line_still_files(q, tmp_path):
    echoed = ("them", "Under five hundred, honestly.",
              {"q": "q2", "verdict": "same_meaning", "option": {"picks": [1]}, "tier": "sure", "state": "answered"})
    s = session(q, tmp_path, [ASK_Q2, echoed])
    post(s, "founder", 1)
    out = post(s, "them", 2)
    assert out["verdict"] is None and out["option"] == {"picks": [1]}
    assert out["filed_row"]["kind"] == "sure" and s.filings["q2"]["label"] == "Under $500"


def test_an_empty_transcript_is_heard_as_nothing_and_not_classified(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ("them", "", None)])
    post(s, "founder", 1)
    out = post(s, "them", 2)
    assert out["heard"] == "" and out["parts"]["classify"] == 0
    assert out["filed_row"]["kind"] == "heard_nothing" and out["filed_row"]["q"] == "q2"
    assert out["card"]["heard_row"] == {"who": "them", "heard": "", "seq": 2}
    assert sum(1 for r in s.clients.requests if "messages" in r) == 1 and "q2" not in s.filings


def test_unsure_and_unclear_are_handed_over_not_filed(q, tmp_path):
    unsure = ("them", "Mostly me, unless it's a new vendor.",
              {"q": "q2", "verdict": None, "option": {"unclear": True}, "tier": "sure", "state": "answered"})
    s = session(q, tmp_path, [ASK_Q2, unsure])
    post(s, "founder", 1)
    out = post(s, "them", 2)
    assert out["tier"] == "unsure" and out["filed_row"]["kind"] == "unsure" and "q2" not in s.filings


def test_a_changed_meaning_flags_the_pills_not_heard_and_the_filing_repeats_its_frame(q, tmp_path):
    ask = ("founder", "So on the log, about how many hours does your crew spend on it?",
           {"q": "q1", "verdict": "meaning_changed", "option": None, "tier": None, "state": "listening"})
    answer = ("them", "Call it forty hours.",
              {"q": "q1", "verdict": None, "option": {"value": 40}, "tier": "likely", "state": "answered"})
    s = session(q, tmp_path, [ask, answer])
    out = post(s, "founder", 1)
    assert out["frame_missing"] == ["last month", "per site"]
    assert out["card"]["flags"] == {"q1": ["last month", "per site"]}
    filed = post(s, "them", 2)["filed_row"]["filing"]
    assert filed["label"] == "40 hours" and filed["frame"] == ["last month", "per site", "hours"]
    assert filed["frame_missing"] == ["last month", "per site"]


def test_an_off_script_founder_question_is_a_note_under_the_current_question(q, tmp_path):
    own = ("founder", "Before I forget, how many crews do you run at once?",
           {"q": "q2", "verdict": "follow_up", "option": None, "tier": None, "state": "follow_up"})
    s = session(q, tmp_path, [ASK_Q2, own])
    post(s, "founder", 1)
    out = post(s, "founder", 2)
    assert out["filed_row"] == {"kind": "own_question", "who": "founder", "seq": 2, "q": "q2"}
    assert s.notes == [{"kind": "own_question", "under": "q2", "seq": 2, "heard": own[1]}]
    assert out["card"]["current"] == "q2" and out["card"]["counts"]["own_notes"] == 1


# ------------------------------------------------------------------------------------------------ keys

def test_number_keys_file_an_option_for_the_filed_rows_question_and_refuse_what_does_not_exist(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ANSWER_Q2])
    post(s, "founder", 1)
    post(s, "them", 2)
    out = s.key(key="3", seq_of_turn=2, at=2000.0)
    assert out["applied"] is True and s.filings["q2"]["by"] == "key"
    assert s.filings["q2"]["option"] == {"picks": [3]} and s.filings["q2"]["label"] == "$800 to under $2,500"
    assert out["card"]["filed_row"]["kind"] == "keyed"
    assert s.key(key="6", seq_of_turn=2)["applied"] is True          # q2 has six options
    assert s.key(key="0", seq_of_turn=2)["card"]["filings"]["q2"]["option"] == {"escape": True}


def test_number_keys_refuse_on_a_number_item_and_beyond_the_options(q, tmp_path):
    s = session(q, tmp_path, [])
    s.key(key="ArrowRight")                                           # q1, a number item
    out = s.key(key="2")
    assert out["applied"] is False and "X keeps" in out["message"]
    for _ in range(5):
        s.key(key="ArrowRight")
    assert s.current == "q6"
    assert s.key(key="5")["applied"] is False                         # q6 has four options
    assert s.key(key="0")["message"] == "q6 has no escape"


def test_x_keeps_the_reply_as_a_note_and_z_undoes_back_to_the_box(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ANSWER_Q2])
    post(s, "founder", 1)
    post(s, "them", 2)
    s.key(key="x", seq_of_turn=2)
    assert s.filings["q2"]["by"] == "note" and s.filings["q2"]["option"] is None
    assert s.filings["q2"]["verdict"] == "nothing" and s.filings["q2"]["heard"] == ANSWER_Q2[1]
    out = s.key(key="z")
    assert out["applied"] and s.filings["q2"]["by"] == "box" and s.filings["q2"]["option"] == {"picks": [2]}
    assert out["card"]["filed_row"]["kind"] == "undone"
    s.key(key="Z")                                                    # the box's own filing, undone too
    assert "q2" not in s.filings
    assert s.key(key="Z")["message"] == "nothing to undo"


def test_x_on_a_flagged_question_keeps_its_next_reply_as_a_note_and_f_clears_the_flag(q, tmp_path):
    ask = ("founder", "How many hours does your crew spend on it?",
           {"q": "q1", "verdict": "meaning_changed", "option": None, "tier": None, "state": "listening"})
    answer = ("them", "Forty.", {"q": "q1", "verdict": None, "option": {"value": 40}, "tier": "sure",
                                 "state": "answered"})
    s = session(q, tmp_path, [ask, answer])
    post(s, "founder", 1)
    assert s.key(key="X")["card"]["note_next"] == ["q1"]
    out = post(s, "them", 2)
    assert out["filed_row"]["kind"] == "kept_note" and s.filings["q1"]["by"] == "note"
    assert s.key(key="F")["card"]["flags"] == {}
    assert s.key(key="F")["applied"] is False


def test_arrows_move_the_now_card_and_p_toggles_listening(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ANSWER_Q2])
    post(s, "founder", 1)
    post(s, "them", 2)                                                # q2 filed
    assert s.key(key="ArrowRight")["card"]["current"] == "q3"
    assert s.key(key="ArrowLeft")["card"]["current"] == "q2"
    assert s.key(key="ArrowLeft")["card"]["current"] == "q1"
    assert s.key(key="ArrowLeft")["applied"] is False
    assert s.key(key=" ")["card"]["current"] == "q3"                  # Space skips the filed q2
    assert s.key(key="P")["card"]["listening"] is False
    assert s.key(key="p")["card"]["listening"] is True
    for k in ("R", "T", "Escape"):
        assert s.key(key=k)["applied"] == "page"
    assert s.key(key="Q")["applied"] is False


def test_done_after_every_item_is_filed(q, tmp_path):
    ids = [it["id"] for it in q["items"]]
    s = session(q, tmp_path, [("them", "Hmm.", {"q": qid, "verdict": None, "option": {"unclear": True},
                                                "tier": "unsure", "state": "listening"}) for qid in ids])
    for seq, (qid, k) in enumerate(zip(ids, ("0", "1", "2", "3", "4", "1"), strict=True), 1):
        assert s.key(key="ArrowRight")["card"]["current"] == qid
        assert post(s, "them", seq)["filed_row"] == {"kind": "unsure", "who": "them", "seq": seq, "q": qid}
        assert s.key(key=k, seq_of_turn=seq)["applied"] is True
        assert s.card()["done"] is (qid == ids[-1])
    assert s.counts()["filed_by_key"] == 6 and s.key(key="ArrowRight")["message"] == "every question is filed"


# ------------------------------------------------------------------------------------------------ order and stuck turns

class SlowClients(FakeClients):
    """`FakeClients` whose classify call sleeps `delays[i]` seconds on the i-th call."""

    def __init__(self, *a, delays=(), **kw):
        super().__init__(*a, **kw)
        self.delays, self.calls = list(delays), 0

    def messages(self, body):
        d = self.delays[self.calls] if self.calls < len(self.delays) else 0
        self.calls += 1
        out = super().messages(body)                                  # the reply is this call's, whenever it lands
        time.sleep(d)
        return out


def slow_session(q, tmp_path, turns, delays, give_up_s):
    script = {"turns": [{"who": w, "text": h, "truth": {}} for w, h, _ in turns]}
    c = SlowClients(script, events=[r for _, _, r in turns], heard=[h for _, h, _ in turns], delays=delays)
    return srv.Session(q, c, tmp_path / "run", give_up_s=give_up_s)


def test_a_respondent_turn_waits_for_the_founders_question_to_be_read_first(q, tmp_path):
    s = slow_session(q, tmp_path, [ASK_Q2, ANSWER_Q2], delays=[0.3], give_up_s=5)
    results = {}
    t1 = threading.Thread(target=lambda: results.update(f=post(s, "founder", 1)))
    t1.start()
    time.sleep(0.05)
    results["t"] = post(s, "them", 2)
    t1.join()
    assert "Current question: q2" in s.clients.requests[-1]["messages"][0]["content"]
    assert results["t"]["filed_row"]["q"] == "q2" and results["t"]["parts"]["queue"] > 0.1


def test_a_slow_turn_still_lands_never_blocks_the_next_and_a_key_filed_meanwhile_stands(q, tmp_path):
    stuck = ("them", "Probably, after a free look at it first.",
             {"q": "q6", "verdict": None, "option": {"picks": [2]}, "tier": "sure", "state": "answered"})
    nxt = ("founder", "Thanks, that's everything.",
           {"q": None, "verdict": "own_note", "option": None, "tier": None, "state": "done"})
    s = slow_session(q, tmp_path, [stuck, nxt], delays=[1.2, 0], give_up_s=0.3)
    s.key(key="ArrowRight")
    for _ in range(5):
        s.key(key="ArrowRight")
    assert s.current == "q6"
    results = {}
    t1 = threading.Thread(target=lambda: results.update(stuck=post(s, "them", 7)))
    t1.start()
    time.sleep(0.05)
    began = time.monotonic()
    results["next"] = post(s, "founder", 8)
    assert time.monotonic() - began < 1.0                             # held 0.3 s at most, not the 1.2 s call
    assert s.key(key="1", seq_of_turn=7)["card"]["filings"]["q6"]["option"] == {"picks": [1]}
    t1.join()
    late = results["stuck"]
    assert late["late"] is True and late["superseded"] is True and late["option"] == {"picks": [2]}
    assert s.filings["q6"]["by"] == "key" and s.filings["q6"]["option"] == {"picks": [1]}
    assert [e["seq"] for e in s.events] == [8, 7]
    logged = [json.loads(line) for line in (tmp_path / "run" / "events.jsonl").read_text().splitlines()]
    assert [e["seq"] for e in logged] == [8, 7] and logged[1]["late"] is True


# ------------------------------------------------------------------------------------------------ the WAV

def test_a_wav_made_as_the_page_makes_it_decodes_and_other_shapes_are_refused():
    info = srv.wav_info(WAV)
    assert info == {"rate": 24000, "frames": 9600, "seconds": 0.4}
    assert srv.wav_info(page_wav([0.1] * 4410, rate=44100))["rate"] == 44100
    stereo = struct.pack("<4sI4s4sIHHIIHH4sI", b"RIFF", 40, b"WAVE", b"fmt ", 16, 1, 2, 24000, 96000, 4, 16, b"data",
                         4) + b"\0\0\0\0"
    with pytest.raises(srv.BadTurn, match="16-bit mono"):
        srv.wav_info(stereo)
    with pytest.raises(srv.BadTurn, match="not a WAV"):
        srv.wav_info(b"not audio")


def test_the_pages_encoder_writes_the_header_the_test_builds():
    js = (PROTO / "copilot.js").read_text(encoding="utf-8")
    enc = js[js.index("function encodeWav"):]
    enc = enc[:enc.index("return new Blob")]
    for needle in ("'RIFF'", "'WAVE'", "'fmt '", "'data'", "setUint16(20, 1, true)", "setUint16(22, 1, true)",
                   "setUint32(24, rate, true)", "setUint32(28, rate * 2, true)", "setUint16(32, 2, true)",
                   "setUint16(34, 16, true)", "setInt16("):
        assert needle in enc, needle


# ------------------------------------------------------------------------------------------------ over HTTP + the log

@pytest.fixture()
def live(q, tmp_path):
    s = session(q, tmp_path, [ASK_Q2, ANSWER_Q2])
    httpd = srv.make_server(s, 0)
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    yield s, f"http://127.0.0.1:{httpd.server_address[1]}"
    httpd.shutdown()
    httpd.server_close()


def http(url, data=None, ctype=None, headers=None):
    req = urllib.request.Request(url, data=data, method="POST" if data is not None else "GET",
                                 headers={**({"Content-Type": ctype} if ctype else {}), **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers.get("Content-Type"), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type"), e.read()


def test_the_routes_over_http_and_the_run_folder_in_the_bench_shape(live, tmp_path):
    s, base_url = live
    st, _, body = http(base_url + "/turn?who=founder&seq=1&started_at=100.5&ended_at=102.25&mode=share", WAV,
                       "audio/wav")
    assert st == 200 and json.loads(body)["q"] == "q2"
    st, _, body = http(base_url + "/turn?who=them&seq=2&started_at=103&ended_at=106&mode=share&shown=1:102.9", WAV,
                       "audio/wav")
    assert st == 200 and json.loads(body)["filed_row"]["kind"] == "likely"
    st, _, body = http(base_url + "/key", json.dumps({"key": "3", "seq_of_turn": 2, "at": 107.0,
                                                      "shown": {"2": 106.8}}).encode(), "application/json")
    assert st == 200 and json.loads(body)["card"]["filings"]["q2"]["by"] == "key"
    s.close()
    run = tmp_path / "run"
    assert sorted(p.name for p in (run / "turns").iterdir()) == ["1-founder.wav", "2-them.wav"]
    assert (run / "turns" / "1-founder.wav").read_bytes() == WAV
    events = [json.loads(line) for line in (run / "events.jsonl").read_text().splitlines()]
    bench_shape = {"turn", "q", "verdict", "option", "tier", "state", "parsed", "t_emitted", "parts", "usage"}
    for ev in events:
        assert bench_shape | {"heard", "reply", "seq", "who", "wall"} <= set(ev)
        assert {"ended_at", "shown_at"} <= set(ev["wall"]) and {"transcribe", "classify"} <= set(ev["parts"])
    assert events[0]["wall"] == {"started_at": 100.5, "ended_at": 102.25, "shown_at": 102.9}
    assert events[1]["wall"]["shown_at"] == 106.8 and events[1]["who"] == "them"
    keys = [json.loads(line) for line in (run / "keys.jsonl").read_text().splitlines()]
    assert keys == [dict(keys[0], key="3", seq_of_turn=2, at=107.0, applied=True)]
    sess = json.loads((run / "session.json").read_text())
    assert {"questionnaire", "mode", "started", "ended", "filed_by_box", "filed_by_key", "filed_as_notes"} <= set(sess)
    assert sess["mode"] == "share" and sess["filed_by_key"] == 1 and sess["filed_by_box"] == 0
    assert sess["questionnaire"].endswith("questionnaire-08-fresco.json")
    assert not (run / "register-row.md").exists()


def test_bad_posts_are_refused_and_another_sites_page_may_not_post(live):
    _, base_url = live
    assert http(base_url + "/turn?who=founder&seq=1", b"junk", "audio/wav")[0] == 400
    assert http(base_url + "/turn?who=nobody&seq=1", WAV, "audio/wav")[0] == 400
    assert http(base_url + "/turn?who=founder", WAV, "audio/wav")[0] == 400
    assert http(base_url + "/key", b"{}", "application/json",
                headers={"Origin": "https://example.org"})[0] == 403
    assert http(base_url + "/nowhere")[0] == 404
    assert http(base_url + "/frames.json")[0] == 404                  # served inside /copilot.json, not as a file
    assert http(base_url + "/../server.py")[0] == 404


def test_the_page_references_only_files_the_server_serves(live):
    _, base_url = live
    html = (PROTO / "copilot.html").read_text(encoding="utf-8")
    js = (PROTO / "copilot.js").read_text(encoding="utf-8")
    refs = re.findall(r'(?:src|href)="([^"#]+)"', html)
    assert refs and all(not r.startswith(("http:", "https:", "//")) for r in refs), refs
    urls = set(re.findall(r"fetch\('(/[a-z.]*)", js))
    assert urls == {"/copilot.json", "/turn", "/key"}, urls
    for ref in refs + ["/", "/copilot.json"]:
        st, ctype, _ = http(base_url + "/" + ref.lstrip("/"))
        assert st == 200, ref
    assert http(base_url + "/")[1].startswith("text/html")
    assert http(base_url + "/copilot.js")[1].startswith("text/javascript")
    assert http(base_url + "/copilot.css")[1].startswith("text/css")
    data = json.loads(http(base_url + "/copilot.json")[2])
    assert [i["id"] for i in data["items"]] == [f"q{n}" for n in range(1, 7)]
    assert data["constants"]["turn_end_hold_s"] == base.TURN_END_HOLD and data["constants"]["give_up_s"] == 20
    assert "<script" not in html.split("copilot.js")[0].split("<body")[-1] or "src=\"copilot.js\"" in html


def test_the_page_carries_the_ux_pages_states_and_keys():
    js = (PROTO / "copilot.js").read_text(encoding="utf-8")
    css = (PROTO / "copilot.css").read_text(encoding="utf-8")
    for words in ("I did not catch that", "heard nothing", "still working, carry on", "Your own question",
                  "Paused · five minutes of silence", "Done", "asked differently?", "documentPictureInPicture",
                  "requestWindow({width: 380, height: 560})", "pagehide", "getUserMedia", "getDisplayMedia",
                  "createAnalyser", "audio: true, video: true"):
        assert words in js, words
    for k in ("'ArrowRight'", "'ArrowLeft'", "' '", "'Escape'", "'r'", "'t'", "'p'", "'x'", "'f'", "'z'"):
        assert k in js, k
    for cls in (".cp .q", ".frame span.miss", ".cp .filed.sure", ".cp .filed.likely", ".cp .filed.hand",
                ".dot.listening", ".dot.working", ".dot.hand", ".dot.done", ".opt .key", ".cp .foot"):
        assert cls in css, cls
    assert "http" not in css.replace("http-equiv", "") and "@import" not in css


def test_no_trade_or_company_word_in_the_prototypes_code(q):
    words = {"Fresco", "Procore", "superintendent", "CFO", "daily log", "per site"}
    for name in ("server.py", "copilot.js", "copilot.html", "copilot.css"):
        text = (PROTO / name).read_text(encoding="utf-8")
        assert not [w for w in words if w.lower() in text.lower()], name


# ------------------------------------------------------------------------------------------------ frames + refusal

def test_frames_json_is_keyed_by_the_fixtures_ids(q):
    raw = json.loads((PROTO / "frames.json").read_text(encoding="utf-8"))
    ids = [it["id"] for it in q["items"]]
    assert sorted(raw["items"]) == sorted(ids)
    for f in raw["items"].values():
        assert set(f) <= {"window", "unit", "anchor"} and all(isinstance(p, str) for v in f.values() for p in v)
    assert srv.frame_of(raw["items"], "q1") == ["last month", "per site", "hours"]
    assert srv.frame_of(raw["items"], "q99") == [] and srv.frame_of(raw["items"], None) == []


def test_missing_pills_ignore_case_punctuation_and_soft_words():
    pills = ["last month", "per site", "$800", "a check it works"]
    heard = "Could you sign off on 800, per site, LAST MONTH? And would a check work?"
    assert srv.missing_pills(pills, heard) == ["a check it works"]


def test_the_server_refuses_without_both_keys_naming_the_variables_never_a_value(capsys):
    assert srv.main(["--port", "0"], env={}) == 2
    err = capsys.readouterr().err.strip().splitlines()
    assert len(err) == 1 and "KEEL_OPENAI_API_KEY and KEEL_ANTHROPIC_API_KEY" in err[0]
    assert srv.main(["--port", "0"], env={"KEEL_OPENAI_API_KEY": "sk-not-a-real-value"}) == 2
    err = capsys.readouterr().err
    assert "KEEL_ANTHROPIC_API_KEY" in err and "KEEL_OPENAI_API_KEY" not in err and "sk-not" not in err


def test_make_copilot_prototype_refuses_in_one_line_with_exit_2():
    env = {"PATH": "/usr/bin:/bin", "HOME": str(Path.home())}
    r = subprocess.run(["make", "-s", "--no-print-directory", "copilot-prototype"], cwd=REPO_ROOT, env=env,
                       capture_output=True, text=True, timeout=30)
    assert r.returncode == 2
    lines = (r.stdout + r.stderr).strip().splitlines()
    assert lines[0].startswith("make copilot-prototype refuses:") and "KEEL_OPENAI_API_KEY" in lines[0]
    assert not [line for line in lines[1:] if "refuses" in line]
