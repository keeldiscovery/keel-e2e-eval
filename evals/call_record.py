"""Spec 154 FR-4 (keel-cloud 249): **the fake call record** -- two short 16 kHz mono 16-bit WAVs and a key log in the
card's shape (keel-web 188's `KeyLog.toJson`, keel-cloud 249's `KeyLog.parse`), built off the call's served script
(`GET calls/{id}/script`) and uploaded as the three multipart parts `founder` / `them` / `keys` to `POST
calls/{id}/record`.

The key log (`fixtures/calls/keys.template.json`, the times fixed; the item ids and the options filled from the script):
the gate's Yes and its STORY stretch, six items filed (one undone and filed again), the FOLLOW_UP stretch after the one
filing the script's `followUp.against` names, the pilot's Yes, then the OWN_QUESTIONS and THEIR_QUESTIONS stretches, End.

The tracks (`write_wav`): silence (zero bytes) with, on the founder's, a short tone at every filing's second (a marker a
player can hear), and -- the stack's fake transcriber (keel-cloud 136 FR-2: audio that is text is heard as that text,
trailing zeros trimmed, at most 4 KiB) -- **words written as bytes at the start of each window the digest cuts**: the
story sentence from the STORY stretch's start, the follow-up's from its, each voice's note from the two closing
stretches', and, on item 1's pick-check window (from the STORY stretch's end to item 1's filing), option 3's served
label -- so the fake classifier names option 3 where option 1 was filed and `heard` is exercised. Every other window
holds silence, heard as the stack's `otherwise` word. Nothing here asserts; `evals/calls_leg.py` judges.
"""

from __future__ import annotations

import json
import math
import struct
from pathlib import Path

from stack.config import REPO_ROOT

FIXTURES = REPO_ROOT / "fixtures" / "calls"
TEMPLATE = FIXTURES / "keys.template.json"
RATE = 16_000
BYTES_PER_SECOND = RATE * 2
STORY = "Last spring we waited six weeks for one approved invoice to be paid, and nobody could say why."
FOLLOW_UP = "Mostly it was the chasing, every week, that wore us down."
OWN_FOUNDER = "Would you want to see the numbers yourself each week, or just a note when something is off?"
OWN_THEM = "A note when something is off would be enough for me."
THEIR_FOUNDER = "Anything you want to ask me about the idea before we finish?"
THEIR_THEM = "Only whether it would work with the till we already have."
#: The record's times, in seconds from the recording's start (the template's).
TIMES = {"gate": 2.0, "story_to": 6.0, "items": [9.0, 12.0, 15.0, 18.0, 21.0, 24.0], "undo": 19.0, "refile": 20.0,
         "follow_up_to": 3.0, "pilot": 27.0, "own": (28.0, 32.0), "theirs": (33.0, 37.0), "end": 38.0}
DURATION_S = 39


def passages_of(script: dict) -> dict:
    """The script's passages by kind: the gate, the items (in order), the pilot."""
    out: dict = {"items": []}
    for passage in script.get("passages") or []:
        kind = passage.get("kind")
        if kind == "gate":
            out["gate"] = passage
        elif kind == "item":
            out["items"].append(passage)
        elif kind == "pilot":
            out["pilot"] = passage
    return out


def _first_option(item: dict, *, prefer_against: bool = False) -> dict | None:
    options = [o for o in item.get("options") or [] if o.get("optionId")]
    if not options and item.get("twoSteps"):
        # keel-cloud 248 FR-6: a two-step ladder's first step is bands with no id (`step` under / over) -- the band
        # opens its second step, whose options carry the served ids; the filing is the second step's option
        band = next((o for o in item.get("options") or [] if o.get("step")), None)
        second = ((item.get("twoSteps") or {}).get(band.get("step")) if band else None) or {}
        options = [o for o in second.get("options") or [] if o.get("optionId")]
    if prefer_against:
        against = set((item.get("followUp") or {}).get("against") or [])
        for option in options:
            if option["optionId"] in against:
                return option
    return options[0] if options else None


