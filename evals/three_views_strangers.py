"""Spec 157 FR-2: **the stranger's legs, three views each** -- each locked project's link (the problem of FR-1 (d), the
solution of FR-1 (b), the money of FR-1 (c)) walked in the text view, the AI avatar view and the copilot view, with
a No on the gate, the anchor and the decision-maker's third-person check ending the interview in every view.

* **text** (keel-web 241 FR-7, 242 FR-4, 243 FR-2): `story_screens.StoryLinkText` -- the screener on its own card, the
  story card, the gate (the anchor on a solution link) with both chips under the story question, each item, the idea
  card and the idea's story card, held to the wire: every served card carries a `clipId` (keel-cloud 259 FR-9) and
  draws the voice bar; the answers are the copilot strip's lettered bubbles.
* **avatar** (241 FR-8, 242 FR-4): the AI link through the stack's fake renderer and the seam's recorder -- the
  hand-over card (the story full frame), Daphne's return, no *Type instead*, *Back to question n* on every question.
* **copilot** (241 FR-9, 242 FR-4): a call planned on the project, the card opened headless on the fake sources (spec
  154's way), the strips in order, *Show the story* / *Story again* growing the window (under half the viewport, the
  card still drawn) and its return, the recorded answer uploaded at End.

Nothing here is new product: what these views draw is keel-web's; the walk reads it and the leg judges it.
"""

from __future__ import annotations

import json
import re
import time

from evals import corpus_scenario as cs
from evals import three_views as tv
from harness import interviewer_fake as fake
from harness import story_screens as ss

#: keel-cloud 259 FR-8: the gate's (and the anchor's) wording on a story link.
STORY_GATE = "In your last {window}, did this happen to you?"
#: The face the avatar legs record (the preselected one, keel-cloud 143).
FACE = fake.PRESELECTED


def window_words(window: dict) -> str:
    from harness.vectors_script import Window, window_words as words   # noqa: PLC0415
    return words(Window(count=int(window["count"]), unit=str(window["unit"])))


def study_project(run: "tv.Run", study: str) -> str | None:
    return {"problem": run.projects.get("b-problem"), "solution": run.projects.get("b-solution"),
            "money": run.projects.get("c-money")}[study]


# ------------------------------------------------------------------------------------------------ preparing a study

def lock_the_solution(run: "tv.Run", leg: "tv.Leg") -> bool:
    """The solution project of FR-1 (b), calibrated (Compatibility, Relative advantage pre-filled, Adoption friction) and
    locked once on the founder's runtime, so its link can be served. True where it locked."""
    solution = run.projects.get("b-solution")
    if not solution:
        return False
    if (run.get(f"/v2/projects/{solution}/overview") or {}).get("questionsState") == "READY":
        return True
    # the solution's chain was answered at the idea's yes (FR-1 (b)); a runtime started since begins past it
    run.load_runtime("SOLUTION", consumed=1 if run.runtime_scope != "SOLUTION" else 0)
    j = run.journey("s", "SOLUTION", solution)
    idea = run.get(f"/v2/projects/{solution}/idea") or {}
    j.idea_name = str(idea.get("shortName") or idea.get("what") or "")
    j.idea_what_it_is = idea.get("whatItIs")
    j.idea_line = idea.get("line") or None
    run.page.goto(f"{run.web}/p/{solution}/define/solution/q/1", wait_until="load")
    cs.leg_calibrate(j, "SOLUTION")
    cs.plan_complete(j)
    run.page.goto(f"{run.web}/p/{solution}/define/ready/interviewer", wait_until="load")
    tv.lock_once(run, leg, j, solution)
    return (run.get(f"/v2/projects/{solution}/overview") or {}).get("questionsState") == "READY"


def interview_of(run: "tv.Run", url: str) -> dict:
    token = url.rstrip("/").split("/")[-1].split("?")[0]
    stranger = run.browser.new_context()
    try:
        return stranger.request.get(f"{run.cloud}/v2/i/{token}/interview", timeout=20_000).json()
    finally:
        stranger.close()


def people(run: "tv.Run", scope: str) -> list[str]:
    return [p.person for p in tv.vs.person_inputs(run.base_entry(scope))]


# ------------------------------------------------------------------------------------------------ the wire's checks

