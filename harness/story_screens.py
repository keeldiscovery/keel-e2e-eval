"""Spec 157: keel-web 241 / 242 / 243's spoken founder screens and the stranger's three views on a story link, as page
objects -- machinery, not judgement (`evals/three_views.py` judges).

**The words the founder says are the cloud's own fixture.** keel-cloud 259 / 260 answer every story reading from one
fixed script wherever the fakes are routed (`src/main/resources/keel/story/fake-readings.json`, `FakeStoryReadings`:
an entry matched by its turn and the words as heard, anything else echoed); the walk reads that file off the stack's
own keel-cloud checkout and says (or types) its `heard` words, so the scripted readings answer, the build reaches
`ready` on the script's own draft, and nothing here names a trade (`said_turns`, `said_idea`). The Prevalence fields
the runtime's calibration answer carries are the cloud's own test fixture for the same story
(`src/test/resources/story/example-prevalence.json`, keel-cloud 259 judgement call 20).

**The founder's two paths** (keel-web 241 FR-2): *I would rather type the answers* (`story-start-type`: one box a
turn, `story-send`) and the spoken screen, driven through the test build's one seam (`window.__keelSpeech`, the same
`interviewer_screens.SPEECH_SEAM` the AI page uses): `__say(words)` pulses the recorder's level and puts the words in
the recording, the page's hands-free mic ends the answer on its own pause (`PAUSE_MS`, 1.5 s), writes it down through
`POST story/transcribe` -- keel-cloud's `FakeTranscriber` hears the recording's bytes as the words said (typed text in,
the same text out) -- and sends the turn. Nothing is pressed on the spoken path but what the founder would press with
their voice off: *No, that is it* on turn 5, the boxes' and the story's yes.

Every write a press makes is read off the response keel-web received, so the leg holds the wire the page was handed.
"""

from __future__ import annotations

import copy
import json
import re
import time
from pathlib import Path
from typing import Any

from harness.browser import _BrowserStep

# ------------------------------------------------------------------------------------ the cloud's own fixtures

#: keel-cloud 259 / 260: the fake readings' script (main resources: what the stack's fakes answer from).
FAKE_READINGS = "src/main/resources/keel/story/fake-readings.json"
#: keel-cloud 259 judgement call 20: the example's own Prevalence fields (test resources: the acceptance pair's chain).
EXAMPLE_PREVALENCE = "src/test/resources/story/example-prevalence.json"
#: keel-cloud 259 FR-5: the story library (rooms and pictograms by id).
STORY_LIBRARY = "src/main/resources/keel/story/story-library.json"


def fake_readings(keel_cloud: Path) -> dict:
    """The fake readings' script, read whole off the stack's keel-cloud checkout."""
    return json.loads((Path(keel_cloud) / FAKE_READINGS).read_text(encoding="utf-8"))


def example_prevalence(keel_cloud: Path) -> dict:
    """The example's four Prevalence fields (`routine`, `went_wrong`, `no_sayer`, `event`)."""
    raw = json.loads((Path(keel_cloud) / EXAMPLE_PREVALENCE).read_text(encoding="utf-8"))
    return {k: raw[k] for k in ("routine", "went_wrong", "no_sayer", "event")}


def story_library(keel_cloud: Path) -> dict:
    return json.loads((Path(keel_cloud) / STORY_LIBRARY).read_text(encoding="utf-8"))


def said_turns(script: dict) -> list[tuple[int, str]]:
    """The seven turns as the founder says them, in order: one utterance a turn, turn 6 one a limit (keel-cloud 259
    judgement call 8: one PUT a limitation) -- the script's `heard` words."""
    out = [(int(t["turn"]), str(t["heard"])) for t in script.get("turns") or []]
    if [n for n, _ in out if n != 6] != [1, 2, 3, 4, 5, 7]:
        raise ValueError(f"the fake readings' turns are not 1-7 with turn 6 repeated: {[n for n, _ in out]}")
    return out


def said_idea(script: dict) -> list[tuple[int, str]]:
    """keel-cloud 260's three idea turns as said: the name, what would be built, then one answer a limit."""
    return [(int(t["turn"]), str(t["heard"])) for t in script.get("ideaTurns") or []]


def reading_of(script: dict, turn: int, heard: str | None = None) -> dict:
    """The scripted result for `turn` (the first, or the one heard as `heard`)."""
    for t in script.get("turns") or []:
        if int(t["turn"]) == turn and (heard is None or t["heard"] == heard):
            return dict(t["result"])
    raise KeyError(f"no fake reading for turn {turn}")


def idea_reading_of(script: dict, turn: int, heard: str | None = None) -> dict:
    for t in script.get("ideaTurns") or []:
        if int(t["turn"]) == turn and (heard is None or t["heard"] == heard):
            return dict(t["result"])
    raise KeyError(f"no fake idea reading for turn {turn}")


def scripted_room(script: dict) -> str | None:
    """The room the script's draft draws the example in (its first `drafts` entry)."""
    drafts = script.get("drafts") or []
    return ((drafts[0] or {}).get("result") or {}).get("room_id") if drafts else None


def limits_read(script: dict) -> list[str]:
    """The limits the script reads turn 6's words as (each as written)."""
    return [str(t["result"]["limit"]) for t in script.get("turns") or [] if int(t["turn"]) == 6]


def condition_question(only_those_who: str | None) -> str | None:
    """The screener the runtime's RESPONDENT_QUESTIONS answer writes for a story whose turn 4 named a condition: *Do
    you {only those who}?* -- the founder's own words, one yes-or-no question (none where it happens to all of them)."""
    words = " ".join(str(only_those_who or "").split()).rstrip(".?")
    if not words:
        return None
    return f"Do you {words[0].lower() + words[1:]}?"


def context_interpret_result(script: dict, rhythm: str) -> dict:
    """keel-cloud 259's acceptance pair's `contextResultOfTheScript`, restated: what CONTEXT_INTERPRET answers for the
    story's own words -- the script's slots in the job's result shape (the window Save on 2 of 2 reads the context
    again, keel-web 241 FR-1). `rhythm` is the window's (keel-cloud `Rhythm.of`)."""
    who, when, everyone = reading_of(script, 1), reading_of(script, 3), reading_of(script, 4)
    return {"spelling": [],
            "occasion": {"noun": when.get("occasion"), "stem": when.get("occasion_stem"), "rhythm": rhythm},
            "actor": who.get("actor"), "actor_plural": who.get("actor_plural"),
            "job": reading_of(script, 2).get("job"), "circumstance": when.get("circumstance"),
            "segment": {"core": who.get("segment_core"), "condition": everyone.get("only_those_who")},
            "window": {"proposed": None}}


