"""Sharing, mirrored for the referee (keel-e2e-eval spec 130; keel-cloud 201, contract 58 and document version 36;
keel-web 163).

**The wire** (keel-cloud `canon/openapi-v2.yaml` at contract 58, the `sharing` tag): the owner's six routes under
`/v2/projects/{id}/sharing` (each answers `SharingState {link?: {on, since?, token, url}, viewers, coFounders}`; 403 for
a co-founder or a viewer, the bare 404 for a stranger, 422 rule `sharing` for a non-email or the owner's own address),
`GET /v2/me/projects` (`{mine, sharedProjects, sharedOverviews}`, a shared row today's row plus `sharedBy: {firstName,
name}`), the public reads `/v2/s/{token}` + `PUBLIC_READS` (no sign-in; off, rotated or unknown is the bare 404, and so
is every other path or method under `/v2/s/**`), and on `Overview` the caller's `access` (`ACCESS`), the owner's
`credits` (served to the owner and a co-founder, absent for a viewer and on an own-AI account) and, on a viewer's and the
link's answers, `sharedBy.firstName`. Respondents read as *Person n* on a viewer's and the link's answers.

**The screens** (keel-web 163's *selectors for eval 130*, `TESTIDS`): the Share control on the owner's Overview, the
two-step sheet, *Who has it*, the shared Overview's brand row (*{Project} (shared by {firstName}) · {market}*), the
greyed Interviews row, *Try Keel* / *Log in*, the dead link's line, and *Your projects*' three tabs, its search and its
pager (five rows a page, *Page x of y*).

Nothing here is a secret and nothing is sent anywhere by importing it: the page objects act on the page they are handed,
the wire helpers on the browser context's own request (its own cookies -- the owner's, the viewer's, the co-founder's,
or a stranger's none).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any

# ----------------------------------------------------------------------------------------------- the wire

#: keel-cloud 201: the contract the sharing routes arrived with, and the project document's version (the root's
#: `sharing`, additive; 21 to 35 read as shared with nobody).
CONTRACT = 58
DOCUMENT_VERSION = 37  # keel-cloud 244: the upcaster copies datasetName + a valid email onto DATASET invitations
#: `Overview.access` (contract 58).
ACCESS = ("OWNER", "CO_FOUNDER", "VIEWER", "LINK")
#: The public reads under `/v2/s/{token}` (the root is `""`), the read set the shared pages draw.
PUBLIC_READS = ("", "/overview", "/standings", "/context", "/idea", "/persona", "/plan", "/calibration/{vector}",
                "/review/{vector}")
LISTS = "/v2/me/projects"
#: The owner's routes, by name (`{id}` the project, `{email}` a granted address).
OWNER_ROUTES = {
    "state": ("GET", "/v2/projects/{id}/sharing"),
    "link": ("PUT", "/v2/projects/{id}/sharing/link"),
    "add_viewer": ("POST", "/v2/projects/{id}/sharing/viewers"),
    "remove_viewer": ("DELETE", "/v2/projects/{id}/sharing/viewers/{email}"),
    "add_co_founder": ("POST", "/v2/projects/{id}/sharing/coFounders"),
    "remove_co_founder": ("DELETE", "/v2/projects/{id}/sharing/coFounders/{email}"),
}
#: The 422 rule a refused address answers.
SHARING_RULE = "sharing"


def owner_route(name: str, project_id: str, email: str | None = None) -> tuple[str, str]:
    """One of `OWNER_ROUTES` filled: `(method, path)`."""
    method, path = OWNER_ROUTES[name]
    return method, path.replace("{id}", project_id).replace("{email}", email or "")


def public_path(token: str, read: str = "", vector: str | None = None) -> str:
    """`/v2/s/{token}{read}`, a vector filled where the read names one."""
    return f"/v2/s/{token}{read.replace('{vector}', vector or 'PROBLEM')}"


def first_name(google_name: str | None) -> str:
    """keel-cloud 201 T010 (`InterviewComposer.firstName`): `sharedBy.firstName` is the first word of the owner's Google
    name (the account keeps no `given_name`)."""
    words = str(google_name or "").split()
    return words[0] if words else ""


def token_of(url: str | None) -> str | None:
    """The token of a served link url (`{founder app}/s/{token}`)."""
    match = re.search(r"/s/([A-Za-z0-9_-]{12,64})(?:[/?#]|$)", str(url or ""))
    return match.group(1) if match else None


@dataclass
class Wire:
    """One browser context's own view of the cloud -- its cookies, whoever they are (the owner, a viewer, a co-founder,
    a stranger with none). `call` never raises on a status: it answers `(status, payload, text)` so a boundary can hold
    a 403, a bare 404 or a 401 by what it is."""
    context: Any
    cloud_base: str

    def call(self, method: str, path: str, body: dict | None = None) -> tuple[int, Any, str]:
        import json                                                     # noqa: PLC0415
        kwargs: dict = {"timeout": 20_000}
        if body is not None:
            kwargs["data"] = json.dumps(body)
            kwargs["headers"] = {"Content-Type": "application/json"}
        response = self.context.request.fetch(f"{self.cloud_base}{path}", method=method, **kwargs)
        text = response.text()
        try:
            payload = response.json()
        except Exception:                                               # noqa: BLE001 - an empty 404, a 204
            payload = None
        return response.status, payload, text

    def get(self, path: str) -> Any:
        status, payload, text = self.call("GET", path)
        if status != 200:
            raise AssertionError(f"GET {path} answered {status}: {text[:400]}")
        return payload

    def owner(self, name: str, project_id: str, *, email: str | None = None, body: dict | None = None):
        method, path = owner_route(name, project_id, email)
        return self.call(method, path, body)

    def state_until(self, project_id: str, holds, *, timeout_s: float = 15) -> dict:
        """The owner's `SharingState`, read until `holds(state)` (a switch or a removal the sheet sent lands on the
        wire a moment after the press), else the last read."""
        import time                                                     # noqa: PLC0415
        deadline, state = time.monotonic() + timeout_s, {}
        while True:
            _, state, _ = self.owner("state", project_id)
            if holds(state or {}) or time.monotonic() > deadline:
                return state or {}
            time.sleep(0.5)


def bare_404(status: int, text: str) -> bool:
    """Spec 031's ownership refusal: 404 and an empty body -- indistinguishable from an id that exists nowhere."""
    return status == 404 and not (text or "").strip()