def wire_checks(run, leg, study: str, interview: dict, view: str, url: str | None = None) -> None:
    """What the link serves, before any screen: the story up the chain, a `clipId` on every card, the gate's story
    wording (the anchor on a solution link), the idea's story on a solution link, the third-person check on money's."""
    story = interview.get("story") or {}
    leg.check(run, "the link serves the problem's story: the room, the scenes, a clip a line, the lines to read instead",
              bool(story.get("roomId")) and bool(story.get("scenes")) and len(story.get("clipIds") or []) >= 1
              and bool(story.get("readInstead")), screen="GET /v2/i/{token}/interview", view=f"{view} (wire)",
              detail={k: (story.get(k) if k != "scenes" else len(story.get(k) or [])) for k in
                      ("roomId", "scenes", "clipIds", "readInstead", "costLine", "askLine")})
    cards = ss.served_cards(interview)
    missing = [c for c in cards if not c.get("clipId")]
    leg.check(run, "every served card carries a clipId on the link's first read (Keel AI reads it aloud: keel-cloud 259 "
                   "FR-9)", bool(cards) and not missing, screen="GET /v2/i/{token}/interview (first read)",
              view=f"{view} (wire)", detail={"cards": len(cards), "without a clip": missing,
                                             "drift": "runs/DRIFT.md #104" if missing else None}, stop=False)
    if missing and url:
        # keel-cloud 259 judgement call 14: a card served with no clip yet is spoken then -- read again until it is
        deadline = time.monotonic() + 30
        while missing and time.monotonic() < deadline:
            time.sleep(2)
            interview.clear()
            interview.update(interview_of(run, url))
            missing = [c for c in ss.served_cards(interview) if not c.get("clipId")]
        leg.check(run, "every served card carries a clipId once the link has been read (CardSpeech on the first serve)",
                  not missing, screen="GET /v2/i/{token}/interview (read again)", view=f"{view} (wire)",
                  detail={"without a clip": missing})
    gate = interview.get("gate") or {}
    if study in ("problem", "solution"):
        want = STORY_GATE.format(window=window_words(tv.STORY_WINDOW))
        leg.check(run, f"the {'anchor' if study == 'solution' else 'gate'} asks *{want}*, the founder's clause under "
                       "readInstead", gate.get("question") == want, screen="the gate card", view=f"{view} (wire)",
                  detail={"question": gate.get("question"), "readInstead": story.get("readInstead")})
    if study == "money":
        leg.check(run, "the decision-maker's link serves the idea's story (keel-cloud 261 FR-3: the idea card with the "
                       "brand, then the `ideaStory`)", bool((interview.get("ideaStory") or {}).get("scenes")),
                  screen="GET /v2/i/{token}/interview", view=f"{view} (wire)",
                  detail={"ideaStory": bool(interview.get("ideaStory")), "idea brand": (interview.get("idea") or {})
                          .get("brand"), "drift": "runs/DRIFT.md #106"}, stop=False)
    if study == "solution":
        leg.check(run, "the solution link serves the idea's story and the brand on the reveal",
                  bool((interview.get("ideaStory") or {}).get("scenes")) and bool((interview.get("reveal") or {})
                                                                                 .get("brand")),
                  screen="GET /v2/i/{token}/interview", view=f"{view} (wire)",
                  detail={"ideaStory": bool(interview.get("ideaStory")), "brand": (interview.get("reveal") or {})
                          .get("brand")})
    if study == "money":
        check = interview.get("problemCheck") or {}
        leg.check(run, "the decision-maker's link serves the third-person check, introduced as what their people go "
                       "through", (check.get("question") or "").startswith("Does your ")
                  and bool(check.get("introducedAs")), screen="GET /v2/i/{token}/interview", view=f"{view} (wire)",
                  detail=check)


# ------------------------------------------------------------------------------------------------ text

