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

Spec 161 (keel-cloud 269 / 270, contract 87; keel-web 258): the four questions -- the gate's fixed words, a No that
goes on, Frequency's five rows, a why on every step against -- walked with the problem study's five people
(`three_surfaces.ROSTER`) and read on the founder's page (Frequency on bands, the ways, Insights with `capped`, no
Current solution); the orb, the face and the Copilot card held to one script (`three_surfaces_check`).

Spec 164 (the mirrors of keel-web 258): keel-web 258 is merged, so the wire-only path and the film-first order of a
keel-web before it are retired; the card's strips are read as its passages (FR-2), its machine's follow-ups and badges
held (mirrors 6, 7), and the founder's page read on screen too (the Frequency chart, the ways panel, Insights' `capped`).

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

#: keel-cloud 259 FR-8: the gate's (and the anchor's) wording on a story link -- until keel-cloud 269.
STORY_GATE = "In your last {window}, did this happen to you?"
#: Spec 161 FR-4 (keel-cloud 269 FR-1): the gate's fixed words after the film, on every surface.
GATE_WORDS = "Did this happen to you?"
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
    spoken = run.get(f"/v2/projects/{solution}/idea/spoken") or {}
    j.idea_name = str(idea.get("shortName") or idea.get("what") or (spoken.get("brand") or {}).get("name") or "")
    j.idea_what_it_is = idea.get("whatItIs") or spoken.get("whatItIs")
    j.idea_line = idea.get("line") or None
    calibration = tv.wait_calibration(run, solution, "SOLUTION")
    if not tv.vs_screens.solution_calibration_answered(calibration):
        # a typed solution walks its three belief pages; a spoken one (keel-cloud 271) wrote them at the board's yes
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
        want = GATE_WORDS
        leg.check(run, f"the {'anchor' if study == 'solution' else 'gate'} asks exactly *{want}* after the film -- no "
                       "window phrase (keel-cloud 269 FR-1)", gate.get("question") == want, screen="the gate card",
                  view=w, detail={"question": gate.get("question"), "readInstead": story.get("readInstead")})
        scenes = ss.scenes_verdict(story)
        leg.check(run, "the link's film: seven scenes, the seventh the pain (`pain: true`, its picture), `costLine` its "
                       "line, eight clips (keel-cloud 268 FR-5)", scenes["ok"], screen="GET /v2/i/{token}/interview",
                  view=w, detail=scenes, stop=False)
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
        # spec 162 FR-5 (keel-cloud 272 FR-3): the plate carries the brand where both films are served; the reveal is gone
        leg.check(run, "the solution link serves the idea's story and the brand on the plate (no reveal)",
                  bool((interview.get("ideaStory") or {}).get("scenes")) and bool((interview.get("plate") or {})
                                                                                 .get("name"))
                  and not interview.get("reveal"), screen="GET /v2/i/{token}/interview", view=w,
                  detail={"ideaStory": bool(interview.get("ideaStory")), "plate": interview.get("plate"),
                          "reveal": bool(interview.get("reveal"))})


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
ONE_PICK = ("single_choice", "single_choice_5", "fixed_four", "fixed_three", "scale_four", "duration_bands",
            "fixed_five",                         # spec 161 FR-6 (keel-web 258 FR-3): Frequency's five, one pick
            "yes_no")                             # spec 162 FR-6 (keel-web 260 FR-2): the solution's yes or no
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


