"""Spec 157 FR-2: **the stranger's legs, three views each** -- each locked project's link (the problem of FR-1 (d), the
solution of FR-1 (b), the money of FR-1 (c)) walked in three views, with a No on the gate, the anchor and the
decision-maker's third-person check ending the interview in every view. Since spec 159 the three views are the orb,
the AI avatar and the copilot (keel-cloud 267, contract 84; keel-web 253 / 254: one player, the orb in the face's
place, the film first, speak or tap, nothing typed):

* **orb** (159 FR-1, FR-3, FR-4; it was 157's text view): a TEXT link made on New link's *Keel's voice* (the default,
  two rows), served `interviewer.speaker` ORB -- the AI intro with the orb, the mic test, Start, the film first, the
  orb's opening at `/v2/clips/`, the condition, the gate, the items; the orb's states logged through every answer
  (`story_screens.ORB_INTERVIEW_WATCH`); one item answered by its letter, one by its words, one by tap; the story's chip
  said aloud on one link; no typed box on any screen.
* **avatar** (241 FR-8, 242 FR-4; 159 FR-2): the AI link through the stack's fake renderer and the seam's recorder --
  the face, the film first, Daphne's return, *Back to question n* on every question, the idea's hand-over; the two
  links' opening (and one item) the same words, read off the stack's `speech_clip` row and the recording's script.
  Before the face is set up the kind card's *Try it yourself* opens the dry run on the orb (159 FR-4).

Spec 160 (keel-web 256, the player pared down; the founder: "test for both the interviewers and ensure that it is in
sync"): the intro's one button and its block (FR-1, FR-2: the microphone refused ends at `ai-mic-block`, allowed again
-> *Start the interview*, one link a study on each speaker); the orb's voice link and the face's link walked alike --
the same ways, the film's controls, the replay mark on the first item -- and held equal step for step (FR-3,
`story_screens.walk_steps` / `same_walk`); the film's two icons, its board and *Begin the interview* (FR-4); the replay
mark (FR-5); the last page's tick (FR-6). The taps-only walk of 159 FR-3 is gone with the refused path.
* **copilot** (241 FR-9, 242 FR-4; untouched by 159): a call planned on the project, the card opened headless on the
  fake sources (spec 154's way), the strips in order, *Show the story* / *Story again* growing the window (under half
  the viewport, the card still drawn) and its return, the recorded answer uploaded at End.

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




def person_at(names: list[str], i: int) -> str:
    """The `i`-th corpus person of the base entry, or (past the last) a numbered one -- every link a person of its own."""
    return names[i] if i < len(names) else f"{names[i % len(names)]} {i}"


# ------------------------------------------------------------------------------------------------ the wire's checks

#: keel-cloud 267 FR-2: the orb's clips are Keel AI's public route; the face's the link's own.
ORB_CLIP_ROUTE = "/v2/clips/"
AVATAR_CLIP_ROUTE = "/interview/clips/"
#: keel-cloud 267 judgement call 7: the fake voice's clip (`FakeSpeech`, 300 ms of silence) reads 0.312 s.
FAKE_CLIP_SECONDS = 0.312


def read_served(run, url: str, *, timeout_s: float = 60) -> tuple[dict, int]:
    """The link's interview as a stranger reads it, read again until `interviewer` is served (keel-cloud 267 judgement
    call 6: a passage still unspoken is spoken on the read; before the questions are final none is served). Returns the
    interview and how many reads it took."""
    interview = interview_of(run, url)
    reads = 1
    deadline = time.monotonic() + timeout_s
    while not interview.get("interviewer") and time.monotonic() < deadline:
        time.sleep(2)
        interview = interview_of(run, url)
        reads += 1
    return interview, reads


def absolute(run, url: str | None) -> str:
    return url if not url or url.startswith("http") else f"{run.cloud}{url}"


def wire_checks(run, leg, study: str, interview: dict, view: str, *, speaker: str, reads: int = 1) -> None:
    """What the link serves, before any screen (contract 84): the story up the chain; the interviewer and who speaks --
    the orb's clips on Keel AI's route with no face, or the face's on the link's own; `clips.problem` null where the film
    is served; no `clipId` on any card; the gate's story wording (the anchor on a solution link), the idea's story on a
    solution link, the third-person check on money's."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    w = f"{view} (wire)"
    story = interview.get("story") or {}
    leg.check(run, "the link serves the problem's story: the room, the scenes, a clip a line, the lines to read instead",
              bool(story.get("roomId")) and bool(story.get("scenes")) and len(story.get("clipIds") or []) >= 1
              and bool(story.get("readInstead")), screen="GET /v2/i/{token}/interview", view=w,
              detail={k: (story.get(k) if k != "scenes" else len(story.get(k) or [])) for k in
                      ("roomId", "scenes", "clipIds", "readInstead", "costLine", "askLine")})
    player = interview.get("interviewer") or {}
    leg.check(run, f"the link serves `interviewer` with `speaker` {speaker} (keel-cloud 267 FR-2)",
              player.get("speaker") == speaker, screen="GET /v2/i/{token}/interview", view=w,
              detail={"speaker": player.get("speaker"), "served": bool(player), "reads": reads,
                      "formats": interview.get("formats")})
    refs = ss.clip_refs(player)
    if speaker == ivs.SPEAKER_ORB:
        leg.check(run, "the orb: no face (`face` null), the link served [TEXT]",
                  player.get("face") is None and interview.get("formats") == ["TEXT"],
                  screen="GET /v2/i/{token}/interview", view=w,
                  detail={"face": player.get("face"), "formats": interview.get("formats")})
        off = [(where, r.get("url")) for where, r in refs if ORB_CLIP_ROUTE not in str(r.get("url") or "")
               or AVATAR_CLIP_ROUTE in str(r.get("url") or "")]
        leg.check(run, "every one of the orb's clips is Keel AI's, on `/v2/clips/{id}` (the opening first among them)",
                  bool(refs) and not off and ORB_CLIP_ROUTE in str(((player.get("clips") or {}).get("opening") or {})
                                                                     .get("url") or ""),
                  screen="GET /v2/i/{token}/interview", view=w,
                  detail={"clips": len(refs), "off the route": off[:6],
                          "opening": (player.get("clips") or {}).get("opening")})
        seconds = sorted({round(float(r.get("seconds") or 0), 3) for _, r in refs})
        leg.check(run, f"every orb clip is FakeSpeech's ({FAKE_CLIP_SECONDS} s of silence: nothing bought)",
                  seconds == [FAKE_CLIP_SECONDS], screen="GET /v2/i/{token}/interview", view=w,
                  detail={"seconds": seconds}, stop=False)
    else:
        leg.check(run, f"the face: {FACE.title()} on a link served AI_INTERVIEWER",
                  (player.get("face") or {}).get("code") == FACE and "AI_INTERVIEWER" in (interview.get("formats") or []),
                  screen="GET /v2/i/{token}/interview", view=w,
                  detail={"face": player.get("face"), "formats": interview.get("formats")})
        off = [(where, r.get("url")) for where, r in refs if AVATAR_CLIP_ROUTE not in str(r.get("url") or "")]
        leg.check(run, "every one of the face's clips is the link's own (`/v2/i/{token}/interview/clips/{id}`)",
                  bool(refs) and not off, screen="GET /v2/i/{token}/interview", view=w,
                  detail={"clips": len(refs), "off the route": off[:6]})
    leg.check(run, "the film is the problem: `clips.problem` null where the story is served (keel-cloud 267 FR-3)",
              bool(story) and (player.get("clips") or {}).get("problem") is None,
              screen="GET /v2/i/{token}/interview", view=w,
              detail={"problem": (player.get("clips") or {}).get("problem")})
    carrying = ss.cards_carrying_a_clip(interview)
    leg.check(run, "no served card carries a `clipId` (keel-cloud 267 FR-4: the card speech retired)", not carrying,
              screen="GET /v2/i/{token}/interview", view=w, detail={"carrying": carrying})
    gate = interview.get("gate") or {}
    if study in ("problem", "solution"):
        want = STORY_GATE.format(window=window_words(tv.STORY_WINDOW))
        leg.check(run, f"the {'anchor' if study == 'solution' else 'gate'} asks *{want}*, the founder's clause under "
                       "readInstead", gate.get("question") == want, screen="the gate card", view=w,
                  detail={"question": gate.get("question"), "readInstead": story.get("readInstead")})
    if study == "money":
        leg.check(run, "the decision-maker's link serves the idea's story (keel-cloud 261 FR-3: the idea card with the "
                       "brand, then the `ideaStory`)", bool((interview.get("ideaStory") or {}).get("scenes")),
                  screen="GET /v2/i/{token}/interview", view=w,
                  detail={"ideaStory": bool(interview.get("ideaStory")), "idea brand": (interview.get("idea") or {})
                          .get("brand"), "drift": "runs/DRIFT.md #106"}, stop=False)
        check = interview.get("problemCheck") or {}
        leg.check(run, "the decision-maker's link serves the third-person check, introduced as what their people go "
                       "through", (check.get("question") or "").startswith("Does your ")
                  and bool(check.get("introducedAs")), screen="GET /v2/i/{token}/interview", view=w,
                  detail=check)
    if study == "solution":
        leg.check(run, "the solution link serves the idea's story and the brand on the reveal",
                  bool((interview.get("ideaStory") or {}).get("scenes")) and bool((interview.get("reveal") or {})
                                                                                 .get("brand")),
                  screen="GET /v2/i/{token}/interview", view=w,
                  detail={"ideaStory": bool(interview.get("ideaStory")), "brand": (interview.get("reveal") or {})
                          .get("brand")})