def text_view(run, leg, study: str, project_id: str) -> None:
    names = people(run, "PROBLEM")
    made = tv.send_link(run, leg, f"{study}-text", project_id, "TEXT", person=names[1], decider=study == "money")
    interview = interview_of(run, made["url"])
    wire_checks(run, leg, study, interview, "text", made["url"])
    stranger = run.browser.new_context()
    try:
        walk = ss.StoryLinkText(stranger.new_page(), run.recorder).walk(made["url"], interview)
    finally:
        stranger.close()
    kinds = [s["screen"] for s in walk["screens"]]
    first_gate = "check" if study == "money" else "gate"
    order = [k for k in kinds if k in ("condition", "story", first_gate, "reveal", "ideaStory")]
    screener = (interview.get("gate") or {}).get("condition") or interview.get("condition")
    want = (["condition"] if screener else []) + ["story", "check" if study == "money" else "gate"]
    if study in ("solution", "money"):
        want += ["reveal", "ideaStory"]          # 242 FR-4 / 243 FR-2: the idea card, then the idea's story
    leg.check(run, f"the text view's order: {' -> '.join(want)}, then the questions",
              order[:len(want)] == want, screen="the link's cards", view="text", detail={"drawn": kinds},
              stop=False)
    story = next((s for s in walk["screens"] if s["screen"] == "story"), {})
    leg.check(run, "the story card: the player, *Read it instead*, the kicker *Before the questions*",
              story.get("player", 0) >= 1 and story.get("read_instead", 0) >= 1
              and story.get("kicker") == ss.STORY_KICKER, screen="the story card", view="text", detail=story)
    gate = next((s for s in walk["screens"] if s["screen"] == "gate"), {})
    chips = gate.get("story_chips") or []
    if study != "money":                       # the decision-maker's link has no gate and no story question
        leg.check(run, "the story question under the gate's Yes carries both chips (*I can't recall one particular "
                       "...*, *I'd rather not say*)", len(chips) == 2 and any("can't recall" in c for c in chips)
                  and any("rather not say" in c for c in chips), screen="the gate card (the story question)",
                  view="text", detail=gate)
    voiced = [s for s in walk["screens"] if s["screen"] in ("condition", "gate", "check", "item")]
    unvoiced = [(s["screen"], s.get("dimension"), s.get("question")) for s in voiced
                if not s["voice"] or s.get("voice_words") not in (ss.VOICE_READS, "Keel AI is muted")]
    leg.check(run, "every card the stranger answers draws the voice bar (*Keel AI reads this card aloud*, Mute)",
              bool(voiced) and not unvoiced, screen="every question card", view="text",
              detail={"cards": len(voiced), "without the bar": unvoiced}, stop=False)
    # the cards that draw option rows; a scale (count cells, the four-point scale, Hours / Amount) keeps its cells
    # and is not lettered (keel-web 244 FR-4 narrowed 241 FR-7 to the option rows; DRIFT #105 closed by that call)
    unlettered = [(s["screen"], s.get("question"), s["letters"]) for s in voiced if s.get("rows")
                  and not s.get("scale") and (s["bubbles"] < 1 or not s["letters"] or s["letters"][0] != "A")]
    leg.check(run, "the answers are the copilot strip's lettered bubbles (A, B, ...) on every option-row card",
              not unlettered, screen="every question card", view="text",
              detail={"unlettered": unlettered}, stop=False)
    leg.check(run, "the answers are sent (201) and the thank-you drawn",
              (walk.get("response") or {}).get("status") == 201, screen="the last card -> the thank-you", view="text",
              detail={"response": walk.get("response"), "done": walk.get("done")})
    # the No that ends it
    no_on = "check" if study == "money" else "gate"
    no_link = tv.send_link(run, leg, f"{study}-text-no", project_id, "TEXT", person=names[2], decider=study == "money")
    no_interview = interview_of(run, no_link["url"])
    stranger = run.browser.new_context()
    try:
        page = stranger.new_page()
        responses: list = []
        page.on("response", lambda r: responses.append({"status": r.status, "sent": r.request.post_data_json})
                if r.request.method == "POST" and r.url.split("?")[0].endswith("/interview/response") else None)
        walked = ss.StoryLinkText(page, run.recorder).walk(no_link["url"], no_interview, no_on=no_on)
        page.wait_for_timeout(1500)
    finally:
        stranger.close()
    after = [s["screen"] for s in walked["screens"]]
    sent = (responses[-1] if responses else {}).get("sent") or {}
    what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
    leg.check(run, f"a No on the {what} ends the interview: no question after it, the response a No alone",
              "item" not in after and bool(responses) and responses[-1]["status"] in (200, 201)
              and sent.get("recency") is False and not (sent.get("answers") or []),
              screen=f"the {what} card -> the exit", view="text",
              detail={"drawn": after, "responses": responses, "done": walked.get("done")})


# ------------------------------------------------------------------------------------------------ the loop

def walk_all(run: "tv.Run") -> None:
    """FR-2's nine legs, each on its study's locked project: the views not built here are said so, by name."""
    prepared: dict[str, str | None] = {}
    for study, _ in tv.STUDIES:
        project = study_project(run, study)
        for view in tv.VIEWS:
            leg_id = f"FR-2 {study} · {view}"
            if study == "money" and not tv.web_has_243(run):
                leg = run.legs[leg_id]
                leg.status = "written, not run"
                leg.why = "keel-web 243 (the decision-maker's third-person check on the three views) is not in the checkout"
                continue
            if not project:
                run.legs[leg_id].status, run.legs[leg_id].why = "skipped", f"no {study} project (its FR-1 leg failed)"
                continue
            if study != "solution" and (run.get(f"/v2/projects/{project}/overview") or {}).get("questionsState") != "READY":
                run.legs[leg_id].status = "skipped"
                run.legs[leg_id].why = f"the {study} project never locked with its questions READY (its FR-1 leg stopped first)"
                continue

            def body(leg, study=study, project=project, view=view):
                if study == "solution" and prepared.get("solution") is None:
                    prepared["solution"] = "locked" if lock_the_solution(run, leg) else "unlocked"
                if study == "solution" and prepared.get("solution") != "locked":
                    raise tv.LegFailed("the solution project never locked (its questions not READY)")
                if view == "text":
                    text_view(run, leg, study, project)
                elif view == "avatar":
                    avatar_view(run, leg, study, project)
                else:
                    copilot_view(run, leg, study, project)
            tv.timed(run, leg_id, body)


