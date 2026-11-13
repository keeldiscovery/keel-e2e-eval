"""Spec 150 (keel-web 185, the founder, 2026-11-09: Interviews is Sent alone): the journeys without the contacts leg.

FR-1: the leg, its marks and the fake contact source are gone (no journey seeds people through the cloud's contacts
endpoints any more); `harness/interviews_screens.py` has no `Contacts` page object, no dataset screens and no
`send_from_dataset`; the nav is one row; Send more's ways are OWN and GROUP; S-006's links past the twenty are made on
Sent (`leg_sent_more`), S-005's NOT_B2B refusal is gone with its page. Each pin held against keel-web's own words where
the checkout is there (skipped by name on a keel-web before 185)."""

from __future__ import annotations

import importlib.util
import inspect
import re
from pathlib import Path

import pytest

from evals import corpus_scenario as cs
from evals import open_link_leg, scope_journey
from harness import interviews_screens as iv
from stack.config import load_config

REPO = Path(__file__).resolve().parent.parent
WEB = load_config(validate=False).keel_web


def _web(rel: str) -> str:
    path = WEB / rel
    if not path.is_file():
        pytest.skip(f"keel-web has no {rel}")
    return path.read_text(encoding="utf-8")


def _web_185() -> str:
    translate = _web("src/lib/translate.ts")
    if 'INTERVIEWS_SUBPAGES = [{ key: "sent"' not in translate:
        pytest.skip("keel-web predates spec 185 (INTERVIEWS_SUBPAGES still holds Contacts and Keel-managed)")
    return translate


# --------------------------------------------------------------------------------------- FR-1: what is gone

@pytest.mark.parametrize("module", ["evals.contacts_leg", "evals.contacts_marks", "harness.contacts_fake"])
def test_the_leg_its_marks_and_the_fake_source_are_gone(module):
    assert importlib.util.find_spec(module) is None, module


def test_no_journey_seeds_people_through_the_contacts_endpoints():
    """The fake contact source (`harness/contacts_fake.py`) stayed only if a journey still called `/contacts/...`: none
    does -- no module under evals/, harness/ or stack/ names a contacts route (keel-cloud 244 removes them)."""
    hits = []
    for folder in ("evals", "harness", "stack"):
        for path in (REPO / folder).rglob("*.py"):
            for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                # the cloud's routes (keel-cloud 244 retires them); the web's old *page* addresses are FR-3's, opened
                # on purpose by `leg_old_addresses`
                if re.search(r"""["'/]contacts/(datasets|suggest|plan)|/managed-requests""", line) \
                        and not line.lstrip().startswith(("#", "`")):
                    hits.append(f"{path.relative_to(REPO)}:{n}: {line.strip()}")
    assert not hits, hits


def test_the_page_objects_have_no_contacts_or_dataset_screens():
    source = Path(iv.__file__).read_text(encoding="utf-8")
    assert not hasattr(iv, "Contacts") and not hasattr(iv.Interviews, "send_from_dataset")
    for gone in ("WHO_DATASET", "CONTACTS_CLIP", "DATASET_OPEN", "COPY_AS_NEW", "CONTACTS_B2C_TITLE",
                 "CONTACTS_NEED_CREDITS_LINE", "GO_TO_SEND_MORE", "SEND_LINKS_TITLE", "FOUND_STATUS"):
        assert not hasattr(iv, gone), gone
    for selector in (".contacts__tabs", ".dsopen__title", ".dseditor", ".dsrow", ".pickrow", "#send-dataset",
                     "table.ppl--tight", "credits-refusal", ".ivsub", ".side-nav__group"):
        assert selector not in source.split('"""', 2)[2], selector         # past the module docstring's history


def test_send_more_has_two_ways():
    assert iv.SEND_WHO_IDS == ("send-who-OWN", "send-who-GROUP")
    assert (iv.WHO_OWN, iv.WHO_GROUP) == ("People I know by name", "A group, with one open link")
    want = inspect.getsource(open_link_leg.make_the_link)
    assert '"ways": [iv_screens.WHO_OWN, iv_screens.WHO_GROUP]' in want


@pytest.mark.skip(reason="retired by spec 154: keel-web 187 FR-3 / FR-4 replaced Send more's ways (SEND_WHO) with New link and New group link, one screen each")
def test_the_ways_are_keel_webs_own():
    translate = _web_185()
    block = re.split(r"\n}", translate.split("export const SEND_WHO = {", 1)[1], maxsplit=1)[0]
    assert re.findall(r"^  ([A-Z]+):", block, re.M) == ["OWN", "GROUP"], block
    assert f'name: "{iv.WHO_OWN}"' in block and f'name: "{iv.WHO_GROUP}"' in block
    popup = _web("src/components/interviews/SendMorePopup.tsx")
    assert "data-testid={`send-who-${option}`}" in popup


# ------------------------------------------------------------------------------------------ FR-1: the nav

