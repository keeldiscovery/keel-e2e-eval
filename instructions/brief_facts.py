"""The `facts`, `beliefs` and `stories` a `BRIEF` job is handed (keel-cloud 079, contract 9).

keel-cloud computes `BriefFacts` from a project's stored answers; the corpus holds no project, only
`expected.standings`, so **this is the eval's reading of those standings in the same shape**, and
it keeps no copy of keel-cloud's arithmetic: it only restates counts the standings already carry
(`n`, `inside`, `optionCounts`, `median`) and the §4.2 decision rule that names a label. What the
corpus cannot say is left out, as keel-cloud leaves it out: no `sharpest` (a cross-tab of two
questions; the corpus records none) and no `priceTable` (the ladder's rows). `brief.md` says both
are optional, and the marks hold the result to exactly the facts it was handed.
"""

from __future__ import annotations

VERDICT_WORDS = {
    "HOLDING_UP": "Holding up", "NOT_HOLDING_UP": "Not holding up",
    "PEOPLE_DISAGREE": "People disagree", "TOO_FEW_TO_CALL": "Too few to call",
    "NOT_ASKED_YET": "Not asked yet", "LEFT_OUT": "Left out", "NOT_TESTED": "Not tested",
}
CURRENCY_SYMBOL = {"GBP": "£", "USD": "$", "EUR": "€", "JPY": "¥"}
_THIN = ("TOO_FEW_TO_CALL", "NOT_ASKED_YET")


def _dims(vectors: list) -> list:
    return [(v["vector"], d) for v in vectors for d in v["dimensions"]]


def decision(vectors: list, b2b: bool) -> dict:
    """§4.2 (`BriefFacts.decision`): the label and how sure, from the vectors' verdicts."""
    verdicts = {v["vector"]: v.get("verdict") for v in vectors}
    problem = next(v for v in vectors if v["vector"] == "PROBLEM")
    deal = lambda d: d.get("weight") == "DEAL_BREAKER"            # noqa: E731
    not_tested = [v["vector"] for v in vectors if v.get("verdict") == "NOT_TESTED"]
    split = False
    if any(deal(d) and d.get("status") in _THIN for d in problem["dimensions"]) \
            or verdicts.get("PROBLEM") == "NOT_TESTED":
        label = "KEEP_INTERVIEWING"
    elif verdicts.get("PROBLEM") != "HOLDING_UP":
        label = "NOT_YET"
        split = verdicts.get("PROBLEM") == "PEOPLE_DISAGREE"       # keel-cloud 082: a split, not a no
    elif not_tested:
        label = "KEEP_INTERVIEWING"
    elif all(v == "HOLDING_UP" for v in verdicts.values()):
        label = "BUILD"
    else:
        label = "BUILD_BUT_CHANGE"
    counted = [(vec, d) for vec, d in _dims(vectors)
               if deal(d) and d.get("status") not in ("NOT_ASKED_YET", "LEFT_OUT")
               and d.get("n_anchored") is not None]
    if not counted:
        return {"label": label, "howSure": "LOW", "reason": "Nothing has been asked yet.",
                "smallestN": 0, "split": split, "notTested": not_tested}
    vec, smallest = min(((v, d["n_anchored"]) for v, d in counted), key=lambda p: p[1])
    too_few = any(d.get("status") == "TOO_FEW_TO_CALL" for _, d in counted)
    disagree = any(d.get("status") == "PEOPLE_DISAGREE" for _, d in counted)
    how = "LOW" if smallest < 5 or too_few else "MEDIUM" if smallest < 10 or disagree \
        else "FAIRLY_SURE"
    who = ("decision-maker" if smallest == 1 else "decision-makers") \
        if b2b and vec == "COMMERCIAL" else ("person" if smallest == 1 else "people")
    return {"label": label, "howSure": how, "reason": f"Smallest group: {smallest} {who}.",
            "smallestN": smallest, "split": split, "notTested": not_tested}


def _row(dimension: dict) -> dict:
    """What a dimension's standing says, in the counts it carries and no others."""
    out = {"status": dimension.get("status"), "n": dimension.get("n_anchored")}
    for source, name in (("inside", "inside"), ("outside", "outside")):
        if dimension.get(source) is not None:
            out[name] = dimension[source]
    if dimension.get("observed"):
        out["said"] = dimension["observed"]
    if dimension.get("option_counts"):
        out["optionCounts"] = dimension["option_counts"]
    return out


def facts_for(entry, vectors: list, context: dict, currency: str | None, period: str | None,
              period_words: str) -> dict:
    """`facts`: decision, vectors, money, the three sections, targets, keys."""
    by_key = {d["key"]: d for _, d in _dims(vectors)}
    symbol = CURRENCY_SYMBOL.get(currency, f"{currency} " if currency else None)
    keys = [d["key"] for _, d in _dims(vectors)]
    section = {}
    for name in ("problem", "solution", "commercial"):
        section[name] = {k.split(".", 1)[1]: _row(d) for k, d in by_key.items()
                         if k.startswith(name + ".") and d.get("status") != "LEFT_OUT"}
    standing = ((entry.expected or {}).get("standings") or {}).get("problem.prevalence") or {}
    if standing.get("yes") is not None:
        section["problem"]["prevalence"] = {"yes": standing["yes"], "n": standing.get("n"),
                                            "window": context.get("window")}
    targets = [{"key": k, "name": d["name"], "status": d["status"], "n": d.get("n_anchored")}
               for k, d in by_key.items()
               if d.get("status") in ("NOT_HOLDING_UP", "PEOPLE_DISAGREE")][:3]
    return {
        "decision": decision(vectors, entry.b2b()),
        "vectors": [{"vector": v["vector"], "verdict": v.get("verdict"),
                     "words": VERDICT_WORDS.get(v.get("verdict"), "Not asked yet")}
                    for v in vectors],
        "money": {"currency": currency, "currencySymbol": symbol, "period": period,
                  "periodWords": period_words or None},
        **section,
        "sharpest": None,
        "targets": targets,
        "keys": keys,
    }


def beliefs_for(vectors: list) -> list:
    """`beliefs`: per dimension the founder calibrated, `{key, name, weight, belief_sentence,
    founder_phrase}`."""
    return [{"key": d["key"], "name": d["name"], "weight": d["weight"],
             "belief_sentence": d.get("belief_sentence"), "founder_phrase": d.get("founder_phrase")}
            for _, d in _dims(vectors) if d.get("belief_sentence")]


def stories_for(entry) -> list:
    """`stories`: each readable person's story by invitation id (the person's id, here)."""
    return [{"invitation_id": p.person, "link": p.link, "story": p.story}
            for p in entry.people() if p.readable]
