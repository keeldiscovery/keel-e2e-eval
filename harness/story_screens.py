"""Spec 157 / 158: the founder's spoken screens and the stranger's three views on a story link, as page objects --
machinery, not judgement (`evals/three_views.py` judges).

**Spec 158: the conversation** (keel-web 245 on keel-cloud 263, contract 83). The founder's screens are the orb and the
words: four beats, one long answer each (1 who; 2 what and when; 3 every limitation, in one breath; 4 all of them or
some), and beat 5 (the when) only where beat 2 named no moment. **Nothing is pressed**: no *Tap to talk*, *Type
instead*, *Send*, *That is all*, *Yes* / *Not quite*. The walk gets past the stage's opener (the guide's film, its Skip
the first tap) or taps the orb on the begin screen (*Tap me to begin.*), speaks through the test build's seam
(`window.__keelSpeech`: `__say(words)` is the founder speaking, `__listening()` the recorder running; a real pause of
2.5 s sends the answer, written down by `POST story/transcribe` -- keel-cloud's `FakeTranscriber` hears the words as
said), and lets the quiet after every readback pass with `window.__keelSilence()` (it answers the conversation's quiet
wait at once and says whether one stood). The orb's `data-state` is logged through every screen by `ORB_WATCH` (an
init script beside the seam), so a leg can hold *speaking -> listening -> hearing -> writing -> speaking*.

**The words the founder says are the cloud's own fixture.** keel-cloud 263 answers every story reading from one fixed
script wherever the fakes are routed (`src/main/resources/keel/story/fake-readings.json`, `FakeStoryReadings`: an
entry matched by its beat, the words as heard and whether it is a correction; anything else echoed back by code); the
walk reads that file off the stack's own keel-cloud checkout and says its `heard` words (`said_turns`, `said_idea`), so
the scripted readings answer and the build reaches `ready` on the script's own draft. Beat 3's long answer
(`long_beat_3`) is the script's own limitations, two more in its own vocabulary and its own cost, told at length: no
trade, company or title is named here beyond the script's. The Prevalence fields the runtime's calibration answer carries
are the cloud's own test fixture (`src/test/resources/story/example-prevalence.json`, keel-cloud 259 judgement call 20).

Every write the page makes is read off the response keel-web received, so the leg holds the wire the page was handed.

**Spec 161: seven beats** (keel-cloud 268 on contract 85-87, keel-web 257). The founder is asked seven beats: 1 who;
2 what and when; 3 how they do it today and where that falls short, in one breath; 4 what that costs them; 5 all or
some; 6 the when, only where beat 2 named no moment; 7 two or three other tasks of the role. Beats 3, 4 and 7 are the
long beats (keel-web 257 FR-11, `LONG_BEATS`): they never close on quiet -- the walk ends each by saying a done word
(*That's it.*) as its last words, and the words sent carry none. The board reads seven rows (who, job, when, today,
falls short, costs, other tasks); after the film's yes Keel says the served `verdictLine` (`story-verdict`) and, on a
spoken PROBLEM project, no belief page is drawn. The film's seventh scene is the pain (`pain: true`, `costLine` its
line). `limits_only_beat_3` / `way_answer` are the one telling whose beat 3 names no way, so code's one ask (*And how do
they do it today?*) is walked; `two_part_beat_3` is beat 3 said in two parts across seven seconds of quiet.
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

#: keel-cloud 259 / 260 / 263: the fake readings' script (main resources: what the stack's fakes answer from).
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


def _answers(script: dict, key: str) -> list[dict]:
    """A script's entries that answer a beat (a correction's entry answers a readback, not the beat)."""
    return [t for t in script.get(key) or [] if not t.get("correction")]


#: Spec 161 FR-1 (keel-cloud 268 FR-3): the founder's seven beats in order -- 1 who, 2 what and when, 3 the way and every
#: limitation, 4 the cost, 5 all or some, 6 the when (owed only where beat 2 named no moment), 7 the role's other tasks.
BEATS = (1, 2, 3, 4, 5, 6, 7)
#: keel-cloud 268 `StoryTurns`: the cost (4), all or some (5), the when (6), the other tasks (7).
COST_BEAT, ALL_OF_THEM_BEAT, WHEN_BEAT, OTHER_TASKS_BEAT = 4, 5, 6, 7


def said_turns(script: dict) -> list[tuple[int, str]]:
    """keel-cloud 268's beats as the founder says them, in order -- one answer a beat: 1 who, 2 what and when, 3 the way
    and every limitation in one answer, 4 the cost, 5 all of them or some, 6 the when where beat 2 named no moment, and
    7 the role's other tasks -- the script's `heard` words (a correction's entry is not a beat). The script's first story
    only: keel-cloud 263c (`1fb1fa71`) adds more tellings after it (another who, beat 2 said several ways), where the
    beats start again at 1. Any other order is refused by name (spec 161 FR-1)."""
    out: list[tuple[int, str]] = []
    for t in _answers(script, "turns"):
        n = int(t["turn"])
        if out and n <= out[-1][0]:
            break
        out.append((n, str(t["heard"])))
    beats = [n for n, _ in out]
    if beats not in ([1, 2, 3, 4, 5, 6, 7], [1, 2, 3, 4, 5, 7]):
        raise ValueError(f"the fake readings' beats are not keel-cloud 268's seven (1-5, 6 where owed, 7): {beats}")
    return out


def reading_of(script: dict, turn: int, heard: str | None = None, *, correction: bool = False) -> dict:
    """The scripted result for beat `turn` (the first, or the one heard as `heard`; a correction's where asked)."""
    for t in script.get("turns") or []:
        if int(t["turn"]) == turn and bool(t.get("correction")) == correction \
                and (heard is None or t["heard"] == heard):
            return dict(t["result"])
    raise KeyError(f"no fake reading for beat {turn}{' (a correction)' if correction else ''}")


def moment_beat(script: dict) -> int:
    """The beat whose reading names the moment: 2 where its one answer carried the when, else 6 (keel-cloud 268 FR-3;
    263's beat 5 before it)."""
    return 2 if reading_of(script, 2).get("circumstance") else WHEN_BEAT


def scripted_room(script: dict) -> str | None:
    """The room the script's draft draws the example in (its first `drafts` entry)."""
    drafts = script.get("drafts") or []
    return ((drafts[0] or {}).get("result") or {}).get("room_id") if drafts else None


def scripted_who(script: dict) -> str | None:
    """The boxes' *who* the script's draft is matched on (a story told with another who is drawn by code's draft)."""
    drafts = script.get("drafts") or []
    return (drafts[0] or {}).get("who") if drafts else None


def limits_read(script: dict) -> list[str]:
    """The limitations the script reads beat 3's one answer as (each as written, in order)."""
    return [str(x) for x in reading_of(script, 3).get("limits") or []]


def heard_cost(script: dict) -> str | None:
    """The cost the script hears said in passing on beat 3 (263 FR-2b's `heard.cost`), or None. Spec 161 FR-1: such a
    cost is on the board before beat 4, and beat 4 is still asked (keel-cloud 268 FR-2)."""
    return ((reading_of(script, 3).get("heard") or {}).get("cost")) or None


def steps_read(script: dict) -> list[str]:
    """Spec 161 FR-1 (keel-cloud 268 FR-1): today's way the script reads beat 3's one answer as -- its steps, in order."""
    return [str(x) for x in reading_of(script, 3).get("steps") or []]


def act_read(script: dict) -> str | None:
    """Spec 161 FR-1: the -ing phrase of today's way the script reads beat 3 as (`act`), or None."""
    return reading_of(script, 3).get("act") or None


def cost_read(script: dict) -> str | None:
    """Spec 161 FR-1 (keel-cloud 268 FR-2): the cost the script reads beat 4 as."""
    return reading_of(script, COST_BEAT).get("cost") or None


def other_tasks_read(script: dict) -> list[str]:
    """Spec 161 FR-1 (keel-cloud 268 FR-3): the role's other tasks the script reads beat 7 as."""
    return [str(x) for x in reading_of(script, OTHER_TASKS_BEAT).get("other_tasks") or []]


def tasks_correction(script: dict) -> tuple[str, list[str]] | None:
    """Spec 161 FR-1 (keel-cloud 268 FR-4): the cloud's own correction of the other tasks -- the words said on the board
    and the whole new list they are read as (`fake-readings.json`'s `corrections` entry that writes `other_tasks`), or
    None where the script carries none."""
    for entry in script.get("corrections") or []:
        tasks = (entry.get("result") or {}).get("other_tasks")
        if tasks:
            return str(entry["heard"]), [str(t) for t in tasks]
    return None


# ------------------------------------------------------------------------------------ the long beats (keel-web 257)

#: keel-web 257 FR-11 (`LONG_BEATS` in `storyLines.ts`): the beats that never close on quiet alone.
LONG_BEATS = (3, 4, 7)
#: keel-web 257 FR-11 (`DONE_WORDS`): the words that close a long beat when they are the answer's last words.
DONE_WORDS = ("that's it", "that's all", "that is all", "I'm done", "done", "that is everything", "you can go on")
#: The done word the walk says (spec 161 FR-1: *that's it*).
DONE_WORD = "That's it."
#: keel-web 257 FR-11 (translate): the state line after `THINK_MS` of quiet on a long beat, and the line under the orb
#: while a long beat listens.
THINK_LINE = "Take your time."
LONG_BEAT_SUB = 'Take your time. Say "that\'s it" when you are done.'
#: keel-web 257 FR-11: quiet on a long beat dims the orb after 6 s (`THINK_MS`); *Anything else?* at 20 s.
THINK_MS = 6_000
ANYTHING_ELSE_MS = 20_000
#: Spec 161 FR-1: the quiet between the two parts of beat 3 on one founder leg -- past `THINK_MS`, short of 20 s.
TWO_PART_QUIET_S = 7.0
_DONE_TAIL = re.compile(r"(?i)[\s,.;:!-]*\b(?:" + "|".join(re.escape(w).replace("'", "['\u2019]")
                                                       for w in sorted(DONE_WORDS, key=len, reverse=True))
                        + r")[\s.!]*$")


def with_done_word(words: str) -> str:
    """A long beat's answer as the walk says it: the words, then the done word as their last words."""
    return f"{str(words).rstrip()} {DONE_WORD}"


def ends_on_a_done_word(text: str | None) -> bool:
    """Whether words end on a done word (keel-web 257 FR-11: only as the last words is it a close; inside a sentence it
    is not)."""
    return bool(_DONE_TAIL.search(str(text or "")))


_DONE_STRIP = re.compile(r"(?i)\s*\b(?:" + "|".join(re.escape(w).replace("'", "['\u2019]")
                                                  for w in sorted(DONE_WORDS, key=len, reverse=True))
                         + r")[\s.!]*$")


def without_done_word(text: str) -> str:
    """The words a long beat sends: the done word at their end stripped (keel-web 257 FR-11), the words' own last
    stop kept."""
    return _DONE_STRIP.sub("", str(text or "")).rstrip(" ,;:-")


#: Spec 158 FR-1: beat 3's long answer is at least this long (keel-cloud 263 FR-2a: no 240 cut).
LONG_ANSWER_MIN = 1500
#: keel-cloud 263 FR-2a: the most a beat's words may be (20,000 characters); keel-cloud's FakeTranscriber hears up to
#: 4 KB of a recording as its words, so the long answer stays under that.
LONG_ANSWER_MAX = 4000
#: The two limitations the long answer adds to the script's three, in the script's own vocabulary (the managers, the
#: report): no trade, company or title named.
MORE_LIMITS = ("Managers take days to answer their questions", "The report comes out late in the day")
#: The rest of the telling, one clause at a time, said after the fifth limitation in one long sentence (commas only, so
#: an unscripted reading of beat 3 -- each sentence a row -- keeps the four rows the answer opens with).
_TELLING = (
    "so everything they do has to fit into the last hours before the run is signed off",
    "and they sit with the report open on one side and last period's on the other",
    "going down it line by line and marking anything that looks different",
    "then they write to the managers about every line they cannot explain",
    "and they wait, and while they wait the rest of the checks pile up behind it",
    "and some weeks the answers come back after the money has already gone out",
    "and the hours still do not match what the managers said",
    "and nobody has told them that a rate moved in the middle of the period",
    "and then {cost}, which is the part that really costs them",
    "because then they have to put it right by hand the next period",
    "and explain it to the person who was paid wrong",
    "and to the managers who did not answer in time",
    "and it starts again the next time the run is ready to be signed off",
    "and they never feel sure that this time they caught all of it",
)


def _lower(text: str) -> str:
    return text[:1].lower() + text[1:] if text else text


def long_beat_3(script: dict) -> tuple[str, list[str]]:
    """Beat 3 told the long way (spec 158 FR-1; spec 161 FR-1: the way as well as the limitations): today's way in one
    sentence opening *Today they* (keel-cloud 268's fake reads it as the steps), five limitations in one breath -- the
    script's three, then two more -- and the cost said in passing in its own sentence (*In the end ...*: heard on beat 3,
    on the board before beat 4), over at least 1,500 characters. The first four limitations are a sentence each (the
    cloud's fake reader, `FakeStoryReadings`, reads an unscripted beat 3 a sentence a row and keeps four), the fifth and
    the rest of the telling one long last sentence. Returns the words and the four rows a reading keeps."""
    limits = (limits_read(script) + list(MORE_LIMITS))[:5]
    rows = limits[:4]
    cost = _lower(heard_cost(script) or "someone gets paid wrong")
    head = f"{way_sentence(script)} " + " ".join(f"{row}." for row in rows) + f" In the end, {cost}."
    tail = [f"And {_lower(limits[4])}"]
    for clause in _TELLING:
        tail.append(clause.format(cost=cost))
    words = f"{head} {', '.join(tail)}."
    while len(words) < LONG_ANSWER_MIN:            # never: the telling is longer; kept so the rule is the code's
        words = words[:-1] + ", " + ", ".join(c.format(cost=cost) for c in _TELLING) + "."
    if len(words) > LONG_ANSWER_MAX:
        raise ValueError(f"the long answer is {len(words)} characters, over the transcriber's {LONG_ANSWER_MAX}")
    return words, rows


def way_sentence(script: dict) -> str:
    """Today's way as one sentence opening *Today they* -- the script's own steps joined by *then* (keel-cloud 268's
    fake reader, `FakeStoryReadings`, reads such a sentence as the steps, in order)."""
    steps = [_lower(x) for x in steps_read(script)] or ["do it by hand"]
    return "Today they " + ", then ".join(steps) + "."


def limits_only_beat_3(script: dict) -> str:
    """Spec 161 FR-1 (keel-cloud 268 FR-1): beat 3 answered with the limitations alone -- the script's own, a sentence
    each, no way named -- so code asks once, *And how do they do it today?* (`WAY_ASK`)."""
    return " ".join(f"{row}." for row in limits_read(script))


def way_answer(script: dict) -> str:
    """The words said after the way's one ask: today's way, its steps joined by *then* (read as the way: the steps, the
    act from the first)."""
    steps = [_lower(x) for x in steps_read(script)] or ["do it by hand"]
    return "They " + ", then ".join(steps) + "."


def two_part_beat_3(script: dict) -> tuple[str, str]:
    """Spec 161 FR-1 (keel-web 257 FR-11): beat 3 said in two parts with seven seconds of quiet between them -- the way
    and the first limitations, then the rest -- which the page joins into one answer, closed by the done word."""
    rows = limits_read(script)
    first = f"{way_sentence(script)} " + " ".join(f"{row}." for row in rows[:2])
    second = " ".join(f"{row}." for row in rows[2:]) or "And it happens again the next time."
    return first, second


#: keel-cloud 268 FR-1 (`StoryTurns.WAY_ASK`): beat 3's one ask where the words named limitations but no way.
WAY_ASK = "And how do they do it today?"


#: Spec 158 FR-1: the correction said after beat 4's readback (the spec's own words), through the fake mic.
CORRECTION_4 = "only the ones in Europe"
#: Spec 158 FR-1: the word the correction narrows the condition with -- the readback and the stored condition say it.
CORRECTION_4_WORD = "Europe"
#: Spec 158 FR-1 / FR-5: beat 1 said another way for the long telling (the script's own people, said longer), so the
#: draft is code's (keel-cloud 263 FR-3: the cost line drafted from the limitations, `costDrafted`) rather than the
#: script's -- both roads to the seventh line walked in one run.
LONG_WHO_SUFFIX = " in small teams"


def condition_question(only_those_who: str | None) -> str | None:
    """The screener the runtime's RESPONDENT_QUESTIONS answer writes for a story whose all-or-some beat named a
    condition: *Do you {only those who}?* -- the founder's own words, one yes-or-no question (none where it happens to
    all of them)."""
    words = " ".join(str(only_those_who or "").split()).rstrip(".?")
    if not words:
        return None
    return f"Do you {words[0].lower() + words[1:]}?"


def context_interpret_result(script: dict, rhythm: str) -> dict:
    """keel-cloud 259's acceptance pair's `contextResultOfTheScript`, restated on 268's beats: what CONTEXT_INTERPRET
    answers for the story's own words -- the script's slots in the job's result shape (the window Save reads the
    context again, keel-web 241 FR-1). The when is the beat that named it (2, else 6), the condition beat 5's. `rhythm`
    is the window's (keel-cloud `Rhythm.of`)."""
    who, when, everyone = reading_of(script, 1), reading_of(script, moment_beat(script)), \
        reading_of(script, ALL_OF_THEM_BEAT)
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
    everyone = reading_of(readings, ALL_OF_THEM_BEAT)
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



# ------------------------------------------------------------------------------------ the founder's screens (245)

STORY_START = "[data-testid=story-start]"
STORY_TURN = "[data-testid=story-turn]"
STORY_CHECK = "[data-testid=story-check]"
WINDOW_PATH = re.compile(r"/define/context/window")
#: keel-web 257 FR-1 `lib/storyLines.ts` -- the seven beats' questions (keel-cloud 268 `StoryTurns.QUESTIONS`, verbatim)
#: and the opening line. (keel-web 245's five, keel-cloud 263's: `STORY_QUESTIONS_263`.)
STORY_QUESTIONS = {1: "Who has this problem?",
                   2: "What are they trying to get done, and when does that happen?",
                   3: "How do they do it today, and where does that fall short? Tell me all of it.",
                   4: "And what does that cost them? What happens to them because of it?",
                   5: "Does it happen to all of them, or just to some?",
                   6: "When does that come up?",
                   7: "Besides this, what else do they have to do in their role? Name two or three."}
STORY_QUESTIONS_263 = {1: "Who has this problem?",
                       2: "What are they trying to get done, and when does that happen?",
                       3: "While doing that, what limitations do they run into today? Tell me all of them.",
                       4: "Does it happen to all of them, or just to some?",
                       5: "When does that come up?"}
#: keel-web 257 FR-4: after the film's yes, the verdict -- the card (`story-verdict`) with the served `verdictLine`, Keel
#: saying it, then the fixed line; other words than a yes are answered with the second line and the walk goes on.
VERDICT_CARD = "[data-testid=story-verdict]"
VERDICT_ASK = "Say yes, or just tell me if you want a different bar."
VERDICT_LATER = "You can change that later on the review page."
#: keel-cloud 269 FR-6 (`StoryView.verdictLine`): the three defaults said in one breath.
VERDICT_LINE = ("I will call this real if at least six in ten say it happened, most of those say most times or every "
                "time, and most put it in their top two.")
STORY_READY = "Ready? I am ready when you are. Let us start with the problem."
SOLUTION_READY = "Ready? Let us first go through the problem."
SOLUTION_TURN = "This is the problem. Now let us talk about the solution. How will your product solve it?"
#: keel-web 245 `translate.ts` STORY: the begin screen, the boxes' and the stories' questions, the return line.
BEGIN_TITLE = "Tap me to begin."
BOXES_ASK = "Is that right?"
STORY_ASK = "Is that how it goes for them?"
IDEA_BOXES_ASK = "Is that your idea?"
BACK_TO_SOLUTION = "That is the problem. Taking you back to your solution."
#: keel-web 249 FR-2 (`translate.ts` STORY.orb.state): the state line's first line at the hand-over -- on a beat, and on
#: the readback screens (the boxes, the replays, the story) -- and while Keel speaks.
TURN_LISTENING = "Your turn. I am listening."
TURN_READBACK = "Your turn. Is that right?"
TURN_ASKING = "Keel is asking"
TURN_READING = "Keel is reading it to you"
#: keel-web 249 FR-5 (`lib/story/board.ts` BOX_KEYS): the card's rows' `data-box` keys, as the card names them (the job's
#: row is `task`, *Must get done*; the idea's product row rides on `today`, *The product*). Spec 161 FR-1 (keel-web 257
#: FR-3): `tasks` after `cost` -- the role's other tasks, *Besides this they ...*.
CARD_ROWS = ("person", "task", "when", "today", "limits", "cost", "tasks")
#: Spec 161 FR-1 (keel-web 257 FR-3): the board's seven rows in the narration's order -- who, job, when, today, falls
#: short, costs, other tasks -- by their `data-box` keys.
BOARD_ROWS = ("person", "task", "when", "today", "limits", "cost", "tasks")
#: keel-web 249 FR-5 (`translate.ts` STORY.card): the card's label, and the cost row's name (no "drafted" tag).
CARD_LABEL = "What Keel understood"
CARD_COST_NAME = "So"
#: keel-web 245 FR-6: the cost box carries no label (`costTag: null`) -- 241's tag must not be on the board.
COST_TAG = "What it costs"
#: keel-web 245 FR-8: the conversation's screens and the orb, the one button on them. keel-web 249 FR-1 (spec 158c FR-7):
#: the small orb (44 px; 30 px on a phone) is back on every voice screen -- the beats, the boxes, the replays, the story
#: -- with its state line beside it (`story-state`), and the glow band (`story-glow`, 245 polish round 2) is retired.
#: `ORB` is the orb alone; `ORB_TAP` the same element, the one thing tapped.
ORB = "[data-testid=story-orb]"
ORB_TAP = ORB
#: keel-web 249 FR-1: the glow band, retired -- the walk holds that it is never drawn.
GLOW = "[data-testid=story-glow]"
#: The orb's `data-state`, read in the page.
_ORB_JS = "document.querySelector('[data-testid=story-orb]')"
_NOT_ORB_JS = "b.getAttribute('data-testid') !== 'story-orb'"
STAGE = ".vstage"


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


#: keel-web 080's guide welcome and keel-web 245 FR-3's stage opener share the guide sheet and its Skip.
GUIDE_SKIP = "[data-testid='guide-skip']"
GUIDE_OPENER = "[data-testid='guide-opener']"


def _skip_sheet(page) -> str | None:
    """Presses a guide sheet's Skip where one is up: the stage opener (245 FR-3: its Skip is the founder's first tap) or
    080's welcome. Which one it was, or None."""
    skip = page.locator(GUIDE_SKIP)
    try:
        if not (skip.count() and skip.first.is_visible()):
            return None
    except Exception:  # noqa: BLE001 - a navigation in flight
        return None
    which = "opener" if page.locator(GUIDE_OPENER).count() else "welcome"
    skip.first.click()
    try:
        page.locator(".gw-scrim").first.wait_for(state="detached", timeout=10_000)
    except Exception:  # noqa: BLE001 - a scrim slow to go: Escape is Skip too (keel-web 080 FR-2.6)
        page.keyboard.press("Escape")
        page.wait_for_timeout(1000)
    return which


def pass_the_welcome(page, *, wait_ms: int = 4000) -> bool:
    """keel-web 080's welcome over a new project's first screen (a persona step reached from a start): pressed past
    with Skip where it draws within `wait_ms`. True where it was there."""
    deadline = time.monotonic() + wait_ms / 1000
    while time.monotonic() < deadline:
        if _skip_sheet(page):
            return True
        page.wait_for_timeout(200)
    return False


def wake(page, *, settle_s: float = 1.5, timeout_s: float = 60) -> dict:
    """Gets the founder past what stands before Keel's first line (keel-web 245 FR-3, FR-7): the guide's sheets (the
    stage's opener -- its Skip is the first tap -- and 080's welcome) pressed past, or, where nothing plays, the begin
    screen's orb tapped once it has stood `settle_s` with no sheet coming. Returns what was passed; raises where the
    microphone is refused (`data-voice=deaf`)."""
    out: dict = {"sheets": [], "begin": False, "begin_screen": None}
    deadline = time.monotonic() + timeout_s
    standing = None
    while time.monotonic() < deadline:
        which = _skip_sheet(page)
        if which:
            out["sheets"].append(which)
            standing = None
            continue
        stage = page.locator(STAGE).first
        try:
            voice = stage.get_attribute("data-voice", timeout=1_000) if stage.count() else None
        except Exception:  # noqa: BLE001 - re-rendered under the read
            voice = None
        if voice == "deaf":
            raise AssertionError(f"the microphone was refused on {page.url} (245 FR-7: *I cannot hear you.*)")
        if voice == "on":
            return out
        if voice == "begin":
            if out["begin_screen"] is None:
                # keel-web 249 FR-1 (its judgement call 9): *Tap me to begin.* is the begin screen's state line beside
                # the still orb (no `story-q` there any more)
                out["begin_screen"] = {"title": _tc(page.locator("[data-testid=story-begin] .vstage__state-line"))
                                       or _tc(page.locator("[data-testid=story-begin] [data-testid=story-q]")),
                                       "state": _tc(page.locator("[data-testid=story-begin] [data-testid=story-state]")),
                                       "buttons": stage_buttons(page)}
            standing = standing or time.monotonic()
            if time.monotonic() - standing >= settle_s:
                page.locator(ORB_TAP).first.click()
                out["begin"] = True
                standing = None
                page.wait_for_timeout(300)
                continue
        page.wait_for_timeout(200)
    raise AssertionError(f"the conversation never woke on {page.url}: {out}")


def stage_buttons(page) -> list[str]:
    """Spec 158 FR-1: every `button` on the conversation's screen (`.vstage`) other than the orb -- none is owed."""
    try:
        return page.evaluate(
            """() => [...document.querySelectorAll('.vstage button')]
                   .filter((b) => """ + _NOT_ORB_JS + """)
                   .map((b) => b.getAttribute('data-testid') || (b.textContent || '').trim() || b.outerHTML.slice(0, 80))""")
    except Exception:  # noqa: BLE001 - a navigation in flight
        return []


#: Spec 158 FR-2: the orb's `data-state` (and the screen's `data-voice`, the card's `data-lit`) logged through every
#: screen, change by change, on `window.__orbLog` -- an init script on the founder's context beside the speech seam.
#: Spec 158c FR-7 (keel-web 249): each row also carries the state line's first line (`line`), the hand-over chime's
#: count (`chime`, `window.__keelChime`, the test build's) and whether the recorder runs (`mic`, the seam's
#: `__listening()`), read in the same callback -- so a row is one frame: the orb, the words beside it, the chime.
#: FR-8: every guide sheet mounted (`guide-opener`, `guide-welcome`) is logged on `window.__sheetLog` with how many
#: stood at once and where. FR-7: *What I hear* (`story-heard`) and Keel's lines (`story-words`) are logged on
#: `window.__heardLog` change by change (a beat moves on by itself: a read after it would miss them).
ORB_WATCH = r"""(() => {
  const log = (window.__orbLog = window.__orbLog || []);
  const sheets = (window.__sheetLog = window.__sheetLog || []);
  const heard = (window.__heardLog = window.__heardLog || []);
  let last = '';
  let lastSheets = '';
  let lastHeard = '';
  const read = () => {
    const orb = """ + _ORB_JS + r""";
    const stage = document.querySelector('.vstage');
    const board = document.querySelector('[data-testid=story-boxes]');
    const lineEl = document.querySelector('[data-testid=story-state] .vstage__state-line');
    const row = { state: orb ? orb.getAttribute('data-state') : null, voice: stage ? stage.getAttribute('data-voice') : null,
                  lit: board ? board.getAttribute('data-lit') : null, path: location.pathname,
                  line: lineEl ? (lineEl.textContent || '').replace(/\s+/g, ' ').trim() : null,
                  chime: window.__keelChime || 0,
                  mic: !!(window.__listening && window.__listening()) };
    const key = JSON.stringify(row);
    if (key !== last) { last = key; row.t = Date.now(); log.push(row); }
    const up = [...document.querySelectorAll('[data-testid=guide-opener], [data-testid=guide-welcome]')]
      .map((el) => el.getAttribute('data-testid'));
    const sk = JSON.stringify(up) + location.pathname;
    if (sk !== lastSheets) { lastSheets = sk; sheets.push({ up, path: location.pathname, t: Date.now() }); }
    const heardEl = document.querySelector('[data-testid=story-heard]');
    const quoted = (li) => /[\u201C"]/.test(getComputedStyle(li, '::before').content || '')
      && /[\u201D"]/.test(getComputedStyle(li, '::after').content || '');
    const said = heardEl ? [...heardEl.querySelectorAll('li')].map((li) => ({ who: li.getAttribute('data-who'),
      text: (li.textContent || '').replace(/\s+/g, ' ').trim(), quoted: quoted(li) })) : [];
    const keel = [...document.querySelectorAll('[data-testid=story-words] li')].map((li) => ({
      who: li.getAttribute('data-who'), text: (li.textContent || '').replace(/\s+/g, ' ').trim() }));
    const hk = JSON.stringify([said, keel]);
    if (hk !== lastHeard) { lastHeard = hk; heard.push({ said, keel, path: location.pathname,
                                                         fading: !!(heardEl && heardEl.hasAttribute('data-fading')),
                                                         t: Date.now() }); }
  };
  new MutationObserver(read).observe(document, { subtree: true, childList: true, characterData: true, attributes: true,
                                                 attributeFilter: ['data-state', 'data-lit', 'data-voice'] });
  read();
})();"""

#: What one screen of the conversation draws, read in one go (the conversation moves on its own; a slow read misses).
#: keel-web 249 (spec 158c FR-7): `words` are Keel's lines alone (`story-words`); the founder's are `heard` (*What I
#: hear*, `story-heard`, the quotation marks CSS); `card` the rows of *What Keel understood* by `data-box` (`story-boxes`
#: on the boxes and the replays; beat 3's `story-understood`; the idea's `idea-understood`); `chime` the hand-over count.
_SNAPSHOT = r"""() => {
  const q = (s) => document.querySelector(s);
  const t = (el) => (el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : null);
  const all = (s) => [...document.querySelectorAll(s)];
  const stage = q('.vstage');
  const card = (sel) => {
    const el = q(sel);
    if (!el) return null;
    return { lit: el.getAttribute('data-lit'), label: t(el.querySelector('.ucard__label')),
             rows: [...el.querySelectorAll('[data-box]')].map((r) => ({
               box: r.getAttribute('data-box'), name: t(r.querySelector('.ucard__name')),
               lit: r.hasAttribute('data-lit'), wait: r.hasAttribute('data-wait'),
               items: [...r.querySelectorAll('[data-id]')].map((i) => ({ id: i.getAttribute('data-id'),
                                                                         mark: i.getAttribute('data-mark'), text: t(i) })),
               text: t(r.querySelector('.ucard__words')) })),
             svg: el.querySelectorAll('svg').length };
  };
  const lineEl = q('[data-testid=story-state] .vstage__state-line');
  const subEl = q('[data-testid=story-state] .vstage__state-sub');
  return {
    path: location.pathname,
    screen: stage ? stage.getAttribute('data-testid') : null,
    turn: (q('[data-testid=story-turn]') || q('[data-testid=idea-turn]') || { getAttribute: () => null }).getAttribute('data-turn'),
    voice: stage ? stage.getAttribute('data-voice') : null,
    orb: """ + _ORB_JS + r""" ? """ + _ORB_JS + r""".getAttribute('data-state') : null,
    orbs: all('[data-testid=story-orb]').length,
    orbSize: """ + _ORB_JS + r""" ? """ + _ORB_JS + r""".offsetWidth : null,
    glow: all('[data-testid=story-glow]').length,
    kicker: t(q('[data-testid=story-kicker]')),
    question: t(q('[data-testid=story-q]')),
    state: t(q('[data-testid=story-state]')),
    line: t(lineEl),
    sub: t(subEl),
    words: all('[data-testid=story-words] li').map((li) => ({ who: li.getAttribute('data-who'), text: t(li) })),
    heard: all('[data-testid=story-heard] li').map((li) => ({ who: li.getAttribute('data-who'), text: t(li) })),
    heardLabel: t(q('[data-testid=story-heard] .vheard__label')),
    limits: all('[data-testid=story-card-limit]').map((li) => t(li).replace(/^×\s*/, '')),
    marks: all('[data-testid=idea-card-limit]').map((li) => ({ mark: li.getAttribute('data-mark'), text: t(li).replace(/^[✓×]\s*/, '') })),
    understood: card('[data-testid=story-understood]') || card('[data-testid=idea-understood]'),
    card: card('[data-testid=story-boxes]'),
    folded: t(q('[data-testid=story-folded]')),
    said: t(q('[data-testid=story-check-said]')) || t(q('[data-testid=idea-boxes-said]')) || t(q('[data-testid=idea-story-said]')),
    board: t(q('[data-testid=story-boxes]')),
    drop: q('[data-testid=idea-drop]') ? true : false,
    chime: window.__keelChime || 0,
    buttons: stage ? [...stage.querySelectorAll('button')].filter((b) => """ + _NOT_ORB_JS + r""")
      .map((b) => b.getAttribute('data-testid') || t(b)) : [],
  };
}"""


def card_rows(card: dict | None) -> dict[str, str]:
    """Spec 158c FR-7: a card's rows by `data-box` -> the row's words (keel-web 249's `UnderstoodCard`); {} where none."""
    return {r.get("box"): " ".join(str(r.get("text") or "").split()) for r in ((card or {}).get("rows") or [])
            if r.get("box")}


def card_name(card: dict | None, box: str) -> str | None:
    """A row's name on the card's left (*The person*, *So*)."""
    row = next((r for r in ((card or {}).get("rows") or []) if r.get("box") == box), None)
    return (row or {}).get("name")


def card_items(card: dict | None, box: str) -> list[dict]:
    """The lines of one row (`data-id`, `data-mark`, the words) -- a list row's crosses and ticks."""
    row = next((r for r in ((card or {}).get("rows") or []) if r.get("box") == box), None)
    return list((row or {}).get("items") or [])


def hand_overs(log: list[dict]) -> list[dict]:
    """Spec 158c FR-7 (keel-web 249 FR-3): the hand-overs in an orb log -- each row where the orb turns `listening`
    from Keel's turn (`speaking`: the clip ended, the microphone opens). A thinking pause's `writing -> listening` and a
    cough's re-listen are not hand-overs (249's judgement call 5); nor is a row that only re-reads a standing listen."""
    out: list[dict] = []
    prev = None
    for row in log:
        state = row.get("state")
        if state is None:
            continue
        if state == "listening" and prev == "speaking":
            out.append(row)
        prev = state
    return out


def chime_verdict(log: list[dict]) -> dict:
    """Spec 158c FR-7: `window.__keelChime` rises by exactly one per hand-over -- each hand-over's row carries one more
    chime than the last (the first one more than the log's start), no chime is heard between them, and the state line
    reads *Your turn.* in the very row the orb first listens. `listening` only where the microphone opened (`mic`).
    The log is one page's (a reload starts both the counter and the log again)."""
    rows = [r for r in log if r.get("state") is not None]
    overs = hand_overs(log)
    start = (rows[0].get("chime") or 0) if rows else 0
    want = list(range(start + 1, start + 1 + len(overs)))
    got = [o.get("chime") or 0 for o in overs]
    end = (rows[-1].get("chime") or 0) if rows else 0
    # a chime counted somewhere other than a hand-over: the counter rose on a row that is not one -- unless the
    # hand-over's own frame follows within a second carrying that same count (the chime is counted in the microphone's
    # callback, a moment before React draws the listening orb; another change may be logged in between)
    stray = []
    before = start
    for i, r in enumerate(rows):
        c = r.get("chime") or 0
        if c != before and not any(r is o for o in overs):
            nxt = next((o for o in rows[i + 1:] if any(o is h for h in overs)), None)
            if not (nxt is not None and (nxt.get("chime") or 0) == c
                    and (nxt.get("t") or 0) - (r.get("t") or 0) <= 1000):
                stray.append({k: r.get(k) for k in ("state", "line", "path", "chime")})
        before = c
    lines = [{"path": o.get("path"), "line": o.get("line")} for o in overs]
    said_turn = all(str(o.get("line") or "").startswith("Your turn.") for o in overs)
    deaf_listens = [{k: r.get(k) for k in ("state", "path", "line")} for r in rows
                    if r.get("state") == "listening" and not r.get("mic")]
    return {"hand_overs": len(overs), "chimes": end - start, "got": got, "want": want,
            "one_each": got == want and end - start == len(overs) and not stray, "stray": stray[:6],
            "your_turn": said_turn, "lines": lines, "listening_without_mic": deaf_listens[:6],
            "mic_open": not deaf_listens}


#: keel-web 249 FR-6: the conversation's routes, where the shell opens no welcome (the stage opener is the one film).
CONVERSATION_ROUTES = re.compile(r"/define/(story|idea)/|/define/money/start")


def sheet_verdict(sheets: list[dict]) -> dict:
    """Spec 158c FR-8 (keel-web 249 FR-6): from `__sheetLog`, at most one guide sheet mounted at any moment, the stage
    opener met on the conversation (`guide-opener`) and no welcome sheet (`guide-welcome`) on its routes."""
    most = max((len(r.get("up") or []) for r in sheets), default=0)
    on_routes = [r for r in sheets if CONVERSATION_ROUTES.search(str(r.get("path") or ""))]
    openers = sorted({r.get("path") for r in on_routes if "guide-opener" in (r.get("up") or [])})
    welcomes = sorted({r.get("path") for r in on_routes if "guide-welcome" in (r.get("up") or [])})
    return {"most_at_once": most, "one_at_a_time": most <= 1, "opener_on": openers, "welcome_on": welcomes,
            "one_film": bool(openers) and not welcomes and most <= 1}


def heard_verdict(heard: list[dict], said: dict[int, str], path_of) -> dict:
    """Spec 158c FR-7 (keel-web 249 FR-4): each beat's words shown as heard -- in *What I hear* (`story-heard`, the
    founder's `li[data-who=you]`) on that beat's screen -- and never among Keel's lines (`story-words`, which hold
    `data-who=keel` only). `path_of(n)` is beat n's path ending."""
    norm = lambda x: " ".join(str(x or "").split())  # noqa: E731
    shown: dict[int, bool] = {}
    for n, words in said.items():
        rows = [r for r in heard if str(r.get("path") or "").rstrip("/").endswith(path_of(n))]
        texts = [norm(" ".join(li.get("text") or "" for li in (r.get("said") or []) if li.get("who") == "you"))
                 for r in rows]
        shown[n] = any(norm(words) in t for t in texts)
    founder_in_words = [li for r in heard for li in (r.get("keel") or []) if li.get("who") != "keel"
                        or any(norm(w) and norm(w) == norm(li.get("text")) for w in said.values())]
    unquoted = [li.get("text")[:60] for r in heard for li in (r.get("said") or [])
                if li.get("who") == "you" and li.get("quoted") is False]
    return {"shown": shown, "all_shown": all(shown.values()), "founder_in_words": founder_in_words[:4],
            "words_keels_only": not founder_in_words, "unquoted": unquoted[:4], "quoted": not unquoted}


def writing_then_speaking(seq: list[str]) -> bool:
    """Spec 158c FR-7 (keel-web 249's judgement call 2): after Keel has written the founder's words down, Keel speaks
    next -- `writing -> speaking`, never `writing -> listening -> speaking` (`listening` now means the microphone is
    open). Holds where every `writing` in `seq` is followed by `speaking` or ends it."""
    return all(seq[i + 1] == "speaking" for i, s in enumerate(seq[:-1]) if s == "writing")


def orb_sequence(log: list[dict], path: str | None = None) -> list[str]:
    """The orb's states in the order they came (repeats folded), on one path where given."""
    out: list[str] = []
    for row in log:
        if path is not None and row.get("path") != path:
            continue
        state = row.get("state")
        if state and (not out or out[-1] != state):
            out.append(state)
    return out


def holds_in_order(seen: list[str], want: list[str]) -> bool:
    """`want` appears in `seen` in order (not necessarily side by side)."""
    i = 0
    for state in seen:
        if i < len(want) and state == want[i]:
            i += 1
    return i == len(want)


#: Spec 158 FR-2: a beat's orb, from Keel's question to Keel's next line. Spec 158c FR-7 (keel-web 249): the same five,
#: with `listening` only where the microphone opened -- between beats the orb goes `writing -> speaking`
#: (`writing_then_speaking`), never through `listening`.
BEAT_ORB = ["speaking", "listening", "hearing", "writing", "speaking"]


class FounderVoice:
    """The founder's microphone through the seam (`interviewer_screens.SPEECH_SEAM`, installed on the context): wait for
    the page's recorder to run, then say the words; the page does the rest. No tap: keel-web 245 draws no *Tap to talk*."""

    def __init__(self, page):
        self.page = page

    def listening(self) -> bool:
        try:
            return bool(self.page.evaluate("() => !!(window.__listening && window.__listening())"))
        except Exception:  # noqa: BLE001 - a navigation in flight
            return False

    def wait_listening(self, timeout_s: float = 60) -> None:
        deadline = time.monotonic() + timeout_s
        while not self.listening():
            if time.monotonic() > deadline:
                raise AssertionError(f"the founder's microphone never opened on {self.page.url} (the hands-free mic, "
                                     "keel-web 245 FR-5)")
            self.page.wait_for_timeout(100)

    def say(self, words: str, *, timeout_s: float = 60) -> None:
        self.wait_listening(timeout_s)
        self.page.evaluate("(w) => window.__say(w, true)", words)

    def said(self) -> list:
        try:
            return self.page.evaluate("() => window.__said || []")
        except Exception:  # noqa: BLE001 - a read
            return []


class Conversation:
    """What every screen of keel-web 245's conversation shares: the founder's voice, the quiet let pass, the orb's log,
    one read of the screen, and every write the page made with the answer it received (`writes`)."""

    def __init__(self, page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.voice = FounderVoice(page)
        self.writes: list[dict] = []
        self._listening = False

    # ------------------------------------------------------------------------------------------- the wire
    def _keep(self, response) -> None:
        url = response.url.split("?")[0]
        if "/story" not in url and "/idea" not in url and not url.endswith("/v2/projects"):
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

    def writes_to(self, pattern: str) -> list[dict]:
        return [w for w in self.writes if re.search(pattern, w["path"])]

    def put_after(self, pattern: str, act, *, timeout_s: float = 90) -> dict:
        """Does `act` and waits for the next write whose path matches `pattern`; returns it."""
        before = len(self.writes_to(pattern))
        act()
        deadline = time.monotonic() + timeout_s * self.patience
        while len(self.writes_to(pattern)) <= before:
            if time.monotonic() > deadline:
                raise AssertionError(f"no write to {pattern} within {timeout_s} s ({self.page.url})")
            self.page.wait_for_timeout(100)
        return self.writes_to(pattern)[-1]

    # ------------------------------------------------------------------------------------------- reads
    def orb_log(self) -> list[dict]:
        try:
            return list(self.page.evaluate("() => window.__orbLog || []"))
        except Exception:  # noqa: BLE001 - a navigation in flight
            return []

    def _log(self, name: str) -> list[dict]:
        try:
            return list(self.page.evaluate(f"() => window.{name} || []"))
        except Exception:  # noqa: BLE001 - a navigation in flight
            return []

    def begin(self) -> float:
        """Spec 158c: the moment this conversation starts, on the page's clock -- its logs are read from here (a row's
        `t`), so a reload in between (which starts the logs again) never shifts what is read."""
        try:
            self.since_t = float(self.page.evaluate("() => Date.now()"))
        except Exception:  # noqa: BLE001
            self.since_t = time.time() * 1000
        return self.since_t

    def since(self, name: str = "__orbLog", *, standing: bool = False) -> list[dict]:
        """The log's rows since `begin()`; `standing`: with the row that stood at that moment first (a sheet mounted
        just before the conversation began)."""
        t0 = getattr(self, "since_t", 0.0) or 0.0
        rows = self._log(name)
        after = [r for r in rows if (r.get("t") or 0) >= t0]
        before = [r for r in rows if (r.get("t") or 0) < t0]
        return (before[-1:] if standing else []) + after

    def turn_read(self) -> dict:
        """Spec 158c FR-7/FR-8: this conversation's hand-overs and chimes (`chime_verdict`), *What I hear* and Keel's
        lines as they stood, and the guide sheets mounted -- read from `begin()`."""
        heard = self.since("__heardLog")
        return {"chime": chime_verdict(self.since()), "heard": heard,
                "sheets": self.since("__sheetLog", standing=True)}

    def sheets_of(self, project_id: str) -> list[dict]:
        """Spec 158c FR-8: the guide sheets this page met on one project's screens (the whole page's log, not only
        since `begin()`: the opener mounts as the project's first screen draws)."""
        return [r for r in self._log("__sheetLog") if f"/p/{project_id}/" in str(r.get("path") or "")]

    def snapshot(self) -> dict:
        try:
            return self.page.evaluate(_SNAPSHOT)
        except Exception as e:  # noqa: BLE001 - a navigation in flight
            return {"unread": str(e)[:200], "path": self.page.url}

    def wait_path(self, pattern: str | re.Pattern, *, timeout_s: float = 60) -> str:
        rx = re.compile(pattern) if isinstance(pattern, str) else pattern
        deadline = time.monotonic() + timeout_s * self.patience
        while not rx.search(self.page.url):
            if time.monotonic() > deadline:
                raise AssertionError(f"the conversation never reached {rx.pattern}: {self.page.url}")
            self.page.wait_for_timeout(150)
        return self.page.url

    # ------------------------------------------------------------------------------------------- the quiet
    def silence(self, *, timeout_s: float = 120, landed: re.Pattern | None = None) -> None:
        """The founder says nothing: `window.__keelSilence()` (keel-web 245 FR-8) answers the quiet wait at once, polled
        until one stands. A guide sheet that comes up meanwhile is pressed past (the opener decides late). `landed`:
        the page's own four seconds already went on there (a slow read before the quiet, spec 158b's measure) -- done."""
        deadline = time.monotonic() + timeout_s * self.patience
        while time.monotonic() < deadline:
            if landed is not None and landed.search(self.page.url):
                return
            _skip_sheet(self.page)
            try:
                if self.page.evaluate("() => !!(window.__keelSilence && window.__keelSilence() === true)"):
                    return
            except Exception:  # noqa: BLE001 - a navigation in flight
                pass
            self.page.wait_for_timeout(200)
        raise AssertionError(f"no quiet wait stood on {self.page.url} within {timeout_s} s (245 FR-8 `__keelSilence`)")

    def orb_since(self, mark: int, path_end: str | None = None) -> list[str]:
        """The orb's states since `mark`, on the screens whose path ends `path_end` where given."""
        rows = self.orb_log()[mark:]
        if path_end is not None:
            rows = [r for r in rows if str(r.get("path") or "").rstrip("/").endswith(path_end)]
        return orb_sequence(rows)

    def await_quiet(self, mark: int, *, after: tuple[str, ...] = ("hearing", "writing"), timeout_s: float = 60) -> dict:
        """Keel has said its line back and listens again: from the orb's log since `mark`, a `speaking` after the
        founder was heard (`after`), the orb no longer speaking, and the recorder running -- the quiet wait stands
        (never answered here). A line never heard as speaking (its clip unplayed) is waited out to `timeout_s`."""
        deadline = time.monotonic() + timeout_s * self.patience
        spoke = False
        while time.monotonic() < deadline:
            seq = orb_sequence(self.orb_log()[mark:])
            heard = next((i for i, s in enumerate(seq) if s in after), None) if after else -1
            spoke = heard is not None and "speaking" in seq[heard + 1:]
            if spoke and seq and seq[-1] != "speaking" and self.voice.listening():
                return {"spoke": True, "orb": seq}
            self.page.wait_for_timeout(100)
        return {"spoke": spoke, "orb": orb_sequence(self.orb_log()[mark:]), "timeout": True}

    def after_answer(self, n: int, mark: int, *, timeout_s: float = 60, flow: str = "story") -> dict:
        """What follows a beat's answer, whichever comes first. keel-web 245 FR-4 as amended (2026-11-22): the problem's
        beats 1, 2 and 4 go straight on once the reading lands -- the page leaves the beat, and the walk waits for the
        next question's words (or the boxes); beat 3 says only *Anything else?* and waits for the quiet; the idea's beats
        (`flow="idea"`, keel-web 248) go straight on too -- beat 1 unless its spelling check speaks, beat 2 once its ticks
        and crosses stood. The build before polish round 2 reads every beat back and waits for the quiet on the beat's
        own screen. Returns `straight_on` (the page moved), else the quiet as `await_quiet` reads it, on the beat's
        screen alone."""
        deadline = time.monotonic() + timeout_s * self.patience
        here = re.compile(rf"/define/{flow}/{n}/?$")
        moved = re.compile(rf"/define/{flow}/(\d|check)/?$")
        path_end = f"/define/{flow}/{n}"
        seq: list[str] = []
        while time.monotonic() < deadline:
            url = self.page.url
            if not here.search(url) and moved.search(url):
                nxt = url.rstrip("/").split("/")[-1]
                want = STORY_QUESTIONS.get(int(nxt)) if (flow == "story" and nxt.isdigit()) else None
                out = {"straight_on": True, "next": nxt, "asked": want}
                try:
                    if want:
                        self.page.wait_for_function(
                            "(w) => { const el = document.querySelector('[data-testid=story-q]'); "
                            "return !!el && el.textContent.replace(/\\s+/g, ' ').trim() === w; }", arg=want,
                            timeout=30_000 * self.patience)
                    elif nxt.isdigit():
                        self.page.locator(f"{IDEA_TURN}[data-turn='{nxt}']").first.wait_for(state="visible",
                                                                                         timeout=30_000)
                    else:
                        self.page.get_by_test_id(f"{flow}-boxes-screen").first.wait_for(state="visible",
                                                                                         timeout=30_000)
                except Exception:  # noqa: BLE001 - recorded: the next screen's words never stood
                    out["unseen"] = True
                # Keel's next line (the next question, or the boxes' narration on the glow) is the beat's last
                # `speaking`: waited for a little, so the beat's orb reads whole
                spoken_by = time.monotonic() + 10
                while time.monotonic() < spoken_by:
                    seq = orb_sequence(self.orb_log()[mark:])
                    wrote = max((i for i, st in enumerate(seq) if st == "writing"), default=None)
                    if wrote is not None and "speaking" in seq[wrote + 1:]:
                        break
                    self.page.wait_for_timeout(100)
                out["orb"] = orb_sequence(self.orb_log()[mark:])
                return out
            seq = self.orb_since(mark, path_end)
            heard = next((i for i, st in enumerate(seq) if st in ("hearing", "writing")), None)
            spoke = heard is not None and "speaking" in seq[heard + 1:]
            if spoke and seq[-1] != "speaking" and self.voice.listening():
                return {"straight_on": False, "spoke": True, "orb": seq}
            self.page.wait_for_timeout(100)
        return {"straight_on": False, "spoke": False, "orb": seq, "timeout": True}

    def wake(self) -> dict:
        return wake(self.page)


class StoryWalk(Conversation):
    """keel-web 245's problem conversation on one project: the opening (the opener or the begin screen, *Ready?*), the
    beats, the boxes by silence, the building screen, the story by silence."""

    def __init__(self, page, recorder, base_url: str, *, patience: float = 1.0):
        super().__init__(page, recorder, base_url, patience=patience)
        self.beats_seen: list[dict] = []
        #: keel-web 245 FR-4 (2026-11-22): a correction a beat could not take (no readback to answer) -- said on the boxes.
        self.deferred_correction: str | None = None

    def turn_writes(self, n: int) -> list[dict]:
        return self.writes_to(rf"/story/turns/{n}$")

    def _wait_beat(self, n: int, timeout_s: float = 60) -> None:
        self.page.locator(f"{STORY_TURN}[data-turn='{n}']").first.wait_for(state="visible",
                                                                          timeout=timeout_s * 1000 * self.patience)

    # ------------------------------------------------------------------------------------------- the opening
    def open_start(self, project_id: str, *, goto: bool = True) -> dict:
        """`define/story/start`: what stands before Keel speaks passed (the opener or the begin screen), then *Ready?* and
        the quiet that starts beat 1."""
        with self._b.step("the opening: the stage's opener or the begin screen, then Ready? and the quiet") as h:
            self.listen()
            self.begin()
            start = f"/p/{project_id}/define/story/start"
            # spec 158c: a page already on the story's start (a new project opens there) is not reloaded -- a reload
            # would lose what the page met there first (the stage opener, FR-8)
            if goto and not self.page.url.split("?")[0].rstrip("/").endswith(start):
                self.page.goto(f"{self.base}{start}", wait_until="load")
            self.page.locator(STORY_START).first.wait_for(state="visible", timeout=60_000)
            woke = self.wake()
            seen = {"woke": woke, "start": self.snapshot()}
            h.add_screenshot(self._b.screenshot("story-ready"))
            self.silence()
            self.wait_path(r"/define/story/\d$")
            seen["landed"] = self.page.url
            h.record_wire({"GET": "define/story/start"}, seen)
            return seen

    # ------------------------------------------------------------------------------------------- one beat
    def beat(self, n: int, words: str, *, correction: str | None = None, two_part: tuple[str, str] | None = None,
             ask_answer: str | None = None) -> dict:
        """One beat as the founder answers it: Keel's question, the words said once, Keel's readback, then the quiet --
        or, after the readback, `correction` said (sent as the beat again with `correction: true`) and its readback,
        then the quiet. Beat 3's quiet closes the list (`done: true`). Returns what the screen drew and the wire.

        Spec 161 FR-1 (keel-web 257 FR-11): a long beat (3, 4, 7) is said with the done word as its last words
        (`with_done_word`) and never waits on the quiet to close; `two_part` (beat 3 on one leg) says the first part,
        lets `TWO_PART_QUIET_S` of quiet pass -- reading that nothing was sent and the state line says *Take your
        time.* -- then the second part and the done word; `ask_answer` is said after code's one ask on beat 3 (*And how
        do they do it today?*, keel-cloud 268 FR-1)."""
        long = n in LONG_BEATS
        with self._b.step(f"beat {n}: {STORY_QUESTIONS.get(n)}") as h:
            self._wait_beat(n)
            # the beat's log starts where its screen came (Keel is already asking by the time the walk reads it)
            log = self.orb_log()
            path = f"/define/story/{n}"
            mark = next((i for i, row in enumerate(log) if str(row.get("path") or "").endswith(path)), len(log))
            seen: dict = {"turn": n, "asked": self.snapshot(), "long": long}
            if two_part:
                seen["two_part"] = self.two_parts(n, two_part)
                put = self.writes_to(rf"/story/turns/{n}$")[-1] if self.writes_to(rf"/story/turns/{n}$") else {}
                if not put:
                    raise AssertionError(f"beat {n}: the two parts were never sent ({seen['two_part']})")
            else:
                said = with_done_word(words) if long else words
                put = self.put_after(rf"/story/turns/{n}$", lambda: self.voice.say(said))
            seen["put"] = {"status": put["status"], "sent": put["sent"], "body": put["body"]}
            if (put.get("status") or 500) >= 400:
                raise AssertionError(f"beat {n} refused {put.get('status')}: {put.get('body')}")
            asked = (put.get("body") or {}).get("ask")
            if asked and ask_answer:
                # keel-cloud 268 FR-1: the way's one ask -- said by Keel, the microphone open again on the same beat
                seen["ask"] = asked
                said = with_done_word(ask_answer) if long else ask_answer
                again = self.put_after(rf"/story/turns/{n}$", lambda: self.voice.say(said))
                seen["way"] = {"status": again["status"], "sent": again["sent"], "body": again["body"]}
                put = again
            seen["quiet"] = self.after_answer(n, mark)
            seen["straight_on"] = bool(seen["quiet"].get("straight_on"))
            if seen["straight_on"]:
                # keel-web 245 FR-4 (2026-11-22): no readback -- the page went on by itself; nothing to let pass. A
                # correction owed here is said on the boxes instead (FR-6: *Is that right?*, `story/correct`).
                seen["readback"] = {"straight_on": True, "buttons": []}
                if correction:
                    seen["correction_deferred"] = correction
                closes = [w for w in self.writes_to(rf"/story/turns/{n}$") if (w["sent"] or {}).get("done")]
                if closes:
                    seen["closed"] = {"status": closes[-1]["status"], "sent": closes[-1]["sent"],
                                      "next": (closes[-1]["body"] or {}).get("next"), "by": "the done word"}
                seen["next"] = self.page.url.rstrip("/").split("/")[-1]
                seen["orb"] = orb_sequence(self.orb_log()[mark:])
                h.add_screenshot(self._b.screenshot(f"story-beat-{n}-next"))
                h.record_wire({"beat": n, "said": words[:300] + ("..." if len(words) > 300 else "")},
                              {k: seen[k] for k in ("put", "next", "orb", "straight_on") if k in seen})
                self.beats_seen.append(seen)
                return seen
            if n == 3:
                want = len(((put["body"] or {}).get("story") or {}).get("limits") or [])
                try:
                    self.page.wait_for_function("(n) => document.querySelectorAll('[data-testid=story-card-limit]')"
                                                ".length >= n", arg=want, timeout=10_000)
                except Exception:  # noqa: BLE001 - recorded, judged by the leg
                    pass
            seen["readback"] = self.snapshot()
            h.add_screenshot(self._b.screenshot(f"story-beat-{n}"))
            if correction:
                mark2 = len(self.orb_log())
                fixed = self.put_after(rf"/story/turns/{n}$", lambda: self.voice.say(correction))
                seen["correction"] = {"status": fixed["status"], "sent": fixed["sent"], "body": fixed["body"],
                                      "quiet": self.await_quiet(mark2)}
                seen["corrected"] = self.snapshot()
                h.add_screenshot(self._b.screenshot(f"story-beat-{n}-corrected"))
            if n == 3:
                closes = [w for w in self.writes_to(r"/story/turns/3$") if (w["sent"] or {}).get("done")]
                if closes:
                    closed, by = closes[-1], "the done word"
                else:
                    # a page before keel-web 257: the quiet after *Anything else?* closes the list
                    closed, by = self.put_after(r"/story/turns/3$", self.silence), "the quiet"
                seen["closed"] = {"status": closed["status"], "sent": closed["sent"],
                                  "next": (closed["body"] or {}).get("next"), "by": by}
            elif not long:
                self.silence()
            self.wait_path(rf"/define/story/(?!{n}$)(\d|check)$")
            seen["next"] = self.page.url.rstrip("/").split("/")[-1]
            seen["orb"] = orb_sequence(self.orb_log()[mark:])
            h.record_wire({"beat": n, "said": words[:300] + ("..." if len(words) > 300 else "")},
                          {k: seen[k] for k in ("put", "next", "orb") if k in seen})
            self.beats_seen.append(seen)
            return seen

    def two_parts(self, n: int, parts: tuple[str, str]) -> dict:
        """Spec 161 FR-1 (keel-web 257 FR-11): a long beat said in two parts -- the first, then `TWO_PART_QUIET_S` of
        quiet (nothing sent, the beat still open, the state line *Take your time.* once `THINK_MS` passed), then the
        second and the done word; the page sends the two as one answer."""
        before = len(self.writes_to(rf"/story/turns/{n}$"))
        self.voice.say(parts[0])
        deadline = time.monotonic() + TWO_PART_QUIET_S
        lines: list[str] = []
        think = False
        while time.monotonic() < deadline:
            line = _tc(self.page.locator("[data-testid=story-state]"))
            if line and line not in lines:
                lines.append(line)
            # keel-web 257 (its tasks.md's eval mirrors): after 6 s of quiet the orb dims (`story-orb[data-think]`) and
            # the state line says *Take your time.*
            think = think or self.page.locator(f"{ORB}[data-think]").count() > 0
            self.page.wait_for_timeout(250)
        quiet = {"sent_in_the_quiet": len(self.writes_to(rf"/story/turns/{n}$")) - before,
                 "still_on_the_beat": bool(re.search(rf"/define/story/{n}/?$", self.page.url)),
                 "state_lines": lines, "orb_thinks": think,
                 "think_line": think and any(THINK_LINE in line for line in lines),
                 "listening": self.voice.listening()}
        put = self.put_after(rf"/story/turns/{n}$", lambda: self.voice.say(with_done_word(parts[1])))
        quiet["sent"] = (put.get("sent") or {}).get("text")
        quiet["joined"] = all(_bare_words(p) in _bare_words(quiet["sent"]) for p in parts)
        return quiet

    def tell(self, beats: list[tuple[int, str]], *, long3: str | None = None,
             correction: str | None = None, two_part: tuple[str, str] | None = None,
             limits_only: tuple[str, str] | None = None) -> list[dict]:
        """The beats in order (beat 3 the long answer where given, or in two parts, or the limitations alone and then
        the way after code's ask; `correction` after beat 5's readback), beat 6 only where the page asks it (keel-cloud
        268: owed only while the when is unknown), then the boxes."""
        seen = []
        for n, words in beats:
            if n == WHEN_BEAT and not re.search(rf"/define/story/{WHEN_BEAT}$", self.page.url):
                continue
            kw: dict = {"correction": correction if n == ALL_OF_THEM_BEAT else None}
            if n == 3 and two_part:
                kw["two_part"] = two_part
            if n == 3 and limits_only:
                words = limits_only[0]
                kw["ask_answer"] = limits_only[1]
            seen.append(self.beat(n, long3 if (n == 3 and long3) else words, **kw))
            if seen[-1].get("correction_deferred"):
                self.deferred_correction = seen[-1]["correction_deferred"]
        self.wait_path(r"/define/story/check$")
        return seen


    # ------------------------------------------------------------------------------------------- after the beats
    def boxes(self, correction: str | None = None) -> dict:
        """The boxes (`define/story/check`, no yes yet): the board centre stage, Keel narrating it box by box, *Is that
        right?*, then -- where a correction is owed (`correction`, or one a beat deferred) -- the words said and
        `story/correct` answered, then the quiet confirms (`story/confirm`)."""
        with self._b.step("the boxes: the board narrated, Is that right?, the quiet confirms") as h:
            mark = len(self.orb_log())
            self.page.get_by_test_id("story-boxes-screen").first.wait_for(state="visible", timeout=60_000)
            try:
                self.page.wait_for_function(
                    "(w) => { const el = document.querySelector('[data-testid=story-check-said]'); "
                    "return !!el && el.textContent.trim() === w; }", arg=BOXES_ASK, timeout=90_000)
            except Exception:  # noqa: BLE001 - recorded, judged by the leg
                pass
            seen = {"screen": self.snapshot()}
            h.add_screenshot(self._b.screenshot("story-boxes"))
            correction = correction if correction is not None else self.deferred_correction
            if correction:
                # keel-web 245 FR-6: any words after *Is that right?* are a correction (`story/correct`: the changed
                # box lit, the readback said), then *Is that right?* again
                mark2 = len(self.orb_log())
                fixed = self.put_after(r"/story/correct$", lambda: self.voice.say(correction))
                seen["correction"] = {"status": fixed["status"], "sent": fixed["sent"], "body": fixed["body"],
                                      "quiet": self.await_quiet(mark2), "where": "the boxes"}
                seen["corrected"] = self.snapshot()
                h.add_screenshot(self._b.screenshot("story-boxes-corrected"))
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/story/confirm"), timeout=150_000) as got:
                self.silence()
            seen["confirm"] = {"status": got.value.status, "body": _json(got.value)}
            # the card's narration lights its rows from the moment the boxes' screen draws -- which can be before this
            # step starts (a beat that goes straight on lands on the boxes while the walk still reads the beat), so the
            # rows lit are read off every row the page logged on the boxes' path since the conversation began
            seen["lit"] = [row.get("lit") for row in self.since()
                           if row.get("lit") and str(row.get("path") or "").rstrip("/").endswith("/define/story/check")]
            h.record_wire({"POST": "story/confirm (the quiet)"}, {"status": got.value.status, "lit": seen["lit"]})
            return seen

    def building_then_story(self, *, timeout_s: float = 120) -> dict:
        """The building screen while the build builds, then the story played through once."""
        with self._b.step("the building screen, then the story played") as h:
            building = None
            deadline = time.monotonic() + timeout_s * self.patience
            while time.monotonic() < deadline:
                state = self.page.locator(STORY_CHECK).first.get_attribute("data-state") \
                    if self.page.locator(STORY_CHECK).count() else None
                if state == "building" and building is None:
                    building = self.snapshot()
                    building["steps"] = [{"step": li.get_attribute("data-step"), "state": li.get_attribute("data-state")}
                                         for li in self.page.locator(".story-build-steps li").all()]
                    h.add_screenshot(self._b.screenshot("story-building"))
                if state in ("story", "failed"):
                    break
                self.page.wait_for_timeout(250)
            state = self.page.locator(STORY_CHECK).first.get_attribute("data-state") \
                if self.page.locator(STORY_CHECK).count() else None
            seen = {"building": building, "state": state, "story": self.snapshot(),
                    "player": self.page.locator("[data-testid=story-readback] [data-testid=story-player], "
                                                "[data-testid=story-readback] .sty-player").count()}
            h.add_screenshot(self._b.screenshot("story-readback"))
            h.record_assert({"state": "story"}, seen)
            return seen

    def story_yes(self, *, lands: re.Pattern | str = WINDOW_PATH, verdict: bool = False) -> dict:
        """The story played through, *Is that how it goes for them?*, then the quiet goes on (244's window, or the
        return trip). Spec 161 FR-2 (keel-web 257 FR-4, `verdict`): after the film's yes Keel says the verdict line on
        its card (`story-verdict`) and the fixed ask; the walk answers nothing and the quiet goes on."""
        with self._b.step("the story's question, then the quiet goes on") as h:
            landing = re.compile(lands) if isinstance(lands, str) else lands
            self.silence(timeout_s=180, landed=landing)
            said = self.snapshot()
            heard = self.hear_verdict(landing) if verdict else None
            landed = self.wait_path(lands, timeout_s=60)
            h.record_wire({"quiet": "after the story"}, {"url": landed, "said": said.get("said"), "verdict": heard})
            h.add_screenshot(self._b.screenshot("story-landed"))
            return {"landed": landed, "said": said.get("said"), "verdict": heard}

    def hear_verdict(self, landing: re.Pattern, *, timeout_s: float = 30) -> dict:
        """Spec 161 FR-2 (keel-web 257 FR-4): the verdict card read -- its words, what Keel said beside it -- then the
        quiet (a yes or four seconds of silence goes on). Where no card stands (`drawn` false) the page went on without
        it."""
        card = self.page.locator(VERDICT_CARD)
        deadline = time.monotonic() + timeout_s * self.patience
        while time.monotonic() < deadline and not card.count() and not landing.search(self.page.url):
            self.page.wait_for_timeout(200)
        if not card.count():
            return {"drawn": False, "url": self.page.url}
        words = _tc(card)
        said: list[str] = []
        ask_by = time.monotonic() + 20 * self.patience
        while time.monotonic() < ask_by and card.count():
            line = _tc(self.page.locator("[data-testid=story-check-said]")) or _tc(self.page.locator(
                "[data-testid=story-state]"))
            if line and line not in said:
                said.append(line)
            if VERDICT_ASK in " ".join(said):
                break
            self.page.wait_for_timeout(200)
        h_shot = self._b.screenshot("story-verdict")
        if not landing.search(self.page.url):
            self.silence(timeout_s=60, landed=landing)
        return {"drawn": True, "words": words, "said": said, "shot": h_shot}


class StoryWire:
    """Spec 161 (keel-cloud 268-270 on contract 87): the founder's story told on the wire, as keel-web 257's page sends
    it -- each beat's words whole (`PUT story/turns/{n}`, the done words never in them), beat 3's list and beat 7's rows
    closed by `done: true`, the way's one ask answered on beat 3, a correction on the board (`POST story/correct`), the
    boxes' yes (`POST story/confirm`), the build waited for, the window stored (`PUT context/window`). Used where the
    keel-web checkout the stack serves does not yet carry keel-web 257 (`web_has_257`): the cloud's reads are held on the
    wire and every screen check is said to be pending keel-web 257, by name. `call` is `Run.call` (the founder's cookie)."""

    def __init__(self, call, project_id: str):
        self.call = call
        self.base = f"/v2/projects/{project_id}"
        self.writes: list[dict] = []

    def _w(self, method: str, path: str, body: dict | None) -> dict:
        status, answer = self.call(method, f"{self.base}/{path}", body)
        row = {"method": method, "path": path, "status": status, "sent": body,
               "body": answer if isinstance(answer, dict) else None}
        self.writes.append(row)
        return row

    def beat(self, n: int, words: str, *, ask_answer: str | None = None) -> dict:
        put = self._w("PUT", f"story/turns/{n}", {"text": words})
        seen: dict = {"turn": n, "put": put, "asked": {"question": STORY_QUESTIONS.get(n)}}
        body = put.get("body") or {}
        if body.get("ask") and ask_answer:
            seen["ask"] = body["ask"]
            put = self._w("PUT", f"story/turns/{n}", {"text": ask_answer})
            seen["way"] = put
            body = put.get("body") or {}
        if n in (3, OTHER_TASKS_BEAT) and body.get("next") == n and (put.get("status") or 500) < 400:
            closed = self._w("PUT", f"story/turns/{n}", {"done": True})
            seen["closed"] = {"status": closed["status"], "sent": closed["sent"],
                              "next": (closed.get("body") or {}).get("next"), "by": "done: true"}
            body = closed.get("body") or {}
        seen["next"] = str(body.get("next") or "")
        return seen

    def tell(self, beats: list[tuple[int, str]], *, words3: str | None = None,
             limits_only: tuple[str, str] | None = None) -> list[dict]:
        """The beats in order on the wire: beat 3 `words3` (the long telling, or the two parts joined) or the
        limitations alone then the way after the ask; beat 6 only where the last answer's `next` names it."""
        seen: list[dict] = []
        nxt = "1"
        for n, words in beats:
            if n == WHEN_BEAT and nxt != str(WHEN_BEAT):
                continue
            if n == 3 and limits_only:
                one = self.beat(3, limits_only[0], ask_answer=limits_only[1])
            else:
                one = self.beat(n, words3 if (n == 3 and words3) else words)
            seen.append(one)
            nxt = one["next"]
            if (one["put"].get("status") or 500) >= 400:
                raise AssertionError(f"beat {n} refused on the wire {one['put'].get('status')}: {one['put'].get('body')}")
        return seen

    def story(self) -> dict:
        status, body = self.call("GET", f"{self.base}/story", None)
        return body if status < 400 and isinstance(body, dict) else {}

    def correct(self, words: str) -> dict:
        return self._w("POST", "story/correct", {"text": words})

    def confirm(self) -> dict:
        return self._w("POST", "story/confirm", None)

    def built(self, *, timeout_s: float = 120) -> dict:
        deadline = time.monotonic() + timeout_s
        story = self.story()
        while time.monotonic() < deadline and ((story.get("build") or {}).get("state") not in ("ready", "failed")):
            time.sleep(1)
            story = self.story()
        return story

    def window(self, recall_window: dict) -> dict:
        return self._w("PUT", "context/window", {"recallWindow": dict(recall_window)})


def _json(response) -> dict | None:
    try:
        body = response.json()
        return body if isinstance(body, dict) else None
    except Exception:  # noqa: BLE001
        return None


# ------------------------------------------------------------------------------------ the solution start (242 / 245)

SOLUTION_START = "[data-testid=solution-start]"
IDEA_TURN = "[data-testid=idea-turn]"
IDEA_CHECK = "[data-testid=idea-check]"
#: keel-web 242 `lib/solutionStart.ts`: the wait kept in the browser while a problem project is created.
PENDING_START_KEY = "keel.solutionStart"
#: keel-web 245 `translate.ts` STORY.solution.newProblem: the which-problem page's create (drawn *+ A new problem*).
NEW_PROBLEM = "A new problem"
COMPATIBILITY_PATH = re.compile(r"/define/solution/q/1(?:$|[?#])")
#: Spec 158 FR-5: the colour the founder says with the name (keel-cloud 263 FR-9: a colour said in words, written as a
#: hex by the reader -- the fake's own table, `FakeStoryReadings.COLOURS`).
SAID_COLOUR = ("blue", "#2f6db5")


def problem_name_of(name: str) -> str:
    """keel-web 242 `problemNameOf`: the problem project's name, made from the solution's."""
    return f"{name.strip()}: the problem"


def said_name(name: str, colour: str = SAID_COLOUR[0]) -> str:
    """Idea beat 1 as the founder says it: the name, then a colour in words (*Runcheck, in blue*)."""
    return f"{name}, in {colour}"


class SolutionStart:
    """keel-web 245's which-problem page (`SolutionPick`, FR-11: a page -- no orb, nothing spoken; skipped with exactly
    one defined problem project, a problem project created at once with none), walked before the solution project
    exists: the candidates (`solution-candidate`, `data-project`, `data-picked`), *A new problem* and *Pick* /
    *Continue with this problem*."""

    def __init__(self, page, recorder, base_url: str):
        self.page = page
        self.base = base_url.rstrip("/")
        self._b = _BrowserStep(recorder, page, "founder")

    def read(self) -> dict:
        root = self.page.locator(SOLUTION_START).first
        root.wait_for(state="visible", timeout=30_000)
        try:
            root.get_by_test_id("solution-candidate").first.wait_for(state="visible", timeout=10_000)
        except Exception:  # noqa: BLE001 - none listed: recorded
            pass
        # each row's first frame is its project's story, fetched after the list (a row draws a blank plate until its
        # story comes): waited for a little, so a slow fetch is not read as no frame (spec 158c's first run)
        try:
            self.page.wait_for_function(
                "() => [...document.querySelectorAll('[data-testid=solution-candidate]')].every((r) => "
                "r.querySelector('[data-testid=solution-candidate-frame]'))", timeout=10_000)
        except Exception:  # noqa: BLE001 - a row with no frame: recorded, judged by the leg
            pass
        rows = []
        for row in root.get_by_test_id("solution-candidate").all():
            rows.append({"project": row.get_attribute("data-project"), "picked": row.get_attribute("data-picked") is not None,
                         "words": _tc(row), "press": _tc(row.get_by_test_id("solution-pick")),
                         "frame": row.get_by_test_id("solution-candidate-frame").count()})
        return {"say": _tc(root.get_by_test_id("solution-start-say")), "title": _tc(root.locator("h2").first),
                "rows": rows, "none": _tc(root.get_by_test_id("solution-start-none")) or None,
                "create": _tc(root.get_by_test_id("solution-create-problem")),
                "orb": self.page.locator(ORB).count(), "pending": self.pending()}

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
        """The market step's *Start* on a solution scope: it opens the which-problem page, creating nothing."""
        self.page.get_by_role("button", name=re.compile(r"^start$", re.I)).first.click()
        self.page.locator(SOLUTION_START).first.wait_for(state="visible", timeout=30_000)

    def create_problem(self) -> str:
        """*A new problem*: one POST (scope PROBLEM, the problem's name), then its conversation's opening."""
        with self._b.step("which problem: A new problem") as h:
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.split("?")[0].endswith("/v2/projects"), timeout=30_000) as got:
                self.page.get_by_test_id("solution-create-problem").first.click()
            body = _json(got.value) or {}
            sent = got.value.request.post_data_json
            self.page.locator(STORY_START).first.wait_for(state="visible", timeout=30_000)
            h.record_wire(sent, {"status": got.value.status, "projectId": body.get("projectId"), "url": self.page.url})
            self.created_problem = {"sent": sent, "status": got.value.status, "body": body}
            return str(body.get("projectId"))

    def pick(self, problem_id: str | None = None) -> dict:
        """*Pick* (or *Continue with this problem* on the picked row): the one create request with `parentProjectId`."""
        with self._b.step("which problem: the problem picked -- the solution project created on it") as h:
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


#: The brand name's label in the idea's story, read while it plays (spec 158 FR-5, the review condition: the name
#: clearly visible, never faded, cropped or shrunk; the icon in the brand's colour).
_BRAND_IN_STORY = r"""(name) => {
  const root = document.querySelector('[data-testid=idea-story-player]');
  if (!root) return null;
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim().toLowerCase();
  const box = root.getBoundingClientRect();
  const label = [...root.querySelectorAll('.lb')].find((el) => norm(el.textContent) === norm(name));
  const opacity = (el) => { let o = 1; for (let n = el; n && n !== document.body; n = n.parentElement) {
      const s = getComputedStyle(n); o *= parseFloat(s.opacity || '1'); if (s.visibility === 'hidden' || s.display === 'none') o = 0; }
    return o; };
  const out = { player: { w: box.width, h: box.height }, label: null,
                badges: [...root.querySelectorAll('.sty-badge')].map((b) => getComputedStyle(b).backgroundColor) };
  if (label) {
    const r = label.getBoundingClientRect();
    const words = [...label.querySelectorAll('span')];
    const s = getComputedStyle(label);
    out.label = { text: (label.textContent || '').trim(), color: s.color, fontPx: parseFloat(s.fontSize),
      opacity: Math.min(opacity(label), ...words.map(opacity)),
      inside: r.left >= box.left - 1 && r.right <= box.right + 1 && r.top >= box.top - 1 && r.bottom <= box.bottom + 1,
      clipped: label.scrollWidth > label.clientWidth + 1 || label.scrollHeight > label.clientHeight + 1,
      w: r.width, h: r.height };
  }
  return out;
}"""


def rgb_of(hex_colour: str) -> str:
    """`#2f6db5` -> `rgb(47, 109, 181)` (a computed style's form)."""
    h = hex_colour.lstrip("#")
    return f"rgb({int(h[0:2], 16)}, {int(h[2:4], 16)}, {int(h[4:6], 16)})"


# ------------------------------------------------------------------------------------ spec 162: the founder's solution
# keel-cloud 271 (contract 88) / 273 (89) / 272 (90), keel-web 259 / 261: the problem's film opening the solution, the
# brand typed, four long beats, the board's six rows, the film in five chapters behind the brand plate, the verdict
# line and the pilot ask, then the ready page. Every fixed word here is keel-cloud's (`IdeaTurns`, `SolutionLink`) or
# keel-web's (`translate.ts` IDEA), copied word for word; nothing is composed.

#: Spec 162 FR-1 (keel-cloud 271 FR-3 to FR-6): the four beats -- 1 the workflow, 2 the setup, 3 the limitations in
#: one breath, 4 the joy. Every one a long beat (keel-web 259 FR-3, `IDEA_LONG_BEATS`).
IDEA_BEATS = (1, 2, 3, 4)
WORKFLOW_BEAT, SETUP_BEAT, LIMITS_BEAT, JOY_BEAT = IDEA_BEATS
IDEA_LONG_BEATS = IDEA_BEATS
#: keel-cloud 271 `IdeaTurns.QUESTIONS`, verbatim (the placeholders keel-cloud's).
IDEA_QUESTIONS = {
    1: "Now I want to know how {name} does the same task. With {name} in their hands, how does {role} {task}, from the "
       "first step to the last?",
    2: "Before {role} can use {name} this way, is there anything they must do first? A setup, training, a security "
       "review, data to send? Tell me, or say none.",
    3: "Today they ran into {n} things: {the limitations}. Tell me how {name} solves them.",
    4: "In the problem, the cost to them was {the pain}. Now, with {name}, what do they get instead? Tell me the "
       "opposite of that cost.",
}
#: keel-cloud 271 `IdeaTurns.OPENING` -- said after the problem's film ({role} the story's people).
IDEA_OPENING = ("Now we know what {role} are trying to do and how they do it today. We know where it falls short and "
                "what it costs them. Now imagine how your product solves it. First, let us create the brand.")
#: keel-cloud 271 `IdeaTurns`: the three asks, the cross, the readbacks' fixed words.
STEP_ASK = "Start from the first thing they do. What happens first?"
UNMATCHED_ASK = "I did not understand how {X} is solved. Can you think about it?"
NOT_SOLVED = "I will show {X} as not solved."
FEATURE_ASK = "That is what it does. What do they get back because of it?"
NOTHING_TO_SET_UP = "Nothing to set up."
#: keel-cloud 271 FR-11 (`IdeaTurns.PILOT_ASK`).
PILOT_ASK = ("Now {name} is defined. Would you like to invite the people who finish the interview to try it as a "
             "pilot?")
#: keel-cloud 271 FR-8: the verdict on the default bins (`p_60_80` on the three).
SOLUTION_VERDICT_LINE = ("I will call this real if at least six in ten say it fits how they work, six in ten say it is "
                         "better, and six in ten say they could start without trouble.")
#: keel-cloud 271 FR-9: the film's first line.
FILM_OPENING = "This time, {name} is on the screen."
#: keel-cloud 271 FR-9 (`IdeaScene.chapter`) and keel-web 261 (`STORY.chapters`): the five chapters, in order, and
#: their band's words.
IDEA_CHAPTERS = ("before", "task", "solves", "better", "joy")
CHAPTER_WORDS = {"before": "Before", "task": "The task", "solves": "What it solves", "better": "Better",
                 "joy": "What they get"}
#: keel-cloud 271 FR-9: at most eleven scenes.
IDEA_MAX_SCENES = 11
#: keel-web 259 FR-6 (`PLATE_MS`): the plate alone before the film's first scene.
PLATE_MS = 3_000
#: Spec 162 FR-1 (keel-web 259 FR-4, `ideaBoardRows`): the board's six rows by `data-box`, in order.
IDEA_BOARD_ROWS = ("product", "workflow", "setup", "statement", "limits", "joy")
IDEA_BOARD = "[data-testid=idea-board]"
#: keel-web 259 FR-2 (`IDEA.brandPage.logoLine`): the fixed line under the drop box, and a bad file's refusal.
LOGO_LINE = ("A square PNG or SVG, 256 to 4,096 px a side, up to 1 MB. It is drawn small, so a simple mark reads "
             "best.")
#: keel-web 259 FR-7 (`IDEA.failed`): the failed build's line and the chapter as the sentence names it.
FAILED_SAY = "Keel could not draw {part}. Say that part again?"
FAILED_PARTS = {"before": "the setup", "task": "the task", "solves": "what it solves", "better": "what is better",
                "joy": "what they get", "brand": "the brand"}
#: keel-cloud 271 judgement call 9 (the beat a chapter reopens; keel-web `BEAT_OF_CHAPTER`).
BEAT_OF_CHAPTER = {"before": 2, "task": 1, "solves": 3, "better": 3, "joy": 4}
#: keel-web 259 `BRAND_SWATCHES`: the brand page's five; the walk picks the second.
BRAND_SWATCHES = ("#2255aa", "#1f7a5a", "#b8432f", "#7a4fb0", "#c98a1b")
#: The brand the walk types (spec 162 FR-1): the name is the one the cloud's fake script tells the beats with (keel-cloud
#: 271 judgement call 21: an invented product, the payroll story's), a tagline of the walk's own (eight words at most).
IDEA_NAME = "Runcheck"
IDEA_TAGLINE = "Every changed line, seen before sign-off."
IDEA_COLOUR = BRAND_SWATCHES[1]
#: The pilot's answer said by voice (keel-web 259 FR-5: a yes writes `PUT idea/pilot {offer: true}`).
PILOT_YES = "Yes, please."
SOLUTION_READY_PATH = re.compile(r"/define/ready(?:/|$|[?#])")
IDEA_START = "[data-testid=idea-start]"
IDEA_BRAND_PAGE = "[data-testid=idea-brand-page]"


def _idea_answers(script: dict, n: int) -> list[dict]:
    return [t for t in _answers(script, "ideaTurns") if int(t["turn"]) == n]


def said_idea(script: dict) -> list[tuple[int, str]]:
    """Spec 162 FR-1 (keel-cloud 271 FR-3 to FR-6): the four beats as the founder says them -- each beat's first answer
    in the script (beat 1 the workflow with who does each step, 2 the setup, 3 the limitations in one breath, 4 the joy);
    the later answers of a beat are the special scripts (`idea_scripts`). Any other order is refused by name."""
    firsts: list[tuple[int, str]] = []
    seen: list[int] = []
    for t in _answers(script, "ideaTurns"):
        n = int(t["turn"])
        if n not in seen:
            seen.append(n)
            firsts.append((n, str(t["heard"])))
    if seen != list(IDEA_BEATS):
        raise ValueError(f"the fake readings' idea beats are not keel-cloud 271's four (1, 2, 3, 4): {seen}")
    return firsts


def idea_reading_of(script: dict, turn: int, heard: str | None = None, *, correction: bool = False) -> dict:
    """The scripted reading of idea beat `turn` (its first answer, or the one heard as `heard`; a correction's)."""
    for t in script.get("ideaTurns") or []:
        if int(t["turn"]) == turn and bool(t.get("correction")) == correction \
                and (heard is None or t["heard"] == heard):
            return dict(t["result"])
    raise KeyError(f"no fake idea reading for beat {turn}{' (a correction)' if correction else ''}")


def idea_scripts(script: dict) -> dict:
    """Spec 162 FR-1: keel-cloud 271's special scripts on the fake readings, by what they walk --
    `workflow` beat 1's three steps (an advantage held); `advantages_only` beat 1 answered with advantages alone and
    `first_step` the answer after code's ask; `setup` beat 2 with rows and `setup_none` with none; `limits` beat 3's
    long answer (one limitation left unmatched: code's ask), `match` the correction that matches it and `cross` the
    one that leaves it a cross; `joy` beat 4's joy and `features` its feature answers (code's ask)."""
    one = _idea_answers(script, 1)
    stepped = [t for t in one if (t["result"].get("workflow") or [])]
    bare = [t for t in one if not (t["result"].get("workflow") or [])]
    two = _idea_answers(script, 2)
    three = _idea_answers(script, 3)
    fixes = [t for t in script.get("ideaTurns") or [] if int(t["turn"]) == 3 and t.get("correction")]
    match = [t for t in fixes if all(a.get("solved") for a in t["result"].get("limit_answers") or [])]
    cross = [t for t in fixes if not all(a.get("solved") for a in t["result"].get("limit_answers") or [])]
    four = _idea_answers(script, 4)
    joys = [t for t in four if not t["result"].get("is_feature")]
    features = [t for t in four if t["result"].get("is_feature")]
    pick = lambda rows: str(rows[0]["heard"]) if rows else None                       # noqa: E731
    return {"workflow": pick([t for t in stepped if (t["result"].get("heard") or {}).get("advantage")] or stepped),
            "advantages_only": pick(bare),
            "first_step": pick([t for t in stepped if not (t["result"].get("heard") or {}).get("advantage")]),
            "setup": pick([t for t in two if t["result"].get("setup")]),
            "setup_none": pick([t for t in two if t["result"].get("setup_none")]),
            "limits": pick(three), "match": pick(match), "cross": pick(cross),
            "joy": pick(joys), "features": [str(t["heard"]) for t in features]}


def idea_question(n: int, *, name: str, person: str | None = None, people: str | None = None, job: str | None = None,
                  limits: list[str] | None = None, cost: str | None = None) -> str:
    """keel-cloud 271 `IdeaTurns.question(n, ...)`: beat `n`'s question with every placeholder filled -- the brand's
    name (else *it*), beat 1 the person with an indefinite article and the job, beat 2 the people, beat 3 the
    limitations counted and joined, beat 4 the cost (its first letter lower-case)."""
    said = name.strip() if name and name.strip() else "it"
    q = IDEA_QUESTIONS[n].replace("{name}", said)
    if n == 1:
        return q.replace("{role}", _with_article(person or "someone")).replace("{task}", _bare_end(job or "do the task"))
    if n == 2:
        return q.replace("{role}", (people or "they").strip())
    if n == 3:
        rows = [_lower_first(x) for x in limits or []]
        return q.replace("{n}", _count(len(rows))).replace("{the limitations}", _joined(rows))
    return q.replace("{the pain}", _lower_first(_bare_end(cost or "what it cost them")))


def idea_opening(people: str) -> str:
    """keel-cloud 271 `IdeaTurns.opening`: the opening with the story's people."""
    return IDEA_OPENING.replace("{role}", people.strip())


def unmatched_line(template: str, limits: list[str]) -> str:
    """keel-cloud 271 `IdeaTurns.unmatched`: the ask (or the cross) naming every unmatched limitation."""
    return template.replace("{X}", _joined([_lower_first(x) for x in limits]))


def pilot_ask(name: str) -> str:
    return PILOT_ASK.replace("{name}", name.strip())


def _bare_end(text: str) -> str:
    return re.sub(r"[.!?;:,\s]+$", "", str(text or "").strip()).strip()


def _lower_first(row: str) -> str:
    if not row or len(row) < 2 or (row[0].isupper() and row[1].isupper()):
        return row
    return row[0].lower() + row[1:]


_NUMBERS = ("no", "one", "two", "three", "four", "five", "six")


def _count(n: int) -> str:
    return _NUMBERS[n] if 0 <= n < len(_NUMBERS) else str(n)


def _joined(rows: list[str]) -> str:
    kept = [_bare_end(r) for r in rows if r and r.strip()]
    if not kept:
        return ""
    return kept[0] if len(kept) == 1 else ", ".join(kept[:-1]) + " and " + kept[-1]


def _with_article(person: str) -> str:
    said = person.strip()
    lower = said.lower()
    if lower.startswith(("a ", "an ", "the ")) or lower in ("someone", "they"):
        return said
    return ("an " if lower[:1] in "aeiou" else "a ") + said


def board_six_verdict(card: dict | None, idea: dict | None, *, name: str, tagline: str | None) -> dict:
    """Spec 162 FR-1 (keel-web 259 FR-4): the board read by `data-box` -- the six rows in order (the setup row may be
    *Nothing to set up*), each holding the served idea's words: the product the name and the tagline, the workflow each
    step with its doer (`card-step-by`: *they* or the name), the setup its rows, the statement, the limitations each
    with its tick or cross as `limitAnswers` says, the joy. `ok`, the order, what is missing."""
    idea = idea or {}
    rows = card_rows(card)
    order = list(rows)
    want_order = [k for k in IDEA_BOARD_ROWS if k in rows]
    missing: dict = {}

    def holds(key: str, words: list[str]) -> None:
        drawn = _bare_words(rows.get(key))
        gone = [w for w in words if w and _bare_words(w) not in drawn]
        if key not in rows or gone:
            missing[key] = gone or ["(no row)"]
    holds("product", [name] + ([tagline] if tagline else []))
    holds("workflow", [s.get("step") for s in idea.get("workflow") or []])
    holds("setup", list(idea.get("setup") or []) or ([NOTHING_TO_SET_UP.rstrip(".")] if idea.get("setupNone") else []))
    holds("statement", [idea.get("statement")] if idea.get("statement") else [])
    holds("limits", [a.get("limit") for a in idea.get("limitAnswers") or []])
    holds("joy", [idea.get("joy")] if idea.get("joy") else [])
    marks = [i.get("mark") for i in card_items(card, "limits")]
    want_marks = ["tick" if a.get("solved") else "cross" for a in idea.get("limitAnswers") or []]
    if marks != want_marks:
        missing["marks"] = {"drawn": marks, "want": want_marks}
    return {"ok": order == list(IDEA_BOARD_ROWS) and not missing, "order": order, "in_order": order == want_order,
            "missing": missing, "marks": marks}


def _you(text: str | None) -> str:
    """Words compared with the person turned: the film says *you* where the board says *they*."""
    w = _bare_words(text)
    for a, b in ((r"\bthey\b", "you"), (r"\bthem\b", "you"), (r"\btheir\b", "your")):
        w = re.sub(a, b, w)
    return w


def idea_scenes_verdict(story: dict | None, idea: dict | None, *, name: str, tagline: str | None = None,
                        pictures: bool = True) -> dict:
    """Spec 162 FR-3 (keel-cloud 271 FR-9, 273 FR-3): the idea's film read against its board -- at most eleven scenes;
    the opening line exactly *This time, {name} is on the screen.*; the chapters in order (`before`, `task`, `solves`,
    `better`, `joy`, each on its first scene); the setup scene there if and only if the setup is non-empty; one scene per
    workflow step; the limitations scene's marks the board's; the advantage's chapter there if and only if one was read;
    the joy scene last (`joy: true`, its line the board's joy, the person turned); the brand on every screen scene; a
    picture on every scene (contract 89; `pictures`); one clip a line (the ask line's too); the plate the brand with the
    tagline. `ok` and every part by name."""
    story, idea = story or {}, idea or {}
    scenes = [s or {} for s in story.get("scenes") or []]
    chapters = [(i, s.get("chapter")) for i, s in enumerate(scenes) if s.get("chapter")]
    keys = [c for _, c in chapters]
    at = {c: i for i, c in chapters}
    ordered = keys == [c for c in IDEA_CHAPTERS if c in keys] and len(set(keys)) == len(keys)

    def span(chapter: str) -> list[dict]:
        if chapter not in at:
            return []
        start = at[chapter]
        later = [i for i, c in chapters if i > start]
        return scenes[start:(later[0] if later else len(scenes))]
    setup = list(idea.get("setup") or [])
    workflow = list(idea.get("workflow") or [])
    want_marks = [{"limit": a.get("limit"), "mark": "tick" if a.get("solved") else "cross"}
                  for a in idea.get("limitAnswers") or []]
    solves = span("solves")
    marks = [{"limit": m.get("limit"), "mark": m.get("mark")} for m in (solves[0].get("marks") if solves else []) or []]
    last = scenes[-1] if scenes else {}
    screens = [s for s in scenes if s.get("pictogramId") == "screen" or s.get("screen")]
    plate = story.get("plate") or {}
    clips = len(story.get("clipIds") or [])
    parts = {
        "at most eleven": 0 < len(scenes) <= IDEA_MAX_SCENES,
        "the opening line": bool(scenes) and scenes[0].get("line") == FILM_OPENING.replace("{name}", name),
        "the chapters in order": ordered and keys[:1] == ["before"] and keys[-1:] == ["joy"] and "task" in keys
        and "solves" in keys,
        "the setup scene iff a setup": len(span("before")) == (2 if setup else 1),
        "one scene a step": len(span("task")) == len(workflow),
        "the limitations' marks the board's": marks == want_marks,
        "the advantage iff read": ("better" in keys) == bool(idea.get("advantage")),
        "the joy last": last.get("joy") is True and last.get("chapter") == "joy"
        and sum(1 for s in scenes if s.get("joy")) == 1
        and (not idea.get("joy") or _you(idea.get("joy")) in _you(last.get("line"))),
        "the brand on every screen": all(((s.get("screen") or {}).get("name") == name) for s in screens),
        "a picture on every scene": not pictures or all(s.get("pictureAssetId") for s in scenes),
        "one clip a line": clips in (len(scenes), len(scenes) + 1),
        "the plate the brand": plate.get("name") == name and (tagline is None or plate.get("tagline") == tagline),
    }
    return {"ok": all(parts.values()), "parts": parts, "scenes": len(scenes), "chapters": keys,
            "lines": [s.get("line") for s in scenes], "marks": marks, "want_marks": want_marks,
            "clips": clips, "plate": plate}


def failed_say(chapter: str) -> str:
    """keel-web 259 FR-7: the failed build's line for its chapter."""
    return FAILED_SAY.replace("{part}", FAILED_PARTS.get(chapter, "that part"))


def png_bytes(width: int, height: int) -> bytes:
    """A PNG of `width` x `height` (one grey row repeated), built here -- the brand page's refusal of a non-square
    logo is walked with it (keel-web 259 FR-2: refused on the spot, nothing uploaded)."""
    import struct                                                                   # noqa: PLC0415
    import zlib                                                                     # noqa: PLC0415

    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + b"\x80" * width for _ in range(height))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 0, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class IdeaWalk(Conversation):
    """keel-web 259's founder's solution on a solution project (spec 162 FR-1 to FR-3): `define/idea/start` -- the
    problem's film played, the opening said, `story/confirm` stamped with no words; `define/idea/brand` -- the brand
    typed (no orb); the four long beats `define/idea/1..4`, each closed by the done word; the board's six rows by the
    quiet; the building screen; the plate and the film in chapters by the quiet; the verdict line by the quiet; the
    pilot ask answered *yes*; then the ready page."""

    def idea_writes(self, n: int) -> list[dict]:
        return self.writes_to(rf"/idea/turns/{n}$")

    # ---------------------------------------------------------------------------------------- the film, the opening
    def film_then_opening(self, project_id: str) -> dict:
        """`define/idea/start`: the stage's opener (or the begin screen) passed, the problem's film played through the
        one player (`idea-problem-film`), the opening said (`idea-start-said`), then `story/confirm` stamped with no body
        and the brand page opened -- no board, no *still the problem*."""
        with self._b.step("the problem's film, then the opening; the stamp with no words") as h:
            self.listen()
            self.begin()
            self.page.locator(IDEA_START).first.wait_for(state="visible", timeout=60_000)
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/story/confirm"), timeout=180_000) as got:
                woke = self.wake()
                film = self.page.locator("[data-testid=idea-problem-film]")
                seen: dict = {"woke": woke, "film": False, "said": None, "board": False, "still": False}
                deadline = time.monotonic() + 150 * self.patience
                while time.monotonic() < deadline:
                    try:
                        seen["film"] = seen["film"] or film.count() > 0
                        said = _tc(self.page.locator("[data-testid=idea-start-said]"))
                        if said:
                            seen["said"] = said
                        seen["board"] = seen["board"] or self.page.locator("[data-testid=story-boxes]").count() > 0
                        seen["still"] = seen["still"] or self.page.locator("[data-testid=idea-still]").count() > 0
                    except Exception:  # noqa: BLE001 - the page moved under the read
                        pass
                    if "/define/idea/brand" in self.page.url:
                        break
                    self.page.wait_for_timeout(150)
            seen["confirm"] = {"status": got.value.status, "sent": got.value.request.post_data,
                               "body": _json(got.value)}
            seen["screen"] = self.snapshot()
            self.wait_path(r"/define/idea/brand$")
            h.add_screenshot(self._b.screenshot("idea-start"))
            h.record_wire({"POST": "story/confirm (no words)"}, {k: seen[k] for k in ("said", "film", "confirm")})
            return seen

    # ---------------------------------------------------------------------------------------- the brand page
    def brand_page(self, *, name: str = IDEA_NAME, tagline: str = IDEA_TAGLINE, colour: str = IDEA_COLOUR) -> dict:
        """`define/idea/brand` (keel-web 259 FR-2): the one typed page -- the name, the tagline (its counter), a swatch,
        the logo line read word for word, a non-square PNG refused on the spot with that same line and nothing uploaded,
        then *Continue*: `PUT idea/brand {name, colour, tagline}` and the first beat opens."""
        with self._b.step("the brand page: the name, a colour, a tagline; a non-square logo refused; Continue") as h:
            root = self.page.locator(IDEA_BRAND_PAGE).first
            root.wait_for(state="visible", timeout=60_000)
            seen: dict = {"orb": self.page.locator(ORB).count(), "line": _tc(root.get_by_test_id("idea-logo-line"))}
            root.get_by_test_id("idea-name").fill(name)
            root.get_by_test_id("idea-tagline").fill(tagline)
            seen["count"] = _tc(root.get_by_test_id("idea-tagline-count"))
            swatch = root.locator(f"[data-testid=idea-swatch][aria-label*='{colour}' i]")
            (swatch.first if swatch.count() else root.get_by_test_id("idea-swatch").nth(BRAND_SWATCHES.index(colour))
             ).click()
            uploads: list = []
            watch = lambda r: uploads.append(r.url) if "/idea/icon" in r.url else None      # noqa: E731
            self.page.on("request", watch)
            try:
                root.get_by_test_id("idea-icon-file").set_input_files(
                    {"name": "wide-logo.png", "mimeType": "image/png", "buffer": png_bytes(400, 300)})
                try:
                    root.get_by_test_id("idea-icon-fault").wait_for(state="visible", timeout=10_000)
                except Exception:  # noqa: BLE001 - recorded, judged by the leg
                    pass
                seen["fault"] = _tc(root.get_by_test_id("idea-icon-fault"))
                self.page.wait_for_timeout(500)
            finally:
                self.page.remove_listener("request", watch)
            seen["uploads"] = uploads
            seen["preview"] = _tc(root.get_by_test_id("idea-brand-preview"))
            h.add_screenshot(self._b.screenshot("idea-brand"))
            with self.page.expect_response(lambda r: r.request.method == "PUT" and r.url.split("?")[0]
                                           .endswith("/idea/brand"), timeout=30_000) as got:
                root.get_by_test_id("idea-brand-continue").click()
            seen["put"] = {"status": got.value.status, "sent": got.value.request.post_data_json,
                           "body": _json(got.value)}
            self.wait_path(r"/define/idea/1$")
            h.record_wire({"PUT": "idea/brand"}, seen["put"])
            return seen

    # ---------------------------------------------------------------------------------------- one long beat
    def beat(self, n: int, words: str, *, then: list[str] | None = None,
             two_part: tuple[str, str] | None = None) -> dict:
        """One long beat (keel-web 259 FR-3): Keel's question read, the words said with the done word as their last (a
        long beat never closes on the quiet), the reading read back; where the answer is an `ask` (beat 1's first step,
        beat 4's feature) or beat 3's readback asks (`done: false`), the next of `then` is said -- sent as the beat's
        second answer, or with `correction: true` on beat 3 -- until the beat closes (`done: true`) and the page goes on.
        `two_part`: the first part said, `TWO_PART_QUIET_S` of quiet read (nothing sent, *Take your time.*), then the
        second with the done word. Returns what the screen drew and every write of the beat."""
        then = list(then or [])
        with self._b.step(f"idea beat {n}") as h:
            self.page.locator(f"{IDEA_TURN}[data-turn='{n}']").first.wait_for(state="visible", timeout=60_000)
            log = self.orb_log()
            mark = next((i for i, row in enumerate(log) if str(row.get("path") or "").endswith(f"/define/idea/{n}")),
                        len(log))
            seen: dict = {"turn": n, "asked": self.snapshot(), "answers": [], "long": True}
            try:
                self.page.wait_for_function("() => { const el = document.querySelector('[data-testid=story-q]'); "
                                            "return !!el && el.textContent.trim().length > 0; }", timeout=30_000)
            except Exception:  # noqa: BLE001 - recorded
                pass
            seen["question"] = _tc(self.page.locator("[data-testid=story-q]"))
            if two_part:
                seen["two_part"] = self._two_parts(n, two_part)
                put = self.idea_writes(n)[-1] if self.idea_writes(n) else {}
            else:
                put = self.put_after(rf"/idea/turns/{n}$", lambda: self.voice.say(with_done_word(words)))
            while True:
                body = put.get("body") or {}
                seen["answers"].append({"status": put.get("status"), "sent": put.get("sent"), "ask": body.get("ask"),
                                        "readback": body.get("readback"), "done": body.get("done"),
                                        "next": body.get("next")})
                if (put.get("status") or 500) >= 400:
                    raise AssertionError(f"idea beat {n} refused {put.get('status')}: {body}")
                if body.get("done"):
                    break
                if not then:
                    raise AssertionError(f"idea beat {n} still open after {len(seen['answers'])} answer(s) and the walk "
                                         f"has nothing more to say: {body.get('ask') or body.get('readback')}")
                nxt = then.pop(0)
                # the page says the ask (or the readback that asks) first; then the microphone opens again
                mark2 = len(self.orb_log())
                self.await_quiet(mark2, after=(), timeout_s=20)
                seen.setdefault("said_back", []).append(self.snapshot())
                put = self.put_after(rf"/idea/turns/{n}$", lambda w=nxt: self.voice.say(with_done_word(w)))
            seen["understood"] = None
            try:
                self.page.locator("[data-testid=idea-understood]").first.wait_for(state="visible", timeout=5_000)
                seen["understood"] = self.snapshot().get("understood")
            except Exception:  # noqa: BLE001 - the page went on first
                pass
            h.add_screenshot(self._b.screenshot(f"idea-beat-{n}"))
            self.wait_path(rf"/define/idea/(?!{n}$)(\d|check)$", timeout_s=60)
            seen["next"] = self.page.url.rstrip("/").split("/")[-1]
            seen["orb"] = orb_sequence(self.orb_log()[mark:])
            h.record_wire({"beat": n, "said": words[:300]}, {k: seen[k] for k in ("answers", "next")})
            return seen

    def _two_parts(self, n: int, parts: tuple[str, str]) -> dict:
        """A long beat in two parts (keel-web 257 FR-11 as 259 keeps it): the first, `TWO_PART_QUIET_S` of quiet (nothing
        sent, the beat open, *Take your time.*), then the second and the done word."""
        before = len(self.idea_writes(n))
        self.voice.say(parts[0])
        deadline = time.monotonic() + TWO_PART_QUIET_S
        lines: list[str] = []
        think = False
        while time.monotonic() < deadline:
            line = _tc(self.page.locator("[data-testid=story-state]"))
            if line and line not in lines:
                lines.append(line)
            think = think or self.page.locator(f"{ORB}[data-think]").count() > 0
            self.page.wait_for_timeout(250)
        quiet = {"sent_in_the_quiet": len(self.idea_writes(n)) - before,
                 "still_on_the_beat": bool(re.search(rf"/define/idea/{n}/?$", self.page.url)),
                 "state_lines": lines, "orb_thinks": think, "think_line": any(THINK_LINE in x for x in lines),
                 "listening": self.voice.listening()}
        put = self.put_after(rf"/idea/turns/{n}$", lambda: self.voice.say(with_done_word(parts[1])))
        quiet["sent"] = (put.get("sent") or {}).get("text")
        quiet["joined"] = all(_bare_words(p) in _bare_words(quiet["sent"]) for p in parts)
        return quiet

    def beats(self, plan: dict[int, dict]) -> dict:
        """The four beats in order, each `{words, then?, two_part?}` (`plan`)."""
        out = {}
        for n in IDEA_BEATS:
            p = plan[n]
            out[n] = self.beat(n, p["words"], then=p.get("then"), two_part=p.get("two_part"))
        self.wait_path(r"/define/idea/check$")
        return out

    # ---------------------------------------------------------------------------------------- the board
    def boxes(self) -> dict:
        """The board (`idea-board`): the six rows narrated and lit in turn, *Is that your idea?*, the quiet confirms
        (`idea/confirm`)."""
        with self._b.step("the board: six rows narrated, Is that your idea?, the quiet confirms") as h:
            self.page.get_by_test_id("idea-boxes-screen").first.wait_for(state="visible", timeout=60_000)
            try:
                self.page.wait_for_function(
                    "(w) => { const el = document.querySelector('[data-testid=idea-boxes-said]'); "
                    "return !!el && el.textContent.trim() === w; }", arg=IDEA_BOXES_ASK, timeout=90_000)
            except Exception:  # noqa: BLE001 - recorded
                pass
            board = self.page.evaluate(_SNAPSHOT.replace("card('[data-testid=story-boxes]')",
                                                         "card('[data-testid=idea-board]')"))
            seen = {"screen": board, "card": board.get("card"), "said": board.get("said")}
            h.add_screenshot(self._b.screenshot("idea-board"))
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.split("?")[0]
                                           .endswith("/idea/confirm"), timeout=150_000) as got:
                self.silence()
            seen["confirm"] = {"status": got.value.status, "body": _json(got.value)}
            seen["lit"] = [row.get("lit") for row in self.since() if row.get("lit")
                           and str(row.get("path") or "").rstrip("/").endswith("/define/idea/check")]
            h.record_wire({"POST": "idea/confirm (the quiet)"}, {"status": got.value.status})
            return seen

    # ---------------------------------------------------------------------------------------- the build, the film
    def building_then_film(self, *, timeout_s: float = 150) -> dict:
        """The building screen while the build builds, then (`data-state` story) the plate alone for about three seconds
        (its time read on the page's clock), the film in its chapters (the band's words read while it plays), *Is that
        how it goes with {name}?* -- or the failed build (`data-state` failed)."""
        with self._b.step("the idea's building screen, the plate, then the film in chapters") as h:
            building, state = None, None
            deadline = time.monotonic() + timeout_s * self.patience
            while time.monotonic() < deadline:
                state = self.page.locator(IDEA_CHECK).first.get_attribute("data-state") \
                    if self.page.locator(IDEA_CHECK).count() else None
                if state == "building" and building is None:
                    building = self.snapshot()
                    h.add_screenshot(self._b.screenshot("idea-building"))
                if state in ("story", "failed") or not re.search(r"/define/idea/check", self.page.url):
                    break
                self.page.wait_for_timeout(200)
            seen: dict = {"building": building, "state": state, "plate": None, "chapters": [], "pictures": 0}
            if state != "story":
                seen["failed"] = self.failed_build()
                return seen
            t0 = time.monotonic()
            plate_on = None
            plate_text = None
            until = time.monotonic() + 90 * self.patience
            while time.monotonic() < until:
                try:
                    plate = self.page.locator(".idea-plate, [data-testid=idea-plate]")
                    if plate.count() and plate.first.is_visible():
                        plate_on = plate_on or (time.monotonic() - t0)
                        plate_text = plate_text or _tc(plate.first)
                        seen["plate_seen_s"] = time.monotonic() - t0
                    chapter = _tc(self.page.locator("[data-testid=idea-story-player] [data-testid=story-chapter]"))
                    if chapter and chapter not in seen["chapters"]:
                        seen["chapters"].append(chapter)
                    seen["pictures"] = max(seen["pictures"], self.page.locator(
                        "[data-testid=idea-story-player] img[data-testid=story-picture]").count())
                    said = _tc(self.page.locator("[data-testid=idea-story-said]"))
                    if said:
                        seen["ask"] = said
                        break
                except Exception:  # noqa: BLE001 - re-rendered under the read
                    pass
                self.page.wait_for_timeout(120)
            seen["plate"] = {"text": plate_text, "first_seen_s": plate_on,
                             "held_s": (seen.get("plate_seen_s") or 0) - (plate_on or 0) if plate_on is not None
                             else None}
            seen["story"] = self.snapshot()
            h.add_screenshot(self._b.screenshot("idea-film"))
            h.record_assert({"state": "story"}, {k: seen[k] for k in ("state", "plate", "chapters", "pictures")})
            return seen

    def failed_build(self) -> dict:
        """A failed build (keel-web 259 FR-7): *Keel could not draw {chapter}. Say that part again?* on the building
        screen (`idea-building[data-failed-chapter]`), then the chapter's beat (or the brand page) opened again."""
        root = self.page.locator("[data-testid=idea-building]")
        out: dict = {"chapter": None, "said": None}
        try:
            root.first.wait_for(state="visible", timeout=15_000)
            out["chapter"] = root.first.get_attribute("data-failed-chapter")
            out["said"] = _tc(root.first.get_by_test_id("story-q"))
        except Exception:  # noqa: BLE001 - recorded
            pass
        try:
            self.wait_path(r"/define/idea/(\d|brand)$", timeout_s=60)
        except AssertionError:
            pass
        out["reopened"] = self.page.url.rstrip("/").split("/")[-1]
        return out

    # ---------------------------------------------------------------------------------------- the verdict, the pilot
    def film_yes_verdict_pilot(self, *, pilot: str = PILOT_YES) -> dict:
        """After the film: the quiet says yes; the verdict card (`story-verdict`) read, the quiet goes on; the pilot ask
        (`idea-pilot`) read and answered by voice; `PUT idea/pilot {offer}` on the wire; then the ready page."""
        with self._b.step("the film's yes, the verdict, the pilot ask answered yes, the ready page") as h:
            self.silence(timeout_s=120)
            out: dict = {}
            card = self.page.locator(VERDICT_CARD)
            deadline = time.monotonic() + 60 * self.patience
            while time.monotonic() < deadline and not card.count():
                self.page.wait_for_timeout(150)
            out["verdict"] = {"drawn": bool(card.count()), "words": _tc(card) if card.count() else None}
            said: list[str] = []
            ask_by = time.monotonic() + 30 * self.patience
            while time.monotonic() < ask_by and card.count():
                line = _tc(self.page.locator("[data-testid=idea-verdict-said]"))
                if line and line not in said:
                    said.append(line)
                if VERDICT_ASK in " ".join(said):
                    break
                self.page.wait_for_timeout(150)
            out["verdict"]["said"] = said
            h.add_screenshot(self._b.screenshot("idea-verdict"))
            self.silence(timeout_s=60)
            pilot_card = self.page.locator("[data-testid=idea-pilot-card]")
            pilot_card.first.wait_for(state="visible", timeout=60_000)
            out["pilot"] = {"ask": _tc(pilot_card.first.locator(".ucard__verdict")),
                            "options": _tc(self.page.locator("[data-testid=idea-pilot-options]"))}
            put = self.put_after(r"/idea/pilot$", lambda: self.voice.say(pilot))
            out["pilot"]["put"] = {"status": put["status"], "sent": put["sent"], "body": put["body"]}
            h.add_screenshot(self._b.screenshot("idea-pilot"))
            out["landed"] = self.wait_path(SOLUTION_READY_PATH, timeout_s=60)
            h.record_wire({"PUT": "idea/pilot"}, out["pilot"]["put"])
            return out

    def film_yes_to_money(self) -> dict:
        """On a money start's solution (keel-web 243 / 259 FR-8): the film's quiet goes back to the money start -- no
        verdict, no pilot ask."""
        with self._b.step("the film's yes, back to the money start") as h:
            self.silence(timeout_s=120)
            landed = self.wait_path(re.compile(r"start=money"), timeout_s=60)
            h.add_screenshot(self._b.screenshot("idea-landed"))
            return {"landed": landed, "verdict": self.page.locator(VERDICT_CARD).count()}


