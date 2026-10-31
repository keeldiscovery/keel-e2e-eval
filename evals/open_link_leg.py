"""S-017: one open link for a group -- three strangers sign in with Google (spec 092; keel-cloud 162, contract 48;
keel-web 136; the design `canon/designs/open-link-design-2026-10-29.md` with its amendment of 2026-10-30).

The founder walks 01-countly's corridor to the lock on the scripted runtime (the same leg functions S-005 walks, the
golden seven's ALL study; no welcome held, no teaching, no people of the corpus invited), then stands on Keel's door with
a fresh grant (spec 043's stand-in, keyed `e2e-eval:092:` -- a lock on Keel's door never reaches READY on a stack with
no Keel's-AI key, and an own-AI founder makes no group link but a text one, writes no INTERVIEW row and is never
inactive) and records the interviewer the one way contract 16 gives a locked project with none (`POST interviewer/face`,
the fake renderer). Then, through keel-web 136's screens:

1. **The link.** Sent, *Send more* on the people-with-the-problem kind, *Let them choose*, *A group, with one open link*
   (the third way), the group named, *Make the link · Let them choose*; the one link read off the ready screen
   (`group-link-made`) -- that is the copy.
2. **Stranger A** (the browser) opens the link: the arrival card, as the group's token serves it (`GROUP_ARRIVAL`);
   *Continue with Google*, A's own button on the stub's picker, keel-cloud's participant callback, A's own `/i/{token}`;
   the intro greets A by the given name with *Signed in with Google as {A's email} · not you?* (keel-web 140, spec 094
   FR-2a: the served `Interview.arrival`, *not you?* the absolute `groupUrl`); *Answer in writing* is A's Begin
   (one INTERVIEW row of -30 on the ledger), A answers as Countly's first opted-in manager, and ticks the pilot box.
3. **Stranger B** (the browser) signs in the same way, begins (*Answer in writing*), answers the gate as another manager
   and stops on part 1's first question -- the page closed.
4. **Stranger C** signs in on the wire (`stack.auth.sign_in_arrival`) and never begins.
5. **A opens the link again**, signs in in the same browser: the callback's `keel_arrival_<group>` cookie brings A back to
   the same token, served ALREADY_ANSWERED (the page's one line).
6. **B opens it again**, signs in in the same browser: the same token, the intro, *Answer in writing* -- and the written
   interview resumes on part 1's first question, past the gate (keel-web's kept draft, by token); no second row.
7. **The founder's Sent**: the study line, *By group · 1* open (the latest answer is a group person's), the group's
   section (its name as typed, *1 of 20 answered*, its url, Copy link, Close link) and its three rows -- A answered with
   *See answers*, B opened not finished, C as the wire has them -- each with the stranger's email under the name and
   *Group · opened the link*; the wire's GroupRow (2 begun, 1 answered, 20 places, open).
8. **Close**: *Close link*, and a fourth stranger, D, is served the inactive line (the page, the wire, and start's 410).
9. **Reopen**: *Reopen*, and D's page is the arrival card again, 18 of 20 places left.
10. **The ledger**: exactly two INTERVIEW rows on this project -- A's and B's; C never began.
11. The founder back on their own door (the stand-in reversed, in a `finally`); **the brief's Pilot view** carries A,
    source *Group link*, A's email; the wire's `pilotPeople` one GROUP person with that email.

Every stranger is the stub's (`stack.auth.register_stranger`: an address under `strangers.keel-e2e-eval.test`, a `sub`
the stub derives); no real person's email is typed, read or printed. **Local only**: the stub issuer, the ledger and the
stand-in door are the local stack's, so the remote profile refuses the journey by name (`refusal`). No model, no vendor
and no money: the corridor is the scripted executor's, the recording the fake renderer's.
"""

from __future__ import annotations

import json
import re
import secrets
import time

import requests

from evals import corpus_facts
from evals import corpus_scenario as cs
from evals.preludes import own_ai_door
from harness import interview_charge as charge
from harness import interviewer_fake as fake
from harness import interviews_screens as iv_screens
from harness import vectors_screens as vs_screens
from harness import vectors_script as vs
from harness.browser import (Arrival, arrival_heading, arrival_hello, arrival_interviewer, arrival_places,
                             arrival_signed_in, ARRIVAL_CONSENT_WORDS, CHOICE_WRITE)
from harness.evidence import finalize_run, write_generated
from harness.steps import Recorder
from instructions import contract as contract_mod
from stack import auth as stack_auth
from stack import ledger as stack_ledger
from stack import remote

SPEC = "092"
ENTRY_ID = "01-countly"
SLUG = "s017-open-link"
#: The founder's own name for the group (1-60 characters, never shown to the people who open the link).
GROUP_NAME = "Restaurant managers' forum"
FORMAT = "CHOICE"
#: The four strangers -- letter, the name the stub's ID token carries. Fictional; their addresses are the stub's.
STRANGERS = (("a", "Maya Fenwick"), ("b", "Tomas Arden"), ("c", "Iris Calloway"), ("d", "Jun Halvorsen"))
#: The face the recording is made with: the one keel-cloud preselects.
FACE = fake.PRESELECTED
READY_WITHIN_S = 90
REMOTE_REFUSAL = ("S-017 refuses the remote profile (spec 092): its strangers are registered on the local stub issuer "
                  "and the founder stands on Keel's door through the local database -- on staging the participant "
                  "callback is the real Google client's, and the remote run of this journey is not part of the remote "
                  "six")


def refusal(stack) -> str | None:
    """The journey's one refusal: the remote profile, by name."""
    return REMOTE_REFUSAL if getattr(stack, "is_remote", False) else None