def names_out(payload: Any, names: list[str]) -> list[str]:
    """The respondents' names a viewer's or the link's answer still says (keel-cloud 201 T009: each is *Person n*),
    as whole words, case aside -- `[]` where none."""
    import json                                                         # noqa: PLC0415
    text = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
    return [n for n in names if n and re.search(rf"(?<![\w]){re.escape(n)}(?![\w])", text, re.IGNORECASE)]


def person_fields_out(payload: Any) -> list[str]:
    """keel-cloud 201 T009: on any object naming an `invitationId`, `email`, `link`, `picture`, `givenName` and
    `emailStatus` are dropped -- the paths where one is still served."""
    out: list[str] = []

    def walk(node, where: str) -> None:
        if isinstance(node, dict):
            if "invitationId" in node:
                out.extend(f"{where}.{k}" for k in ("email", "link", "picture", "givenName", "emailStatus")
                           if node.get(k) not in (None, ""))
            for key, value in node.items():
                walk(value, f"{where}.{key}")
        elif isinstance(node, list):
            for i, value in enumerate(node):
                walk(value, f"{where}[{i}]")

    walk(payload, "$")
    return out


# --------------------------------------------------------------------------------------------- the screens

#: Spec 129 (keel-web 163's amendments of 2026-11-02): the reads the harness must no longer make -- the summary line
#: under *Shared* (its test id, now `share-count`) and the project stepper (keel-web's `JourneyRail`, class `jrail`: no
#: project page draws it since the 23:00 ET amendment, A002) -- as code would write them.
RETIRED = ('"share-line"', "testid=share-line", ".jrail")
#: keel-web 163 *Owed elsewhere*: the selectors for eval 130.
TESTIDS = ("share", "share-count", "tab-share", "share-sheet", "share-what-overview", "share-what-project", "share-next", "share-back",
           "share-done", "share-cancel", "share-close", "share-more", "share-link-switch", "share-link-url",
           "share-copy", "share-link-since", "share-address", "share-add", "share-refusal", "share-chip",
           "share-remove", "share-who-viewers", "share-who-coFounders", "nav-interviews-not-shared",
           "tab-interviews-not-shared", "try-keel", "shared-log-in", "shared-link-gone", "projects-tab-mine",
           "projects-tab-sharedProjects", "projects-tab-sharedOverviews", "projects-search", "projects-pager",
           "projects-none")