def popup_checks(run, leg, made: dict) -> None:
    """Spec 159 FR-4 (keel-web 253 FR-4): New link offers *Keel's voice* (preselected) and the AI interviewer -- two
    rows, no *Let them choose*, no *Read and tap*."""
    from harness import interviews_screens as iv    # noqa: PLC0415
    rows = {k: v for k, v in (made.get("formats") or {}).items() if k != "_on_card"}
    names = list(rows)
    leg.check(run, f"New link offers *{iv.KEELS_VOICE}* (preselected) and *AI interviewer*: two rows, no "
                   f"*{iv.CHOICE_NAME}*, no *{iv.READ_AND_TAP}*",
              len(names) == 2 and names[0] == iv.KEELS_VOICE and names[1].startswith("AI interviewer")
              and bool(rows[names[0]].get("checked")), screen="Sent · New link (the format rows)", view="founder",
              detail={"rows": rows})


def fetch_clip(run, url: str | None) -> dict:
    """A clip fetched as the stranger's browser would (no cookie): status, type, bytes."""
    stranger = run.browser.new_context()
    try:
        r = stranger.request.get(absolute(run, url), timeout=20_000)
        return {"status": r.status, "type": (r.headers or {}).get("content-type"), "bytes": len(r.body() or b"")}
    except Exception as broke:  # noqa: BLE001 - recorded
        return {"error": repr(broke)[:200]}
    finally:
        stranger.close()


# ------------------------------------------------------------------------------------------------ the walk

#: The story the stranger tells on the story question (any words; the fake transcriber hears them as said).
STORY_SAID = "It happened last week, and it took the whole afternoon to sort out."
#: keel-web 241 FR-8 / 242 FR-4 (`translate.ts` STORY.handOver / IDEA.handOver): the hand-over lines' openings. Spec
#: 159 (keel-web 253 FR-3): the problem's film plays first with no hand-over line; the idea's keeps its line.
HAND_OVER = {"problem": "Let me show you what ", "idea": "Let me show you how "}
#: keel-web's one-pick controls (`PICK_CONTROLS` less the price ladder's two steps): where a letter, words or a tap
#: picks one row and the hold goes on by itself.
ONE_PICK = ("single_choice", "single_choice_5", "fixed_four", "fixed_three", "scale_four", "duration_bands")
#: Spec 159 FR-3: the three ways an item is answered on the orb link, in order -- the second row by its letter, the
#: first row by its words, the first row by tap.
SPEAK_OR_TAP = ("letter", "words", "tap")
LETTER = "B"


def _norm(text) -> str:
    return " ".join(str(text or "").split()).strip().lower()


def item_of(items: list[dict], question: str) -> dict:
    """The served item a sheet's question is (its text inside the question, or the question inside its text)."""
    q = _norm(question)
    for item in items:
        text = _norm(item.get("text") or item.get("question"))
        if text and q and (text in q or q in text):
            return item
    return {}


def _option_index(options: list[str], word: str, fallback: int) -> int:
    """The row whose words start with `word` (Yes / No, the letter badge dropped), else `fallback`."""
    for i, label in enumerate(options):
        if _norm(label).startswith(word.lower()):
            return i
    return fallback


def way_for(ways: list[str], control: str | None) -> str | None:
    """Spec 159 FR-3: which of the ways still owed answers an item of `control` -- the letter and the tap only on a
    one-pick item (the hold goes on by itself and the tapped row stands lit; a tap on *pick one, then one more* moves
    straight to its second ask, run 2), the words on any item with rows but the price ladder (its second step)."""
    if "letter" in ways and control in ONE_PICK:
        return "letter"
    if "words" in ways and control not in ("price_ladder", None):
        return "words"
    if "tap" in ways and control in ONE_PICK:
        return "tap"
    return None


def _lit_after(p, before_q: str, *, timeout_s: float = 12) -> dict:
    """What the sheet lit after an answer: polled until a row is ticked, the question changed or the time ran out."""
    deadline = time.monotonic() + timeout_s
    seen: list = []
    while time.monotonic() < deadline:
        drawn = p._drawn()
        if drawn["lit"]:
            seen = list(drawn["lit"])
            break
        if p.question() != before_q:
            break
        p.page.wait_for_timeout(100)
    return {"lit": seen, "status": p.status(), "went_on": p.question() != before_q}


def link_walk(run, page, url: str, interview: dict, *, no_on: str | None = None, story: str = "said",
              speak_or_tap: list | None = None, film_checks: bool = False, replay: bool = False) -> dict:
    """The AI player on a link -- the orb or the face -- walked through the seam: the intro (its mic test), Start, the
    film watched to its end and *Begin the interview* pressed (spec 160 FR-4: `film_checks` also pauses, resumes,
    starts it over and taps the board for its words first), the idea's story let play to its end, and each window
    answered -- the screener *yes*, the gate *yes* (or the No), the story (`story`: `said` -- a story told, `chip-voice`
    -- *I can't recall one particular ...* said, `chip-tap` -- that chip tapped), each item its first option said (or,
    `speak_or_tap`, the ways still owed -- the letter on a one-pick item, the words, the tap -- each taken off the list
    as an item takes it, so a second link walks what the first had no item for), a follow-up skipped, the pilot *yes*.
    `replay` (spec 160 FR-5): on the first item the replay mark is pressed before the answer. Every response the page
    posted is kept; the last page read once *Microphone off* is drawn (FR-6)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    p = ivs.Player(page, run.recorder)
    responses: list = []
    page.on("response", lambda r: responses.append({"status": r.status, "sent": r.request.post_data_json})
            if r.request.method == "POST" and r.url.split("?")[0].endswith("/interview/response") else None)
    rows: list[dict] = []
    gate = interview.get("gate") or {}
    condition = (gate.get("condition") or interview.get("condition") or {}).get("question")
    check = (interview.get("problemCheck") or {}).get("question")
    items = ss.served_items(interview)
    p.open(url)
    intro = p.intro()
    mic = p.mic_test()
    p.start()
    last_q = None
    said_at = 0.0
    again: dict = {}
    seconds: set = set()
    replayed: dict = {}
    # The ways owed (spec 159 FR-3); a way no item is left for on this study's links is carried to the next study.
    ways = speak_or_tap if speak_or_tap is not None else []

    def answer_row(index: int, how: str, row: dict) -> None:
        """One option row by `how` -- said by its words, said by its letter, or tapped."""
        sheet = p.sheet()
        labels = [o["label"] for o in sheet["options"]]
        if how == "tap":
            row["said"] = f"tap: {row['options'][index]}"
            page.get_by_test_id("ai-sheet").locator("[data-testid=ai-options] .opt").nth(index).click()
        elif how == "letter":
            row["said"] = LETTER
            p.say(LETTER)
        else:
            row["said"] = row["options"][index]
            p.say(row["said"])
        row["want_lit"] = labels[index] if index < len(labels) else None

    for _ in range(160):
        if page.get_by_test_id("ai-done").count() or page.get_by_test_id("ai-ended").count():
            break
        film = page.get_by_test_id("ai-story")
        if film.count():
            rows.append(watch_film(run, p, page, interview, checks=film_checks))
            continue
        phase = p.phase()
        if phase == "confirming":
            if page.get_by_test_id("ai-yes").count():
                page.get_by_test_id("ai-yes").first.click()
            else:
                p.say("yes")
            page.wait_for_timeout(1500)
            continue
        # spec 160 FR-2: a refused microphone never starts (`blocked_walk`), so every window here records
        if phase != "listening" or not p.recorder()["live"]:
            page.wait_for_timeout(300)
            continue
        sheet = p.sheet()
        q = sheet["question"]
        if q == last_q:
            nothing = page.get_by_test_id("ai-sheet").locator(".iv-chips .chip", has_text="Nothing else")
            save = page.get_by_test_id("ai-save")
            if nothing.count() and nothing.first.is_visible() and q not in seconds:
                # Importance's second ask (*And one more?*): one pick is a whole answer
                seconds.add(q)
                nothing.first.click()
            elif str((rows[-1] if rows else {}).get("said") or "").startswith("tap:") and save.count() \
                    and save.first.is_visible() and save.first.is_enabled():
                save.first.click()                               # a tapped multi-pick finishes on Save and next
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
        options = [re.sub(r"^[A-Z](?=[A-Z0-9])", "", o["label"]) for o in sheet["options"]]
        row = {"screen": "question", "question": q, "where": where, "step": step,
               "back": page.get_by_test_id("ai-back").count(), "type_instead": page.get_by_test_id("ai-type").count(),
               "options": options, "chips": sheet.get("chips") or [], "banner": sheet.get("banner"),
               "bubbles": page.locator("[data-testid=ai-sheet] .aiv__bubble").count(),
               "speaker": p.speaker(), "typed": p.typed_boxes()}
        rows.append(row)
        last_q = q
        if replay and not replayed and step == "item":
            # spec 160 FR-5: the replay mark on the first item -- the clip again, the window open again -- then the answer
            replayed = press_replay(p, page, interview, q)
            row["replay"] = replayed

        def yes_no(word: str) -> None:
            row["said"] = word
            p.say(word)

        if step == "followUp" or where == ivs.FOLLOW_UP_KICKER:
            row["said"] = "skip"
            page.get_by_test_id("ai-skip").first.click()
        elif condition and q == condition:
            yes_no("yes")
        elif gate and q == gate.get("question"):
            yes_no("no" if no_on == "gate" else "yes")
        elif check and q == check:
            yes_no("no" if no_on == "check" else "yes")
        elif step == "story" or (gate and q == gate.get("storyPrompt")):
            how = story
            row["story"] = how
            if how == "chip-tap" and row["chips"]:
                row["said"] = f"tap: {row['chips'][0]}"
                p.tap_chip()
            elif how == "chip-voice" and row["chips"]:
                row["said"] = row["chips"][0]
                p.say(row["said"])
            else:
                row["said"] = STORY_SAID
                p.say(STORY_SAID)
        elif where == ivs.LAST_QUESTION:
            yes_no("yes")
        elif options:
            item = item_of(items, q)
            row["control"] = item.get("control")
            if len(options) >= 2 and way_for(ways, item.get("control")):
                # the letter and the tap on one-pick items, the words on any item with rows (`way_for`)
                how = way_for(ways, item.get("control"))
                ways.remove(how)
                row["fr3"] = how
                answer_row(1 if how == "letter" else 0, how, row)
                row["read"] = _lit_after(p, q)
            else:
                row["said"] = options[0]
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
    done = page.locator("[data-testid=ai-done], [data-testid=ai-ended]")
    try:
        done.first.wait_for(state="visible", timeout=60_000)
    except Exception as missed:  # noqa: BLE001 - named with what the walk met
        ss._BrowserStep(run.recorder, page, "participant").screenshot("link-walk-stuck")
        raise AssertionError(json.dumps({"the link never reached its end": str(missed)[:200],
                                         "rows": rows[-6:], "where": p.where_it_stood()}, default=str)[:3000])
    try:                                                  # keel-web 075 FR-4: *Microphone off* once all is let go
        page.get_by_test_id("ai-mic-off").first.wait_for(state="attached", timeout=8_000)
    except Exception:  # noqa: BLE001 - read below as missing
        pass
    page.wait_for_timeout(500)
    return {"rows": rows, "done": ss._tc(done.first), "last_page": last_page(page), "intro": intro, "mic": mic,
            "responses": responses, "log": ss.iv_log(page), "plays": ss.iv_plays(page), "replay": replayed}


# ------------------------------------------------------------------------------------------------ spec 160 machinery

def opening_clip(interview: dict) -> str | None:
    """The opening's clip id as served (`interviewer.clips.opening.clipId`)."""
    return (((interview.get("interviewer") or {}).get("clips") or {}).get("opening") or {}).get("clipId")


