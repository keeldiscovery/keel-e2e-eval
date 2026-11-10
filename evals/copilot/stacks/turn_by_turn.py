"""Spec 151 FR-5 Stack 1, `turn_by_turn`: Keel's path today, one turn at a time. The turn's end comes from the script's
silences (the browser's own silence detection stands in: `TURN_END_HOLD`), gpt-transcribe writes the turn down with
`keywords[]` from the current item's labels and the questionnaire's stems, then Haiku 5.5 (the noise pipeline's request
shape) on `instructions/copilot-match.md` says which question it is, or reads the answer against the current item's
options (`norm_out` reused). At the text level the script's words stand for the transcript and nothing waits."""

from __future__ import annotations

from evals.copilot.stacks import base

TRANSCRIBE_PROMPT = "One turn of a video call: a founder asking survey questions, or the respondent answering."


def match_prompt(q: dict, current: str | None, state: str, who: str, heard: str) -> str:
    lines = [base.questionnaire_block(q), ""] + base.status_lines(current, state)
    lines += [f"Speaker: {base.SPEAKER[who]}", f'They said: "{(heard or "").strip()}"']
    return "\n".join(lines)


class TurnByTurn(base.Stack):
    number = 1
    name = "turn_by_turn"
    levels = ("text", "audio")
    instruction_file = "copilot-match.md"

    def run(self, script, q, clients, *, level, audio_dir=None, clocks=None):
        system = base.instruction(self.instruction_file)
        items = {it["id"]: it for it in q["items"]}
        current, state, events = None, "listening", []
        for i, turn in enumerate(script["turns"]):
            usage, wait, t_ms = {}, 0.0, 0
            heard = turn["text"]
            if level == "audio":
                start, end = clocks[i]["start"], clocks[i]["end"]
                wav = base.cut_wav(base.track_of(audio_dir, turn["who"]), start, end)
                heard, t_ms, secs = clients.transcribe(wav, keywords=base.keywords(q, current),
                                                       prompt=TRANSCRIBE_PROMPT)
                wait = min(base.TURN_END_HOLD, float(turn.get("silence_after") or 0) or base.TURN_END_HOLD)
                usage["transcribe_s"] = secs or (end - start)
            reply, c_ms = clients.messages(base.haiku_body(system, match_prompt(q, current, state, turn["who"], heard)))
            usage.update(base.haiku_usage(reply))
            ev = base.event_from(base.read_reply(reply), turn=i, who=turn["who"], items=items, current=current,
                                 state=state)
            ev.update(heard=heard, parts={"wait": wait, "transcribe": t_ms / 1000, "classify": c_ms / 1000},
                      usage=usage)
            ev["t_emitted"] = round(sum(ev["parts"].values()), 3)
            events.append(ev)
            current, state = base.advance(ev, current), ev["state"]
        return events
