"""The shared discourse stoplist is keel-cloud 058's `LeakStems.DISCOURSE_STOPLIST`, word for word
(2026-10-08): the mark and the runtime's R4 drop the same connective prose."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from instructions import text as text_mod

LEAK_STEMS = (Path("src") / "main" / "java" / "com" / "keeldiscovery" / "cloud" / "domain"
              / "vectors" / "LeakStems.java")


def _cloud_list():
    try:
        from stack.config import load_config                    # noqa: PLC0415
        path = Path(load_config().keel_cloud) / LEAK_STEMS
    except Exception:                                           # noqa: BLE001 - no sibling here
        path = None
    if path is None or not path.is_file():
        pytest.skip("keel-cloud 058's LeakStems.java is not checked out here")
    source = path.read_text(encoding="utf-8")
    match = re.search(r"DISCOURSE_STOPLIST\s*=\s*List\.of\((.*?)\);", source, re.S)
    assert match, "058 keeps DISCOURSE_STOPLIST in LeakStems"
    return tuple(re.findall(r'"([^"]+)"', match.group(1)))


def test_the_discourse_stoplist_is_058s_word_for_word():
    assert text_mod.DISCOURSE_STOPLIST == _cloud_list()


def test_the_discourse_words_are_never_content_words():
    assert text_mod.content_words("What happened as a result, one way or another, in the end?") \
        == ["happened", "another"]