# ------------------------------------------------------------------------------------ the money front (245 FR-12)

class MoneyReplay(Conversation):
    """`define/money/start`: the opener or the begin screen, the problem's board with the idea's box lit on top (or the
    name alone), *This is the problem, and this is {name}. Now, will they pay for it?*, then the quiet opens today's
    persona step."""

    def walk(self, *, lands: re.Pattern | str = r"/define/persona$") -> dict:
        with self._b.step("the money study's one orb moment: the problem and the idea shown back, the quiet") as h:
            self.listen()
            self.begin()
            self.page.get_by_test_id("money-replay").first.wait_for(state="visible", timeout=60_000)
            woke = self.wake()
            try:
                self.page.wait_for_function(
                    "() => { const el = document.querySelector('[data-testid=story-check-said]'); "
                    "return !!el && /will they pay for it\\?$/i.test(el.textContent.trim()); }", timeout=90_000)
            except Exception:  # noqa: BLE001 - recorded
                pass
            seen = {"woke": woke, "screen": self.snapshot()}
            h.add_screenshot(self._b.screenshot("money-replay"))
            self.silence()
            seen["landed"] = self.wait_path(lands, timeout_s=60)
            seen["corrected"] = self.writes_to(r"/story/correct$")
            seen["turn"] = self.turn_read()
            h.record_wire({"quiet": "money replay"}, {"landed": seen["landed"], "said": seen["screen"].get("said")})
            return seen


