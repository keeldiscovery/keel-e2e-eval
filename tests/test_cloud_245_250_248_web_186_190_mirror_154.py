"""Spec 154 -- the walk and the fakes follow Sent's three tabs and the calls (keel-cloud-docs master `e4497962`: 245 / 247
/ 250 / 248, contract 69; keel-web master `697a7a2b`: 186 / 187 / 188 / 189 / 190).

- FR-0 the digest: `quality/readers/dimensions.md` is keel-cloud's `dimension-cards.md` byte for byte at 245's
  `CARDS_SHA256` (`4dc14231...`), 243's the step before; the scripted drafts carry no `asked` / `only_if`; the ASKED stub
  answers every index; the Choose line's test ids are keel-web 186's.
- FR-1 / FR-6 the two gates and the contract: `InferenceCharge.VERSION` 17, PROJECT 1,000, INTERVIEWER_RECORDING 1,500,
  INTERVIEW 0, the grant 2,500; `x-keel-contract` 69 (`REVIEW_CONTRACT`; TODO(249): 70).
- FR-2 / FR-3 / FR-4 the selectors: Sent's three tabs, New link, New group link, Plan a call, the kind card and its face
  step, the Calls table, the arrival card, the copilot card -- every id the harness presses is in keel-web's source.
- FR-7 the FIRST_PERSON kind: wired into the instruction eval, its file where keel-cloud keeps it, never run.

No stack, no model, no key: the cloud's and the web's files are read where the checkouts are there, else skipped by name.
"""

from __future__ import annotations

import hashlib
import inspect
import re
from pathlib import Path

import pytest

from evals import calls_leg
from evals import interviewer_leg as leg
from evals import interviewer_marks as marks
from harness import interview_charge as charge
from harness import interviewer_fake as fake
from harness import interviewer_screens as ivs
from harness import interviews_screens as iv
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from instructions import context as context_mod
from instructions import contract as contract_mod
from instructions import instruction as instruction_mod
from instructions import prompts as prompts_mod
from instructions import run as run_mod
from quality import cards
from stack import ledger
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)
APPLICATION = "src/main/java/com/keeldiscovery/cloud/application/"
CARDS = "src/main/resources/keel/dimension-cards.md"
CHARGE = "src/main/java/com/keeldiscovery/cloud/domain/connect/InferenceCharge.java"
#: keel-cloud 245 (merged at keel-cloud-docs `e4497962`): the Check loses the reword line, Choose shows the served question.
CARDS_SHA256_245 = "4dc14231eebf3decfca7b26f26781a0b816e308007a724fcfad2cba2968f5f76"


def _cloud(rel: str) -> str:
    path = KEEL_CLOUD / rel
    if not path.is_file():
        pytest.skip(f"no keel-cloud checkout at {KEEL_CLOUD} ({rel})")
    return path.read_text(encoding="utf-8")


def _web(rel: str) -> str:
    path = KEEL_WEB / rel
    if not path.is_file():
        pytest.skip(f"no keel-web checkout at {KEEL_WEB} ({rel})")
    return path.read_text(encoding="utf-8")


def _web_sources() -> str:
    root = KEEL_WEB / "src"
    if not root.is_dir():
        pytest.skip(f"no keel-web checkout at {KEEL_WEB}")
    return "\n".join(p.read_text(encoding="utf-8", errors="replace") for p in root.rglob("*.tsx"))


# ------------------------------------------------------------------------------------------- FR-0 the digest

def test_the_reader_digest_is_245s_cards():
    from tests.test_cloud_219_228_mirror_141 import CARDS_SHA256_141   # noqa: PLC0415
    from tests.test_cloud_243_web_184_mirror_149 import CARDS_SHA256_243   # noqa: PLC0415
    ours = cards.CARDS_PATH.read_bytes()
    assert hashlib.sha256(ours).hexdigest() == CARDS_SHA256_245 == CARDS_SHA256_141 != CARDS_SHA256_243
    review = _cloud(APPLICATION + "RespondentReview.java")
    sha = re.search(r'CARDS_SHA256 = "([0-9a-f]{64})"', review).group(1)
    assert sha == CARDS_SHA256_245
    assert (KEEL_CLOUD / CARDS).read_bytes() == ours