#: keel-web 163 `translate.ts`.
SHARE_LABEL = "Share"
SHARED_LABEL = "Shared"
SHARE_NOT_EMAIL = "That isn't an email address."
SHARE_OWN_ADDRESS = "That's your own address."
SHARED_LINK_GONE = "This link is no longer shared."
NAV_NOT_SHARED = "Not shared"
SHARED_TRY_KEEL = "Try Keel"
PROJECTS_NONE_MATCH = "No project matches that."
PROJECTS_NONE_SHARED = "Nothing is shared with you yet."
#: keel-web 163 FR-8 (`pageOf`): five rows a page.
PAGE_SIZE = 5
TABS = ("mine", "sharedProjects", "sharedOverviews")
_TAB_WORDS = {"mine": "My projects", "sharedProjects": "Projects shared with me",
              "sharedOverviews": "Overviews shared with me"}


def share_summary(*, link_on: bool, viewers: int, co_founders: int) -> str:
    """keel-web 163 amendment 2026-11-02 22:55 ET (`shareCount`, `shareGrants`): beside *Shared* in the side nav and
    the phone's tab, the count of grants -- the link counts one while on, each address one -- as *· N*; empty when
    nothing is shared (the entry then reads *Share* with no count)."""
    grants = (1 if link_on else 0) + viewers + co_founders
    return f"· {grants}" if grants else ""


def shared_brand(name: str, first: str, country: str | None) -> str:
    """keel-web 163 FR-5 (`sharedByBrand` inside `projectDisplayName`): *Paidly (shared by Daphne) · United States*."""
    said = f"{name} (shared by {first})"
    return f"{said} · {country}" if country else said


def tab_label(tab: str, n: int, of: int | None = None) -> str:
    """keel-web 163 `projectsTab*`: *My projects · N*, *Overviews shared with me · k of N* while a search is on."""
    return f"{_TAB_WORDS[tab]} · {n if of is None else f'{n} of {of}'}"


def page_label(page: int, pages: int) -> str:
    """The Contacts dataset's pager words (`namesPageOf`): *Page 1 of 2*."""
    return f"Page {page} of {pages}"


def pages_of(rows: int) -> int:
    return max(1, math.ceil(rows / PAGE_SIZE))


def matches_search(row: dict, query: str) -> bool:
    """keel-web 163 `matchesSearch`: the project's and the owner's name, case aside."""
    q = query.strip().lower()
    if not q:
        return True
    by = (row.get("sharedBy") or {}).get("name") or ""
    return q in str(row.get("name") or "").lower() or q in str(by).lower()


def _text(locator) -> str:
    try:
        return " ".join(str(locator.first.inner_text() or "").split()) if locator.count() else ""
    except Exception:                                                   # noqa: BLE001 - a detached node
        return ""