# ------------------------------------------------------------------------------------ the drawn story's fit (spec 158b)

#: Spec 158b: the founder's phone (2026-11-22: "fits on a phone"): 390 x 844, as keel-web's `-phone` frames.
PHONE = {"width": 390, "height": 844}
#: Spec 158b (B): the spoken line under the frame is at most this many rows.
LINE_ROWS_MAX = 3
#: keel-web polish round 2's kinds on the drawing's groups (`data-draw`); `caption` is a text's own plate, not a drawing
#: a text may not sit on.
DRAW_KINDS_NOT_DRAWN = ("caption",)

#: One read of a story player (spec 158b): (A) every text box inside the frame (the room's caption, the labels) and the
#: spoken line under it against every drawn element's box -- keel-web's `[data-draw]` groups where they are, else the
#: SVG's top-level `<g>` children -- only what is visible now; (B) the frame, the line and the player's state inside the
#: viewport between the header (`.pbar`) and the tab bar (`.ptabs`), the page and the player's scrolling column not
#: scrolling, and the line's rows (its text's client rects, one row a distinct top). The numbers: the frame's size, the
#: person's height over the frame's, each pictogram's size, the line's font and line height.
_MEASURE_STORY = r"""(args) => {
  const root = document.querySelector(args.root);
  if (!root) return null;
  const board = root.querySelector('[data-testid=story-board], [data-testid=idea-story-board], .sty-board');
  const svg = board ? board.querySelector('svg') : null;
  const R = (el) => { const r = el.getBoundingClientRect(); return { x: Math.round(r.left), y: Math.round(r.top), w: Math.round(r.width), h: Math.round(r.height) }; };
  const seen = (el) => { let o = 1; for (let n = el; n && n.nodeType === 1; n = n.parentElement) {
      const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden') return 0; o *= parseFloat(s.opacity || '1'); }
    return o; };
  const words = (el) => (el.textContent || '').replace(/\s+/g, ' ').trim();
  const tagged = svg ? [...svg.querySelectorAll('[data-draw]')] : [];
  const drawnEls = tagged.length ? tagged : (svg ? [...svg.children].filter((c) => c.tagName.toLowerCase() === 'g') : []);
  // keel-web's strokes are drawn by `.on` (stroke-dashoffset 1 -> 0): a figure is on the board only where a stroke of
  // it is inked, and its box is those strokes' (a group with no `.ink` at all is taken whole)
  const inkedBox = (e) => {
    const inks = e.classList.contains('ink') ? [e] : [...e.querySelectorAll('.ink')];
    if (!inks.length) return R(e);
    const on = inks.filter((i) => i.classList.contains('on')).map(R).filter((b) => b.w > 0 || b.h > 0);
    if (!on.length) return null;
    const x = Math.min(...on.map((b) => b.x)); const y = Math.min(...on.map((b) => b.y));
    return { x, y, w: Math.max(...on.map((b) => b.x + b.w)) - x, h: Math.max(...on.map((b) => b.y + b.h)) - y };
  };
  const drawn = drawnEls.map((e) => ({ id: e.getAttribute('data-id') || e.getAttribute('class') || 'g', kind: e.getAttribute('data-draw') || 'g',
      box: inkedBox(e), seen: seen(e) }))
    .filter((d) => !args.notDrawn.includes(d.kind) && d.box && d.box.w > 0 && d.box.h > 0);
  // the wipes (`.sty-wipe.on`, the board's own colour over the drawing between scenes) cover what is under them
  const wipes = board ? [...board.querySelectorAll('.sty-wipe.on')].map(R).filter((b) => b.w > 0 && b.h > 0) : [];
  const under = (x, y) => wipes.some((w) => x >= w.x - 1 && x <= w.x + w.w + 1 && y >= w.y - 1 && y <= w.y + w.h + 1);
  const labels = board ? [...board.querySelectorAll('.lb')].map((el) => {
      const spans = [...el.querySelectorAll('span')];
      const o = spans.length ? Math.max(...spans.map(seen)) : seen(el);
      return { text: words(el), id: el.getAttribute('data-id') || '', box: R(el), seen: o }; }).filter((t) => t.text) : [];
  const lineEl = root.querySelector('[data-testid=story-line]');
  const line = lineEl ? { text: words(lineEl), id: 'the spoken line', box: R(lineEl), seen: seen(lineEl) } : null;
  let rows = 0; let lh = null; let font = null;
  if (lineEl && line.text) {
    const range = document.createRange(); range.selectNodeContents(lineEl);
    const tops = []; for (const r of range.getClientRects()) { if (r.width > 0 && !tops.some((t) => Math.abs(t - r.top) < 3)) tops.push(r.top); }
    rows = tops.length; const s = getComputedStyle(lineEl); lh = s.lineHeight; font = s.fontSize;
  }
  const texts = labels.concat(line && line.text ? [line] : []).filter((t) => t.seen > 0.05);
  const live = drawn.filter((d) => d.seen > 0.05);
  const hit = (a, b) => Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x) > 1 && Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y) > 1;
  const covered = (a, b) => {
    const x0 = Math.max(a.x, b.x); const x1 = Math.min(a.x + a.w, b.x + b.w);
    const y0 = Math.max(a.y, b.y); const y1 = Math.min(a.y + a.h, b.y + b.h);
    return [[x0, y0], [x1, y0], [x0, y1], [x1, y1], [(x0 + x1) / 2, (y0 + y1) / 2]].every(([x, y]) => under(x, y));
  };
  const overlaps = [];
  for (const t of texts) for (const d of live) if (hit(t.box, d.box) && !covered(t.box, d.box)) overlaps.push({ text: t.text.slice(0, 80), text_id: t.id, text_box: t.box, drawn: d.id, kind: d.kind, drawn_box: d.box });
  const frame = board ? R(board) : null;
  const person = drawn.filter((d) => d.kind === 'person' || /^(walkin|m-|man|person|walker)/.test(d.id));
  const pictos = drawn.filter((d) => d.kind === 'pictogram' || /^p\d+$/.test(d.id));
  const vis = (sel) => { const el = document.querySelector(sel); if (!el) return null; const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 ? r : null; };
  const head = vis('.pbar'); const tabs = vis('.ptabs');
  const top = head ? head.bottom : 0; const bottom = tabs ? tabs.top : window.innerHeight;
  const inside = (b) => !!b && b.y >= top - 1 && b.y + b.h <= bottom + 1 && b.x >= -1 && b.x + b.w <= window.innerWidth + 1;
  const stateEl = args.state ? document.querySelector(args.state) : null;
  const state = stateEl ? R(stateEl) : null;
  let scroller = null;
  for (let n = root.parentElement; n && n !== document.body; n = n.parentElement) {
    const s = getComputedStyle(n);
    if (/(auto|scroll)/.test(s.overflowY) && n.scrollHeight > n.clientHeight + 1) { scroller = { cls: (n.className || n.tagName).toString().slice(0, 40), scroll: n.scrollHeight, client: n.clientHeight }; break; }
  }
  const doc = document.scrollingElement || document.documentElement;
  // the screen's own content (its <main>, or the page where it has none; fixed bands and any <footer> aside) below the
  // fold -- the site's footer under it is not the story's: the page may scroll to it without the story failing to fit
  const main = root.closest('main') || document.body;
  // leaves only (an <svg> one leaf): a container holding the footer reaches the page's bottom with it
  let low = 0; let lowest = null;
  const all = [...main.querySelectorAll('*')];
  const fixed = all.filter((e) => getComputedStyle(e).position === 'fixed');
  for (const e of all) {
    const tag = e.tagName.toLowerCase();
    if (e.closest('footer') || (tag !== 'svg' && e.closest('svg')) || (tag !== 'svg' && e.children.length)) continue;
    if (fixed.some((f) => f.contains(e))) continue;
    const r = e.getBoundingClientRect();
    if (r.width > 0 && r.height > 0 && r.bottom > low && seen(e) > 0.05) {
      low = r.bottom;
      lowest = [tag, (e.getAttribute('class') || '').slice(0, 40), e.getAttribute('data-testid'), (e.textContent || '').trim().slice(0, 40)].filter(Boolean).join(' ');
    }
  }
  return {
    viewport: { w: window.innerWidth, h: window.innerHeight }, band: { top: Math.round(top), bottom: Math.round(bottom) },
    frame, person_ratio: person.length && frame ? +(Math.max(...person.map((p) => p.box.h)) / frame.h).toFixed(3) : null,
    person: person.map((p) => ({ id: p.id, w: p.box.w, h: p.box.h })),
    pictograms: pictos.map((p) => ({ id: p.id, w: p.box.w, h: p.box.h, seen: +p.seen.toFixed(2) })),
    drawn_by: tagged.length ? 'data-draw' : 'top-level g', drawn: live.length, texts: texts.length,
    line: line ? { text: line.text, rows, line_height: lh, font, box: line.box } : null, state,
    fit: { frame: inside(frame), line: inside(line && line.box), state: inside(state),
           page_scrolls: doc.scrollHeight > window.innerHeight + 1, doc: { scroll: doc.scrollHeight, view: window.innerHeight },
           content_below: low > bottom + 1 ? Math.round(low) : null, lowest: low > bottom + 1 ? lowest : null, scroller },
    overlaps, player: root.getAttribute('data-state'),
  };
}"""