def stranger_ids(stamp: str) -> dict[str, str]:
    """`stranger-<letter>-<stamp>`: the stub's registry is per process and an id is refused once taken, so each run's
    strangers are its own (a second run on the same stack registers four new ones)."""
    return {letter: f"stranger-{letter}-{stamp}" for letter, _ in STRANGERS}


def stranger_people(people: list) -> tuple:
    """Who A and B answer as: A the first of the entry's people-with-the-problem who had one, told the story, sits inside
    the segment and opts in to the pilot; B the next such person (opted in or not). Countly's own answers, so the
    written walk is the corpus's (`vs_screens.Interview.walk`)."""
    def fits(p) -> bool:
        return (p.link == vs.LINK_PRIMARY and bool(p.recency) and bool(p.story) and not p.anchor_chip
                and getattr(p, "in_segment", True))
    a = next((p for p in people if fits(p) and p.pilot_opt_in), None)
    b = next((p for p in people if fits(p) and p is not a), None)
    if a is None or b is None:
        raise ValueError("the entry has no two people-with-the-problem with a story inside the segment, one opted in")
    return a, b


def ledger_faults(rows: list[dict], project_id: str, begun: dict[str, str]) -> list:
    """FR-2's ledger: exactly one INTERVIEW row of -30 per person who began (`begun`: letter -> invitation id), under
    `interview:<invitationId>`, and no other INTERVIEW row on the project."""
    charged = charge.charges(rows, project_id)
    faults = []
    keys = sorted(x.get("idempotency_key") for x in charged)
    want = sorted(charge.key(i) for i in begun.values())
    if keys != want:
        faults.append({"INTERVIEW rows": keys, "owed": want})
    others = [x for x in rows if x.get("kind") == charge.INTERVIEW and x.get("project_id") == project_id
              and x not in charged]
    if others:
        faults.append({"other INTERVIEW rows": others})
    return faults


def register_faults(rows: list[dict], wire: list[dict], people: dict) -> list:
    """FR-2's register: the group's rows as drawn against the wire's GROUP rows -- one row a stranger who signed in, the
    name and the email under it as stored, *Group · opened the link*, the status word of the wire's status, *See
    answers* on the answered one alone. `people`: letter -> StubStranger."""
    faults = []
    by_id = {r.get("invitationId"): r for r in wire}
    if sorted(r.get("invitation") for r in rows) != sorted(by_id):
        faults.append({"drawn": [r.get("invitation") for r in rows], "wire": sorted(by_id)})
    emails = {p.email: p for p in people.values()}
    for row in rows:
        w = by_id.get(row.get("invitation")) or {}
        stranger = emails.get(row.get("email") or "")
        if stranger is None or w.get("email") != row.get("email"):
            faults.append({"row": row.get("Who"), "email": row.get("email"), "wire": w.get("email")})
            continue
        if row.get("Who") != w.get("personName") or w.get("personName") != stranger.name:
            faults.append({"row": row.get("Who"), "wire": w.get("personName"), "stranger": stranger.name})
        if not row.get("email_under_name"):
            faults.append({"row": row.get("Who"), "email under the name": False})
        if row.get("Kind · from") != iv_screens.KIND_FROM_GROUP:
            faults.append({"row": row.get("Who"), "Kind · from": row.get("Kind · from")})
        word = iv_screens.REGISTER_STATUS.get(w.get("status") or "", "?")
        if not (row.get("Status") or "").startswith(word):
            faults.append({"row": row.get("Who"), "status": row.get("Status"), "wire": w.get("status")})
        action = [iv_screens.SEE_ANSWERS] if w.get("status") == "ANSWERED" else [iv_screens.NEW_LINK]
        if row.get("actions") != action:
            faults.append({"row": row.get("Who"), "actions": row.get("actions"), "owed": action})
    return faults


# ------------------------------------------------------------------------------------------------------- the wire

def _participant(j, token: str, suffix: str = "/interview", method: str = "GET") -> tuple[int, dict]:
    response = requests.request(method, f"{j.cloud_base}/v2/i/{token}{suffix}", timeout=20)
    try:
        body = response.json()
    except ValueError:
        body = {}
    return response.status_code, body if isinstance(body, dict) else {}


def _group_rows(j, group_id: str) -> tuple[dict, list[dict], dict]:
    register = j.get(j.project("/invitations")) or {}
    group = next((g for g in register.get("groups") or [] if g.get("groupId") == group_id), {})
    rows = [r for r in register.get("invitations") or [] if r.get("groupId") == group_id]
    return group, rows, register


def _invitation_of(rows: list[dict], stranger) -> str | None:
    return next((r.get("invitationId") for r in rows if r.get("email") == stranger.email), None)


def _wait_stem(page, text: str, timeout_s: float = 20) -> str:
    """The written interview's question (`h1.iv-q`) once it reads `text` -- or, after `timeout_s`, whatever it reads
    (the caller's step holds it to `text`, so a page on another screen is named, not timed out on)."""
    want = " ".join(text.split())
    deadline = time.monotonic() + timeout_s
    seen = ""
    while time.monotonic() < deadline:
        stem = page.locator("h1.iv-q")
        seen = " ".join((stem.first.text_content() or "").split()) if stem.count() else ""
        if seen == want:
            return seen
        page.wait_for_timeout(200)
    return seen or " ".join((page.locator("main").first.text_content() or "").split())[:400]


# ------------------------------------------------------------------------------------------------------ the legs

