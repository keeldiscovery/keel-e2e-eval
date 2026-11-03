"""Spec 130 FR-1..FR-3: the three sharing journeys (keel-cloud 201, contract 58; keel-web 163), on the twin.

Each starts from a **fresh owner account with one project at the answers stage**: S-016's money-alone study, walked
strict to its scored Overview (`evals/scope_journey.run` with `money_entry`, the scripted runtime on the owner's own AI
-- so it has an Overview, Insights, a Pilot view, the COMMERCIAL stage page and a brief), then the sharing leg on that
finished project, in the same bundle (`after`):

* **S-018, the link** (`link`): FR-3's pager first -- five more projects of the owner's own (`POST /v2/projects`), so
  *My projects · 6* pages as *Page 1 of 2* (on the twin; a local founder of many runs reads its own count) and *Next*
  reads *Page 2 of 2*. Then *Share* -> *The Overview* -> the link switched on; the url read off the box, the control's
  line *link on*, the wire's `SharingState.link`. A stranger -- a fresh browser context, no sign-in -- opens
  `/s/{token}`: the brand row reads *{Project} (shared by {firstName}) · {market}*, the Overview, Insights and Pilot
  views draw, the COMMERCIAL stage page draws its rows, the brief prints; no Share control, Interviews greyed; on the
  wire the root's `sharedBy.firstName` is the owner's, `access` LINK, no respondent's name and no person's email or link
  anywhere, Interviews (`/v2/s/{token}/invitations`) and every write (`POST /v2/s/{token}/overview`) the bare 404, the
  owner's own routes 401. The owner switches the link off on *Who has it*: the stranger's page reads *This link is no
  longer shared.* and the root is the bare 404; switched on again with `rotate` the old token stays 404 and the new
  one opens; the link is left off.
* **S-019, a viewer** (`viewer`): the owner's address and a non-email refused inline on the sheet (nothing sent), the
  viewer named (*1 can view*), and a second project of the owner's shared with them too (on the wire), so the search
  has something to narrow. The viewer signs in (their own fresh context, Keel's door), finds *Overviews shared with me
  · 2*, searches by the owner's name (*2 of 2*), by the project's name (*1 of 2*), by nothing anyone is called (*0 of
  2*, *No project matches that.*), opens the project: the brand row as on the link, no Share, Interviews greyed, *Try
  Keel*; on the wire `access` VIEWER, `sharedBy`, no credits, no respondent's name; Interviews, a write and the owner's
  sharing routes refused (404, 404, 403). The owner removes them on *Who has it*: the row is gone from their list and
  the project is the bare 404 to them.
* **S-020, a co-founder** (`co_founder`): before the lock the owner names a co-founder (on the wire: the Share control
  sits on the Overview, which a project before its lock does not draw); the co-founder signs in, finds it under
  *Projects shared with me*, and **edits a Check row** (Purchase friction's third step reworded and saved, then put back
  as the founder typed it, so the strict walk goes on on its own words) -- each save landing at a new revision, as the
  owner's would; the owner locks and the walk reaches the answers. Then the co-founder sends a link (`POST
  invitations`, one text link) and it is begun: the co-founder's credits never move; the credits line the co-founder
  reads (`Overview.credits`) is the owner's balance; **on Keel's door the owner's balance falls by the INTERVIEW row**
  (the owner here is on their own AI, which is never charged and serves no credits -- held as such, and named in the
  step); the co-founder has no Share control and is refused 403 on every sharing route. The owner's sheet reads *1 works
  on it* with the co-founder's chip.

**Run against staging by the coordinator, never by the builder** (spec 130): `make remote K=s018` (or `make eval
K=s018 PROFILE=remote`), likewise `s019` and `s020`. Each is marked `remote` (`make remote` runs every marked journey).
No model, no vendor, no money: the corridor is the scripted executor's, the owner's own AI.
"""

from __future__ import annotations

import json
import time

from evals import scope_journey
from harness import interview_charge as charge
from harness import sharing
from harness.browser import Auth
from stack import remote

ENTRY_FROM = scope_journey.money_entry
SCOPE = "COMMERCIAL"
#: FR-3: the owner's own projects for the pager -- the study and five more, two pages of five.
EXTRA_PROJECTS = 5
#: The search that matches nobody (S-019).
NOBODY = "zqxjv"
#: S-020: the Check row the co-founder rewords -- Purchase friction's third step (S-016's seed, `scope_journey.FRICTION`).
FRICTION = "commercial.purchase_friction"
REWORDED = "Putting a company card on file"
#: S-020: the one person the co-founder sends a link to (not a corpus name: nothing reads their answer).
COFOUNDER_SENDS_TO = "Sam Okonjo"