def measure_story(page, root: str, *, state: str | None = None, play: bool = False, timeout_s: float = 90) -> dict:
    """Spec 158b: the drawn story read while it plays (`play`: its *Play* pressed first, the stranger's card), every
    250 ms until the player ends (or `timeout_s`): every overlap of a text on a drawn element met at any moment (one
    row a pair), every spoken line with its rows (the most), the fit at its worst, and the numbers of the fullest read."""
    if play:
        # `story-play` is the worded player's (the founder's screens; the retired text player's card). Spec 160 (keel-web
        # 256 FR-3): the AI link's film plays by itself and has no *Play* -- its icons are `ai-film-pause` /
        # `ai-film-again`, its words behind `ai-film-board` -- so it is measured with `play=False`.
        button = page.locator(f"{root} [data-testid=story-play]").first
        try:
            button.wait_for(state="visible", timeout=15_000)
            button.click()
        except Exception:  # noqa: BLE001 - recorded: nothing played
            pass
    out: dict = {"samples": 0, "overlaps": [], "lines": {}, "unfit": [], "numbers": None}
    pairs: set = set()
    best = -1
    deadline = time.monotonic() + timeout_s
    started = False
    while time.monotonic() < deadline:
        try:
            read = page.evaluate(_MEASURE_STORY, {"root": root, "state": state, "notDrawn": list(DRAW_KINDS_NOT_DRAWN)})
        except Exception:  # noqa: BLE001 - re-rendered under the read
            read = None
        if read:
            out["samples"] += 1
            for o in read["overlaps"]:
                key = (o["text"], o["drawn"])
                if key not in pairs:
                    pairs.add(key)
                    out["overlaps"].append(o)
            line = read.get("line") or {}
            if line.get("text"):
                was = out["lines"].get(line["text"])
                if not was or line["rows"] > was["rows"]:
                    out["lines"][line["text"]] = {"rows": line["rows"], "line_height": line["line_height"],
                                                  "font": line["font"], "box": line["box"]}
            fit = read["fit"]
            bad = [k for k in ("frame", "line", "state") if fit.get(k) is False and (k != "state" or read.get("state"))]
            if fit.get("content_below"):
                bad.append(f"the screen runs below the fold (to y={fit['content_below']}: {fit.get('lowest')})")
            if fit.get("page_scrolls"):
                out["page_scrolls"] = max(out.get("page_scrolls") or 0, (fit.get("doc") or {}).get("scroll") or 0)
            if fit.get("scroller"):
                bad.append(f"its column scrolls ({fit['scroller'].get('cls')})")
            if bad:
                out["unfit"].append({"what": bad, "band": read["band"], "frame": read["frame"],
                                     "line": (read.get("line") or {}).get("box"), "state": read.get("state"),
                                     "doc": fit.get("doc"), "scroller": fit.get("scroller")})
            if read["drawn"] + read["texts"] > best:
                best = read["drawn"] + read["texts"]
                out["numbers"] = {k: read[k] for k in ("viewport", "band", "frame", "person_ratio", "person",
                                                       "pictograms", "drawn_by", "drawn", "texts", "state")}
            if read.get("player") == "playing":
                started = True
            if started and read.get("player") in ("ended", "idle") or (not started and out["samples"] > 160):
                break
        page.wait_for_timeout(250)
    out["played"] = started
    out["unfit_reads"] = len(out["unfit"])
    out["unfit"] = list({json.dumps(u, sort_keys=True): u for u in out["unfit"]}.values())[:6]
    return out