def corridor_to_lock(j) -> None:
    """The ALL study to its lock, through the leg functions S-005 walks in the order it walks them (S-012's way: the
    welcome passed by on Start, nothing of the guide judged)."""
    cs.leg_project(j)
    cs.leg_context(j)
    cs.leg_interpret_problem(j)
    cs.leg_calibrate(j, "PROBLEM")
    cs.leg_interpret_solution(j)
    cs.leg_calibrate(j, "SOLUTION")
    cs.leg_persona(j)
    cs.leg_calibrate(j, "COMMERCIAL")
    cs.leg_lock(j)


def keels_door(j, founder_id: str, run: str) -> None:
    with cs._step(j, "STAND-IN (spec 043's, keyed e2e-eval:092:): the founder on Keel's door with a fresh grant of "
                     "2,000 -- an own-AI founder makes no group link but a text one and writes no INTERVIEW row",
                  party="stack", kind="protocol") as h:
        added = stack_ledger.stand_in_keels_door(j.stack, founder_id, run, spec=SPEC)
        me = j.get("/v2/me") or {}
        h.record_wire({"stand-in": "ai_path KEEL + GRANT", "credits added": added},
                      {"aiPath": me.get("aiPath"), "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "KEEL" and me.get("creditsAvailable") == stack_ledger.GRANT_CREDITS, me


def restore(j, founder_id: str, run: str) -> None:
    with cs._step(j, "STAND-IN reversed: the founder back on their own door with nothing to spend", party="stack",
                  kind="protocol") as h:
        taken = stack_ledger.restore_own_door(j.stack, founder_id, run, spec=SPEC)
        me = j.get("/v2/me") or {}
        h.record_wire({"closing row": taken}, {"aiPath": me.get("aiPath"), "creditsAvailable": me.get("creditsAvailable")})
        assert me.get("aiPath") == "OWN", me


def record_the_interviewer(j, record: dict) -> None:
    with cs._step(j, f"the interviewer recorded on Keel's door (contract 16: POST interviewer/face on a project locked "
                     f"with none; {fake.FACE_NAMES[FACE]}, the fake renderer) and READY -- Let them choose needs a "
                     "served recording", party="founder", kind="assert") as h:
        status, view = j.call("POST", j.project("/interviewer/face"), {"face": FACE})
        started, trail = time.monotonic(), []
        while time.monotonic() - started < READY_WITHIN_S:
            view = j.get(j.project("/interviewer")) or {}
            if not trail or trail[-1] != view.get("status"):
                trail.append(view.get("status"))
            if view.get("status") in ("READY", "FAILED"):
                break
            time.sleep(1)
        record["recording"] = {"status": status, "trail": trail, "face": (view.get("face") or {}).get("code")}
        h.record_assert({"status": "READY", "face": FACE}, record["recording"])
        assert view.get("status") == "READY" and (view.get("face") or {}).get("code") == FACE, (trail, view)


def make_the_link(j, sent, record: dict) -> dict:
    register = j.get(j.project("/invitations")) or {}
    kinds = {k.get("respondentType"): k for k in register.get("kinds") or []}
    primary = kinds[vs.LINK_PRIMARY]
    made = sent.send_group(j.project_id, primary.get("label"), GROUP_NAME, FORMAT)
    record["made"] = made
    with cs._step(j, "keel-web 136 FR-1: Send more's third way -- the three ways in order, the group named, the cap line "
                     "fixed, *Make the link · Let them choose* posting POST groups {expectedRevision, roleId, name, "
                     "format}; 201 {groupId, url}, the link shown once", party="founder") as h:
        sent_body = made.get("sent") or {}
        want = {"ways": [iv_screens.WHO_OWN, iv_screens.WHO_DATASET, iv_screens.WHO_GROUP],
                "ids": list(iv_screens.SEND_WHO_IDS),
                "panel": {"label": iv_screens.SEND_GROUP_NAME_LABEL, "max_length": str(iv_screens.GROUP_NAME_MAX),
                          "placeholder": iv_screens.SEND_GROUP_NAME_EXAMPLE, "cap": iv_screens.SEND_GROUP_CAP_LINE},
                "button": iv_screens.send_make_group(iv_screens.FORMAT_NAMES[FORMAT]), "status": 201,
                "sent": {"roleId": primary.get("roleId"), "name": GROUP_NAME, "format": FORMAT},
                "ready": iv_screens.send_group_ready(GROUP_NAME)}
        h.record_assert(want, made)
        assert made.get("status") == 201, made
        assert [w["name"] for w in made["ways"]] == want["ways"], made["ways"]
        assert [w["id"] for w in made["ways"]] == want["ids"], made["ways"]
        assert {k: made["panel"].get(k) for k in want["panel"]} == want["panel"], made["panel"]
        assert made["panel"]["cap_lead"] == iv_screens.SEND_GROUP_CAP_LINE.split(" After")[0], made["panel"]
        assert made["button"] == want["button"] and made["button_disabled_before"] is True, made
        assert {k: sent_body.get(k) for k in ("roleId", "name", "format")} == want["sent"], sent_body
        assert isinstance(sent_body.get("expectedRevision"), int), sent_body
        assert made["url"] == (made.get("made") or {}).get("url") and made["made"].get("groupId"), made
        assert made["ready"] == want["ready"] and made["copy"] == 1, made
        assert iv_screens.SEND_GROUP_HINT in made["hint"], made["hint"]
    return made


def read_the_card(j, arrival: Arrival, group_url: str, group_token: str, places: int, what: str) -> dict:
    card = arrival.open(group_url, title=f"{what} opens the group link")
    _, served = _participant(j, group_token)
    face = served.get("interviewer") or {}
    with cs._step(j, f"{what}: the arrival card as the group's token serves it -- who is asking and about what, the "
                     f"interviewer's row ({face.get('name') or 'no face'}: keel-web 140, contract 49), {places} of 20 "
                     "places, Continue with Google (a link to signInUrl), the sentence; no Begin",
                  party="participant") as h:
        # spec 094 FR-2a (keel-web 140 FR-1, contract 49): the row names the served face, or 136's words when it is null
        want = {"state": "GROUP_ARRIVAL",
                "heading": arrival_heading(served.get("founderName") or "", served.get("title") or ""),
                "interviewer": arrival_interviewer(int(served.get("minutes") or 0), face.get("name")),
                "interviewer_name": face.get("name"), "interviewer_face": 1 if face else 0,
                "places": arrival_places(places), "href": served.get("signInUrl"), "consent": ARRIVAL_CONSENT_WORDS}
        h.record_assert({**want, "served": {"state": "GROUP_ARRIVAL", "placesLeft": places}},
                        {"card": card, "served": served})
        assert served.get("state") == "GROUP_ARRIVAL" and served.get("placesLeft") == places, served
        assert served.get("founderName") and served.get("signInUrl") == f"/v2/i/{group_token}/auth/google/start", served
        assert card["state"] == "GROUP_ARRIVAL" and card["heading_tag"] == "H1", card
        assert (card["heading"], card["interviewer"], card["places"]) == (want["heading"], want["interviewer"],
                                                                         want["places"]), card
        assert (card["interviewer_name"], card["interviewer_face"]) == (want["interviewer_name"],
                                                                        want["interviewer_face"]), card
        assert card["google"]["href"] == want["href"] and card["google"]["tag"] == "A", card["google"]
        assert card["google"]["role_link"] == 1 and card["consent"] == ARRIVAL_CONSENT_WORDS, card
        assert card["begin"] == 0 and card["auth_error"] is None, card
    return card


def sign_in_in_the_browser(j, arrival: Arrival, stranger, group_token: str, what: str) -> dict:
    landed = arrival.sign_in(stranger, title=f"{what} ({stranger.name}) signs in with Google on the group link")
    with cs._step(j, f"{what}: the round trip -- Continue with Google, {stranger.given_name}'s own button on the stub's "
                     "picker, keel-cloud's participant callback -- lands on their own link, not the group's",
                  party="participant") as h:
        h.record_assert({"auth_error": None, "token": "the arrival's own"}, landed)
        assert landed["auth_error"] is None and landed["token"] and landed["token"] != group_token, landed
    return landed


def read_the_intro(j, arrival: Arrival, stranger, token: str, group_token: str, what: str) -> tuple[dict, dict]:
    status, interview = _participant(j, token)
    intro = arrival.intro()
    with cs._step(j, f"{what}: their own link serves the interview (FULL, the given name, text or the interviewer, and "
                     "the arrival: the email and the group's url) and the intro greets them -- *Hi "
                     f"{stranger.given_name}.* and *Signed in with Google as {{email}} · not you?* back to the group's "
                     "page, the absolute groupUrl (keel-web 140 FR-2, contract 49)", party="participant") as h:
        heading = arrival_heading(interview.get("founderName") or "", interview.get("topic") or "")
        arrived = interview.get("arrival") or {}
        # spec 094 FR-2a (keel-web 140 FR-2): the who line is the served email, *not you?* the served groupUrl as is
        want = {"kind": "FULL", "personName": stranger.given_name, "formats": ["TEXT", "AI_INTERVIEWER"],
                "intro": FORMAT, "greeting": arrival_hello(stranger.given_name, heading),
                "who": arrival_signed_in(stranger.email), "not_you": arrived.get("groupUrl"),
                "arrival": {"email": stranger.email, "groupUrl": f"http(s)://…/{group_token}"},
                "buttons": ["choice-talk", CHOICE_WRITE]}
        h.record_assert(want, {"status": status, "interview": {k: interview.get(k) for k in
                                                               ("kind", "personName", "formats", "arrival")},
                               "intro": intro})
        assert status == 200 and interview.get("kind") == "FULL", (status, interview.get("kind"))
        assert interview.get("personName") == stranger.given_name, interview.get("personName")
        assert interview.get("formats") == want["formats"], interview.get("formats")
        # contract 49 (keel-cloud 164): the stored email and the group's own url, on this token only
        assert arrived.get("email") == stranger.email, interview.get("arrival")
        assert re.match(r"^https?://", arrived.get("groupUrl") or "") and \
            arrived["groupUrl"].endswith(f"/{group_token}"), arrived
        assert intro["state"] == "INTERVIEW" and intro["intro"] == FORMAT, intro
        assert (intro["greeting"], intro["who"], intro["not_you"]) == (want["greeting"], want["who"], want["not_you"]), \
            intro
        assert intro["buttons"] == want["buttons"], intro
    return interview, intro


def _ledger_now(j, founder_id: str, since: str) -> list[dict]:
    return stack_ledger.rows(j.stack, founder_id, since=since)


def _begun_rows(j, founder_id: str, since: str, invitation_id: str) -> list[dict]:
    return charge.rows_for(_ledger_now(j, founder_id, since), invitation_id)


def stranger_a(j, ctx: dict, record: dict) -> None:
    a, person = ctx["strangers"]["a"], ctx["person_a"]
    page = ctx["contexts"]["a"].new_page()
    arrival = Arrival(page, j.recorder, j.web_base)
    record["cards"]["a"] = read_the_card(j, arrival, ctx["url"], ctx["group_token"], 20, "stranger A")
    landed = sign_in_in_the_browser(j, arrival, a, ctx["group_token"], "stranger A")
    token = ctx["tokens"]["a"] = landed["token"]
    interview, intro = read_the_intro(j, arrival, a, token, ctx["group_token"], "stranger A")
    record["intros"]["a"] = intro
    items = {i.get("dimension"): i for part in interview.get("parts") or [] for i in part.get("items") or []}
    person = cs._served_options(j, person, items)
    recall = ((items.get("commercial.existing_sacrifice") or {}).get("costTotal") or {}).get("recallPeriod")
    expected = person.response(token, recall)
    by_item = {x["itemId"]: x for x in expected.get("answers") or []}
    screens = vs_screens.Interview(page, j.recorder)
    walked = screens.walk(person, interview, by_item, begin=CHOICE_WRITE)
    _, rows, _ = _group_rows(j, ctx["group_id"])
    ctx["invitations"]["a"] = _invitation_of(rows, a)
    begun = _begun_rows(j, ctx["founder_id"], ctx["since"], ctx["invitations"]["a"] or "")
    with cs._step(j, f"stranger A: *Answer in writing* is the Begin -- one INTERVIEW row of -30 under interview:<A's "
                     f"invitation> -- and A answers as {person.person} (the corpus's answers), sent in writing",
                  party="participant") as h:
        h.record_assert({"rows": 1, "credits": -charge.INTERVIEW_CREDITS, "status": 201},
                        {"rows": begun, "status": walked.get("status"), "body": walked.get("body"),
                         "expected": expected})
        assert len(begun) == 1 and int(begun[0].get("credits")) == -charge.INTERVIEW_CREDITS, begun
        assert walked.get("status") in (200, 201), walked.get("status")
        assert (walked.get("body") or {}).get("format") == "TEXT", walked.get("body")
        assert walked.get("pilot_box"), "the thank-you drew no pilot box"
    screens.opt_in_to_pilot(interview)
    with cs._step(j, "stranger A ticks the pilot box (POST interview/pilot, 204) -- stored on A's invitation",
                  party="participant") as h:
        opted = stack_ledger.pilot_opt_in(j.stack, j.project_id, ctx["invitations"]["a"])
        h.record_assert({"pilotOptIn": True}, {"pilotOptIn": opted})
        assert opted is True, opted
    record["walked"]["a"] = {"status": walked.get("status"), "done": walked.get("done")}
    page.close()


def stranger_b(j, ctx: dict, record: dict) -> None:
    b, person = ctx["strangers"]["b"], ctx["person_b"]
    page = ctx["contexts"]["b"].new_page()
    arrival = Arrival(page, j.recorder, j.web_base)
    record["cards"]["b"] = read_the_card(j, arrival, ctx["url"], ctx["group_token"], 19, "stranger B")
    landed = sign_in_in_the_browser(j, arrival, b, ctx["group_token"], "stranger B")
    token = ctx["tokens"]["b"] = landed["token"]
    interview, intro = read_the_intro(j, arrival, b, token, ctx["group_token"], "stranger B")
    record["intros"]["b"] = intro
    ctx["interview_b"] = interview
    first = ((interview.get("parts") or [{}])[0].get("items") or [{}])[0]
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith(vs.BEGIN_PATH),
                              timeout=30_000) as began:
        arrival.write_my_answers()
    screens = vs_screens.Interview(page, j.recorder)
    screens._gate(person, interview.get("gate") or {}, interview.get("occasion"))
    stem = _wait_stem(page, first.get("question") or "")
    _, rows, _ = _group_rows(j, ctx["group_id"])
    ctx["invitations"]["b"] = _invitation_of(rows, b)
    begun = _begun_rows(j, ctx["founder_id"], ctx["since"], ctx["invitations"]["b"] or "")
    with cs._step(j, f"stranger B begins (*Answer in writing*: one INTERVIEW row), answers the gate as {person.person}, "
                     "and stops on part 1's first question -- the page closed, nothing sent", party="participant") as h:
        h.record_assert({"begin": charge.BEGIN_STATUS, "rows": 1, "stem": first.get("question")},
                        {"begin": began.value.status, "rows": begun, "stem": stem})
        assert began.value.status == charge.BEGIN_STATUS, began.value.status
        assert len(begun) == 1 and int(begun[0].get("credits")) == -charge.INTERVIEW_CREDITS, begun
        assert stem == " ".join((first.get("question") or "").split()), stem
    record["paused"] = {"stem": stem, "item": first.get("dimension")}
    page.close()


def stranger_c(j, ctx: dict, record: dict) -> None:
    c = ctx["strangers"]["c"]
    _, signed = stack_auth.sign_in_arrival(j.stack, ctx["url"], c)
    status, interview = _participant(j, signed.token or "") if signed.token else (None, {})
    record["wire_sign_in"] = {"hops": [list(x) for x in signed.hops], "cookie": signed.cookie,
                              "refused": signed.refused, "auth_error": signed.auth_error}
    with cs._step(j, "stranger C signs in on the wire (start -> the stub's /authorize with identity= -> the participant "
                     "callback -> C's own /i/{token}, the keel_arrival_ cookie set) and never begins: C's link is served",
                  party="participant") as h:
        h.record_assert({"hops": [302, 302, 302], "token": "C's own", "cookie": "keel_arrival_<group>",
                         "served": {"kind": "FULL", "personName": c.given_name}},
                        {**record["wire_sign_in"], "status": status,
                         "served": {k: interview.get(k) for k in ("state", "kind", "personName")}})
        assert [s for s, _ in signed.hops] == [302, 302, 302] and signed.token, signed
        assert signed.token not in (ctx["group_token"], ctx["tokens"].get("a"), ctx["tokens"].get("b")), signed
        assert (signed.cookie or "").startswith(stack_auth.ARRIVAL_COOKIE_PREFIX), signed
        assert status == 200 and interview.get("kind") == "FULL" and interview.get("personName") == c.given_name, \
            interview
    ctx["tokens"]["c"] = signed.token
    _, rows, _ = _group_rows(j, ctx["group_id"])
    ctx["invitations"]["c"] = _invitation_of(rows, c)


def a_again(j, ctx: dict, record: dict) -> None:
    a = ctx["strangers"]["a"]
    page = ctx["contexts"]["a"].new_page()
    arrival = Arrival(page, j.recorder, j.web_base)
    record["cards"]["a_again"] = read_the_card(j, arrival, ctx["url"], ctx["group_token"], 18, "stranger A, again")
    landed = sign_in_in_the_browser(j, arrival, a, ctx["group_token"], "stranger A, again")
    line = arrival.intro()
    _, served = _participant(j, landed["token"])
    with cs._step(j, "stranger A opens the link again and signs in in the same browser: the same token (keel-cloud's "
                     "keel_arrival_ cookie), served ALREADY_ANSWERED -- the page's one line", party="participant") as h:
        h.record_assert({"token": ctx["tokens"]["a"], "state": "ALREADY_ANSWERED"},
                        {"token": landed["token"], "page": line, "served": served})
        assert landed["token"] == ctx["tokens"]["a"], landed
        assert served.get("state") == "ALREADY_ANSWERED", served
        assert line["state"] == "ALREADY_ANSWERED" and line["line"] == served.get("message"), line
    page.close()


def b_again(j, ctx: dict, record: dict) -> None:
    b = ctx["strangers"]["b"]
    page = ctx["contexts"]["b"].new_page()
    arrival = Arrival(page, j.recorder, j.web_base)
    arrival.open(ctx["url"], title="stranger B opens the group link again")
    landed = sign_in_in_the_browser(j, arrival, b, ctx["group_token"], "stranger B, again")
    intro = arrival.intro()
    with page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith(vs.BEGIN_PATH),
                              timeout=30_000) as began:
        arrival.write_my_answers()
    stem = _wait_stem(page, record["paused"]["stem"])
    gate = (ctx["interview_b"].get("gate") or {}).get("question") or ""
    gate_drawn = page.get_by_role("radiogroup", name=gate, exact=True).count() if gate else 0
    begun = _begun_rows(j, ctx["founder_id"], ctx["since"], ctx["invitations"]["b"] or "")
    with cs._step(j, "stranger B opens it again and signs in in the same browser: the same token, the intro, and *Answer "
                     "in writing* resumes on part 1's first question, past the gate (the kept draft); Begin again "
                     "writes no second row", party="participant") as h:
        h.record_assert({"token": ctx["tokens"]["b"], "stem": record["paused"]["stem"], "gate": 0, "rows": 1},
                        {"token": landed["token"], "intro": intro, "begin": began.value.status, "stem": stem,
                         "gate": gate_drawn, "rows": begun})
        assert landed["token"] == ctx["tokens"]["b"], landed
        assert intro["state"] == "INTERVIEW" and intro["intro"] == FORMAT, intro
        assert began.value.status == charge.BEGIN_STATUS and stem == record["paused"]["stem"], (began.value.status, stem)
        assert gate_drawn == 0 and len(begun) == 1, (gate_drawn, begun)
    page.close()