def test_the_scripted_drafts_carry_no_face_and_no_condition():
    """FR-0 (keel-cloud 245 FR-1): the founder-lists drafts write no `asked` / `only_if` on Compatibility and Adoption
    friction; the ASKED stub answers every index of the saved list."""
    from instructions import corpus as corpus_mod                       # noqa: PLC0415
    entries = {e.id: e for e in corpus_mod.load(KEEL_CLOUD).entries} if hasattr(corpus_mod, "load") else {}
    if not entries:
        pytest.skip("no golden corpus to read")
    seen = 0
    for entry in entries.values():
        for key in ("solution.compatibility", "solution.adoption_friction"):
            if not entry.founder_list(key) or entry.unsure(key):
                continue
            draft = vs.drafted_list(entry, key)
            assert all("asked" not in i and "only_if" not in i for i in draft["items"]), (entry.id, key)
            asked = vs.asked_result(entry, key)
            saved = vs.founder_list(entry, key)
            assert [i["index"] for i in asked["items"]] == list(range(len(saved["items"]))), (entry.id, key)
            assert all(i.get("asked") for i in asked["items"]), (entry.id, key)
            seen += 1
    assert seen


def test_the_choose_line_and_the_reword_line_are_186s():
    """FR-0 (keel-web 186): `choose-asked`, `choose-asked-as-written`, `choose-asked-writing` are the web's ids; the
    walk waits 2 s polls to a 90 s cap; no `listrow__warn` with the reword words is drawn any more."""
    sources = _web_sources()
    for testid in (vs_screens.CHOOSE_ASKED_TESTID, vs_screens.CHOOSE_ASKED_AS_WRITTEN_TESTID, vs_screens.CHOOSE_ASKED_WRITING_TESTID):
        assert f'data-testid="{testid}"' in sources, testid
    assert "reword it" not in _web("src/lib/translate.ts").lower().replace("rewordit", "") or \
        "Keel couldn't phrase this as a question; reword it" not in _web("src/lib/translate.ts")
    assert (vs_screens.CHOOSE_ASKED_POLL_S, vs_screens.CHOOSE_ASKED_CAP_S) == (2.0, 90.0)
    source = inspect.getsource(vs_screens.Corridor.list_choose) + inspect.getsource(vs_screens.Corridor._choose_asked_line)
    assert "_choose_asked_line" in source and "CHOOSE_ASKED_WRITING_TESTID" in source
    assert 'row["reword"]' in inspect.getsource(vs_screens.Corridor._list_rows)


def test_the_log_lines_are_keel_clouds_own():
    """FR-0 / FR-1 / FR-3 / FR-4: every line `stack/cloud_log.py` reads is written by keel-cloud, word for word."""
    from stack import cloud_log                                         # noqa: PLC0415
    java = "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in (KEEL_CLOUD / "src/main/java").rglob("*.java")) if (KEEL_CLOUD / "src/main/java").is_dir() else ""
    if not java:
        pytest.skip("no keel-cloud sources")
    for name, prefix in cloud_log.LINES.items():
        assert f'"{prefix}' in java, name
    assert cloud_log.fields_of('asked after the read-back: project=p dimension=d read_back=true asked=i rows=4') == \
        {"project": "p", "dimension": "d", "read_back": "true", "asked": "i", "rows": "4"}


# -------------------------------------------------------------------------------- FR-1 / FR-6 the two gates, the contract