def phone_page(context, browser, *, inits: tuple[str, ...] = ()):
    """A 390 x 844 context signed in as `context` is (its cookies and storage), with the founder's init scripts."""
    phone = browser.new_context(viewport=PHONE, storage_state=context.storage_state())
    for script in inits:
        phone.add_init_script(script)
    return phone, phone.new_page()


def fit_verdicts(measured: dict, *, phone: bool) -> dict:
    """Spec 158b's verdicts over one `measure_story`: `drawn` -- no text on a drawn element at any moment; `rows` -- every
    spoken line at most `LINE_ROWS_MAX` rows; and, on a phone, `fits` -- the frame, the line and the player's state
    inside the band at every read, nothing scrolling. Each `(ok, detail)`; a player never read holds none of them."""
    numbers = measured.get("numbers") or {}
    read = bool(measured.get("samples")) and bool(numbers.get("drawn"))
    lines = measured.get("lines") or {}
    rows = {text: (line or {}).get("rows") or 0 for text, line in lines.items()}
    long = {text[:80]: n for text, n in rows.items() if n > LINE_ROWS_MAX}
    out = {
        "drawn": (read and not measured.get("overlaps"),
                  {"read": read, "samples": measured.get("samples"), "drawn by": numbers.get("drawn_by"),
                   "overlaps": [{k: o.get(k) for k in ("text", "drawn", "kind", "text_box", "drawn_box")}
                                for o in (measured.get("overlaps") or [])][:12]}),
        "rows": (read and bool(rows) and not long,
                 {"lines": len(rows), "most rows": max(rows.values()) if rows else None, "over": long,
                  "font": next(iter(lines.values()), {}).get("font") if lines else None}),
    }
    if phone:
        out["fits"] = (read and not measured.get("unfit"),
                       {"viewport": numbers.get("viewport"), "band": numbers.get("band"), "frame": numbers.get("frame"),
                        "unfit": (measured.get("unfit") or [])[:3], "unfit reads": measured.get("unfit_reads"),
                        "page height (the footer below the story)": measured.get("page_scrolls")})
    return out


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
               # the badges as drawn: letters on every question here; on the Copilot card Frequency's five carry the
               # digits 1-5 (keel-web 258 FR-5, spec 164 mirror 6: `three_surfaces.badge_faults`), and the orb's sheet
               # on a film link letters Frequency A-E
               "letters": _texts(main.locator(".cpl-bubble__let")),
               "rows": _texts(main.locator(".cpl-bubble__w")) or _texts(main.locator("[role=radio]")),
               # keel-web 244 FR-4: a scale keeps its cells -- count cells, the four-point scale, Hours / Amount -- and
               # is not lettered; only the option rows (ChoiceRows, PickOneThenOne) are the copilot strip's bubbles
               "scale": main.locator(".iv-seg, .iv-scale4, .iv-cost").count(),
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

    def to_story(self, url: str, interview: dict, *, max_screens: int = 6) -> dict:
        """Spec 158b: Begin, the screener answered where it is shown, and on to the story card -- nothing pressed on it.
        `reached` where the story card stands."""
        page = self.page
        gate = interview.get("gate") or {}
        self.open(url)
        self._press(IV_BEGIN)
        page.wait_for_timeout(600)
        for _ in range(max_screens):
            kind = self._kind(gate.get("question"))
            if kind == "story":
                self._card("story")
                return {"reached": True, "screens": [r["screen"] for r in self.screens]}
            if kind == "condition":
                self._card("condition")
                self._pick(page.get_by_test_id("condition-screen").first, 0)
                self._press(IV_CONTINUE)
            page.wait_for_timeout(500)
        return {"reached": False, "screens": [r["screen"] for r in self.screens], "url": page.url}

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