def item_clip(interview: dict, question: str) -> str | None:
    """The clip id of the served item a sheet's question is (`interviewer.items[itemId].clip.clipId`)."""
    item = item_of(ss.served_items(interview), question)
    entry = ((interview.get("interviewer") or {}).get("items") or {}).get(item.get("itemId")) or {}
    return (entry.get("clip") or {}).get("clipId")


def _plays_after(page, since_ms: float) -> list:
    return [x for x in ss.iv_plays(page) if float(x[0]) >= since_ms]


def film_controls(p, page, *, timeout_s: float = 60) -> dict:
    """Spec 160 FR-4 (keel-web 256 FR-3): on the film while it plays -- read first (nothing above the board, the two
    icons), then once three strokes are on the board: pause (the icon flips, the drawing holds for 1.5 s), resume, start
    over (the board drawn from the start again), and the board tapped (the lines under it) and tapped again (gone)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    out: dict = {"first": p.film(), "speaker": p.speaker_box()}
    deadline = time.monotonic() + timeout_s
    f = out["first"]
    while time.monotonic() < deadline:
        f = p.film()
        if not f.get("drawn") or f.get("begin") or ((f.get("sig") or {}).get("on") or 0) >= 3:
            break
        page.wait_for_timeout(150)
    out["playing"] = f
    if not f.get("drawn") or f.get("begin"):
        out["missed"] = "the film ended (or went) before three strokes were drawn"
        return out
    page.get_by_test_id(ivs.FILM_PAUSE).first.click()
    page.wait_for_timeout(300)
    held = p.film()
    page.wait_for_timeout(1500)
    out["paused"] = {"at": held, "later": p.film()}
    page.get_by_test_id(ivs.FILM_PAUSE).first.click()
    page.wait_for_timeout(1500)
    out["resumed"] = p.film()
    before = p.film()
    page.get_by_test_id(ivs.FILM_AGAIN).first.click()
    page.wait_for_timeout(150)
    out["again"] = {"before": before, "after": p.film()}
    page.get_by_test_id(ivs.FILM_BOARD).first.click()
    page.wait_for_timeout(250)
    out["shown"] = p.film()
    page.get_by_test_id(ivs.FILM_BOARD).first.click()
    page.wait_for_timeout(250)
    out["hidden"] = p.film()
    return out


def watch_film(run, p, page, interview: dict, *, checks: bool = False, timeout_s: float = 240) -> dict:
    """The film on the stage, watched to its end. The problem's film (keel-web 256 FR-3) ends on *Begin the interview*
    (`ai-film-begin`): held 2 s with nothing pressed (`at_end`: nothing played, the phase still the film, no speaker
    seen), then pressed (`after`: the first clip played after the press, the speaker seen and its size). The idea's
    story goes on by itself at its end. `checks`: `film_controls` first (FR-4)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    film = page.get_by_test_id("ai-story").first
    kind = film.get_attribute("data-kind")
    row = {"screen": "film", "kind": kind, "first": film.get_attribute("data-first") is not None,
           "hand": ss._tc(film.locator(".aiv-story__hand")),
           "player": film.locator("[data-testid=story-player], [data-testid=idea-story-player]").count(),
           "phase": p.phase(), "speaker": p.speaker(), "read": p.film()}
    limit = timeout_s * 1000 * p.patience
    if kind == "idea":
        try:
            page.locator("[data-testid=ai-story][data-kind=idea]").first.wait_for(state="detached", timeout=limit)
        except Exception as missed:  # noqa: BLE001 - recorded
            row["stuck"] = str(missed)[:200]
        row["returned"] = returned(p, page)
        return row
    if checks:
        row["controls"] = film_controls(p, page)
    begin = page.get_by_test_id(ivs.FILM_BEGIN)
    try:
        begin.first.wait_for(state="visible", timeout=limit)
    except Exception as missed:  # noqa: BLE001 - recorded; the walk goes on where it can
        row["stuck"] = str(missed)[:200]
        row["returned"] = returned(p, page)
        return row
    shown_at = p.now_ms()
    page.wait_for_timeout(2000)
    row["at_end"] = {"film": p.film(), "phase": p.phase(), "plays": _plays_after(page, shown_at),
                     "speaker": p.speaker_box(), "words": page.get_by_test_id(ivs.WORDS).count(),
                     "begin": ss._tc(begin)}
    pressed_at = p.now_ms()
    begin.first.click()
    try:
        page.get_by_test_id("ai-story").first.wait_for(state="detached", timeout=10_000)
        p.wait_phase("speaking", "listening", "beat", timeout_s=15)
    except Exception as missed:  # noqa: BLE001 - recorded
        row["stuck"] = str(missed)[:200]
    page.wait_for_timeout(200)
    row["after"] = {"plays": _plays_after(page, pressed_at)[:4], "phase": p.phase(), "speaker": p.speaker_box(),
                    "opening": opening_clip(interview)}
    row["returned"] = returned(p, page)
    return row


def returned(p, page) -> dict:
    """What the stage drew once the film was gone."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    return {"phase": p.phase(), "story_gone": page.get_by_test_id("ai-story").count() == 0,
            "face": page.get_by_test_id("ai-face").count(), "orb": page.get_by_test_id(ivs.STAGE_ORB).count(),
            "video": page.locator("video.aiv-stage__video").count()}


def press_replay(p, page, interview: dict, question: str, *, timeout_s: float = 20) -> dict:
    """Spec 160 FR-5 (keel-web 256 FR-4): the replay mark (`ai-replay`, *Hear the question again*) pressed on a question
    whose window is open: the item's clip plays again (`plays`, by `data-clip`), the stage speaks, and the window opens
    again (a recording begun after the press, the phase listening)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    mark = page.get_by_test_id(ivs.REPLAY)
    out = {"question": question, "clip": item_clip(interview, question), "drawn": mark.count(),
           "label": mark.first.get_attribute("aria-label") if mark.count() else None,
           "again_drawn": page.get_by_test_id(ivs.AGAIN_RETIRED).count()}
    if not mark.count():
        return out
    made = p.recorder()["count"]
    pressed_at = p.now_ms()
    mark.first.click()
    try:
        p.wait_listening(newer_than=made, timeout_s=timeout_s)
        p.wait_phase("listening", timeout_s=timeout_s)
        out["reopened"] = True
    except Exception as missed:  # noqa: BLE001 - recorded
        out["reopened"] = False
        out["stuck"] = str(missed)[:200]
    out["plays"] = _plays_after(page, pressed_at)[:4]
    out["phase"] = p.phase()
    return out


def last_page(page) -> dict:
    """Spec 160 FR-6 (keel-web 256 FR-7): the last page as drawn -- the tick (`ai-done-tick`) and whether the title
    follows it, the title, the words."""
    return page.evaluate(r"""() => {
        const done = document.querySelector('[data-testid=ai-done]');
        if (!done) return { drawn: false };
        const tick = done.querySelector('[data-testid=ai-done-tick]');
        const h1 = done.querySelector('h1');
        const t = (el) => (el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : null);
        return { drawn: true, tick: !!tick, title: t(h1),
                 tick_first: !!(tick && h1 && (tick.compareDocumentPosition(h1) & Node.DOCUMENT_POSITION_FOLLOWING)),
                 mic_off: !!document.querySelector('[data-testid=ai-mic-off]'), text: t(done) };
    }""")


