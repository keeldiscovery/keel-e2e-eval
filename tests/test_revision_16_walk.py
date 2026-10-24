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