# ================================================================================ spec 159: the orb interviews
# keel-cloud 267 (contract 84) serves `Interview.interviewer` on every TEXT and AI_INTERVIEWER link, `speaker` ORB or
# AVATAR, the orb's clips Nova audio at `/v2/clips/{id}`, `clips.problem` null where the film is served, the cards'
# `clipId` gone; keel-web 253 plays it (one player, the orb in the face's place, the film first) and 254 retires the
# text player and typing.

#: keel-web 253's player and the files 254 deletes -- read to say which keel-web the walk meets.
ORB_PLAYER_SOURCE = "src/components/interview/ai/AiInterviewPlayer.tsx"
TYPING_SOURCE = "src/lib/aiInterviewFlow.ts"
CARD_VOICE_SOURCE = "src/components/interview/CardVoice.tsx"


def web_has_orb(keel_web: Path) -> bool:
    """keel-web 253 is in the checkout: the AI player renders the orb by `speaker`."""
    source = Path(keel_web) / ORB_PLAYER_SOURCE
    return source.exists() and 'data-speaker={orb ? "ORB" : "AVATAR"}' in source.read_text(encoding="utf-8")


def web_retired_typing(keel_web: Path) -> bool:
    """keel-web 254 is in the checkout: no *Type instead* in the flow and no card voice (FR-1, FR-2)."""
    flow = Path(keel_web) / TYPING_SOURCE
    return flow.exists() and "typeInstead" not in flow.read_text(encoding="utf-8") \
        and not (Path(keel_web) / CARD_VOICE_SOURCE).exists()