def _day() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _identity(stack, role: str, fallback):
    """The second person on the twin: an identity this cell registers (the gated twin lets the harness be only the
    identities it registered); the built-in second founder locally."""
    name = f"{role.title()} {time.strftime('%m%d', time.gmtime())} {remote.cell_name()}"
    return remote.identity_to_sign_in_as(stack, f"{remote.cell_name()} · sharing {role} · {_day()}", fallback=fallback,
                                         name=name)


def _step(j, name: str, party: str = "founder"):
    return j.recorder.step(name, party=party, kind="assert")


def _owner(j) -> dict:
    """The owner's name words and the brand row their own Overview draws (*Paidly · United States*)."""
    ident = getattr(j, "founder_identity", None)
    full = getattr(ident, "name", "") or ""
    pages = sharing.SharedPages(j.page, j.web_base)
    pages.open(f"/p/{j.project_id}")
    brand = pages.brand()
    name, _, country = brand.partition(" · ")
    return {"full": full, "first": sharing.first_name(full), "email": getattr(ident, "email", None),
            "brand": brand, "name": name, "country": country or None}


def _people_names(j) -> list[str]:
    return sorted({p.person for p in getattr(j, "people", None) or [] if getattr(p, "person", None)})


def _extra_projects(j, n: int, stem: str) -> list[str]:
    """`n` more projects of the owner's own (`POST /v2/projects`, a naming-only errand, no AI) on the study's market."""
    market = ((j.get(j.project("/overview")) or {}).get("market") or {})
    made = []
    for i in range(1, n + 1):
        body = {"name": f"{stem} {i}", "scope": "PROBLEM", "market": {"country": market.get("country") or "US"}}
        _, created = j.call("POST", "/v2/projects", body, ok=(200, 201))
        made.append((created or {}).get("projectId"))
    return made


def _new_page(j, *, signed_in=None):
    """A fresh browser context (its own cookie jar) and page; signed in as `signed_in` through the real `/login` where
    named (Keel's door), else nobody at all."""
    context = j.browser.new_context()
    page = context.new_page()
    if signed_in is not None:
        Auth(page, j.recorder, j.web_base).sign_in(signed_in)
    return context, page


def _hold_the_shared_reads(j, wire: sharing.Wire, base_read, owner: dict, *, access: str, where: str) -> dict:
    """The answers a viewer or the link reads: `access`, `sharedBy.firstName` the owner's, no credits, no respondent's
    name and no person's email, link or picture anywhere (keel-cloud 201 T009, T014)."""
    overview = wire.get(base_read("/overview"))
    standings = wire.get(base_read("/standings"))
    names = _people_names(j)
    seen = {"access": overview.get("access"), "sharedBy": overview.get("sharedBy"), "credits": overview.get("credits"),
            "names said": sharing.names_out([overview, standings], names),
            "person fields": sharing.person_fields_out(standings)}
    with _step(j, f"{where}: the shared answers are the owner's with names out -- access {access}, shared by "
                  f"{owner['first']}, no credits, every respondent *Person n*, no email or link (keel-cloud 201)",
               party="stack") as h:
        h.record_assert({"access": access, "sharedBy": {"firstName": owner["first"]}, "credits": None,
                         "names said": [], "person fields": []}, seen)
        assert seen["access"] == access, seen
        assert (seen["sharedBy"] or {}).get("firstName") == owner["first"], seen
        assert seen["credits"] is None, seen
        assert seen["names said"] == [], seen
        assert seen["person fields"] == [], seen
    return {"overview": overview, "standings": standings}


