"""keel-cloud's fake contact source, restated (spec 043): what `FakeContactSource` will count and return for a query,
read from keel-cloud's own fixture (`src/main/resources/keel/contacts/fake-contacts.json`, read-only) so the contacts
leg can hold the wire to **the fake's counts** rather than to numbers typed here.

keel-cloud spec 092 FR-D: 59 invented people for a payroll study (30 GB, 29 US; six with no work email, three in each
country), every address under `.example`. The stack's default source (`keel.v2.contacts.source = fake`), so the eval
stack calls no vendor and needs nothing new. The matching rules restated from `FakeContactSource.matching`:

- only people with a work email, and never one in the excluded set (the port's contract, E5 / E11);
- a title matches when every word of it is a word of the person's title (`split("\\W+")`, ASCII, lower-cased);
- levels, categories (case-insensitive) and sizes match any of their values, an empty list matching all;
- places match any of theirs: a COUNTRY on `country`, a REGION on `region`, a CITY on `region` and `city`;
- a page is the next `page_size` people in **fixture order** after the cursor's position.

This module is machinery: it asserts nothing. `evals/contacts_leg.py` asserts with it.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

FIXTURE = Path("src/main/resources/keel/contacts/fake-contacts.json")

#: keel-cloud `Dataset.PAGE_SIZE`; `InferenceCharge.CONTACT_PAGE` / `CONTACT_EMAIL` and their Starter-rate
#: costs in µUSD (spec 093 judgement call 6: 30,000 a name -- one source credit at $0.03 -- and 60,000 an email, two).
PAGE_SIZE = 25
PAGE_CREDITS = 150
EMAIL_CREDITS = 12
NAME_CREDITS = PAGE_CREDITS // PAGE_SIZE
NAME_COST_MICRO_USD = 30_000
EMAIL_COST_MICRO_USD = 60_000
#: `InferenceCharge.VERSION`, which every HOLD carries: 8 at spec 093, **9** since keel-cloud 094 added the interviewer's
#: two rows (spec 044 FR-001; the contacts rows and their prices did not move); **10** since keel-cloud 104 (BRIEF out,
#: THEMES in; spec 052 -- no contacts price moved); **11** since keel-cloud 125 (EXAMPLE_MATCH added at 0, never held;
#: no price moved -- S-006 met it on the 129 build, spec 068); 12 since keel-cloud 156 (spec 088: INTERVIEW 30 at
#: Begin added, INTERPRET and THEMES priced 0; no contacts price moved); **13** since keel-cloud 169 (spec 105:
#: PROBLEM_INTERPRET 26 and SOLUTION_MECHANISM 28, the frame class on frontier; no contacts price moved); **14** since
#: keel-cloud 170 (spec 110: RESPONDENT_QUESTIONS 35 -> 70, the lock's job on frontier; no contacts price moved).
PRICE_VERSION = 14

_WORDS = re.compile(r"\W+", re.ASCII)


class FakeUnavailable(RuntimeError):
    """The keel-cloud checkout carries no fake contact fixture (before spec 092)."""


@dataclass(frozen=True)
class FakePerson:
    source_id: str
    full_name: str
    job_title: str | None
    level: str
    size: str
    category: str
    city: str | None
    region: str
    country: str
    email: str | None
    email_status: str | None

    @property
    def verified(self) -> bool:
        return self.email_status == "VALID"


def people(keel_cloud: Path) -> list[FakePerson]:
    """Everyone in the fixture, in fixture order, with or without an email."""
    path = Path(keel_cloud) / FIXTURE
    if not path.is_file():
        raise FakeUnavailable(f"no {FIXTURE} in {keel_cloud}: keel-cloud predates spec 092's FakeContactSource")
    rows = json.loads(path.read_text(encoding="utf-8")).get("people") or []
    return [FakePerson(source_id=r["id"], full_name=r["fullName"], job_title=r.get("jobTitle"),
                       level=r["level"], size=r["companySize"], category=r.get("category") or "",
                       city=r.get("city"), region=r.get("region") or "", country=r.get("country") or "",
                       email=r.get("email"), email_status=r.get("emailStatus")) for r in rows]


def _title_matches(wanted: str, title: str | None) -> bool:
    if title is None:
        return False
    words = _WORDS.split(title.lower())
    return all(w in words for w in _WORDS.split(wanted.lower()) if w)


def _place_matches(place: dict, person: FakePerson) -> bool:
    kind = (place.get("kind") or "").upper()
    if kind == "COUNTRY":
        return place.get("code") == person.country
    if kind == "REGION":
        return place.get("code") == person.region
    if kind == "CITY":
        return (place.get("regionCode") == person.region
                and (place.get("name") or "").lower() == (person.city or "").lower())
    return False


def matching(everyone: list[FakePerson], query: dict, excluded: set[str] | frozenset = frozenset()) -> list[FakePerson]:
    """`FakeContactSource.matching`, restated over a `ContactQuery` as the wire carries it."""
    titles = query.get("titles") or []
    levels = set(query.get("levels") or [])
    categories = {c.lower() for c in query.get("categories") or []}
    sizes = set(query.get("companySizes") or [])
    places = query.get("places") or []
    return [p for p in everyone
            if p.email is not None
            and p.source_id not in excluded
            and (not titles or any(_title_matches(t, p.job_title) for t in titles))
            and (not levels or p.level in levels)
            and (not categories or p.category.lower() in categories)
            and (not sizes or p.size in sizes)
            and any(_place_matches(place, p) for place in places)]


def size(everyone: list[FakePerson], query: dict, excluded: set[str] | frozenset = frozenset()) -> int:
    """What `POST .../size` answers: people with a work email, none already fetched on the project."""
    return len(matching(everyone, query, excluded))


def page(everyone: list[FakePerson], query: dict, excluded: set[str] | frozenset = frozenset(), *,
         after: str | None = None, page_size: int = PAGE_SIZE) -> list[FakePerson]:
    """The next page, in fixture order, after the person `after` names (the cursor's position)."""
    position = next((i for i, p in enumerate(everyone) if p.source_id == after), -1) if after else -1
    rest = [p for p in matching(everyone, query, excluded) if everyone.index(p) > position]
    return rest[:page_size]


def by_id(everyone: list[FakePerson]) -> dict[str, FakePerson]:
    return {p.source_id: p for p in everyone}