def web_pared_down(keel_web: Path) -> bool:
    """keel-web 256 is in the checkout: the film ends on *Begin the interview* (`ai-film-begin`) and the speaker has two
    sizes (`data-size`)."""
    source = Path(keel_web) / ORB_PLAYER_SOURCE
    return source.exists() and 'data-testid="ai-film-begin"' in source.read_text(encoding="utf-8")


#: keel-web 257's story lines (the seven beats, `LONG_BEATS`) and keel-web 258's interview control and flow -- read to say
#: which keel-web the walk meets (spec 161: written to the specs; the stranger's and the founder's sides run once each is
#: merged, and where one is not the leg says so by name).
STORY_LINES_SOURCE = "src/lib/storyLines.ts"
CONTROL_SOURCE = "src/components/interview/Control.tsx"


def web_has_257(keel_web: Path) -> bool:
    """keel-web 257 is in the checkout: the seven beats and the long beats (`LONG_BEATS` in `storyLines.ts`)."""
    source = Path(keel_web) / STORY_LINES_SOURCE
    return source.exists() and "LONG_BEATS" in source.read_text(encoding="utf-8") \
        and STORY_QUESTIONS[7] in source.read_text(encoding="utf-8")


#: keel-web 258 (DRIFT #114, `storyList.ts` `BEFORE_THE_LOCK`): a problem project a solution uses is nested under it,
#: *Defined, not sent*, on `defined`, `calibrating` and `calibrated` (keel-cloud 269 writes the PROBLEM beliefs at the
#: board's yes); `locked` stands on its own.
BEFORE_THE_LOCK = ("defined", "calibrating", "calibrated")


def is_defined(row: dict | None) -> bool:
    """keel-web `storyList.isDefined` (spec 164 mirror 10)."""
    return str(((row or {}).get("definition") or {}).get("status") or "") in BEFORE_THE_LOCK


def parent_of(row: dict | None, rows: list[dict]) -> dict | None:
    """keel-web `storyList.parentOf`: the study a defined project is nested under, where the list holds it -- the one whose
    lineage names it as its problem, or the one it was made to return to."""
    if not is_defined(row):
        return None
    me = (row or {}).get("projectId")
    back = ((row or {}).get("definition") or {}).get("returnTo")
    return next((o for o in rows or [] if o.get("projectId") != me and (
        ((o.get("lineage") or {}).get("problemProjectId") == me) or o.get("projectId") == back)), None)


def web_has_258(keel_web: Path) -> bool:
    """keel-web 258 is in the checkout: Frequency's five rows drawn (`fixed_five` in `Control.tsx`) and the screener's own
    step before the film (`kind: "condition"` in `aiInterviewFlow.ts`'s `stepsOf`)."""
    control = Path(keel_web) / CONTROL_SOURCE
    flow = Path(keel_web) / TYPING_SOURCE
    return control.exists() and '"fixed_five"' in control.read_text(encoding="utf-8") and flow.exists() \
        and "fixed_five" in flow.read_text(encoding="utf-8")


def web_has_260(keel_web: Path) -> bool:
    """keel-web 260 is in the checkout (spec 162 FR-5, FR-6): the stranger's solution link -- `yes_no` drawn
    (`Control.tsx`) and the plate's own step on the link (`kind: "plate"` in `aiInterviewFlow.ts`'s `stepsOf`)."""
    control = Path(keel_web) / CONTROL_SOURCE
    flow = Path(keel_web) / TYPING_SOURCE
    return control.exists() and '"yes_no"' in control.read_text(encoding="utf-8") and flow.exists() \
        and '"plate"' in flow.read_text(encoding="utf-8")


def web_has_259(keel_web: Path) -> bool:
    """keel-web 259 is in the checkout: the founder's solution spoken -- the brand page (`IdeaBrandPage.tsx`)."""
    return (Path(keel_web) / "src/components/idea/IdeaBrandPage.tsx").exists()


# ------------------------------------------------------------------------------------ spec 161: the film's seven scenes

#: keel-cloud 268 FR-5: the film's scenes (the seventh the pain) and its clips (the seven scenes' and the ask line's).
SCENES = 7
CLIPS = 8


def scenes_verdict(story: dict | None, *, cost: str | None = None) -> dict:
    """Spec 161 FR-3 (keel-cloud 268 FR-5): a drawn or served story read for the pain scene -- seven scenes, the seventh
    alone `pain: true`, its line the board's cost (where `cost` is given) and a picture (a library pictogram or a drawn
    one), `costLine` equal to its line, eight clips. `ok` and every part by name."""
    story = story or {}
    scenes = list(story.get("scenes") or [])
    pains = [i for i, sc in enumerate(scenes) if (sc or {}).get("pain") is True]
    seventh = scenes[6] if len(scenes) >= 7 else {}
    line = str(seventh.get("line") or "")
    parts = {
        "seven": len(scenes) == SCENES,
        "the seventh alone is the pain": pains == [6],
        "a picture": bool(seventh.get("pictogramId")),
        "costLine is its line": bool(line) and story.get("costLine") == line,
        "eight clips": len(story.get("clipIds") or []) == CLIPS,
        "the cost said": cost is None or _bare_words(cost) in _bare_words(line),
    }
    return {"ok": all(parts.values()), "parts": parts, "scenes": len(scenes), "pain_at": pains,
            "seventh": {"line": line, "pictogramId": seventh.get("pictogramId")}, "costLine": story.get("costLine"),
            "clips": len(story.get("clipIds") or [])}


def _bare_words(text: str | None) -> str:
    return " ".join(re.findall(r"[a-z0-9']+", str(text or "").lower()))


#: keel-web 257 FR-6 (`scene.ts`): a scene's hold after its clip, and the pain scene's -- twice it.
HOLD_MS = 450
HOLD_PAIN_MS = 2 * HOLD_MS