def _why_of(question: str | None) -> dict:
    """Spec 161 FR-7: which why a follow-up sheet asks, by its words (the registry's three; else Importance's). Spec 162
    FR-7: the solution's three whys (keel-cloud 272 FR-2) by theirs."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    from harness import three_surfaces as ts    # noqa: PLC0415
    q = ts._bare(question)
    for dimension, (words, _) in sol.WHYS.items():
        if q == ts._bare(words):
            return {"dimension": dimension, "text": words}
    for dimension, words in ((ts.PREVALENCE, ts.PREVALENCE_WHY), (ts.FREQUENCY, ts.DIFFERENCE_WHY),
                             (ts.FREQUENCY, ts.NEVER_WHY)):
        if q == ts._bare(words):
            return {"dimension": dimension, "text": words}
    return {"dimension": ts.IMPORTANCE, "text": question}


def link_walk(run, page, url: str, interview: dict, *, no_on: str | None = None, story: str = "said",
              speak_or_tap: list | None = None, film_checks: bool = False, replay: bool = False,
              plan: dict | None = None) -> dict:
    """The AI player on a link -- the orb or the face -- walked through the seam: the intro (its mic test), Start, the
    film watched to its end and *Begin the interview* pressed (spec 160 FR-4: `film_checks` also pauses, resumes,
    starts it over and taps the board for its words first), the idea's story let play to its end, and each window
    answered -- the screener *yes*, the gate *yes* (or the No), the story (`story`: `said` -- a story told, `chip-voice`
    -- *I can't recall one particular ...* said, `chip-tap` -- that chip tapped), each item its first option said (or,
    `speak_or_tap`, the ways still owed -- the letter on a one-pick item, the words, the tap -- each taken off the list
    as an item takes it, so a second link walks what the first had no item for), a follow-up skipped, the pilot *yes*.
    `replay` (spec 160 FR-5): on the first item the replay mark is pressed before the answer. Every response the page
    posted is kept; the last page read once *Microphone off* is drawn (FR-6).

    Spec 161 (`plan`, one of `three_surfaces.ROSTER`'s people, keel-web 258): the screener answered as the plan says,
    the gate yes or no, the plan's own story, Frequency answered by its row's words, Importance's first pick the own row
    or not (then *Nothing else*), and every why answered in words (never skipped); each sheet's row names its step's
    key (`screener`, `gate`, the item's dimension) and a why's row `follow_up` with the rung it asks. Spec 165 (the
    film's strangers, `harness/film_strangers.walk_plan`): a plan's `pick` names Importance's row by its label and its
    `why` the person's own words for every why."""
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
    started_at = time.monotonic()            # spec 162 FR-5: each row's time from Start (the time to the first question)
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
        if page.get_by_test_id("ai-plate-stage").count() and not any(r.get("screen") == "plate" for r in rows):
            # spec 162 FR-5 (keel-web 260 FR-1): the brand plate between the check and the solution's film
            rows.append(dict(watch_plate(p, page), t=round(time.monotonic() - started_at, 1)))
            continue
        film = page.get_by_test_id("ai-story")
        if film.count():
            rows.append(dict(watch_film(run, p, page, interview, checks=film_checks),
                             t=round(time.monotonic() - started_at, 1)))
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
        # the row's words without its badge: on a story link each row carries its letter first (`cpl-bubble__let`,
        # `letterOf(i)`) -- taken off by its place (spec 164: a row such as *$10 to under $20* kept whole)
        lettered = page.locator("[data-testid=ai-sheet] .aiv__bubble").count() > 0
        options = [o["label"][1:] if lettered and o["label"][:1] == chr(ord("A") + i) and len(o["label"]) > 1
                   else re.sub(r"^[A-Z](?=[A-Z0-9])", "", o["label"]) for i, o in enumerate(sheet["options"])]
        row = {"screen": "question", "question": q, "where": where, "step": step,
               "back": page.get_by_test_id("ai-back").count(), "type_instead": page.get_by_test_id("ai-type").count(),
               "options": options, "chips": sheet.get("chips") or [], "banner": sheet.get("banner"),
               "bubbles": page.locator("[data-testid=ai-sheet] .aiv__bubble").count(),
               "speaker": p.speaker(), "typed": p.typed_boxes(), "t": round(time.monotonic() - started_at, 1)}
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
            row["follow_up"] = _why_of(q)
            if plan is not None:
                from harness import solution_surfaces as sol    # noqa: PLC0415
                from harness import three_surfaces as ts    # noqa: PLC0415
                # spec 165: a person's own recorded words where the plan carries them (the film's strangers); spec 162:
                # the solution's whys answered in the solution roster's words
                row["said"] = plan.get("why") or sol.WHY_SAID.get(str(row["follow_up"].get("dimension"))) \
                    or ts.why_said(row["follow_up"])
                p.say(row["said"])
            else:
                row["said"] = "skip"
                page.get_by_test_id("ai-skip").first.click()
        elif condition and q == condition:
            row["key"] = "screener"
            yes_no("no" if (plan or {}).get("screener") == "no" or no_on == "screener" else "yes")
        elif gate and q == gate.get("question"):
            row["key"] = "gate"
            yes_no("no" if (no_on == "gate" or (plan is not None and not plan.get("gate"))) else "yes")
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
                row["said"] = (plan or {}).get("story") or STORY_SAID
                p.say(row["said"])
        elif where == ivs.LAST_QUESTION:
            yes_no("yes")
        elif options:
            item = item_of(items, q)
            row["control"] = item.get("control")
            row["key"] = item.get("dimension")
            if plan is not None and item.get("control") == "yes_no" and item.get("dimension") in (plan.get("picks") or {}):
                # spec 162 FR-6: the solution's three answered *Yes* or *No* -- by the option's words, or by its letter
                pick = plan["picks"][item["dimension"]]
                by = (plan.get("by") or {}).get(item["dimension"], "words")
                row["said"] = ("A" if pick == "yes" else "B") if by == "letter" else ("Yes" if pick == "yes" else "No")
                p.say(row["said"])
                row["read"] = _lit_after(p, q)
            elif plan is not None and item.get("control") == "fixed_five" and plan.get("frequency"):
                # spec 161 FR-6: Frequency answered by its row's words
                from harness import three_surfaces as ts    # noqa: PLC0415
                row["said"] = ts.FREQUENCY_LABELS[ts.FREQUENCY_CODES.index(plan["frequency"])]
                p.say(row["said"])
            elif plan is not None and item.get("control") == "pick_one_then_one":
                # spec 161 FR-7: the own row first, or a row that is not the own row; then *Nothing else*
                from harness import three_surfaces as ts    # noqa: PLC0415
                mine = ts.own_option(item, other_tasks=plan.get("other_tasks") or (),
                                     own_label=plan.get("own_label"))
                labels = [o.get("label") for o in item.get("options") or []]
                pick = plan.get("pick") or ((mine or {}).get("label") if plan.get("own") else next(
                    (x for x in labels if not mine or x != mine.get("label")), labels[0] if labels else None))
                row["said"] = pick
                p.say(str(pick))
            elif len(options) >= 2 and way_for(ways, item.get("control")):
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
            row["key"] = item_of(items, q).get("dimension")        # spec 164: a step of the walked record too
            row["said"] = f"tap: {sheet['chips'][0]}"
            p.tap_chip()
        else:
            row["key"] = item_of(items, q).get("dimension")
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
            "plated": bool(interview.get("plate")),
            "responses": responses, "log": ss.iv_log(page), "plays": ss.iv_plays(page), "replay": replayed}


# ------------------------------------------------------------------------------------------------ spec 160 machinery

def opening_clip(interview: dict) -> str | None:
    """The opening's clip id as served (`interviewer.clips.opening.clipId`)."""
    return (((interview.get("interviewer") or {}).get("clips") or {}).get("opening") or {}).get("clipId")


def gate_clip(interview: dict) -> str | None:
    """The gate's own clip id (`interviewer.items[gate.itemId].clip.clipId`) -- spec 161 FR-4: what plays first after
    *Begin* once the opening and the screener came before the film (keel-web 258 FR-2b)."""
    gate_id = (interview.get("gate") or {}).get("itemId")
    entry = ((interview.get("interviewer") or {}).get("items") or {}).get(gate_id) or {}
    return (entry.get("clip") or {}).get("clipId")


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
    # spec 162 (keel-web 261's eval mirrors): a film in pictures shows one picture at a time -- it plays once the shown
    # picture is past the first scene's (the pause holds it, *Start over* brings the first back)
    first_shown = (f.get("sig") or {}).get("shown")
    while time.monotonic() < deadline:
        f = p.film()
        sig = f.get("sig") or {}
        if f.get("mode") == "pictures" and first_shown is None:
            first_shown = sig.get("shown")
        if not f.get("drawn") or f.get("begin") or (sig.get("on") or 0) >= 3 \
                or (f.get("mode") == "pictures" and sig.get("shown") and first_shown and sig.get("shown") != first_shown):
            break
        page.wait_for_timeout(150)
    out["first_shown"] = first_shown
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
    after = p.film()
    if after.get("mode") == "pictures":
        # a picture follows the voice (keel-web 261 judgement call 7): the first scene's shows when its clip starts --
        # read until the first scene's picture is back (at most 3 s; the film may move on a scene before it restarts)
        until = time.monotonic() + 3
        while time.monotonic() < until and (after.get("sig") or {}).get("shown") != out.get("first_shown"):
            page.wait_for_timeout(100)
            after = p.film()
    out["again"] = {"before": before, "after": after}
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
                    "opening": gate_clip(interview)}
    row["returned"] = returned(p, page)
    return row


def watch_plate(p, page, *, timeout_s: float = 60) -> dict:
    """Spec 162 FR-5 (keel-web 260 FR-1): the brand plate on the stage -- `plate.before` said, the plate alone about three
    seconds, `plate.after` said over its fade (written under it, `ai-plate-said`), then the solution's film. Read every
    150 ms: the plate's words, its moments (`data-plate`: on, fading), the lines said, how long it stood."""
    stage = page.get_by_test_id("ai-plate-stage")
    row: dict = {"screen": "plate", "moments": [], "said": [], "plate": None}
    t0 = time.monotonic()
    deadline = t0 + timeout_s * p.patience
    while time.monotonic() < deadline and stage.count():
        try:
            moment = stage.first.get_attribute("data-plate")
            if moment and moment not in [m for m, _ in row["moments"]]:
                row["moments"].append((moment, round(time.monotonic() - t0, 2)))
            row["plate"] = row["plate"] or ss._tc(page.get_by_test_id("ai-plate"))
            said = ss._tc(page.get_by_test_id("ai-plate-said"))
            if said and said not in row["said"]:
                row["said"].append(said)
        except Exception:  # noqa: BLE001 - the stage went under the read
            pass
        page.wait_for_timeout(150)
    row["seconds"] = round(time.monotonic() - t0, 2)
    on = next((t for m, t in row["moments"] if m == "on"), None)
    fading = next((t for m, t in row["moments"] if m == "fading"), None)
    row["alone_s"] = round(fading - on, 2) if on is not None and fading is not None else None
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
    """159 FR-1 / FR-2 as keel-web 258 FR-2b moved them: the opening (and the screener) first, then the film with no
    hand-over line before it; on a solution or money link the idea's story later, after its hand-over line. The
    film-first order of keel-web 253 is retired (spec 164 mirror 1)."""
    log = walked.get("log") or []
    seq = ss.stage_sequence(log)
    lead = [s for s in seq if s in ("speaking", "listening", "held", "confirming") or str(s).startswith("film:")]
    films = [r for r in walked["rows"] if r["screen"] == "film"]
    first = films[0] if films else {}
    # spec 161 FR-4 (keel-web 258 FR-2b; spec 164 mirror 1: the film-first branch retired): the opening passage and the
    # screener come before the film -- the order itself is `screener_order_check`'s; here the film is drawn with no
    # hand-over line, then the gate
    leg.check(run, "the film after the opening (and the screener), with no hand-over line before it (keel-web 258 "
                   "FR-2b)", first.get("kind") == "problem" and not first.get("hand") and bool(first.get("player"))
              and bool(lead) and lead[0] != "film:problem", screen="the opening -> the film", view=view,
              detail={"stage": seq[:12], "film": first}, stop=False)
    if study in ("solution", "money") and walked.get("plated"):
        # spec 162 (keel-web 260 FR-1, FR-8; its eval mirrors): on the plated link the plate hands over -- no hand-over
        # line on the idea's film, the plate's row before it
        idea = [r for r in films if r.get("kind") == "idea"]
        at = [r.get("screen") for r in walked["rows"]]
        leg.check(run, "the idea's film after the plate, with no hand-over line (keel-web 260 FR-1, FR-8)",
                  bool(idea) and not any(r.get("hand") for r in idea) and "plate" in at
                  and at.index("plate") < max(i for i, r in enumerate(walked["rows"]) if r.get("screen") == "film"
                                              and r.get("kind") == "idea"),
                  screen="the plate -> the idea's film", view=view, detail={"films": films}, stop=False)
    elif study in ("solution", "money"):
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
              and ((before.get("on") or 0) > (after.get("on") or 0) if (again.get("after") or {}).get("mode") != "pictures"
                   else before.get("shown") != after.get("shown") and after.get("shown") == c.get("first_shown")),
              screen="the film · start over", view=view,
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
    if (interview.get("gate") or {}).get("itemId"):
        leg.check(run, "after *Begin the interview*: the gate's clip is the first to play (keel-web 258 FR-2b: the "
                       "opening and the screener said before the film), and the speaker is drawn (large, as it asks)",
                  bool(plays) and first_clip == after_press.get("opening")
                  and box.get("seen") and not box.get("covered") and box.get("size") == ivs.SIZE_LARGE,
                  screen="Begin the interview -> the gate", view=view,
                  detail={"plays": plays, "gate clip": after_press.get("opening"), "speaker": box,
                          "phase": after_press.get("phase")}, stop=False)
    else:
        # the decision-maker's link (spec 164, keel-web 258 FR-2b): the problem check follows the film -- a step with
        # no clip of its own (`stepsOf`: `clip: undefined`), so nothing plays and its window opens
        leg.check(run, "after *Begin the interview*: the problem check, asked with no clip of its own (keel-web 258 "
                       "FR-2b: the opening and the screener said before the film), the speaker drawn",
                  not plays and after_press.get("phase") == "listening" and box.get("seen") and not box.get("covered"),
                  screen="Begin the interview -> the check", view=view,
                  detail={"plays": plays, "speaker": box, "phase": after_press.get("phase")}, stop=False)


def pain_hold_check(run, leg, walked: dict, interview: dict, *, view: str) -> None:
    """Spec 161 FR-3 (keel-web 257 FR-6): the link's film ends on the pain scene before *Begin* and holds it longer than
    a scene (two holds read off the page's clock); before keel-web 257 is in the checkout, pending by name."""
    if not ss.web_has_257(run.stack.keel_web):
        leg.notes.append(f"the film's pain scene held longer ({view}): pending keel-web 257 (scene.ts's `HOLD_PAIN`)")
        return
    holds = ss.film_holds(walked.get("log") or [], interview.get("story"))
    leg.check(run, "the film ends on the pain scene before *Begin the interview* and holds it longer than a scene "
                   "(keel-web 257 FR-6)", ss.held_longer(holds), screen="the film's pain scene", view=view,
              detail=holds, stop=False)


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


def answered_rows(rows: list[dict] | None) -> dict[str, int]:
    """Spec 164 FR-2: the row each item of a walk was answered on, by its dimension (`{dimension: row}`) -- the row lit
    or said (the letter's row for a letter), so the Copilot card can be walked on the same answers and owe the same
    whys."""
    out: dict[str, int] = {}
    for r in rows or []:
        key, options = r.get("key"), r.get("options") or []
        if r.get("screen") != "question" or not key or key in ("screener", "gate", "check") or not options:
            continue
        said = str(r.get("said") or "")
        if said.startswith("tap: "):
            said = said[len("tap: "):]
        for want in (r.get("want_lit"), said):
            if want and want in options:
                out[str(key)] = options.index(want)
                break
        else:
            out[str(key)] = 1 if said == LETTER else 0
    return out


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
    clips).

    Spec 161: the link's script kept for the three surfaces (FR-9); the screener before the film (FR-4) and, on the
    problem study, the five people of `three_surfaces.ROSTER` walked on the orb (FR-5, FR-7) in place of the one No
    that ended it. Then the founder's page read (FR-7, FR-8) -- spec 164: on the wire and on screen, over every
    yes-sayer the study's links were walked with. Spec 164 retired the wire-only path of a keel-web before 258."""
    from harness import interview_charge as charge    # noqa: PLC0415
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from harness import three_surfaces as ts    # noqa: PLC0415
    names = people(run, "PROBLEM")
    decider = study == "money"
    view = "orb"
    four = study == "problem"
    made = tv.send_link(run, leg, f"{study}-orb", project_id, "TEXT", person=person_at(names, 1), decider=decider)
    popup_checks(run, leg, made)
    interview, reads = read_served(run, made["url"])
    run.orb_wires[study] = {"interview": interview, "url": made["url"]}
    if not interview.get("plate"):          # spec 162: the plated link's record is `solution_view`'s (the solution's steps)
        keep_surface(run, study, "orb", ts.served_record(interview), source="the link as served (the wire)")
    wire_checks(run, leg, study, interview, view, speaker=ivs.SPEAKER_ORB, reads=reads)
    opening = ((interview.get("interviewer") or {}).get("clips") or {}).get("opening") or {}
    got = fetch_clip(run, opening.get("url"))
    leg.check(run, "the orb's opening clip is served to a stranger with no cookie (audio, FakeSpeech's)",
              got.get("status") == 200 and "audio" in str(got.get("type") or ""), screen="GET /v2/clips/{id}",
              view=f"{view} (wire)", detail=got)
    ways = list(SPEAK_OR_TAP)          # owed across the voice links (a problem link has two items with rows)
    # 1. by voice: a story told; one item by its letter, one by its words, one by tap; the film's controls and the
    # replay mark (spec 160 FR-4, FR-5) -- the walk the face's is held to (FR-3)
    walked = walk_link(run, made["url"], interview, shot=f"orb-{study}-done", speak_or_tap=ways, film_checks=True,
                       replay=True)
    steps = speaker_walk(run, study, ivs.SPEAKER_ORB, walked)
    run.__dict__.setdefault("orb_rows", {})[study] = answered_rows(walked["rows"])
    run.__dict__.setdefault("study_walks", {}).setdefault(study, []).append(
        {"url": made["url"], "interview": interview, "sent": first_response(walked).get("sent") or {},
         "invitation": made_invitation(made)})
    run.orbs.append({"study": study, "link": "voice", **summary(walked)})
    orb_screen_checks(run, leg, walked, interview, view=view, label="by voice")
    retired_checks(run, leg, walked, view=view, label="by voice")
    film_first_checks(run, leg, walked, view=view, study=study)
    film_checks(run, leg, walked, interview, view=view)
    pain_hold_check(run, leg, walked, interview, view=view)
    replay_checks(run, leg, walked, view=view)
    last_page_checks(run, leg, walked, interview, view=view)
    chip_checks(run, leg, walked, view=view, speaker=ivs.SPEAKER_ORB)
    screener_order_check(run, leg, walked, interview, view=view)
    leg.notes.append(f"the orb's walk ({study}): {len(steps)} steps -- " + " > ".join(s_["step"] for s_ in steps)[:600])
    orb_states_check(run, leg, walked, view=view)
    no_typed_box_check(run, leg, walked, view=view, label="by voice")
    sent = first_response(walked)
    leg.check(run, "the answers are sent (201), named TEXT (the format the link was served), and the thank-you drawn",
              sent.get("status") == 201 and (sent.get("sent") or {}).get("format") == "TEXT" and bool(walked["done"]),
              screen="the last question -> the thank-you", view=view,
              detail={"status": sent.get("status"), "format": (sent.get("sent") or {}).get("format"),
                      "answers": len((sent.get("sent") or {}).get("answers") or []), "done": walked["done"]})
    keep_surface(run, study, "orb", ts.walked_record(walked["rows"]), source="the orb's walk (keel-web 258)")
    said: dict = {"rows": []}
    if study != "money" and not interview.get("plate"):
        # the decision-maker's link has no gate and no story; spec 162: nor is a story asked on the plated solution link
        story_rows = [r for r in walked["rows"] if r.get("story")]
        if story_rows:
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
    speak_or_tap_checks(run, leg, walked["rows"] + said["rows"], view=view, study=study)
    # 3. the microphone refused: the block, nothing starts; allowed again, Start (spec 160 FR-2)
    block_link = tv.send_link(run, leg, f"{study}-orb-block", project_id, "TEXT", person=person_at(names, 9),
                              decider=decider)
    blocked = blocked_walk(run, block_link["url"], shot=f"orb-{study}-blocked")
    run.orbs.append({"study": study, "link": "the microphone refused", "block": block_line(blocked)})
    blocked_checks(run, leg, blocked, view=f"{view} · refused")
    if four:
        # spec 161 FR-5, FR-7: the five people (the No goes on); the screener's No; then the founder's page
        roster = roster_on_screen(run, leg, project_id, speaker=ivs.SPEAKER_ORB)
        founder_page_on_the_wire(run, leg, project_id, roster)
    else:
        # 4. the No that ends it (a solution or money link: the gate is the anchor alone, spec 269 FR-2)
        no_on = "check" if decider else "gate"
        no_link = tv.send_link(run, leg, f"{study}-orb-no", project_id, "TEXT", person=person_at(names, 2),
                               decider=decider)
        no_wire, _ = read_served(run, no_link["url"])
        no_walk = walk_link(run, no_link["url"], no_wire, shot=f"orb-{study}-no", no_on=no_on)
        asked = [r["question"] for r in no_walk["rows"] if r["screen"] == "question"]
        sent = first_response(no_walk).get("sent") or {}
        what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
        leg.check(run, f"a No on the {what} still ends the interview in the orb view (`exitText`; keel-cloud 269 FR-2: "
                       "the anchor alone): no question after it, the response a No alone",
                  bool(no_walk["responses"]) and sent.get("recency") is False and not (sent.get("answers") or []),
                  screen=f"the {what} -> the end", view=view,
                  detail={"asked": asked, "responses": no_walk["responses"], "done": no_walk["done"]})
    phone_film(run, leg, study, project_id, person_at(names, 7))
    if not run.remote and run.account_id:
        from stack import ledger    # noqa: PLC0415
        rows = [r for r in ledger.rows(run.stack, run.account_id, since=run.ledger_since)
                if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
        faults = charge.orb_charge_faults(rows)
        leg.check(run, "the orb's clips bought nothing: every CARD_SPEECH row 0 credits, no charge but the lock's "
                       "PROJECT and the face's INTERVIEWER_RECORDING (InferenceCharge 21: STORY_TURN and "
                       "EXPERIENCE_WAYS priced 0)", not faults,
                  screen="the ledger", view="wire",
                  detail={"faults": faults, "CARD_SPEECH rows": len(charge.card_speech_rows(rows)),
                          "charges": [(r.get("action"), r.get("credits")) for r in rows if int(r.get("credits") or 0) < 0]})
        free = charge.free_reading_faults(rows)
        leg.check(run, "the story's turns and the ways' reading bought nothing: every STORY_TURN and EXPERIENCE_WAYS row "
                       "on the ledger 0 credits (spec 161 FR-11)", not free, screen="the ledger", view="wire",
                  detail={"faults": free, "rows": charge.reading_rows(rows)}, stop=False)


def screener_order_check(run, leg, walked: dict, interview: dict, *, view: str) -> None:
    """Spec 161 FR-4 (keel-web 258 FR-2b): on a film link the opening passage, the screener (its own step), the film,
    *Begin*, then the gate; a link without a screener: the opening, the film, the gate."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    gate = interview.get("gate") or {}
    if not gate or not interview.get("story"):
        return
    screener = bool((gate.get("condition") or {}).get("question"))
    labelled = []
    for r in walked.get("rows") or []:
        if r.get("screen") == "film" and r.get("kind") == "problem":
            labelled.append("film:problem")
        elif r.get("key") in ("screener", "gate"):
            labelled.append(r["key"])
    steps = [s.get("step") for s in ss.walk_steps(walked.get("log") or [])]
    order = (["speaking:opening"] if steps and str(steps[0]).startswith(("intro", "speaking")) else []) + labelled
    v = ts.screener_first(order, screener=screener)
    leg.check(run, "the order on the film link: the opening, the screener (its own step), the film, *Begin*, then the "
                   "gate (keel-web 258 FR-2b)" if screener else "the order on a film link without a screener: the "
                   "opening, the film, the gate", v["ok"], screen="the link's order", view=view,
              detail={"verdict": v, "steps": steps[:20]}, stop=False)


def roster_on_screen(run, leg, project_id: str, *, speaker: str, fmt: str = "TEXT", only_no: bool = False) -> dict:
    """Spec 161 FR-5, FR-7 on keel-web 258's screens: the problem study's people of `three_surfaces.ROSTER` walked on
    the speaker -- each why answered in words, the No-sayer's walk the No, the Prevalence why on the spot, Importance,
    the pilot ask and the thanks -- and the stranger whose screener No leaves before the film. `only_no`: the No-sayer
    alone (the face's). The roster's record as `roster_on_the_wire` keeps it."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    view = "orb" if speaker == "ORB" else "avatar"
    run.load_runtime("PROBLEM", extra={"INTERPRET": [ts.ANCHORED] * 12})      # the stories read ANCHORED (as above)
    own, tasks, act = owner_row_and_tasks(run, project_id)
    people_ = [p for p in ts.ROSTER if not only_no or not p["gate"]]
    names = [f"Stranger {run.stamp} {view} {i}" for i in range(1, len(people_) + (1 if not only_no else 0) + 1)]
    links = make_links(run, project_id, names, fmt=fmt)
    out: dict = {"people": [], "picks": [], "stories": [], "said": {}, "own": own, "tasks": tasks, "act": act}
    yes_stories = iter(ts.STORIES)
    for person, link in zip(people_, links):
        plan = dict(person, own_label=own, other_tasks=tasks)
        if person["gate"]:
            plan["story"] = next(yes_stories)
        interview, _ = read_served(run, link["url"])
        walked = walk_link(run, link["url"], interview, shot=f"{view}-161-{person['who'][:12]}", plan=plan)
        sent = first_response(walked)
        body = sent.get("sent") or {}
        whys = [r["follow_up"] for r in walked["rows"] if r.get("follow_up")]
        got = [w["dimension"] for w in whys]
        leg.check(run, f"{person['who']} on the {view}: owed {', '.join(person['owed'])} -- each why asked "
                       f"({', '.join(got) or 'none'}) and answered in words, the response taken (201)",
                  got == person["owed"] and sent.get("status") == 201
                  and [f.get("dimension") for f in body.get("followUps") or []] == person["owed"],
                  screen="the four questions", view=view,
                  detail={"whys": whys, "status": sent.get("status"), "rows": [(r.get("key"), r.get("question"),
                                                                                r.get("said")) for r in walked["rows"]
                                                                               if r.get("screen") == "question"]},
                  stop=False)
        if not person["gate"]:
            keys = [r.get("key") or ("why" if r.get("follow_up") else r.get("where"))
                    for r in walked["rows"] if r.get("screen") == "question"]
            after = keys[keys.index("gate") + 1:] if "gate" in keys else []
            leg.check(run, f"a No goes on ({view}): the No, the Prevalence why on the spot, Importance, the pilot ask, "
                           "the thanks; the response `recency: false`, no story, no Frequency, the Importance pick, one "
                           "why", after[:2] == ["why", ts.IMPORTANCE] and bool(walked.get("done"))
                      and body.get("recency") is False and "story" not in body and len(body.get("answers") or []) == 1
                      and len(body.get("followUps") or []) == 1, screen="the No path", view=view,
                      detail={"after the No": after, "sent": body, "done": walked.get("done")}, stop=False)
        else:
            out["picks"].append(person["frequency"])
            out["stories"].append((link.get("invitationId"), plan["story"]))
        for w in whys:
            out["said"].setdefault(w["dimension"], []).append(ts.why_said(w))
        out["people"].append({"who": person["who"], "owed": person["owed"], "whys": got,
                              "status": sent.get("status"), "invitation": link.get("invitationId")})
    if not only_no and len(links) > len(people_):
        screened = links[len(people_)]
        interview, _ = read_served(run, screened["url"])
        walked = walk_link(run, screened["url"], interview, shot=f"{view}-161-screened", plan={"screener": "no",
                                                                                               "gate": True})
        films = [r for r in walked["rows"] if r.get("screen") == "film"]
        body = first_response(walked).get("sent") or {}
        leg.check(run, f"the screener's No leaves before the film ({view}): no film drawn, `outsideSegment: true` alone, "
                       "the thanks", not films and body.get("outsideSegment") is True and bool(walked.get("done")),
                  screen="the screener's No", view=view, detail={"films": films, "sent": body}, stop=False)
    run.__dict__.setdefault("roster", {})["problem" if not only_no else "problem-face"] = out
    return out


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
    and the film read while it plays -- no text on the drawing, it fits, the spoken line at most three rows. Since
    keel-web 258 FR-2b (spec 164) the opening and the screener come first: the screener is answered *yes* on the way."""
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
            film = page.locator(ORB_FILM_PLAYER).first
            deadline = time.monotonic() + 60 * p.patience
            answered: set = set()
            while time.monotonic() < deadline and not film.is_visible():
                # keel-web 258 FR-2b: the opening, then the screener on a step of its own -- *yes* -- then the film
                if p.phase() == "listening" and p.recorder()["live"]:
                    q = p.sheet().get("question")
                    if q and q not in answered:
                        answered.add(q)
                        p.say("yes")
                page.wait_for_timeout(300)
            film.wait_for(state="visible", timeout=5_000)
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
                if study == "solution":
                    # spec 162: the solution study on the wire every run (keel-cloud 272); its screens are keel-web 260's
                    solution_view(run, leg, view, project)
                    if not ss.web_has_260(run.stack.keel_web):
                        return
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
    """The face's links (159 FR-2, 160 FR-1 to FR-6). Spec 161: the link's script kept for the three surfaces (FR-9); on
    keel-web 258 the problem study's No-sayer walked on the face too (FR-5: the No goes on)."""
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from harness import three_surfaces as ts    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    if run.remote:
        leg.status, leg.why = "skipped", "remote profile: the AI interviewer is bought on Keel's door (a stand-in here)"
        return
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == tv.vs.LINK_B2B) == (study == "money")), kinds[0])
    names = people(run, "PROBLEM")
    four = study == "problem"
    try:
        interviewer_ready(run, leg, study, project_id, kind.get("label"))
        made = tv.send_link(run, leg, f"{study}-avatar", project_id, "AI_INTERVIEWER", person=person_at(names, 3),
                            decider=study == "money")
        interview, reads = read_served(run, made["url"])
        if not interview.get("plate"):      # spec 162: the plated link's record is `solution_view`'s
            keep_surface(run, study, "face", ts.served_record(interview), source="the link as served (the wire)")
        wire_checks(run, leg, study, interview, "avatar", speaker=ivs.SPEAKER_AVATAR, reads=reads)
        same_words(run, leg, study, project_id, kind.get("roleId"), interview)
        # spec 160 FR-3: walked as the orb's voice link was -- the same ways from the start, the film's controls,
        # the replay mark on the first item -- so the two walks can be held equal step for step
        walked = walk_link(run, made["url"], interview, shot=f"avatar-{study}-done",
                           speak_or_tap=list(SPEAK_OR_TAP), film_checks=True, replay=True)
        steps = speaker_walk(run, study, ivs.SPEAKER_AVATAR, walked)
        keep_surface(run, study, "face", ts.walked_record(walked["rows"]), source="the face's walk (keel-web 258)")
        leg.notes.append(f"the face's walk ({study}): {len(steps)} steps -- "
                         + " > ".join(s_["step"] for s_ in steps)[:600])
        run.orbs.append({"study": study, "link": "the face", **summary(walked)})
        rows = walked["rows"]
        films = [r for r in rows if r["screen"] == "film"]
        name = ((interview.get("interviewer") or {}).get("face") or {}).get("name") or FACE.title()
        intro_checks(run, leg, walked, interview, view="avatar", label="the face", speaker=ivs.SPEAKER_AVATAR,
                     name=name)
        retired_checks(run, leg, walked, view="avatar", label="the face")
        film_first_checks(run, leg, walked, view="avatar", study=study)
        film_checks(run, leg, walked, interview, view="avatar")
        pain_hold_check(run, leg, walked, interview, view="avatar")
        replay_checks(run, leg, walked, view="avatar")
        last_page_checks(run, leg, walked, interview, view="avatar")
        chip_checks(run, leg, walked, view="avatar", speaker=ivs.SPEAKER_AVATAR, name=name)
        screener_order_check(run, leg, walked, interview, view="avatar")
        same_walk_check(run, leg, study, view="avatar")
        leg.check(run, "Daphne returns after the film and each hand-over: the story gone, her face on the stage",
                  bool(films) and all((h.get("returned") or {}).get("story_gone")
                                      and (h.get("returned") or {}).get("face") for h in films),
                  screen="the stage after the film", view="avatar", detail=[h.get("returned") for h in films])
        questions = [r for r in rows if r["screen"] == "question"]
        leg.check(run, "the face asks on the stage (`data-speaker` AVATAR, her `<video>`)",
                  bool(questions) and all(r.get("speaker") == ivs.SPEAKER_AVATAR for r in questions),
                  screen="every question", view="avatar",
                  detail={"speakers": sorted({str(r.get('speaker')) for r in questions})})
        items = [r for r in questions if r.get("step") == "item"
                 and not str(r.get("where") or "").startswith("Question 1 ")]
        backless = [r["question"] for r in items if not r["back"]]
        leg.check(run, "*Back to question n* on every question card after the first (the screener, the gate, its "
                       "story and the check are the link's opening)", bool(items) and not backless,
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
        if four:
            # spec 161 FR-5: the No-sayer on the face too -- the No goes on
            roster_on_screen(run, leg, project_id, speaker=ivs.SPEAKER_AVATAR, fmt="AI_INTERVIEWER", only_no=True)
        else:
            no_made = tv.send_link(run, leg, f"{study}-avatar-no", project_id, "AI_INTERVIEWER",
                                   person=person_at(names, 4), decider=study == "money")
            no_interview, _ = read_served(run, no_made["url"])
            no_walk = walk_link(run, no_made["url"], no_interview, shot=f"avatar-{study}-no",
                                no_on="check" if study == "money" else "gate")
            asked = [r["question"] for r in no_walk["rows"] if r["screen"] == "question"]
            sent = first_response(no_walk).get("sent") or {}
            what = {"problem": "gate", "solution": "anchor", "money": "third-person check"}[study]
            leg.check(run, f"a No on the {what} still ends the interview in the avatar view: no question after it",
                      bool(no_walk["responses"]) and sent.get("recency") is False and not (sent.get("answers") or []),
                      screen=f"the {what} -> the end", view="avatar",
                      detail={"asked": asked, "responses": no_walk["responses"], "done": no_walk["done"]})
    finally:
        ledger.restore_own_door(run.stack, run.account_id, f"{study}-avatar-restore-{run.stamp}", spec=tv.STAND_IN_SPEC)


# ------------------------------------------------------------------------------------------------ copilot

def still_of(page) -> dict:
    """Spec 167 FR-2 (keel-web 263 FR-4, judgement call 9): the strip's still as drawn -- its ratio (`data-ratio`, read
    off its picture: `portrait` 80 x 120 on a 275 build, `landscape` on a film before 275 or FakePictures' 48 x 32) and
    its box; none where the strip carries no still (a line whose scene was left out has no frame)."""
    try:
        return page.evaluate("""() => {
          const el = document.querySelector('[data-testid=copilot-still]');
          if (!el) return { still_ratio: null, still_box: null };
          const r = el.getBoundingClientRect();
          return { still_ratio: el.getAttribute('data-ratio'), still_box: [Math.round(r.width), Math.round(r.height)] };
        }""")
    except Exception:  # noqa: BLE001 - a read under a re-render
        return {"still_ratio": None, "still_box": None}


def copilot_walk(run, page, call: dict, *, no_on: str | None = None, script: dict | None = None,
                 check: str | None = None, picks: dict | None = None) -> dict:
    """The copilot card headless (spec 154's fake sources): the set-up steps by their own buttons (the Meet ticked, the
    mic opened on its step, the tab shared, the sign-in skipped, Start), then each strip by the card's own buttons --
    the screener's Yes, *Show the story* (the window grown, measured, shrunk), the gate's *Story again* (grown again)
    then Yes (or the No), each question's first answer, the idea's story where offered, the stretches stopped -- and
    End, the call's own recording sent.

    Spec 164 FR-2: each strip is read as the card's passage it draws (`three_surfaces.card_passages` over the call's
    `script`, `check` the decision-maker's check the route words) -- its kind and item, its bubbles' words and badges,
    a follow-up's words -- and each pick is kept (`filed`: the passage's option ids, in the order filed) so the card's
    own follow-ups can be held to its machine (`three_surfaces.card_follow_ups`). `picks` (`{dimension: row}`): the row
    each item is answered on (the orb's walk's), else the first."""
    from evals import calls_leg    # noqa: PLC0415
    from harness import three_surfaces as ts    # noqa: PLC0415
    passages = ts.card_passages(script, check=check) if script else []
    picks = dict(picks or {})
    filed: list = []
    ladder_passage: dict | None = None
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
                           "read": ss._tc(page.locator("[data-testid=read]"))[:200],
                           "still": page.get_by_test_id("copilot-still").count(), **still_of(page)})
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
        card_root = page.locator(calls_leg.COPILOT_CARD).first
        passage = ts.passage_of(read, passages) if phase == "reading" else None
        if passage is None and phase == "reading" and passages and not any(x["kind"] == "gate" for x in passages) \
                and page.get_by_test_id("story-again").count():
            # the decision-maker's check: the route words it (the script serves none) -- on a script with no gate it is
            # the one question strip that carries the story's press (keel-web 243 FR-2, `withCheck`)
            passage = {"kind": "check", "itemId": "problemCheck", "dimension": None}
        strip = {"phase": phase, "head": head, "read": read[:200],
                 # the question's anchor, drawn apart above its stem (`.cpl-anchor`): the card says both
                 "anchor": ss._tc(card_root.locator(".cpl-anchor")) or None,
                 "still": page.get_by_test_id("copilot-still").count(), **still_of(page),
                 "show_story": page.get_by_test_id("show-story").count(),
                 "story_again": page.get_by_test_id("story-again").count(),
                 "idea_story": page.get_by_test_id("show-idea-story").count(),
                 "screener": card_root.get_attribute("data-screener"),
                 "question": card_root.get_attribute("data-question"),
                 # spec 164 FR-2: the strip read as its passage -- the kind and the item, never its place
                 "passage_kind": (passage or {}).get("kind"), "passage_item": (passage or {}).get("itemId"),
                 "passage_dimension": (passage or {}).get("dimension"),
                 "options": ss._texts(card_root.locator(".cpl-bubble__w")),
                 "badges": ss._texts(card_root.locator(".cpl-bubble__let"))}
        if passage and passage.get("twoSteps"):
            strip["ladder"] = ts._card_labels(passage)
            ladder_passage = passage
        if (read, head) != last:
            strips.append(strip)
            last = (read, head)
        if strip["story_again"] and not any(g["press"] == "story-again" for g in grows):
            grow("story-again")
            continue
        if strip["idea_story"] and not any(g["press"] == "show-idea-story" for g in grows):
            grow("show-idea-story")
            continue
        gate_strip = bool(strip["story_again"]) if not passage else passage.get("kind") == "gate"
        if gate_strip and no_on == "gate" and enabled("opt-2") is not None:
            if passage:
                filed.append((passage.get("itemId"), _option_ids(passage, [1])))
            enabled("opt-2").click()
            page.wait_for_timeout(600)
            continue
        answers = page.locator("[data-testid=as-the-interview], [data-testid=as-the-condition]")
        row = int(picks.get(str((passage or {}).get("dimension")), 0)) if passage and passage.get("kind") == "item" else 0
        if enabled("opt-1") is not None:
            if passage and passage.get("kind") in ("gate", "pilot"):
                filed.append((passage.get("itemId"), _option_ids(passage, [0])))
            enabled("opt-1").click()
        elif answers.locator("label.cpl-bubble").count():
            bubbles = answers.locator("label.cpl-bubble")
            at = 1 if (no_on == "check" and "have this problem" in read) else min(row, bubbles.count() - 1)
            if passage and passage.get("kind") == "item" and not passage.get("twoSteps"):
                filed.append((passage.get("itemId"), _option_ids(passage, [at])))
            elif phase == "second-step" and ladder_passage:
                # a ladder's second step files its own option (the side the first band opened)
                drawn = [ts._words(o) for o in strip["options"]]
                for side in ("under", "over"):
                    rows = ((ladder_passage.get("twoSteps") or {}).get(side) or {}).get("options") or []
                    if [ts._words(o.get("label")) for o in rows] == drawn:
                        filed.append((ladder_passage.get("itemId"), _option_ids({"options": rows}, [at])))
                        break
            bubbles.nth(at).click()
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
    return {"strips": strips, "grows": grows, "end_phase": end_phase, "phase": card.phase(), "filed": filed,
            "passages": passages}