@dataclass
class ShareSheet:
    """The owner's Share control and its sheet (keel-web 163 FR-1..FR-3), on the owner's Overview `/p/{id}`."""
    page: Any
    recorder: Any
    web_base: str
    seen: list = field(default_factory=list)

    def open_overview(self, project_id: str) -> None:
        self.page.goto(f"{self.web_base}/p/{project_id}", wait_until="load")
        from harness.vectors_screens import pass_teaching_sheet           # noqa: PLC0415
        pass_teaching_sheet(self.page, self.recorder, self.web_base, "report")
        self.page.get_by_test_id("share").first.wait_for(state="visible", timeout=30_000)

    def control(self) -> dict:
        """The control as drawn (the side nav's entry): its word (*Share* / *Shared*) and the count beside it
        (`share-count`, absent until something is shared)."""
        count = self.page.get_by_test_id("share-count")
        return {"label": _text(self.page.get_by_test_id("share")), "line": _text(count) if count.count() else ""}

    def _sheet(self, step: str):
        sheet = self.page.locator(f"[data-testid=share-sheet][data-step={step}]").first
        sheet.wait_for(state="visible", timeout=15_000)
        return sheet

    def start(self, what: str) -> None:
        """*Share* (or *Shared* -> *Share more*), then step one: the Overview or the project, and *Next*."""
        self.page.get_by_test_id("share").first.click()
        if self.page.locator("[data-testid=share-sheet][data-step=who]").count():
            self.page.get_by_test_id("share-more").first.click()
        self._sheet("what")
        self.page.get_by_test_id(f"share-what-{what}").first.click()
        self.page.get_by_test_id("share-next").first.click()

    def switch_link(self) -> str | None:
        """The link's switch pressed; the url box's value once drawn (None where switched off)."""
        self.page.get_by_test_id("share-link-switch").first.click()
        box = self.page.get_by_test_id("share-link-url")
        try:
            box.first.wait_for(state="visible", timeout=10_000)
        except Exception:                                               # noqa: BLE001 - switched off: no box
            return None
        return box.first.input_value()

    def add(self, email: str) -> dict:
        """One address typed and *Add* pressed: the chips after, and any refusal line."""
        import time                                                     # noqa: PLC0415
        chips = lambda: [" ".join(t.split()) for t in self.page.get_by_test_id("share-chip").all_inner_texts()]  # noqa: E731
        before = chips()
        box = self.page.get_by_test_id("share-address").first
        box.fill(email)
        self.page.get_by_test_id("share-add").first.click()
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:                              # a refusal is local; an add waits on the POST
            refusal = _text(self.page.get_by_test_id("share-refusal"))
            if refusal or chips() != before:
                break
            self.page.wait_for_timeout(250)
        return {"refusal": _text(self.page.get_by_test_id("share-refusal")), "chips": chips()}

    def done(self) -> None:
        self.page.get_by_test_id("share-done").first.click()
        self.page.locator("[data-testid=share-sheet]").first.wait_for(state="hidden", timeout=10_000)

    def who(self) -> dict:
        """*Shared* opens *Who has it* (`data-step=who`): its rows as drawn."""
        self.page.get_by_test_id("share").first.click()
        sheet = self._sheet("who")
        return {"viewers": _text(self.page.get_by_test_id("share-who-viewers")),
                "coFounders": _text(self.page.get_by_test_id("share-who-coFounders")),
                "since": _text(self.page.get_by_test_id("share-link-since")),
                "url": (self.page.get_by_test_id("share-link-url").first.input_value()
                        if self.page.get_by_test_id("share-link-url").count() else None),
                "chips": [" ".join(t.split()) for t in sheet.get_by_test_id("share-chip").all_inner_texts()]}

    def remove(self, email: str) -> None:
        """✕ beside one chip on *Who has it* (immediate)."""
        chip = self.page.get_by_test_id("share-chip").filter(has_text=email)
        chip.first.get_by_test_id("share-remove").first.click()
        chip.first.wait_for(state="detached", timeout=15_000)

    def close(self) -> None:
        if self.page.get_by_test_id("share-close").count():
            self.page.get_by_test_id("share-close").first.click()
        elif self.page.get_by_test_id("share-done").count():
            self.page.get_by_test_id("share-done").first.click()
        self.page.locator("[data-testid=share-sheet]").first.wait_for(state="hidden", timeout=10_000)


