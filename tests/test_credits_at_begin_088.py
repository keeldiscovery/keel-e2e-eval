"""Spec 088 (keel-cloud 156, contract 45, `InferenceCharge.VERSION` 12): one charge per interview, at Begin.

FR-1, the prices: both fakes at price version 12, the harness's mirror (`harness/interview_charge.py`) held to keel-cloud's
own charge table (skipped by name on a keel-cloud before 156), and §6.3's five-participant figure re-summed wherever the
harness states it. FR-2, Begin on the wire: the scripted person's posts (Begin, then the response), the one row's shape,
the legs' sweeps letting a Begin's row through; the browser half behind the keel-web 131 marker. FR-3, the inactive
link: the body held to keel-cloud's controller (skipped by name before 156), what reads inactive and what reads served,
the full interviewer leg's order and its stand-ins; the page behind the keel-web 131 marker."""

from __future__ import annotations

import inspect
import re
from pathlib import Path

import pytest

from evals import contacts_leg, interviewer_leg
from harness import contacts_fake
from harness import interview_charge as charge
from harness import interviewer_fake
from harness import vectors_script as vs
from stack import ledger
from stack.config import load_config

CONFIG = load_config(validate=False)
REPO = Path(__file__).resolve().parent.parent
CHARGE_JAVA = "src/main/java/com/keeldiscovery/cloud/domain/connect/InferenceCharge.java"


def _cloud(rel: str) -> str:
    path = CONFIG.keel_cloud / rel
    if not path.is_file():
        pytest.skip(f"keel-cloud has no {rel}")
    return path.read_text(encoding="utf-8")


def _charge_table() -> tuple[int, dict[str, int]]:
    """keel-cloud's `InferenceCharge`: its VERSION and every row's `priceCredits` (the first argument)."""
    text = _cloud(CHARGE_JAVA)
    rows = {m.group(1): int(m.group(2).replace("_", ""))
            for m in re.finditer(r"^\s{4}([A-Z_]+)\s*\(\s*([\d_]+)\s*,", text, re.M)}
    if charge.INTERVIEW not in rows:
        pytest.skip("keel-cloud predates spec 156 (no INTERVIEW row in InferenceCharge)")
    version = re.search(r"public static final int VERSION = (\d+);", text)
    assert version, "InferenceCharge declares no VERSION"
    return int(version.group(1)), rows


# --------------------------------------------------------------------------------------------- FR-1: the prices

def test_both_fakes_carry_price_version_12():
    assert interviewer_fake.PRICE_VERSION == contacts_fake.PRICE_VERSION == charge.PRICE_VERSION == 12


def test_the_mirror_is_keel_clouds_charge_table():
    version, rows = _charge_table()
    assert version == charge.PRICE_VERSION
    assert rows[charge.INTERVIEW] == charge.INTERVIEW_CREDITS == 30
    assert {k: rows[k] for k in charge.READ_PRICES} == charge.READ_PRICES == {"INTERPRET": 0, "THEMES": 0}
    # the founder-side rows 156 left alone, as the two fakes state them
    assert rows["INTERVIEWER_RECORDING"] == rows["INTERVIEWER_CHANGE"] == interviewer_fake.CREDITS
    assert rows["CONTACT_PAGE"] == contacts_fake.PAGE_CREDITS and rows["CONTACT_EMAIL"] == contacts_fake.EMAIL_CREDITS


def test_section_6_3s_five_participants_re_summed():
    assert charge.project_credits(5, version=11) == 1_250             # §6.3's table as written
    assert charge.FIVE_PARTICIPANTS == charge.project_credits(5) == 540 + 105 + 560 + 5 * 30 == 1_355
    assert charge.project_credits(20) == 540 + 105 + 560 + 20 * 30


@pytest.mark.parametrize("rel", ["Makefile", "matrix/cells.toml", "tests/test_matrix_cells.py",
                                 "evals/test_s012_journey_through_a_host.py"])
