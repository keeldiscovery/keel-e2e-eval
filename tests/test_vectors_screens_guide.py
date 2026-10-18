"""Spec 054 FR-1 / FR-6: keel-web 080's welcome as the harness acts on it, over a stub page (no browser in `make unit`):
`MarketStep.start`'s pass-by with and without the sheet (and `hold`, which leaves it up), `GuideWelcome`'s presses and
reads, `GuideWire`'s sorting of what the page sent, and the six test ids against keel-web where it carries 080."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from harness import vectors_screens as vs
from harness.browser import MarketStep
from harness.steps import Recorder
from stack.config import load_config

CLOUD = "http://localhost:8080"
WEB = "http://localhost:5173"


class _Response:
    def __init__(self, method: str, url: str, status: int = 200, body=None):
        self.url, self.status, self._body = url, status, body
        self.request = _Request(method, url, response=self)

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body


class _Request:
    def __init__(self, method: str, url: str, body=None, response=None):
        self.method, self.url, self.post_data_json, self.post_data = method, url, body, None
        self._response = response

    def response(self):
        return self._response


class _Timeout(Exception):
    pass


class _Locator:
    def __init__(self, page: "_Page", selector: str):
        self.page, self.selector = page, selector

    @property
    def first(self):
        return self

    def _there(self) -> bool:
        p = self.page
        return {vs.GUIDE_WELCOME: p.sheet, vs.GUIDE_SKIP: p.sheet, vs.GUIDE_REPLAY: p.panel,
                vs.FEEDBACK_TRIGGER: True, vs.PROJECT_SCREEN: True, "role:start": True}.get(self.selector, False)

    def count(self) -> int:
        return int(self._there())

    def is_visible(self) -> bool:
        return self._there()

    def wait_for(self, state: str = "visible", timeout: float = 0) -> None:
        if (state in ("visible", "attached")) != self._there():
            raise _Timeout(f"{self.selector} never {state}")

    def click(self) -> None:
        p = self.page
        p.clicks.append(self.selector)
        if self.selector == "role:start":
            p.url = f"{WEB}/p/abc/define/context"
            p.emit("response", _Response("POST", f"{CLOUD}/v2/projects", 201, {"id": "abc"}))
            body = {"revision": 1} if p.guide is None else {"revision": 1, "guide": p.guide}
            p.emit("response", _Response("GET", f"{CLOUD}/v2/projects/abc/overview", 200, body))
            p.sheet = p.offers_sheet
        elif self.selector == vs.GUIDE_SKIP:
            p.close(post=not p.replaying)
        elif self.selector == vs.FEEDBACK_TRIGGER:
            p.panel = True
        elif self.selector == vs.GUIDE_REPLAY:
            p.panel, p.sheet, p.replaying = False, True, True


class _Keyboard:
    def __init__(self, page):
        self.page = page

    def press(self, key: str) -> None:
        if key == "Escape" and self.page.sheet:
            self.page.close(post=not self.page.replaying)


class _Page:
    def __init__(self, *, guide=None, offers_sheet=False, sheet=False):
        self.url = f"{WEB}/"
        self.guide, self.offers_sheet, self.sheet = guide, offers_sheet, sheet
        self.panel = self.replaying = False
        self.listeners: dict[str, list] = {}
        self.clicks: list[str] = []
        self.keyboard = _Keyboard(self)
        self.evaluated: list = []

    # events
    def on(self, event, fn):
        self.listeners.setdefault(event, []).append(fn)

    def remove_listener(self, event, fn):
        self.listeners[event].remove(fn)

    def emit(self, event, obj):
        for fn in list(self.listeners.get(event, [])):
            fn(obj)

    def wait_for_event(self, event, predicate=None, timeout=0):
        raise _Timeout(event)

    def wait_for_timeout(self, ms):
        pass

    # the page
    def close(self, *, post: bool) -> None:
        self.sheet = False
        self.replaying = False
        if post:
            url = f"{CLOUD}/v2/projects/abc/guide-seen"
            self.emit("request", _Request("POST", url, {"what": "WELCOME"},
                                          _Response("POST", url, 204)))

    def locator(self, selector: str):
        return _Locator(self, selector)

    def get_by_role(self, role, name=None):
        return _Locator(self, "role:start")

    def evaluate(self, script, arg=None):
        self.evaluated.append((script, arg))
        if script is vs._SKIP_JS:
            return {"present": True, "visible": True, "enabled": True, "in_view": True, "hit": True}
        if script is vs._CONTROLS_JS:
            return [{"tag": "button", "testid": "guide-skip", "words": "Skip ›", "label": None}]
        return None

    def screenshot(self, **kwargs):
        pass

    def content(self):
        return ""


def _steps(recorder: Recorder) -> list[dict]:
    return list(recorder._records)


def _listening(page: _Page) -> dict:
    return {k: len(v) for k, v in page.listeners.items() if k != "console" and v}


# -------------------------------------------------------------------------------------------- the pass-by

def test_the_pass_by_skips_a_welcome_that_comes_in_one_note_step(tmp_path):
    page = _Page(guide={"welcomeSeen": False, "openersSeen": []}, offers_sheet=True)
    recorder = Recorder(tmp_path)
    assert MarketStep(page, recorder, WEB).start() == "abc"
    assert page.sheet is False and page.clicks == ["role:start", vs.GUIDE_SKIP]
    notes = [s for s in _steps(recorder) if s["kind"] == "note"]
    assert len(notes) == 1 and "passes it by with Skip" in notes[0]["name"], notes
    assert notes[0]["response"]["shown"] is True
    assert notes[0]["response"]["requests"] == [{"method": "POST", "path": f"{CLOUD}/v2/projects/abc/guide-seen",
                                                 "body": {"what": "WELCOME"}, "status": 204}]
    assert _listening(page) == {}, "the pass-by's listeners are taken off"


@pytest.mark.parametrize("guide", [{"welcomeSeen": True, "openersSeen": []}, None])
def test_the_pass_by_does_not_wait_where_no_welcome_is_due(tmp_path, guide):
    page = _Page(guide=guide, offers_sheet=False)
    recorder = Recorder(tmp_path)
    started = time.monotonic()
    assert MarketStep(page, recorder, WEB).start() == "abc"
    assert time.monotonic() - started < 1.0
    assert page.clicks == ["role:start"]
    assert not [s for s in _steps(recorder) if s["kind"] == "note"]
    assert _listening(page) == {}


def test_a_welcome_that_was_due_but_never_came_is_not_a_failure(tmp_path):
    page = _Page(guide={"welcomeSeen": False, "openersSeen": []}, offers_sheet=False)
    recorder = Recorder(tmp_path)
    assert MarketStep(page, recorder, WEB).start() == "abc"
    assert page.clicks == ["role:start"]
    assert all(s["ok"] for s in _steps(recorder))


def test_hold_leaves_the_welcome_up_for_the_leg(tmp_path):
    page = _Page(guide={"welcomeSeen": False, "openersSeen": []}, offers_sheet=True)
    recorder = Recorder(tmp_path)
    assert MarketStep(page, recorder, WEB).start(welcome="hold") == "abc"
    assert page.sheet is True and page.clicks == ["role:start"]
    assert _listening(page) == {}


def test_welcome_is_pass_or_hold(tmp_path):
    with pytest.raises(ValueError):
        MarketStep(_Page(), Recorder(tmp_path), WEB).start(welcome="watch")


def test_create_project_forwards_welcome():
    import inspect
    from evals import preludes
    signature = inspect.signature(preludes.create_project)
    assert signature.parameters["welcome"].default == "pass"
    assert "market.start(welcome=welcome)" in inspect.getsource(preludes.create_project)


# --------------------------------------------------------------------------------------------- the sheet

def test_skip_and_escape_return_the_requests_they_caused(tmp_path):
    for press in ("skip", "escape"):
        page = _Page(sheet=True)
        guide = vs.GuideWelcome(page, Recorder(tmp_path / press), WEB)
        out = getattr(guide, press)()
        assert out["door"] == press and isinstance(out["gone_ms"], int)
        assert [(r["method"], r["body"], r["status"]) for r in out["requests"]] == [("POST", {"what": "WELCOME"}, 204)]
        assert page.sheet is False and _listening(page) == {}


def test_a_sheet_that_never_goes_reads_as_none(tmp_path):
    page = _Page(sheet=True)
    page.keyboard = type("K", (), {"press": lambda self, key: None})()
    out = vs.GuideWelcome(page, Recorder(tmp_path), WEB).escape()
    assert out == {"door": "escape", "gone_ms": None, "requests": []}


def test_replay_opens_the_feedback_panel_first_and_posts_nothing(tmp_path):
    page = _Page()
    guide = vs.GuideWelcome(page, Recorder(tmp_path), WEB)
    opened = guide.replay()
    assert opened == {"found": True, "via": "the Feedback panel", "opened": True, "requests": []}
    assert page.clicks == [vs.FEEDBACK_TRIGGER, vs.GUIDE_REPLAY]
    closed = guide.skip()
    assert closed["requests"] == [] and closed["gone_ms"] is not None


def test_replay_presses_guide_replay_directly_when_it_is_visible(tmp_path):
    page = _Page()
    page.panel = True
    assert vs.GuideWelcome(page, Recorder(tmp_path), WEB).replay()["via"] == "guide-replay"
    assert page.clicks == [vs.GUIDE_REPLAY]


def test_the_reads_are_one_evaluate_each(tmp_path):
    page = _Page(sheet=True)
    guide = vs.GuideWelcome(page, Recorder(tmp_path), WEB)
    assert guide.skip_in_view()["in_view"] is True
    assert guide.controls()[0]["testid"] == "guide-skip"
    assert [arg for _, arg in page.evaluated] == [vs.GUIDE_SKIP, vs.GUIDE_WELCOME]


def test_absent_reads_after_the_overview_and_the_first_screen(tmp_path):
    page = _Page()

    def open_seen():
        page.emit("response", _Response("GET", f"{CLOUD}/v2/projects/abc/overview", 200,
                                        {"revision": 1, "guide": {"welcomeSeen": True, "openersSeen": []}}))

    got = vs.GuideWelcome(page, Recorder(tmp_path), WEB).absent(after=open_seen)
    assert got["count"] == 0 and got["screen"] is True and got["overviews"] == 1
    assert got["received"] == {"welcomeSeen": True, "openersSeen": []}
    assert _listening(page) == {}


def test_absent_counts_a_sheet_that_came_back(tmp_path):
    page = _Page()

    def open_unseen():
        page.emit("response", _Response("GET", f"{CLOUD}/v2/projects/abc/overview", 200,
                                        {"revision": 1, "guide": {"welcomeSeen": False, "openersSeen": []}}))
        page.sheet = True

    got = vs.GuideWelcome(page, Recorder(tmp_path), WEB).absent(after=open_unseen)
    assert got["count"] == 1 and got["received"]["welcomeSeen"] is False


def test_the_wire_sorts_what_the_page_sent(tmp_path):
    page = _Page()
    wire = vs.GuideWire(page).attach()
    page.emit("response", _Response("POST", f"{CLOUD}/v2/projects", 201, {"id": "abc"}))
    page.emit("response", _Response("GET", f"{CLOUD}/v2/projects/abc/overview", 200,
                                    {"revision": 3, "guide": {"welcomeSeen": False, "openersSeen": []}}))
    page.emit("response", _Response("PUT", f"{CLOUD}/v2/projects/abc/context", 202, {}))   # before the mark
    page.close(post=True)
    page.emit("response", _Response("POST", f"{CLOUD}/v2/projects/abc/guide-seen", 204))      # not a write
    page.emit("response", _Response("GET", f"{CLOUD}/v2/projects/abc/plan", 200, {}))          # a read
    page.emit("response", _Response("PUT", f"{CLOUD}/v2/projects/abc/context?x=1", 202, {}))
    wire.detach()
    assert wire.received() == {"welcomeSeen": False, "openersSeen": []}
    assert wire.overviews() == [{"guide": {"welcomeSeen": False, "openersSeen": []}, "revision": 3, "status": 200}]
    assert [p["body"] for p in wire.guide_posts()] == [{"what": "WELCOME"}]
    assert wire.writes_after_guide() == [{"method": "PUT", "path": f"{CLOUD}/v2/projects/abc/context",
                                          "status": 202}]
    assert _listening(page) == {}


def test_the_corridor_frame_counts_the_sheet():
    import inspect
    assert '"welcome": self.page.locator(GUIDE_WELCOME).count()' in inspect.getsource(vs.Corridor.frame)


# ------------------------------------------------------------------------------------------ against keel-web

@pytest.mark.parametrize("testid", ["guide-welcome", "guide-face", "guide-caption", "guide-snippet", "guide-skip",
                                    "guide-replay"])
def test_every_guide_selector_is_in_keel_web(testid):
    root = load_config(validate=False).keel_web / "src"
    if not (root / "components" / "guide").is_dir():
        pytest.skip("keel-web predates spec 080")
    hits = [p for p in root.rglob("*.tsx") if f'data-testid="{testid}"' in p.read_text(encoding="utf-8")]
    assert hits, testid
    assert f"'{testid}'" in Path(vs.__file__).read_text(encoding="utf-8")


def test_the_feedback_trigger_is_keel_webs_own():
    source = load_config(validate=False).keel_web / "src" / "components" / "FeedbackTab.tsx"
    if not source.is_file():
        pytest.skip("no FeedbackTab in this keel-web")
    text = source.read_text(encoding="utf-8")
    assert 'className="fb-tab pbar__fb"' in text and 'aria-haspopup="dialog"' in text
