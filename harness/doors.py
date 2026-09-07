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

**D5, every opener** (spec 010 FR-018, and **this repo's own rule**, not keel-cloud's).
`every-door-design.md` has D1-D4 and predates a screen with a strip that expands, a dot that pops
a box, and a modal. An in-page control that *reveals* content -- a strip row, a dot, the popover's
*see all*, the modal's close, a chip tap -- is not an `<a href>` and no D1-D4 rule reaches it, but
it is a door in every sense a founder cares about: it names something and it either opens it or it
does not.

    D5 opens_nothing   the control was exercised once and nothing appeared
    D5 cannot_close    it opened what it named and would not close back to the screen it came from

Judgement call 4 of the spec records that this is the referee's addition rather than keel-cloud's
design; if the founder would rather it went into `every-door-design.md` first, it can wait for
that. Until then it is stated here so it reads as chosen.

Everything that reads a page is here so the rule lives in one place; `judge` and `judge_opener`
are pure functions over what was read, so `tests/test_doors.py` and `tests/test_doors_d5.py` can
exercise every verdict without a browser.
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

# `opens_nothing` and `cannot_close` are D5's (see the module docstring); the first five are
# keel-cloud's own design and are untouched.
VERDICTS = ("opens", "not_found", "blank", "failed_request", "unreachable", "skipped",
            "opens_nothing", "cannot_close")

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
    # spec 010: `/p/:id/brief` retires with `BriefRoute.tsx`; `/p/:id/print` -- the download page,
    # which sits outside the project shell -- joins the table as a seed of its own (FR-017).
    "/p/:id/print": re.compile(r"^/p/[^/]+/print$"),
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


# ----------------------------------------------------------------------------- D5, every opener

@dataclass
class Opener:
    """An in-page control that reveals content. `names` is what it says it will open -- a person's
    name on a dot, a line's heading on a strip row -- and is what "opens what it names" means."""
    source: str          # the page it was found on (path)
    label: str           # the control's own visible words, or its aria-label
    names: str = ""      # what it promises to reveal; "" when it promises nothing in particular


def judge_opener(*, before: str, opened: str, closed: str | None, names: str = "") -> Verdict:
    """D5 over three reads of the same region: before the control was used, after it was used, and
    after it was used again to close (or `None` where the control is one-way by design).

    Three verdicts and nothing looser:

    - **opens_nothing** -- the opened read is no bigger than the before read. A control that
      reveals nothing is dead in exactly the way a `<a href>` to a blank page is dead.
    - **opens** but the promised words are missing -> also `opens_nothing`, with the promise
      quoted: a dot labelled *Dana Okafor* that opens somebody else's box has not opened what it
      names, and calling that "opens" would be the referee agreeing with the screen.
    - **cannot_close** -- it opened, and the closed read still carries what the opened one added.
      The design's own phrasing is *closes back to the screen it came from*; a box that will not
      shut is a founder stuck on a screen they did not choose.
    """
    before_text = (before or "").strip()
    opened_text = (opened or "").strip()
    if len(opened_text) <= len(before_text):
        return Verdict("opens_nothing", "the control was exercised once and nothing appeared", [])
    revealed = opened_text
    if names and names.strip().casefold() not in revealed.casefold():
        return Verdict("opens_nothing",
                       f"something appeared, but not what the control names ({names!r})", [])
    if closed is None:
        return Verdict("opens", "it opened what it names (one-way by design; no close to judge)", [])
    closed_text = (closed or "").strip()
    if len(closed_text) > len(before_text):
        return Verdict("cannot_close",
                       "it opened what it names but would not close back to the screen it came "
                       "from", [])
    return Verdict("opens", "it opened what it names and closed back", [])