def held_longer(holds: dict | None) -> bool:
    """Spec 161 FR-3 (keel-web 257 FR-6, `HOLD_PAIN`): the film's pain scene held longer than a scene -- `holds` is the
    page's clock read on the lines, `{"scene": ms (the shortest other scene), "pain": ms}`. Each line's time is its clip,
    its drawing and its hold, and the drawing differs scene to scene, so the pain scene is held to at least `HOLD_PAIN_MS`
    and to the shortest other scene's time plus the hold it adds (`HOLD_PAIN_MS - HOLD_MS`)."""
    holds = holds or {}
    try:
        pain, scene = float(holds.get("pain") or 0), float(holds.get("scene") or 0)
    except (TypeError, ValueError):
        return False
    return pain >= HOLD_PAIN_MS and scene > 0 and pain >= scene + (HOLD_PAIN_MS - HOLD_MS)


def board_rows_verdict(card: dict | None, want: dict[str, str | list | None]) -> dict:
    """Spec 161 FR-1 (keel-web 257 FR-3): the board read by its `data-box` keys -- the rows drawn in `BOARD_ROWS`' order
    (a row the story has no words for may be missing, never out of order), and each wanted row holding its words
    (`want`: key -> the words, or a list whose every item must be on the row). `ok`, the rows, what is missing."""
    rows = card_rows(card)
    order = [k for k in rows]
    in_order = order == [k for k in BOARD_ROWS if k in rows]
    missing = {}
    for key, words in (want or {}).items():
        drawn = _bare_words(rows.get(key))
        need = words if isinstance(words, list) else ([words] if words else [])
        gone = [w for w in need if _bare_words(w) not in drawn]
        if key not in rows or gone:
            missing[key] = gone or ["(no row)"]
    return {"ok": in_order and not missing and (order[-1:] == ["tasks"] if "tasks" in (want or {}) else True),
            "order": order, "missing": missing, "in_order": in_order}


def speech_key(voice: str, text: str) -> str:
    """keel-cloud `KeelVoice.key`: the sha256 hex of the voice, a newline and the words as spoken (whitespace runs as one
    space, the ends stripped) -- the `speech_clip.cache_key` a clip of these words in this voice is stored under."""
    import hashlib                                                            # noqa: PLC0415
    words = re.sub(r"[ \t\n\x0b\f\r]+", " ", str(text or "").strip())
    return hashlib.sha256(f"{voice}\n{words}".encode("utf-8")).hexdigest()


def clip_refs(player: dict | None) -> list[tuple[str, dict]]:
    """Every `ClipRef` an `InterviewerPlayer` serves, named where it sits: `clips.<kind>`, `clips.followUp.<rung>`,
    `items.<itemId>.<clip|more|under|over>`."""
    out: list[tuple[str, dict]] = []
    clips = (player or {}).get("clips") or {}
    for kind, ref in clips.items():
        if kind == "followUp":
            for rung, one in (ref or {}).items():
                if one:
                    out.append((f"clips.followUp.{rung}", one))
        elif isinstance(ref, dict):
            out.append((f"clips.{kind}", ref))
    for item_id, entry in ((player or {}).get("items") or {}).items():
        for part in ("clip", "more", "under", "over"):
            ref = (entry or {}).get(part)
            if isinstance(ref, dict):
                out.append((f"items.{item_id}.{part}", ref))
    return out


def cards_carrying_a_clip(interview: dict) -> list[str]:
    """Spec 159 FR-1 (keel-cloud 267 FR-4, contract 84): every served card that still carries a `clipId` key -- the gate,
    its condition, the link's condition, the problem check, each item, each follow-up. [] on contract 84."""
    out = []
    gate = interview.get("gate") or {}
    if "clipId" in gate:
        out.append("gate")
    if "clipId" in (gate.get("condition") or {}):
        out.append("gate.condition")
    if "clipId" in (interview.get("condition") or {}):
        out.append("condition")
    if "clipId" in (interview.get("problemCheck") or {}):
        out.append("problemCheck")
    for part in interview.get("parts") or []:
        for item in part.get("items") or []:
            if "clipId" in item:
                out.append(f"item {item.get('dimension') or item.get('itemId')}")
    for follow in interview.get("followUps") or []:
        if isinstance(follow, dict) and "clipId" in follow:
            out.append(f"followUp {follow.get('dimension') or follow.get('rung') or '?'}")
    return out


def served_items(interview: dict) -> list[dict]:
    """The link's items in the served order (every part's)."""
    return [i for part in interview.get("parts") or [] for i in part.get("items") or []]


#: Spec 159 FR-1: the stranger's player watched change by change on `window.__ivLog` (158 FR-2's collector, on the AI
#: player): the stage orb's `data-state` (`ai-orb`; `orb_sequence` / `holds_in_order` read it as 158 read the founder's),
#: the stage's phase and speaker, the film or the idea's story on the stage (`ai-story`: its kind, `data-first`, the
#: hand-over line), the question pill and the sheet's question, the intro's speaker, and on every row what must never be
#: drawn on an orb link: a typed box (`textarea`, `input[type=text]`), the text player's voice bar (`card-voice`), the
#: Let-them-choose buttons (`choice-talk`, `choice-write`), the words *Read and tap*; the recorder running (`mic`).
#:
#: Spec 160 (keel-web 256): on both speakers, each row also carries the speaker's size (`size`: `data-size` on `ai-orb`
#: or `ai-facecol`), the ids drawn of `WALK_IDS` (`ids`; the speaker's own box as `speaker`; on the film, the ids inside
#: `ai-story` alone -- it covers the stage), the words drawn and how many are lit (`words`, `lit`: `ai-words`' `data-lit`),
#: the intro's mic state, the film player's state and whether *Begin the interview* is up, and the retired ids
#: (`filmOrb`: `ai-story-orb`; `again`: `ai-again`; `goOn`: `ai-story-go-on`; `fallback`: `ai-mic-fallback`). Every
#: `play()` on a media element is stamped on `window.__ivPlays` (`[t, src, video, data-clip]`: the one player swaps
#: blob sources and names the clip in `data-clip`) -- what played, and when.
WALK_IDS = ("ai-intro", "ai-intro-study", "ai-intro-asks", "ai-intro-chips", "ai-intro-answers", "ai-mic-test",
            "ai-mic-heard", "ai-mic-block", "ai-start", "ai-story", "ai-film-pause", "ai-film-again", "ai-film-board",
            "ai-film-begin", "story-read", "speaker", "ai-words", "ship-mark", "ai-where", "ai-state", "ai-end",
            "ai-sheet", "ai-options", "ai-field", "ai-replay", "ai-back", "ai-skip", "ai-yes", "ai-save", "ai-finish",
            "ai-tap-to-hear", "ai-done", "ai-done-tick", "ai-mic-off", "ai-ended")
ORB_INTERVIEW_WATCH = r"""(() => {
  const log = (window.__ivLog = window.__ivLog || []);
  const plays = (window.__ivPlays = window.__ivPlays || []);
  const IDS = %s;
  if (!window.__ivPlayWrapped && window.HTMLMediaElement) {
    window.__ivPlayWrapped = true;
    const play = HTMLMediaElement.prototype.play;
    HTMLMediaElement.prototype.play = function (...args) {
      try { plays.push([Date.now(), this.currentSrc || this.src || '', this instanceof HTMLVideoElement,
                        this.getAttribute('data-clip')]); } catch (e) {}
      return play.apply(this, args);
    };
  }
  let last = '';
  const t = (el) => (el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : null);
  const read = () => {
    const q = (s) => document.querySelector(s);
    const stage = q('[data-testid=ai-stage]');
    const onStage = !!stage && !stage.hasAttribute('hidden');
    const orb = q('[data-testid=ai-orb]');
    const col = q('[data-testid=ai-facecol]');
    const story = q('[data-testid=ai-story]');
    const intro = q('[data-testid=ai-intro]');
    const words = q('[data-testid=ai-words]');
    const player = story ? story.querySelector('[data-testid=story-player], [data-testid=idea-story-player]') : null;
    const mic = q('[data-testid=ai-mic]');
    const scope = story || document;
    const mark = q('[data-testid=ship-mark]');
    // the stage is drawn hidden under the intro and the last page: what it holds then is not on the screen
    const shown = (el) => !!el && !(stage && !onStage && stage.contains(el));
    const ids = IDS.filter((id) => id === 'speaker' ? onStage && !story && !!(orb || col)
      : shown(scope.querySelector('[data-testid="' + id + '"]')));
    const typed = [...document.querySelectorAll('textarea, input[type=text]')]
      .map((el) => el.getAttribute('data-testid') || el.tagName.toLowerCase());
    const row = {
      state: onStage && orb ? orb.getAttribute('data-state') : null,
      phase: stage ? stage.getAttribute('data-phase') : null, onStage,
      speaker: stage ? stage.getAttribute('data-speaker') : null,
      intro: intro ? intro.getAttribute('data-speaker') : null,
      micState: mic ? mic.getAttribute('data-state') : null,
      film: story ? story.getAttribute('data-kind') : null,
      first: !!(story && story.hasAttribute('data-first')),
      hand: story ? t(story.querySelector('.aiv-story__hand')) : null,
      line: story ? t(story.querySelector('[data-testid=story-line]')) : null,
      filmState: player ? player.getAttribute('data-state') : null,
      begin: !!q('[data-testid=ai-film-begin]'),
      filmOrb: !!q('[data-testid=ai-story-orb]') || (story ? !!story.querySelector('[data-testid=story-orb]') : false),
      size: onStage && !story && (orb || col) ? (orb || col).getAttribute('data-size') : null,
      ids,
      chip: mark ? t(mark) : null,
      chipIn: mark ? (mark.closest('[data-testid=ai-caption]') ? 'caption'
        : mark.closest('[data-testid=ai-facecol]') ? 'facecol' : mark.closest('[data-testid=ai-orb]') ? 'orb' : 'other')
        : null,
      words: words ? t(words) : null,
      lit: words ? words.querySelectorAll('[data-lit=true]').length : 0,
      litFirst: words ? (words.querySelector('[data-lit]') || {getAttribute: () => null}).getAttribute('data-lit') === 'true' : null,
      where: t(q('[data-testid=ai-where]')),
      question: t(q('[data-testid=ai-sheet] .iv-q')),
      typed,
      voiceBar: document.querySelectorAll('[data-testid=card-voice]').length,
      choice: document.querySelectorAll('[data-testid=choice-talk], [data-testid=choice-write]').length,
      readTap: (document.body ? document.body.textContent || '' : '').includes('Read and tap'),
      again: document.querySelectorAll('[data-testid=ai-again]').length,
      goOn: document.querySelectorAll('[data-testid=ai-story-go-on]').length,
      fallback: document.querySelectorAll('[data-testid=ai-mic-fallback]').length,
      video: document.querySelectorAll('video').length,
      mic: !!(window.__listening && window.__listening()),
      path: location.pathname };
    const key = JSON.stringify(row);
    if (key !== last) { last = key; row.t = Date.now(); log.push(row); }
  };
  new MutationObserver(read).observe(document, { subtree: true, childList: true, characterData: true, attributes: true,
                                                 attributeFilter: ['data-state', 'data-phase', 'data-speaker', 'hidden',
                                                                   'data-size', 'data-lit'] });
  read();
})();""" % json.dumps(list(WALK_IDS))


def film_holds(log: list[dict], story: dict | None) -> dict:
    """Spec 161 FR-3 (keel-web 257 FR-6, `HOLD_PAIN`): how long the film held each line, read off the watched rows'
    `story-line` changes (the page's clock, ms): the pain scene's line (`costLine`, the seventh) and the scene before it
    -- the last run of the film (a start over draws it again). `{"scene": ms, "pain": ms}`; None where unseen."""
    scenes = list((story or {}).get("scenes") or [])
    pain = next((sc.get("line") for sc in scenes if sc.get("pain")), (story or {}).get("costLine"))
    others = {_bare_words(sc.get("line")) for sc in scenes if not sc.get("pain") and sc.get("line")}
    changes: list[tuple[float, str]] = []
    for row in log:
        if row.get("film") != "problem" or row.get("t") is None:
            continue
        line = row.get("line") or ""
        if not changes or changes[-1][1] != line:
            changes.append((float(row["t"]), line))
    holds: dict = {"scene": None, "pain": None, "scenes": []}
    for i, (t, line) in enumerate(changes):
        end = changes[i + 1][0] if i + 1 < len(changes) else None
        if end is None:
            continue
        if pain and _bare_words(line) == _bare_words(pain):
            holds["pain"] = end - t
        elif _bare_words(line) in others:
            holds["scenes"].append(end - t)
    # the last run of the film counts (a start over draws it again): its scenes are the last of each line's reads
    holds["scene"] = min(holds["scenes"][-len(others):]) if holds["scenes"] else None
    return holds


def iv_log(page) -> list[dict]:
    """`ORB_INTERVIEW_WATCH`'s rows so far ([] where the page has gone)."""
    try:
        return list(page.evaluate("() => (window.__ivLog || []).slice()") or [])
    except Exception:  # noqa: BLE001 - a page that has gone
        return []


def iv_plays(page) -> list[list]:
    """Spec 160: every media `play()` stamped by `ORB_INTERVIEW_WATCH` so far -- `[t (ms since the epoch), src, video,
    data-clip]`."""
    try:
        return list(page.evaluate("() => (window.__ivPlays || []).slice()") or [])
    except Exception:  # noqa: BLE001 - a page that has gone
        return []


def stage_sequence(log: list[dict]) -> list[str]:
    """What the stage did, in order, repeats folded: `film:<kind>` while a film or the idea's story stands, else the
    stage's phase (speaking, listening, held, ...) once on the stage -- so *the film first, then the opening* reads
    `film:problem, speaking, ...`."""
    out: list[str] = []
    for row in log:
        if not row.get("onStage"):
            continue
        what = f"film:{row['film']}" if row.get("film") else row.get("phase")
        if what and (not out or out[-1] != what):
            out.append(what)
    return out


def orb_answer_runs(log: list[dict]) -> list[list[str]]:
    """The stage orb's states cut at each `speaking` -- one run a clip and the answer after it -- so an answer's
    *speaking -> listening -> hearing -> writing* is one run (158 FR-2's states, on the stranger's orb)."""
    runs: list[list[str]] = []
    for state in orb_sequence([r for r in log if r.get("state")]):
        if state == "speaking" or not runs:
            runs.append([state])
        else:
            runs[-1].append(state)
    return runs


def never_drawn(log: list[dict]) -> dict:
    """Spec 159 FR-1 / FR-3: what an orb link must never draw, met anywhere in the log -- typed boxes (with the
    question they stood on), the voice bar, the choice buttons, *Read and tap*, a `<video>`."""
    typed = [{"typed": r["typed"], "where": r.get("where"), "question": r.get("question"), "phase": r.get("phase")}
             for r in log if r.get("typed")]
    return {"typed": list({json.dumps(x, sort_keys=True): x for x in typed}.values())[:8],
            "voice_bar": any(r.get("voiceBar") for r in log), "choice": any(r.get("choice") for r in log),
            "read_and_tap": any(r.get("readTap") for r in log),
            "video": any(r.get("video") for r in log if r.get("speaker") == "ORB")}


# ================================================================================ spec 160: both speakers, one walk
# keel-web 256 pared the player down on both speakers alike; the founder's rule (2026-11-23): "test for both the
# interviewers and ensure that it is in sync". A link's walk is folded into steps (`walk_steps`) and the orb's and the
# face's are compared step for step (`same_walk`).

#: The stage's own moments that are not a step of the walk: the flow's loading and sending (a fetch's length, never the
#: same twice), the film's phase where no film is drawn (the frame between the film's end and the opening), and the
#: frame in which the stage is shown on the Start tap before the flow has left `intro` (run 1: `intro:`).
TRANSIENT_PHASES = ("loading", "sending", "story", "intro", None, "")
#: The speaker-specific ids are never in `WALK_IDS` (`intro-orb`, `ai-face`, `ai-caption`, `ai-face-state`,
#: `ai-orb-state`); the speaker's own box is `speaker` on both.


def step_of(row: dict) -> str | None:
    """The step a watched row stands in: `intro` (`+start` once *Start the interview* is up, `+block` at the block), the
    film (`film:<kind>`, `+begin` once *Begin the interview* is up), the stage's `<phase>:<where>` (speaking, beat,
    listening, held, confirming), `done` / `ended`; None for a transient moment."""
    ids = set(row.get("ids") or [])
    if row.get("onStage"):
        if row.get("film"):
            return f"film:{row['film']}" + ("+begin" if row.get("begin") else "")
        phase = row.get("phase")
        if phase in TRANSIENT_PHASES:
            return None
        if phase in ("done", "ended"):
            return phase
        return f"{phase}:{row.get('where') or ''}"
    if "ai-done" in ids:
        return "done"
    if "ai-ended" in ids:
        return "ended"
    if row.get("intro") or "ai-intro" in ids:
        return "intro" + ("+start" if "ai-start" in ids else "") + ("+block" if "ai-mic-block" in ids else "")
    return None


def walk_steps(log: list[dict]) -> list[dict]:
    """Spec 160 FR-3: the walk as its steps, repeats folded -- per step the state word (`step`), the speaker's sizes
    seen (`sizes`: `large` while it asks, `small` once the sheet opens), the ids drawn in it (`ids`, the union of its
    rows: a frame drawn a moment late is still the step's), the words drawn while it speaks (`words`) and how they lit
    (`lit_first`: the first word lit, `lit_max`: the most lit at once)."""
    steps: list[dict] = []
    for row in log:
        name = step_of(row)
        if name is None:
            continue
        if not steps or steps[-1]["step"] != name:
            steps.append({"step": name, "sizes": [], "ids": [], "words": None, "lit_first": False, "lit_max": 0,
                          "rows": 0})
        cur = steps[-1]
        cur["rows"] += 1
        size = row.get("size")
        if size and size not in cur["sizes"]:
            cur["sizes"].append(size)
        for i in row.get("ids") or []:
            if i not in cur["ids"]:
                cur["ids"].append(i)
        if row.get("words"):
            cur["words"] = row["words"]
            cur["lit_first"] = cur["lit_first"] or bool(row.get("litFirst"))
            cur["lit_max"] = max(cur["lit_max"], int(row.get("lit") or 0))
    for cur in steps:
        cur["ids"] = sorted(cur["ids"])
    return steps


def step_record(step: dict) -> dict:
    """What `same_walk` compares of a step: the state word, the sizes, the ids, the words and that they lit from the
    first (the count lit at the clip's end is a timer's race against a clip of 0.312 s on the orb and 1 s on the face --
    reported, not compared)."""
    return {"step": step.get("step"), "sizes": list(step.get("sizes") or []), "ids": list(step.get("ids") or []),
            "words": step.get("words"), "lit": bool(step.get("lit_first")) if step.get("words") else None}


def same_walk(orb: list[dict], face: list[dict]) -> dict:
    """Spec 160 FR-3: the orb's walk and the face's, step for step -- equal (`same`), or the first step they part at
    (`at`, its index, both records and what differs: `differs`)."""
    for i in range(max(len(orb), len(face))):
        a = step_record(orb[i]) if i < len(orb) else None
        b = step_record(face[i]) if i < len(face) else None
        if a != b:
            differs = (["missing on the face"] if b is None else ["missing on the orb"] if a is None
                       else [k for k in a if a[k] != b[k]])
            return {"same": False, "at": i, "orb": a, "face": b, "differs": differs,
                    "orb_steps": len(orb), "face_steps": len(face)}
    return {"same": True, "at": None, "steps": len(orb)}


def sizes_line(steps: list[dict]) -> str:
    """The sizes as the walk went: one letter a stage step (L large, S small), `-` where no speaker is drawn."""
    out = []
    for s in steps:
        sizes = s.get("sizes") or []
        out.append("/".join("L" if z == "large" else "S" if z == "small" else z for z in sizes) or "-")
    return " ".join(out)
