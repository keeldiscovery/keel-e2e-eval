"""keel-web 156 FR-1 (J-6): the lock step's people in the plural, by the page's grammar -- `vs_screens.people_plural`
is keel-web's `peoplePlural` ported (translate.ts), pinned on the page's own examples and on 03-lullaby's *parent*."""
from harness import vectors_screens as vs


def test_the_pages_examples():
    assert vs.people_plural("parent") == "parents"
    assert vs.people_plural("the parent") == "parents"
    assert vs.people_plural("construction superintendent") == "construction superintendents"
    assert vs.people_plural("Deaf or hard-of-hearing adult") == "deaf or hard-of-hearing adults"
    assert vs.people_plural("HR manager") == "HR managers"
    assert vs.people_plural("CFO") == "CFOs"
    assert vs.people_plural("head of finance") == "heads of finance"
    assert vs.people_plural("person who has a baby") == "people who have a baby"
    assert vs.people_plural("parents of babies under six months") == "parents of babies under six months"
    assert vs.people_plural("payroll practitioners") == "payroll practitioners"
    assert vs.people_plural("boss") == "bosses"
    assert vs.people_plural("nanny") == "nannies"
    assert vs.people_plural("") is None and vs.people_plural(None) is None


def test_the_lock_title_on_lullaby():
    assert vs.l1_title(vs.people_plural("parent")) == "Who should ask parents your questions?"
    assert vs.l1_title(None) == "Who should ask them your questions?"
