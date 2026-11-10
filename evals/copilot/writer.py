"""Spec 151 FR-3: the script writer -- a model writes each script to the fixed form, the catalogue checks it offline.

`claude-sonnet-5-5` through the Anthropic key (the writer's quality matters; its cost is cents), one call a script, the
plan entry's kinds named in the prompt, the questionnaire's items and spoken forms given, the system prompt
`instructions/script-writer.md`. The reply is read past any thinking block (`evals.noise.pipeline.answer_text`), parsed,
and validated against the catalogue's rules (`catalogue.validate`); a script that fails is rewritten once with its
faults named (the first reply kept in the conversation, unchanged), then dropped and counted.

`FakeWriter` (`DRY=1`, the tests) writes the same plan entries from the catalogue's own templates with no call; its
scripts pass the same validation, which is what proves the rules and the plan agree.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from evals.copilot import catalogue as cat
from evals.noise.pipeline import answer_text, parse

HERE = Path(__file__).resolve().parent
INSTRUCTION = HERE / "instructions" / "script-writer.md"
WRITER_MODEL = "claude-sonnet-5-5"
#: Long rounds write long scripts (a 60-minute call is hundreds of turns).
MAX_TOKENS = {1: 8_000, 2: 16_000, 3: 64_000, 4: 128_000}
THINKING = {"type": "adaptive"}
#: Sonnet 5.5's list prices, $ a million tokens in and out (Anthropic's list; thinking billed as output).
SONNET_USD_IN, SONNET_USD_OUT = 2.0, 10.0


def system_prompt() -> str:
    return INSTRUCTION.read_text(encoding="utf-8").strip()


def _item_block(item: dict) -> str:
    sp = item.get("spoken") or {}
    lines = [f"- {item['id']} ({item['kind']}{', pick ' + str(item['pick']) if item.get('pick') else ''}"
             f"{', unit ' + str(item['unit']) if item.get('unit') else ''}): {item['question']}"]
    if sp.get("anchor"):
        lines.append(f"    spoken anchor: {sp['anchor']}")
    lines.append(f"    spoken stem: {sp.get('stem') or item['question']}")
    for key in ("countLine", "optionsLine", "escapeLine", "under", "over"):
        if sp.get(key):
            lines.append(f"    spoken {key}: {sp[key]}")
    for n, o in enumerate(item.get("options") or [], 1):
        lines.append(f"    option {n}: {o}")
    if item.get("escape"):
        lines.append(f"    escape: {item['escape']}")
    return "\n".join(lines)


def user_prompt(entry: dict, q: dict, name: str) -> str:
    items = {it["id"]: it for it in q["items"]}
    lines = [f"id: {entry['id']}", f"round: {entry['round']}", f"questionnaire: {name}",
             f"length: the last turn starts between {entry['seconds'][0]} and {entry['seconds'][1]} seconds", "",
             "The idea the respondent was shown:"]
    for link in q.get("links", {}).values():
        idea = link.get("idea") or {}
        lines.append(f"  {idea.get('what') or ''} {idea.get('how') or ''}".rstrip())
    lines += ["", "The questionnaire's items (every one, in Keel's order):"]
    lines += [_item_block(it) for it in q["items"]]
    lines += ["", "This script:", f"- the founder asks, in this order: {', '.join(entry['items'])}"]
    for iid in entry["items"]:
        f, r = entry["founder"].get(iid), entry["respondent"].get(iid)
        lines.append(f"- {iid}: founder habit {f} ({cat.KINDS[f].describe}); respondent behaviour {r} "
                     f"({cat.KINDS[r].describe}); follow-ups after the answer: {entry['follow_ups'].get(iid, 0)}")
        if entry["also"].get(iid):
            lines.append(f"  (stacked with {entry['also'][iid]} in the same breath)")
    for k in entry.get("extras") or []:
        lines.append(f"- also on this call: {k} ({cat.KINDS[k].describe})")
    if entry.get("silence"):
        lines.append(f"- a silence of {entry['silence']} seconds with no one speaking (the box pauses: state_after "
                     f"paused on the turn before it)")
    if entry.get("long_item"):
        lines.append(f"- {entry['long_item']}'s follow-ups run about ten minutes")
    if entry.get("never_reached"):
        lines.append(f"- never asked: {', '.join(entry['never_reached'])} (the call ends first)")
    lines.append(f"- every one of these kinds appears on at least one turn, with kind set: {', '.join(entry['kinds'])}")
    for it in (items[i] for i in entry["items"]):
        if it["kind"] == "free":
            lines.append(f"- {it['id']} is free text: its answer's option is null")
    return "\n".join(lines)


def request_body(entry: dict, q: dict, name: str, *, system: str | None = None, messages: list | None = None) -> dict:
    """The Messages request: the writer's pin, adaptive thinking, the round's cap; no temperature (Sonnet 5.5 refuses
    a non-default one), no prefill."""
    return {"model": WRITER_MODEL, "max_tokens": MAX_TOKENS[entry["round"]], "system": system or system_prompt(),
            "messages": messages or [{"role": "user", "content": user_prompt(entry, q, name)}],
            "thinking": dict(THINKING)}


def cost(usage: dict) -> float:
    return round((usage.get("input_tokens", 0) * SONNET_USD_IN + usage.get("output_tokens", 0) * SONNET_USD_OUT) / 1e6,
                 6)


class ModelWriter:
    """One call a script, rewritten once on a fault, through `clients.messages(body) -> (reply json, ms)`."""

    def __init__(self, clients, q: dict, name: str):
        self.clients, self.q, self.name, self.system = clients, q, name, system_prompt()

    def write(self, entry: dict) -> dict:
        body = request_body(entry, self.q, self.name, system=self.system)
        usage = {"input_tokens": 0, "output_tokens": 0}
        faults, script, tries = [], None, 0
        started = time.time()
        for attempt in range(2):
            tries += 1
            reply, _ms = self.clients.messages(body)
            u = (reply or {}).get("usage") or {}
            usage["input_tokens"] += int(u.get("input_tokens") or 0)
            usage["output_tokens"] += int(u.get("output_tokens") or 0)
            script = parse(answer_text(reply or {}))
            faults = ["the reply is not one JSON object"] if script is None else cat.validate(
                script, self.q, kinds=entry["kinds"])
            if not faults:
                break
            if attempt == 0:
                body = dict(body, messages=body["messages"] + [
                    {"role": "assistant", "content": (reply or {}).get("content") or [{"type": "text", "text": ""}]},
                    {"role": "user", "content": "The script fails these checks; write it again, whole, with every "
                                                "one fixed:\n- " + "\n- ".join(faults[:40])}])
        return finish(entry, script, faults, tries, usage, time.time() - started)


def finish(entry: dict, script: dict | None, faults: list, tries: int, usage: dict, seconds: float) -> dict:
    record = {"id": entry["id"], "kept": not faults, "tries": tries, "faults": faults, "usage": usage,
              "cost_usd": cost(usage), "seconds": round(seconds, 2)}
    if not faults:
        script = dict(script, id=entry["id"], round=entry["round"], plan=entry)
        record["script"] = script
    return record


# ---------------------------------------------------------------------------------------- the fake writer

LATE_ASK_S = 1850
FOLLOW_UPS = ["Why is that, would you say?", "And who else deals with that, usually?",
              "How did that go, the last time?", "What happens when it doesn't work out?",
              "Is that the same for everyone you work with?"]
REPLIES = ["Mostly because it takes time, I'd say.", "A couple of the others, now and then.",
           "It went fine in the end, it just took longer.", "Then it waits until someone has a minute.",
           "Pretty much, yeah, give or take."]


def _decap(s: str) -> str:
    return s[:1].lower() + s[1:] if s else s


def _bare(s: str) -> str:
    return s.rstrip(" ?.")


class _Composer:
    """Builds one script's turns, the clock running as it goes."""

    def __init__(self, entry: dict, items: dict):
        self.entry, self.items, self.turns, self.t = entry, items, [], 1.0
        self.state = "listening"

    def say(self, who, text, *, kind=None, q=None, verdict=None, option=None, tier=None, state=None, gap=0.6,
            words_per_s=2.6):
        state = state or self.state
        self.turns.append({"t": round(self.t, 1), "who": who, "text": text, "silence_after": gap, "kind": kind,
                           "truth": {"q": q, "verdict": verdict, "option": option, "tier": tier,
                                     "state_after": state}})
        self.state = state
        self.t += len(text.split()) / words_per_s + gap

    # the founder asking
    def ask(self, item, habit):
        stem = (item.get("spoken") or {}).get("stem") or item["question"]
        anchor = (item.get("spoken") or {}).get("anchor")
        opts = item.get("options") or []
        q = item["id"]
        verdict = cat.FOUNDER[habit].verdict
        if habit == "verbatim":
            text = f"{anchor} {stem}" if anchor else stem
        elif habit in ("light_reword", "went_back"):
            text = ("Going back to one from before: " if habit == "went_back" else "So, ") + _decap(_bare(stem)) + \
                   ", roughly?"
        elif habit == "options_own_words":
            text = "Let me put this one my own way. Would you say the low end, somewhere in the middle, or the top " \
                   "end of what I'd list?"
        elif habit == "options_reordered_or_missing":
            shown = list(reversed(opts))[:-1] if len(opts) > 1 else opts
            text = f"{stem} Is it {', or '.join(shown)}?" if shown else stem
        elif habit == "story_prompt":
            text = "Walk me through the last time that came up for you."
        elif habit == "meaning_changed":
            text = "In general, is this something you ever think about?"
        elif habit == "preface":
            text = f"Okay so, the next thing I wanted to get into, and this is really the heart of it, is this. {stem}"
        elif habit == "stacked":
            other = self.items[self.entry["also"][q]]
            text = f"{_bare(stem)}, and {_decap((other.get('spoken') or {}).get('stem') or other['question'])}"
        elif habit == "leading":
            text = f"I'd guess you'd say the obvious one here, right? {stem}"
        elif habit == "restart":
            words = stem.split()
            text = f"{' '.join(words[:3])}... sorry, {stem}"
        else:
            raise ValueError(habit)
        self.say("founder", text, kind=habit, q=q, verdict=verdict, state="listening")

    def answer_option(self, item):
        if item["kind"] == "number":
            return {"value": 3}, "About three, I'd say."
        if item["kind"] == "free":
            return None, "It was last week, and it took most of the afternoon to sort out."
        opts = item["options"]
        if item["kind"] == "multi":
            return {"picks": [1, 2]}, f"{opts[0]}, and {_decap(opts[1])}."
        return {"picks": [1]}, f"{opts[0]}."

    def respond(self, item, beh, habit):
        q = item["id"]
        option, plain = self.answer_option(item)
        tier = cat.expected_tier(habit, beh) if beh in cat.RESPONDENT else "sure"
        if beh == "straight":
            self.say("them", plain, kind=beh, q=q, option=option, tier=tier, state="answered")
        elif beh == "story_first":
            text = ("So the last time this came up it was a busy week, two things went wrong on the same day, and I "
                    "had to sort it out before anyone else got in. Anyway, " + _decap(plain))
            self.say("them", text, kind=beh, q=q, option=option, tier=tier, state="answered")
        elif beh == "hedged":
            self.say("them", f"Mostly {_decap(_bare(plain))}, I'd say. Not always.", kind=beh, q=q, option=option,
                     tier=tier, state="answered")
        elif beh == "late_negation":
            if item["kind"] == "number":
                text, option = "About ten I'd have said, no, actually, more like three.", {"value": 3}
            elif item["kind"] == "multi":
                text = f"{item['options'][2]}, and... no, actually, {_decap(_bare(plain))}."
            else:
                text = f"{item['options'][-1]}, I think... no, actually, {_decap(plain)}"
            self.say("them", text, kind=beh, q=q, option=option, tier=tier, state="answered")
        elif beh == "number_for_yes_no":
            self.say("them", "Four times, maybe five.", kind=beh, q=q, option={"picks": [1]}, tier=tier,
                     state="answered")
        elif beh == "different_question":
            self.say("them", "Honestly the bigger problem is the tools we use, they are terrible.", kind=beh, q=q,
                     option={"unclear": True}, tier="unsure", state="listening")
            self.ask(item, "verbatim")
            self.say("them", plain, q=q, option=option, tier="sure", state="answered")
        elif beh == "counter_question":
            self.say("them", "Sorry, what do you mean by that?", kind=beh, q=q, verdict="nothing", state="listening")
            self.say("founder", "I mean the one I just asked, for you yourself, the way it usually goes.",
                     kind="clarifying", q=q, verdict="same_meaning", state="listening")
            self.say("them", plain, q=q, option=option, tier=cat.expected_tier(habit, "straight"), state="answered")
        elif beh == "interrupted":
            self.say("them", "Well, I think it's mostly the--", kind=beh, q=q, option={"unclear": True},
                     tier="unsure", state="listening", gap=0)
            self.say("founder", "Sorry, go on.", kind=None, verdict="back_channel", state="listening")
            self.say("them", plain, q=q, option=option, tier=cat.expected_tier(habit, "straight"), state="answered")
        elif beh == "two_voices":
            self.say("them", "(someone beside them) Tell them about last week.", kind=beh, q=q, verdict="nothing",
                     state="listening", gap=0.4)
            self.say("them", plain, q=q, option=option, tier=cat.expected_tier(habit, "straight"), state="answered")
        else:
            raise ValueError(beh)

    def follow_ups(self, item, n):
        for j in range(n):
            self.say("founder", FOLLOW_UPS[j % len(FOLLOW_UPS)],
                     kind="follow_ups_in_a_row" if n >= 2 and j == 1 else ("follow_up" if j == 0 else None),
                     q=item["id"], verdict="follow_up", state="follow_up")
            self.say("them", REPLIES[j % len(REPLIES)], q=item["id"], verdict="follow_up", state="follow_up")


