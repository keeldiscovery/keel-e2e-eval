"""Spec 151 FR-6: the scorer, offline -- a run's events against its scripts' truth, the seven numbers, the certificate.

* **A** mapping, per founder turn: right question and right verdict (as written and same meaning read as one), a
  confusion matrix by the catalogue kind the turn was written for, the own-words options rows on their own; precision =
  real Keel questions not filed as a follow-up, a note, a back-channel or nothing.
* **B** the answer read, per answer turn: `ok` as the noise check (`evals.noise.pipeline.ok`), by control and tier,
  offered vs not (the asking kind's `offers_options`), confident-wrong = read *sure* and wrong; a noisy script's rows
  reported, never gated (the call is in a quiet room).
* **C** follow-ups: tagged to the right question; each stretch's boundaries right (every turn in it tagged, the turns
  either side not); own notes kept apart; follow-up replies never read as answers.
* **D** following: a move is a founder turn that asks a question other than the current one; false moves, missed moves
  (each one key), keys per question, seconds behind (the move's `t_emitted`, median).
* **E** unsure calls on the answers the script says were readable (the catalogue writes unclear ones on purpose; the
  raw rate is reported), and the share of unsure calls the script says were truly unclear.
* **F** (R4) mapping right after 30 minutes; the pause shown where the script says.
* **G** time to match: question asked -> recognised, answer given -> shown, median and worst, each split into the
  turn-end wait, the transcription and the classification.

The certificate line, as the noise check prints it: PASS, FAIL naming the first failing cell, or INCOMPLETE (a gated
cell with no rows). Costs from usage at list prices.
"""

from __future__ import annotations

import statistics as st

from evals.copilot import bars as B
from evals.copilot import catalogue as cat
from evals.copilot.render import TTS_USD_A_MINUTE
from evals.copilot.stacks.audio_direct import AUDIO_USD_IN_PER_M
from evals.copilot.stacks.base import HAIKU_USD_IN, HAIKU_USD_OUT
from evals.noise.pipeline import TRANSCRIBE_USD_A_MINUTE, ok

LIVE_USD_A_MINUTE = 0.017
LATE_S = 1800


def pct(a: int, b: int) -> float | None:
    return None if not b else round(100 * a / b, 1)


def med(xs: list) -> float | None:
    return round(st.median(xs), 3) if xs else None


def _verdict_right(truth_v: str, got_v: str | None) -> bool:
    if truth_v in cat.MEANING_KEPT:
        return got_v in cat.MEANING_KEPT
    return got_v == truth_v


def _asking(turns: list, i: int, q: str):
    for t in reversed(turns[:i]):
        tr = t["truth"]
        if t["who"] == "founder" and tr.get("q") == q and tr.get("verdict") in cat.QUESTION_VERDICTS:
            return t
    return None


def _offered(turn) -> bool:
    if turn is None:
        return False
    k = cat.KINDS.get(turn.get("kind") or "")
    if k is not None and k.offers_options is not None:
        return bool(k.offers_options)
    return turn["truth"].get("verdict") in ("as_written", "options_own_words")


def _tagged_at(turns: list, evs: dict, k: int, q: str | None) -> bool:
    """Turn `k`'s event tags it as a follow-up under `q` (a reply: its state is follow-up)."""
    e = evs.get(k) or {}
    return e.get("q") == q and (e.get("verdict") == "follow_up" or (turns[k]["who"] == "them"
                                                                    and e.get("state") == "follow_up"))