def the_register(j, sent, ctx: dict, record: dict) -> None:
    group, rows, register = _group_rows(j, ctx["group_id"])
    sent.land(j.project_id)
    tabs = sent.tabs()
    line = sent.study_line()
    if not (tabs.get("group") or {}).get("selected"):
        tabs = sent.open_tab("group")
    drawn = sent.groups()
    record["sent"] = {"tabs": tabs, "line": line, "groups": drawn, "wire": {"group": group, "rows": rows}}
    kinds = register.get("kinds") or []
    answered = sum(int(k.get("answered") or 0) for k in kinds)
    planned = sum(int(k.get("linksMade") or 0) for k in kinds)
    named = [r for r in register.get("invitations") or [] if not r.get("groupId")]
    with cs._step(j, "the founder's Sent (keel-web 136 FR-2): the study line, By group · 1 open (the latest answer is "
                     "a group person's), the group's section -- its name as typed, 1 of 20 answered, its url (the "
                     "section's data-url, eval 098), Copy link, Close link -- and three rows, each with the email "
                     "under the name, *Group · opened the link*, *See answers* on A's", party="founder") as h:
        want_line = iv_screens.sent_study_line(answered, planned)
        h.record_assert({"tabs": {"name": iv_screens.sent_tab_by_name(len(named)),
                                  "group": iv_screens.sent_tab_by_group(1), "open": "group"},
                         "line": want_line + " · {counted}", "group": {"name": GROUP_NAME,
                                                                      "count": iv_screens.group_answered(1),
                                                                      "url": ctx["url"]},
                         "wire": {"begun": 2, "answered": 1, "cap": 20, "closedAt": None, "format": FORMAT,
                                  "rows": 3}}, record["sent"])
        assert tabs.get("label") == iv_screens.SENT_TABS_LABEL, tabs
        assert tabs["group"] == {"text": iv_screens.sent_tab_by_group(1), "role": "tab", "selected": True}, tabs
        assert tabs["name"]["text"] == iv_screens.sent_tab_by_name(len(named)) and not tabs["name"]["selected"], tabs
        assert line and (line == want_line or line.startswith(f"{want_line} · ")), (line, want_line)
        assert (group.get("begun"), group.get("answered"), group.get("cap"), group.get("closedAt")) == (2, 1, 20, None), \
            group
        assert group.get("name") == GROUP_NAME and group.get("format") == FORMAT and group.get("url") == ctx["url"], group
        assert len(drawn) == 1, drawn
        section = drawn[0]
        assert section["id"] == ctx["group_id"] and section["closed"] == "false", section
        assert section["name"] == GROUP_NAME and section["count"] == iv_screens.group_answered(1), section
        assert section["url"] == ctx["url"] and section["copy"] == iv_screens.group_link_label(GROUP_NAME), section
        assert section["close"] == iv_screens.GROUP_CLOSE_WORD and section["reopen"] is None, section
        letters = ("a", "b", "c")
        assert len(rows) == 3 and {r.get("email") for r in rows} == {ctx["strangers"][x].email for x in letters}, rows
        assert all(r.get("source") == "GROUP" for r in rows), rows
        status = {x: next(r.get("status") for r in rows if r.get("email") == ctx["strangers"][x].email) for x in letters}
        assert status["a"] == "ANSWERED" and status["b"] == "OPENED" and status["c"] in ("SENT", "OPENED"), status
        faults = register_faults(section["rows"], rows, ctx["strangers"])
        assert not faults, json.dumps(faults, indent=2, default=str)