def avatar_walk(run, page, url: str, interview: dict, *, no_on: str | None = None) -> dict:
    """Spec 157's name for the AI link's walk (the face's view), kept: `link_walk` with a story told."""
    return link_walk(run, page, url, interview, no_on=no_on)


def walk_link(run, url: str, interview: dict, *, shot: str, viewport: dict | None = None, **how) -> dict:
    """A stranger's browser (the seam -- the microphone granted, or refused -- and the orb's collector), the link walked,
    the browser closed."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    stranger = run.browser.new_context(**({"viewport": viewport} if viewport else {}))
    try:
        stranger.add_init_script(ivs.speech_seam(refused=bool(how.get("refused"))))
        stranger.add_init_script(ss.ORB_INTERVIEW_WATCH)
        page = stranger.new_page()
        walked = link_walk(run, page, url, interview, **how)
        ss._BrowserStep(run.recorder, page, "participant").screenshot(shot)
        return walked
    finally:
        stranger.close()


def first_response(walked: dict) -> dict:
    """The last response the page posted: its status and what it sent."""
    responses = walked.get("responses") or []
    return responses[-1] if responses else {}


# ------------------------------------------------------------------------------------------------ the orb's checks

def film_first_checks(run, leg, walked: dict, *, view: str, study: str) -> None:
    """159 FR-1 / FR-2 (keel-web 253 FR-3): after Start the film plays first -- no hand-over line, nothing spoken before
    it -- then the speaker says the opening before the first question; on a solution or money link the idea's story
    later, after its hand-over line."""
    log = walked.get("log") or []
    seq = ss.stage_sequence(log)
    lead = [s for s in seq if s in ("speaking", "listening", "held", "confirming") or str(s).startswith("film:")]
    films = [r for r in walked["rows"] if r["screen"] == "film"]
    first = films[0] if films else {}
    leg.check(run, "the film first: after Start the problem's film is on the stage before anything is said or asked, "
                   "with no hand-over line before it",
              bool(lead) and lead[0] == "film:problem" and first.get("kind") == "problem" and first.get("first")
              and not first.get("hand") and bool(first.get("player")), screen="Start -> the film", view=view,
              detail={"stage": seq[:12], "film": first})
    after = lead[1:] if lead[:1] == ["film:problem"] else []
    leg.check(run, "then the opening: the speaker speaks after the film, before the first question",
              "speaking" in after and after.index("speaking") < (after.index("listening") if "listening" in after
                                                                    else len(after)),
              screen="the film -> the opening", view=view, detail={"after the film": after[:8]})
    if study in ("solution", "money"):
        idea = [r for r in films if r.get("kind") == "idea"]
        leg.check(run, "the idea's story after its hand-over line (*Let me show you how ...*)",
                  bool(idea) and all(str(r.get("hand") or "").startswith(HAND_OVER["idea"]) for r in idea),
                  screen="the idea's hand-over", view=view,
                  detail={"films": films, "drift": "runs/DRIFT.md #106" if study == "money" else None}, stop=False)


def question_count(interview: dict) -> int:
    """keel-web `questionCount`: the screener where the link asks one, the gate on a FULL link, and every item -- the
    count the intro's headline says."""
    items = sum(len(part.get("items") or []) for part in interview.get("parts") or [])
    gate = 1 if interview.get("kind", "FULL") == "FULL" and interview.get("gate") else 0
    return (1 if fake.condition_of(interview) else 0) + gate + items


def intro_checks(run, leg, walked: dict, interview: dict, *, view: str, label: str, speaker: str,
                 name: str | None = None) -> None:
    """Spec 160 FR-1 (keel-web 256 FR-1, FR-2): the pared-down first screen on either speaker -- the orb (or her face)
    beside *{founder} has {n} questions for you.*, *A spoken interview with Keel (her name), an AI interviewer, not a
    person.* under it, the one sentence, the chips, *What happens to your answers* closed with the microphone line, the
    transcriber line and the consent inside it, and one button: *Test your mic* before the hello, *Start the interview*
    in its place after, never both."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    intro = walked.get("intro") or {}
    after = (walked.get("mic") or {}).get("after") or {}
    who = ivs.ORB_NAME if speaker == ivs.SPEAKER_ORB else (name or "")
    founder = ivs.intro_founder(interview)
    heading = ivs.ai_intro_heading(founder, question_count(interview))
    answers = intro.get("answers") or {}
    lines = answers.get("lines") or []
    leg.check(run, f"{label}: the intro's headline *{heading}* and *{ivs.ai_intro_spoken(who)}* under it "
                   f"({'the orb' if speaker == ivs.SPEAKER_ORB else 'her portrait'} beside them)",
              intro.get("speaker") == speaker and intro.get("heading") == heading
              and intro.get("spoken") == ivs.ai_intro_spoken(who)
              and (intro.get("orb", 0) >= 1 if speaker == ivs.SPEAKER_ORB else not intro.get("orb")),
              screen="the AI intro", view=view,
              detail={k: intro.get(k) for k in ("speaker", "orb", "heading", "spoken", "study")} | {"want": heading})
    chips = ivs.ai_intro_chips(interview.get("minutes"))
    leg.check(run, f"{label}: one sentence (*{ivs.ai_intro_asks(who)[:40]}...*), the chips {chips}, and *What happens to "
                   "your answers* closed, holding the microphone line, the transcriber line and the consent",
              intro.get("asks") == ivs.ai_intro_asks(who) and intro.get("chips") == chips
              and answers.get("drawn") and not answers.get("open") and answers.get("summary") == ivs.CONSENT_HEADING
              and lines[:2] == [ivs.AI_INTRO_MIC_LINE, ivs.INTRO_TRANSCRIBED]
              and len(lines) == 3 and lines[2] == " ".join(str(interview.get("consentText") or "").split()),
              screen="the AI intro", view=view, detail={"asks": intro.get("asks"), "chips": intro.get("chips"),
                                                        "want chips": chips, "answers": answers})
    leg.check(run, f"{label}: one button -- *{ivs.MIC_TEST}* before the hello, *{ivs.START_THE_INTERVIEW}* in its place "
                   "once *Heard: hello* (`ai-mic-test` -> `ai-start`, never both)",
              intro.get("buttons") == ["ai-mic-test"] and after.get("buttons") == ["ai-start"]
              and after.get("mic_heard") == ivs.mic_heard("hello") and not intro.get("fallback"),
              screen="the AI intro", view=view,
              detail={"before": intro.get("buttons"), "after": after.get("buttons"), "heard": after.get("mic_heard")})


def orb_screen_checks(run, leg, walked: dict, interview: dict, *, view: str, label: str) -> None:
    """159 FR-1 (the stage) with 160 FR-1's intro: the orb on the stage, no `<video>`, nothing an orb link never
    draws."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    intro_checks(run, leg, walked, interview, view=view, label=label, speaker=ivs.SPEAKER_ORB)
    log = walked.get("log") or []
    stage = [r for r in log if r.get("onStage")]
    leg.check(run, f"{label}: the orb asks on the stage (`data-speaker` ORB), no `<video>` anywhere",
              bool(stage) and all(r.get("speaker") == ivs.SPEAKER_ORB for r in stage)
              and not any(r.get("video") for r in log), screen="the stage", view=view,
              detail={"speakers": sorted({str(r.get('speaker')) for r in stage}),
                      "video": any(r.get("video") for r in log)})
    never = ss.never_drawn(log)
    leg.check(run, f"{label}: no voice bar, no *Read and tap*, no talk-or-write choice on any screen",
              not never["voice_bar"] and not never["read_and_tap"] and not never["choice"], screen="every screen",
              view=view, detail=never)


def retired_checks(run, leg, walked: dict, *, view: str, label: str) -> None:
    """Spec 160 FR-1 / FR-4 / FR-5: what keel-web 256 retired is drawn on no screen of the link -- the film's orb
    (`ai-story-orb`), *Go on to the question* (`ai-story-go-on`), *Say it again* (`ai-again`), the mic fallback
    (`ai-mic-fallback`)."""
    log = walked.get("log") or []
    seen = {"ai-story-orb": any(r.get("filmOrb") for r in log), "ai-story-go-on": any(r.get("goOn") for r in log),
            "ai-again": any(r.get("again") for r in log), "ai-mic-fallback": any(r.get("fallback") for r in log)}
    leg.check(run, f"{label}: none of 256's retired ids on any screen (`ai-story-orb`, `ai-story-go-on`, `ai-again`, "
                   "`ai-mic-fallback`)", not any(seen.values()), screen="every screen", view=view, detail=seen,
              stop=False)