# ------------------------------------------------------------------------------------------------ avatar

#: keel-web 241 FR-8 / 242 FR-4 (`translate.ts` STORY.handOver / IDEA.handOver): the hand-over lines' openings.
HAND_OVER = {"problem": "Let me show you what ", "idea": "Let me show you how "}
#: The story the stranger tells on the story question (any words; the fake transcriber hears them as said).
STORY_SAID = "It happened last week, and it took the whole afternoon to sort out."


def interviewer_ready(run, leg, study: str, project_id: str, label: str) -> None:
    """The kind's AI interviewer set up on Keel's door (a stand-in grant: a recording is bought, keel-cloud 247) and
    READY on the stack's fake renderer; the door is left on Keel's while the AI links are made and walked."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    ledger.stand_in_keels_door(run.stack, run.account_id, f"{study}-avatar-{run.stamp}", spec=tv.STAND_IN_SPEC)
    persona = ivs.Persona(run.page, run.recorder, run.web)
    tv.open_sent(run, project_id)
    card = persona.card(label)
    if card.get("state") != "READY":
        pressed = persona.set_up(label, FACE)
        leg.check(run, f"the AI interviewer set up for the kind ({FACE.title()}), 202", pressed["status"] in (200, 202),
                  screen="Sent · the kind's card", detail={k: pressed.get(k) for k in ("status", "sent", "refusal")})
        persona.wait_card_state(label, "READY", timeout_s=180)


def avatar_walk(run, page, url: str, interview: dict, *, no_on: str | None = None) -> dict:
    """The AI link walked by voice through the seam: *Test your mic*, Start, then each window answered -- the screener
    *yes*, the gate *yes* (or the No), the story said, each item its first option said, a follow-up skipped, the pilot
    *yes* -- and each hand-over watched: the story full frame, *Go on to the question*, her return."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    p = ivs.Player(page, run.recorder)
    rows: list[dict] = []
    gate = interview.get("gate") or {}
    condition = (gate.get("condition") or interview.get("condition") or {}).get("question")
    check = (interview.get("problemCheck") or {}).get("question")
    p.open(url)
    p.mic_test()
    p.start()
    last_q = None
    said_at = 0.0
    again: dict = {}
    seconds: set = set()
    for _ in range(120):
        if page.get_by_test_id("ai-done").count():
            break
        story = page.get_by_test_id("ai-story")
        if story.count():
            row = {"screen": "handover", "kind": story.first.get_attribute("data-kind"),
                   "hand": ss._tc(story.locator(".aiv-story__hand")),
                   "player": story.locator("[data-testid=story-player], [data-testid=idea-story-player]").count(),
                   "phase": p.phase()}
            rows.append(row)
            page.get_by_test_id("ai-story-go-on").first.click()
            page.wait_for_timeout(1500)
            row["returned"] = {"phase": p.phase(), "story_gone": page.get_by_test_id("ai-story").count() == 0,
                               "face": page.get_by_test_id("ai-face").count(),
                               "video": page.locator("video.aiv-stage__video").count()}
            continue
        phase = p.phase()
        if phase == "confirming":
            page.get_by_test_id("ai-yes").first.click() if page.get_by_test_id("ai-yes").count() else p.say("yes")
            page.wait_for_timeout(1500)
            continue
        if phase != "listening" or not p.recorder()["live"]:
            page.wait_for_timeout(300)
            continue
        sheet = p.sheet()
        q = sheet["question"]
        if q == last_q:
            second = page.get_by_test_id("ai-sheet").locator(".iv-chips .chip", has_text="Nothing else")
            if second.count() and second.first.is_visible() and q not in seconds:
                # Importance's second ask (*And one more?*): one pick is a whole answer
                seconds.add(q)
                second.first.click()
            elif rows and rows[-1].get("said") and not str(rows[-1]["said"]).startswith(("tap:", "skip")) \
                    and time.monotonic() - said_at > 10 and again.get(q, 0) < 2:
                # spec 158: the same window still listening ten seconds after the answer -- the words fell between the
                # recorder's windows (seen once on the money link's check, 2026-11-22): said again, as a person would
                again[q] = again.get(q, 0) + 1
                rows[-1]["said_again"] = again[q]
                said_at = time.monotonic()
                p.say(rows[-1]["said"])
            page.wait_for_timeout(500)
            continue
        where = ss._tc(page.get_by_test_id("ai-where"))
        step = page.get_by_test_id("ai-sheet").first.get_attribute("data-step") if page.get_by_test_id("ai-sheet").count() else None
        row = {"screen": "question", "question": q, "where": where, "step": step,
               "back": page.get_by_test_id("ai-back").count(), "type_instead": page.get_by_test_id("ai-type").count(),
               "options": [re.sub(r"^[A-Z](?=[A-Z0-9])", "", o["label"]) for o in sheet["options"]],
               "bubbles": page.locator("[data-testid=ai-sheet] .aiv__bubble").count()}
        rows.append(row)
        last_q = q
        if step == "followUp" or where == ivs.FOLLOW_UP_KICKER:
            row["said"] = "skip"
            page.get_by_test_id("ai-skip").first.click()
        elif condition and q == condition:
            row["said"] = "yes"
            p.say("yes")
        elif gate and q == gate.get("question"):
            row["said"] = "no" if no_on == "gate" else "yes"
            p.say(row["said"])
        elif check and q == check:
            row["said"] = "no" if no_on == "check" else "yes"
            p.say(row["said"])
        elif step == "story" or (gate and q == gate.get("storyPrompt")):
            row["said"] = STORY_SAID
            p.say(STORY_SAID)
        elif where == ivs.LAST_QUESTION:
            row["said"] = "yes"
            p.say("yes")
        elif row["options"]:
            row["said"] = row["options"][0]
            p.say(row["said"])
        elif sheet.get("chips"):
            # a box with no rows (an amount, a count): its escape, tapped
            row["said"] = f"tap: {sheet['chips'][0]}"
            p.tap_chip()
        else:
            row["said"] = "about three"
            p.say(row["said"])
        said_at = time.monotonic()
        page.wait_for_timeout(1200)
    done = page.get_by_test_id("ai-done")
    try:
        done.first.wait_for(state="visible", timeout=60_000)
    except Exception as missed:  # noqa: BLE001 - named with what the walk met
        ss._BrowserStep(run.recorder, page, "participant").screenshot("avatar-stuck")
        raise AssertionError(json.dumps({"the AI link never reached its done screen": str(missed)[:200],
                                         "rows": rows[-6:], "where": p.where_it_stood()}, default=str)[:3000])
    return {"rows": rows, "done": ss._tc(done.first)}