def close_and_reopen(j, sent, ctx: dict, record: dict) -> None:
    closed = sent.close_group(ctx["group_id"])
    group, _, _ = _group_rows(j, ctx["group_id"])
    page = ctx["contexts"]["d"].new_page()
    arrival = Arrival(page, j.recorder, j.web_base)
    shut = arrival.open(ctx["url"], title="stranger D opens the closed group link")
    _, served = _participant(j, ctx["group_token"])
    _, refused = stack_auth.sign_in_arrival(j.stack, ctx["url"], ctx["strangers"]["d"])
    record["closed"] = {"pressed": closed, "group": group, "page": shut, "served": served, "start": refused.refused}
    with cs._step(j, "the founder presses Close link: the section greyed with Reopen, the wire's closedAt set -- and a "
                     "fourth stranger, D, is served the inactive line (the page, GET interview, and start 410)",
                  party="founder") as h:
        h.record_assert({"close": 204, "closed": "true", "reopen": iv_screens.GROUP_REOPEN_WORD,
                         "page": charge.INACTIVE_MESSAGE, "served": charge.INACTIVE_BODY, "start": 410},
                        record["closed"])
        assert closed["status"] == 204 and closed["group"].get("closed") == "true", closed
        assert closed["group"].get("reopen") == iv_screens.GROUP_REOPEN_WORD and closed["group"].get("close") is None, \
            closed["group"]
        assert closed["group"].get("count", "").startswith(iv_screens.group_answered(1)), closed["group"]
        assert group.get("closedAt"), group
        assert shut["state"] == "INACTIVE" and shut["inactive"] == charge.INACTIVE_MESSAGE, shut
        assert served == charge.INACTIVE_BODY, served
        assert refused.refused == 410 and refused.token is None, refused
    reopened = sent.reopen_group(ctx["group_id"])
    group, _, _ = _group_rows(j, ctx["group_id"])
    with cs._step(j, "the founder presses Reopen: the section open again, closedAt null -- and the group's page serves "
                     "the arrival card to D once more, 18 of 20 places left", party="founder") as h:
        h.record_assert({"reopen": 204, "closed": "false", "closedAt": None}, {"pressed": reopened, "group": group})
        assert reopened["status"] == 204 and reopened["group"].get("closed") == "false", reopened
        assert group.get("closedAt") is None, group
    record["cards"]["d_reopened"] = read_the_card(j, arrival, ctx["url"], ctx["group_token"], 18, "stranger D, reopened")
    page.close()