def rows(scripts: list[dict], events: dict, q: dict, *, noisy: set | None = None) -> dict:
    """Every scored row, by number."""
    items = {it["id"]: it for it in q["items"]}
    noisy = noisy or set()
    out = {k: [] for k in ("A", "B", "C", "C_blocks", "C_notes", "C_answers", "D", "F_late", "F_limits", "G_q")}
    d = {"moves": 0, "missed": 0, "false": 0, "behind": []}
    for s in scripts:
        turns = s["turns"]
        evs = {e["turn"]: e for e in events.get(s["id"]) or []}
        truth_cur = ev_cur = None
        for i, t in enumerate(turns):
            tr, e = t["truth"], evs.get(i) or {}
            got_q, got_v = e.get("q"), e.get("verdict")
            base = {"script": s["id"], "turn": i, "t": t["t"], "who": t["who"], "kind": t.get("kind"),
                    "text": t["text"], "heard": e.get("heard"), "t_emitted": e.get("t_emitted"),
                    "parts": e.get("parts") or {}}
            if t["who"] == "founder":
                tv = tr.get("verdict")
                row = dict(base, truth_q=tr.get("q"), truth_v=tv, got_q=got_q, got_v=got_v,
                           right=got_q == tr.get("q") and _verdict_right(tv, got_v))
                out["A"].append(row)
                if tv in cat.QUESTION_VERDICTS:
                    if got_q == tr.get("q"):
                        out["G_q"].append(row)
                    if t["t"] >= LATE_S:
                        out["F_late"].append(row)
                # D: the moves
                truth_move = tv in cat.QUESTION_VERDICTS and tr.get("q") and tr["q"] != truth_cur
                ev_move = got_v in cat.QUESTION_VERDICTS and got_q and got_q != ev_cur
                if truth_move:
                    d["moves"] += 1
                    if ev_move and got_q == tr["q"]:
                        d["behind"].append(e.get("t_emitted") or 0.0)
                    else:
                        d["missed"] += 1
                elif ev_move:
                    d["false"] += 1
                out["D"].append(dict(row, truth_move=bool(truth_move), ev_move=bool(ev_move)))
                if tv == "own_note":
                    out["C_notes"].append(dict(row, apart=got_v != "follow_up"))
            # B: the answers
            if t["who"] == "them" and tr.get("verdict") is None and tr.get("option") is not None \
                    and tr.get("q") in items and items[tr["q"]]["kind"] in cat.CLOSED:
                got = e.get("option") if e.get("option") is not None else {"unclear": True}
                asking = _asking(turns, i, tr["q"])
                tier = e.get("tier") if e.get("tier") else ("unsure" if got.get("unclear") else None)
                good = ok(tr["option"], got)
                out["B"].append(dict(base, q=tr["q"], control=items[tr["q"]]["control"],
                                     item_kind=items[tr["q"]]["kind"], expected=tr["option"], got=got, ok=good,
                                     truth_tier=tr.get("tier"), tier=tier, offered=_offered(asking),
                                     noisy=s["id"] in noisy, confident_wrong=tier == "sure" and not good))
            # C: the follow-ups (founder and replies)
            if tr.get("verdict") == "follow_up":
                tagged = got_q == tr.get("q") and (got_v == "follow_up" or (t["who"] == "them"
                                                                            and e.get("state") == "follow_up"))
                out["C"].append(dict(base, truth_q=tr.get("q"), got_q=got_q, got_v=got_v, tagged=tagged))
                if t["who"] == "them" and e.get("option") and not e["option"].get("unclear"):
                    out["C_answers"].append(dict(base, got=e["option"]))
            if tr.get("state_after") == "paused":
                out["F_limits"].append(dict(base, shown=e.get("state") == "paused"))
            if t["who"] == "founder":
                truth_cur = tr["q"] if tr.get("verdict") in cat.QUESTION_VERDICTS and tr.get("q") else truth_cur
                ev_cur = got_q if got_v in cat.QUESTION_VERDICTS and got_q else ev_cur
        # C's stretches
        i = 0
        while i < len(turns):
            tr = turns[i]["truth"]
            if tr.get("verdict") != "follow_up":
                i += 1
                continue
            j = i
            while j + 1 < len(turns) and turns[j + 1]["truth"].get("verdict") == "follow_up" \
                    and turns[j + 1]["truth"].get("q") == tr.get("q"):
                j += 1
            qq = tr.get("q")
            inside = all(_tagged_at(turns, evs, k, qq) for k in range(i, j + 1))
            before = i > 0 and _tagged_at(turns, evs, i - 1, qq) and turns[i - 1]["truth"].get("verdict") != "follow_up"
            after = j + 1 < len(turns) and _tagged_at(turns, evs, j + 1, qq)
            out["C_blocks"].append({"script": s["id"], "start": i, "end": j, "q": tr.get("q"),
                                    "right": inside and not before and not after})
            i = j + 1
    out["D_totals"] = d
    return out


