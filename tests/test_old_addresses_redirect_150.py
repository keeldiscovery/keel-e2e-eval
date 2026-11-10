"""Spec 150 FR-3 (keel-web 185 FR-1): a journey that opens `/interviews/contacts` or `/interviews/managed` (and a
dataset under Contacts, and `/interviews/keel-managed`) lands on `/interviews/sent`, the query dropped.

The harness has no route-pin pattern and no journey dry mode (a journey needs a stack), so the redirect is held three
ways at zero spend: the journey step itself (`corpus_scenario.leg_old_addresses`, S-005's extra where its NOT_B2B
refusal stood) run here against a page double that redirects as keel-web's router does -- and fails by name on one that
does not; the addresses it opens pinned to keel-web's own `AppRoutes.tsx` (each a `Navigate ... replace` to Sent with no
query carried); and S-005 calling it."""

from __future__ import annotations

import re
from pathlib import Path
from types import SimpleNamespace

import pytest

from evals import corpus_scenario as cs
from harness import interviews_screens as iv
from stack.config import load_config

REPO = Path(__file__).resolve().parent.parent
WEB = load_config(validate=False).keel_web
BASE = "http://localhost:5173"
PROJECT = "7f0c"


class _Locator:
    def __init__(self, page, selector):
        self.page, self.selector = page, selector

    @property
    def first(self):
        return self

    def wait_for(self, **_):
        return None

    def count(self):
        return 1 if self.selector == ".sent__kinds" and self.page.on_sent() else 0


class _Router:
    """A page double: `goto` lands where keel-web's router sends the address -- an old sub-page to Sent with the query
    dropped (`redirects`), or nowhere new (`redirects=False`, a web before 185 drawing the old page)."""

    def __init__(self, *, redirects: bool = True, keeps_query: bool = False):
        self.url, self.asked = "", []
        self.redirects, self.keeps_query = redirects, keeps_query

    def on_sent(self) -> bool:
        return bool(re.search(r"/interviews/sent(?:[?#]|$)", self.url))

    def goto(self, url, **_):
        self.asked.append(url)
        path, _, query = url.partition("?")
        m = re.match(r"^(.*/p/[^/]+/interviews)/(contacts(?:/[^/?#]+)?|managed|keel-managed)$", path)
        if m and self.redirects:
            self.url = f"{m.group(1)}/sent" + (f"?{query}" if self.keeps_query and query else "")
        else:
            self.url = url

    def locator(self, selector):
        return _Locator(self, selector)

    def wait_for_url(self, pattern, **_):
        if not re.search(pattern, self.url):
            raise AssertionError(f"never reached {pattern.pattern}: {self.url}")


class _Step:
    def __init__(self, steps):
        self.steps = steps

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def record_assert(self, want, got):
        self.steps.append((want, got))


def _journey(page) -> SimpleNamespace:
    return SimpleNamespace(page=page, recorder=None, web_base=BASE, project_id=PROJECT, patience=1.0, guide={})


@pytest.fixture
def stepped(monkeypatch):
    steps: list = []
    monkeypatch.setattr(cs, "_step", lambda j, title, **kw: _Step(steps))
    monkeypatch.setattr(iv.Interviews, "pass_sheet", lambda self: {"shown": False})
    monkeypatch.setattr(iv, "_BrowserStep", lambda recorder, page, party: None)
    return steps


def test_the_old_addresses_land_on_sent_the_query_dropped(stepped):
    page = _Router()
    landed = cs.leg_old_addresses(_journey(page))
    sent = f"{BASE}/p/{PROJECT}/interviews/sent"
    assert list(landed) == list(iv.REDIRECTED) == ["contacts", "contacts/{dataset}", "managed", "keel-managed"]
    assert {sub: got["landed"] for sub, got in landed.items()} == {sub: sent for sub in iv.REDIRECTED}
    assert all(got["drew"] == "sent" for got in landed.values()), landed
    asked = [a.split(f"/p/{PROJECT}/interviews/", 1)[1] for a in page.asked]
    assert asked == ["contacts?view=names", "contacts/old-dataset?send=COMMERCIAL_B2B&dataset=old",
                     "managed?from=nav", "keel-managed?from=nav"]              # each opened with a query
    assert len(stepped) == 1 and stepped[0][0] == {sub: f"/p/{PROJECT}/interviews/sent" for sub in iv.REDIRECTED}


def test_a_query_carried_to_sent_is_named(stepped):
    with pytest.raises(AssertionError) as raised:
        cs.leg_old_addresses(_journey(_Router(keeps_query=True)))
    assert "view=names" in str(raised.value) and "contacts" in str(raised.value)


def test_an_old_page_still_drawn_is_named(stepped):
    with pytest.raises(AssertionError, match="never reached"):
        cs.leg_old_addresses(_journey(_Router(redirects=False)))


def test_s005_opens_the_old_addresses():
    source = (REPO / "evals" / "test_s005_countly.py").read_text(encoding="utf-8")
    assert "corpus_scenario.leg_old_addresses(j)" in source
    assert source.index("corpus_scenario.leg_old_addresses(j)") < source.index("interviewer_leg.leg_interviewer_short(j)")


def test_the_addresses_are_keel_webs_redirects():
    """keel-web 185's `AppRoutes.tsx`: each old sub-page a `Navigate` to `/p/{id}/interviews/sent`, `replace`, carrying no
    `location.search` (the query is dropped)."""
    path = WEB / "src/routes/AppRoutes.tsx"
    if not path.is_file():
        pytest.skip("keel-web has no src/routes/AppRoutes.tsx")
    routes = path.read_text(encoding="utf-8")
    if 'path="interviews/managed"' not in routes:
        pytest.skip("keel-web predates spec 185 (Keel-managed still a page, no redirect)")
    for sub in iv.REDIRECTED:
        route = f'path="interviews/{sub.replace("{dataset}", ":datasetId")}"'
        line = next((ln for ln in routes.splitlines() if route in ln), "")
        assert "<Navigate to={`/p/${projectId}/interviews/sent`} replace />" in line, (sub, line)
        assert "search" not in line, line
    assert 'path="interviews/sent" element={<InterviewsRoute' in routes