def avatar_view(run, leg, study: str, project_id: str) -> None:
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    if run.remote:
        leg.status, leg.why = "skipped", "remote profile: the AI interviewer is bought on Keel's door (a stand-in here)"
        return
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == tv.vs.LINK_B2B) == (study == "money")), kinds[0])
    names = people(run, "PROBLEM")
    try:
        interviewer_ready(run, leg, study, project_id, kind.get("label"))
        made = tv.send_link(run, leg, f"{study}-avatar", project_id, "AI_INTERVIEWER", person=names[3],
                            decider=study == "money")
        no_made = tv.send_link(run, leg, f"{study}-avatar-no", project_id, "AI_INTERVIEWER", person=names[4],
                               decider=study == "money")
        interview = interview_of(run, made["url"])
        wire_checks(run, leg, study, interview, "avatar", made["url"])
        stranger = run.browser.new_context()
        try:
            stranger.add_init_script(ivs.SPEECH_SEAM)
            page = stranger.new_page()
            walked = avatar_walk(run, page, made["url"], interview)
            ss._BrowserStep(run.recorder, page, "participant").screenshot(f"avatar-{study}-done")
        finally:
            stranger.close()
        rows = walked["rows"]
        hands = [r for r in rows if r["screen"] == "handover"]
        # 242 FR-4 / 243 FR-2: twice where the link holds the idea (the problem's story, then the idea's)
        want_kinds = ["problem", "idea"] if study in ("solution", "money") else ["problem"]
        leg.check(run, f"she hands over {'twice' if len(want_kinds) == 2 else 'once'}: the story full frame in Keel AI's "
                       "voice (*Let me show you ...*), nothing recorded", [h["kind"] for h in hands] == want_kinds
                  and all(h["hand"].startswith(HAND_OVER["idea" if h["kind"] == "idea" else "problem"]) and h["player"]
                          for h in hands), screen="the hand-over card", view="avatar",
                  detail={"hand-overs": hands, "drift": "runs/DRIFT.md #106" if study == "money" else None}, stop=False)
        leg.check(run, "Daphne returns after each hand-over: the story gone, her face on the stage, the next question",
                  bool(hands) and all((h.get("returned") or {}).get("story_gone") and (h.get("returned") or {}).get("face")
                                      for h in hands), screen="the stage after the hand-over", view="avatar",
                  detail=[h.get("returned") for h in hands])
        questions = [r for r in rows if r["screen"] == "question"]
        typed = [r["question"] for r in questions if r["type_instead"]]
        leg.check(run, "no *Type instead* on any card of a story link", bool(questions) and not typed,
                  screen="every question sheet", view="avatar", detail={"with Type instead": typed})
        items = [r for r in questions if r.get("step") == "item" and not str(r.get("where") or "").startswith("Question 1 ")]
        backless = [r["question"] for r in items if not r["back"]]
        leg.check(run, "*Back to question n* on every question card after the first (the screener, the gate, its story "
                       "and the check are the link's opening)", bool(items) and not backless,
                  screen="every question sheet", view="avatar", detail={"without Back": backless,
                                                                         "rows": [(r["question"][:60], r["back"])
                                                                                  for r in questions]})
        leg.check(run, "the thank-you", bool(walked["done"]), screen="the done screen", view="avatar",
                  detail=walked["done"])
        no_interview = interview_of(run, no_made["url"])
        stranger = run.browser.new_context()
        try:
            stranger.add_init_script(ivs.SPEECH_SEAM)
            page = stranger.new_page()
            responses: list = []
            page.on("response", lambda r: responses.append({"status": r.status, "sent": r.request.post_data_json})
                    if r.request.method == "POST" and r.url.split("?")[0].endswith("/interview/response") else None)
            no_walk = avatar_walk(run, page, no_made["url"], no_interview,
                                  no_on="check" if study == "money" else "gate")
        finally:
            stranger.close()
        asked = [r["question"] for r in no_walk["rows"] if r["screen"] == "question"]
        sent = (responses[-1] if responses else {}).get("sent") or {}
        what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
        leg.check(run, f"a No on the {what} ends the interview in the avatar view: no question after it",
                  bool(responses) and sent.get("recency") is False and not (sent.get("answers") or []),
                  screen=f"the {what} -> the end", view="avatar",
                  detail={"asked": asked, "responses": responses, "done": no_walk["done"]})
    finally:
        ledger.restore_own_door(run.stack, run.account_id, f"{study}-avatar-restore-{run.stamp}", spec=tv.STAND_IN_SPEC)