def _hold_the_shared_pages(j, page, base: str, brief: str, owner: dict, where: str, *, signed_in: bool) -> dict:
    """The shared Overview as drawn under `base`: the brand row, the three views, the stage page, the brief; no Share,
    Interviews greyed, the foot's *Try Keel* (a viewer) or the brand row's *Log in* (the link, nobody signed in)."""
    pages = sharing.SharedPages(page, j.web_base)
    pages.open(base)
    want_brand = sharing.shared_brand(owner["name"], owner["first"], owner["country"])
    seen = {"brand": pages.brand(), "views": pages.views()}
    seen["drawn"] = {v: pages.view(v) for v in ("overview", "insights", "pilot")}
    seen["marks"] = pages.marks()
    seen["stage rows"] = pages.stage(base, SCOPE)
    seen["brief pages"] = pages.brief(brief)
    with _step(j, f"{where}: the shared Overview reads '{want_brand}' and opens the Overview, Insights, Pilot, the "
                  f"{SCOPE} stage page and the brief -- no Share, Interviews greyed (keel-web 163 FR-4, FR-5)") as h:
        h.record_assert({"brand": want_brand, "drawn": {"overview": True, "insights": True, "pilot": True},
                         "share": 0, "interviews greyed": ">= 1", "stage rows": ">= 1", "brief pages": ">= 1",
                         "foot": "Try Keel" if signed_in else "Log in"}, seen)
        assert seen["brand"] == want_brand, seen
        assert all(seen["drawn"].values()), seen
        assert seen["marks"]["share"] == 0, seen
        assert seen["marks"]["interviews_not_shared"] >= 1, seen
        assert seen["stage rows"] >= 1 and seen["brief pages"] >= 1, seen
        if signed_in:
            assert seen["marks"]["try_keel"] >= 1, seen
    return seen


# ------------------------------------------------------------------------------------- FR-3: the pager

def _hold_the_pager(j, owner_wire: sharing.Wire) -> None:
    _extra_projects(j, EXTRA_PROJECTS, f"{owner_name_stem(j)} spare")
    lists = owner_wire.get(sharing.LISTS)
    mine = len(lists.get("mine") or [])
    page = sharing.ProjectLists(j.page, j.web_base)
    page.visit()
    label = page.tab("mine")
    first, pages = page.pager(), sharing.pages_of(mine)
    second = page.next_page() if pages > 1 else None
    with _step(j, f"S-018 (FR-3): My projects pages five a page -- {mine} own, '{sharing.page_label(1, pages)}', Next "
                  f"'{sharing.page_label(2, pages)}' (keel-web 163 FR-8)") as h:
        want = {"label": sharing.tab_label("mine", mine), "pager": sharing.page_label(1, pages),
                "next": sharing.page_label(2, pages) if pages > 1 else None,
                "mine on the twin": 1 + EXTRA_PROJECTS}
        h.record_assert(want, {"label": label, "pager": first, "next": second, "mine": mine,
                               "lists": {k: len(v or []) for k, v in lists.items()}})
        if getattr(j.stack, "is_remote", False):
            assert mine == 1 + EXTRA_PROJECTS, mine                     # a fresh owner: the study and five more
            assert first == "Page 1 of 2" and second == "Page 2 of 2", (first, second)
        assert label == want["label"], (label, want)
        assert first == want["pager"] and second == want["next"], (first, second, want)


def owner_name_stem(j) -> str:
    return str(getattr(j.founder, "project_name", None) or "Project").split(" ")[0]


# ------------------------------------------------------------------------------------- S-018: the link