def compose(entry: dict, q: dict) -> dict:
    """A plan entry written from the catalogue's templates: the fake writer's script."""
    items = {it["id"]: it for it in q["items"]}
    c = _Composer(entry, items)
    extras = set(entry.get("extras") or [])
    if "own_note" in extras:
        c.say("founder", "Before we start, how many sites does your team run at once?",
              kind="own_note", verdict="own_note", state="note")
    asked = []
    for n, iid in enumerate(entry["items"]):
        item = items[iid]
        habit = entry["founder"][iid]
        if entry["round"] == 4 and asked and n == len(entry["items"]) - 1:
            while c.t < LATE_ASK_S:                                    # R4: the last question asked late in the call
                c.follow_ups(items[asked[-1]], 2)
        c.ask(item, habit)
        asked.append(iid)
        c.respond(item, entry["respondent"][iid], habit)
        if "answered_for_them" in extras and n == 0:
            c.say("founder", "So that's your answer then, basically.", kind="answered_for_them", q=iid,
                  verdict="nothing", state="answered")
        if "back_channel" in extras and n == 0:
            c.say("founder", "Right. Okay, yeah.", kind="back_channel", verdict="back_channel", state="answered")
        fups = entry["follow_ups"].get(iid, 0)
        if fups:
            c.follow_ups(item, fups)
            if entry.get("long_item") == iid:
                while c.t < 600 + (c.turns[0]["t"] if c.turns else 0):
                    c.follow_ups(item, 2)
        if entry.get("silence") and n == len(entry["items"]) // 2:
            c.say("founder", "Let me just check something on my side, one moment.", verdict="back_channel",
                  state="paused", gap=float(entry["silence"]))
        if "went_back" in extras and n == 1 and len(asked) >= 2:
            back = items[asked[0]]
            c.say("founder", "Going back to one from before: " + _decap(_bare((back.get("spoken") or {}).get("stem")
                                                                           or back["question"])) + ", roughly?",
                  kind="went_back", q=back["id"], verdict="same_meaning", state="listening")
            opt, plain = c.answer_option(back)
            c.say("them", "Same as before, " + _decap(plain), q=back["id"], option=opt, tier="sure", state="answered")
    low = entry["seconds"][0]
    while c.turns and c.turns[-1]["t"] < low:                                   # a long call runs to its round's length
        item = items[asked[-1]]
        c.follow_ups(item, 2)
    c.turns[-1]["truth"]["state_after"] = "done" if entry["round"] >= 3 else c.turns[-1]["truth"]["state_after"]
    return {"id": entry["id"], "round": entry["round"], "questionnaire": q.get("name") or Path(q.get("path") or
                                                                                               "questionnaire").stem,
            "turns": c.turns}