def rhythm_of(window: dict) -> str:
    """keel-cloud `Rhythm.of`: nights, days and working days DAILY, weeks WEEKLY, one or two months MONTHLY, three or
    more QUARTERLY."""
    unit = str(window.get("unit") or "NIGHTS").upper()
    if unit in ("NIGHTS", "DAYS", "WORKING_DAYS"):
        return "DAILY"
    if unit == "WEEKS":
        return "WEEKLY"
    return "QUARTERLY" if int(window.get("count") or 0) >= 3 else "MONTHLY"


def completed(result: dict) -> dict:
    return {"outcome": "COMPLETED", "result": result}


def story_runtime_script(base: dict, readings: dict, prevalence: dict, window: dict) -> dict:
    """The scripted runtime's script for a project the story defined (spec 157 judgement call 2): `base` is the
    harness's own script for the study's scope (`vectors_script.generate` on the 01-countly study of that scope, the
    lists, the faces and the readings the scripted journeys already walk), with exactly three answers made the
    story's own -- CONTEXT_INTERPRET from the story's slots (`context_interpret_result`), every PROBLEM calibration
    answer's Prevalence fields the cloud's own fixture for this story (`prevalence`; E7 / E9 read them against the
    story's context), and part 1's screener the story's own condition (`condition_question`). Nothing else moved; the
    `_source` line says so."""
    out = copy.deepcopy(base)
    everyone = reading_of(readings, 4)
    out["_story"] = ("spec 157: CONTEXT_INTERPRET, the PROBLEM calibration's Prevalence fields and part 1's screener are "
                     "the story's own (keel-cloud fake-readings.json, example-prevalence.json); the rest is "
                     f"{base.get('_entry_id')}'s")
    out["CONTEXT_INTERPRET"] = [completed(context_interpret_result(readings, rhythm_of(window)))]
    for screen, entries in out.items():
        if not screen.startswith("CALIBRATION_QUESTIONS") or not isinstance(entries, list):
            continue
        for entry in entries:
            result = entry.get("result") or {}
            if result.get("vector") != "PROBLEM":
                continue
            for q in result.get("questions") or []:
                if q.get("key") == "problem.prevalence":
                    for k, v in prevalence.items():
                        if k in q or k in ("routine", "went_wrong", "no_sayer", "event"):
                            q[k] = v
    question = condition_question(everyone.get("only_those_who"))
    for entry in out.get("RESPONDENT_QUESTIONS") or []:
        result = entry.get("result") or {}
        if result.get("part") == 1:
            # a solution study's anchor carries the gate's event (the problem's, keel-cloud 260 FR-5): the story's own
            for item in result.get("items") or []:
                if item.get("key") == "problem.prevalence" and "event" in item:
                    item["event"] = prevalence["event"]
            if question:
                result["condition"] = {"question": question, "inside": "YES"}
            else:
                result.pop("condition", None)
    return out


# ------------------------------------------------------------------------------------ the founder's screens (241)

STORY_START = "[data-testid=story-start]"
STORY_TURN = "[data-testid=story-turn]"
STORY_CHECK = "[data-testid=story-check]"
WINDOW_PATH = re.compile(r"/define/context/window")
#: keel-web 241 `lib/storyLines.ts` -- the seven questions (a turn screen's `h1.story-q`).
STORY_QUESTIONS = {1: "Who has this problem?", 2: "What are they trying to get done?", 3: "When does it happen?",
                   4: "Does it happen to all of them, or just to some?", 5: "How do they do it today?",
                   6: "What gets in the way?", 7: "And what does that cost them?"}
#: keel-web 241 FR-4 / `translate.ts` STORY: the story readback's two buttons.
STORY_YES = "Yes, that is exactly the problem"
STORY_YES_BACK = "Yes, exactly the problem · back to my solution"
#: keel-web 243 `translate.ts` MONEY: the two yeses from a money start.
STORY_YES_MONEY = "Yes, exactly the problem · back to will they pay"
IDEA_YES_MONEY = "Yes, exactly my idea · back to will they pay"


def _tc(locator) -> str:
    """A locator's words, or "" where it draws nothing -- read at once, never waited for (an absent element's
    `text_content` would wait out Playwright's default 30 s)."""
    try:
        if locator.count() == 0:
            return ""
        return " ".join((locator.first.text_content(timeout=2_000) or "").split())
    except Exception:  # noqa: BLE001 - a read
        return ""


def _texts(locator) -> list[str]:
    try:
        return [" ".join((t or "").split()) for t in locator.all_text_contents()]
    except Exception:  # noqa: BLE001 - a read
        return []


#: keel-web 080's guide welcome over a new project's first screen: its Skip (the walk passes it by, spec 054 FR-6).
GUIDE_SKIP = "[data-testid='guide-skip']"


def pass_the_welcome(page, *, wait_ms: int = 4000) -> bool:
    """keel-web 080's welcome opens over a new project's first screen (here the story's opening, on a project made from
    a start): pressed past with Skip where it draws within `wait_ms`. True where it was there."""
    deadline = time.monotonic() + wait_ms / 1000
    while time.monotonic() < deadline:
        skip = page.locator(GUIDE_SKIP)
        if skip.count() and skip.first.is_visible():
            skip.first.click()
            try:
                page.locator(".gw-scrim").first.wait_for(state="detached", timeout=10_000)
            except Exception:  # noqa: BLE001 - a scrim slow to go: Escape is Skip too (keel-web 080 FR-2.6)
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
            return True
        page.wait_for_timeout(200)
    return False