def link(j) -> None:
    """S-018's leg on the finished project (module docstring)."""
    owner_wire = sharing.Wire(j.context, j.cloud_base)
    owner = _owner(j)
    _hold_the_pager(j, owner_wire)

    sheet = sharing.ShareSheet(j.page, j.recorder, j.web_base)
    sheet.open_overview(j.project_id)
    before = sheet.control()
    sheet.start("overview")
    url = sheet.switch_link()
    sheet.done()
    after = sheet.control()
    state = owner_wire.state_until(j.project_id, lambda st: (st.get("link") or {}).get("on") is True)
    token = sharing.token_of(url)
    with _step(j, "S-018: Share -> The Overview -> the link switched on; the url copied, the control reads Shared · "
                  "link on, the wire's link on with that token (keel-web 163 FR-1, FR-2; keel-cloud 201 FR-2)") as h:
        h.record_assert({"before": sharing.SHARE_LABEL, "after": sharing.SHARED_LABEL,
                         "line": sharing.share_summary(link_on=True, viewers=0, co_founders=0), "link.on": True,
                         "url": ".../s/{token}"}, {"before": before, "after": after, "url": url, "state": state})
        assert before["label"] == sharing.SHARE_LABEL, before
        assert after["label"].startswith(sharing.SHARED_LABEL), after
        assert after["line"] == sharing.share_summary(link_on=True, viewers=0, co_founders=0), after
        assert token and (state or {}).get("link", {}).get("on") is True, state
        assert state["link"]["token"] == token and state["link"]["url"].endswith(f"/s/{token}"), state

    stranger_context, stranger = _new_page(j)
    try:
        stranger_wire = sharing.Wire(stranger_context, j.cloud_base)
        _hold_the_shared_pages(j, stranger, f"/s/{token}", f"/p/link-{token}/print", owner,
                               "S-018 (a stranger, no sign-in)", signed_in=False)
        root = stranger_wire.get(sharing.public_path(token))
        _hold_the_shared_reads(j, stranger_wire, lambda r: sharing.public_path(token, r), owner, access="LINK",
                               where="S-018 (a stranger)")
        refused = {"interviews": stranger_wire.call("GET", f"/v2/s/{token}/invitations"),
                   "a write": stranger_wire.call("POST", sharing.public_path(token, "/overview"), {}),
                   "the owner's route": stranger_wire.call("GET", j.project("/overview")),
                   "the owner's sharing": stranger_wire.owner("state", j.project_id)}
        with _step(j, "S-018: the link reads, never writes -- the root names the project and the owner's first name; "
                      "Interviews and any write the bare 404, the owner's routes 401 (keel-cloud 201 FR-3)",
                   party="stack") as h:
            seen = {k: (s, t[:200]) for k, (s, _, t) in refused.items()}
            h.record_assert({"root": {"projectId": j.project_id, "sharedBy": {"firstName": owner["first"]}},
                             "interviews": 404, "a write": 404, "the owner's route": 401,
                             "the owner's sharing": 401}, {"root": root, **seen})
            assert root.get("projectId") == j.project_id and (root.get("sharedBy") or {}).get("firstName") == \
                owner["first"], root
            assert sharing.bare_404(refused["interviews"][0], refused["interviews"][2]), seen
            assert sharing.bare_404(refused["a write"][0], refused["a write"][2]), seen
            assert refused["the owner's route"][0] == 401 and refused["the owner's sharing"][0] == 401, seen

        # the owner switches it off on *Who has it*
        sheet.open_overview(j.project_id)
        who = sheet.who()
        sheet.switch_link()
        sheet.close()
        state_off = owner_wire.state_until(j.project_id, lambda st: (st.get("link") or {}).get("on") is False)
        off = sheet.control()
        stranger.goto(f"{j.web_base}/s/{token}", wait_until="load")
        stranger.get_by_test_id("shared-link-gone").first.wait_for(state="visible", timeout=30_000)
        gone = sharing.SharedPages(stranger, j.web_base).marks()["gone"]
        status, _, text = stranger_wire.call("GET", sharing.public_path(token))
        with _step(j, "S-018: the owner switches the link off on Who has it -- the stranger's page reads 'This link is "
                      "no longer shared.' and the root is the bare 404 (keel-web 163 FR-3; keel-cloud 201 FR-3)") as h:
            h.record_assert({"who url": url, "line": "", "link.on": False, "page": sharing.SHARED_LINK_GONE,
                             "root": 404}, {"who": who, "after": off, "state": state_off, "page": gone,
                                            "root": (status, text[:200])})
            assert who.get("url") == url, who
            assert (state_off.get("link") or {}).get("on") is False, state_off
            assert off["line"] == "", off
            assert gone == sharing.SHARED_LINK_GONE, gone
            assert sharing.bare_404(status, text), (status, text)

        # rotate: on again with a new token -- the old one stays dead
        _, rotated, _ = owner_wire.owner("link", j.project_id, body={"on": True, "rotate": True})
        new = (rotated.get("link") or {}).get("token")
        old_status, _, old_text = stranger_wire.call("GET", sharing.public_path(token))
        new_status, new_root, _ = stranger_wire.call("GET", sharing.public_path(new or "none"))
        _, final, _ = owner_wire.owner("link", j.project_id, body={"on": False})
        with _step(j, "S-018: switched on again with rotate -- a new token opens, the old one is the bare 404; the link "
                      "left off (keel-cloud 201 T001)", party="stack") as h:
            h.record_assert({"new token": "another", "old": 404, "new": 200, "left": False},
                            {"rotated": rotated, "old": (old_status, old_text[:200]), "new": (new_status, new_root),
                             "final": final})
            assert new and new != token, rotated
            assert sharing.bare_404(old_status, old_text), (old_status, old_text)
            assert new_status == 200 and (new_root or {}).get("projectId") == j.project_id, new_root
            assert (final.get("link") or {}).get("on") is False, final
    finally:
        stranger_context.close()


# ------------------------------------------------------------------------------------- S-019: a viewer