class _Node:
    def __init__(self, words: str = "", attrs: dict | None = None):
        self.words, self.attrs = words, attrs or {}

    def text_content(self):
        return self.words

    def get_attribute(self, name):
        return self.attrs.get(name)


class _Found:
    """A Playwright locator's few reads: `first`, `count()`, `all()` and the first node's words and attributes."""

    def __init__(self, nodes: list):
        self.nodes = nodes

    @property
    def first(self):
        return _Found(self.nodes[:1])

    def count(self):
        return len(self.nodes)

    def all(self):
        return list(self.nodes)

    def text_content(self):
        return self.nodes[0].text_content() if self.nodes else None

    def get_attribute(self, name):
        return self.nodes[0].get_attribute(name) if self.nodes else None


class _Page:
    def __init__(self, dom: dict):
        self.dom = dom

    def locator(self, selector):
        return _Found(self.dom.get(selector, []))


def _sent(dom: dict) -> iv.Interviews:
    sent = iv.Interviews.__new__(iv.Interviews)
    sent.page = _Page(dom)
    return sent


def test_the_nav_reads_the_one_row_current_inside_the_section():
    row = _Node(" Interviews ", {"href": "/p/7/interviews/sent", "aria-current": "page"})
    nav = _sent({iv.NAV_ROW: [row]}).nav()
    assert nav == {"row": "Interviews", "href": "/p/7/interviews/sent", "subs": [], "current": ["Interviews"]}
    # off the section (or a web that marks no row current) reads no current row; a sub-row still drawn is read
    off = _sent({iv.NAV_ROW: [_Node("Interviews", {"href": "/p/7/interviews/sent"})],
                 ".side-nav a.side-nav__item--sub": [_Node("Contacts")]}).nav()
    assert off["current"] == [] and off["subs"] == ["Contacts"]
    assert iv.NAV_ROW == '.side-nav a.side-nav__item[href$="/interviews/sent"]' and iv.SUBPAGES == ["Sent"]


def test_the_kicker_is_interviews():
    assert iv.SENT_KICKER == iv.NAV_INTERVIEWS == "Interviews"
    assert _sent({"p.corridor__kicker": [_Node(" Interviews ")]}).kicker() == "Interviews"
    translate = _web_185()
    assert "export const SENT_KICKER = NAV_INTERVIEWS;" in translate
    assert 'export const NAV_INTERVIEWS = "Interviews";' in translate


def test_the_journey_holds_the_one_row_and_the_kicker():
    source = inspect.getsource(cs.leg_invite)
    assert 'nav["subs"] == [] and nav["current"] == [iv_screens.NAV_INTERVIEWS]' in source
    assert "kicker == iv_screens.SENT_KICKER" in source
    assert "iv_screens.SUBPAGES" not in source


def test_the_side_nav_is_keel_webs_one_row():
    _web_185()
    nav = _web("src/components/SideNav.tsx")
    assert "side-nav__item--sub" not in nav and "side-nav__group" not in nav
    assert "`${base}/interviews/sent`" in nav and 'aria-current={inside ? "page" : undefined}' in nav


# -------------------------------------------------------------------------------- FR-1: the journeys' extras

def test_s006_makes_its_links_past_the_twenty_on_sent():
    source = (REPO / "evals" / "test_s006_paidly.py").read_text(encoding="utf-8")
    assert "contacts_leg" not in source
    order = [source.index(s) for s in ("sample.take(j)", "corpus_scenario.leg_sent_more(j)",
                                       "corpus_scenario.leg_outside_decider(j)", "interviewer_leg.leg_interviewer(j)")]
    assert order == sorted(order), order


def test_s005_drives_no_contacts():
    source = (REPO / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    assert "contacts_leg" not in source and "NOT_B2B" in source              # named once, as history


def test_leg_sent_more_sends_by_name_and_makes_a_new_link():
    """The contacts leg's links past ten and its relink (keel-cloud 093 D7), on Send more by name: one decision-maker,
    *New link* on the row (old 404, new 200, the same invitation, Link made moved), an answered row's relink refused
    ALREADY_ANSWERED on the wire, then G16's links table past ten."""
    source = inspect.getsource(cs.leg_sent_more)
    for needle in ("sent.send_someone(j.project_id, labels[vs.LINK_B2B], SENT_MORE_DECIDER)",
                   "sent.make_new_link(SENT_MORE_DECIDER)", "(old_status, new_status) == (404, 200)",
                   '"ALREADY_ANSWERED"', 'links_reading(j, "after Send more", sent)', "name_alone_faults(made"):
        assert needle in source, needle
    assert source.index("send_someone(") < source.index("make_new_link(") < source.index("links_reading(")
    assert cs.SENT_MORE_DECIDER != cs.OUTSIDE_DECIDER


def test_one_kind_reads_no_contacts_picker():
    source = inspect.getsource(scope_journey.one_kind)
    assert "/contacts/" not in source.split('"""', 2)[2] and "Contacts(" not in source