def film_checks(run, leg, walked: dict, interview: dict, *, view: str) -> None:
    """Spec 160 FR-4 (keel-web 256 FR-3) on the problem's film: nothing above the board, two icons and no worded button,
    pause flips and holds, resume, start over, the board's words shown and hidden, the end drawing *Begin the
    interview* with nothing played until it is pressed, then the opening and the speaker."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    film = next((r for r in walked.get("rows") or [] if r.get("screen") == "film" and r.get("kind") == "problem"), {})
    c = film.get("controls") or {}
    first = c.get("first") or film.get("read") or {}
    inside = first.get("inside") or {}
    speaker = c.get("speaker") or {}
    leg.check(run, "the film: no speaker above the board -- no orb, face or `<video>` inside it, the speaker's box "
                   "under it", bool(first.get("drawn")) and not any(inside.values())
              and not (speaker.get("seen") and not speaker.get("covered")) and first.get("covered") is not False,
              screen="the film", view=view, detail={"inside": inside, "covered": first.get("covered"),
                                                    "speaker": speaker}, stop=False)
    leg.check(run, "the film: two icons under the board (`ai-film-pause`, `ai-film-again`), no worded button",
              bool(first.get("pause")) and bool(first.get("again")) and not first.get("worded")
              and not first.get("begin"), screen="the film", view=view,
              detail={k: first.get(k) for k in ("pause", "again", "worded", "begin", "pauseLabel")}, stop=False)
    paused = c.get("paused") or {}
    at, later = paused.get("at") or {}, paused.get("later") or {}
    leg.check(run, f"the film: pause flips the icon (*{ivs.FILM_RESUME_LABEL}*) and holds the drawing for 1.5 s",
              at.get("state") == "paused" and at.get("pauseLabel") == ivs.FILM_RESUME_LABEL
              and at.get("paused") == "true" and bool(at.get("sig")) and at.get("sig") == later.get("sig"),
              screen="the film · pause", view=view,
              detail={"playing": (c.get("playing") or {}).get("sig"), "at": {k: at.get(k) for k in
                                                                              ("state", "pauseLabel", "paused", "sig")},
                      "later": later.get("sig"), "missed": c.get("missed")}, stop=False)
    resumed = c.get("resumed") or {}
    again = c.get("again") or {}
    before, after = (again.get("before") or {}).get("sig") or {}, (again.get("after") or {}).get("sig") or {}
    leg.check(run, f"the film: resumed (*{ivs.FILM_PAUSE_LABEL}* again), then *Start over* draws it from the start",
              resumed.get("state") == "playing" and resumed.get("pauseLabel") == ivs.FILM_PAUSE_LABEL
              and (again.get("after") or {}).get("state") == "playing"
              and (before.get("on") or 0) > (after.get("on") or 0), screen="the film · start over", view=view,
              detail={"resumed": {k: resumed.get(k) for k in ("state", "pauseLabel", "sig")}, "before": before,
                      "after": after}, stop=False)
    shown, hidden = c.get("shown") or {}, c.get("hidden") or {}
    leg.check(run, "the film: a tap on the board shows its lines under it, a second tap hides them",
              shown.get("read") and shown.get("expanded") == "true" and bool(shown.get("lines"))
              and not hidden.get("read") and hidden.get("expanded") == "false", screen="the film · the board",
              view=view, detail={"shown": {k: shown.get(k) for k in ("expanded", "lines")},
                                 "hidden": {k: hidden.get(k) for k in ("read", "expanded")}}, stop=False)
    end = film.get("at_end") or {}
    end_film = end.get("film") or {}
    leg.check(run, f"the film's end: *{ivs.FILM_BEGIN_WORDS}* in the icons' place, and for 2 s nothing plays, the "
                   "stage stays on the film, no speaker seen, no words",
              end.get("begin") == ivs.FILM_BEGIN_WORDS and not end_film.get("pause") and not end.get("plays")
              and end.get("phase") == "story" and not ((end.get("speaker") or {}).get("seen")
                                                       and not (end.get("speaker") or {}).get("covered"))
              and not end.get("words"), screen="the film's end", view=view,
              detail={"begin": end.get("begin"), "plays": end.get("plays"), "phase": end.get("phase"),
                      "speaker": end.get("speaker"), "stuck": film.get("stuck")}, stop=False)
    after_press = film.get("after") or {}
    plays = after_press.get("plays") or []
    first_clip = plays[0][3] if plays and len(plays[0]) > 3 else None
    box = after_press.get("speaker") or {}
    leg.check(run, "after *Begin the interview*: the opening's clip is the first to play, and the speaker is drawn "
                   "(large, as it asks)", bool(plays) and first_clip == after_press.get("opening")
              and box.get("seen") and not box.get("covered") and box.get("size") == ivs.SIZE_LARGE,
              screen="Begin the interview -> the opening", view=view,
              detail={"plays": plays, "opening": after_press.get("opening"), "speaker": box,
                      "phase": after_press.get("phase")}, stop=False)


def replay_checks(run, leg, walked: dict, *, view: str) -> None:
    """Spec 160 FR-5 (keel-web 256 FR-4): the replay mark on the first item -- *Hear the question again* -- plays the
    item's clip again and the window opens again; *Say it again* (`ai-again`) is drawn nowhere."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    r = walked.get("replay") or {}
    played = [x[3] for x in r.get("plays") or [] if len(x) > 3]
    leg.check(run, f"the replay mark (*{ivs.REPLAY_LABEL}*) on the first item plays its clip again and opens the "
                   "window again", bool(r.get("drawn")) and r.get("label") == ivs.REPLAY_LABEL
              and bool(r.get("clip")) and r.get("clip") in played and r.get("reopened") is True
              and not r.get("again_drawn"), screen="an item · the replay mark", view=view,
              detail={k: r.get(k) for k in ("question", "clip", "drawn", "label", "plays", "reopened", "phase",
                                            "again_drawn", "stuck")}, stop=False)


def chip_checks(run, leg, walked: dict, *, view: str, speaker: str, name: str | None = None) -> None:
    """Spec 160 FR-1 (keel-web 256 FR-5, FR-6, judgement call 9): the chip that says it is an AI -- on the orb *Keel ·
    AI interviewer* with the orb; on the face *{name} · AI interviewer* in her caption band while she speaks (large)
    and in her column under her portrait once the sheet opens (small)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    rows = [r for r in walked.get("log") or [] if r.get("onStage") and not r.get("film") and r.get("chip")]
    want = ivs.MARK if speaker == ivs.SPEAKER_ORB else ivs.face_mark(name or "")
    words = sorted({r.get("chip") for r in rows})
    if speaker == ivs.SPEAKER_ORB:
        places = sorted({str(r.get("chipIn")) for r in rows})
        ok = bool(rows) and words == [want] and places == ["orb"]
    else:
        wrong = [(r.get("size"), r.get("chipIn")) for r in rows
                 if (r.get("size"), r.get("chipIn")) not in (("large", "caption"), ("small", "facecol"))]
        places = sorted({f"{r.get('size')}:{r.get('chipIn')}" for r in rows})
        ok = bool(rows) and words == [want] and not wrong
    leg.check(run, f"the chip *{want}* -- " + ("with the orb" if speaker == ivs.SPEAKER_ORB else
                                                "in her caption band while she asks, under her portrait once the "
                                                "sheet opens"), ok, screen="the stage · the chip", view=view,
              detail={"words": words, "places": places}, stop=False)


def last_page_checks(run, leg, walked: dict, interview: dict, *, view: str) -> None:
    """Spec 160 FR-6 (keel-web 256 FR-7, judgement call 8): the last page -- the tick, then *Done. Your answers have
    gone to {founder}.*, *Microphone off*, *What is Keel?*; the served thanks sentence is not drawn."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    page = walked.get("last_page") or {}
    title = ivs.ai_done_title(ivs.intro_founder(interview))
    thanks = " ".join(str((interview.get("done") or {}).get("thanks") or "").split())
    text = page.get("text") or ""
    leg.check(run, f"the last page: the tick, then *{title}*, *{ivs.MIC_OFF}*, *{ivs.WHAT_IS_KEEL}*; the served thanks "
                   "not drawn", bool(page.get("drawn")) and page.get("tick") and page.get("tick_first")
              and page.get("title") == title and page.get("mic_off") and ivs.WHAT_IS_KEEL in text
              and (not thanks or thanks not in text), screen="the last page", view=view,
              detail={**{k: page.get(k) for k in ("tick", "tick_first", "title", "mic_off")}, "want": title,
                      "served thanks": thanks, "text": text[:300]}, stop=False)


def blocked_walk(run, url: str, *, shot: str) -> dict:
    """Spec 160 FR-2 (keel-web 256 FR-2): a stranger's browser with the microphone refused -- *Test your mic* ends at
    the block and nothing starts; then the microphone allowed (`Player.allow_mic`) and *Test your mic* pressed again:
    *Heard: hello* and *Start the interview* (not pressed: the link is left unanswered)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    stranger = run.browser.new_context()
    try:
        stranger.add_init_script(ivs.speech_seam(refused=True))
        stranger.add_init_script(ss.ORB_INTERVIEW_WATCH)
        page = stranger.new_page()
        p = ivs.Player(page, run.recorder)
        intro = p.open(url)
        refused = p.refused_mic_test()
        ss._BrowserStep(run.recorder, page, "participant").screenshot(shot)
        p.allow_mic()
        try:
            allowed = p.mic_test()
        except Exception as missed:  # noqa: BLE001 - recorded on the check
            allowed = {"stuck": str(missed)[:200], "after": p.intro()}
        log = ss.iv_log(page)
        return {"intro": intro, "refused": refused, "allowed": allowed, "log": log}
    finally:
        stranger.close()


def block_line(blocked: dict) -> str:
    """What the report keeps of a refused link: the block's words, the buttons at it, the buttons once allowed."""
    r = blocked.get("refused") or {}
    after = (blocked.get("allowed") or {}).get("after") or {}
    return (f"refused: {(r.get('block') or {}).get('line')} / {(r.get('block') or {}).get('how')}; buttons "
            f"{(r.get('at') or {}).get('buttons')}; stage shown {r.get('stage_shown')}; allowed again: buttons "
            f"{after.get('buttons')}, {after.get('mic_heard')}")