def _option_ids(passage: dict, rows: list[int]) -> list[str]:
    """The option ids a passage files for the rows picked (by their place in the passage's options)."""
    options = passage.get("options") or []
    return [str(options[i].get("optionId")) for i in rows if 0 <= i < len(options) and options[i].get("optionId")]


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
    """The Copilot card's two calls (241 FR-9, 242 FR-4): a yes walk and a No. Spec 164 FR-2: each strip read as the
    card's passage (its kind and item), the yes walk answered on the orb's rows (`answered_rows`) so the card owes the
    whys the orb owed, the card's follow-ups held to its machine (`three_surfaces.card_follow_ups`, mirror 7), the
    bubbles' badges (Frequency's digits, mirror 6), and the card's walked record kept for the three surfaces."""
    from evals import calls_leg    # noqa: PLC0415
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == tv.vs.LINK_B2B) == (study == "money")), kinds[0])
    names = people(run, "PROBLEM")
    from harness import three_surfaces as ts    # noqa: PLC0415
    results = {}
    first_person(run, leg, project_id)
    for which, person, no_on in (("yes", names[5], None), ("no", names[6], "check" if study == "money" else "gate")):
        status, call = run.call("POST", f"/v2/projects/{project_id}/calls", {"roleId": kind.get("roleId"),
                                                                             "name": person})
        leg.check(run, f"a call planned with {person} (POST calls 201, the copilot's path)",
                  status == 201 and bool((call or {}).get("copilotPath")), screen="Sent · Calls with me",
                  view="copilot", detail=call)
        script = card_script(run, project_id, call or {})
        if which == "yes":
            # spec 161 FR-9: the card's script, kept for the three surfaces
            if not any(p.get("kind") == "plate" for p in script.get("passages") or []):
                keep_surface(run, study, "card", ts.card_record(script), source="the call's script (the wire)")
        page = run.context.new_page()
        try:
            page.add_init_script(calls_leg.FAKE_MEDIA)
            page.add_init_script(calls_leg.UPLOAD_SEAM)
            results[which] = copilot_walk(run, page, call, no_on=no_on, script=script,
                                          picks=(run.__dict__.get("orb_rows") or {}).get(study) if which == "yes"
                                          else None)
            ss._BrowserStep(run.recorder, page, "founder").screenshot(f"copilot-{study}-{which}")
        finally:
            page.close()
    walked = results["yes"]
    grows = walked["grows"]
    presses = [g["press"] for g in grows]
    # keel-web 241 FR-9 / 242 FR-4 / 243 judgement call 12: the screener's *Show the story* then the gate's *Story
    # again*; the decision-maker's call has no screener, its check strip carries the story's press (`story-again`); the
    # idea's story after the idea where the study holds one
    plated = any(p.get("kind") == "plate" for p in walked.get("passages") or [])
    # spec 162 (keel-web 260 FR-5): on the plated card the idea film is its lines, read one at a time -- no grown idea film
    want = (["story-again"] if study == "money" else ["show-story", "story-again"]) + \
        (["show-idea-story"] if study in ("solution", "money") and not plated else [])
    leg.check(run, f"the story moments in order: {', '.join(want)}", presses == want, screen="the strips",
              view="copilot", detail={"grows": presses, "strips": [(s.get("head"), s.get("read", "")[:50])
                                                                  for s in walked["strips"]]})
    vp = (grows[0]["viewport"] if grows else {"width": 1280, "height": 720})
    half = vp["width"] * vp["height"] / 2
    small = [g for g in grows if (g["box"].get("width") or 0) * (g["box"].get("height") or 0) >= half]
    leg.check(run, "the grown window is under half the viewport, the card still drawn, the player playing",
              bool(grows) and not small and all(g["card_shown"] and g["player"] for g in grows),
              screen="the grown window", view="copilot", detail=grows)
    # spec 162 (keel-web 260 FR-5): on the plated card the problem film's lines stand between the screener and the check,
    # so the check's own *Story again* is the grow that returns to it
    back = [g for g in grows if g["press"] == "story-again"][:1] if plated else grows[:1]
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
    # spec 167 FR-2 (keel-web 263 FR-4): the still takes its picture's ratio -- portrait 80 x 120 on a 275 build,
    # landscape on a film before 275 or FakePictures' 48 x 32: recorded, the picture decides
    leg.notes.append(f"the copilot's stills as drawn: ratios {sorted({str(s.get('still_ratio')) for s in problem_strips})}"
                     f", boxes {sorted({tuple(s.get('still_box') or ()) for s in problem_strips})}")
    leg.check(run, "the call ends and its recording is sent (the card done)", walked["phase"] in ("done", "sent"),
              screen="End -> the upload", view="copilot", detail={"phase": walked["phase"], "end": walked["end_phase"]})
    no = results["no"]
    gate_at = next((i for i, s in enumerate(no["strips"]) if s.get("story_again")), None)
    asked_after = [s for s in (no["strips"][gate_at + 1:] if gate_at is not None else no["strips"])
                   if s.get("phase") in ("reading", "follow-up") and not s.get("story_again")]
    if study == "problem":
        # spec 161 FR-5 (keel-web 258 FR-5): on the problem study the No goes on -- the Prevalence why, then Importance
        after = [s.get("phase") for s in asked_after]
        leg.check(run, "a No on the gate in the copilot view goes on: the Prevalence why, then Importance, nothing "
                       "else (keel-web 258 FR-5)", after[:2] == ["follow-up", "reading"] and len(after) == 2,
                  screen="the gate's strip -> the why -> Importance", view="copilot", stop=False,
                  detail={"end": no["end_phase"], "after": [(s["phase"], s["head"], s.get("read", "")[:60])
                                                            for s in asked_after]})
    else:
        leg.check(run, "a No on the gate in the copilot view ends the questions (no item strip after it)",
                  not asked_after,
                  screen="the gate's strip -> the end", view="copilot", stop=False,
                  detail={"end": no["end_phase"], "after": [(s["head"], s.get("read", "")[:60]) for s in asked_after]})
    card_machine_checks(run, leg, study, walked, no)
    keep_surface(run, study, "card", ts.strips_record(walked["strips"]), source="the card's walk (keel-web 258)")
    if plated:
        # spec 162 FR-9: the plated study's three surfaces are `solution_surfaces_check`'s (held in `solution_view`)
        leg.notes.append("the solution study's three surfaces: held by `solution_surfaces_check` on its own steps")
    else:
        three_surfaces_check(run, leg, study)


