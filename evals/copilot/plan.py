"""Spec 151 FR-3: what each round's scripts must cover, drawn before a word is written -- seeded, so a round is
reproducible.

* **R1** one item, one founder habit, one respondent behaviour, under a minute: every applicable (item x founder habit x
  respondent behaviour), up to 700 (a seeded draw past that).
* **R2** one item with two or three follow-ups and their replies, then a second item, 2 to 4 minutes: about 200, drawn
  so every follow-up kind is covered.
* **R3** every item in the founder's own order with follow-ups and a few own-note stretches, 12 to 30 minutes: about 120.
* **R4** R3 run long -- an item at ten minutes of follow-ups, a five-minute silence, an item never reached -- 45 to 60
  minutes: about 12.

A plan entry: `{"id", "round", "seed", "items": [ids in asking order], "founder": {id: habit}, "respondent": {id:
behaviour}, "also": {id: second id} (stacked), "extras": [kinds around the asking], "follow_ups": {id: n}, "never_reached":
[ids], "silence": seconds | None, "long_item": id | None, "kinds": [every kind the script must show], "seconds": [low,
high]}`.
"""

from __future__ import annotations

import random

from evals.copilot import catalogue as cat

R1_CAP = 700
R2_N, R3_N, R4_N = 200, 120, 12
SEED_BASE = 151
#: R1's non-asking habits: an asking turn of their own is written beside them (verbatim).
R1_AROUND = ("own_note", "answered_for_them", "back_channel", "clarifying")


def seed_for(round_: int, seed: int | None = None) -> int:
    return SEED_BASE * 10 + round_ if seed is None else int(seed)


def _kinds(entry: dict) -> list[str]:
    ks = list(entry["founder"].values()) + list(entry["respondent"].values()) + list(entry.get("extras") or [])
    return sorted(set(ks))


def _entry(round_: int, n: int, seed: int, **kw) -> dict:
    e = {"id": f"r{round_}-{n:04d}", "round": round_, "seed": seed, "items": [], "founder": {}, "respondent": {},
         "also": {}, "extras": [], "follow_ups": {}, "never_reached": [], "silence": None, "long_item": None,
         "seconds": list(cat.ROUND_SECONDS[round_])}
    e.update(kw)
    extras = [k for k in e["extras"] if k != "clarifying"]
    if "counter_question" in e["respondent"].values():
        extras.append("clarifying")                                    # the clarifying line answers a counter-question
    e["extras"] = sorted(set(extras))
    e["kinds"] = _kinds(e)
    return e


def _behaviours(item: dict, round_: int) -> list[str]:
    return [b for b in cat.RESPONDENT if cat.applicable(b, item, round_=round_)]


def round1(q: dict, seed: int) -> list[dict]:
    items = q["items"]
    combos = []
    for idx, item in enumerate(items):
        other = items[(idx + 1) % len(items)]["id"] if len(items) > 1 else None
        for habit in cat.FOUNDER:
            if not cat.applicable(habit, item, round_=1, n_items=len(items)):
                continue
            needs = cat.FOUNDER[habit].needs
            for beh in _behaviours(item, 1):
                if needs and beh not in needs:
                    continue
                combos.append((item["id"], habit, beh, other))
    if len(combos) > R1_CAP:
        combos = sorted(random.Random(seed).sample(combos, R1_CAP), key=combos.index)
    out = []
    for n, (iid, habit, beh, other) in enumerate(combos, 1):
        extras = [habit] if habit in R1_AROUND else []
        founder = {iid: "verbatim" if habit in R1_AROUND else habit}
        if beh == "counter_question" and "clarifying" not in extras:
            extras.append("clarifying")
        out.append(_entry(1, n, seed, items=[iid], founder=founder, respondent={iid: beh}, extras=extras,
                          also={iid: other} if habit == "stacked" else {}))
    return out