def _cell(name: str, value, n: int, *, vacuous: bool = False) -> dict:
    op, bar, what = next((o, b, w) for c, o, b, w in B.BARS if c == name)
    if value is None or (n == 0 and not vacuous):
        return {"name": name, "value": None, "n": n, "op": op, "bar": bar, "what": what, "status": "not measured"}
    good = value >= bar if op == ">=" else value <= bar
    return {"name": name, "value": value, "n": n, "op": op, "bar": bar, "what": what, "status": "ok" if good else "fail",
            **({"vacuous": True} if vacuous else {})}


def cells(r: dict) -> dict:
    A, Bq = r["A"], [x for x in r["B"] if not x["noisy"]]
    same = [x for x in A if x["truth_v"] in cat.MEANING_KEPT]
    own = [x for x in A if x["truth_v"] == "options_own_words"]
    changed = [x for x in A if x["truth_v"] == "meaning_changed"]
    questions = [x for x in A if x["truth_v"] in cat.QUESTION_VERDICTS]
    offered = [x for x in Bq if x["offered"]]
    not_offered = [x for x in Bq if not x["offered"]]
    d = r["D_totals"]
    unsure = [x for x in Bq if x["tier"] == "unsure"]
    honest = [x for x in unsure if x["truth_tier"] == "unsure" or (x["expected"] or {}).get("unclear")]
    readable = [x for x in Bq if not (x["truth_tier"] == "unsure" or (x["expected"] or {}).get("unclear"))]
    q_clock = [x["t_emitted"] for x in r["G_q"] if x["t_emitted"] is not None]
    a_clock = [x["t_emitted"] for x in Bq if x["t_emitted"] is not None]
    out = {
        "A.same_meaning": _cell("A.same_meaning", pct(sum(x["right"] for x in same), len(same)), len(same)),
        "A.options_own_words": _cell("A.options_own_words", pct(sum(x["right"] for x in own), len(own)), len(own)),
        "A.meaning_changed": _cell("A.meaning_changed", pct(sum(x["right"] for x in changed), len(changed)),
                                   len(changed)),
        "A.precision": _cell("A.precision", pct(sum(x["got_v"] in cat.QUESTION_VERDICTS for x in questions),
                                                len(questions)), len(questions)),
        "B.offered": _cell("B.offered", pct(sum(x["ok"] for x in offered), len(offered)), len(offered)),
        "B.not_offered": _cell("B.not_offered", pct(sum(x["ok"] for x in not_offered), len(not_offered)),
                               len(not_offered)),
        "B.confident_wrong": _cell("B.confident_wrong", pct(sum(x["confident_wrong"] for x in Bq), len(Bq)), len(Bq)),
        "C.tagged": _cell("C.tagged", pct(sum(x["tagged"] for x in r["C"]), len(r["C"])), len(r["C"])),
        "C.boundaries": _cell("C.boundaries", pct(sum(x["right"] for x in r["C_blocks"]), len(r["C_blocks"])),
                              len(r["C_blocks"])),
        "D.false_move": _cell("D.false_move", pct(d["false"], d["moves"]), d["moves"]),
        "D.keys": _cell("D.keys", pct(d["false"] + d["missed"], d["moves"]), d["moves"]),
        "D.behind_s": _cell("D.behind_s", med(d["behind"]), len(d["behind"])),
        # the catalogue writes unclear answers on purpose (a quarter of R1), so the bar reads the unsure calls on the
        # answers the script says were readable; the raw rate is reported beside it (`E` in the sheet)
        "E.unsure": _cell("E.unsure", pct(sum(1 for x in readable if x["tier"] == "unsure"), len(readable)),
                          len(readable)),
        "E.honest": _cell("E.honest", pct(len(honest), len(unsure)) if unsure else (100.0 if Bq else None),
                          len(unsure), vacuous=bool(Bq) and not unsure),
        "F.late_mapping": _cell("F.late_mapping", pct(sum(x["right"] for x in r["F_late"]), len(r["F_late"])),
                                len(r["F_late"])),
        "F.limits": _cell("F.limits", pct(sum(x["shown"] for x in r["F_limits"]), len(r["F_limits"])),
                          len(r["F_limits"])),
        "G.question_s": _cell("G.question_s", med(q_clock), len(q_clock)),
        "G.answer_s": _cell("G.answer_s", med(a_clock), len(a_clock)),
        "G.worst_s": _cell("G.worst_s", round(max(q_clock + a_clock), 3) if q_clock + a_clock else None,
                           len(q_clock + a_clock)),
    }
    return out