def card_machine_checks(run, leg, study: str, walked: dict, no: dict) -> None:
    """Spec 164 mirrors 6 and 7 on the Copilot card's two walks (keel-web 258 FR-5): every question strip read as its
    passage; the follow-ups the card opened are its machine's for the picks filed (two a call, the rung's or the second
    stem's hint, the gate's on a No where it carries one); after a No on a gate with a follow-up, the why and Importance
    alone; the bubbles' badges -- Frequency's the digits 1-5, every other question's letters."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    questions = [s for s in walked["strips"] if s.get("phase") == "reading" and (s.get("question") or s.get("story_again")
                                                                                 or s.get("show_story"))]
    unread = [(s.get("head"), str(s.get("read") or "")[:60]) for s in questions if not s.get("passage_kind")]
    leg.check(run, "every question strip on the card is read as its passage -- the kind and the item (spec 164 FR-2)",
              bool(questions) and not unread, screen="the strips", view="copilot", stop=False,
              detail={"unread": unread, "read": [(s.get("passage_kind"), s.get("passage_dimension"),
                                                  str(s.get("read") or "")[:50]) for s in questions]})
    for name, walk in (("the yes", walked), ("the No", no)):
        want = [ts._words(f.get("hint")) for f in ts.card_follow_ups(walk.get("passages") or [], walk.get("filed") or [])]
        got = [ts._words(s.get("read")) for s in walk["strips"] if s.get("phase") == "follow-up"]
        leg.check(run, f"{name} call: the card opens the follow-ups its machine owes the picks filed -- at most two, the "
                       "rung's hint or Frequency's second stem's, the gate's on a No (keel-web 258 FR-5)", got == want,
                  screen="the follow-up strips", view="copilot", stop=False,
                  detail={"opened": got, "machine": want, "filed": walk.get("filed")})
    if study == "problem":
        passages = no.get("passages") or []
        gate_at = next((i for i, s in enumerate(no["strips"]) if s.get("passage_kind") == "gate"), None)
        after = [ts.strip_step(s) for s in (no["strips"][gate_at + 1:] if gate_at is not None else [])
                 if s.get("phase") in ("reading", "follow-up")]
        after = [a for a in after if a]
        want = [x for x in ts.card_no_path(passages) if x not in ("pilot", "screened")]
        leg.check(run, "after the gate's No the card asks its machine's No path by passage: the gate's follow-up, then "
                       "Importance alone (keel-web 258 FR-5)", after == want, screen="the No path (by passage)",
                  view="copilot", stop=False, detail={"asked": after, "machine": want})
    faults = ts.badge_faults(walked["strips"])
    leg.check(run, "the bubbles' badges: Frequency's five the digits 1-5, every other question's letters (keel-web 258 "
                   "FR-5)", not faults, screen="the strips' bubbles", view="copilot", stop=False,
              detail={"faults": faults, "badges": [(s.get("passage_dimension") or s.get("passage_kind"), s.get("badges"))
                                                   for s in walked["strips"] if s.get("badges")]})


# ================================================================================ spec 161: the four questions
# keel-cloud 269 / 270 (contract 87), keel-web 258. The gate's fixed words, a No that goes on, Frequency's five rows,
# every why; the founder's page on bands, the ways, no Current solution; the orb, the face and the Copilot card held to
# one script. The stranger's screens are walked to keel-web 258 (spec 164: the wire-only path of a keel-web before it is
# retired); the cloud's side is read on the wire every time (`harness/three_surfaces.py`), the founder's page on screen too.

def make_links(run, project_id: str, names: list[str], *, fmt: str = "TEXT", decider: bool = False) -> list[dict]:
    """Links made on the wire (`POST invitations/batch`, Send more's last step): one a person, the kind's, `fmt`."""
    register = run.get(f"/v2/projects/{project_id}/invitations") or {}
    kinds = register.get("kinds") or []
    kind = next((k for k in kinds if (k.get("respondentType") == tv.vs.LINK_B2B) == decider), kinds[0] if kinds else {})
    revision = (run.get(f"/v2/projects/{project_id}/overview") or {}).get("revision")
    status, body = run.call("POST", f"/v2/projects/{project_id}/invitations/batch",
                            {"expectedRevision": revision, "respondentType": kind.get("respondentType") or "PRIMARY",
                             "format": fmt, "people": [{"personName": n} for n in names]})
    if status != 201:
        raise tv.LegFailed(f"invitations/batch {status}: {json.dumps(body, default=str)[:400]}")
    links = list((body or {}).get("links") or (body or {}).get("made") or [])
    run.findings.extend({"link": "161 wire", "person": l.get("personName"), "url": l.get("url")} for l in links)
    return links


def token_of(url: str) -> str:
    return url.rstrip("/").split("/")[-1].split("?")[0]


def stranger_call(run, method: str, path: str, body: dict | None = None) -> tuple[int, dict | None]:
    """A stranger's request (no cookie): the interview routes are open to the token alone."""
    stranger = run.browser.new_context()
    try:
        kw: dict = {"timeout": 20_000}
        if body is not None:
            kw["data"] = json.dumps(body)
            kw["headers"] = {"Content-Type": "application/json"}
        r = stranger.request.fetch(f"{run.cloud}{path}", method=method, **kw)
        try:
            payload = r.json()
        except Exception:  # noqa: BLE001 - an empty body (204)
            payload = None
        return r.status, payload if isinstance(payload, dict) else None
    finally:
        stranger.close()


def owner_row_and_tasks(run, project_id: str) -> tuple[str | None, list[str], str | None]:
    """The Importance rows' own row (the review's first, written at the yes), the story's other tasks, its act."""
    from harness import vectors_screens as vs_screens    # noqa: PLC0415
    review = run.get(f"/v2/projects/{project_id}/review/PROBLEM") or {}
    rows = vs_screens.written_beliefs(review)["importance"]
    story = run.get(f"/v2/projects/{project_id}/story") or {}
    return (rows[0] if rows else None), list(story.get("otherTasks") or []), story.get("act")


def four_questions_served(run, leg, interview: dict, *, view: str, other_tasks: list[str], own: str | None) -> None:
    """Spec 161 FR-4 / FR-6 on the wire (keel-cloud 269): the problem link's four -- the gate's fixed words, Frequency
    `fixed_five` (the five in order, no escape), Importance the story's other tasks and the own row, no Current
    solution item."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    gate = interview.get("gate") or {}
    leg.check(run, f"the gate on a film link asks exactly *{ts.GATE_WORDS}* (no window phrase; keel-cloud 269 FR-1)",
              gate.get("question") == ts.GATE_WORDS and bool(interview.get("story")), screen="the gate", view=view,
              detail={"question": gate.get("question"), "noLabel": gate.get("noLabel")}, stop=False)
    freq = ts.item_of(interview, ts.FREQUENCY)
    leg.check(run, "Frequency is `fixed_five` -- *Every time*, *Most times*, *About half the time*, *Now and then*, "
                   "*Never*, in order, no escape (keel-cloud 269 FR-3)",
              freq.get("control") == "fixed_five" and [o.get("label") for o in freq.get("options") or []]
              == list(ts.FREQUENCY_LABELS) and not freq.get("escape"), screen="Frequency", view=view,
              detail={k: freq.get(k) for k in ("control", "question", "escape")}
              | {"options": [o.get("label") for o in freq.get("options") or []]}, stop=False)
    imp = ts.item_of(interview, ts.IMPORTANCE)
    rows = [o.get("label") for o in imp.get("options") or []]
    leg.check(run, "Importance's rows are the story's other tasks and the own row, the own never first, *None of "
                   "these* its escape (keel-cloud 269 FR-4)",
              {ts._bare(r) for r in rows} >= {ts._bare(t) for t in other_tasks} and len(rows) == len(other_tasks) + 1
              and (own is None or ts._bare(rows[0]) != ts._bare(own))
              and ((imp.get("escape") or {}).get("code") == "NONE_OF_THESE"), screen="Importance", view=view,
              detail={"rows": rows, "otherTasks": other_tasks, "own": own, "question": imp.get("question"),
                      "escape": imp.get("escape")}, stop=False)
    leg.check(run, "no Current solution item on the link (keel-cloud 269 FR-5)",
              not ts.item_of(interview, ts.CURRENT_SOLUTION) and not ts.current_solution_anywhere(interview),
              screen="the link's items", view=view, detail=ts.current_solution_anywhere(interview), stop=False)


def walk_whys_on_the_wire(run, token: str, person: dict, interview: dict, *, other_tasks: list[str],
                          own: str | None) -> list[dict]:
    """keel-cloud 270 FR-2 as the page calls it: the follow-up route after the gate's No (on the spot), after
    Frequency's answer, and at the end with every answer -- each time with the rungs already asked -- until 204 or two
    are asked. Returns each why served, in order (`{dimension, text, at}`)."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    answers = ts.answers_for(person, interview, other_tasks=other_tasks, own_label=own)
    asked: list[dict] = []
    path = f"/v2/i/{token}/interview/follow-up"

    def ask(so_far: list[dict], at: str) -> bool:
        if len(asked) >= ts.MAX_FOLLOW_UPS:
            return False
        status, body = stranger_call(run, "POST", path, {"answers": so_far, "recency": bool(person["gate"]),
                                                         "asked": [a["dimension"] for a in asked]})
        if status == 200 and body:
            asked.append({"dimension": body.get("dimension"), "text": body.get("text"), "spoken": body.get("spoken"),
                          "at": at})
            return True
        return False
    if not person["gate"]:
        ask([], "after the No")
    else:
        ask(answers[:1], "after Frequency")
    while ask(answers, "at the end"):
        pass
    return asked


def roster_on_the_wire(run, leg, project_id: str, *, view: str = "orb (wire)") -> dict:
    """Spec 161 FR-5, FR-7 on the wire (keel-cloud 269 FR-2, 270 FR-1, FR-2): the problem study's five people -- About
    half with the own row (Frequency's why alone), Every time without it (Importance's alone), Now and then without it
    (two, Frequency's first), Never after a yes (the second stem), the No-sayer (the Prevalence why on the spot, then
    Importance) -- each link served, each why asked as the page asks it, each response sent and taken; then one stranger
    who answers the screener No and leaves, counted nowhere."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    # the roster's stories read ANCHORED, so every yes-sayer's answers count (the run's reading: a GUESSED story is
    # counted nowhere, and the base script's readings are the corpus people's, in its own order)
    run.load_runtime("PROBLEM", extra={"INTERPRET": [ts.ANCHORED] * 12})
    names = [f"Stranger {run.stamp} {i}" for i in range(1, len(ts.ROSTER) + 2)]
    links = make_links(run, project_id, names)
    own, tasks, act = owner_row_and_tasks(run, project_id)
    out: dict = {"people": [], "picks": [], "stories": [], "said": {}}
    yes_stories = iter(ts.STORIES)
    for person, link in zip(ts.ROSTER, links):
        person = dict(person)
        if person["gate"]:
            person["story"] = next(yes_stories)
        token = token_of(link["url"])
        interview, _ = read_served(run, link["url"])
        if not out["people"]:
            four_questions_served(run, leg, interview, view=view, other_tasks=tasks, own=own)
        whys = walk_whys_on_the_wire(run, token, person, interview, other_tasks=tasks, own=own)
        body = ts.response_for(person, interview, fmt="TEXT", whys=whys, other_tasks=tasks, own_label=own)
        status, answer = stranger_call(run, "POST", f"/v2/i/{token}/interview/response", body)
        got = [w["dimension"] for w in whys]
        want_stems = [ts._bare(x) for x in person["stems"] if x]
        stems = [ts._bare(w["text"]) for w in whys]
        leg.check(run, f"{person['who']}: owed {', '.join(person['owed'])} -- the whys served in that order "
                       f"({', '.join(got) or 'none'}), the words the registry's, and the response taken (201)",
                  got == person["owed"] and all(s in stems for s in want_stems) and status == 201,
                  screen="POST follow-up / response", view=view,
                  detail={"whys": whys, "status": status, "refused": answer, "sent": {k: body.get(k) for k in
                                                                                       ("recency", "story")}
                          | {"answers": len(body.get("answers") or []), "followUps": [f["dimension"] for f in
                                                                                     body.get("followUps") or []]}},
                  stop=False)
        if not person["gate"]:
            leg.check(run, "the No-sayer's response on the wire: the gate's No (`recency: false`), no story, no "
                           "Frequency, the Importance pick, one why (keel-cloud 269 FR-2)",
                      body.get("recency") is False and "story" not in body and len(body.get("answers") or []) == 1
                      and len(body.get("followUps") or []) == 1 and status == 201, screen="the No path", view=view,
                      detail={"sent": body, "status": status}, stop=False)
            whys0 = [w for w in whys if w["at"] == "after the No"]
            leg.check(run, f"the No goes on: *{ts.PREVALENCE_WHY}* served on the spot after the No, before Importance",
                      bool(whys0) and whys0[0]["dimension"] == ts.PREVALENCE
                      and ts._bare(whys0[0]["text"]) == ts._bare(ts.PREVALENCE_WHY), screen="the gate's No",
                      view=view, detail=whys, stop=False)
        else:
            out["picks"].append(person["frequency"])
            out["stories"].append((link.get("invitationId"), person["story"]))
        for w in whys:
            out["said"].setdefault(w["dimension"], []).append(ts.why_said(w))
        out["people"].append({"who": person["who"], "owed": person["owed"], "whys": got, "status": status,
                              "invitation": link.get("invitationId")})
    if len(links) > len(ts.ROSTER):
        screened = links[len(ts.ROSTER)]
        status, answer = stranger_call(run, "POST", f"/v2/i/{token_of(screened['url'])}/interview/response",
                                       {"outsideSegment": True, "format": "TEXT"})
        leg.check(run, "a stranger who answers the screener No leaves: `outsideSegment: true` alone, taken (201), "
                       "counted nowhere", status == 201, screen="the screener's No", view=view,
                  detail={"status": status, "refused": answer}, stop=False)
    out["own"], out["tasks"], out["act"] = own, tasks, act
    run.__dict__.setdefault("roster", {})["problem"] = out
    return out


def founder_page_on_the_wire(run, leg, project_id: str, roster: dict) -> None:
    """Spec 161 FR-7, FR-8 on the wire (keel-cloud 269 FR-3, FR-5; 270 FR-2-FR-5): the founder's page after the five --
    the scripted runtime given the walk's THEMES and the ways' reading, then the standings and the overview read:
    Frequency on five bands with the two `forCodes` and the share, no Current solution anywhere, the ways GROUPED with
    the founder's way flagged and never on Insights, the Insights cards read as spec 119's with `capped` and no
    `tookBy`, the brief's facts on bands."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    # spec 164: every yes-sayer the study's links were walked with counts on the founder's page -- the roster's and the
    # orb's walk by voice before it (on keel-web 258 the problem link's yes walk runs, its Frequency and its story too)
    others = other_yes_sayers(run, project_id, "problem")
    roster = dict(roster, picks=list(roster["picks"]) + others["picks"],
                  stories=list(roster["stories"]) + others["stories"])
    if others["picks"] or others["stories"]:
        leg.notes.append(f"the founder's page counts the study's other yes-sayers too: {others}")
    run.load_runtime("PROBLEM", extra={"THEMES": ts.themes_entries(roster["said"]),
                                       "EXPERIENCE_WAYS": [ts.ways_entry(roster["stories"], roster.get("act"))],
                                       "INTERPRET": [ts.ANCHORED] * 12})
    deadline = time.monotonic() + 120
    overview, standings = {}, {}
    while time.monotonic() < deadline:
        overview = run.get(f"/v2/projects/{project_id}/overview") or {}
        standings = run.get(f"/v2/projects/{project_id}/standings") or {}
        grouped = ((overview.get("ways") or {}).get("state") == "GROUPED") and all(
            i.get("state") != "GROUPING" for i in standings.get("insights") or [])
        if grouped and not overview.get("openSteps"):
            break
        time.sleep(2)
    (run.run_dir / "standings-problem.json").write_text(json.dumps(standings, indent=1, default=str), encoding="utf-8")
    (run.run_dir / "overview-problem.json").write_text(json.dumps(overview, indent=1, default=str), encoding="utf-8")
    row = ts.frequency_row(standings)
    faults = ts.frequency_faults(row, picks=roster["picks"])
    leg.check(run, "the Overview's Frequency is five bands with the two for the founder (`forCodes` every_time, "
                   "most_times), the share of the yes-sayers on them and the founder's band (keel-cloud 269 FR-3)",
              not faults, screen="the Overview · Frequency", view="founder (wire)",
              detail={"faults": faults, "chart": row.get("chart"), "picks": roster["picks"]}, stop=False)
    where = ts.current_solution_anywhere(standings, overview)
    leg.check(run, "no Current solution anywhere -- no card, row, fact, breakdown line or insight (keel-cloud 269 FR-5)",
              not where, screen="the Overview, the standings", view="founder (wire)", detail=where[:12], stop=False)
    ways = ts.ways_faults(overview, standings, stories=len(roster["stories"]), founder_way=roster.get("act"))
    leg.check(run, f"the ways panel's reading (*How they do it today*): `Overview.ways` GROUPED over the "
                   f"{len(roster['stories'])} stories, the founder's way flagged, nothing of it on Insights (keel-cloud "
                   "270 FR-3, FR-4)", not ways, screen="the Overview · the ways", view="founder (wire)",
              detail={"faults": ways, "ways": overview.get("ways")}, stop=False)
    faults = ts.insights_faults(standings)
    leg.check(run, "the Insights cards as spec 119's: the three rungs' headings (*What keeps it from happening to "
                   "them*, *What makes the difference*), the quotes with their option (*No*, a band's label), `capped` "
                   "with `asked + capped = against`, `tookBy` nowhere (keel-cloud 270 FR-2, FR-5)",
              not faults and any(i.get("dimension") == ts.PREVALENCE for i in standings.get("insights") or []),
              screen="Insights", view="founder (wire)",
              detail={"faults": faults, "insights": [{k: i.get(k) for k in ("dimension", "status", "rungHeading",
                                                                              "against", "asked", "capped", "state",
                                                                              "dissent", "frame")}
                                                     for i in standings.get("insights") or []]}, stop=False)
    faults = ts.brief_frequency_faults(standings.get("facts") or {}, picks=roster["picks"])
    leg.check(run, "the brief's facts on bands: `facts.problem.frequency` {n, the five bands, mostOrEvery}, no median "
                   "(keel-cloud 269 FR-3)", not faults, screen="the brief's facts", view="founder (wire)",
              detail={"faults": faults, "frequency": ((standings.get("facts") or {}).get("problem") or {})
                      .get("frequency")}, stop=False)
    founder_page_on_screen(run, leg, project_id, overview, standings)


def made_invitation(made: dict) -> str | None:
    """The invitation id of a link made on Send more (`MadeLink.invitationId` in the batch Send more posted): the link
    whose url is the one kept, else the batch's one link."""
    links = (made.get("batch") or {}).get("links") or []
    by_url = next((x.get("invitationId") for x in links if x.get("url") and x.get("url") == made.get("url")), None)
    return by_url or (links[0].get("invitationId") if len(links) == 1 else None)


def invitation_of(run, project_id: str, url: str) -> str | None:
    """The invitation id of a link by its address, where the register carries the link's token (a fallback: the link
    made on Send more keeps its `MadeLink.invitationId`)."""
    token = token_of(url)
    found: list[str] = []

    def walk(value) -> None:
        if isinstance(value, dict):
            if value.get("invitationId") and any(isinstance(v, str) and token in v for v in value.values()):
                found.append(str(value["invitationId"]))
            for v in value.values():
                walk(v)
        elif isinstance(value, list):
            for v in value:
                walk(v)
    walk(run.get(f"/v2/projects/{project_id}/invitations") or {})
    return found[0] if found else None


def other_yes_sayers(run, project_id: str, study: str) -> dict:
    """Spec 164: the yes-sayers the study's links were walked with outside the roster (`run.study_walks`: the orb's walk
    by voice) -- each one's Frequency code and story `(invitationId, words)`, read off what the page posted."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    out: dict = {"picks": [], "stories": []}
    for w in (run.__dict__.get("study_walks") or {}).get(study) or []:
        body = w.get("sent") or {}
        if body.get("recency") is not True or body.get("anchorChip"):
            continue
        code = ts.frequency_code_of(w.get("interview"), body)
        if code:
            out["picks"].append(code)
        if body.get("story"):
            invitation = w.get("invitation") or invitation_of(run, project_id, w["url"])
            if invitation:
                out["stories"].append((invitation, body["story"]))
            else:
                out.setdefault("unfound", []).append(w["url"])
    return out


#: Spec 164 (keel-web 258 FR-8): the ways panel as the Overview draws it, read for `three_surfaces.ways_panel_faults`.
WAYS_PANEL_JS = r"""() => {
  const t = (e) => e ? (e.textContent || '').replace(/\s+/g, ' ').trim() : '';
  const w = document.querySelector('[data-testid=rp-ways]');
  if (!w) return {present: false};
  const li = w.closest('li');
  const rowLi = !!(li && li.classList.contains('rp-ways-row'));
  const prev = rowLi ? li.previousElementSibling : null;
  const prevRow = prev ? prev.querySelector('.rp-row') : null;
  const panel = w.closest('[data-testid^=report-stage-]');
  const reading = w.querySelector('[data-testid=rp-ways-reading]');
  return {present: true, in_row_li: rowLi, panel: panel ? panel.getAttribute('data-testid') : null,
          before: prevRow ? prevRow.getAttribute('data-dim') : null,
          after_prevalence: rowLi && !!prevRow && prevRow.getAttribute('data-dim') === 'problem.prevalence'
                            && (!panel || panel.getAttribute('data-testid') === 'report-stage-PROBLEM'),
          state: w.getAttribute('data-state'), head: t(w.querySelector('.rp-ways__head')),
          reading: reading ? t(reading) : null, line: reading ? null : t(w.querySelector('.rp-ways__line')),
          rows: Array.from(w.querySelectorAll('.rp-ways__row')).map((r) => {
            const lab = r.querySelector('.rp-ways__label');
            const yours = lab ? lab.querySelector('.rp-ways__yours') : null;
            const label = lab ? Array.from(lab.childNodes).filter((n) => n !== yours).map((n) => n.textContent)
                .join('').replace(/\s+/g, ' ').trim() : '';
            return {label: label, founders: r.getAttribute('data-founders') === 'true',
                    yours: yours ? t(yours) : null, n: t(r.querySelector('.rp-ways__n'))};
          })};
}"""


def founder_page_on_screen(run, leg, project_id: str, overview: dict, standings: dict) -> None:
    """Spec 164 (the mirrors of keel-web 258 FR-6 to FR-9): the founder's page as drawn, held to the wire just read --
    the ways panel under Prevalence's row (mirror 9), Frequency's card on the stage page (mirror 4: five bands, the two
    `data-for`, the caption), the Insights boxes' `capped` line in `tookBy`'s place (mirrors 2, 3) and the breakdown's
    Frequency cell on bands with no Current solution row (mirror 5). Each read failed by name where the page would not
    draw (`stop=False`)."""
    from evals import backtest    # noqa: PLC0415
    from evals import report_marks as rm    # noqa: PLC0415
    from harness import three_surfaces as ts    # noqa: PLC0415
    from harness import vectors_screens as vs_screens    # noqa: PLC0415
    page = run.page
    answers = vs_screens.Answers(page, run.recorder, run.web)
    view = "founder (screen)"
    try:
        answers._report(project_id, "overview")
        page.get_by_test_id("report-hero").first.wait_for(state="visible", timeout=30_000)
        drawn = page.evaluate(WAYS_PANEL_JS)
        ss._BrowserStep(run.recorder, page, "founder").screenshot("report-overview-ways")
    except Exception as missed:  # noqa: BLE001 - the read named
        drawn = {"error": str(missed)[:300]}
    faults = ts.ways_panel_faults(drawn, overview.get("ways")) if "error" not in drawn else [drawn]
    leg.check(run, "the ways panel as drawn (*How they do it today*, keel-web 258 FR-8): right under Prevalence's row, "
                   "the read line, a row a group with the founder's marked *your way*", not faults,
              screen="the Overview · the ways", view=view, stop=False,
              detail={"faults": faults, "drawn": drawn, "served": overview.get("ways")})
    row = ts.frequency_row(standings)
    try:
        page.goto(f"{run.web}/p/{project_id}/s/PROBLEM", wait_until="load")
        key = ts.FREQUENCY
        page.wait_for_selector(backtest.card_selector(key), state="visible", timeout=30_000)
        body = backtest.card_selector(key, backtest.CARD_BODY)
        if not page.evaluate("(sel) => !!document.querySelector(sel)", body):
            page.click(backtest.card_selector(key, backtest.CARD_OPEN))
        page.wait_for_selector(body, state="visible", timeout=10_000)
        card = page.evaluate(backtest.CARD_JS, key) or {}
        ss._BrowserStep(run.recorder, page, "founder").screenshot("stage-problem-frequency")
    except Exception as missed:  # noqa: BLE001 - the read named
        card = {"error": str(missed)[:300]}
    chart = card.get("chart") if "error" not in card else None
    faults = ts.frequency_chart_faults(chart, row) if chart is not None else [card]
    leg.check(run, "Frequency's card as drawn (keel-web 258 FR-6): `data-chart=\"frequency\"`, the five bands with their "
                   "counts, Every time and Most times `data-for`, the caption *{k} of {n} said most times or every time "
                   "· you said {band}*", not faults, screen="the stage page · Frequency", view=view, stop=False,
              detail={"faults": faults, "drawn": {k: (chart or {}).get(k) for k in ("chart", "frequency_caption",
                                                                                      "bars")}})
    try:
        insights = answers.insights(project_id)
    except Exception as missed:  # noqa: BLE001 - the read named
        insights = {"error": str(missed)[:300]}
    served = {i.get("dimension"): i for i in standings.get("insights") or []}
    faults = []
    for box in insights.get("boxes") or []:
        want = served.get(box.get("key")) or {}
        if ts._words(box.get("capped")) != ts._words(rm.capped_line(want)):
            faults.append({box.get("key"): "capped", "drawn": box.get("capped"), "want": rm.capped_line(want)})
        if box.get("took_by"):
            faults.append({box.get("key"): "a took-by line drawn (keel-web 258 FR-9: gone)", "drawn": box["took_by"]})
    if "error" in insights or not insights.get("boxes"):
        faults.append({"insights": insights.get("error") or "no box drawn"})
    leg.check(run, "the Insights boxes as drawn (keel-web 258 FR-9): the people past the two-question cap on their own "
                   "line where served (`insights-capped`), no took-by line", not faults, screen="Insights",
              view=view, stop=False, detail={"faults": faults, "boxes": [{k: b.get(k) for k in (
                  "key", "capped", "count_line", "took_by")} for b in insights.get("boxes") or []]})
    try:
        binding = answers.brief(project_id)
    except Exception as missed:  # noqa: BLE001 - the read named
        binding = {"error": str(missed)[:300]}
    faults = rm.breakdown_faults(binding.get("breakdown"), standings.get("facts") or {}) if "error" not in binding \
        else [binding]
    if "error" not in binding and not any(r.get("key") == ts.FREQUENCY for r in binding.get("breakdown") or []):
        faults.append({"breakdown": "no Frequency row"})
    leg.check(run, "the breakdown as drawn (keel-web 258 FR-6, FR-7): Frequency's answers the served bands (*Every time "
                   "k · Most times k · ...*), no Current solution row", not faults, screen="Download the brief · the "
                   "breakdown", view=view, stop=False,
              detail={"faults": faults, "rows": binding.get("breakdown"),
                      "want": rm.breakdown_frequency(standings.get("facts") or {})})


# ------------------------------------------------------------------------------------------------ FR-9: three surfaces

def keep_surface(run, study: str, surface: str, record: list[dict], *, source: str) -> None:
    """One surface's record for the study, kept for the comparison and the report -- the wire's (`source` names the
    link as served or the call's script) and, on keel-web 258, the walk's beside it."""
    kind = "walked" if "walk" in source else "wire"
    run.__dict__.setdefault("surfaces", {}).setdefault(study, {}).setdefault(kind, {})[surface] = {
        "record": record, "source": source}


def card_script(run, project_id: str, call: dict) -> dict:
    """The Copilot card's script for a planned call (`GET .../calls/{callId}/script`)."""
    call_id = call.get("callId") or call.get("id")
    status, body = run.call("GET", f"/v2/projects/{project_id}/calls/{call_id}/script")
    return body if status == 200 and isinstance(body, dict) else {}


def three_surfaces_check(run, leg, study: str) -> dict:
    """Spec 161 FR-9: the orb's, the face's and the Copilot card's records of the study held equal step for step -- the
    question's words, the options' labels in order, the follow-up stems, the gate's words; the leg fails by name at the
    step and the surface where one differs. The wire's records (the link as served to the orb and to the face, the
    call's script) are compared on every run -- the cloud's one script; the walks' (keel-web 258's screens) where all
    three were walked."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    kept = (run.__dict__.get("surfaces") or {}).get(study) or {}
    verdicts = {}
    for kind in ("wire", "walked"):
        by = kept.get(kind) or {}
        records = {k: v["record"] for k, v in by.items()}
        missing = [x for x in ("orb", "face", "card") if x not in records]
        if kind == "walked" and missing:
            continue
        # spec 164: a walked why is compared by where it is asked (`three_surfaces.WALKED_WHY`); its words on the wire
        verdict = ts.same_script(records, follow_up_words=kind == "wire") if not missing else \
            {"same": None, "missing": missing}
        verdicts[kind] = verdict
        where = "" if verdict.get("same") or verdict.get("same") is None else \
            f" -- they part at step {int(verdict['at']) + 1} (`{verdict.get('step')}`) on the {verdict.get('surface')}: " \
            f"{', '.join(verdict.get('differs') or [])}"
        leg.check(run, f"one script, three surfaces ({'as served' if kind == 'wire' else 'as walked'}): the orb, the face "
                       "and the Copilot card say the same questions, the same options in order, the same follow-ups and "
                       "the same gate, step for step" + where,
                  verdict.get("same") is True, screen="every question (three surfaces)", view=f"three surfaces ({kind})",
                  detail={"verdict": verdict, "sources": {k: v["source"] for k, v in by.items()},
                          "gate": {k: ts.gate_words(v) for k, v in records.items()}}, stop=False)
        if study in ("problem", "solution") and not missing:
            gates = {k: ts.gate_words(v) for k, v in records.items()}
            leg.check(run, f"the gate's words are *{ts.GATE_WORDS}* on the orb, the face and the Copilot card "
                           f"({'as served' if kind == 'wire' else 'as walked'}; keel-cloud 269 FR-1, D12)",
                      all(g == ts.GATE_WORDS for g in gates.values()), screen="the gate (three surfaces)",
                      view=f"three surfaces ({kind})", detail=gates, stop=False)
    run.__dict__.setdefault("surface_verdicts", {})[study] = verdicts
    return verdicts


# ================================================================================ spec 162: the solution, on three surfaces
# keel-cloud 272 (contract 90), keel-web 260: the solution link's order (the opening, the screener, the bridge, the
# problem's film, the check, the plate and its two lines, the idea's film), three yes-or-no questions, a why after every
# No, the pilot ask; the founder's page on three share bars; the orb, the face and the Copilot card held to one script.
# The cloud's side is read on the wire every run (`harness/solution_surfaces.py`); the stranger's screens are keel-web
# 260's -- where the checkout lacks it they are written to the specs and named *pending keel-web 260* (spec 162 FR-11).

#: Spec 162 FR-11: the stranger's screen checks of the solution study a keel-web before 260 cannot hold.
SCREEN_CHECKS_260 = ["the link's order on screen: the opening, the screener, *Let us see it.*, the problem's film to the "
                     "pain, *Begin*, the check, the plate (`plate.before` said, the plate shown, `plate.after` over the "
                     "fade), the idea's film to the joy, the three questions, the whys, the pilot ask, the thanks",
                     "a check No leaving before the plate (one stranger)", "`yes_no` drawn as two rows and answered by "
                     "*yes*, *no*, *A*, *B* and the option's words; *si* unclear", "every why answered in words",
                     "the idea card's three lines drawn nowhere", "the time to the first question measured on screen",
                     "the three share bars drawn on the Overview (the founder's band shaded)",
                     "the Copilot card's `plate` passage drawn (the plate, its two lines, the idea film's lines with "
                     "*Next*) and its two yes / no bubbles walked"]


def solution_founder(run) -> dict:
    """What the founder's solution leg (FR-1b) left: the brand's name and tagline, the idea's setup, the pilot offered."""
    from harness import story_screens as ss_    # noqa: PLC0415
    kept = run.__dict__.get("founders_solution") or {}
    idea = kept.get("idea") or {}
    project = run.projects.get("b-solution")
    if not idea and project:
        idea = run.get(f"/v2/projects/{project}/idea/spoken") or {}
    brand = idea.get("brand") or {}
    return {"name": brand.get("name") or ss_.IDEA_NAME, "tagline": brand.get("tagline"),
            "setup": list(idea.get("setup") or []), "pilot": idea.get("pilot") is not False, "idea": idea}


def solution_wire_checks(run, leg, interview: dict, *, view: str) -> dict:
    """Spec 162 FR-5, FR-6 on the wire (keel-cloud 272 FR-1, FR-3, FR-4): the link's words around the two films, the plate
    and its lines, the idea card nowhere, the pilot ask, the three questions on `yes_no` in 272's words."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    f = solution_founder(run)
    founder = str(interview.get("founderFirstName") or "")
    faults = sol.link_faults(interview, founder=founder, name=f["name"], tagline=f["tagline"], pilot=f["pilot"])
    leg.check(run, "the solution link's words (keel-cloud 272 FR-3, FR-4): the opening with the founder's first name "
                   "and *First, one question.*, the bridge *Let us see it.*, the check *Did this happen to you?*, both "
                   "films, the plate (the name, the tagline) with *Now {founder} has built {name}.* and *and believes it "
                   "solves this. Let us see.*, no idea card, *Would you try {name} for real?*; every sentence within 20 "
                   "words", not faults, screen="GET /v2/i/{token}/interview", view=f"{view} (wire)",
              detail={"faults": faults, "passages": interview.get("passages"), "plate": interview.get("plate"),
                      "pilot": interview.get("pilot"), "reveal": bool(interview.get("reveal"))}, stop=False)
    faults = sol.question_faults(interview, name=f["name"], setup=f["setup"])
    leg.check(run, "the three questions on `yes_no` (*Yes* · *No*, no escape), in 272's words: Compatibility with the "
                   "brand's name and the job's -ing form, Relative advantage the base job, Adoption friction "
                   + ("its setup form" if f["setup"] else "its no-setup form") + "; each sentence at most 20 words",
              not faults, screen="the three questions", view=f"{view} (wire)",
              detail={"faults": faults, "questions": {k: sol.ts.item_of(interview, k).get("question")
                                                      for k in sol.SOLUTION_DIMENSIONS}}, stop=False)
    lines = sol.films_lines(interview)
    leg.check(run, "the solution film served to the stranger ends on the joy, the plate on its story (`ideaStory.plate`)",
              bool(lines["idea"]) and bool(((interview.get("ideaStory") or {}).get("scenes") or [{}])[-1].get("joy"))
              and bool((interview.get("ideaStory") or {}).get("plate")), screen="GET /v2/i/{token}/interview",
              view=f"{view} (wire)", detail={"lines": lines, "plate": (interview.get("ideaStory") or {}).get("plate")},
              stop=False)
    timed = sol.first_question_seconds(interview)
    run.__dict__.setdefault("first_question", {})[view] = timed
    leg.notes.append(f"the time to the first question on the solution link ({view}, the cloud's count; D6: recorded, "
                     f"never asserted): {timed}")
    return {"founder": founder, **f}


def solution_whys_on_the_wire(run, token: str, person: dict, interview: dict) -> list[dict]:
    """keel-web 260 FR-3 as the page calls it: the follow-up route after each of the three items, with the answers so
    far and the rungs already asked, until two are asked. Returns each why served, in order."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    answers = sol.answers_for(person, interview)
    asked: list[dict] = []
    path = f"/v2/i/{token}/interview/follow-up"
    for k in range(len(answers)):
        if len(asked) >= sol.MAX_FOLLOW_UPS:
            break
        status, body = stranger_call(run, "POST", path, {"answers": answers[:k + 1], "recency": True,
                                                         "asked": [a["dimension"] for a in asked]})
        if status == 200 and body:
            asked.append({"dimension": body.get("dimension"), "text": body.get("text"), "spoken": body.get("spoken"),
                          "heading": body.get("heading"), "after": sol.SOLUTION_DIMENSIONS[k]})
    return asked


def solution_roster_on_the_wire(run, leg, project_id: str, *, view: str = "orb (wire)") -> dict:
    """Spec 162 FR-7 on the wire (keel-cloud 272 FR-2): the solution study's five people -- yes on all three (asked
    nothing), a No on each dimension alone (its why), three Nos (two whys, the third capped) -- each link served, each why
    asked as keel-web 260's page asks it, each response sent and taken; then the check's No (leaving before the plate:
    the answers empty) and the screener's No (outside the segment)."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    run.load_runtime("SOLUTION")
    names = [f"Stranger {run.stamp} solution {i}" for i in range(1, len(sol.SOLUTION_ROSTER) + 3)]
    links = make_links(run, project_id, names)
    out: dict = {"people": [], "picks": [], "said": {}, "capped": {}}
    for person, link in zip(sol.SOLUTION_ROSTER, links):
        token = token_of(link["url"])
        interview, _ = read_served(run, link["url"])
        whys = solution_whys_on_the_wire(run, token, person, interview)
        body = sol.response_for(person, interview, fmt="TEXT", whys=whys)
        status, answer = stranger_call(run, "POST", f"/v2/i/{token}/interview/response", body)
        got = [w["dimension"] for w in whys]
        words_ok = all(sol.ts._bare(w.get("text") or w.get("spoken")) == sol.ts._bare(sol.WHYS[w["dimension"]][0])
                       for w in whys if w.get("dimension") in sol.WHYS)
        leg.check(run, f"{person['who']}: owed {', '.join(person['owed']) or 'nothing'} -- the whys served in that order "
                       f"({', '.join(got) or 'none'}), each on the spot after its No, the words the registry's "
                       + (f"(*{sol.WHYS[person['owed'][0]][0]}* ...)" if person["owed"] else "")
                       + (f"; {', '.join(person['capped'])} capped" if person["capped"] else "")
                       + "; the response taken (201)",
                  got == person["owed"] and words_ok and status == 201
                  and all(w["after"] == w["dimension"] for w in whys), screen="POST follow-up / response", view=view,
                  detail={"whys": whys, "status": status, "refused": answer,
                          "sent": {"answers": len(body["answers"]), "followUps": [f["dimension"] for f in
                                                                                 body.get("followUps") or []]}},
                  stop=False)
        out["picks"].append(person["picks"])
        for w in whys:
            out["said"].setdefault(w["dimension"], []).append(sol.WHY_SAID[w["dimension"]])
        for key in person["capped"]:
            out["capped"][key] = out["capped"].get(key, 0) + 1
        out["people"].append({"who": person["who"], "owed": person["owed"], "whys": got, "status": status,
                              "invitation": link.get("invitationId")})
    if len(links) > len(sol.SOLUTION_ROSTER):
        no_link = links[len(sol.SOLUTION_ROSTER)]
        status, answer = stranger_call(run, "POST", f"/v2/i/{token_of(no_link['url'])}/interview/response",
                                       {"format": "TEXT", "recency": False, "answers": []})
        leg.check(run, "a No on the check leaves with the thanks before the plate: `recency: false`, the answers empty, "
                       "taken (201) -- one stranger per study", status == 201, screen="the check's No", view=view,
                  detail={"status": status, "refused": answer}, stop=False)
    if len(links) > len(sol.SOLUTION_ROSTER) + 1:
        screened = links[len(sol.SOLUTION_ROSTER) + 1]
        status, answer = stranger_call(run, "POST", f"/v2/i/{token_of(screened['url'])}/interview/response",
                                       {"outsideSegment": True, "format": "TEXT"})
        leg.check(run, "a stranger who answers the screener No leaves: `outsideSegment: true` alone, taken (201)",
                  status == 201, screen="the screener's No", view=view, detail={"status": status, "refused": answer},
                  stop=False)
    run.__dict__.setdefault("roster", {})["solution"] = out
    return out


def solution_founder_page(run, leg, project_id: str, roster: dict) -> None:
    """Spec 162 FR-7, FR-8 on the wire (keel-cloud 272 FR-2, FR-6): after the five -- the scripted runtime given the
    walk's THEMES -- the standings read: the three Overview cards as share bars (the yes of n, the founder's band), the
    So lines evidence only, no benefit scale anywhere, the Insights cards as spec 119's (the three headings, the quotes
    with *No*, `capped`, no `tookBy`), the brief's solution rows on `{yes, n, share, founderBand}`."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    run.load_runtime("SOLUTION", extra={"THEMES": sol.themes_entries(roster["said"])})
    deadline = time.monotonic() + 120
    standings: dict = {}
    while time.monotonic() < deadline:
        standings = run.get(f"/v2/projects/{project_id}/standings") or {}
        insights = [i for i in standings.get("insights") or [] if i.get("dimension") in sol.WHYS]
        if insights and all(i.get("state") != "GROUPING" for i in insights):
            break
        time.sleep(2)
    overview = run.get(f"/v2/projects/{project_id}/overview") or {}
    (run.run_dir / "standings-solution.json").write_text(json.dumps(standings, indent=1, default=str), encoding="utf-8")
    (run.run_dir / "overview-solution.json").write_text(json.dumps(overview, indent=1, default=str), encoding="utf-8")
    faults = sol.share_faults(standings, roster["picks"])
    leg.check(run, "the three Overview cards are share bars (keel-cloud 272 FR-6): `chart.share` -- the yes of n "
                   "counted, the proportion, the founder's band -- the bars *Yes* and *No*, no `chart.benefit`",
              not faults, screen="the Overview · the solution's three", view="founder (wire)",
              detail={"faults": faults, "charts": {k: (sol.standing_of(standings, k).get("chart") or {})
                                                   for k in sol.SOLUTION_DIMENSIONS}}, stop=False)
    faults = sol.so_line_faults(standings)
    leg.check(run, "the So lines are evidence only -- no *should*, *next*, *try* -- and no benefit scale anywhere (the "
                   "founder's rule of 2026-11-15)", not faults, screen="the Overview · the So lines",
              view="founder (wire)", detail={"faults": faults, "rows": {k: {f: sol.standing_of(standings, k).get(f)
                                                                          for f in ("status", "so", "insight")}
                                                                      for k in sol.SOLUTION_DIMENSIONS}}, stop=False)
    faults = sol.insights_faults(standings, capped_by=roster.get("capped"))
    leg.check(run, "the Insights cards as spec 119's: the three headings (*What would get in the way*, *What it would "
                   "have to do better*, *What makes it a trouble*), the quotes with the option *No*, `capped` with "
                   "`asked + capped = against` (the three-Nos person's third capped), `tookBy` nowhere",
              not faults and any(i.get("dimension") in sol.WHYS for i in standings.get("insights") or []),
              screen="Insights", view="founder (wire)",
              detail={"faults": faults, "insights": [{k: i.get(k) for k in ("dimension", "status", "rungHeading",
                                                                              "against", "asked", "capped", "state")}
                                                     for i in standings.get("insights") or []
                                                     if i.get("dimension") in sol.WHYS]}, stop=False)
    from harness import story_screens as ss_    # noqa: PLC0415
    if ss_.web_has_260(run.stack.keel_web):
        solution_page_on_screen(run, leg, project_id, standings)
    faults = sol.brief_faults(standings.get("facts") or {}, roster["picks"])
    leg.check(run, "the brief's solution rows on `{yes, n, share, founderBand}`, no benefit scale (keel-cloud 272 FR-6)",
              not faults, screen="the brief's facts", view="founder (wire)",
              detail={"faults": faults, "rows": ((standings.get("facts") or {}).get("solution") or {}).get("rows")},
              stop=False)


