"""Doors: every link on a screen, opened once, judged once (spec 007-every-door, FR-001).

A door is an `<a href>` the founder can see. It is *dead* in one of four shapes (keel-cloud
`canon/designs/every-door-design.md` §1):

    D1 not_found       the target renders keel-web's not-found page
    D2 blank           the target renders no screen -- the shell with an empty main pane, or a bare
                       page with no text at all
    D3 failed_request  a 4xx/5xx on the document or on `/v2/*` while the target loads (other than
                       the 401 a logged-out probe deliberately provokes)
    D4 unreachable     an external door that does not answer 2xx/3xx within 10 s, or a resource
                       404 during load (`/favicon.ico`)

Everything that reads a page is here so the rule lives in one place; `judge` is a pure function
over what was read, so `tests/test_doors.py` can exercise every verdict without a browser.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit

NOT_FOUND_MARKER = "This page doesn't exist."
# The apostrophe keel-web renders is the typographic one on some frames and ASCII on others
# (`&apos;` in JSX); match either so a copy change in quoting never hides a not-found page.
_NOT_FOUND_RE = re.compile(r"This page doesn[’']t exist\.")

VERDICTS = ("opens", "not_found", "blank", "failed_request", "unreachable", "skipped")

# keel-web's route table (`src/routes/AppRoutes.tsx`), as patterns over a path -- the walk's
# coverage tally (§3.5 of the design) reports which of these at least one rendered link reached.
ROUTE_PATTERNS: dict[str, re.Pattern[str]] = {
    "/": re.compile(r"^/$"),
    "/login": re.compile(r"^/login$"),
    "/setup": re.compile(r"^/setup$"),
    "/connect": re.compile(r"^/connect$"),
    "/p/:id": re.compile(r"^/p/[^/]+$"),
    "/p/:id/s/:stage": re.compile(r"^/p/[^/]+/s/[^/]+$"),
    "/p/:id/people": re.compile(r"^/p/[^/]+/people$"),
    "/p/:id/invite": re.compile(r"^/p/[^/]+/invite$"),
    "/p/:id/invitations": re.compile(r"^/p/[^/]+/invitations$"),
    "/p/:id/brief": re.compile(r"^/p/[^/]+/brief$"),
    "/i/:token": re.compile(r"^/i/[^/]+$"),
}


@dataclass
class Door:
    source: str          # the page the link was found on (path)
    href: str            # normalised, absolute
    text: str            # the link's own visible words
    external: bool


@dataclass
class Verdict:
    verdict: str                     # one of VERDICTS
    detail: str
    statuses: list[dict[str, Any]] = field(default_factory=list)  # [{url, status}] seen while loading

    def to_row(self) -> dict[str, Any]:
        return asdict(self)


# --------------------------------------------------------------------------------- normalising

def normalise(href: str, base: str) -> str | None:
    """Absolute URL for `href` against `base`; `None` for a door that is not a navigation at all
    (`javascript:`, `mailto:`, `tel:`, an empty or fragment-only href). Fragments are dropped;
    of the query, only `user_code` is kept (the connect screen's own deep link), so `/connect?x=1`
    and `/connect` are the same door and `/connect?user_code=ABCD-EFGH` is its own."""
    if href is None:
        return None
    stripped = href.strip()
    if not stripped or stripped.startswith("#"):
        return None
    lowered = stripped.lower()
    if lowered.startswith(("javascript:", "mailto:", "tel:", "data:")):
        return None
    absolute = urljoin(base if base.endswith("/") else base + "/", stripped)
    parts = urlsplit(absolute)
    query = parse_qs(parts.query)
    kept = {"user_code": query["user_code"]} if "user_code" in query else {}
    path = parts.path or "/"
    if len(path) > 1 and path.endswith("/"):
        path = path[:-1]
    return urlunsplit((parts.scheme, parts.netloc, path, urlencode(kept, doseq=True), ""))


def is_external(url: str, base: str) -> bool:
    return urlsplit(url).netloc.lower() != urlsplit(base).netloc.lower()


def route_of(path: str) -> str | None:
    for name, pattern in ROUTE_PATTERNS.items():
        if pattern.match(path):
            return name
    return None


# ------------------------------------------------------------------------------------ enumerating

def enumerate_doors(page: Any, *, base: str) -> list[Door]:
    """Every `<a href>` in the document, in DOM order, normalised; anchors that are not
    navigations (see `normalise`) are left out. Duplicates on one page are kept -- the row is
    where the link was, the walk dedupes when it opens."""
    source = urlsplit(page.url).path or "/"
    doors: list[Door] = []
    anchors = page.locator("a[href]")
    for i in range(anchors.count()):
        anchor = anchors.nth(i)
        href = anchor.get_attribute("href")
        target = normalise(href, base)
        if target is None:
            continue
        try:
            text = anchor.inner_text().strip()
        except Exception:  # noqa: BLE001 - a detached anchor still counts as a door with no words
            text = ""
        doors.append(Door(source=source, href=target, text=text, external=is_external(target, base)))
    return doors


# ---------------------------------------------------------------------------------------- judging

def judge(*, body_text: str, main_text: str | None, statuses: list[dict[str, Any]],
          allow_401: bool = False) -> Verdict:
    """D1-D3 over what a load produced. `main_text` is the shell's own main pane when the page has
    one (`.shell__main`), else `None`; `statuses` are `{url, status}` for every response seen
    while the page settled."""
    failed = [s for s in statuses if _is_failed(s, allow_401)]
    not_found = bool(_NOT_FOUND_RE.search(body_text or ""))
    if not_found and failed and all(int(f.get("status") or 0) == 404 for f in failed):
        # The wire said 404 and the screen said so too (an unknown participant token: `GET
        # /v2/i/{token}` → 404 → "This page doesn't exist."): that is a not-found door, honestly
        # rendered -- D1, not D3. D3 is a failed request the screen depends on and hides.
        return Verdict("not_found", "the not-found page rendered (the wire answered 404)", statuses)
    if failed:
        first = failed[0]
        return Verdict("failed_request", f"{first['status']} on {first['url']}", statuses)
    if not_found:
        return Verdict("not_found", "the not-found page rendered", statuses)
    if main_text is not None:
        if not main_text.strip():
            return Verdict("blank", "the shell rendered with an empty main pane", statuses)
        return Verdict("opens", "a screen rendered inside the shell", statuses)
    if not (body_text or "").strip():
        return Verdict("blank", "the page rendered no text at all", statuses)
    return Verdict("opens", "a screen rendered", statuses)


def _is_failed(entry: dict[str, Any], allow_401: bool) -> bool:
    status = int(entry.get("status") or 0)
    url = str(entry.get("url") or "")
    path = urlsplit(url).path
    if status < 400:
        return False
    if status == 401 and allow_401:
        return False
    # A resource 404 is D4, judged separately; here only the document and the wire count.
    if path.endswith("/favicon.ico"):
        return False
    return "/v2/" in path or entry.get("document", False)


def resource_misses(statuses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """D4's resource half: any non-wire, non-document response outside 2xx/3xx (today:
    `GET /favicon.ico` → 404 on every load)."""
    misses = []
    for entry in statuses:
        status = int(entry.get("status") or 0)
        path = urlsplit(str(entry.get("url") or "")).path
        if status >= 400 and "/v2/" not in path and not entry.get("document", False):
            misses.append(entry)
    return misses


# ---------------------------------------------------------------------------------------- opening

def open_door(page: Any, url: str, *, allow_401: bool = False, quiet_ms: int = 1000) -> Verdict:
    """Navigates `page` to `url` and judges what rendered. Listens for every response from just
    before `goto` until a short quiet window after `domcontentloaded` (the founder UI polls on a
    4 s cadence, so `networkidle` would never come)."""
    statuses: list[dict[str, Any]] = []
    document_url = {"value": url}

    def on_response(response: Any) -> None:
        try:
            is_document = response.request.resource_type == "document"
            statuses.append({"url": response.url, "status": response.status, "document": is_document})
        except Exception:  # noqa: BLE001 - a response we cannot read is not evidence either way
            pass

    page.on("response", on_response)
    try:
        page.goto(url, wait_until="domcontentloaded")
        try:
            page.evaluate("document.fonts.ready")
        except Exception:  # noqa: BLE001 - fonts are cosmetic for a door check
            pass
        page.wait_for_timeout(quiet_ms)
        document_url["value"] = page.url
        body_text = _text_of(page, "body")
        main_text = _text_of(page, ".shell__main") if page.locator(".shell__main").count() > 0 else None
    finally:
        page.remove_listener("response", on_response)
    verdict = judge(body_text=body_text, main_text=main_text, statuses=statuses, allow_401=allow_401)
    if document_url["value"] != url:
        verdict.detail = f"{verdict.detail}; landed on {urlsplit(document_url['value']).path}"
    return verdict


def check_external(request_context: Any, url: str, *, timeout_ms: int = 10_000) -> Verdict:
    """D4's link half: HEAD, then GET if HEAD is refused, judged on 2xx/3xx."""
    try:
        response = request_context.head(url, timeout=timeout_ms, max_redirects=5)
        status = response.status
        if status in (405, 501):
            response = request_context.get(url, timeout=timeout_ms, max_redirects=5)
            status = response.status
    except Exception as exc:  # noqa: BLE001 - no answer is the finding
        return Verdict("unreachable", f"no answer: {exc}", [])
    if 200 <= status < 400:
        return Verdict("opens", f"answered {status}", [{"url": url, "status": status}])
    return Verdict("unreachable", f"answered {status}", [{"url": url, "status": status}])