def certificate(cs: dict, *, round_: int, stack: str, level: str) -> dict:
    gated = [c for c, *_ in B.BARS if c.split(".")[0] in B.ROUND_CELLS[round_]]
    failing = next((c for c in gated if cs[c]["status"] == "fail"), None)
    unmeasured = [c for c in gated if cs[c]["status"] == "not measured"]
    verdict = "FAIL" if failing else ("INCOMPLETE" if unmeasured else "PASS")
    head = f"Certificate (the founder's bars, {B.BARS_DATE}; round {round_}, {level}, {stack}): {verdict}"
    if failing:
        c = cs[failing]
        head += (f" -- the first failing cell is {failing} ({c['what']}): {c['value']}"
                 f"{'' if failing.endswith('_s') else '%'} {'<' if c['op'] == '>=' else '>'} {c['bar']:g}")
    elif unmeasured:
        head += f" -- {len(unmeasured)} of {len(gated)} cells not measured ({', '.join(unmeasured)})"
    bits = []
    for c in ("A.same_meaning", "A.options_own_words", "B.offered", "G.question_s", "G.answer_s"):
        v = cs[c]["value"]
        if v is not None:
            bits.append(f"{c} {v}{' s' if c.endswith('_s') else '%'}")
    line = head + (". " + ", ".join(bits) if bits else "") + "."
    return {"verdict": verdict, "failing": failing, "unmeasured": unmeasured, "gated": gated,
            "not_applicable": [c for c, *_ in B.BARS if c not in gated], "line": line}


def costs(events: dict, scripts: list[dict]) -> dict:
    """The stack's spend from its events' usage at list prices, and the cost of a 30-minute call at that rate."""
    u: dict = {}
    for evs in events.values():
        for e in evs:
            for k, v in (e.get("usage") or {}).items():
                u[k] = u.get(k, 0) + (v or 0)
    usd = {"anthropic": round((u.get("haiku_in", 0) * HAIKU_USD_IN + u.get("haiku_out", 0) * HAIKU_USD_OUT) / 1e6, 6),
           "openai_transcribe": round(u.get("transcribe_s", 0) / 60 * TRANSCRIBE_USD_A_MINUTE, 6),
           "openai_live": round(u.get("live_s", 0) / 60 * LIVE_USD_A_MINUTE, 6),
           "openai_audio": round(u.get("audio_tokens_in", 0) * AUDIO_USD_IN_PER_M / 1e6, 6)}
    total = round(sum(usd.values()), 6)
    minutes = sum((s["turns"][-1]["t"] + 1) / 60 for s in scripts if s.get("turns"))
    return {"usage": u, "usd": usd, "total_usd": total, "call_minutes": round(minutes, 2),
            "per_30_min_call_usd": round(total / minutes * 30, 4) if minutes else None,
            "unpriced": [k for k in ("audio_text_in", "audio_text_out") if u.get(k)]}