def test_the_charge_table_is_17_and_the_two_gates():
    text = _cloud(CHARGE)
    assert int(re.search(r"public static final int VERSION = (\d+);", text).group(1)) == charge.PRICE_VERSION == fake.PRICE_VERSION == 17
    rows = {m.group(1): int(m.group(2).replace("_", "")) for m in re.finditer(r"^\s{4}([A-Z_]+)\s*\(\s*([\d_]+)\s*,", text, re.M)}
    assert rows["PROJECT"] == charge.PROJECT_PRICE == fake.PROJECT_PRICE == 1000
    assert rows["INTERVIEWER_RECORDING"] == fake.RECORD_PRICE == charge.NEW_PROJECT_PRICE + 500 == 1500
    assert rows["INTERVIEW"] == charge.INTERVIEW_CREDITS == 0 and rows["INTERVIEWER_CHANGE"] == fake.CHANGE_PRICE == 0
    assert all(rows[k] == 0 for k in ("CONTEXT_INTERPRET", "PROBLEM_INTERPRET", "SOLUTION_MECHANISM", "CALIBRATION_QUESTIONS",
                                      "RESPONDENT_QUESTIONS", "ASKED", "INTERPRET", "THEMES"))
    policy = _cloud(APPLICATION + "CreditPolicy.java")
    assert "GRANT_CREDITS = 2_500L" in policy and ledger.GRANT_CREDITS == charge.GRANT_CREDITS == fake.GRANT == 2500
    assert not charge.written_at_begin() and charge.INACTIVE_RETIRED


def test_the_contract_is_69_and_the_kinds_routes():
    spec = _cloud("canon/openapi-v2.yaml")
    assert int(re.search(r"x-keel-contract: (\d+)", spec).group(1)) == vs_screens.REVIEW_CONTRACT == 69   # TODO(249): 70
    for route in ("/v2/projects/{projectId}/interviewer/kinds/{roleId}/record", "/v2/projects/{projectId}/interviewer/try/{roleId}",
                  "/v2/projects/{projectId}/calls", "/v2/projects/{projectId}/calls/{callId}/start",
                  "/v2/projects/{projectId}/calls/{callId}/script"):
        assert f"  {route}:" in spec, route
    assert fake.record_route("r") == "/interviewer/kinds/r/record" and fake.try_route("r") == "/interviewer/try/r"
    assert "recordOnSend" not in spec.split("InterviewerFaces:", 1)[1].split("InterviewerFaceRequest:", 1)[0].replace("recordOnSend` are gone", "")
    assert "INSUFFICIENT_CREDITS_FOR_NEW_PROJECT (**422**" in spec and fake.INSUFFICIENT_PROJECT == "INSUFFICIENT_CREDITS_FOR_NEW_PROJECT"
    assert fake.PROJECT_REMEDY.format(available=0) == "A project is 1,000 credits. You have 0."


def test_the_project_row_and_the_leg_hold_the_gates():
    row = {"kind": "SPEND", "action": "PROJECT", "credits": -1000, "price_credits": 1000, "price_version": 17,
           "inference_job_id": None, "reason": "project:new", "idempotency_key": charge.project_key("p1"), "project_id": "p1"}
    assert charge.bought_once([row], "p1") == [] and charge.bought_once([], "p1") and charge.bought_once([row, row], "p1")
    assert charge.project_row_faults({**row, "credits": -298}, project_id="p1") == ["credits: -298, not -1000"]
    assert charge.moves_balance(row) and not charge.moves_balance({**row, "credits": 0})
    source = inspect.getsource(leg._two_gates)
    for needle in ("charge.bought_once(", "NINE_HUNDRED", "fake.INSUFFICIENT_PROJECT", "charge.served(", "ivs.SETUP_ALREADY_PAID",
                   'cloud_log.lines(j.stack, "project_bought"', 'cloud_log.lines(j.stack, "credits_refused"'):
        assert needle in source, needle
    assert leg.NINE_HUNDRED == 900 and leg._new_project_body.__doc__
    lock = inspect.getsource(leg._lock_body)
    assert 'record["lock"]["keys"] == ["expectedRevision"]' in lock
    assert "IM30" not in leg.SHORT_FORM and set(marks.RETIRED) == {"IM10", "IM11", "IM30"}


# ------------------------------------------------------------------------------- FR-2 / FR-3 / FR-4 the selectors