# ------------------------------------------------------------------------------------------------ copilot

def copilot_walk(run, page, call: dict, *, no_on: str | None = None) -> dict:
    """The copilot card headless (spec 154's fake sources): the set-up steps by their own buttons (the Meet ticked, the
    mic opened on its step, the tab shared, the sign-in skipped, Start), then each strip by the card's own buttons --
    the screener's Yes, *Show the story* (the window grown, measured, shrunk), the gate's *Story again* (grown again)
    then Yes (or the No), each question's first answer, the idea's story where offered, the stretches stopped -- and
    End, the call's own recording sent."""
    from evals import calls_leg    # noqa: PLC0415
    card = calls_leg.Card(page, run.recorder, run.web)
    card.open(call["copilotPath"])

    def visible(testid: str):
        loc = page.locator(f"[data-testid='{testid}']")
        return loc.first if loc.count() and loc.first.is_visible() else None

    def enabled(testid: str):
        loc = visible(testid)
        return loc if loc is not None and loc.is_enabled() else None

    for _ in range(40):                                   # the set-up steps
        if card.phase() != "before":
            break
        for testid in ("start", "meet-done", "share", "skip-sign-in", "next"):
            button = enabled(testid)
            if button is not None:
                button.click()
                break
        page.wait_for_timeout(400)
    strips: list[dict] = []
    grows: list[dict] = []
    viewport = page.viewport_size or {"width": 1280, "height": 720}

    def grow(testid: str) -> None:
        page.get_by_test_id(testid).first.click()
        grown = page.get_by_test_id("copilot-grown").first
        grown.wait_for(state="visible", timeout=10_000)
        box = grown.bounding_box() or {}
        row = {"press": testid, "kind": grown.get_attribute("data-kind"), "box": box, "viewport": viewport,
               "card_shown": page.locator(calls_leg.COPILOT_CARD).first.is_visible(),
               "card_grown": page.locator(calls_leg.COPILOT_CARD).first.get_attribute("data-grown") is not None,
               "player": grown.get_by_test_id("copilot-story-player").count()}
        page.get_by_test_id("copilot-shrink").first.click()
        page.get_by_test_id("copilot-grown").first.wait_for(state="detached", timeout=10_000)
        page.wait_for_timeout(300)
        row["after"] = {"phase": card.phase(), "head": ss._tc(page.locator("[data-testid=head]")),
                        "story_again": page.get_by_test_id("story-again").count()}
        grows.append(row)

    last = None
    for _ in range(120):
        phase = card.phase()
        if phase in ("sending", "done", "failed", "sent"):
            break
        if page.get_by_test_id("copilot-grown").count():
            page.get_by_test_id("copilot-shrink").first.click()
            page.wait_for_timeout(300)
            continue
        if phase in ("story", "follow-up"):
            strips.append({"phase": phase, "head": ss._tc(page.locator("[data-testid=head]")),
                           "still": page.get_by_test_id("copilot-still").count()})
            if enabled("stop") is not None:
                enabled("stop").click()
            elif enabled("next") is not None:
                enabled("next").click()
            page.wait_for_timeout(400)
            continue
        if phase not in ("reading", "second-step"):
            # the closing stretches, the screened ask, the end: End where it is offered, else on
            for testid in ("finish", "end", "stop", "next"):
                if enabled(testid) is not None:
                    strips.append({"phase": phase, "head": ss._tc(page.locator("[data-testid=head]")), "pressed": testid})
                    enabled(testid).click()
                    break
            page.wait_for_timeout(500)
            continue
        read = ss._tc(page.locator("[data-testid=read]"))
        head = ss._tc(page.locator("[data-testid=head]"))
        strip = {"phase": phase, "head": head, "read": read[:120],
                 "still": page.get_by_test_id("copilot-still").count(),
                 "show_story": page.get_by_test_id("show-story").count(),
                 "story_again": page.get_by_test_id("story-again").count(),
                 "idea_story": page.get_by_test_id("show-idea-story").count(),
                 "screener": page.locator(calls_leg.COPILOT_CARD).first.get_attribute("data-screener"),
                 "question": page.locator(calls_leg.COPILOT_CARD).first.get_attribute("data-question")}
        if (read, head) != last:
            strips.append(strip)
            last = (read, head)
        if strip["story_again"] and not any(g["press"] == "story-again" for g in grows):
            grow("story-again")
            continue
        if strip["idea_story"] and not any(g["press"] == "show-idea-story" for g in grows):
            grow("show-idea-story")
            continue
        gate_strip = bool(strip["story_again"])
        if gate_strip and no_on == "gate" and enabled("opt-2") is not None:
            enabled("opt-2").click()
            page.wait_for_timeout(600)
            continue
        answers = page.locator("[data-testid=as-the-interview], [data-testid=as-the-condition]")
        if enabled("opt-1") is not None:
            enabled("opt-1").click()
        elif answers.locator("label.cpl-bubble").count():
            bubbles = answers.locator("label.cpl-bubble")
            bubbles.nth(1 if (no_on == "check" and "have this problem" in read) else 0).click()
        elif answers.get_by_role("radio").count():
            answers.get_by_role("radio").first.click()
        elif answers.locator("input[type=number], input[type=text], input:not([type])").count():
            answers.locator("input[type=number], input[type=text], input:not([type])").first.fill("3")
        elif answers.locator(".iv-chips button").count():
            answers.locator(".iv-chips button").first.click()
        page.wait_for_timeout(300)
        nothing = answers.locator(".iv-chips button", has_text="Nothing else")
        if nothing.count() and nothing.first.is_visible() and enabled("next") is None:
            nothing.first.click()
        page.wait_for_timeout(500)
        if visible("show-story") is not None and not any(g["press"] == "show-story" for g in grows):
            grow("show-story")
            continue
        if enabled("next") is not None:
            enabled("next").click()
        page.wait_for_timeout(400)
    end_phase = card.phase()
    try:
        card.wait_phase("done", "sent", "failed", timeout_s=60)
    except Exception:  # noqa: BLE001 - recorded: the phase the card stood in
        pass
    return {"strips": strips, "grows": grows, "end_phase": end_phase, "phase": card.phase()}


