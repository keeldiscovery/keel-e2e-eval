"""`instructions/judge.py`: the judge answers at the CLI's own default, whatever the subject is set to.

The judge is this repo's ruler. A run that shops a model or an effort level asks for it through the
environment — `CLAUDE_CODE_EFFORT_LEVEL` is the form keel-runtime's `_build_env` allow-lists through
to the CLI — and `subprocess.run` with no `env=` inherits the whole parent environment. So before
this test the judge would have scored a run at whatever effort the subject was launched with, and
nothing in the bundle would have said so (keel-cloud `canon/drafts/effort-high-vs-xhigh-2026-09-29.md`
§3, the seventh confound). These two tests are the ones that fail if that `env=` is ever dropped
again.
"""

from __future__ import annotations

from instructions import judge as judge_mod


def test_the_subjects_effort_never_reaches_the_judges_environment():
    environ = {"PATH": "/usr/bin", "HOME": "/home/founder",
               "CLAUDE_CODE_EFFORT_LEVEL": "medium",
               "CLAUDE_CODE_ALWAYS_ENABLE_EFFORT": "1",
               "CLAUDE_CODE_MAX_EFFORT_REMINDER": "1"}
    passed = judge_mod.judge_env(environ)
    for name in judge_mod.JUDGE_UNSET_ENV:
        assert name not in passed, f"{name} would have moved the scorer with the subject"
    # Stripped, never overridden: there is no value that means "the CLI's default".
    assert passed == {"PATH": "/usr/bin", "HOME": "/home/founder"}, \
        "everything else is passed through -- a judge that cannot authenticate answers None to " \
        "every question and quietly costs the run its recall"


def test_every_judge_call_is_given_an_explicit_environment(monkeypatch):
    """Not just that the helper is right: that `_ask` actually uses it."""
    seen = {}

    class _Done:
        stdout = '{"is_error": false, "result": "SAME"}'

    def _fake_run(argv, **kwargs):
        seen["argv"] = argv
        seen["kwargs"] = kwargs
        return _Done()

    monkeypatch.setattr(judge_mod.subprocess, "run", _fake_run)
    monkeypatch.setattr(judge_mod.shutil, "which", lambda _name: "/usr/local/bin/claude")
    monkeypatch.setenv("CLAUDE_CODE_EFFORT_LEVEL", "medium")

    assert judge_mod.Judge().same_expected_option("about an hour", "roughly 60 minutes") is True
    assert "env" in seen["kwargs"], "a judge call with no env= inherits the subject's effort"
    assert "CLAUDE_CODE_EFFORT_LEVEL" not in seen["kwargs"]["env"]
    assert seen["kwargs"]["env"].get("PATH"), "the CLI still has to be findable"