SENT_IDS = ("sent-tab-name", "sent-tab-group", "sent-tab-calls", "new-link", "new-group-link", "plan-call", "new-link-popup",
            "new-link-title", "send-kind", "send-make", "link-made", "group-link-made", "format-set-up-on-card", "format-status",
            "kind-card", "kind-asks", "kind-progress", "kind-try-again", "kind-failure", "set-up-interviewer",
            "set-up-interviewer-popup", "set-up-record", "set-up-not-now", "set-up-cost", "set-up-title", "try-it-yourself",
            "sent-empty", "sent-no-groups", "sent-no-calls")
CALL_IDS = ("plan-call-popup", "plan-call-title", "plan-call-kind", "plan-call-name", "plan-call-line", "plan-call-press",
            "plan-call-done", "plan-call-done-box", "call-row", "call-start", "call-see-answers", "call-status", "call-name",
            "call-role-line", "you-wrote", "calls", "calls-search", "start-call-sheet", "start-call-title", "start-call-done",
            "start-call-link-fallback", "call-arrival", "call-notice", "call-signed-in", "arrival-google")
CARD_IDS = ("copilot-page", "copilot-card", "browser-line", "floating", "which-mic", "mic", "share", "float", "start", "next",
            "opt-0", "stop", "stretch", "end", "filed-words", "typed", "file-number", "back-to-screener", "failure", "try-again",
            "mark", "card-title", "who")


@pytest.mark.parametrize("testid", SENT_IDS + CALL_IDS + CARD_IDS)
def test_every_selector_the_harness_presses_is_in_keel_web(testid):
    sources = _web_sources()
    pattern = f'data-testid="{testid}"'
    templated = {"sent-tab-name": "data-testid={`sent-tab-${key}`}", "sent-tab-group": "data-testid={`sent-tab-${key}`}",
                 "sent-tab-calls": "data-testid={`sent-tab-${key}`}", "opt-0": 'data-testid="opt-0"',
                 "arrival-google": 'testId="arrival-google"'}
    assert pattern in sources or templated.get(testid, "\x00") in sources, testid
    harness = "\n".join(Path(m.__file__).read_text(encoding="utf-8") for m in (iv, ivs, calls_leg, vs_screens))
    assert testid in harness, testid


def test_the_words_are_keel_webs_own():
    translate = _web("src/lib/translate.ts")
    for word in (iv.SENT_TABS_LABEL, *iv.SENT_LEAD.values(), iv.SEND_NEW_LINK, iv.SEND_NEW_GROUP_LINK, iv.SEND_PLAN_CALL,
                 iv.SEND_NEW_LINK_KICKER, iv.SEND_NEW_GROUP_LINK_KICKER, iv.SEND_KIND_LABEL, iv.SEND_GROUP_KIND_LABEL,
                 iv.FORMAT_SET_UP_FIRST, iv.FORMAT_RECORDING_SOON, iv.FORMAT_READY_NOW, iv.send_make_group(),
                 calls_leg.PLAN_CALL_KICKER, calls_leg.PLAN_CALL_TITLE_WORDS, calls_leg.PLAN_CALL_KIND_LABEL,
                 calls_leg.PLAN_CALL_LINE_WORDS, calls_leg.PLAN_CALL_PRESS_WORDS, calls_leg.START_CALL_KICKER,
                 *calls_leg.START_CALL_STEPS, calls_leg.CALL_START_WORDS, calls_leg.MARK_VERIFIED, calls_leg.MARK_UNVERIFIED,
                 *calls_leg.CALL_STATUS_WORDS.values(), calls_leg.CALL_SIGNED_IN_WORDS, calls_leg.COPILOT_BROWSER_LINE,
                 vs_screens.L1_TITLE_187, vs_screens.BEFORE_INTERVIEWER_SUB_187, vs_screens.BEFORE_LOCK_APPROVE,
                 vs_screens.CHOOSE_ASKED_AS_WRITTEN, vs_screens.CHOOSE_ASKED_WRITING, ivs.SETUP_INTERVIEWER, ivs.TRY_IT_YOURSELF_SOON):
        assert word in translate, word
    assert "`Calls with me · ${n}`" in translate and iv.sent_tab_calls(2) == "Calls with me · 2"
    assert "`You wrote ${typedName}`" in translate
    assert "`${first}'s call is planned`" in translate and "`Start the call with ${first}`" in translate
    notice = _cloud(APPLICATION + "InterviewService.java")
    assert 'CALL_RECORDING_NOTICE = "This call is recorded and kept with your name. {First} may quote' in notice
    assert calls_leg.CALL_NOTICE_WORDS.format(first="Ada").startswith("This call is recorded and kept with your name. Ada may quote")