class FounderVoice:
    """The founder's microphone through the seam (`interviewer_screens.SPEECH_SEAM`, installed on the context): wait for
    the page's recorder to run, then say the words; the page does the rest."""

    def __init__(self, page):
        self.page = page

    def listening(self) -> bool:
        try:
            return bool(self.page.evaluate("() => !!(window.__listening && window.__listening())"))
        except Exception:  # noqa: BLE001 - a navigation in flight
            return False

    def wait_listening(self, timeout_s: float = 30) -> None:
        deadline = time.monotonic() + timeout_s
        while not self.listening():
            if time.monotonic() > deadline:
                raise AssertionError(f"the founder's microphone never opened on {self.page.url} (the hands-free mic, "
                                     "keel-web 241 FR-2)")
            self.page.wait_for_timeout(150)

    def say(self, words: str, *, timeout_s: float = 30) -> None:
        # a screen reached without the Start tap (after a navigation: keel-web 241 judgement call 6, 242 call 7) offers
        # *Tap to talk*: the founder taps it, as they would, before speaking
        talk = self.page.get_by_test_id("story-talk")
        if not self.listening() and talk.count() and talk.first.is_visible():
            talk.first.click()
        self.wait_listening(timeout_s)
        self.page.evaluate("(w) => window.__say(w, true)", words)

    def said(self) -> list:
        try:
            return self.page.evaluate("() => window.__said || []")
        except Exception:  # noqa: BLE001 - a read
            return []