def build_key_log(script: dict, client_id: str = "c-eval-154") -> dict:
    """The key log off the served script (the template's times): the gate's Yes (the first option) and the STORY
    stretch; six items filed -- option 1 of each choice item (option 3 is what the fake hears on item 1), a typed 3 on a
    number item, the item whose `against` the filed option sits in followed by the FOLLOW_UP stretch (the first such
    item after item 1; none: no follow-up); the third filing undone at `undo` and filed again at `refile`; the pilot's
    first option; the two closing stretches; End. Returns the log and `plan`: what was filed, per item, for the leg."""
    parts = passages_of(script)
    # six items the card can file: a number, or a choice with an option that carries an id (a ladder's by its second
    # step) -- an item the card cannot file is passed over and named in the plan
    fileable = [i for i in parts["items"] if i.get("control") == "number" or _first_option(i) is not None]
    gate, items, pilot = parts.get("gate"), fileable[:6], parts.get("pilot")
    if gate is None or len(items) < 6:
        raise ValueError(f"the script has no gate or fewer than six items ({len(items)}): the fake record needs six")
    filings: list[dict] = []
    stretches: list[dict] = []
    plan: dict = {"items": [], "follow_up_item": None, "heard_item": items[0]["itemId"],
                  "passed_over": [{"itemId": i.get("itemId"), "control": i.get("control"),
                                   "options": [{k: o.get(k) for k in ("optionId", "step")} for o in i.get("options") or []]}
                                  for i in parts["items"] if i not in fileable]}
    yes = _first_option(gate)
    filings.append({"at": TIMES["gate"], "itemId": gate["itemId"], "option": yes["optionId"]})
    stretches.append({"kind": "STORY", "from": TIMES["gate"], "to": TIMES["story_to"], "itemId": gate["itemId"]})
    follow_up_done = False
    undos: list[dict] = []
    for n, (item, at) in enumerate(zip(items, TIMES["items"])):
        control = item.get("control")
        want_against = n > 0 and not follow_up_done and bool((item.get("followUp") or {}).get("against"))
        if control == "number":
            filing = {"at": at, "itemId": item["itemId"], "value": 3}
            label = f"3 {item.get('unit') or ''}".strip()
            option = None
        else:
            option = _first_option(item, prefer_against=want_against)
            if option is None:
                raise ValueError(f"item {item.get('itemId')} offers no option with an id")
            filing = {"at": at, "itemId": item["itemId"], "option": option["optionId"]}
            label = option.get("label")
        filings.append(filing)
        if n == 2:
            # the third filing undone and filed again (the record keeps the later one)
            undos.append({"at": TIMES["undo"], "itemId": item["itemId"]})
            filings.append({**filing, "at": TIMES["refile"]})
        plan["items"].append({"itemId": item["itemId"], "filed": option["optionId"] if option else None, "label": label,
                              "control": control, "options": [o.get("label") for o in item.get("options") or []]})
        if want_against and option is not None and option["optionId"] in set((item.get("followUp") or {}).get("against") or []):
            stretches.append({"kind": "FOLLOW_UP", "from": at, "to": at + TIMES["follow_up_to"], "itemId": item["itemId"]})
            plan["follow_up_item"] = item["itemId"]
            follow_up_done = True
    if pilot is not None:
        option = _first_option(pilot)
        filings.append({"at": TIMES["pilot"], "itemId": pilot.get("itemId") or "pilot", "option": option["optionId"]})
    stretches.append({"kind": "OWN_QUESTIONS", "from": TIMES["own"][0], "to": TIMES["own"][1]})
    stretches.append({"kind": "THEIR_QUESTIONS", "from": TIMES["theirs"][0], "to": TIMES["theirs"][1]})
    log = {"clientId": client_id, "scriptRevision": str(script.get("revision") or ""), "start": 0,
           "end": TIMES["end"], "filings": filings, "undos": undos, "stretches": stretches}
    plan["heard_option_label"] = (items[0].get("options") or [{}, {}, {}])[2].get("label") if len(items[0].get("options") or []) >= 3 else None
    return {"log": log, "plan": plan}


def wav_bytes(data: bytearray) -> bytes:
    """A canonical 44-byte PCM header (16 kHz, mono, 16-bit) over `data`."""
    header = b"RIFF" + struct.pack("<I", 36 + len(data)) + b"WAVE" + b"fmt " + struct.pack("<IHHIIHH", 16, 1, 1, RATE, BYTES_PER_SECOND, 2, 16) \
        + b"data" + struct.pack("<I", len(data))
    return header + bytes(data)


def _write_text(data: bytearray, at_s: float, text: str) -> None:
    """The words as UTF-8 bytes at the window's first byte (the fake transcriber trims the zeros after them)."""
    start = int(at_s * BYTES_PER_SECOND)
    raw = text.encode("utf-8")
    data[start:start + len(raw)] = raw


def _write_tone(data: bytearray, at_s: float, seconds: float = 0.1, hz: float = 1000.0) -> None:
    start = int(at_s * BYTES_PER_SECOND) // 2
    for n in range(int(seconds * RATE)):
        sample = int(8000 * math.sin(2 * math.pi * hz * n / RATE))
        data[(start + n) * 2:(start + n) * 2 + 2] = struct.pack("<h", sample)


