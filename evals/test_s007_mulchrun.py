"""S-007: `07-mulchrun`, the only US market (spec 010 US2, T031).

`{country: US, region: TX, language: en-US}` -- the only entry that exercises American English,
dollars **and cents**, the three US physical unit families (miles, feet, cubic yards, never
converted), a non-null region on the market screen, and design rule `M1`.

It also holds the tightest phrase-table-to-builder chain in the corpus: the founder's *about 45
minutes* becomes the band 33.75…56.25, which is rounded to the duration unit's own five-minute
step and **cut at exactly those edges** -- `35 min to 55 min`, with the scale on either side of
it. If a bucket boundary here is off by one step, the whole rounding rule is wrong, and no other
entry would have shown it.
"""

from __future__ import annotations

import re

from evals import corpus_scenario

ENTRY_ID = "07-mulchrun"

# The band's own edges, after *about 45 minutes* -> 33.75…56.25 -> rounded to the unit's five-
# minute step. The scale is cut at exactly those two labels.
BAND_EDGES = ("30 min to 35 min", "35 min to 55 min", "55 min to 1 h")

# The three US unit families, and the one currency. `never converted` is the assertion: a US
# market that quietly rendered kilometres would be design rule M1 broken, not a preference.
US_UNITS = ("miles", "feet", "cubic yards")
METRIC_LEAKS = ("kilometre", "kilometer", " km", "metre", "meter", "litre", "liter", "£", "€")


def _mulchrun_extras(ctx) -> None:
    recorder, entry, overview = ctx["recorder"], ctx["entry"], ctx["overview"]
    buckets = entry.expected.get("buckets") or {}

    with recorder.step("T031: the market persisted as United States, Texas",
                        party="stack", kind="assert") as h:
        market = (ctx["get"](f"/v2/projects/{ctx['project_id']}/overview") or {}).get("market") or {}
        h.record_assert({"country": "US", "region": "TX", "language": "en-US"}, market)
        assert market.get("country") == "US"
        assert market.get("region") == "TX", (
            f"the region is the only non-null one in the corpus and it did not persist: {market}")
        assert market.get("language") == "en-US"

    with recorder.step("T031: the duration scale is cut at the band's own rounded edges",
                        party="stack", kind="assert") as h:
        scale = list(buckets.get("S2") or [])
        h.record_assert(list(BAND_EDGES), scale)
        for edge in BAND_EDGES:
            assert edge in scale, (
                f"{edge!r} is missing from S2's scale {scale} -- *about 45 minutes* rounds to "
                "35…55 on the unit's own five-minute step, and the scale is cut there")
        assert scale.index(BAND_EDGES[0]) + 1 == scale.index(BAND_EDGES[1]), scale
        assert scale.index(BAND_EDGES[1]) + 1 == scale.index(BAND_EDGES[2]), scale

    with recorder.step("T031: every money option is in dollars and cents, down to the minor unit",
                        party="stack", kind="assert") as h:
        money = list(buckets.get("S11") or [])
        h.record_assert("$, with cents", money)
        assert money, "the entry's own money scale is missing"
        assert all("$" in label for label in money), money
        assert any(re.search(r"\$\d+\.\d\d?\b", label) for label in money), (
            f"no money option reaches the minor unit: {money}")

    with recorder.step("T031: every physical option is in a US unit family, never converted",
                        party="stack", kind="assert") as h:
        physical = [label for key in ("S3", "S4", "S5") for label in buckets.get(key) or []]
        h.record_assert(list(US_UNITS), physical)
        for family, key in zip(US_UNITS, ("S3", "S4", "S5")):
            assert all(family in label or "more than" in label for label in buckets.get(key) or []), (
                f"{key} is not in {family}: {buckets.get(key)}")

    # **The same sweep over strictly more text, because the screen changed under it.** It read
    # three things: the evidence bar's headline, the *What this says* box, and the three
    # `OverviewCard` claim sentences. keel-web spec 027 retired all three from this route (FR-020)
    # and moved the paragraph to page 1 of the sheet (FR-027). So the sweep reads **the whole
    # deck** -- the ship's caption, every panel's name, status word, claim and count line, every
    # HELD and DID NOT HOLD clause, and the foot -- and the printed paragraph beside it. Nothing
    # it swept before is out of its reach now; several things it never swept are in it.
    with recorder.step("T031: no metric unit and no other currency reaches the deck",
                        party="founder", kind="assert") as h:
        body = overview.deck_text()
        leaks = [token for token in METRIC_LEAKS if token in body]
        h.record_assert([], leaks)
        assert body.strip(), "the deck rendered no text at all, so this swept nothing"
        assert not leaks, f"a US market screen carries {leaks}: {body[:400]!r}"

    print_page = ctx["print_page"]
    print_page.open(ctx["project_id"])
    with recorder.step("T031: and none reaches the paragraph the founder hands over",
                        party="founder", kind="assert") as h:
        # The half of the old sweep that moved. `Overview.whatThisSays` is the model's own prose
        # about a US market's numbers, which is the single most likely place for a metric unit to
        # appear -- so it is swept where it is now drawn rather than dropped with the box it used
        # to sit in.
        paragraph = print_page.what_this_says_paragraph()
        leaks = [token for token in METRIC_LEAKS if token in paragraph]
        h.record_assert([], leaks)
        assert paragraph.strip(), (
            "page 1 of the brief prints no paragraph, so the one piece of model prose about this "
            "market's numbers went unswept")
        assert not leaks, f"the printed paragraph carries {leaks}: {paragraph[:400]!r}"


def test_s007_mulchrun(stack, founder_one, browser, run_dir):
    corpus_scenario.run(stack, founder_one, browser, run_dir,
                        entry_id=ENTRY_ID, slug="s007-mulchrun", extra=_mulchrun_extras)