# Every text node under a region, SVG included. `innerText` drops SVG `<text>` entirely, and a
# strip row that opens reveals a chart -- so an opener that genuinely revealed something would
# read as `opens_nothing` against `innerText` alone. Same walker `harness/browser.py` uses for its
# screen captures, inlined here so `harness/doors.py` stays importable with no browser at all.
#
# A strip's own reveal is drawn by CSS, not by mounting: `StageRoute.tsx` renders every line's
# `.strip__svg`/`.strip__read`/`.strip__you`/`.said` unconditionally and `app.css`'s
# `.lines .strip .strip__svg{display:none}` / `.lines .strip.open .strip__svg{display:block}`
# (and siblings) is what shows or hides them -- so a walk that only checks the `hidden` attribute
# (as `innerText` itself effectively does, by way of the render tree) finds the same text before
# and after the toggle and reads a real reveal as `opens_nothing`. `isRendered` below skips a
# subtree CSS has hidden (`display:none` or `visibility:hidden`), same as `innerText` would, while
# still walking into the SVG `innerText` drops -- the region D5 needs is "what a founder can
# actually see", not "everything the DOM happens to hold".
_DEEP_TEXT_JS = r"""(el) => {
  if (!el) return "";
  const parts = [];
  const isRendered = (node) => {
    if (node.hidden) return false;
    const style = window.getComputedStyle(node);
    if (!style) return true;
    return style.display !== "none" && style.visibility !== "hidden";
  };
  const walk = (node) => {
    for (const child of node.childNodes) {
      if (child.nodeType === 3) {
        const text = child.textContent.replace(/\s+/g, ' ').trim();
        if (text) parts.push(text);
      } else if (child.nodeType === 1 && isRendered(child)) {
        walk(child);
      }
    }
  };
  walk(el);
  return parts.join(' ');
}"""


def _deep_text(page: Any, selector: str) -> str:
    try:
        locator = page.locator(selector).first
        if locator.count() == 0:
            return ""
        return locator.evaluate(_DEEP_TEXT_JS) or ""
    except Exception:  # noqa: BLE001 - a region that will not evaluate reads as no text
        return ""


def open_opener(page: Any, control: Any, *, region: str, names: str = "",
                 closer: Any = None, settle_ms: int = 250, deep: bool = True) -> Verdict:
    """Exercises one opener **once** and judges it (D5). `region` is the selector whose text is
    read three times; `closer` is the control that shuts it again (the same control, when it
    toggles), or `None` for a one-way reveal.

    A harness mechanic, not an assertion -- the rule is `judge_opener`'s, which is why that half
    is pure and unit-tested against canned DOMs.
    """
    read = (lambda: _deep_text(page, region)) if deep else (lambda: _text_of(page, region))
    before = read()
    forced = False
    try:
        control.click(timeout=5_000)
    except Exception:  # noqa: BLE001 - see below
        # Two people who answered the same thing are two dots at the same point, and the one on
        # top intercepts the click meant for the one beneath (live-confirmed
        # `runs/20260907T153949Z-s003-every-door`: Marisol Ortega's circle over Kaylee Nguyen's).
        # That is a drawing, not a dead door -- the control is visible, enabled and stable, and a
        # founder reaches it by clicking a pixel or two along. Dispatching the click on the element
        # itself exercises *that* control; the fallback is recorded, never silent.
        control.click(force=True, timeout=5_000)
        forced = True
    page.wait_for_timeout(settle_ms)
    opened = read()
    closed = None
    if closer is not None:
        try:
            closer.click()
            page.wait_for_timeout(settle_ms)
            closed = read()
        except Exception as exc:  # noqa: BLE001 - a closer that cannot even be clicked is D5
            return Verdict("cannot_close", f"the closing control could not be used: {exc}", [])
    verdict = judge_opener(before=before, opened=opened, closed=closed, names=names)
    if forced:
        verdict.detail += " (the click was dispatched on the control: another dot sat over it)"
    return verdict


def opener_rows(openers: list[Opener], verdicts: list[Verdict]) -> list[dict[str, Any]]:
    """`doors.json`'s `openers` half: one row per control exercised."""
    return [{**asdict(opener), "verdict": verdict.verdict, "detail": verdict.detail}
            for opener, verdict in zip(openers, verdicts)]


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