def first_person(run, leg, project_id: str) -> None:
    """keel-cloud 248 FR-7b: a call on a study that holds the idea waits on the FIRST_PERSON line, a job on Keel's AI
    alone -- off on this stack on either door -- so the card would draw only *Keel is writing the first-person lines*.
    Locally the line is written as the job would (spec 154's stand-in, `stack/ledger.stand_in_first_person`); on the
    remote profile the twin writes it."""
    if run.remote:
        return
    from evals import calls_leg    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    idea = ledger.idea_lines(run.stack, project_id)
    if idea and not idea.get("beliefFirstPerson") and idea.get("belief"):
        stored = ledger.stand_in_first_person(run.stack, project_id, calls_leg.first_person_line(idea["belief"]))
        leg.notes.append(f"STAND-IN (spec 154's): the first-person line written as keel-cloud 248's job would: {stored!r}")


def copilot_view(run, leg, study: str, project_id: str) -> None:
    from evals import calls_leg    # noqa: PLC0415
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == tv.vs.LINK_B2B) == (study == "money")), kinds[0])
    names = people(run, "PROBLEM")
    results = {}
    first_person(run, leg, project_id)
    for which, person, no_on in (("yes", names[5], None), ("no", names[6], "check" if study == "money" else "gate")):
        status, call = run.call("POST", f"/v2/projects/{project_id}/calls", {"roleId": kind.get("roleId"),
                                                                             "name": person})
        leg.check(run, f"a call planned with {person} (POST calls 201, the copilot's path)",
                  status == 201 and bool((call or {}).get("copilotPath")), screen="Sent · Calls with me",
                  view="copilot", detail=call)
        page = run.context.new_page()
        try:
            page.add_init_script(calls_leg.FAKE_MEDIA)
            page.add_init_script(calls_leg.UPLOAD_SEAM)
            results[which] = copilot_walk(run, page, call, no_on=no_on)
            ss._BrowserStep(run.recorder, page, "founder").screenshot(f"copilot-{study}-{which}")
        finally:
            page.close()
    walked = results["yes"]
    grows = walked["grows"]
    presses = [g["press"] for g in grows]
    # keel-web 241 FR-9 / 242 FR-4 / 243 judgement call 12: the screener's *Show the story* then the gate's *Story
    # again*; the decision-maker's call has no screener, its check strip carries the story's press (`story-again`); the
    # idea's story after the idea where the study holds one
    want = (["story-again"] if study == "money" else ["show-story", "story-again"]) + \
        (["show-idea-story"] if study in ("solution", "money") else [])
    leg.check(run, f"the story moments in order: {', '.join(want)}", presses == want, screen="the strips",
              view="copilot", detail={"grows": presses, "strips": [(s.get("head"), s.get("read", "")[:50])
                                                                  for s in walked["strips"]]})
    vp = (grows[0]["viewport"] if grows else {"width": 1280, "height": 720})
    half = vp["width"] * vp["height"] / 2
    small = [g for g in grows if (g["box"].get("width") or 0) * (g["box"].get("height") or 0) >= half]
    leg.check(run, "the grown window is under half the viewport, the card still drawn, the player playing",
              bool(grows) and not small and all(g["card_shown"] and g["player"] for g in grows),
              screen="the grown window", view="copilot", detail=grows)
    back = grows[:1]
    leg.check(run, "it shrinks back with the gate (or the check) up (*Story again* on its strip)",
              bool(back) and all(g["after"]["story_again"] for g in back), screen="the gate's strip",
              view="copilot", detail=[g["after"] for g in grows])
    # 241 judgement call 13: the stills are the problem's (a solution or money question has none): every strip of the
    # problem's -- the screener, the gate or check, and on a problem link each question
    problem_strips = [s for s in walked["strips"] if s.get("phase") == "reading" and (
        s.get("story_again") or s.get("show_story") or (study == "problem" and s.get("question")))]
    stills = [s for s in problem_strips if not s.get("still")]
    leg.check(run, "every question strip carries the step's still beside the question", not stills,
              screen="the strips", view="copilot", detail={"without a still": [(s["head"], s["read"][:60])
                                                                              for s in stills]}, stop=False)
    leg.check(run, "the call ends and its recording is sent (the card done)", walked["phase"] in ("done", "sent"),
              screen="End -> the upload", view="copilot", detail={"phase": walked["phase"], "end": walked["end_phase"]})
    no = results["no"]
    gate_at = next((i for i, s in enumerate(no["strips"]) if s.get("story_again")), None)
    asked_after = [s for s in (no["strips"][gate_at + 1:] if gate_at is not None else no["strips"])
                   if s.get("phase") == "reading" and not s.get("story_again")]
    leg.check(run, "a No on the gate in the copilot view ends the questions (no item strip after it)",
              not asked_after,
              screen="the gate's strip -> the end", view="copilot", stop=False,
              detail={"end": no["end_phase"], "after": [(s["head"], s["read"][:60]) for s in asked_after]})