def the_ledger(j, ctx: dict, record: dict) -> None:
    rows = _ledger_now(j, ctx["founder_id"], ctx["since"])
    begun = {x: ctx["invitations"][x] for x in ("a", "b")}
    faults = ledger_faults(rows, j.project_id, begun)
    record["ledger"] = [(x.get("kind"), x.get("action"), x.get("credits"), x.get("idempotency_key")) for x in rows]
    with cs._step(j, "the ledger since Keel's door: exactly two INTERVIEW rows of -30 on this project, A's and B's -- C "
                     "signed in and never began, D never got in", party="stack", kind="assert") as h:
        h.record_assert({"INTERVIEW": sorted(charge.key(i) for i in begun.values())},
                        {"rows": record["ledger"], "faults": faults})
        assert all(begun.values()) and ctx["invitations"]["c"], ctx["invitations"]
        assert not faults, json.dumps(faults, indent=2, default=str)


def the_pilot(j, ctx: dict, record: dict) -> None:
    standings = j.get(j.project("/standings")) or {}
    people = standings.get("pilotPeople") or []
    view = j.answers.pilot(j.project_id)
    a = ctx["strangers"]["a"]
    record["pilot"] = {"wire": people, "view": view}
    with cs._step(j, "the brief's Pilot view: A, who ticked the box, with A's Google email -- the wire's pilotPeople one "
                     "GROUP person with that email (keel-cloud 162 FR-5, keel-web 136)", party="founder") as h:
        h.record_assert({"wire": [{"invitationId": ctx["invitations"]["a"], "source": "GROUP", "email": a.email}],
                         "view": [{"invitation": ctx["invitations"]["a"], "email": a.email}]}, record["pilot"])
        assert [(p.get("invitationId"), p.get("source"), p.get("email")) for p in people] == [
            (ctx["invitations"]["a"], "GROUP", a.email)], people
        assert [(p.get("invitation"), p.get("email")) for p in view["people"]] == [(ctx["invitations"]["a"], a.email)], \
            view["people"]