class FakeWriter:
    """No call: the plan entry composed from the catalogue's templates, validated as a model's script is."""

    def __init__(self, q: dict, name: str | None = None):
        self.q, self.name = q, name

    def write(self, entry: dict) -> dict:
        script = compose(entry, self.q)
        faults = cat.validate(script, self.q, kinds=entry["kinds"])
        return finish(entry, script, faults, 1, {"input_tokens": 0, "output_tokens": 0}, 0.0)


def sample_markdown(scripts: list[dict], n: int = 20) -> str:
    """Twenty scripts as the founder's reviewer reads them: each turn's words beside its truth."""
    w = [f"# Scripts to read before any audio ({min(n, len(scripts))} of {len(scripts)})", "",
         "Each turn: the clock, who, the words, then the truth the bench scores against (question, verdict, option, "
         "tier, box after). Throw out any script whose truth misstates its words.", ""]
    for s in scripts[:n]:
        plan = s.get("plan") or {}
        w += [f"## {s['id']} -- round {s['round']}", "",
              f"Kinds: {', '.join(plan.get('kinds') or [])}. Items: {', '.join(plan.get('items') or [])}.", "",
              "| t | who | words | kind | q | verdict | option | tier | box after |",
              "|---|---|---|---|---|---|---|---|---|"]
        for t in s["turns"]:
            tr = t["truth"]
            words = t["text"].replace("|", "/")
            w.append(f"| {t['t']:.1f} | {t['who']} | {words} | {t.get('kind') or ''} | {tr.get('q') or ''} | "
                     f"{tr.get('verdict') or ''} | {json.dumps(tr.get('option')) if tr.get('option') else ''} | "
                     f"{tr.get('tier') or ''} | {tr.get('state_after')} |")
        w.append("")
    return "\n".join(w) + "\n"
