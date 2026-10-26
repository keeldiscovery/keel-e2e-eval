"""Spec 073 FR-4: the welcome per scope (keel-web 114 FR-1) -- the clip key the sheet draws as `data-clip`, read off
keel-web's markup in a real page, kept by the pass every scoped journey makes, and held on S-015 / S-016; under ALL the
key stays `welcome`."""

from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from playwright.sync_api import sync_playwright

from evals import corpus_scenario as cs
from evals import guide_marks as marks
from harness import vectors_screens as vs
from harness.steps import Recorder
from stack.config import load_config


@pytest.fixture(scope="module")
def browser():
    with sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


def _sheet(key: str) -> str:
    return (f'<div data-testid="guide-welcome" data-clip="{key}" role="dialog">'
            f'<video data-testid="guide-face" src="/guide/{key}.mp4" poster="/guide/{key}.jpg" muted>'
            f'<track kind="captions" src="/guide/{key}.vtt"></video>'
            '<button data-testid="guide-skip">Skip ›</button></div>')


@pytest.mark.parametrize("scope, key", [("ALL", "welcome"), (None, "welcome"), ("PROBLEM", "welcome-problem"),
                                        ("SOLUTION", "welcome-solution"),
                                        ("SOLUTION_COMMERCIAL", "welcome-solution-money"),
                                        ("COMMERCIAL", "welcome-money")])
def test_the_clip_key_per_scope_is_keel_web_114s(scope, key):
    assert marks.welcome_clip(scope) == key


def test_the_sheets_clip_and_files_are_read_as_drawn(tmp_path, browser):
    page = browser.new_page()
    try:
        page.set_content(_sheet("welcome-money"))
        got = vs.GuideWelcome(page, Recorder(tmp_path)).clip()
        assert got == {"clip": "welcome-money", "src": "/guide/welcome-money.mp4",
                       "poster": "/guide/welcome-money.jpg", "track": "/guide/welcome-money.vtt"}
        page.set_content("<main></main>")
        assert vs.GuideWelcome(page, Recorder(tmp_path)).clip() == {"clip": None, "src": None, "poster": None,
                                                                     "track": None}
    finally:
        page.close()


class _Step:
    def __init__(self):
        self.asserted = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def record_assert(self, want, got):
        self.asserted = (want, got)


def _journey(scope: str, passed: dict) -> SimpleNamespace:
    return SimpleNamespace(scope=scope, changed={"welcome_pass": passed}, strict=True)


def _passed(key: str, **over) -> dict:
    return {"shown": True, "clip": key, "src": f"/guide/{key}.mp4", "poster": f"/guide/{key}.jpg",
            "track": f"/guide/{key}.vtt", **over}


@pytest.fixture
def steps(monkeypatch):
    monkeypatch.setattr(cs, "_step", lambda *a, **k: _Step())


@pytest.mark.parametrize("scope", ["PROBLEM", "COMMERCIAL"])
def test_s015_and_s016_hold_their_scopes_clip(steps, scope):
    cs.hold_the_welcome_clip(_journey(scope, _passed(marks.welcome_clip(scope))))


@pytest.mark.parametrize("scope, passed", [
    ("PROBLEM", _passed("welcome")),                                  # the whole study's clip on a problem study
    ("COMMERCIAL", _passed("welcome-problem")),                       # another scope's
    ("PROBLEM", _passed("welcome-problem", src="/guide/welcome.mp4")),  # the key right, the face the whole study's
    ("COMMERCIAL", _passed("welcome-money", track="/guide/welcome.vtt")),
    ("PROBLEM", {"shown": False}),                                    # no sheet came
    ("PROBLEM", {}),                                                  # no pass recorded
])
def test_a_scoped_welcome_that_is_not_the_scopes_fails(steps, scope, passed):
    with pytest.raises(AssertionError):
        cs.hold_the_welcome_clip(_journey(scope, passed))


def test_every_scoped_journey_holds_the_clip_after_the_project():
    import inspect

    from evals import scope_journey
    source = inspect.getsource(scope_journey.run)
    assert source.index("cs.leg_project(j)") < source.index("cs.hold_the_welcome_clip(j)") < source.index("walk(j)")


def test_the_four_scoped_clips_are_in_keel_webs_manifest_with_their_files():
    guide = load_config(validate=False).keel_web / "public" / "guide"
    manifest = guide / "manifest.json"
    if not manifest.is_file():
        pytest.skip("keel-web predates spec 086 (no manifest)")
    keys = set(vs.normal_manifest(json.loads(manifest.read_text(encoding="utf-8"))))
    scoped = [marks.welcome_clip(s) for s in ("PROBLEM", "SOLUTION", "SOLUTION_COMMERCIAL", "COMMERCIAL")]
    if not set(scoped) <= keys:
        pytest.skip("keel-web predates spec 114 (no scoped welcome)")
    for key in scoped:
        assert all((guide / f"{key}.{ext}").is_file() for ext in ("mp4", "vtt", "jpg")), key
    assert all((guide / f"welcome.{ext}").is_file() for ext in ("mp4", "vtt", "jpg"))      # ALL's, unchanged