class StoryWalk:
    """keel-web 241's founder flow on one project: the opening, the seven turns (typed or spoken), the boxes, the
    building screen and the story; every PUT the page sent and the answer it received kept (`writes`)."""

    def __init__(self, page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.voice = FounderVoice(page)
        self.writes: list[dict] = []
        self.turns_seen: list[dict] = []
        self._listening = False

    # ------------------------------------------------------------------------------------------- the wire
    def _keep(self, response) -> None:
        url = response.url.split("?")[0]
        if "/story" not in url and "/idea" not in url:
            return
        method = response.request.method
        if method not in ("PUT", "POST"):
            return
        try:
            body = response.json()
        except Exception:  # noqa: BLE001 - a clip or an empty body
            body = None
        try:
            sent = response.request.post_data_json
        except Exception:  # noqa: BLE001
            sent = None
        self.writes.append({"method": method, "path": url.split("/v2/")[-1], "status": response.status,
                            "sent": sent if isinstance(sent, dict) else None,
                            "body": body if isinstance(body, dict) else None})

    def listen(self) -> None:
        if not self._listening:
            self.page.on("response", self._keep)
            self._listening = True

    def stop_listening(self) -> None:
        if self._listening:
            self.page.remove_listener("response", self._keep)
            self._listening = False

    def turn_writes(self, n: int) -> list[dict]:
        return [w for w in self.writes if re.search(rf"/story/turns/{n}$", w["path"])]

    # ------------------------------------------------------------------------------------------- reads
    def screen(self) -> dict:
        """What the turn screen draws now: its turn and mode, the question, the bubbles, the person card's rows."""
        root = self.page.locator(STORY_TURN).first
        card = self.page.get_by_test_id("story-person-card")
        rows = {}
        for row in card.locator(".story-card__row").all():
            key = row.get_attribute("data-row") or ""
            rows[key] = {"label": _tc(row.locator("dt")), "value": _tc(row.locator("dd")),
                         "current": row.get_attribute("data-current") is not None}
        return {"turn": root.get_attribute("data-turn") if root.count() else None,
                "mode": root.get_attribute("data-mode") if root.count() else None,
                "question": _tc(self.page.locator("h1.story-q").first),
                "bubbles": [{"who": b.get_attribute("data-who"), "text": _tc(b.locator("p").first),
                             "note": _tc(b.locator(".story-bubble__note"))}
                            for b in self.page.get_by_test_id("story-conversation").locator("li").all()],
                "card": rows,
                "limits": [t.lstrip("×").strip() for t in _texts(card.get_by_test_id("story-card-limit"))],
                "sentence": _tc(card.get_by_test_id("story-card-sentence")) or None,
                "look": _tc(card.get_by_test_id("story-card-look")) or None,
                "dashes_on": self.page.locator("[data-testid=story-dashes] .story-dash[data-on]").count(),
                "url": self.page.url}

    def _wait_turn(self, n: int, timeout_s: float = 30) -> None:
        self.page.locator(f"{STORY_TURN}[data-turn='{n}']").first.wait_for(state="visible",
                                                                          timeout=timeout_s * 1000 * self.patience)

    def _wait_idle(self, timeout_s: float = 30) -> None:
        """No turn in flight (the typed box enabled again, or the page moved on)."""
        deadline = time.monotonic() + timeout_s * self.patience
        while time.monotonic() < deadline:
            busy = self.page.locator(f"{STORY_TURN} textarea[disabled]").count()
            if not busy:
                return
            self.page.wait_for_timeout(150)

    # ------------------------------------------------------------------------------------------- the opening
    def open_start(self, project_id: str) -> dict:
        with self._b.step("founder opens the story's opening (define/story/start)") as h:
            self.page.goto(f"{self.base}/p/{project_id}/define/story/start", wait_until="load")
            self.page.locator(STORY_START).first.wait_for(state="visible", timeout=30_000)
            welcomed = pass_the_welcome(self.page)
            seen = {"welcome passed": welcomed, "six": _texts(self.page.get_by_test_id("story-six").locator("li")),
                    "opening": _tc(self.page.get_by_test_id("story-opening")),
                    "start": _tc(self.page.get_by_test_id("story-start-go")),
                    "type": _tc(self.page.get_by_test_id("story-start-type"))}
            h.record_wire({"GET": "define/story/start"}, seen)
            h.add_screenshot(self._b.screenshot("story-start"))
            return seen

    def begin(self, mode: str) -> None:
        """`spoken`: Start (the tap that opens the mic and the sound); `typed`: *I would rather type the answers*."""
        with self._b.step(f"founder begins the story -- {'Start' if mode == 'spoken' else 'I would rather type the answers'}"):
            self.listen()
            self.page.get_by_test_id("story-start-go" if mode == "spoken" else "story-start-type").first.click()
            self._wait_turn(1, 60)

    # ------------------------------------------------------------------------------------------- one utterance
    def _put_after(self, n: int, act, *, timeout_s: float = 60) -> dict:
        before = len(self.turn_writes(n))
        act()
        deadline = time.monotonic() + timeout_s * self.patience
        while len(self.turn_writes(n)) <= before:
            if time.monotonic() > deadline:
                raise AssertionError(f"turn {n}: no PUT story/turns/{n} within {timeout_s} s of the founder's words "
                                     f"({self.page.url})")
            self.page.wait_for_timeout(150)
        return self.turn_writes(n)[-1]

    def utter(self, n: int, words: str, mode: str) -> dict:
        """One answer on turn `n`: typed into the box and sent, or said into the seam. Returns the PUT the page sent."""
        if mode == "typed":
            box = self.page.locator(f"#story-typed-{n}")
            box.wait_for(state="visible", timeout=30_000)
            self.page.wait_for_function("(el) => !el.disabled", arg=box.element_handle(), timeout=30_000)

            def act():
                box.fill(words)
                self.page.get_by_test_id("story-send").first.click()
            return self._put_after(n, act)
        return self._put_after(n, lambda: self.voice.say(words))

    def tell(self, turns: list[tuple[int, str]], mode: str) -> list[dict]:
        """Turns 1-7 on their screens, as a founder answers them: each turn's words; on turn 4 the readback's yes (spoken
        *yes*, typed the button); on turn 5 *No, that is it*; on turn 6 each limit then *That is all* (spoken *that is
        all*, typed the button); turn 7 the cost, then the boxes."""
        seen = []
        by_turn: dict[int, list[str]] = {}
        for n, words in turns:
            by_turn.setdefault(n, []).append(words)
        for n in range(1, 8):
            with self._b.step(f"turn {n}: {STORY_QUESTIONS[n]} -- {mode}") as h:
                self._wait_turn(n, 60)
                for words in by_turn.get(n, []):
                    put = self.utter(n, words, mode)
                    h.record_wire(put.get("sent"), {"status": put.get("status"),
                                                    "next": (put.get("body") or {}).get("next"),
                                                    "readback": (put.get("body") or {}).get("readback")})
                    if (put.get("status") or 500) >= 400:
                        raise AssertionError(f"turn {n} refused {put.get('status')}: {put.get('body')}")
                if n == 4:
                    self.page.get_by_test_id("story-person-check").first.wait_for(state="visible", timeout=30_000)
                    shown = self.screen()
                    if mode == "spoken":
                        self.voice.say("yes")
                    else:
                        self.page.get_by_test_id("story-yes-person").first.click()
                elif n == 5:
                    self.page.get_by_test_id("story-steps").first.wait_for(state="visible", timeout=30_000)
                    shown = self.screen()
                    shown["steps"] = _texts(self.page.get_by_test_id("story-steps").locator("li"))
                    yes = self.page.get_by_test_id("story-that-is-it").first
                    self.page.wait_for_function("(el) => !el.disabled", arg=yes.element_handle(), timeout=30_000)
                    yes.click()
                elif n == 6:
                    self.page.wait_for_function(
                        "(n) => document.querySelectorAll('[data-testid=story-card-limit]').length >= n",
                        arg=len(by_turn.get(6, [])), timeout=30_000)
                    shown = self.screen()

                    def close():
                        if mode == "spoken":
                            self.voice.say("that is all")
                        else:
                            self.page.get_by_test_id("story-that-is-all").first.click()
                    closed = self._put_after(6, close)
                    shown["closed"] = {"sent": closed.get("sent"), "next": (closed.get("body") or {}).get("next")}
                elif n == 7:
                    self.page.locator(STORY_CHECK).first.wait_for(state="visible", timeout=60_000)
                    shown = {"after": self.page.url}
                else:
                    self._wait_turn(n + 1, 60)
                    shown = {"after": self.page.url}
                h.add_screenshot(self._b.screenshot(f"story-turn-{n}-{mode}"))
                seen.append({"turn": n, "screen": shown})
        self.turns_seen = seen
        return seen

    # ------------------------------------------------------------------------------------------- the readbacks
    def boxes(self) -> dict:
        """The boxes readback (`define/story/check`, state boxes): the board's box words once drawn, then its yes."""
        with self._b.step("the boxes: This is the problem I understood -- the board drawn, then Yes, that is the problem") as h:
            screen = self.page.get_by_test_id("story-boxes-screen").first
            screen.wait_for(state="visible", timeout=30_000)
            self.page.wait_for_timeout(500)
            seen = {"title": _tc(screen.locator("h1").first), "text": _tc(screen),
                    "state": self.page.locator(STORY_CHECK).first.get_attribute("data-state"),
                    "back": self.page.get_by_test_id("story-back").count()}
            h.add_screenshot(self._b.screenshot("story-boxes"))
            yes = self.page.get_by_test_id("story-boxes-yes").first
            self.page.wait_for_function("(el) => !el.disabled", arg=yes.element_handle(), timeout=30_000)
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/story/confirm"), timeout=30_000) as got:
                yes.click()
            seen["confirm"] = {"status": got.value.status, "body": _json(got.value)}
            h.record_wire({"POST": "story/confirm"}, {"status": got.value.status})
            return seen

    def building_then_story(self, *, timeout_s: float = 60) -> dict:
        """The building screen while the build builds (its steps ticking), then the story readback once ready."""
        with self._b.step("the building screen, then the story in the phone frame") as h:
            building = None
            deadline = time.monotonic() + timeout_s * self.patience
            while time.monotonic() < deadline:
                state = self.page.locator(STORY_CHECK).first.get_attribute("data-state")
                if state == "building" and building is None:
                    building = {"steps": [{"step": li.get_attribute("data-step"), "state": li.get_attribute("data-state"),
                                           "words": _tc(li)}
                                          for li in self.page.locator(".story-build-steps li").all()]}
                    h.add_screenshot(self._b.screenshot("story-building"))
                if state in ("story", "failed"):
                    break
                self.page.wait_for_timeout(250)
            state = self.page.locator(STORY_CHECK).first.get_attribute("data-state")
            readback = self.page.get_by_test_id("story-readback")
            seen = {"building": building, "state": state,
                    "named": _tc(self.page.get_by_test_id("story-named")) or None,
                    "yes": _tc(self.page.get_by_test_id("story-yes")) or None,
                    "player": readback.locator(".sty-player, [data-testid=story-player]").count() if readback.count() else 0}
            h.add_screenshot(self._b.screenshot("story-readback"))
            h.record_assert({"state": "story"}, seen)
            return seen

    def story_yes(self, *, lands: re.Pattern | str = WINDOW_PATH) -> str:
        with self._b.step("the story's yes") as h:
            self.page.get_by_test_id("story-yes").first.click()
            pattern = re.compile(lands) if isinstance(lands, str) else lands
            deadline = time.monotonic() + 30 * self.patience
            while not pattern.search(self.page.url):
                if time.monotonic() > deadline:
                    raise AssertionError(f"the story's yes did not land on {pattern.pattern}: {self.page.url}")
                self.page.wait_for_timeout(200)
            h.record_wire({"press": "story-yes"}, {"url": self.page.url})
            h.add_screenshot(self._b.screenshot("story-yes-landed"))
            return self.page.url


def _json(response) -> dict | None:
    try:
        body = response.json()
        return body if isinstance(body, dict) else None
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------------------------ the solution start (242)

SOLUTION_START = "[data-testid=solution-start]"
IDEA_TURN = "[data-testid=idea-turn]"
IDEA_CHECK = "[data-testid=idea-check]"
#: keel-web 242 `lib/ideaLines.ts` BRAND_SWATCHES: the five colours of the brand's first option.
BRAND_SWATCHES = ("#2255aa", "#1f7a5a", "#b8432f", "#7a4fb0", "#c98a1b")
#: keel-web 242 `lib/solutionStart.ts`: the wait kept in the browser while a problem project is created.
PENDING_START_KEY = "keel.solutionStart"
COMPATIBILITY_PATH = re.compile(r"/define/solution/q/1(?:$|[?#])")


def problem_name_of(name: str) -> str:
    """keel-web 242 `problemNameOf`: the problem project's name, made from the solution's."""
    return f"{name.strip()}: the problem"


class SolutionStart:
    """keel-web 242's solution start (`SolutionPick`), walked on the landing before the solution project exists: Keel
    AI's line, the candidates (`solution-candidate`, `data-project`, `data-picked`), *Create a problem project* and
    *Pick* / *Continue with this problem*."""

    def __init__(self, page, recorder, base_url: str):
        self.page = page
        self.base = base_url.rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")

    def read(self) -> dict:
        root = self.page.locator(SOLUTION_START).first
        root.wait_for(state="visible", timeout=30_000)
        rows = []
        for row in root.get_by_test_id("solution-candidate").all():
            rows.append({"project": row.get_attribute("data-project"), "picked": row.get_attribute("data-picked") is not None,
                         "words": _tc(row), "press": _tc(row.get_by_test_id("solution-pick")),
                         "frame": row.get_by_test_id("solution-candidate-frame").count()})
        return {"say": _tc(root.get_by_test_id("solution-start-say")), "title": _tc(root.locator("h2").first),
                "rows": rows, "none": _tc(root.get_by_test_id("solution-start-none")) or None,
                "create": _tc(root.get_by_test_id("solution-create-problem")),
                "pending": self.pending()}

    def pending(self) -> dict | None:
        try:
            raw = self.page.evaluate("(k) => { try { return localStorage.getItem(k); } catch (e) { return null; } }",
                                     PENDING_START_KEY)
        except Exception:  # noqa: BLE001
            return None
        try:
            return json.loads(raw) if raw else None
        except ValueError:
            return {"unreadable": raw}

    def press_start(self) -> None:
        """The market step's *Start* on a solution scope: it opens the start, creating nothing."""
        self.page.get_by_role("button", name=re.compile(r"^start$", re.I)).first.click()
        self.page.locator(SOLUTION_START).first.wait_for(state="visible", timeout=30_000)

    def create_problem(self) -> str:
        """*Create a problem project*: one POST (scope PROBLEM, the problem's name), then its story's opening."""
        with self._b.step("solution start: Create a problem project") as h:
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.split("?")[0].endswith("/v2/projects"), timeout=30_000) as got:
                self.page.get_by_test_id("solution-create-problem").first.click()
            body = _json(got.value) or {}
            sent = got.value.request.post_data_json
            self.page.locator(STORY_START).first.wait_for(state="visible", timeout=30_000)
            h.record_wire(sent, {"status": got.value.status, "projectId": body.get("projectId"),
                                 "definition": body.get("definition"), "url": self.page.url})
            self.created_problem = {"sent": sent, "status": got.value.status, "body": body}
            return str(body.get("projectId"))

    def pick(self, problem_id: str | None = None) -> dict:
        """*Pick* (or *Continue with this problem* on the picked row): the one create request with `parentProjectId`."""
        with self._b.step("solution start: the problem picked -- the solution project created on it") as h:
            root = self.page.locator(SOLUTION_START).first
            row = (root.locator(f"[data-testid=solution-candidate][data-project='{problem_id}']").first if problem_id
                   else root.get_by_test_id("solution-candidate").first)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.split("?")[0].endswith("/v2/projects"), timeout=30_000) as got:
                row.get_by_test_id("solution-pick").click()
            body = _json(got.value) or {}
            sent = got.value.request.post_data_json
            h.record_wire(sent, {"status": got.value.status, "projectId": body.get("projectId"),
                                 "lineage": body.get("lineage")})
            return {"sent": sent, "status": got.value.status, "body": body}


