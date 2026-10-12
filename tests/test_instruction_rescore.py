"""`instructions/rescore.py` across the bumps (spec 029 FR-004, SC-004, research R11; T021; spec 030
FR-004, SC-002, judgement call 49; spec 031 SC-002, judgement call 58).

A v8 bundle holds answers to screens v9 does not have, scored against a corpus revision 3 no longer
carries; a v9 bundle answered the registry of twenty-five, and corpus revision 4 does not carry
what it measured. Each is refused in one line, by name, with the reason -- `marks_version` read
**first**, before a corpus is loaded or a file is written. A bundle at the current version is
re-read for free, and its new scorecard lands **beside** the original, never over it.
"""

from __future__ import annotations

import hashlib
import json
import shutil

from instructions import marks as marks_mod
from instructions import rescore as rescore_mod
from tests import v9_fixtures as fx


def _digests(directory):
    return {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(directory.rglob("*")) if p.is_file()}


def test_a_v8_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    bundle = tmp_path / "20261001T043420Z-instructions"
    shutil.copytree(fx.V8_BUNDLE, bundle)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))

    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261001T043420Z-instructions" in said
    assert "marks_version 8" in said
    assert "answered on screens v9 does not have, against corpus r2" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_bundle_with_no_version_at_all_is_refused_the_same_way(tmp_path):
    assert "marks_version None" in rescore_mod.refusal(tmp_path, {})


def _bundle(tmp_path, version=None):
    version = marks_mod.MARKS_VERSION if version is None else version
    bundle = tmp_path / "20261008T000000Z-instructions"
    bundle.mkdir()
    fx.write_export(bundle / "contracts")
    (bundle / "scorecard.json").write_text(json.dumps(
        {"marks_version": version, "n_runs": 1, "model": {"host": "claude"}, "totals": {}}))
    (bundle / "manifest.json").write_text(json.dumps({"host": "claude",
                                                      "marks_version": version}))
    return bundle


def test_a_v9_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """SC-002: the v9 run of record (`runs/20261008T194906Z-instructions`) and every bundle like
    it -- one line, by name, with the reason, and before the corpus is reached."""
    bundle = _bundle(tmp_path, version=9)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 9" in said
    assert "a v9 scorecard cannot be re-scored at v15" in said
    assert "corpus r4 does not carry what it measured" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_v10_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """Spec 031 SC-002, call 58: a v10 bundle answered with no Price, no units and the window in
    the model's own words -- one line, by name, before the corpus is reached."""
    bundle = _bundle(tmp_path, version=10)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 10" in said
    assert "a v10 scorecard cannot be re-scored at v15" in said
    assert "no Price, no units and the window in the model's own words" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_v11_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """Spec 032 SC-002, call 66: a v11 bundle answered a founder tick list, a Price over month / year /
    one-off and a model-written Ability to pay -- one line, by name, before the corpus is reached."""
    bundle = _bundle(tmp_path, version=11)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 11" in said
    assert "a v11 scorecard cannot be re-scored at v15" in said
    assert "a model-written Ability to pay" in said and "(WHY=marks:12)" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_v12_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """Spec 033 SC-003, call 70: a v12 bundle answered an Existing sacrifice of kinds with a unit each and a
    question held to the recall words -- one line, by name, before the corpus is reached."""
    bundle = _bundle(tmp_path, version=12)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 12" in said
    assert "a v12 scorecard cannot be re-scored at v15" in said
    assert "kinds with a unit each" in said and "(WHY=marks:13)" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_v13_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """Spec 034 SC-003, call 73: a v13 bundle answered the BRIEF screen with a `whatThisSays` paragraph --
    one line, by name, before the corpus is reached."""
    bundle = _bundle(tmp_path, version=13)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 13" in said
    assert "a v13 scorecard cannot be re-scored at v15" in said
    assert "`whatThisSays` paragraph" in said and "(WHY=marks:14)" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_v14_bundle_is_refused_by_name_and_left_untouched(tmp_path, capsys, monkeypatch):
    """Spec 036 SC-003, call 74: a v14 bundle was scored against corpus revision 7's status / drift --
    one line, by name, before the corpus is reached."""
    bundle = _bundle(tmp_path, version=14)
    before = _digests(bundle)
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: (_ for _ in ()).throw(AssertionError("the corpus was reached")))
    assert rescore_mod.main([str(bundle)]) == 2
    said = capsys.readouterr().err
    assert "20261008T000000Z-instructions was scored at marks_version 14" in said
    assert "a v14 scorecard cannot be re-scored at v15" in said
    assert "corpus revision 7's status / drift" in said and "(WHY=marks:15)" in said
    assert _digests(bundle) == before, "nothing in a refused bundle is touched"


def test_a_current_bundle_is_rescored_beside_and_never_over(tmp_path, monkeypatch, capsys):
    from types import SimpleNamespace
    bundle = _bundle(tmp_path)
    original = (bundle / "scorecard.json").read_bytes()
    # The corpus a rescore reads is the configured one; here, the hand-sized fixture entry.
    monkeypatch.setattr(rescore_mod, "load_config",
                        lambda: SimpleNamespace(keel_cloud=tmp_path / "no-keel-cloud"))
    monkeypatch.setattr(rescore_mod.corpus_mod, "load",
                        lambda keel_cloud: rescore_mod.corpus_mod.Corpus(
                            entries=[rescore_mod.corpus_mod.load_file(fx.ENTRY)],
                            directory=fx.ENTRY.parent))

    assert rescore_mod.main([str(bundle), "--no-judge"]) == 0
    assert (bundle / "scorecard.json").read_bytes() == original, "never over"
    written = json.loads((bundle / f"scorecard-v{marks_mod.MARKS_VERSION}.json").read_text())
    assert written["marks_version"] == written["rescored_from"] == marks_mod.MARKS_VERSION == 15
    assert written["totals"]["compare_measured"] is False, \
        "a bundle with no engine input re-measures no compare"
    assert "re-scored" in capsys.readouterr().out