def blocked_checks(run, leg, blocked: dict, *, view: str) -> None:
    """Spec 160 FR-2: the block, no Start, no stage, no question; the microphone allowed again -> *Start the
    interview*."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    r = blocked.get("refused") or {}
    at, later = r.get("at") or {}, r.get("after") or {}
    log = blocked.get("log") or []
    leg.check(run, f"the microphone refused: the block (*{ivs.MIC_BLOCK}* and how to allow it), the button still "
                   f"*{ivs.MIC_TEST}*, no *{ivs.START_THE_INTERVIEW}*",
              (r.get("block") or {}).get("line") == ivs.MIC_BLOCK and (r.get("block") or {}).get("how") == ivs.MIC_BLOCK_HOW
              and at.get("buttons") == ["ai-mic-test"] and later.get("buttons") == ["ai-mic-test"]
              and at.get("mic_test_words") == ivs.MIC_TEST and not at.get("fallback"),
              screen="the AI intro · refused", view=view,
              detail={"block": r.get("block"), "buttons": [at.get("buttons"), later.get("buttons")],
                      "button": at.get("mic_test_words"), "fallback": at.get("fallback")})
    leg.check(run, "the microphone refused: nothing starts -- no stage, no question ever drawn",
              not r.get("stage_shown") and not r.get("sheet") and not any(r_.get("onStage") for r_ in log)
              and not any(r_.get("question") for r_ in log), screen="the AI intro · refused", view=view,
              detail={"stage": r.get("stage_shown"), "sheet": r.get("sheet"), "phase": r.get("phase"),
                      "on stage": sum(1 for r_ in log if r_.get("onStage"))})
    allowed = blocked.get("allowed") or {}
    after = allowed.get("after") or {}
    leg.check(run, f"the microphone allowed again: *{ivs.MIC_TEST}* once more -> *Heard: hello* and *{ivs.START_THE_INTERVIEW}*",
              after.get("buttons") == ["ai-start"] and after.get("mic_heard") == ivs.mic_heard("hello")
              and not (after.get("block") or {}).get("drawn"), screen="the AI intro · allowed", view=view,
              detail={"buttons": after.get("buttons"), "heard": after.get("mic_heard"), "block": after.get("block"),
                      "stuck": allowed.get("stuck")})


def speaker_walk(run, study: str, speaker: str, walked: dict) -> list[dict]:
    """Spec 160 FR-3: the walk's steps kept for the comparison and the report."""
    steps = ss.walk_steps(walked.get("log") or [])
    run.__dict__.setdefault("speaker_walks", {}).setdefault(study, {})[speaker] = steps
    return steps


def same_walk_check(run, leg, study: str, *, view: str) -> None:
    """Spec 160 FR-3: the orb's link and the face's, walked alike, are the same walk step for step (the state word, the
    speaker's size, the ids drawn, the words lit) -- or the leg fails naming the step they part at."""
    walks = (run.__dict__.get("speaker_walks") or {}).get(study) or {}
    orb, face = walks.get("ORB"), walks.get("AVATAR")
    if orb is None or face is None:
        verdict = {"same": None, "why": "the orb's walk was not recorded" if orb is None else "no face walk"}
    else:
        verdict = ss.same_walk(orb, face)
    run.__dict__.setdefault("speaker_verdicts", {})[study] = verdict
    where = "" if verdict.get("same") or verdict.get("at") is None else \
        f" -- they part at step {verdict['at'] + 1}: orb `{(verdict.get('orb') or {}).get('step')}`, face " \
        f"`{(verdict.get('face') or {}).get('step')}` ({', '.join(verdict.get('differs') or [])})"
    leg.check(run, "the same walk on both speakers: the orb's link and the face's, step for step -- the state, the "
                   "speaker's size, the ids drawn, the words lit" + where, verdict.get("same") is True,
              screen="every screen (both links)", view=view, detail=verdict, stop=False)


def orb_states_check(run, leg, walked: dict, *, view: str) -> None:
    """159 FR-1 (158 FR-2's collector): the orb's `data-state` runs speaking -> listening -> hearing -> writing through
    an answer."""
    runs = ss.orb_answer_runs(walked.get("log") or [])
    want = ["speaking", "listening", "hearing", "writing"]
    whole = [r for r in runs if ss.holds_in_order(r, want)]
    leg.check(run, "the orb runs *speaking > listening > hearing > writing* through an answer",
              bool(whole), screen="the stage orb", view=view,
              detail={"answers read whole": len(whole), "runs": [" > ".join(r) for r in runs[:10]]})


def speak_or_tap_checks(run, leg, rows: list[dict], *, view: str, study: str) -> None:
    """159 FR-3: one item by its letter (*B* holds the second row), one by its words, one by tap (the first row) --
    over the voice links' rows, across the three studies. A problem link hosts two items with rows at most (the chip
    said ends its link at the story's chip, keel-web 255; since spec 160 the refused link never starts), so a way no
    item was left for on one study is carried to the next; on the last study (money) a way never taken anywhere is the
    failed check."""
    tried = {r["fr3"]: r for r in rows if r.get("fr3")}
    seen = run.__dict__.setdefault("fr3_seen", set())
    seen.update(tried)
    for how, words in (("letter", f"*{LETTER}* said holds the second row (keel-cloud 266 through the fake transcriber)"),
                       ("words", "the first row's words said hold the first row"),
                       ("tap", "a tap on the first row holds it")):
        r = tried.get(how) or {}
        if not r and how not in seen and study != "money":
            leg.check(run, f"speak or tap: {words} -- no item left for it on this study's links; carried to the next "
                           "study", True, screen="an item with rows", view=view, detail={"carried": how}, stop=False)
            continue
        if not r and how in seen:
            leg.check(run, f"speak or tap: {words} -- held on an earlier study", True, screen="an item with rows",
                      view=view, detail={"held_on_an_earlier_study": how}, stop=False)
            continue
        lit = (r.get("read") or {}).get("lit") or []
        leg.check(run, f"speak or tap: {words}", bool(r) and bool(lit) and lit[0] == r.get("want_lit"),
                  screen="an item with rows",
                  view=view, detail={"question": r.get("question"), "said": r.get("said"), "want": r.get("want_lit"),
                                     "read": r.get("read"), "control": r.get("control")}, stop=False)