def leg_open_link(j, browser, record: dict) -> None:
    """Steps 1-11 of this module's docstring, on a project already locked (`corridor_to_lock`)."""
    account = stack_ledger.founder_account(j.stack, j.founder_identity.sub)
    stamp = f"{time.strftime('%m%d%H%M%S', time.gmtime())}{secrets.token_hex(2)}"
    ids = stranger_ids(stamp)
    ctx: dict = {"founder_id": account["id"], "since": stack_ledger.now(j.stack), "tokens": {}, "invitations": {},
                 "contexts": {}}
    ctx["person_a"], ctx["person_b"] = stranger_people(j.people)
    run = f"{j.project_id}:{int(time.time())}"
    record.update({"cards": {}, "intros": {}, "walked": {}, "founder_id": ctx["founder_id"]})
    restored = False
    try:
        keels_door(j, ctx["founder_id"], run)
        record_the_interviewer(j, record)
        with cs._step(j, "four strangers registered on the stub issuer (POST /identities): fictional names, addresses "
                         f"under {stack_auth.STRANGER_EMAIL_DOMAIN}, each `sub` the stub's", party="stack",
                      kind="protocol") as h:
            ctx["strangers"] = {letter: stack_auth.register_stranger(j.stack, ids[letter], name)
                                for letter, name in STRANGERS}
            record["strangers"] = {x: {"id": s.id, "sub": s.sub, "email": s.email, "name": s.name}
                                   for x, s in ctx["strangers"].items()}
            h.record_wire({"ids": ids}, record["strangers"])
            assert all(s.sub == f"cell-{s.id}" for s in ctx["strangers"].values()), record["strangers"]
        sent = iv_screens.Interviews(j.page, j.recorder, j.web_base, patience=j.patience, guide=j.guide)
        made = make_the_link(j, sent, record)
        ctx["url"], ctx["group_id"] = made["url"], made["made"]["groupId"]
        ctx["group_token"] = stack_auth.token_of(ctx["url"])
        ctx["contexts"] = {x: browser.new_context() for x in ("a", "b", "d")}
        try:
            stranger_a(j, ctx, record)
            stranger_b(j, ctx, record)
            stranger_c(j, ctx, record)
            a_again(j, ctx, record)
            b_again(j, ctx, record)
            the_register(j, sent, ctx, record)
            close_and_reopen(j, sent, ctx, record)
            the_ledger(j, ctx, record)
        finally:
            for context in ctx["contexts"].values():
                context.close()
        restore(j, ctx["founder_id"], run)
        restored = True
        the_pilot(j, ctx, record)
    finally:
        record["tokens"] = {x: bool(t) for x, t in ctx["tokens"].items()}
        record["invitations"] = dict(ctx["invitations"])
        if not restored:
            try:
                stack_ledger.restore_own_door(j.stack, ctx["founder_id"], run, spec=SPEC)
            except Exception as failed:  # noqa: BLE001 - the leg's own failure is the one to report
                record["restore_failed"] = str(failed)