@dataclass
class SharedPages:
    """The shared Overview as a viewer or the link reads it (keel-web 163 FR-4, FR-5): the brand row, the views, a stage
    page, the brief, the greyed Interviews row; `base` is `/s/{token}` on the link or `/p/{id}` for a signed-in viewer."""
    page: Any
    web_base: str

    def brand(self) -> str:
        """The desktop brand row's project words (`.brandrow .shell__brand .hint`)."""
        hint = self.page.locator(".brandrow .shell__brand .hint").first
        hint.wait_for(state="visible", timeout=30_000)
        return " ".join(str(hint.inner_text() or "").split())

    def open(self, base: str) -> None:
        self.page.goto(f"{self.web_base}{base}", wait_until="load")

    def view(self, view: str) -> bool:
        """One of the report's views (`report-views` `[role=tab][data-view]`) pressed and its panel drawn."""
        views = self.page.get_by_test_id("report-views").first
        views.wait_for(state="visible", timeout=30_000)
        tab = views.locator(f"button[role='tab'][data-view='{view}']").first
        if not tab.count():
            return False
        if tab.get_attribute("aria-selected") != "true":
            tab.click()
        self.page.locator(f"button[role='tab'][data-view='{view}'][aria-selected='true']").first.wait_for(
            state="visible", timeout=10_000)
        self.page.locator("#report-view[role='tabpanel']").first.wait_for(state="visible", timeout=10_000)
        return True

    def views(self) -> list[str]:
        views = self.page.get_by_test_id("report-views").first
        views.wait_for(state="visible", timeout=30_000)
        return [t.get_attribute("data-view") for t in views.locator("[role=tab][data-view]").all()]

    def stage(self, base: str, vector: str) -> int:
        """A stage page under `base`: its rows drawn (how many)."""
        self.page.goto(f"{self.web_base}{base}/s/{vector}", wait_until="load")
        self.page.locator(".dimrow").first.wait_for(state="visible", timeout=30_000)
        return self.page.locator(".dimrow").count()

    def brief(self, path: str) -> int:
        """The printed brief (`report-binding`): its pages drawn. `window.print` stubbed so nothing opens a dialog."""
        self.page.add_init_script("window.print = () => {};")
        self.page.goto(f"{self.web_base}{path}", wait_until="commit")
        binding = self.page.get_by_test_id("report-binding").first
        binding.locator("article.page.rp-page").first.wait_for(state="visible", timeout=60_000)
        return binding.locator("article.page.rp-page").count()

    def marks(self) -> dict:
        """What a shared page must and must not draw: no Share, Interviews greyed, *Try Keel* / *Log in*. Spec 129
        (keel-web 163 amendment 22:55 ET, J-10): Share is the side nav's entry (`share`) and the phone's tab
        (`tab-share`), both in the DOM at every width, so *no Share* counts the two."""
        return {"share": self.page.get_by_test_id("share").count() + self.page.get_by_test_id("tab-share").count(),
                "interviews_not_shared": self.page.get_by_test_id("nav-interviews-not-shared").count()
                + self.page.get_by_test_id("tab-interviews-not-shared").count(),
                "try_keel": self.page.get_by_test_id("try-keel").count(),
                "log_in": self.page.get_by_test_id("shared-log-in").count(),
                "gone": _text(self.page.get_by_test_id("shared-link-gone"))}


@dataclass
class ProjectLists:
    """*Your projects*' three tabs, the search and the pager on `/` (keel-web 163 FR-7, FR-8)."""
    page: Any
    web_base: str

    def visit(self) -> None:
        self.page.goto(f"{self.web_base}/", wait_until="load")
        self.page.get_by_test_id("projects-tab-mine").first.wait_for(state="visible", timeout=30_000)

    def tab(self, tab: str) -> str:
        """Press one tab; its own label after."""
        button = self.page.get_by_test_id(f"projects-tab-{tab}").first
        button.click()
        self.page.locator(f"[role=tabpanel][data-tab={tab}]").first.wait_for(state="attached", timeout=10_000)
        return _text(self.page.get_by_test_id(f"projects-tab-{tab}"))

    def label(self, tab: str) -> str:
        return _text(self.page.get_by_test_id(f"projects-tab-{tab}"))

    def rows(self) -> list[dict]:
        out = []
        for row in self.page.locator("[role=tabpanel] .project-list a.project-row").all():
            out.append({"name": _text(row.locator(".project-row__name")),
                        "state": _text(row.locator(".project-row__state")), "href": row.get_attribute("href")})
        return out

    def search(self, text: str) -> None:
        box = self.page.get_by_test_id("projects-search").first
        box.fill(text)
        self.page.wait_for_timeout(300)

    def pager(self) -> str:
        return _text(self.page.locator("[data-testid=projects-pager] .pager__at"))

    def next_page(self) -> str:
        self.page.locator("[data-testid=projects-pager] button").last.click()
        self.page.wait_for_timeout(300)
        return self.pager()

    def none(self) -> str:
        return _text(self.page.get_by_test_id("projects-none"))