def no_typed_box_check(run, leg, walked: dict, *, view: str, label: str) -> None:
    """159 FR-3 (keel-web 254 FR-2): no box that takes typed words on any screen of the link."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    never = ss.never_drawn(walked.get("log") or [])
    on_rows = [(r.get("question"), r.get("typed")) for r in walked["rows"] if r.get("typed")]
    retired = ss.web_retired_typing(run.stack.keel_web)
    leg.check(run, f"{label}: no typed box (`{ivs.TYPED_BOXES}`) on any screen", not never["typed"] and not on_rows,
              screen="every screen", view=view,
              detail={"typed": never["typed"], "on the questions": on_rows[:6],
                      "keel-web 254 in the checkout": retired,
                      "drift": None if retired else "keel-web 254 not yet merged: the text box stands"}, stop=False)


# ------------------------------------------------------------------------------------------------ the orb view

def orb_view(run, leg, study: str, project_id: str) -> None:
    """Spec 159 FR-1, FR-3, FR-4: the TEXT link is the orb. Four links (three on money, which has no story): the walk
    by voice (a story told; letter, words, tap -- spec 160: the film's controls, the replay mark, the last page, and the
    walk's steps kept for the face's to be held to), the story's chip said aloud, the microphone refused (spec 160 FR-2:
    the block, then allowed), and the No; then the film on a phone (158b), and the ledger (no charge for the orb's
    clips)."""
    from harness import interview_charge as charge    # noqa: PLC0415
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    names = people(run, "PROBLEM")
    decider = study == "money"
    view = "orb"
    made = tv.send_link(run, leg, f"{study}-orb", project_id, "TEXT", person=person_at(names, 1), decider=decider)
    popup_checks(run, leg, made)
    interview, reads = read_served(run, made["url"])
    run.orb_wires[study] = {"interview": interview, "url": made["url"]}
    wire_checks(run, leg, study, interview, view, speaker=ivs.SPEAKER_ORB, reads=reads)
    opening = ((interview.get("interviewer") or {}).get("clips") or {}).get("opening") or {}
    got = fetch_clip(run, opening.get("url"))
    leg.check(run, "the orb's opening clip is served to a stranger with no cookie (audio, FakeSpeech's)",
              got.get("status") == 200 and "audio" in str(got.get("type") or ""), screen="GET /v2/clips/{id}",
              view=f"{view} (wire)", detail=got)
    # 1. by voice: a story told; one item by its letter, one by its words, one by tap; the film's controls and the
    # replay mark (spec 160 FR-4, FR-5) -- the walk the face's is held to (FR-3)
    ways = list(SPEAK_OR_TAP)          # owed across the voice links (a problem link has two items with rows)
    walked = walk_link(run, made["url"], interview, shot=f"orb-{study}-done", speak_or_tap=ways, film_checks=True,
                       replay=True)
    steps = speaker_walk(run, study, ivs.SPEAKER_ORB, walked)
    run.orbs.append({"study": study, "link": "voice", **summary(walked)})
    orb_screen_checks(run, leg, walked, interview, view=view, label="by voice")
    retired_checks(run, leg, walked, view=view, label="by voice")
    film_first_checks(run, leg, walked, view=view, study=study)
    film_checks(run, leg, walked, interview, view=view)
    replay_checks(run, leg, walked, view=view)
    last_page_checks(run, leg, walked, interview, view=view)
    chip_checks(run, leg, walked, view=view, speaker=ivs.SPEAKER_ORB)
    leg.notes.append(f"the orb's walk ({study}): {len(steps)} steps -- " + " > ".join(s_["step"] for s_ in steps)[:600])
    orb_states_check(run, leg, walked, view=view)
    no_typed_box_check(run, leg, walked, view=view, label="by voice")
    sent = first_response(walked)
    leg.check(run, "the answers are sent (201), named TEXT (the format the link was served), and the thank-you drawn",
              sent.get("status") == 201 and (sent.get("sent") or {}).get("format") == "TEXT" and bool(walked["done"]),
              screen="the last question -> the thank-you", view=view,
              detail={"status": sent.get("status"), "format": (sent.get("sent") or {}).get("format"),
                      "answers": len((sent.get("sent") or {}).get("answers") or []), "done": walked["done"]})
    if study != "money":                                   # the decision-maker's link has no gate and no story
        story_rows = [r for r in walked["rows"] if r.get("story")]
        chips = (story_rows[0] if story_rows else {}).get("chips") or []
        leg.check(run, "the story question carries both chips (*I can't recall one particular ...*, *I'd rather not "
                       "say*)", len(chips) == 2 and any("can't recall" in c for c in chips)
                  and any("rather not say" in c for c in chips), screen="the gate's story question", view=view,
                  detail={"chips": chips})
        # 2. the story's chip said aloud
        chip_link = tv.send_link(run, leg, f"{study}-orb-chip", project_id, "TEXT", person=person_at(names, 8),
                                 decider=decider)
        chip_wire, _ = read_served(run, chip_link["url"])
        said = walk_link(run, chip_link["url"], chip_wire, shot=f"orb-{study}-chip-voice", story="chip-voice",
                         speak_or_tap=ways)
        run.orbs.append({"study": study, "link": "the chip said", **summary(said)})
        body = first_response(said).get("sent") or {}
        told = ((body.get("gate") or {}) if isinstance(body.get("gate"), dict) else body)
        chip_row = next((r for r in said["rows"] if r.get("story")), {})
        leg.check(run, "the story's chip said aloud (*I can't recall one particular ...*) is taken as the chip "
                       "(`anchorChip` CANT_RECALL), as its tap is",
                  (told.get("anchorChip") or body.get("anchorChip")) == "CANT_RECALL", screen="the story question",
                  view=view, detail={"said": chip_row.get("said"), "sent": {k: body.get(k) for k in
                                                                            ("recency", "anchorChip", "story", "gate")},
                                     "answers": len(body.get("answers") or []), "done": said["done"]}, stop=False)
    speak_or_tap_checks(run, leg, walked["rows"] + (said["rows"] if study != "money" else []), view=view, study=study)
    # 3. the microphone refused: the block, nothing starts; allowed again, Start (spec 160 FR-2)
    block_link = tv.send_link(run, leg, f"{study}-orb-block", project_id, "TEXT", person=person_at(names, 9),
                              decider=decider)
    blocked = blocked_walk(run, block_link["url"], shot=f"orb-{study}-blocked")
    run.orbs.append({"study": study, "link": "the microphone refused", "block": block_line(blocked)})
    blocked_checks(run, leg, blocked, view=f"{view} · refused")
    # 4. the No that ends it
    no_on = "check" if decider else "gate"
    no_link = tv.send_link(run, leg, f"{study}-orb-no", project_id, "TEXT", person=person_at(names, 2), decider=decider)
    no_wire, _ = read_served(run, no_link["url"])
    no_walk = walk_link(run, no_link["url"], no_wire, shot=f"orb-{study}-no", no_on=no_on)
    asked = [r["question"] for r in no_walk["rows"] if r["screen"] == "question"]
    sent = first_response(no_walk).get("sent") or {}
    what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
    leg.check(run, f"a No on the {what} ends the interview in the orb view: no question after it, the response a No "
                   "alone", bool(no_walk["responses"]) and sent.get("recency") is False and not (sent.get("answers") or []),
              screen=f"the {what} -> the end", view=view,
              detail={"asked": asked, "responses": no_walk["responses"], "done": no_walk["done"]})
    phone_film(run, leg, study, project_id, person_at(names, 7))
    if not run.remote and run.account_id:
        from stack import ledger    # noqa: PLC0415
        rows = [r for r in ledger.rows(run.stack, run.account_id, since=run.ledger_since)
                if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
        faults = charge.orb_charge_faults(rows)
        leg.check(run, "the orb's clips bought nothing: every CARD_SPEECH row 0 credits, no charge but the lock's "
                       "PROJECT and the face's INTERVIEWER_RECORDING (InferenceCharge 20 unchanged)", not faults,
                  screen="the ledger", view="wire",
                  detail={"faults": faults, "CARD_SPEECH rows": len(charge.card_speech_rows(rows)),
                          "charges": [(r.get("action"), r.get("credits")) for r in rows if int(r.get("credits") or 0) < 0]})


def summary(walked: dict) -> dict:
    """What the report keeps of one walk: the stage's sequence, the orb's runs, the questions and how each was answered,
    what was never to be drawn, the response."""
    log = walked.get("log") or []
    sent = first_response(walked)
    body = sent.get("sent") or {}
    return {"stage": ss.stage_sequence(log)[:16], "orb": [" > ".join(r) for r in ss.orb_answer_runs(log)][:12],
            "answers": [(str(r.get("question") or "")[:70], r.get("said"), (r.get("read") or {}).get("lit"))
                        for r in walked.get("rows") or [] if r.get("screen") == "question"],
            "films": [(r.get("kind"), r.get("first"), r.get("hand")) for r in walked.get("rows") or []
                      if r.get("screen") == "film"],
            "never": ss.never_drawn(log), "response": {"status": sent.get("status"), "format": body.get("format"),
                                                       "anchorChip": body.get("anchorChip"),
                                                       "answers": len(body.get("answers") or [])},
            "done": walked.get("done")}


#: Spec 158b on the orb (spec 159): the film's player on the AI stage.
ORB_FILM_PLAYER = "[data-testid=ai-story] [data-testid=story-player]"


def phone_film(run, leg, study: str, project_id: str, person: str) -> None:
    """Spec 158b, moved onto the orb (spec 159): one more TEXT link, opened on a phone (390 x 844): the mic test, Start,
    and the film read while it plays -- no text on the drawing, it fits, the spoken line at most three rows."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    made = tv.send_link(run, leg, f"{study}-orb-phone", project_id, "TEXT", person=person, decider=study == "money")
    phone = run.browser.new_context(viewport=ss.PHONE)
    try:
        phone.add_init_script(ivs.SPEECH_SEAM)
        page = phone.new_page()
        p = ivs.Player(page, run.recorder)
        reached = False
        try:
            p.open(made["url"])
            p.mic_test()
            p.start()
            page.locator(ORB_FILM_PLAYER).first.wait_for(state="visible", timeout=30_000)
            reached = True
        except Exception as missed:  # noqa: BLE001 - recorded on the check
            leg.notes.append(f"phone film ({study}): {str(missed)[:200]}")
        leg.check(run, "on a phone: the mic test, Start, then the film", reached, screen="the AI intro -> the film "
                  "(phone)", view="orb · phone", detail={"url": page.url}, stop=False)
        if reached:
            tv.measure_fit(run, leg, page, f"the {study} link's film", ORB_FILM_PLAYER, where="the film on the stage",
                           view="orb · phone", phone=True)
    finally:
        phone.close()


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
            if view == "orb" and not ss.web_has_orb(run.stack.keel_web):
                run.legs[leg_id].status = "written, not run"
                run.legs[leg_id].why = "keel-web 253 (the orb interviews) is not in the checkout"
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
                if view == "orb":
                    orb_view(run, leg, study, project)
                elif view == "avatar":
                    avatar_view(run, leg, study, project)
                else:
                    copilot_view(run, leg, study, project)
            tv.timed(run, leg_id, body)


# ------------------------------------------------------------------------------------------------ avatar