def viewer(j, viewer_identity) -> None:
    """S-019's leg on the finished project (module docstring)."""
    owner_wire = sharing.Wire(j.context, j.cloud_base)
    owner = _owner(j)
    email = viewer_identity.email.lower()

    sheet = sharing.ShareSheet(j.page, j.recorder, j.web_base)
    sheet.open_overview(j.project_id)
    sheet.start("overview")
    own = sheet.add(owner["email"].upper() if owner["email"] else "owner")
    bad = sheet.add("not-an-email")
    named = sheet.add(viewer_identity.email)
    sheet.done()
    line = sheet.control()
    state = owner_wire.state_until(j.project_id, lambda st: bool(st.get("viewers")))
    with _step(j, "S-019: the owner's own address and a non-email are refused inline, the viewer named -- the control "
                  "reads 1 can view, the wire's viewers the address lower-cased (keel-web 163 FR-2; keel-cloud 201)") as h:
        h.record_assert({"own": sharing.SHARE_OWN_ADDRESS, "not an email": sharing.SHARE_NOT_EMAIL, "chip": email,
                         "line": sharing.share_summary(link_on=False, viewers=1, co_founders=0),
                         "viewers": [email]}, {"own": own, "bad": bad, "named": named, "line": line, "state": state})
        assert own["refusal"] == sharing.SHARE_OWN_ADDRESS and not own["chips"], own
        assert bad["refusal"] == sharing.SHARE_NOT_EMAIL and not bad["chips"], bad
        assert any(email in c for c in named["chips"]), named
        assert line["line"] == sharing.share_summary(link_on=False, viewers=1, co_founders=0), line
        assert [v.get("email") for v in state.get("viewers") or []] == [email], state

    # a second Overview of the owner's, shared with the viewer too, so the search narrows
    spare = _extra_projects(j, 1, "Spare overview")[0]
    owner_wire.owner("add_viewer", spare, body={"email": email})

    context, page = _new_page(j, signed_in=viewer_identity)
    try:
        wire = sharing.Wire(context, j.cloud_base)
        lists = wire.get(sharing.LISTS)
        rows = lists.get("sharedOverviews") or []
        n = len(rows)
        mine_rows = [r for r in rows if r.get("projectId") in (j.project_id, spare)]
        page_lists = sharing.ProjectLists(page, j.web_base)
        page_lists.visit()
        tab = page_lists.tab("sharedOverviews")
        page_lists.search(owner["full"])
        by_owner = page_lists.label("sharedOverviews")
        page_lists.search(owner["name"])
        by_project = page_lists.label("sharedOverviews")
        project_rows = page_lists.rows()
        k = sum(1 for r in rows if sharing.matches_search(r, owner["name"]))
        page_lists.search(NOBODY)
        nobody, none_line = page_lists.label("sharedOverviews"), page_lists.none()
        with _step(j, "S-019: the viewer finds it under Overviews shared with me; the search on the owner's name, the "
                      "project's name and a name nobody has narrows the count (keel-web 163 FR-7)", party="viewer") as h:
            want = {"tab": sharing.tab_label("sharedOverviews", n),
                    "by owner": sharing.tab_label("sharedOverviews",
                                                  sum(1 for r in rows if sharing.matches_search(r, owner["full"])), n),
                    "by project": sharing.tab_label("sharedOverviews", k, n),
                    "nobody": sharing.tab_label("sharedOverviews", 0, n), "none": sharing.PROJECTS_NONE_MATCH,
                    "row": f"Shared by {owner['full']}"}
            h.record_assert(want, {"tab": tab, "by owner": by_owner, "by project": by_project, "nobody": nobody,
                                   "none": none_line, "rows": project_rows, "wire": lists})
            assert len(mine_rows) == 2, mine_rows
            assert all((r.get("sharedBy") or {}).get("name") == owner["full"] for r in mine_rows), mine_rows
            assert (tab, by_owner, by_project, nobody, none_line) == (want["tab"], want["by owner"], want["by project"],
                                                                     want["nobody"], want["none"]), want
            assert k < n, (k, n, "the project's name narrows")
            assert any(r["name"].startswith(owner["name"]) and r["state"].startswith(want["row"])
                       for r in project_rows), project_rows

        page_lists.search(owner["name"])
        page.locator("[role=tabpanel] a.project-row").filter(has_text=owner["name"]).first.click()
        page.wait_for_url(f"**/p/{j.project_id}**", timeout=30_000)
        _hold_the_shared_pages(j, page, f"/p/{j.project_id}", f"/p/{j.project_id}/print", owner,
                               "S-019 (the viewer, signed in)", signed_in=True)
        _hold_the_shared_reads(j, wire, lambda r: j.project(r), owner, access="VIEWER", where="S-019 (the viewer)")
        refused = {"interviews": wire.call("GET", j.project("/invitations")),
                   "a write": wire.call("PUT", j.project("/context"), {"expectedRevision": 0}),
                   "sharing": wire.owner("state", j.project_id),
                   "share on": wire.owner("add_viewer", j.project_id, body={"email": "someone@example.org"})}
        with _step(j, "S-019: the viewer reads, never writes -- Interviews and a write the bare 404, the sharing routes "
                      "403 (keel-cloud 201 T006, T013)", party="stack") as h:
            seen = {k: (s, t[:200]) for k, (s, _, t) in refused.items()}
            h.record_assert({"interviews": 404, "a write": 404, "sharing": 403, "share on": 403}, seen)
            # T013: a viewer is served the read set and 404 elsewhere (the bare 404 is the link's catch-all's, T008)
            assert seen["interviews"][0] == 404 and seen["a write"][0] == 404, seen
            assert seen["sharing"][0] == 403 and seen["share on"][0] == 403, seen

        # the owner removes them
        sheet.open_overview(j.project_id)
        who = sheet.who()
        sheet.remove(email)
        sheet.close()
        after = owner_wire.state_until(j.project_id, lambda st: not st.get("viewers"))
        lists_after = wire.get(sharing.LISTS)
        status, _, text = wire.call("GET", j.project("/overview"))
        page_lists.visit()
        tab_after = page_lists.tab("sharedOverviews")
        rows_after = page_lists.rows()
        with _step(j, "S-019: the owner removes the viewer on Who has it -- the row is gone from their list and the "
                      "project is the bare 404 to them (keel-web 163 FR-3; keel-cloud 201 FR-6)", party="viewer") as h:
            h.record_assert({"viewers": [], "row": "gone", "overview": 404,
                             "tab": sharing.tab_label("sharedOverviews", n - 1)},
                            {"who": who, "state": after, "lists": lists_after, "overview": (status, text[:200]),
                             "tab": tab_after, "rows": rows_after})
            assert any(email in c for c in who["chips"]), who
            assert not (after.get("viewers") or []), after
            assert j.project_id not in [r.get("projectId") for r in lists_after.get("sharedOverviews") or []], \
                lists_after
            assert sharing.bare_404(status, text), (status, text)
            assert tab_after == sharing.tab_label("sharedOverviews", n - 1), tab_after
            assert not any(r["href"] and r["href"].endswith(f"/p/{j.project_id}") for r in rows_after), rows_after
    finally:
        context.close()