def run_costs(writer_records: list[dict], tts_seconds: float) -> dict:
    """What the run spent outside the stacks: the writer (Sonnet 5.5) and the voices."""
    w = round(sum(r.get("cost_usd") or 0 for r in writer_records), 6)
    tts = round(tts_seconds / 60 * TTS_USD_A_MINUTE, 6)
    return {"writer_usd": w, "tts_usd": tts, "tts_minutes": round(tts_seconds / 60, 2)}


def confusion(A: list[dict]) -> dict:
    out: dict = {}
    for x in A:
        k = x["kind"] or f"({x['truth_v']})"
        row = out.setdefault(k, {"n": 0, "right": 0, "q_right": 0, "got": {}})
        row["n"] += 1
        row["right"] += bool(x["right"])
        row["q_right"] += x["got_q"] == x["truth_q"]
        row["got"][x["got_v"] or "null"] = row["got"].get(x["got_v"] or "null", 0) + 1
    return dict(sorted(out.items()))


def by(rows_: list[dict], key: str) -> dict:
    out: dict = {}
    for x in rows_:
        g = out.setdefault(str(x.get(key)), {"n": 0, "ok": 0})
        g["n"] += 1
        g["ok"] += bool(x["ok"])
    return {k: dict(v, pct=pct(v["ok"], v["n"])) for k, v in sorted(out.items())}


def _parts(rows_: list[dict]) -> dict:
    return {p: med([(x.get("parts") or {}).get(p, 0.0) for x in rows_]) for p in ("wait", "transcribe", "classify")}


def sheet(scripts: list[dict], events: dict, q: dict, *, round_: int, level: str, stack: str, number: int,
          noisy: set | None = None) -> dict:
    r = rows(scripts, events, q, noisy=noisy)
    cs = cells(r)
    cert = certificate(cs, round_=round_, stack=f"stack {number} {stack}", level=level)
    Bq = [x for x in r["B"] if not x["noisy"]]
    late = [x for x in r["G_q"] + Bq if x["t_emitted"] is not None and x["t_emitted"] > 0
            and x["t_emitted"] > _gap(scripts, x)]
    return {
        "stack": stack, "number": number, "round": round_, "level": level, "n_scripts": len(scripts),
        "n_turns": sum(len(s["turns"]) for s in scripts), "cells": cs, "certificate": cert,
        "A": {"confusion": confusion(r["A"]),
              "options_own_words_rows": [x for x in r["A"] if x["truth_v"] == "options_own_words" and not x["right"]]},
        "B": {"by_control": by(Bq, "control"), "by_tier": by(Bq, "truth_tier"), "by_kind": by(Bq, "kind"),
              "noisy": by([x for x in r["B"] if x["noisy"]], "control"), "n": len(r["B"])},
        "C": {"notes_apart": pct(sum(x["apart"] for x in r["C_notes"]), len(r["C_notes"])),
              "read_as_answers": len(r["C_answers"]), "stretches": len(r["C_blocks"])},
        "D": {k: v for k, v in r["D_totals"].items() if k != "behind"},
        "E": {"unsure_of_all_answers": pct(sum(1 for x in Bq if x["tier"] == "unsure"), len(Bq)),
              "written_unclear": sum(1 for x in Bq if x["truth_tier"] == "unsure"), "answers": len(Bq)},
        "G": {"question_parts": _parts(r["G_q"]), "answer_parts": _parts(Bq), "after_the_next_turn_began": len(late)},
        "misses": [_miss(x) for x in r["A"] if not x["right"]][:60] + [_miss(x) for x in r["B"] if not x["ok"]][:60],
        "cost": costs(events, scripts),
    }


def _gap(scripts: list[dict], x: dict) -> float:
    s = next(s for s in scripts if s["id"] == x["script"])
    return float(s["turns"][x["turn"]].get("silence_after") or 0) if x["turn"] + 1 < len(s["turns"]) else float("inf")


def _miss(x: dict) -> dict:
    keep = ("script", "turn", "who", "kind", "text", "heard", "truth_q", "truth_v", "got_q", "got_v", "expected", "got",
            "tier", "truth_tier")
    return {k: x.get(k) for k in keep if k in x}