def solution_surfaces_check(run, leg) -> dict:
    """Spec 162 FR-9: the orb's, the face's and the Copilot card's records of the solution study held equal step for
    step -- the opening, the screener, the bridge, the problem film's lines, the check, the plate's two lines, the idea
    film's lines, the three questions with their options, their whys, the pilot ask; the leg fails by name at the step
    and the surface where one differs."""
    from harness import three_surfaces as ts    # noqa: PLC0415
    kept = ((run.__dict__.get("surfaces") or {}).get("solution") or {}).get("wire") or {}
    records = {k: v["record"] for k, v in kept.items()}
    missing = [x for x in ("orb", "face", "card") if x not in records]
    verdict = ts.same_script(records) if not missing else {"same": None, "missing": missing}
    where = "" if verdict.get("same") or verdict.get("same") is None else \
        f" -- they part at step {int(verdict['at']) + 1} (`{verdict.get('step')}`) on the {verdict.get('surface')}: " \
        f"{', '.join(verdict.get('differs') or [])}"
    leg.check(run, "one script, three surfaces on the solution study (as served): the orb, the face and the Copilot card "
                   "say the same opening, screener, bridge, the problem film's lines, the check, the plate's two lines, "
                   "the idea film's lines, the three questions with their options, their whys and the pilot ask, step "
                   "for step" + where, verdict.get("same") is True, screen="every step (three surfaces)",
              view="three surfaces (wire)", detail={"verdict": verdict, "sources": {k: v["source"] for k, v in
                                                                                    kept.items()}}, stop=False)
    run.__dict__.setdefault("surface_verdicts", {})["solution"] = {"wire": verdict}
    return verdict