# ---------------------------------------------------------------------------------- S-020: a co-founder

class CoFounder:
    """S-020's two halves: `before_lock` (named, signs in, edits a Check row) and `after` (sends a link, the credits,
    the refusals) -- one co-founder context across both."""

    def __init__(self, identity):
        self.identity = identity
        self.context = None
        self.page = None
        self.wire = None
        self.credits_before = None

    def before_lock(self, j) -> None:
        owner_wire = sharing.Wire(j.context, j.cloud_base)
        email = self.identity.email.lower()
        status, state, text = owner_wire.owner("add_co_founder", j.project_id, body={"email": self.identity.email})
        self.context, self.page = _new_page(j, signed_in=self.identity)
        self.wire = sharing.Wire(self.context, j.cloud_base)
        me = self.wire.get("/v2/me")
        self.credits_before = me.get("creditsAvailable")
        lists = self.wire.get(sharing.LISTS)
        page_lists = sharing.ProjectLists(self.page, j.web_base)
        page_lists.visit()
        tab = page_lists.tab("sharedProjects")
        rows = page_lists.rows()
        n = len(lists.get("sharedProjects") or [])
        owner_full = getattr(j.founder_identity, "name", "")
        with _step(j, "S-020: the owner names a co-founder; the co-founder signs in and finds it under Projects shared "
                      "with me, shared by the owner (keel-cloud 201 FR-1, FR-6; keel-web 163 FR-7)",
                   party="co-founder") as h:
            h.record_assert({"status": 200, "coFounders": [email], "tab": sharing.tab_label("sharedProjects", n),
                             "row": f"Shared by {owner_full}"},
                            {"status": status, "state": state, "tab": tab, "rows": rows, "lists": lists, "me": me})
            assert status == 200 and [c.get("email") for c in (state or {}).get("coFounders") or []] == [email], text
            assert j.project_id in [r.get("projectId") for r in lists.get("sharedProjects") or []], lists
            assert tab == sharing.tab_label("sharedProjects", n), tab
            assert any(r["state"].startswith(f"Shared by {owner_full}") for r in rows), rows

        # the co-founder edits a Check row, as the owner would: Purchase friction's third step, then back
        view = self.wire.get(j.project("/calibration/COMMERCIAL"))
        question = next(q for q in view.get("questions") or [] if q.get("dimension") == FRICTION)
        saved = dict(((question.get("answer") or {}).get("list")) or {})
        items = [{"label": i.get("label")} for i in saved.get("items") or []]
        original = items[-1]["label"]
        edits = []
        for label in (REWORDED, original):
            listed = {"items": items[:-1] + [{"label": label}], "pickedIndex": saved.get("pickedIndex")}
            if saved.get("duration"):
                listed["duration"] = saved["duration"]
            revision = int((self.wire.get(j.project("/overview")) or {}).get("revision") or 0)
            body = {"expectedRevision": revision, "answers": [{"dimension": FRICTION, "list": listed}]}
            put_status, _, put_text = self.wire.call("PUT", j.project("/calibration/COMMERCIAL"), body)
            read = self.wire.get(j.project("/calibration/COMMERCIAL"))
            row = next(q for q in read.get("questions") or [] if q.get("dimension") == FRICTION)
            edits.append({"label": label, "status": put_status, "text": put_text[:200], "revision": revision,
                          "after": int(read.get("revision") or 0),
                          "saved": [i.get("label") for i in ((row.get("answer") or {}).get("list") or {}).get("items")
                                    or []]})
        overview = self.wire.get(j.project("/overview"))
        with _step(j, "S-020: the co-founder edits a Check row (Purchase friction's third step reworded and saved, then "
                      "put back) -- each save lands at a new revision, served as the owner (keel-cloud 201 T013)",
                   party="co-founder") as h:
            h.record_assert({"saves": [200, 200], "saved": [REWORDED, original], "access": "CO_FOUNDER",
                             "sharedBy": None}, {"edits": edits, "access": overview.get("access"),
                                                 "sharedBy": overview.get("sharedBy")})
            assert [e["status"] for e in edits] == [200, 200], edits
            assert [e["saved"][-1] for e in edits] == [REWORDED, original], edits
            assert all(e["after"] > e["revision"] for e in edits), edits
            assert overview.get("access") == "CO_FOUNDER" and overview.get("sharedBy") is None, overview
        # the owner's page drew its revision before these saves: reloaded, so the lock is pressed at the new one
        j.page.reload(wait_until="load")

    def after(self, j) -> None:
        owner_wire = sharing.Wire(j.context, j.cloud_base)
        owner_me = owner_wire.get("/v2/me")
        owner_before = owner_me.get("creditsAvailable")
        try:
            register = self.wire.get(j.project("/invitations"))
            kind = (register.get("kinds") or [{}])[0]
            revision = int((self.wire.get(j.project("/overview")) or {}).get("revision") or 0)
            body = {"expectedRevision": revision, "roleId": kind.get("roleId"), "personName": COFOUNDER_SENDS_TO,
                    "about": kind.get("label") or "asked about one real occasion", "format": "TEXT"}
            sent_status, sent, sent_text = self.wire.call("POST", j.project("/invitations"), body)
            token = str((sent or {}).get("url") or "").rstrip("/").rsplit("/", 1)[-1]
            stranger = sharing.Wire(self.context, j.cloud_base)
            opened = stranger.call("GET", f"/v2/i/{token}") if token else (None, None, "")
            begun = stranger.call("POST", f"/v2/i/{token}/interview/begin") if token else (None, None, "")
            overview = self.wire.get(j.project("/overview"))
            owner_after = owner_wire.get("/v2/me").get("creditsAvailable")
            mine_after = self.wire.get("/v2/me").get("creditsAvailable")
            on_keel = isinstance(owner_before, (int, float))
            with _step(j, "S-020: the co-founder sends a link and it is begun -- the co-founder's credits never move, the "
                          "credits line they read is the owner's, and on Keel's door the owner's balance falls by the "
                          f"interview's {charge.INTERVIEW_CREDITS} (an own-AI owner is never charged; keel-cloud 201 FR-5)",
                       party="co-founder") as h:
                want = {"sent": 201, "begun": 204, "co-founder credits": self.credits_before,
                        "Overview.credits": owner_after,
                        "owner": (owner_before - charge.INTERVIEW_CREDITS) if on_keel else "own AI: none, never charged"}
                h.record_assert(want, {"sent": (sent_status, sent_text[:200]), "opened": opened[0],
                                       "begun": begun[:1] if begun else None,
                                       "co-founder credits": mine_after, "Overview.credits": overview.get("credits"),
                                       "owner before": owner_before, "owner after": owner_after,
                                       "owner aiPath": owner_me.get("aiPath")})
                assert sent_status == 201 and token, sent_text
                assert begun and begun[0] in (200, 204), begun
                assert mine_after == self.credits_before, (mine_after, self.credits_before)
                assert overview.get("credits") == owner_after, (overview.get("credits"), owner_after)
                if on_keel:
                    assert owner_after == owner_before - charge.INTERVIEW_CREDITS, (owner_before, owner_after)
                else:
                    assert owner_after is None and overview.get("credits") is None, (owner_after, overview)

            page = sharing.SharedPages(self.page, j.web_base)
            page.open(f"/p/{j.project_id}")
            self.page.get_by_test_id("report-views").first.wait_for(state="visible", timeout=30_000)
            marks = page.marks()
            refused = {"state": self.wire.owner("state", j.project_id),
                       "link": self.wire.owner("link", j.project_id, body={"on": True}),
                       "add viewer": self.wire.owner("add_viewer", j.project_id, body={"email": "someone@example.org"}),
                       "add co-founder": self.wire.owner("add_co_founder", j.project_id,
                                                         body={"email": "someone@example.org"})}
            with _step(j, "S-020: the co-founder has no Share control and is refused 403 on every sharing route "
                          "(keel-web 163 FR-6; keel-cloud 201 T006)", party="co-founder") as h:
                seen = {k: (s, t[:200]) for k, (s, _, t) in refused.items()}
                h.record_assert({"share": 0, **{k: 403 for k in refused}}, {"marks": marks, **seen})
                assert marks["share"] == 0, marks
                assert all(s == 403 for s, _ in seen.values()), seen

            sheet = sharing.ShareSheet(j.page, j.recorder, j.web_base)
            sheet.open_overview(j.project_id)
            line = sheet.control()
            who = sheet.who()
            sheet.close()
            with _step(j, "S-020: the owner's control reads 1 works on it, the co-founder's chip under Work on the "
                          "project (keel-web 163 FR-1, FR-3)") as h:
                h.record_assert({"line": sharing.share_summary(link_on=False, viewers=0, co_founders=1),
                                 "chip": self.identity.email.lower()}, {"line": line, "who": who})
                assert line["line"] == sharing.share_summary(link_on=False, viewers=0, co_founders=1), line
                assert any(self.identity.email.lower() in c for c in who["chips"]), who
                assert who["coFounders"].startswith("Work on the project · 1"), who
        finally:
            if self.context is not None:
                self.context.close()


