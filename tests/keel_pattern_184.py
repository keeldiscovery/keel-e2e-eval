"""Spec 149: the Check as keel-web 184 draws it (`KeelChanged.tsx`, `ListQuestion.tsx` at keel-web master `82a746d9`),
for the walk's tests -- Keel's rows (`li.listrow--keel[data-keel][data-n]`, the pill and number inside `span.listrow__box`,
the line `row-line` with its lead, the why `row-why` and Put back `row-put-back`) and the record *What Keel changed*
(`keel-changed`, each `keel-changed-entry[data-kind][data-whose][data-n]`). Built from a served list (contract 64) the
way 184's `keelKindOf` / `keelChanges` read it; the fixtures are invented (keel-cloud 243's own study).
"""

from __future__ import annotations

import html


def _e(text) -> str:
    return html.escape(str(text or ""), quote=True)


def keel_kind(item: dict, dimension: str) -> str | None:
    """keel-web 184 `keelKindOf`: in place where `inPlaceOf`, reworded where `typed` differs from the row, Compatibility's
    untouched `suggested` row a suggestion; else none."""
    if item.get("inPlaceOf"):
        return "in-place"
    if item.get("typed") and item.get("typed") != item.get("label"):
        return "reworded"
    if dimension == "solution.compatibility" and item.get("suggested"):
        return "suggestion"
    return None


def record(saved: dict) -> tuple[list[dict], dict[int, int]]:
    """keel-web 184 `keelChanges`: the record's entries -- put aside in served order (*replaced* where Keel's row stands
    in its place, else *aside*), then the reworded rows in list order -- numbered 1, 2, 3 where a Keel row pairs with
    one; and the number each row carries (by its index)."""
    items = saved.get("items") or []
    entries, numbers, n = [], {}, 0
    for aside in saved.get("putAside") or []:
        at = next((i for i, it in enumerate(items) if it.get("inPlaceOf") == aside.get("typed")), None)
        entry = {"kind": "replaced" if at is not None else "aside", "struck": [aside.get("typed")],
                 "why": aside.get("why"), "keels": bool(aside.get("keels"))}
        if at is not None:
            n += 1
            entry.update(n=n, now=items[at].get("label"))
            numbers[at] = n
        entries.append(entry)
    for at, item in enumerate(items):
        if item.get("typed") and item.get("typed") != item.get("label"):
            n += 1
            entries.append({"kind": "reworded", "struck": [item.get("typed")], "why": item.get("why"), "n": n,
                            "now": item.get("label"), "keels": bool(item.get("typedKeels"))})
            numbers[at] = n
    return entries, numbers


def row_html(item: dict, kind: str | None, n: int | None, *, locked: bool = False, note: str | None = None) -> str:
    if locked:
        return (f'<li class="listrow"><div class="listrow__line"><span class="listrow__ed listrow__ed--lock">'
                f'{_e(item["label"])}</span><span class="listrow__tag">yours</span></div></li>')
    box = f'<textarea class="listrow__ed" rows="1">{_e(item["label"])}</textarea>'
    cls = "listrow" + (" listrow--keel" if kind else "")
    attrs = (f' data-keel="{kind}"' + (f' data-n="{n}"' if n is not None else "")) if kind else ""
    if kind:
        box = (f'<span class="listrow__box"><span class="listrow__pill" data-testid="row-keel">Keel</span>'
               + (f'<span class="keelnum" data-testid="row-num" aria-hidden="true">{n}</span>' if n is not None else "")
               + box + "</span>")
    words = len(str(item["label"]).split())
    out = (f'<li class="{cls}"{attrs}><div class="listrow__line">{box}<span class="listrow__wc">{words} / 9</span>'
           f'<button type="button" class="listrow__rm">×</button></div>')
    if note:
        out += f'<p class="listrow__warn" role="note" data-testid="row-note">{_e(note)}</p>'
    if kind:
        behind = item.get("typed") if kind == "reworded" else item.get("inPlaceOf")
        why = item.get("why") if kind == "reworded" else item.get("suggestedWhy")
        lead = ("Keel's suggestion." if kind == "suggestion"
                else f'{"Reworded from" if kind == "reworded" else "In place of"} "{behind}".')
        out += (f'<p class="listrow__keel" data-testid="row-line" data-kind="{kind}"><span class="listrow__keel-k">'
                f'{_e(lead)}</span>'
                + (f'<span class="listrow__keel-why" data-testid="row-why">{_e(why)}</span>' if why else "")
                + (f'<button type="button" class="listrow__putback" aria-label="Put back &quot;{_e(behind)}&quot;" '
                   f'data-testid="row-put-back">Put back</button>' if kind != "suggestion" else "")
                + "</p>")
    return out + "</li>"


def record_html(entries: list[dict]) -> str:
    if not entries:
        return ""
    out = ['<div class="keelrecord" data-testid="keel-changed"><p class="listcheck__k">What Keel changed</p>'
           '<ul class="keelrecord__list">']
    for e in entries:
        n = e.get("n")
        out.append(f'<li class="keelrecord__entry" data-testid="keel-changed-entry" data-kind="{e["kind"]}" '
                   f'data-whose="{"keels" if e.get("keels") else "yours"}"' + (f' data-n="{n}"' if n else "") + ">"
                   '<p class="keelrecord__head">' + (f'<span class="keelnum" aria-hidden="true">{n}</span>' if n else "")
                   + "".join(f'<s class="keelrecord__struck">{_e(s)}</s>' for s in e["struck"])
                   + f'<span class="keelrecord__tag" data-testid="keel-changed-tag">'
                   f'{"Keel&#x27;s draft" if e.get("keels") else "yours"}</span></p>'
                   + (f'<p class="keelrecord__why" role="note">{_e(e["why"])}</p>' if e.get("why") else "")
                   + (f'<p class="keelrecord__as" data-testid="keel-changed-as">'
                      f'{"Replaced by" if e["kind"] == "replaced" else "Reworded as"} <b class="keelrecord__now">'
                      f'{_e(e["now"])}</b></p>' if e.get("now") else "")
                   + ('<p class="keelrecord__back"><button type="button" class="listrow__putback" '
                      'data-testid="put-aside-back">Put back</button></p>' if e["kind"] == "aside" else "")
                   + "</li>")
    return "".join(out) + "</ul></div>"


def band_html(band: dict | None) -> str:
    if not band:
        return ""
    return (f'<div class="calib__changed" role="status" data-testid="list-changed"><p class="calib__changed-line">'
            f'{_e(band.get("line"))}</p>' + (f'<p class="calib__changed-why">{_e(band.get("why"))}</p>'
                                             if band.get("why") else "") + "</div>")


def check_html(saved: dict, dimension: str, *, own_locked: bool = False, notes: dict | None = None) -> str:
    """The Check's list, the band over it and the record under it, as 184 draws a list the review changed."""
    entries, numbers = record(saved)
    rows = "".join(row_html(item, keel_kind(item, dimension), numbers.get(i), locked=own_locked and i == 0,
                            note=(notes or {}).get(item.get("label")))
                   for i, item in enumerate(saved.get("items") or []))
    return (band_html(saved.get("changed")) + '<div class="listcheck"><p class="listcheck__title">Check</p>'
            f'<ul class="listrows">{rows}</ul>{record_html(entries)}</div>')


def page(saved: dict, dimension: str, **kw) -> str:
    return ('<!doctype html><html><body><main><div class="ccard calib"><div class="ccard__body">'
            '<p class="corridor__kicker">Problem</p>' + check_html(saved, dimension, **kw)
            + '</div></div></main></body></html>')