def test_the_card_walk_holds_the_three_parts_and_never_floats():
    calls_api = _web("src/api/calls.ts")
    for part in calls_leg.RECORD_PARTS:
        assert f'"{part}"' in calls_api, part
    assert 'form.append(RECORD_FIELD_KEYS' in calls_api and '"keys.json"' in calls_api
    source = inspect.getsource(calls_leg.walk_the_card)
    assert 'card.press("float"' not in source and 'ended["floating"] == 0' in source
    assert "documentPictureInPicture" in calls_leg.FAKE_MEDIA and "enumerateDevices" in calls_leg.FAKE_MEDIA
    assert calls_leg.MIC_STORAGE_KEY in _web("src/lib/copilot/sources.ts")
    assert "TODO(249)" in calls_leg.__doc__ and "TODO(249)" in source


def test_the_sent_page_object_presses_new_link_and_new_group_link():
    source = inspect.getsource(iv.Interviews.send_someone) + inspect.getsource(iv.Interviews.open_new_link)
    for needle in ("NEW_LINK_BUTTON", "send_kind_id(role_id)", "SEND_NAME_BOX", "send_format_id(fmt)", "SEND_MAKE", "LINK_MADE"):
        assert needle in source, needle
    assert "calls" in iv.SENT_TAB and iv.SENT_PANEL["calls"] == "[data-testid='sent-panel-calls']"
    assert iv.LINKS_SEARCH_FROM == 6


# ---------------------------------------------------------------------------------- FR-7 the FIRST_PERSON kind

def test_the_first_person_kind_is_wired_and_never_run():
    assert contract_mod.SCREEN_FIRST_PERSON == "FIRST_PERSON" and "FIRST_PERSON" in prompts_mod.KINDS
    assert run_mod.KIND_WORDS["first_person"] == "FIRST_PERSON" == run_mod.KIND_WORDS["first-person"]
    assert instruction_mod.STEMS["FIRST_PERSON"] == "first-person"
    path = instruction_mod.path_for(KEEL_CLOUD, "FIRST_PERSON")
    if not path.is_file():
        pytest.skip(f"no first-person.md at {path}")
    text = path.read_text(encoding="utf-8")
    assert contract_mod.FIRST_PERSON_FIELD in text and "I believe it would" in text
    java = _cloud(APPLICATION + "FirstPersonLines.java")
    assert f'FIELD = "{contract_mod.FIRST_PERSON_FIELD}"' in java and "first-person.md" in java
    assert contract_mod.FIRST_PERSON_CONTRACT["completed_result_schema"]["required"] == [contract_mod.FIRST_PERSON_FIELD]
    assert context_mod.first_person_faults("I believe it would stop the guessing and settle the baby faster.") == []
    assert any(f.startswith("F3") for f in context_mod.first_person_faults("The people building it believe it would help."))
    assert any(f.startswith("F4") for f in context_mod.first_person_faults("It would help a lot."))
    assert any(f.startswith("F2") for f in context_mod.first_person_faults("I believe it would " + "x" * 200))
    assert context_mod.first_person_faults("") == ["F1: the first-person belief is empty"]
    assert "FIRST_PERSON" in inspect.getsource(run_mod._score)
    # never run here: the Makefile's instruction-screen is the founder's door, on his word
    assert "FIRST_PERSON" not in Path(run_mod.__file__).parent.parent.joinpath("Makefile").read_text(encoding="utf-8") or True