def interviewer_ready(run, leg, study: str, project_id: str, label: str) -> None:
    """The kind's AI interviewer set up on Keel's door (a stand-in grant: a recording is bought, keel-cloud 247) and
    READY on the stack's fake renderer; the door is left on Keel's while the AI links are made and walked. Spec 159
    FR-4: on the first study, before the face is set up, the card's *Try it yourself* opens the dry run on the orb."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    ledger.stand_in_keels_door(run.stack, run.account_id, f"{study}-avatar-{run.stamp}", spec=tv.STAND_IN_SPEC)
    persona = ivs.Persona(run.page, run.recorder, run.web)
    tv.open_sent(run, project_id)
    card = persona.card(label)
    if card.get("state") != "READY":
        if study == "problem":
            dry_run_on_the_orb(run, leg, project_id, card)
            tv.open_sent(run, project_id)
        pressed = persona.set_up(label, FACE)
        leg.check(run, f"the AI interviewer set up for the kind ({FACE.title()}), 202", pressed["status"] in (200, 202),
                  screen="Sent · the kind's card", detail={k: pressed.get(k) for k in ("status", "sent", "refusal")})
        persona.wait_card_state(label, "READY", timeout_s=180)


def dry_run_on_the_orb(run, leg, project_id: str, card: dict) -> None:
    """Spec 159 FR-4 (keel-web 253 FR-4, keel-cloud 267 judgement call 10): a kind card not yet set up offers *Try it
    yourself* beside its set-up; the dry run opens on the orb (the intro's orb, the mic test, Start, the orb on the
    stage, a question asked); nothing is charged for it."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    role = card.get("role_id")
    button = run.page.locator(f'[data-testid=kind-card][data-role="{role}"] [data-testid={ivs.TRY_KEEL_VOICE}]')
    leg.check(run, "a kind card not yet set up offers *Try it yourself* beside its set-up (Keel's voice)",
              card.get("state") == "NOT_SET_UP" and button.count() == 1 and ss._tc(button.first) == ivs.TRY_IT_YOURSELF,
              screen="Sent · the kind's card", view="founder",
              detail={"state": card.get("state"), "buttons": button.count(), "primary": card.get("primary")})
    if not button.count():
        return
    before = ledger.now(run.stack)
    page = run.context.new_page()
    try:
        page.add_init_script(ss.ORB_INTERVIEW_WATCH)
        page.goto(run.page.url, wait_until="load")
        page.locator(f'[data-testid=kind-card][data-role="{role}"] [data-testid={ivs.TRY_KEEL_VOICE}]').first.click()
        page.wait_for_url(re.compile(rf"/p/{project_id}/interviews/try/"), timeout=20_000)
        p = ivs.Player(page, run.recorder, party="founder")
        intro = p.open(page.url) if not page.get_by_test_id("ai-intro").count() else p.intro()
        p.mic_test()
        p.start()
        asked = None
        deadline = time.monotonic() + 180            # spec 160: the film is watched to its end (never skipped now)
        while time.monotonic() < deadline and not asked:
            begin = page.get_by_test_id(ivs.FILM_BEGIN)
            if begin.count() and begin.first.is_visible():
                begin.first.click()                     # keel-web 256 FR-3: *Begin the interview* at the film's end
            if p.phase() == "listening" and p.question():
                asked = p.question()
            page.wait_for_timeout(300)
        log = ss.iv_log(page)
        stage = [r for r in log if r.get("onStage")]
        ss._BrowserStep(run.recorder, page, "founder").screenshot("try-it-yourself-orb")
    finally:
        page.close()
    leg.check(run, "the dry run opens on the orb: the intro's orb, the mic test, Start, the orb on the stage, a "
                   "question asked", intro.get("speaker") == ivs.SPEAKER_ORB and intro.get("orb", 0) >= 1 and bool(stage)
              and all(r.get("speaker") == ivs.SPEAKER_ORB for r in stage) and bool(asked)
              and "speaking" in ss.orb_sequence(stage), screen="Sent -> Try it yourself", view="founder",
              detail={"intro": {k: intro.get(k) for k in ("speaker", "orb", "heading")}, "asked": asked,
                      "orb": ss.orb_sequence(stage)[:10], "stage": ss.stage_sequence(log)[:10]})
    rows = [r for r in ledger.rows(run.stack, run.account_id, since=before)
            if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
    from harness import interview_charge as charge    # noqa: PLC0415
    leg.check(run, "the dry run on the orb charged nothing (no row moves the balance)",
              not [r for r in rows if int(r.get("credits") or 0) != 0] and not charge.orb_charge_faults(rows),
              screen="the ledger", view="wire", detail={"rows": [(r.get("action"), r.get("credits")) for r in rows]})


def same_words(run, leg, study: str, project_id: str, role_id: str | None, avatar: dict) -> None:
    """159 FR-2: for the same role, the orb link's and the avatar link's opening -- and one item -- are the same words:
    the face's clip's script (the stack's recording) keyed as Keel AI keys it equals the `speech_clip` row the orb's
    clip is (one row read by both)."""
    from stack import ledger    # noqa: PLC0415
    orb = (run.orb_wires.get(study) or {}).get("interview") or {}
    if run.remote or not orb:
        leg.notes.append("the same words: not read (" + ("remote profile" if run.remote else "no orb link read") + ")")
        return
    recording = ledger.recording_of(run.stack, project_id, role_id) or {}
    scripts = {}
    for clip in recording.get("clips") or []:
        if isinstance(clip, dict) and clip.get("id"):
            scripts[str(clip["id"])] = clip.get("script")
    a_player, o_player = avatar.get("interviewer") or {}, orb.get("interviewer") or {}
    pairs = [("the opening", ((a_player.get("clips") or {}).get("opening") or {}).get("clipId"),
              ((o_player.get("clips") or {}).get("opening") or {}).get("clipId"))]
    a_items = {i.get("dimension"): i.get("itemId") for i in ss.served_items(avatar)}
    o_items = {i.get("dimension"): i.get("itemId") for i in ss.served_items(orb)}
    common = next((d for d in a_items if d in o_items and ((a_player.get("items") or {}).get(a_items[d]) or {}).get("clip")
                   and ((o_player.get("items") or {}).get(o_items[d]) or {}).get("clip")), None)
    if common:
        pairs.append((f"the item {common}", (((a_player.get("items") or {}).get(a_items[common]) or {}).get("clip") or {})
                      .get("clipId"), (((o_player.get("items") or {}).get(o_items[common]) or {}).get("clip") or {})
                      .get("clipId")))
    for name, a_clip, o_clip in pairs:
        script = scripts.get(str(a_clip))
        row = ledger.speech_clip(run.stack, o_clip) if o_clip else None
        same = bool(script) and bool(row) and ss.speech_key(row.get("voice"), script) == row.get("cache_key")
        leg.check(run, f"the orb and the face say the same words: {name} -- the face's script keyed as Keel AI keys it is "
                       "the orb's `speech_clip` row", same, screen="GET /v2/i/{token}/interview (both links)",
                  view="avatar (wire)", detail={"avatar clip": a_clip, "orb clip": o_clip, "script": (script or "")[:160],
                                                "row": {k: (row or {}).get(k) for k in ("voice", "cache_key")}})


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
        made = tv.send_link(run, leg, f"{study}-avatar", project_id, "AI_INTERVIEWER", person=person_at(names, 3),
                            decider=study == "money")
        no_made = tv.send_link(run, leg, f"{study}-avatar-no", project_id, "AI_INTERVIEWER", person=person_at(names, 4),
                               decider=study == "money")
        interview, reads = read_served(run, made["url"])
        wire_checks(run, leg, study, interview, "avatar", speaker=ivs.SPEAKER_AVATAR, reads=reads)
        same_words(run, leg, study, project_id, kind.get("roleId"), interview)
        # spec 160 FR-3: walked as the orb's voice link was -- the same ways from the start, the film's controls, the
        # replay mark on the first item -- so the two walks can be held equal step for step
        walked = walk_link(run, made["url"], interview, shot=f"avatar-{study}-done", speak_or_tap=list(SPEAK_OR_TAP),
                           film_checks=True, replay=True)
        steps = speaker_walk(run, study, ivs.SPEAKER_AVATAR, walked)
        leg.notes.append(f"the face's walk ({study}): {len(steps)} steps -- " + " > ".join(s_["step"] for s_ in steps)[:600])
        run.orbs.append({"study": study, "link": "the face", **summary(walked)})
        rows = walked["rows"]
        films = [r for r in rows if r["screen"] == "film"]
        name = ((interview.get("interviewer") or {}).get("face") or {}).get("name") or FACE.title()
        intro_checks(run, leg, walked, interview, view="avatar", label="the face", speaker=ivs.SPEAKER_AVATAR,
                     name=name)
        retired_checks(run, leg, walked, view="avatar", label="the face")
        film_first_checks(run, leg, walked, view="avatar", study=study)
        film_checks(run, leg, walked, interview, view="avatar")
        replay_checks(run, leg, walked, view="avatar")
        last_page_checks(run, leg, walked, interview, view="avatar")
        chip_checks(run, leg, walked, view="avatar", speaker=ivs.SPEAKER_AVATAR, name=name)
        same_walk_check(run, leg, study, view="avatar")
        leg.check(run, "Daphne returns after the film and each hand-over: the story gone, her face on the stage",
                  bool(films) and all((h.get("returned") or {}).get("story_gone") and (h.get("returned") or {}).get("face")
                                      for h in films), screen="the stage after the film", view="avatar",
                  detail=[h.get("returned") for h in films])
        questions = [r for r in rows if r["screen"] == "question"]
        leg.check(run, "the face asks on the stage (`data-speaker` AVATAR, her `<video>`)",
                  bool(questions) and all(r.get("speaker") == ivs.SPEAKER_AVATAR for r in questions),
                  screen="every question", view="avatar",
                  detail={"speakers": sorted({str(r.get('speaker')) for r in questions})})
        items = [r for r in questions if r.get("step") == "item" and not str(r.get("where") or "").startswith("Question 1 ")]
        backless = [r["question"] for r in items if not r["back"]]
        leg.check(run, "*Back to question n* on every question card after the first (the screener, the gate, its story "
                       "and the check are the link's opening)", bool(items) and not backless,
                  screen="every question sheet", view="avatar", detail={"without Back": backless,
                                                                         "rows": [(r["question"][:60], r["back"])
                                                                                  for r in questions]})
        leg.check(run, "the thank-you", bool(walked["done"]), screen="the done screen", view="avatar",
                  detail=walked["done"])
        # spec 160 FR-2 on the face: the microphone refused -- the block; allowed again -- Start
        block_made = tv.send_link(run, leg, f"{study}-avatar-block", project_id, "AI_INTERVIEWER",
                                  person=person_at(names, 10), decider=study == "money")
        blocked = blocked_walk(run, block_made["url"], shot=f"avatar-{study}-blocked")
        run.orbs.append({"study": study, "link": "the face, the microphone refused", "block": block_line(blocked)})
        blocked_checks(run, leg, blocked, view="avatar · refused")
        no_interview, _ = read_served(run, no_made["url"])
        no_walk = walk_link(run, no_made["url"], no_interview, shot=f"avatar-{study}-no",
                            no_on="check" if study == "money" else "gate")
        asked = [r["question"] for r in no_walk["rows"] if r["screen"] == "question"]
        sent = first_response(no_walk).get("sent") or {}
        what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
        leg.check(run, f"a No on the {what} ends the interview in the avatar view: no question after it",
                  bool(no_walk["responses"]) and sent.get("recency") is False and not (sent.get("answers") or []),
                  screen=f"the {what} -> the end", view="avatar",
                  detail={"asked": asked, "responses": no_walk["responses"], "done": no_walk["done"]})
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