def tracks(log: dict, plan: dict, *, otherwise_item_words: bool = True) -> dict[str, bytes]:
    """The two tracks for `log`: the founder's -- silence, a tone at every filing, the founder's voice at the two closing
    stretches; the person's -- the story at the STORY stretch, the follow-up at the FOLLOW_UP stretch, their voice at the
    closing stretches, and option 3's label at item 1's pick-check window (the STORY stretch's end to item 1's filing)."""
    size = DURATION_S * BYTES_PER_SECOND
    founder = bytearray(size)
    them = bytearray(size)
    for filing in log["filings"]:
        _write_tone(founder, filing["at"])
    by_kind = {s["kind"]: s for s in log["stretches"]}
    _write_text(them, by_kind["STORY"]["from"], STORY)
    if "FOLLOW_UP" in by_kind:
        _write_text(them, by_kind["FOLLOW_UP"]["from"], FOLLOW_UP)
    _write_text(founder, by_kind["OWN_QUESTIONS"]["from"], OWN_FOUNDER)
    _write_text(them, by_kind["OWN_QUESTIONS"]["from"], OWN_THEM)
    _write_text(founder, by_kind["THEIR_QUESTIONS"]["from"], THEIR_FOUNDER)
    _write_text(them, by_kind["THEIR_QUESTIONS"]["from"], THEIR_THEM)
    if plan.get("heard_option_label"):
        # item 1's window opens where the STORY stretch ended (keel-cloud 249 judgement call 3: the latest stretch
        # that ended at or before the filing) and runs to its filing
        _write_text(them, by_kind["STORY"]["to"], plan["heard_option_label"])
    return {"founder": wav_bytes(founder), "them": wav_bytes(them)}


def write_record(run_dir: Path, script: dict) -> dict:
    """The record for one call written into `run_dir/call-record/` (founder.wav, them.wav, keys.json); returns the paths,
    the log and the plan."""
    out = Path(run_dir) / "call-record"
    out.mkdir(parents=True, exist_ok=True)
    (out / "script.json").write_text(json.dumps(script, indent=2) + "\n", encoding="utf-8")   # what the log was built off
    built = build_key_log(script)
    audio = tracks(built["log"], built["plan"])
    (out / "keys.json").write_text(json.dumps(built["log"], indent=2) + "\n", encoding="utf-8")
    (out / "founder.wav").write_bytes(audio["founder"])
    (out / "them.wav").write_bytes(audio["them"])
    return {"dir": out, "log": built["log"], "plan": built["plan"], "founder": audio["founder"], "them": audio["them"]}


def write_fixtures() -> None:
    """The committed fixtures: the key log's template (the times, the shape, placeholders for the ids) and the founder's
    silent track with its tone markers (script-independent); the person's track is written per run (its words name the
    served labels)."""
    FIXTURES.mkdir(parents=True, exist_ok=True)
    template = {"clientId": "c-eval-154", "scriptRevision": "{revision}", "start": 0, "end": TIMES["end"],
                "filings": [{"at": TIMES["gate"], "itemId": "{gate}", "option": "{gate.yes}"},
                            *[{"at": at, "itemId": f"{{item{n + 1}}}", "option": f"{{item{n + 1}.option}}"} for n, at in enumerate(TIMES["items"])],
                            {"at": TIMES["refile"], "itemId": "{item3}", "option": "{item3.option}"},
                            {"at": TIMES["pilot"], "itemId": "{pilot}", "option": "{pilot.yes}"}],
                "undos": [{"at": TIMES["undo"], "itemId": "{item3}"}],
                "stretches": [{"kind": "STORY", "from": TIMES["gate"], "to": TIMES["story_to"], "itemId": "{gate}"},
                              {"kind": "FOLLOW_UP", "from": TIMES["items"][1], "to": TIMES["items"][1] + TIMES["follow_up_to"], "itemId": "{item2}"},
                              {"kind": "OWN_QUESTIONS", "from": TIMES["own"][0], "to": TIMES["own"][1]},
                              {"kind": "THEIR_QUESTIONS", "from": TIMES["theirs"][0], "to": TIMES["theirs"][1]}]}
    TEMPLATE.write_text(json.dumps(template, indent=2) + "\n", encoding="utf-8")
    founder = bytearray(DURATION_S * BYTES_PER_SECOND)
    for filing in template["filings"]:
        _write_tone(founder, filing["at"])
    (FIXTURES / "founder.wav").write_bytes(wav_bytes(founder))


if __name__ == "__main__":
    write_fixtures()
