"""The door judge against canned readings (spec 007-every-door FR-004) -- no browser."""

from __future__ import annotations

from harness import doors


def test_normalise_keeps_only_the_user_code_query_and_drops_fragments() -> None:
    base = "http://localhost:5174"
    assert doors.normalise("/p/abc#top", base) == "http://localhost:5174/p/abc"
    assert doors.normalise("/connect?user_code=ABCD-EFGH&x=1", base) == "http://localhost:5174/connect?user_code=ABCD-EFGH"
    assert doors.normalise("/people/", base) == "http://localhost:5174/people"
    assert doors.normalise("https://example.org/docs", base) == "https://example.org/docs"


def test_normalise_ignores_non_navigations() -> None:
    base = "http://localhost:5174"
    for href in ("", "#", "javascript:void(0)", "mailto:x@y.z", "tel:123", None):
        assert doors.normalise(href, base) is None


def test_external_is_by_host() -> None:
    base = "http://localhost:5174"
    assert doors.is_external("https://example.org/", base)
    assert not doors.is_external("http://localhost:5174/p/abc", base)


def test_route_of_matches_the_route_table() -> None:
    assert doors.route_of("/") == "/"
    assert doors.route_of("/p/abc") == "/p/:id"
    assert doors.route_of("/p/abc/s/PROBLEM") == "/p/:id/s/:stage"
    assert doors.route_of("/p/abc/invitations") == "/p/:id/invitations"
    assert doors.route_of("/i/tok") == "/i/:token"
    assert doors.route_of("/p/abc/nope") is None


def test_judge_not_found_page() -> None:
    v = doors.judge(body_text="Keel\nThis page doesn't exist.", main_text=None, statuses=[])
    assert v.verdict == "not_found"
    v = doors.judge(body_text="Keel\nThis page doesn’t exist.", main_text=None, statuses=[])
    assert v.verdict == "not_found"


def test_judge_blank_main_pane_inside_the_shell() -> None:
    v = doors.judge(body_text="Keel · Payroll Exceptions\nOverview\nThe problem", main_text="  \n",
                    statuses=[{"url": "http://x/v2/me", "status": 200}])
    assert v.verdict == "blank"


def test_judge_a_screen_inside_the_shell_opens() -> None:
    v = doors.judge(body_text="Keel\nOverview", main_text="Where it stands", statuses=[])
    assert v.verdict == "opens"


def test_judge_failed_wire_request_is_d3_but_favicon_is_not() -> None:
    v = doors.judge(body_text="x", main_text="y",
                    statuses=[{"url": "http://x/v2/projects/1", "status": 500}])
    assert v.verdict == "failed_request" and "500" in v.detail
    v = doors.judge(body_text="x", main_text="y",
                    statuses=[{"url": "http://x/favicon.ico", "status": 404}])
    assert v.verdict == "opens"
    assert doors.resource_misses([{"url": "http://x/favicon.ico", "status": 404}])


def test_judge_allows_the_logged_out_401_only_when_asked() -> None:
    statuses = [{"url": "http://x/v2/me", "status": 401}]
    assert doors.judge(body_text="Log in", main_text=None, statuses=statuses, allow_401=True).verdict == "opens"
    assert doors.judge(body_text="Log in", main_text=None, statuses=statuses).verdict == "failed_request"


def test_judge_a_bare_page_with_no_text_is_blank() -> None:
    assert doors.judge(body_text="   ", main_text=None, statuses=[]).verdict == "blank"


def test_tally_reports_unreached_routes_without_failing() -> None:
    base = "http://localhost:5174"
    found = [
        doors.Door(source="/", href=f"{base}/p/abc", text="Payroll Exceptions", external=False),
        doors.Door(source="/p/abc", href=f"{base}/p/abc/people", text="People", external=False),
        doors.Door(source="/p/abc", href="https://example.org/", text="docs", external=True),
    ]
    t = doors.tally(found, base=base)
    assert t["reached"]["/p/:id"] == ["/"]
    assert t["reached"]["/p/:id/people"] == ["/p/abc"]
    assert "/p/:id/brief" in t["unreached"]
    rows = doors.rows(found, {f"{base}/p/abc": doors.Verdict("opens", "ok")})
    assert rows[0]["verdict"] == "opens" and rows[1]["verdict"] == "skipped" and rows[2]["route"] is None


def test_judge_a_404_the_screen_turns_into_not_found_is_d1_not_d3() -> None:
    statuses = [{"url": "http://x/v2/i/nope", "status": 404}]
    v = doors.judge(body_text="This page doesn't exist.", main_text=None, statuses=statuses)
    assert v.verdict == "not_found"
    # but a 404 the screen hides is still D3
    v = doors.judge(body_text="Keel", main_text="Overview", statuses=statuses)
    assert v.verdict == "failed_request"