def _text_of(page: Any, selector: str) -> str:
    try:
        return page.locator(selector).first.inner_text()
    except Exception:  # noqa: BLE001 - absent selector reads as no text
        return ""


# ------------------------------------------------------------------------------------------ tally

def tally(doors: list[Door], *, base: str) -> dict[str, Any]:
    """Which route-table entries at least one rendered link reached, and from where. Unreached
    routes are reported, never failed (design §3.5)."""
    reached: dict[str, set[str]] = {name: set() for name in ROUTE_PATTERNS}
    for door in doors:
        if door.external:
            continue
        path = urlsplit(door.href).path or "/"
        name = route_of(path)
        if name is not None:
            reached[name].add(door.source)
    return {
        "reached": {name: sorted(sources) for name, sources in reached.items() if sources},
        "unreached": [name for name, sources in reached.items() if not sources],
    }


def rows(doors: list[Door], verdicts: dict[str, Verdict]) -> list[dict[str, Any]]:
    """`doors.json`'s shape: one row per (source, href), the verdict of the href's one opening."""
    out: list[dict[str, Any]] = []
    for door in doors:
        verdict = verdicts.get(door.href)
        out.append({
            **asdict(door),
            "route": route_of(urlsplit(door.href).path or "/") if not door.external else None,
            "verdict": verdict.verdict if verdict else "skipped",
            "detail": verdict.detail if verdict else "not opened",
        })
    return out


JudgeFn = Callable[..., Verdict]