# ------------------------------------------------------------------------------------------- the runs

def run_link(stack, founder_one, browser, run_dir) -> None:
    scope_journey.run(stack, founder_one, browser, run_dir, scope=SCOPE, entry_from=ENTRY_FROM, strict=False, slug="s018-share-link",
                      after=link, label=f"{remote.cell_name()} · sharing owner (link) · {_day()}")


def run_viewer(stack, founder_one, founder_two, browser, run_dir) -> None:
    identity = _identity(stack, "viewer", founder_two)
    scope_journey.run(stack, founder_one, browser, run_dir, scope=SCOPE, entry_from=ENTRY_FROM, strict=False,
                      slug="s019-share-viewer", after=lambda j: viewer(j, identity),
                      label=f"{remote.cell_name()} · sharing owner (viewer) · {_day()}")


def run_co_founder(stack, founder_one, founder_two, browser, run_dir) -> None:
    co = CoFounder(_identity(stack, "co-founder", founder_two))
    scope_journey.run(stack, founder_one, browser, run_dir, scope=SCOPE, entry_from=ENTRY_FROM, strict=False,
                      slug="s020-share-co-founder", before_lock=co.before_lock, after=co.after,
                      label=f"{remote.cell_name()} · sharing owner (co-founder) · {_day()}")


def summary(j) -> str:
    """One line for a bundle's reader: who holds the project, from the owner's own state."""
    _, state, _ = sharing.Wire(j.context, j.cloud_base).owner("state", j.project_id)
    return json.dumps(state, default=str)