# ------------------------------------------------------------------------------------------------------- the run

def run(stack, founder_one, browser, run_dir) -> None:
    recorder = Recorder(run_dir)
    web_base = stack.web_base_url
    cell_label = f"{remote.cell_name()} · {SLUG} · {time.strftime('%Y-%m-%d', time.gmtime())}"
    founder_one = remote.identity_to_sign_in_as(stack, cell_label, fallback=founder_one)
    corpus, entry = vs.entry_for(stack.keel_cloud, ENTRY_ID)
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    hashes_before = dict(corpus.hashes)
    script = vs.generate(entry)
    founder = vs.founder_inputs(entry)
    people = vs.person_inputs(entry)
    write_generated(run_dir, script=script.to_json(), inputs=vs.inputs_json(entry, founder, people))
    record: dict = {"entry": ENTRY_ID, "group": GROUP_NAME, "format": FORMAT}
    try:
        exported = contract_mod.export(stack.keel_cloud, run_dir / "export")
        keys_path = run_dir / "context-keys.json"
        keys_path.write_text(json.dumps(vs.context_keys_for(exported.context_keys), indent=2) + "\n", encoding="utf-8")
        page = context.new_page()
        j = cs.open_journey(recorder, page, context, browser, stack, entry, founder, people, script=script,
                            registry=exported.registry)
        j.stack, j.founder_identity = stack, founder_one
        user_code = cs._connect(stack, recorder, page, founder_one, web_base, run_dir, keys_path)
        own_ai_door(page, recorder, stack, j.get, through_the_code_story=bool(user_code))
        corridor_to_lock(j)
        record["project_id"] = j.project_id
        leg_open_link(j, browser, record)
        with recorder.step("the corpus hashes exactly as it did when the run began", party="stack", kind="assert") as h:
            corpus.verify_unchanged()
            h.record_assert(hashes_before, dict(corpus.hashes))
        passed = True
    finally:
        (run_dir / "open-link.json").write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8")
        context.close()
        finalize_run(run_dir, slug=SLUG, facts=corpus_facts.vectors_facts_for(entry), passed=passed,
                     failed_step=recorder.failed_step, duration_s=time.monotonic() - started)
        print(f"\nrun bundle: {run_dir}")
