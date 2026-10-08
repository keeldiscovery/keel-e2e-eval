"""`instructions/rescore.py` across the bump (spec 029 FR-004, SC-004, research R11; T021).

A v8 bundle holds answers to screens v9 does not have, scored against a corpus revision 3 no longer
carries. It is refused in one line, by name, with the reason -- `marks_version` read **first**,
before a corpus is loaded or a file is written. A v9 bundle is re-read for free, and its new
scorecard lands **beside** the original, never over it.
"""

from __future__ import annotations

import hashlib
import json
import shutil

from instructions import marks as marks_mod
from instructions import rescore as rescore_mod
from tests import v9_fixtures as fx


def _digests(directory):
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}


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


def _v9_bundle(tmp_path):
    bundle = tmp_path / "20261008T000000Z-instructions"
    bundle.mkdir()
    fx.write_export(bundle / "contracts")
    (bundle / "scorecard.json").write_text(json.dumps(
        {"marks_version": 9, "n_runs": 1, "model": {"host": "claude"}, "totals": {}}))
    (bundle / "manifest.json").write_text(json.dumps({"host": "claude", "marks_version": 9}))
    return bundle


def test_a_v9_bundle_is_rescored_beside_and_never_over(tmp_path, monkeypatch, capsys):
    from types import SimpleNamespace
    bundle = _v9_bundle(tmp_path)
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
    assert written["marks_version"] == 9 and written["rescored_from"] == 9
    assert written["totals"]["compare_measured"] is False, \
        "a bundle with no engine input re-measures no compare"
    assert "re-scored" in capsys.readouterr().out