def solution_view(run, leg, view: str, project_id: str) -> None:
    """Spec 162 FR-5 to FR-9 on the solution study, one view: the link (or the call's script) read on the wire -- its
    words, the three questions, the record kept for the three surfaces; on the orb the five people walked on the wire
    and the founder's page read; on the card the script's plate passage and the comparison. The screen walks are keel-web
    260's: where the checkout lacks it they are named pending (`SCREEN_CHECKS_260`)."""
    from harness import interview_charge as charge    # noqa: PLC0415
    from harness import interviewer_screens as ivs    # noqa: PLC0415
    from evals import calls_leg as calls_leg_mod    # noqa: PLC0415
    from harness import solution_surfaces as sol    # noqa: PLC0415
    from stack import ledger    # noqa: PLC0415
    names = people(run, "PROBLEM")
    if view == "orb":
        made = tv.send_link(run, leg, "solution-orb", project_id, "TEXT", person=person_at(names, 1))
        interview, reads = read_served(run, made["url"])
        run.orb_wires["solution"] = {"interview": interview, "url": made["url"]}
        leg.check(run, "the orb's link served (`speaker` ORB, the clips on Keel AI's route)",
                  (interview.get("interviewer") or {}).get("speaker") == ivs.SPEAKER_ORB,
                  screen="GET /v2/i/{token}/interview", view="orb (wire)",
                  detail={"reads": reads, "interviewer": bool(interview.get("interviewer"))}, stop=False)
        solution_wire_checks(run, leg, interview, view="orb")
        keep_surface(run, "solution", "orb", sol.served_record(interview), source="the link as served (the wire)")
        roster = solution_roster_on_the_wire(run, leg, project_id)
        solution_founder_page(run, leg, project_id, roster)
        from harness import story_screens as ss_    # noqa: PLC0415
        if ss_.web_has_260(run.stack.keel_web):
            solution_roster_on_screen(run, leg, project_id, speaker=ivs.SPEAKER_ORB)
        if not run.remote and run.account_id:
            rows = [r for r in ledger.rows(run.stack, run.account_id, since=run.ledger_since)
                    if not str(r.get("idempotency_key") or "").startswith(ledger.STAND_IN_PREFIX)]
            free = charge.free_reading_faults(rows) + charge.solution_reading_faults(rows)
            leg.check(run, "nothing bought on the solution study: every IDEA_TURN, STORY_PICTURES, PICTURE_REVIEW, "
                           "STORY_TURN and EXPERIENCE_WAYS row on the ledger 0 credits (spec 162 FR-10)", not free,
                      screen="the ledger", view="wire", detail={"faults": free, "rows": charge.reading_rows(rows)},
                      stop=False)
    elif view == "avatar":
        if run.remote:
            leg.status, leg.why = "skipped", "remote profile: the AI interviewer is bought on Keel's door"
            return
        register = run.get(f"/v2/projects/{project_id}/invitations") or {}
        kinds = register.get("kinds") or []
        kind = next((k for k in kinds if k.get("respondentType") != tv.vs.LINK_B2B), kinds[0])
        try:
            # its own stand-in key (spec 162): `avatar_view` stands Keel's door in again on keel-web 260
            interviewer_ready(run, leg, "solution-wire", project_id, kind.get("label"))
            made = tv.send_link(run, leg, "solution-avatar", project_id, "AI_INTERVIEWER", person=person_at(names, 3))
            interview, reads = read_served(run, made["url"])
            leg.check(run, f"the face's link served (`speaker` AVATAR, {FACE.title()})",
                      (interview.get("interviewer") or {}).get("speaker") == ivs.SPEAKER_AVATAR,
                      screen="GET /v2/i/{token}/interview", view="avatar (wire)",
                      detail={"reads": reads, "face": (interview.get("interviewer") or {}).get("face")}, stop=False)
            clips = ((interview.get("interviewer") or {}).get("clips") or {})
            leg.check(run, "the face's clips carry the solution link's lines: the bridge (`toTheFilm`) and the plate's "
                           "two (`plateBefore`, `plateAfter`) -- the pilot ask where offered (keel-cloud 272 judgement "
                           "call 6)", all(clips.get(k) for k in ("toTheFilm", "plateBefore", "plateAfter")),
                      screen="GET /v2/i/{token}/interview (clips)", view="avatar (wire)",
                      detail={"clips": sorted(clips)}, stop=False)
            solution_wire_checks(run, leg, interview, view="avatar")
            keep_surface(run, "solution", "face", sol.served_record(interview), source="the link as served (the wire)")
            from harness import story_screens as ss_    # noqa: PLC0415
            if ss_.web_has_260(run.stack.keel_web):
                solution_roster_on_screen(run, leg, project_id, speaker=ivs.SPEAKER_AVATAR, fmt="AI_INTERVIEWER",
                                          only=("three Nos",))
        finally:
            ledger.restore_own_door(run.stack, run.account_id, f"solution-wire-avatar-restore-{run.stamp}",
                                    spec=tv.STAND_IN_SPEC)
    else:
        register = run.get(f"/v2/projects/{project_id}/invitations") or {}
        kinds = register.get("kinds") or []
        kind = next((k for k in kinds if k.get("respondentType") != tv.vs.LINK_B2B), kinds[0])
        first_person(run, leg, project_id)
        status, call = run.call("POST", f"/v2/projects/{project_id}/calls", {"roleId": kind.get("roleId"),
                                                                             "name": names[5]})
        leg.check(run, f"a call planned with {names[5]} (POST calls 201)", status == 201 and bool((call or {}).get(
            "copilotPath")), screen="Sent · Calls with me", view="copilot", detail=call)
        script = card_script(run, project_id, call or {})
        (run.run_dir / "card-script-solution.json").write_text(json.dumps(script, indent=1, default=str),
                                                               encoding="utf-8")
        kinds_ = [p.get("kind") for p in script.get("passages") or []]
        plate = next((p for p in script.get("passages") or [] if p.get("kind") == "plate"), {})
        f = solution_founder(run)
        lines = sol.films_lines((run.orb_wires.get("solution") or {}).get("interview"))
        leg.check(run, "the call's script carries the plate passage (keel-cloud 272 FR-5): the brand, its two lines in "
                       "two forms, the idea film's lines as text (the link's, in order) and its pictures; no reveal "
                       "passage", "plate" in kinds_ and "reveal" not in kinds_ and plate.get("name") == f["name"]
                  and (not lines["idea"] or list(plate.get("lines") or []) == lines["idea"])
                  # a picture a scene; the last line is the film's ask, which has none
                  and len(plate.get("pictures") or []) in (len(plate.get("lines") or []),
                                                           len(plate.get("lines") or []) - 1),
                  screen="GET .../calls/{callId}/script", view="copilot (wire)",
                  detail={"kinds": kinds_, "plate": {k: plate.get(k) for k in ("name", "tagline", "before", "after",
                                                                                "lines")},
                          "pictures": len(plate.get("pictures") or [])}, stop=False)
        words = calls_leg_mod.plate_words(script, form="third")
        leg.check(run, "the card's plate passage reads the plate's two lines around the idea film's lines, as the link "
                       "says them (`calls_leg.plate_words`, the link's form)",
                  bool(words) and words[0] == (run.orb_wires.get("solution") or {}).get("interview", {}).get(
                      "plate", {}).get("before") and words[1:-1] == lines["idea"]
                  and words[-1] == sol.PLATE_AFTER, screen="the card's plate passage", view="copilot (wire)",
                  detail={"card": words, "link": lines["idea"]}, stop=False)
        faults = sol.first_person_faults(script, name=f["name"])
        leg.check(run, "the card's first-person forms: *I believe ...* on the opening, *Now I have built {name}.* and "
                       "*and I believe it solves this. Let us see.* on the plate (keel-cloud 272 FR-5)", not faults,
                  screen="GET .../calls/{callId}/script", view="copilot (wire)", detail=faults, stop=False)
        keep_surface(run, "solution", "card", sol.card_record(script), source="the call's script (the wire)")
        solution_surfaces_check(run, leg)
    from harness import story_screens as ss_    # noqa: PLC0415
    if not ss_.web_has_260(run.stack.keel_web):
        tv.pending_web(run, leg, "260", f"the solution study ({view})", SCREEN_CHECKS_260, screen="the solution link")