def round2(q: dict, seed: int, n: int = R2_N) -> list[dict]:
    rng = random.Random(seed)
    items = q["items"]
    if len(items) < 2:
        raise SystemExit("plan refuses: round 2 needs at least two items")
    habits = [h for h in cat.ASKING if h not in ("stacked",)]
    rng.shuffle(habits)
    fups = list(cat.FOLLOW_UP_KINDS)
    out = []
    for i in range(n):
        a = items[i % len(items)]
        b = rng.choice([it for it in items if it["id"] != a["id"]])
        habit = next(h for h in habits[i % len(habits):] + habits if cat.applicable(h, a, round_=2))
        behs = _behaviours(a, 2)
        beh = behs[(i // len(items)) % len(behs)]
        extra = fups[i % len(fups)]
        extras = ["follow_up", extra] if extra != "follow_up" else ["follow_up"]
        if beh == "counter_question":
            extras.append("clarifying")
        if extra == "any_order":
            # the second item comes before the first in Keel's order
            ids = [it["id"] for it in items]
            a, b = (a, b) if ids.index(b["id"]) < ids.index(a["id"]) else (b, a)
            habit = next(h for h in habits if cat.applicable(h, a, round_=2))
            behs = _behaviours(a, 2)
            beh = behs[i % len(behs)]
            if beh == "counter_question":
                extras.append("clarifying")
        b_habit = next(h for h in habits[(i + 3) % len(habits):] + habits if cat.applicable(h, b, round_=2))
        out.append(_entry(2, i + 1, seed, items=[a["id"], b["id"]], founder={a["id"]: habit, b["id"]: b_habit},
                          respondent={a["id"]: beh, b["id"]: "straight"}, extras=sorted(set(extras)),
                          follow_ups={a["id"]: 3 if extra == "follow_ups_in_a_row" else 2}))
    return out


def _long(round_: int, q: dict, seed: int, n: int) -> list[dict]:
    rng = random.Random(seed)
    items = q["items"]
    habits = list(cat.ASKING)
    out = []
    for i in range(n):
        order = [it["id"] for it in items]
        if i % 4:                                                      # three in four in the founder's own order
            rng.shuffle(order)
        by = {it["id"]: it for it in items}
        founder, respondent, follow_ups = {}, {}, {}
        for j, iid in enumerate(order):
            pool = [h for h in habits if cat.applicable(h, by[iid], round_=round_, n_items=len(items))
                    and h != "stacked"]
            founder[iid] = pool[(i * len(order) + j) % len(pool)]
            behs = _behaviours(by[iid], round_)
            respondent[iid] = behs[(i + j) % len(behs)]
            follow_ups[iid] = rng.randint(0, 3)
        if not any(follow_ups.values()):
            follow_ups[order[0]] = 1                                   # at least one follow-up on every long call
        extras = ["own_note", "follow_up"] + (["any_order"] if order != [it["id"] for it in items] else [])
        if "counter_question" in respondent.values():
            extras.append("clarifying")
        if i % 3 == 0 and len(order) > 2:
            extras.append("went_back")
        kw = {}
        if round_ == 4:
            kw = {"never_reached": [order[-1]], "silence": 300, "long_item": order[len(order) // 2]}
            follow_ups[kw["long_item"]] = 12
            for gone in kw["never_reached"]:
                founder.pop(gone), respondent.pop(gone), follow_ups.pop(gone)
            order = order[:-1]
        out.append(_entry(round_, i + 1, seed, items=order, founder=founder, respondent=respondent,
                          extras=sorted(set(extras)), follow_ups=follow_ups, **kw))
    return out


def build(round_: int, q: dict, *, seed: int | None = None) -> list[dict]:
    s = seed_for(round_, seed)
    if round_ == 1:
        return round1(q, s)
    if round_ == 2:
        return round2(q, s)
    if round_ == 3:
        return _long(3, q, s, R3_N)
    if round_ == 4:
        return _long(4, q, s, R4_N)
    raise SystemExit(f"plan refuses: round {round_} is not 1, 2, 3 or 4")


def coverage(plan: list[dict]) -> dict:
    """How many entries name each kind."""
    out: dict = {}
    for e in plan:
        for k in e["kinds"]:
            out[k] = out.get(k, 0) + 1
    return dict(sorted(out.items()))