def test_no_harness_line_states_the_old_five_participant_total(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert "1,250 credits a" not in text and "is 1,250 credits" not in text and "about 1,250" not in text, rel
    assert "$12.50" not in text, rel


@pytest.mark.parametrize("rel", ["Makefile", "matrix/cells.toml", "tests/test_matrix_cells.py"])
def test_the_new_total_is_stated(rel):
    text = (REPO / rel).read_text(encoding="utf-8")
    assert f"{charge.FIVE_PARTICIPANTS:,} credits" in text and "$13.55" in text, rel


# ------------------------------------------------------------------------------------------- FR-2: Begin on the wire

#: The browser half of FR-2 and FR-3 waits on keel-web 131 (Begin posted from the intro, the inactive page).
WEB_131 = pytest.mark.skipif(not charge.web_131_built(), reason=charge.WEB_131_PENDING)
INVITATION = "6f1c1a52-6a43-4f5e-9d39-0b7a2d6c1e11"
PROJECT = "0b8e5f8e-3a5c-4b7e-8f0e-6c2b1d9a7e22"


def _row(**over) -> dict:
    row = {"kind": "INTERVIEW", "action": "INTERVIEW", "credits": -30, "price_credits": 30, "price_version": 12,
           "inference_job_id": None, "actual_cost_micro_usd": None, "reason": f"invitation:{INVITATION}",
           "idempotency_key": f"interview:{INVITATION}", "project_id": PROJECT}
    return {**row, **over}


def test_the_key_is_cloud_s_interview_key():
    assert charge.key(INVITATION) == f"interview:{INVITATION}"
    assert vs.BEGIN_PATH == charge.BEGIN_PATH == "/interview/begin" and charge.BEGIN_STATUS == 204


def test_one_row_of_the_right_shape_is_charged_once():
    assert charge.charged_once([_row()], INVITATION, PROJECT) == []
    assert charge.charged_once([{"kind": "GRANT", "credits": 2000}, _row()], INVITATION) == []


@pytest.mark.parametrize("ledger, fault", [
    ([], "0 rows"),
    ([_row(), _row(id="b")], "2 rows"),
    ([_row(credits=-10)], "credits"),
    ([_row(price_credits=10)], "price_credits"),
    ([_row(price_version=11)], "price_version"),
    ([_row(kind="SPEND")], "kind"),
    ([_row(action="INTERPRET")], "action"),
    ([_row(inference_job_id="j")], "inference_job_id"),
    ([_row(actual_cost_micro_usd=60_000)], "actual_cost_micro_usd"),
    ([_row(reason="read-on-arrival:x")], "reason"),
    ([_row(project_id="another")], "project_id"),
])
def test_a_wrong_charge_is_named(ledger, fault):
    faults = charge.charged_once(ledger, INVITATION, PROJECT)
    assert faults and any(fault in f for f in faults), faults


def test_the_no_other_row_sweeps_let_a_begin_through_and_nothing_else():
    assert charge.is_charge(_row(), PROJECT) and charge.is_charge(_row())
    assert not charge.is_charge(_row(), "another project")
    assert not charge.is_charge(_row(idempotency_key="e2e-eval:044:x"))
    assert not charge.is_charge(_row(credits=-10))
    assert not charge.is_charge({"kind": "HOLD", "action": "INTERPRET", "credits": 0})
    assert charge.charges([_row(), {"kind": "GRANT", "credits": 5}], PROJECT) == [_row()]
    for leg in (interviewer_leg._leg, contacts_leg.leg_contacts):
        assert "charge.is_charge(x, j.project_id)" in inspect.getsource(leg), leg.__name__


def test_the_script_posts_begin_before_the_response():
    person = vs.PersonInputs(person="P", link=vs.LINK_PRIMARY, recency=True, story="A story.", anchor_chip=None,
                             picks=[], pilot_opt_in=False, anchoring=None)
    posts = person.scripted_posts("tok", None, format="TEXT")
    assert [p for p, _ in posts] == ["/interview/begin", "/interview/response"]
    assert posts[0][1] is None
    assert posts[1][1] == {**person.response("tok"), "format": "TEXT"}


def test_the_scripted_links_post_begin_first():
    choice = inspect.getsource(interviewer_leg._choice_link)
    assert "scripted_posts" in choice and "twice=True" in choice
    assert choice.index("_begin(") < choice.index('"POST", made["token"], response_path')
    recorded = inspect.getsource(interviewer_leg._recorded_link)
    assert "scripted_posts" in recorded
    assert recorded.index("_begin(") < recorded.index('"/interview/answer"') < recorded.index("response_path, body)")


def test_the_screens_read_the_row_behind_the_131_marker():
    for fn in (interviewer_leg._ai_link, interviewer_leg._chip_ends_it, contacts_leg._the_work):
        assert "_begun_on_screen(" in inspect.getsource(fn), fn.__name__
    for fn in (interviewer_leg._begun_on_screen, contacts_leg._begun_on_screen):
        source = inspect.getsource(fn)
        assert "charge.web_131_built()" in source and "WEB_131_PENDING" in source, fn.__name__


def test_the_marker_turns_on_for_one_run(monkeypatch):
    monkeypatch.setenv("KEEL_WEB_131", "1")
    assert charge.web_131_built()
    monkeypatch.delenv("KEEL_WEB_131")
    assert charge.web_131_built() is charge.WEB_131_BUILT
    assert charge.WEB_131_PENDING == "keel-web 131 not yet built"


def _web_sources() -> str:
    root = CONFIG.keel_web / "src"
    if not root.is_dir():
        pytest.skip("keel-web has no src/")
    return "\n".join(p.read_text(encoding="utf-8", errors="replace")
                     for p in root.rglob("*") if p.suffix in (".ts", ".tsx") and p.is_file())


@WEB_131
def test_keel_web_posts_begin_from_the_intro():
    """FR-2's browser half: keel-web 131 posts `interview/begin` when the intro's Begin (or Continue) is pressed."""
    assert "interview/begin" in _web_sources()


# ------------------------------------------------------------------------------------------ FR-3: the inactive link

CONTROLLER = "src/main/java/com/keeldiscovery/cloud/protocol/participant/InterviewController.java"


def test_the_inactive_body_is_keel_clouds():
    text = _cloud(CONTROLLER)
    if "Inactive" not in text:
        pytest.skip("keel-cloud predates spec 156 (no Inactive link)")
    assert f'"{charge.INACTIVE_STATE}", "{charge.INACTIVE_MESSAGE}"' in text
    assert '@PostMapping("/v2/i/{token}/interview/begin")' in text
    _, rows = _charge_table()
    assert charge.INACTIVE_BELOW == rows[charge.INTERVIEW]       # CreditPolicy.INTERVIEW_PRICE: inactive below one


def test_what_reads_inactive():
    assert charge.inactive_faults(200, dict(charge.INACTIVE_BODY)) == []
    assert charge.inactive_faults(404, charge.INACTIVE_BODY)
    assert charge.inactive_faults(200, {"state": "ALREADY_ANSWERED", "message": "Thanks"})
    assert charge.inactive_faults(200, {"state": "OPEN", "parts": [{}]})
    assert charge.inactive_faults(200, {**charge.INACTIVE_BODY, "creditsAvailable": 29})
    assert any("credits" in f for f in charge.inactive_faults(200, {"state": "INACTIVE",
                                                                   "message": "Out of credits: 29 left."}))


def test_what_reads_served():
    assert charge.served(200, {"state": "OPEN", "kind": "FULL", "parts": [{"items": []}]})
    assert not charge.served(200, charge.INACTIVE_BODY)
    assert not charge.served(200, {"state": "OPEN", "parts": []})
    assert not charge.served(404, {})


def test_what_the_page_may_say():
    assert charge.page_faults("This link is no longer active.") == []
    assert charge.page_faults("Keel\nThis link is no longer active.\n") == []
    assert charge.page_faults("This page doesn't exist.")
    assert charge.page_faults("This link is no longer active. The founder has 0 credits.")


def test_the_full_leg_walks_the_inactive_link_after_the_scripted_ones():
    leg = inspect.getsource(interviewer_leg._leg)
    assert leg.index("_recorded_link(j, wire, record)") < leg.index("_inactive_link(j, wire, record, founder_id, run)")
    assert leg.index("_inactive_link(") < leg.index("_change_face(j, wire, record)")
    assert leg.index("if not short:\n            _choice_link") < leg.index("_inactive_link(")
    walk = inspect.getsource(interviewer_leg._inactive_link)
    labels = re.findall(r'label="([a-z-]+)"', walk)
    assert labels == ["inactive-under", "inactive-at-one", "inactive-back"] and len(set(labels)) == 3
    order = [walk.index(s) for s in ('"inactive-under"', "inactive_faults", "_inactive_on_screen(", '"inactive-at-one"',
                                     "charge.served(", "_begin(", '"inactive-back"')]
    assert order == sorted(order)
    assert len(interviewer_leg.WAITING_PERSONS) == 2


def test_a_stand_in_label_is_one_word_of_the_key():
    with pytest.raises(ledger.LedgerUnavailable, match="label"):
        ledger.stand_in_balance(object(), "6f1c1a52-6a43-4f5e-9d39-0b7a2d6c1e11", "r", to=29, label="x'; DROP")
    source = inspect.getsource(ledger.stand_in_balance)
    assert 'key=f"{key_prefix(spec)}{run}:{label}"' in source and 'label: str = "low-balance"' in source


@WEB_131
def test_keel_web_draws_the_inactive_page():
    """FR-3's page: keel-web 131 renders INACTIVE as the one line (the ALREADY_ANSWERED way), no number, no credits."""
    sources = _web_sources()
    assert charge.INACTIVE_STATE in sources and charge.INACTIVE_MESSAGE in sources