# ------------------------------------------------------------------------------------------------ spec 162 on screen
# keel-web 260's screens: the solution link's order walked on the orb and the face, the plate, `yes_no` by letter and by
# words, every why in words, the check's No before the plate; the card's plate passage. Run where the checkout carries
# keel-web 260 (`story_screens.web_has_260`).

#: The order of a plated link's steps as a walk reads them (`solution_order`).
SOLUTION_ORDER = ["screener", "film:problem", "check", "plate", "film:idea", "solution.compatibility",
                  "solution.relative_advantage", "solution.adoption_friction"]


def solution_order(rows: list[dict]) -> list[str]:
    """A walk's rows as the solution link's steps, in order: the screener, the problem's film, the check, the plate, the
    idea's film, the three questions (a why folded away), the pilot ask."""
    out: list[str] = []
    for r in rows:
        if r.get("screen") == "film":
            key = "film:idea" if r.get("kind") == "idea" else "film:problem"
        elif r.get("screen") == "plate":
            key = "plate"
        elif r.get("key") == "gate":
            key = "check"
        elif r.get("follow_up"):
            continue
        else:
            key = r.get("key")
        if key and (not out or out[-1] != key):
            out.append(key)
    return out


def solution_walk_checks(run, leg, walked: dict, interview: dict, *, view: str, label: str) -> None:
    """Spec 162 FR-5, FR-6 on keel-web 260's screens: the order, the plate (its words, its two lines, about three seconds
    alone), the three questions answered as said, the idea card nowhere, the time to the first question recorded."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    rows = walked.get("rows") or []
    order = [k for k in solution_order(rows) if k in SOLUTION_ORDER]
    leg.check(run, f"{label}: the link's order on screen -- the screener, the problem's film, the check, the plate, the "
                   "idea's film, then the three questions (keel-web 260 FR-1)", order == SOLUTION_ORDER,
              screen="the solution link's order", view=view, detail={"order": order, "want": SOLUTION_ORDER},
              stop=False)
    plate = next((r for r in rows if r.get("screen") == "plate"), {})
    want_plate = interview.get("plate") or {}
    leg.check(run, f"{label}: the plate -- the brand and its tagline on the stage, *{sol.PLATE_AFTER}* said over its fade "
                   "into the idea's film, the plate alone a while before it",
              bool(plate) and ts_bare(want_plate.get("name")) in ts_bare(plate.get("plate"))
              and any(ts_bare(sol.PLATE_AFTER) in ts_bare(x) for x in plate.get("said") or [])
              and (plate.get("alone_s") or 0) >= 1.0, screen="the plate", view=view,
              detail={"plate": plate, "served": want_plate}, stop=False)
    asked = [r for r in rows if r.get("key") in sol.SOLUTION_DIMENSIONS]
    leg.check(run, f"{label}: the three questions drawn as two rows, *Yes* and *No*, and answered as said (lit as said)",
              len(asked) == 3 and all([ts_bare(o) for o in r.get("options") or []] == ["yes", "no"] for r in asked),
              screen="the three questions", view=view,
              detail=[{k: r.get(k) for k in ("key", "question", "options", "said", "read")} for r in asked],
              stop=False)
    words = " ".join(str(r.get("question") or "") for r in rows)
    leg.check(run, f"{label}: the idea card's lines nowhere on the plated link (no *Imagine ...*, no reveal step)",
              "Imagine " not in words and not any(r.get("step") == "reveal" for r in rows), screen="every step",
              view=view, detail={"questions": [r.get("question") for r in rows if r.get("question")]}, stop=False)
    first = next((r.get("t") for r in rows if r.get("key") in sol.SOLUTION_DIMENSIONS and r.get("t") is not None), None)
    if first is not None:
        run.__dict__.setdefault("first_question", {})[f"{view} (walked)"] = {
            "seconds": first, "parts": "the walk's own clock, from Start to the first question's window (FakeSpeech "
                                       "clips: the films play at the fake's pace)", "minutes served": interview.get("minutes")}


def ts_bare(text) -> str:
    from harness import three_surfaces as ts    # noqa: PLC0415
    return ts._bare(text)


def solution_roster_on_screen(run, leg, project_id: str, *, speaker: str, fmt: str = "TEXT",
                              only: tuple[str, ...] | None = None) -> dict:
    """Spec 162 FR-7 on keel-web 260's screens: the solution study's people walked on the speaker -- each answer said
    (one by its letter), every why answered in words, the response taken -- then (the orb's) the check's No leaving
    before the plate and the screener's No before the film. `only`: the people by `who` (the face's three Nos)."""
    from harness import solution_surfaces as sol    # noqa: PLC0415
    view = "orb" if speaker == "ORB" else "avatar"
    people_ = [p for p in sol.SOLUTION_ROSTER if not only or p["who"] in only]
    extra = 0 if only else 2
    names = [f"Stranger {run.stamp} solution {view} {i}" for i in range(1, len(people_) + extra + 1)]
    links = make_links(run, project_id, names, fmt=fmt)
    out: dict = {"people": [], "walks": []}
    for n, (person, link) in enumerate(zip(people_, links)):
        plan = {"gate": True, "picks": person["picks"],
                "by": {sol.SOLUTION_DIMENSIONS[n % 3]: "letter"}}
        interview, _ = read_served(run, link["url"])
        walked = walk_link(run, link["url"], interview, shot=f"{view}-162-{n}", plan=plan)
        sent = first_response(walked)
        body = sent.get("sent") or {}
        whys = [r["follow_up"]["dimension"] for r in walked["rows"] if r.get("follow_up")]
        leg.check(run, f"{person['who']} on the {view}: owed {', '.join(person['owed']) or 'nothing'} -- each why asked "
                       f"({', '.join(whys) or 'none'}) and answered in words, the response taken (201)",
                  whys == person["owed"] and sent.get("status") == 201
                  and [f.get("dimension") for f in body.get("followUps") or []] == person["owed"],
                  screen="the three questions", view=view,
                  detail={"whys": whys, "status": sent.get("status"),
                          "rows": [(r.get("key"), r.get("question"), r.get("said")) for r in walked["rows"]
                                   if r.get("screen") == "question"]}, stop=False)
        out["people"].append({"who": person["who"], "whys": whys, "status": sent.get("status")})
        out["walks"].append({"url": link["url"], "interview": interview, "sent": body, "rows": walked["rows"]})
        if n == 0:
            solution_walk_checks(run, leg, walked, interview, view=view, label=f"{person['who']} on the {view}")
            keep_surface(run, "solution", "orb" if view == "orb" else "face", __import__(
                "harness.three_surfaces", fromlist=["walked_record"]).walked_record(walked["rows"]),
                source=f"the {view}'s walk (keel-web 260)")
    if extra:
        no_link = links[len(people_)]
        interview, _ = read_served(run, no_link["url"])
        walked = walk_link(run, no_link["url"], interview, shot=f"{view}-162-no", no_on="gate")
        body = first_response(walked).get("sent") or {}
        leg.check(run, f"a No on the check leaves with the thanks before the plate ({view}): no plate, no idea film, the "
                       "response `recency: false` with no answers",
                  not any(r.get("screen") == "plate" or (r.get("screen") == "film" and r.get("kind") == "idea")
                          for r in walked["rows"]) and body.get("recency") is False and not body.get("answers")
                  and bool(walked.get("done")), screen="the check's No", view=view,
                  detail={"order": solution_order(walked["rows"]), "sent": body, "done": walked.get("done")},
                  stop=False)
        screened = links[len(people_) + 1]
        interview, _ = read_served(run, screened["url"])
        walked = walk_link(run, screened["url"], interview, shot=f"{view}-162-screened",
                           plan={"screener": "no", "gate": True})
        body = first_response(walked).get("sent") or {}
        leg.check(run, f"the screener's No leaves before the film ({view}): no film, `outsideSegment: true`",
                  not [r for r in walked["rows"] if r.get("screen") == "film"] and body.get("outsideSegment") is True,
                  screen="the screener's No", view=view, detail={"sent": body}, stop=False)
    run.__dict__.setdefault("roster", {})[f"solution-{view}"] = out
    return out


def solution_page_on_screen(run, leg, project_id: str, standings: dict) -> None:
    """Spec 162 FR-8 on keel-web 260's screens: the solution's stage page -- each of the three cards drawn as the share
    bar (`data-chart="share"`, keel-web 260 FR-6), the founder's band shaded; no benefit scale drawn."""
    from evals import backtest    # noqa: PLC0415
    from harness import solution_surfaces as sol    # noqa: PLC0415
    page = run.page
    drawn: dict = {}
    try:
        page.goto(f"{run.web}/p/{project_id}/s/SOLUTION", wait_until="load")
        for key in sol.SOLUTION_DIMENSIONS:
            page.wait_for_selector(backtest.card_selector(key), state="visible", timeout=30_000)
            body = backtest.card_selector(key, backtest.CARD_BODY)
            if not page.evaluate("(sel) => !!document.querySelector(sel)", body):
                page.click(backtest.card_selector(key, backtest.CARD_OPEN))
            page.wait_for_selector(body, state="visible", timeout=10_000)
            drawn[key] = (page.evaluate(backtest.CARD_JS, key) or {}).get("chart") or {}
        ss._BrowserStep(run.recorder, page, "founder").screenshot("stage-solution-shares")
        bands = page.locator(".achart__shareband").count()
    except Exception as missed:  # noqa: BLE001 - the read named
        drawn["error"] = str(missed)[:300]
        bands = 0
    # keel-web 260 FR-6 (`DimensionRowBody`): the three are drawn as Prevalence is -- its strip on a people axis where the
    # card carries the strip, else the share bar (`data-chart="share"`, the founder's band shaded)
    leg.check(run, "the solution's three cards drawn as Prevalence's share (the strip on a people axis, or "
                   "`data-chart=\"share\"` with the founder's band; keel-web 260 FR-6), no benefit scale",
              "error" not in drawn and all((drawn.get(k) or {}).get("chart") in ("share", "strip")
                                           for k in sol.SOLUTION_DIMENSIONS)
              and not any("benefit" in str((drawn.get(k) or {}).get("chart")) for k in sol.SOLUTION_DIMENSIONS),
              screen="the stage page · the solution's three", view="founder (screen)", stop=False,
              detail={"drawn": {k: {f: (v or {}).get(f) for f in ("chart", "strip", "bar")} if isinstance(v, dict)
                                else v for k, v in drawn.items()}, "bands": bands})
