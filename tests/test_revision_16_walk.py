"""Spec 068 (keel-cloud 129, keel-web 106): the harness half after revision 16, stackless -- contract 36's occasion on the
wire (FR-5), the spoken mirror's served escapes (FR-2), the moved people's lines (FR-3) and the reads of keel-web 106's
screens (FR-4). Pages are stubs; no browser, no stack."""

from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace

from harness import vectors_screens as vsc


# ------------------------------------------------------------------------------- FR-5: contract 36 on the wire

class _Request:
    def __init__(self, method: str, url: str, body):
        self.method, self.url, self.post_data_json = method, url, body


class _Response:
    def __init__(self, url: str, status: int, sent, body=None):
        self.url, self.status, self._body = url, status, body
        self.request = _Request("PUT", url, sent)

    def json(self):
        if self._body is None:
            raise ValueError("no body")
        return self._body


class _SavePage:
    """Just enough of a page for `Corridor._save_context`: the Save button and the PUT it answers."""

    def __init__(self, response: _Response):
        self.response, self.clicked = response, []

    @contextmanager
    def expect_response(self, predicate, timeout=0):
        assert predicate(self.response)
        yield SimpleNamespace(value=self.response)

    def get_by_role(self, role, name=None, exact=True):
        return SimpleNamespace(click=lambda: self.clicked.append(name))

    def on(self, *a):
        pass


def _corridor(page) -> vsc.Corridor:
    corridor = vsc.Corridor.__new__(vsc.Corridor)
    corridor.page, corridor.saves = page, []
    return corridor


def test_the_context_put_is_recorded_with_the_occasion_it_carried():
    """Contract 36 (keel-cloud 129 FR-11): the page sends `occasion` on the PUT once the founder's field holds one; the
    harness records the fields it sent and the occasion apart, and an older body (no occasion) reads None."""
    url = "http://localhost:18080/v2/projects/p1/context"
    sent = {"actor": "a", "job": "j", "circumstance": "c", "segment": "s",
            "recallWindow": {"count": 4, "unit": "WEEKS"}, "occasion": "delivery"}
    saved = _corridor(_SavePage(_Response(url, 202, sent, {"interaction_id": "i1"})))._save_context()
    assert saved["occasion"] == "delivery" and saved["sent"] == sent and saved["interaction_id"] == "i1"
    older = dict(sent)
    older.pop("occasion")
    saved = _corridor(_SavePage(_Response(url, 202, older, {"interaction_id": "i2"})))._save_context()
    assert saved["occasion"] is None and saved["sent"] == older
    refused = _corridor(_SavePage(_Response(url, 422, sent, {"code": "TEXT_REFUSED"})))._save_context()
    assert refused["status"] == 422 and refused["body"] == {"code": "TEXT_REFUSED"} and refused["occasion"] == "delivery"


# ------------------------------------------------------------------------------- FR-2: the served escapes

def test_issens_consumer_ability_item_names_the_served_escape_and_is_clean():
    """Spec 068 FR-2 (keel-cloud 129's owed list): Issen's 2026-10-23 host-door run served Ability to pay as the
    consumer budget item with *I can't say*; the guard read the registry's *I can't recall one* and called it RED.
    The escape a consumer Ability item names is the served one; the same item on a B2B link keeps the registry's."""
    from instructions import spoken as sp                               # noqa: PLC0415
    from instructions.cloud_corpus import ComposedItem                  # noqa: PLC0415
    from tests import v9_fixtures as fx                                 # noqa: PLC0415
    registry = fx.registry()
    stem = "Could you pay about $20 a month for this from money you already spend, or not?"
    item = ComposedItem(entry="11-issen", key="commercial.ability_to_pay", part=3, question=stem,
                        options=("From money I already spend on this", "From other money I'd set aside",
                                 "I couldn't pay it"),
                        escape="I can't say", anchor=None, stem=stem, count_line="I'll read three options.",
                        options_line="From money you already spend on this; from other money you'd set aside; or "
                                     "you couldn't pay it.",
                        escape_line="Or say you can't say.", transform="none")
    consumer = SimpleNamespace(chain=lambda: True, b2b=lambda: False, founder_list=lambda key: None)
    business = SimpleNamespace(chain=lambda: True, b2b=lambda: True, founder_list=lambda key: None)
    assert sp.item_escape(registry, "commercial.ability_to_pay", consumer) == "I can't say"
    assert sp.item_faults(item, registry, consumer) == []
    assert sp.item_escape(registry, "commercial.ability_to_pay", business) == \
        sp.registry_escape(registry, "commercial.ability_to_pay") == "I can't recall one"
    assert any(f.startswith("S6") for f in sp.item_faults(item, registry, business))