class IdeaWalk:
    """keel-web 242's idea flow on a solution project: *Still the problem*, the three turns (the brand on turn 1), the
    boxes, the building screen and the day with the idea. Typed (the box) or spoken (the seam), as `StoryWalk`."""

    def __init__(self, page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.voice = FounderVoice(page)
        self.story = StoryWalk(page, recorder, base_url, patience=patience)      # its wire log and waits

    @property
    def writes(self) -> list[dict]:
        return self.story.writes

    def idea_writes(self, n: int) -> list[dict]:
        return [w for w in self.writes if re.search(rf"/idea/turns/{n}$", w["path"])]

    def _put_after(self, n: int, act, *, timeout_s: float = 60) -> dict:
        before = len(self.idea_writes(n))
        act()
        deadline = time.monotonic() + timeout_s * self.patience
        while len(self.idea_writes(n)) <= before:
            if time.monotonic() > deadline:
                raise AssertionError(f"idea turn {n}: no PUT idea/turns/{n} within {timeout_s} s ({self.page.url})")
            self.page.wait_for_timeout(150)
        return self.idea_writes(n)[-1]

    def still(self, project_id: str) -> dict:
        """`define/idea/start`: the picked problem read back -- the boxes, the story, *From {problem}* -- and its yes."""
        with self._b.step("still the problem: the picked problem read back, then Yes, still the problem") as h:
            self.story.listen()
            root = self.page.get_by_test_id("idea-still").first
            root.wait_for(state="visible", timeout=30_000)
            pass_the_welcome(self.page)
            seen = {"from": _tc(self.page.get_by_test_id("idea-still-from")) or None,
                    "ask": _tc(self.page.get_by_test_id("idea-still-ask")) or None, "url": self.page.url}
            h.add_screenshot(self._b.screenshot("idea-still"))
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/story/confirm"), timeout=30_000) as got:
                self.page.get_by_test_id("idea-still-yes").first.click()
            seen["confirm"] = {"status": got.value.status, "body": _json(got.value)}
            self.page.locator(f"{IDEA_TURN}[data-turn='1']").first.wait_for(state="visible", timeout=30_000)
            h.record_wire({"POST": "story/confirm"}, {"status": got.value.status, "url": self.page.url})
            return seen

    def _utter(self, n: int, words: str, mode: str) -> dict:
        if mode == "typed":
            box = self.page.locator(f"#idea-typed-{n}")
            box.wait_for(state="visible", timeout=30_000)
            self.page.wait_for_function("(el) => !el.disabled", arg=box.element_handle(), timeout=30_000)

            def act():
                box.fill(words)
                self.page.get_by_test_id("story-send").first.click()
            return self._put_after(n, act)
        return self._put_after(n, lambda: self.voice.say(words))

    def _mode_now(self) -> str | None:
        return self.page.locator(IDEA_TURN).first.get_attribute("data-mode")

    def type_instead(self) -> None:
        if self._mode_now() == "spoken" and self.page.get_by_test_id("story-type-instead").count():
            self.page.get_by_test_id("story-type-instead").first.click()

    def turns(self, said: list[tuple[int, str]], mode: str, *, swatch: str = BRAND_SWATCHES[1]) -> dict:
        """The three turns: the name, then the brand's colour (`swatch`); what would be built, then *Yes, that is it*;
        each limit's answer, then Next to the boxes."""
        seen: dict = {}
        by_turn: dict[int, list[str]] = {}
        for n, words in said:
            by_turn.setdefault(n, []).append(words)
        with self._b.step(f"idea turn 1: the name, then the brand's colour ({swatch}) -- {mode}") as h:
            if mode == "typed":
                self.type_instead()
            put = self._utter(1, by_turn[1][0], mode)
            h.record_wire(put.get("sent"), {"status": put.get("status"), "next": (put.get("body") or {}).get("next")})
            brand = self.page.get_by_test_id("idea-brand").first
            brand.wait_for(state="visible", timeout=30_000)
            with self.page.expect_response(lambda r: r.request.method == "PUT" and r.url.split("?")[0]
                                           .endswith("/idea/brand"), timeout=30_000) as got:
                self.page.locator(f"[data-testid=idea-swatch][aria-label*='{swatch}' i], "
                                  "[data-testid=idea-swatch]").nth(BRAND_SWATCHES.index(swatch)).click()
            seen["brand"] = {"status": got.value.status, "sent": got.value.request.post_data_json,
                             "body": _json(got.value)}
            h.add_screenshot(self._b.screenshot("idea-turn-1-brand"))
            nxt = self.page.get_by_test_id("story-next").first
            self.page.wait_for_function("(el) => !el.disabled", arg=nxt.element_handle(), timeout=30_000)
            nxt.click()
            self.page.locator(f"{IDEA_TURN}[data-turn='2']").first.wait_for(state="visible", timeout=30_000)
        with self._b.step(f"idea turn 2: what would be built, the line read back, Yes, that is it -- {mode}") as h:
            if mode == "typed":
                self.type_instead()
            put = self._utter(2, by_turn[2][0], mode)
            self.page.get_by_test_id("idea-readback").first.wait_for(state="visible", timeout=30_000)
            seen["readback"] = _tc(self.page.get_by_test_id("idea-readback"))
            h.record_wire(put.get("sent"), {"status": put.get("status"), "readback": seen["readback"]})
            h.add_screenshot(self._b.screenshot("idea-turn-2"))
            if mode == "spoken":
                self.voice.say("yes")
            else:
                self.page.get_by_test_id("idea-yes-line").first.click()
            self.page.locator(f"{IDEA_TURN}[data-turn='3']").first.wait_for(state="visible", timeout=30_000)
        with self._b.step(f"idea turn 3: each limit answered, a tick or a cross on the card -- {mode}") as h:
            if mode == "typed":
                self.type_instead()
            answers = []
            for words in by_turn.get(3, []):
                put = self._utter(3, words, mode)
                answers.append({"sent": put.get("sent"), "status": put.get("status"),
                                "next": (put.get("body") or {}).get("next")})
            self.page.get_by_test_id("idea-new-way").first.wait_for(state="visible", timeout=30_000)
            seen["limits"] = answers
            seen["new_way"] = _texts(self.page.get_by_test_id("idea-new-way").locator("li"))
            seen["card"] = _tc(self.page.get_by_test_id("idea-card"))
            seen["card_limits"] = [{"text": _tc(li), "state": li.get_attribute("data-state") or li.get_attribute("class")}
                                   for li in self.page.get_by_test_id("idea-card-limit").all()]
            h.record_wire({"turn 3": len(answers)}, seen)
            h.add_screenshot(self._b.screenshot("idea-turn-3"))
            nxt = self.page.get_by_test_id("story-next").first
            self.page.wait_for_function("(el) => !el.disabled", arg=nxt.element_handle(), timeout=30_000)
            nxt.click()
            self.page.locator(IDEA_CHECK).first.wait_for(state="visible", timeout=30_000)
        return seen

    def boxes(self) -> dict:
        with self._b.step("the idea's boxes, then Yes, that is my idea") as h:
            screen = self.page.get_by_test_id("idea-boxes-screen").first
            screen.wait_for(state="visible", timeout=30_000)
            self.page.wait_for_timeout(500)
            seen = {"text": _tc(screen)}
            h.add_screenshot(self._b.screenshot("idea-boxes"))
            yes = self.page.get_by_test_id("idea-boxes-yes").first
            self.page.wait_for_function("(el) => !el.disabled", arg=yes.element_handle(), timeout=30_000)
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/idea/confirm"), timeout=30_000) as got:
                yes.click()
            seen["confirm"] = {"status": got.value.status, "body": _json(got.value)}
            h.record_wire({"POST": "idea/confirm"}, {"status": got.value.status})
            return seen

    def building_then_story(self, *, timeout_s: float = 60) -> dict:
        with self._b.step("the idea's building screen, then the day with the idea") as h:
            building = None
            deadline = time.monotonic() + timeout_s * self.patience
            while time.monotonic() < deadline:
                state = self.page.locator(IDEA_CHECK).first.get_attribute("data-state")
                if state == "building" and building is None:
                    building = {"rows": _texts(self.page.get_by_test_id("idea-building").locator("li"))}
                    h.add_screenshot(self._b.screenshot("idea-building"))
                if state in ("story", "failed"):
                    break
                self.page.wait_for_timeout(250)
            state = self.page.locator(IDEA_CHECK).first.get_attribute("data-state")
            seen = {"building": building, "state": state,
                    "yes": _tc(self.page.get_by_test_id("idea-story-yes")) or None}
            h.add_screenshot(self._b.screenshot("idea-story"))
            h.record_assert({"state": "story"}, seen)
            return seen

    def story_yes(self, lands: re.Pattern = COMPATIBILITY_PATH) -> str:
        with self._b.step("the idea's story's yes") as h:
            self.page.get_by_test_id("idea-story-yes").first.click()
            deadline = time.monotonic() + 30 * self.patience
            while not lands.search(self.page.url):
                if time.monotonic() > deadline:
                    raise AssertionError(f"the idea's story's yes did not land on {lands.pattern}: {self.page.url}")
                self.page.wait_for_timeout(200)
            h.add_screenshot(self._b.screenshot("idea-landed"))
            return self.page.url


# ------------------------------------------------------------------------------------ the stranger's text view (241 FR-7)

IV_BEGIN, IV_CONTINUE, IV_NEXT, IV_SEND = "Begin", "Continue", "Next", "Send my answers"
#: keel-web `ExitScreen` / the thank-you's heading words (the exit after a gate No, outside, or a check's No).
EXIT_TITLE = "That's it."
#: keel-web 241 FR-7: the story card's chrome.
STORY_KICKER = "Before the questions"
VOICE_READS = "Keel AI reads this card aloud"


def served_cards(interview: dict) -> list[dict]:
    """Every card the wire serves that carries words a stranger answers (the screener, the gate, each item, the
    decision-maker's check): `{kind, itemId, clipId}` -- keel-cloud 259 FR-9 owes a `clipId` on each of a story link."""
    out = []
    gate = interview.get("gate") or None
    if gate:
        if gate.get("condition"):
            out.append({"kind": "screener", "itemId": "condition", "clipId": gate["condition"].get("clipId")})
        out.append({"kind": "gate", "itemId": gate.get("itemId"), "clipId": gate.get("clipId")})
    elif interview.get("condition"):
        out.append({"kind": "screener", "itemId": "condition", "clipId": interview["condition"].get("clipId")})
    check = interview.get("problemCheck") or None
    if check:
        out.append({"kind": "check", "itemId": check.get("itemId") or "problemCheck", "clipId": check.get("clipId")})
    for part in interview.get("parts") or []:
        for item in part.get("items") or []:
            out.append({"kind": "item", "itemId": item.get("itemId"), "dimension": item.get("dimension"),
                        "clipId": item.get("clipId")})
    return out


def _norm(text: str | None) -> str:
    return " ".join(str(text or "").split()).strip().lower()


class StoryLinkText:
    """The stranger's text page on a story link (keel-web 241 FR-7, 242 FR-4, 243 FR-2), walked by what it draws: the
    screener on its own card, the story card, the gate (or the anchor, or the decision-maker's check), the story
    question with its chips, each item, the idea card and the idea's story card, the follow-ups (skipped), the done or
    the exit screen. Every card drawn is recorded with its voice bar, its still, its bubbles and its letters; each item
    is answered with its escape where it has one, else its first bubble -- the walk asserts nothing."""

    def __init__(self, page, recorder):
        self.page = page
        self._b = _BrowserStep(recorder, page, "participant")
        self.screens: list[dict] = []

    def _card(self, kind: str, extra: dict | None = None) -> dict:
        main = self.page.locator("main").first
        bubbles = main.locator(".cpl-bubbles")
        voice = main.get_by_test_id("card-voice")
        row = {"screen": kind,
               "question": _tc(main.locator("h1.iv-q").first) or _tc(main.locator("h1").first),
               "kicker": _tc(main.locator(".iv-kicker").first) or None,
               "voice": voice.count(), "voice_words": _tc(voice.first.locator(".iv-voice__words")) if voice.count() else None,
               "mute": main.get_by_test_id("card-voice-mute").count(),
               "still": main.locator(".iv-still").count(),
               "bubbles": bubbles.count(),
               "letters": _texts(main.locator(".cpl-bubble__let")),
               "rows": _texts(main.locator(".cpl-bubble__w")) or _texts(main.locator("[role=radio]")),
               "chips": _texts(main.locator(".iv-chips button")),
               "data_story": self.page.locator(".iv-page[data-story]").count()}
        if extra:
            row.update(extra)
        self.screens.append(row)
        return row

    def _press(self, name: str) -> None:
        self.page.get_by_role("button", name=name, exact=True).first.click()

    @staticmethod
    def _pick(root, index: int) -> None:
        """The `index`-th answer on a card: a lettered bubble (`label.cpl-bubble`, its radio visually hidden) where the
        card draws them, else the row's radio."""
        bubbles = root.locator("label.cpl-bubble")
        if bubbles.count() > index:
            bubbles.nth(index).click()
        else:
            root.get_by_role("radio").nth(index).click()

    def _kind(self, gate_question: str | None = None) -> str:
        page = self.page
        h1 = _tc(page.locator("h1").first)
        if gate_question and _norm(_tc(page.locator("main h1.iv-q").first)) == _norm(gate_question):
            return "gate"
        if h1 == EXIT_TITLE or page.locator("main .iv-done").count():
            return "done"
        for testid, kind in (("condition-screen", "condition"), ("story-screen", "story"),
                             ("idea-story-screen", "ideaStory"), ("iv-follow-up", "followUp"),
                             ("problem-check-screen", "check")):
            if page.get_by_test_id(testid).count():
                return kind
        if page.locator("main .iv-control, main .iv-chips, main .cpl-bubbles").count():
            return "item"
        if page.get_by_role("button", name=IV_CONTINUE, exact=True).count():
            return "reveal"
        return "unknown"

    def open(self, url: str) -> None:
        self.page.goto(url, wait_until="load")
        self.page.get_by_role("button", name=IV_BEGIN, exact=True).first.wait_for(state="visible", timeout=30_000)

    def walk(self, url: str, interview: dict, *, no_on: str | None = None, story: str = "",
             max_screens: int = 60) -> dict:
        """Begin, then every screen to the end. `no_on` -- `gate` (the problem's gate or the solution's anchor) or
        `check` (the decision-maker's third-person check) -- answers that one No; the walk then expects the exit."""
        page = self.page
        items = [i for part in interview.get("parts") or [] for i in part.get("items") or []]
        gate = interview.get("gate") or {}
        with self._b.step(f"the stranger walks the text view{' -- No on the ' + no_on if no_on else ''}") as h:
            self.open(url)
            h.add_screenshot(self._b.screenshot("text-intro"))
            self._press(IV_BEGIN)
            page.wait_for_timeout(600)
            response = None
            for _ in range(max_screens):
                kind = self._kind(gate.get("question"))
                if kind == "done":
                    break
                if kind == "condition":
                    self._card("condition")
                    self._pick(page.get_by_test_id("condition-screen").first, 0)
                    self._press(IV_CONTINUE)
                elif kind in ("story", "ideaStory"):
                    root = page.get_by_test_id("story-screen" if kind == "story" else "idea-story-screen").first
                    self._card(kind, {"player": root.locator("[data-testid=story-player], [data-testid=idea-story-player]")
                                      .count(), "read_instead": root.get_by_test_id("story-read-instead").count(),
                                      "title": _tc(root.locator("h1").first),
                                      "introduced": root.get_attribute("data-introduced") is not None})
                    h.add_screenshot(self._b.screenshot(f"text-{kind}"))
                    self._press(IV_CONTINUE)
                elif kind == "check":
                    root = page.get_by_test_id("problem-check-screen").first
                    row = self._card("check")
                    no = no_on == "check"
                    self._pick(root, 1 if no else 0)
                    h.add_screenshot(self._b.screenshot("text-check"))
                    self._press(IV_CONTINUE)
                elif kind == "gate":
                    no = no_on == "gate"
                    group = page.locator("main [role=radiogroup]").first
                    self._pick(group, 1 if no else 0)
                    page.wait_for_timeout(300)
                    row = self._card("gate", {"gate_question": gate.get("question")})
                    if not no:
                        box = page.locator("main textarea").first
                        box.fill(story or "It happened last week, and it took the whole afternoon.")
                        row["story_prompt"] = _tc(page.locator("main .iv-story p").first)
                        row["story_chips"] = _texts(page.locator("main .iv-story .iv-chips button"))
                        row["story_still"] = page.locator("main .iv-story .iv-still").count()
                    h.add_screenshot(self._b.screenshot("text-gate"))
                    self._press(IV_CONTINUE)
                elif kind == "followUp":
                    self._card("followUp")
                    page.get_by_test_id("iv-follow-up-skip").first.click()
                elif kind == "item":
                    stem = _norm(_tc(page.locator("main h1.iv-q").first))
                    stem_full = _norm(_tc(page.locator("main [data-testid=item-stem]").first) + " " + stem)
                    item = next((i for i in items if _norm(i.get("text")) and (_norm(i.get("text")) in stem_full
                                                                            or stem in _norm(i.get("text")))), {})
                    self._card("item", {"dimension": item.get("dimension")})
                    escape = (item.get("escape") or {}).get("label")
                    chip = page.locator("main .iv-chips").get_by_role("button", name=escape, exact=True) if escape else None
                    if chip is not None and chip.count():
                        chip.first.click()
                    elif page.locator("main label.cpl-bubble").count():
                        page.locator("main label.cpl-bubble").first.click()
                    elif page.locator("main").get_by_role("radio").count():
                        page.locator("main").get_by_role("radio").first.click()
                    elif page.locator("main .iv-chips button").count():
                        page.locator("main .iv-chips button").first.click()
                    page.wait_for_timeout(300)
                    second = page.locator("main .iv-chips").get_by_role("button", name="Nothing else", exact=True)
                    if second.count() and second.first.is_visible():
                        # Importance's second ask (*And one more?*, keel-cloud 158): one pick is a whole answer
                        second.first.click()
                    before = stem
                    send = page.get_by_role("button", name=IV_SEND, exact=True)
                    if send.count():
                        with page.expect_response(lambda r: r.request.method == "POST"
                                                  and r.url.split("?")[0].endswith("/interview/response"),
                                                  timeout=60_000) as answered:
                            send.first.click()
                            # a follow-up asked at the end comes first: skip it, then the response goes
                            for _ in range(4):
                                page.wait_for_timeout(800)
                                if page.get_by_test_id("iv-follow-up").count():
                                    self._card("followUp")
                                    page.get_by_test_id("iv-follow-up-skip").first.click()
                                else:
                                    break
                        response = {"status": answered.value.status, "body": answered.value.request.post_data_json}
                    else:
                        self._press(IV_NEXT)
                        deadline = time.monotonic() + 10
                        while time.monotonic() < deadline and _norm(_tc(page.locator("main h1.iv-q").first)) == before \
                                and self._kind(gate.get("question")) == "item":
                            page.wait_for_timeout(200)
                elif kind == "reveal":
                    self._card("reveal", {"card": _tc(page.locator("main").first)[:400],
                                          "brand": page.locator("main [data-testid=brand-mark], main .idea-brand-mark")
                                          .count()})
                    self._press(IV_CONTINUE)
                else:
                    page.wait_for_timeout(500)
                    if self._kind(gate.get("question")) == "unknown":
                        raise AssertionError(f"the text view drew a screen the walk cannot read: {page.url} "
                                             f"{_tc(page.locator('main').first)[:300]!r}")
                page.wait_for_timeout(400)
            if response is None and (no_on or True):
                # an exit's response (a No) is posted on its Continue; read it off what the wire holds
                pass
            page.locator("h1").first.wait_for(state="visible", timeout=30_000)
            done = _tc(page.locator("h1").first)
            h.add_screenshot(self._b.screenshot(f"text-done{'-' + no_on if no_on else ''}"))
            h.record_wire({"url": url, "no_on": no_on}, {"screens": self.screens, "done": done, "response": response})
            return {"screens": list(self.screens), "done": done, "response": response,
                    "exit": done == EXIT_TITLE}
