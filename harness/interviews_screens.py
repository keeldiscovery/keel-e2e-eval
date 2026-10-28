"""keel-web 068's Interviews section, as page objects (spec 043's second commit).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/corpus_scenario.py` (the
links every journey makes) and `evals/contacts_leg.py` (the contacts leg) judge what they read. The labels a page
object presses are spelled once, below, copied from keel-web `src/lib/translate.ts` at `752a8c4`; the selectors are
the ones 068's spec names for this repository (`.side-nav__group a.side-nav__item`, `.side-nav__item--sub`,
`.role .btn.primary`, `[role=radio]`, `.pop table.ppl--tight`, *Make a new link* in the status cell) plus the
section's own class names (`table.ppl--sent`, `.dsrow`, `.prow`, `.qchip__x`, `.pickrow`, `dialog.credits-refusal`).

* `Interviews` -- `/p/{id}/interviews/sent`: W1 the walkthrough (once per account), the side nav's group, the
                  register (newest first), the rows per kind, *Send more* (format -> who -> links) for someone the
                  founder knows or for a dataset's people, and *Make a new link* (*New link* since keel-web 088).
* `Contacts`   -- `/p/{id}/interviews/contacts`: the tabs per kind, Keel's base query (*Start from it*), C2's chips,
                  *Size it* / *Size it again* / *Show the first 25*, the page of names (`?view=names`) and *Save n
                  picked*, C3 (the saved people, *Find 25 more*, *Go to Sent -> Send more*), the *Not enough credits*
                  popup, the NOT_B2B card and the own-AI line.

Every action that writes returns the response keel-web received for it, so the leg holds the wire the page was
handed and the screen it drew from it.

**Spec 059 (keel-web 088, contract 24): Sent reworked.** The links are a TanStack table (`[data-testid=links]`, rows
`tr[data-invitation]`, pages of ten with `links-prev` / `links-range` *1–10 of 14* / `links-next`, drawn only past ten;
`links-search` from six links; `links-download` at the right of that row; every heading `th button[data-sort]` with
`aria-sort` on its `th`); `register()` walks every page with Next until it is disabled -- it never searches -- and
puts the table back on its first page. The row's action is *See answers, {name}* / *New link, {name}* (no *Make a new
link* in the status cell). Each role card's count is `role-count` in its action row. And **the Interviews first-open
sheet** (`guide-interviews`, while `guide.interviewsSeen` is false): every way this module (and
`harness/interviewer_screens.Persona`) opens Sent goes through `pass_interviews_sheet`, which skips it when drawn and
records the pass in the journey's guide record (`guide["interviews"]`) -- only the guide journey holds it up to judge
(`land(..., sheet="hold")`).
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness.browser import _BrowserStep, _safe_all_texts, _safe_text

# ---- keel-web 088 (spec 059): Sent's first-open sheet, the links table, the role counts (088 tasks.md, *Selectors*)
GUIDE_INTERVIEWS = "[data-testid='guide-interviews']"
#: The sheet's clip (`INTERVIEWS_FIRST`) -- also chapter 1 of Sent's pill; `page-sent` is chapter 2, Contacts' its own.
INTERVIEWS_CLIP = "page-interviews-first"
SENT_CHAPTERS = ("page-interviews-first", "page-sent")
CONTACTS_CLIP = "page-contacts"
#: 088 FR-0 / its e2e: the sheet is a lazy chunk -- 30 s for it on a cold dev server.
SHEET_WAIT_S = 30
GUIDE_PILL_PAGE = "How this page works"
LINKS = "[data-testid='links']"
LINK_ROWS = f"{LINKS} table.ppl tbody tr[data-invitation]"
LINKS_SEARCH = "[data-testid='links-search']"
LINKS_DOWNLOAD = "[data-testid='links-download']"
LINKS_PREV = "[data-testid='links-prev']"
LINKS_NEXT = "[data-testid='links-next']"
LINKS_RANGE = "[data-testid='links-range']"
ROLE_COUNT = "[data-testid='role-count']"
#: 088 judgement calls 1 / 2 / 8: ten a page; the search box from six links; the pager only past ten.
LINKS_PAGE_SIZE = 10
LINKS_SEARCH_FROM = 6
SEE_ANSWERS = "See answers"
NEW_LINK = "New link"
SENT_DOWNLOAD = "Download (.csv)"
SENT_SEARCH_LABEL = "Search who, format, status"
#: 088 `SENT_CSV_HEADER`: the register's .csv, one header line and one line a link (every link, not the page).
SENT_CSV_HEADER = ["name", "kind", "from", "format", "link made", "status", "answered at"]
HOW_IT_WORKS = "How it works"


def row_action(action: str, name: str) -> str:
    """088 `rowAction`: the row's action named with the person, the visible words first (*New link, Hannah Okafor*)."""
    return f"{action}, {name}"


def sent_range(start: int, end: int, total: int) -> str:
    """088 `sentRange`: *1–10 of 14*."""
    return f"{start}–{end} of {total}"

# ---- keel-web 752a8c4 `translate.ts`
NAV_INTERVIEWS = "Interviews"
SUBPAGES = ["Sent", "Contacts", "Keel-managed"]
WALKTHROUGH_TITLE = "Your study is ready. Here is how the interviews happen."
WALKTHROUGH_GOT_IT = "Got it"
SEND_MORE = "Send more"
SEND_THE_QUESTIONS = "Send the questions"
#: keel-web 068's *Make a new link* in the status cell is keel-web 088's row action *New link* (named *New link,
#: {name}*); the constant keeps its name for the legs that hold an answered row offers none.
MAKE_A_NEW_LINK = "New link"
RELINK_DONE = "Done"
FORMAT_NOT_AVAILABLE = "Not available yet"             # keel-web 068, until 069
FORMAT_NAMES = {"TEXT": "Text", "AI_INTERVIEWER": "AI interviewer", "CHOICE": "Let them choose"}   # the Continue words
# ---- keel-web 069 (`translate.ts` at d23895f): Send more's rows and their greyed words
TEXT_ONLY = "Text only"
CHOICE_NAME = "Let them choose"
FORMAT_RECORDING = "recording"
FORMAT_NOT_RECORDED = "not recorded"
FORMAT_NEEDS_CREDITS = "needs Keel's credits"


def ai_format_name(face: str) -> str:
    return f"AI interviewer · {face}"
WHO_OWN = "Someone I know"
WHO_DATASET = "People from a dataset"
SEND_NAME = "Their name"
SEND_MAKE_ONE = "Make their link"
#: keel-web 026's second box on *Someone I know*, removed by keel-web 127 FR-1 (spec 076 FR-3): read only to say none is
#: drawn.
SEND_ABOUT_LABEL = "A short line the top of their page will show"
SEND_DONE = "Done"
SEND_LINKS_TITLE = "One link each. Send them yourself."
SEND_LINKS_DOWNLOAD = "Download the links (.csv)"
START_FROM_IT = "Start from it"
DATASET_OPEN = "Open"
SIZE_IT = "Size it"
SIZE_IT_AGAIN = "Size it again"
SHOW_FIRST = re.compile(r"^Show the first \d+ · [\d,]+ credits$")
FIND_MORE = re.compile(r"^Find \d+ more · [\d,]+ credits$")
SAVE_PICKED = re.compile(r"^Save \d+ picked and get their emails · [\d,]+ credits$")
#: keel-web 070 F3: hidden on the dataset page "for now" (its route stays) -- the page object reads its absence.
COPY_AS_NEW = "Copy as a new dataset"
#: keel-web 070 F4: the page of names' two tools (`names-select-all`, `names-clear`) and its pager (`names-pager`).
NAMES_SELECT_ALL = "Select all"
NAMES_CLEAR = "Clear"
NAMES_PER_PAGE = 25
GO_TO_SEND_MORE = "Go to Sent → Send more"
CHIP_REMOVE = "Remove"
CHIP_ROW_PLACES = "Where"
CONTACTS_B2C_TITLE = "Finding consumers is coming"
CONTACTS_NEED_CREDITS_LINE = ("Finding people runs on Keel's credits, and this account runs on its own AI. Send links to "
                              "people you know from Sent.")
FOUND_STATUS = {"FOUND": "Saved · no link yet", "LINK_MADE": "Not opened", "OPENED": "Opened, not answered",
                "ANSWERED": "Answered"}
REGISTER_STATUS = {"SENT": "Not opened", "OPENED": "Opened, not answered", "ANSWERED": "Answered"}


def _cells(row) -> dict:
    """A `table.ppl` row's cells by their `data-label` (the column heading keel-web writes on each)."""
    out = {}
    for cell in row.locator("td").all():
        label = cell.get_attribute("data-label") or ""
        if not label:                    # keel-web 088: the action column (*See answers* / *New link*) has none
            continue
        out[label] = " ".join((cell.text_content() or "").split())
    return out


def _words(locator) -> str:
    return " ".join((locator.first.text_content() or "").split()) if locator.count() else ""


# ------------------------------------------------------------- spec 059: passing the Interviews sheet by

def pass_interviews_sheet(page: Page, recorder, base: str, *, guide: dict | None = None,
                          timeout_s: float = SHEET_WAIT_S) -> dict:
    """Spec 059 FR-4: keel-web 088's first-open sheet over Sent, passed by as `vectors_screens.pass_teaching_sheet`
    passes the report and opener sheets. Up already: skipped. Due (the clip present in the served manifest, the
    project's contract-24 `guide.interviewsSeen` false, the page on Sent): waited for up to `timeout_s` (the lazy chunk)
    and skipped, in one `note` step. Nothing due: no wait. Absence is never a failure. What happened goes into
    `guide["interviews"]` -- on the guide journey (`judged`) every open after the judged one is kept in its `later`
    (G13: none may draw the sheet again); elsewhere each pass is kept in `passed`."""
    from harness import vectors_screens as vss                  # noqa: PLC0415 - vectors_screens imports this module's kin
    base = (base or "").rstrip("/")
    sheet = vss.GuideWelcome(page, recorder, base, sheet=GUIDE_INTERVIEWS)
    out: dict = {"shown": False}
    if sheet.count():
        out["due"] = True
    elif not re.search(r"/interviews/sent(?:[?#]|$)", page.url or ""):
        out["why"] = "not on Sent"
    else:
        if base not in vss._MANIFESTS:
            vss._MANIFESTS[base] = vss.GuideTeaching(page, recorder, base).manifest()
        seen = vss._due_guide(page, base)
        if not (vss._MANIFESTS[base].get(INTERVIEWS_CLIP) or {}).get("present"):
            out["why"] = f"{INTERVIEWS_CLIP} absent from the manifest"
        elif seen is None or "interviewsSeen" not in seen:
            out["why"] = "no contract-24 guide"
        else:
            out["due"] = seen.get("interviewsSeen") is False
    if out.get("due") and (sheet.count() or sheet.present(timeout_s=timeout_s)):
        with recorder.step("keel-web 088's Interviews sheet opened over Sent; this open does not judge it and passes "
                           "it by with Skip (spec 059)", party="founder", kind="note") as h:
            out = {"shown": True, **sheet._close(sheet._press_skip)}
            h.request = {"sheet": "guide-interviews", "url": page.url}
            h.response = out
    if guide is not None:
        record = guide.setdefault("interviews", {"judged": False, "passed": []})
        if record.get("judged"):
            record.setdefault("later", []).append({"shown": out["shown"], "url": page.url})
        elif out["shown"]:
            record.setdefault("passed", []).append(out)
    return out


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


class Interviews:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0, guide: dict | None = None):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.recorder = recorder
        #: Spec 059: the journey's guide record (`Journey.guide`), where the Sent-open helper keeps each pass.
        self.guide = guide
        #: Spec 062 FR-3: the back-test's camera on the send screen (`evals/backtest.Camera`), or None.
        self.camera = None

    def _shot(self, slug: str) -> None:
        if self.camera is not None:
            self.camera(slug)

    def pass_sheet(self) -> dict:
        """Spec 059 FR-4: keel-web 088's Interviews sheet, skipped when it is drawn over Sent (see the module helper)."""
        return pass_interviews_sheet(self.page, self.recorder, self.base, guide=self.guide)

    # ------------------------------------------------------------------------------------- arriving

    def open(self, project_id: str, sub: str = "sent", query: str = "") -> str:
        """The sub-page, and what drew: `walkthrough` (W1), `sent` (the register's kinds) or `other`."""
        self.page.goto(f"{self.base}/p/{project_id}/interviews/{sub}{query}", wait_until="load")
        return self.arrived()

    def arrived(self, *, timeout_s: float = 60) -> str:
        self.page.locator(".wtstrip, .sent__kinds, .contacts__tabs, .ccard__title, .intro[role=note], .dsopen__title,"
                          " .dseditor").first.wait_for(state="visible", timeout=timeout_s * 1000 * self.patience)
        if self.page.locator(".wtstrip").count():
            return "walkthrough"
        return "sent" if self.page.locator(".sent__kinds").count() else "other"

    def walkthrough(self) -> dict:
        """W1: what it drew, then *Got it* -- the PATCH keel-web sent, and Sent landed on."""
        with self._b.step("the walkthrough plays once for this account; the founder presses Got it") as h:
            drawn = {"title": _safe_text(lambda: self.page.locator(".ccard__title").first.inner_text()),
                     "intro": _safe_text(lambda: self.page.locator(".corridor__intro").first.inner_text()),
                     "frames": self.page.locator(".wtframe").count()}
            h.add_screenshot(self._b.screenshot("walkthrough"))
            with self.page.expect_response(lambda r: r.request.method == "PATCH" and r.url.endswith("/v2/me"),
                                           timeout=20_000) as patched:
                self.page.get_by_role("button", name=WALKTHROUGH_GOT_IT, exact=True).click()
            drawn["patch"] = {"status": patched.value.status, "sent": patched.value.request.post_data_json,
                              "body": _json(patched.value)}
            self.page.wait_for_url(re.compile(r"/interviews/sent"), timeout=20_000)
            self.page.locator(".sent__kinds").wait_for(state="visible", timeout=30_000)
            return drawn

    def land(self, project_id: str, *, sheet: str = "pass") -> dict | None:
        """Sent, with W1 got through first when it plays; returns what W1 drew, or None. `sheet` (spec 059): "pass"
        skips keel-web 088's first-open sheet when it comes (every journey), "hold" leaves it up for the guide journey
        to judge (G13)."""
        seen = None
        if self.open(project_id) == "walkthrough":
            seen = self.walkthrough()
        self.page.locator(".sent__kinds").wait_for(state="visible", timeout=30_000 * self.patience)
        if sheet == "pass":
            self.pass_sheet()
        return seen

    def nav(self) -> dict:
        """The side nav's Interviews group: its row (and where it goes) and its sub-rows, the current one marked."""
        row = self.page.locator(".side-nav__group a.side-nav__item:not(.side-nav__item--sub)").first
        subs = self.page.locator(".side-nav__group a.side-nav__item--sub")
        return {"row": " ".join((row.text_content() or "").split()) if row.count() else "",
                "href": row.get_attribute("href") if row.count() else None,
                "subs": [" ".join((s.text_content() or "").split()) for s in subs.all()],
                "current": [" ".join((s.text_content() or "").split()) for s in subs.all()
                            if s.get_attribute("aria-current") == "page"]}

    # ------------------------------------------------------------------------------------- the register

    def _range(self) -> str:
        return _words(self.page.locator(LINKS_RANGE))

    def _enabled(self, selector: str) -> bool | None:
        found = self.page.locator(selector)
        return found.first.is_enabled() if found.count() else None

    def _turn(self, selector: str) -> bool:
        """Previous or Next, when drawn and enabled; waits for the range to move. False when it could not be pressed."""
        if not self._enabled(selector):
            return False
        before = self._range()
        raw = self.page.locator(LINKS_RANGE).first.text_content()
        self.page.locator(selector).first.click()
        self.page.wait_for_function(
            "([sel, was]) => { const el = document.querySelector(sel); return !el || el.textContent !== was; }",
            arg=[LINKS_RANGE, raw], timeout=10_000)
        return self._range() != before

    def first_page(self) -> None:
        for _ in range(50):
            if not self._turn(LINKS_PREV):
                return

    def _footer_kind(self) -> str:
        """088 judgement call 5: the *Kind · from* column folded into the footer when every link shares one value."""
        return _words(self.page.locator(f"{LINKS} .lt-foot .hint"))

    def page_rows(self) -> list[dict]:
        """The rows of the page in view, by their headings; the footer's *Kind · from* where the column is folded."""
        kind = self._footer_kind()
        rows = [_cells(r) for r in self.page.locator(LINK_ROWS).all()]
        if kind:
            for row in rows:
                row.setdefault("Kind · from", kind)
        return rows

    def register(self) -> list[dict]:
        """Every row of the Sent register as drawn (spec 059 judgement call 1): from the first page, each page's rows,
        Next pressed until it is disabled -- never the search box -- and then back to the first page."""
        self.page.locator(f"{LINKS}, .sent__links").first.wait_for(state="visible", timeout=20_000)
        if not self.page.locator(LINKS).count():
            return []                                              # *No links yet.*: the empty register
        self.first_page()
        rows = self.page_rows()
        for _ in range(50):
            if not self._turn(LINKS_NEXT):
                break
            rows += self.page_rows()
        self.first_page()
        return rows

    def _row(self, person: str):
        """`person`'s row, paging forward from the first page until it is in view (the register is paged since 088)."""
        self.page.locator(LINKS).first.wait_for(state="visible", timeout=20_000)
        self.first_page()
        row = self.page.locator(LINK_ROWS, has=self.page.locator("td b", has_text=person)).first
        for _ in range(50):
            if row.count() or not self._turn(LINKS_NEXT):
                break
        return row

    def kinds(self) -> list[dict]:
        """Each role card: its label, the primary's words and (keel-web 088 FR-3) its own count in the action row."""
        out = []
        for card in self.page.locator(".sent__kinds .role").all():
            out.append({"label": _safe_text(lambda c=card: c.locator(".role__label").first.inner_text()),
                        "button": _safe_text(lambda c=card: c.locator(".btn.primary").first.inner_text()),
                        "count": _words(card.locator(f".actions {ROLE_COUNT}")),
                        # 088 FR-3: the duplicated count line under the buttons (`.actions .hint`) is gone
                        "hints": card.locator(".actions .hint").count()})
        return out

    # ------------------------------------------------------------------------- spec 059: the page's reads

    def order(self) -> dict:
        """G15 (keel-web 088 FR-1): the top of each of Sent's regions, in page coordinates -- the kicker, the total
        line, the pill's placement, the who-asks band, the role cards, the links -- None where it is not drawn; and
        every control anywhere on the page named *How it works*."""
        return self.page.evaluate(r"""(how) => {
          const kinds = document.querySelector('.sent__kinds');
          const root = kinds ? kinds.parentElement : null;
          const top = (el) => el ? Math.round(el.getBoundingClientRect().top + window.scrollY) : null;
          const q = (sel) => root ? root.querySelector(sel) : null;
          const words = (el) => el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : null;
          const controls = Array.from(document.querySelectorAll('button, a, [role=button]'))
            .filter((el) => (el.textContent || '').replace(/\s+/g, ' ').trim() === how);
          return {regions: {kicker: top(q(':scope > .corridor__kicker')), total: top(q(':scope > .sent__counts')),
                            pill: top(q(':scope > .sent__guide')), band: top(q(':scope > [data-testid=persona-line]')),
                            cards: top(kinds), links: top(q(':scope > [data-testid=links], :scope > .sent__links'))},
                  words: {kicker: words(q(':scope > .corridor__kicker')), total: words(q(':scope > .sent__counts')),
                          pill: words(q(':scope > .sent__guide'))},
                  how_it_works: controls.length};
        }""", HOW_IT_WORKS)

    def links(self) -> dict:
        """The links table's frame as drawn: the heading, the search box and *Download (.csv)* (and whether they share
        one row), the pager (its range, Previous and Next), the sort state of every heading and the rows in view."""
        section = self.page.locator(LINKS).first
        section.wait_for(state="visible", timeout=20_000)
        tools = self.page.evaluate("""([search, download]) => {
          const s = document.querySelector(search), d = document.querySelector(download);
          return {same_row: !!(s && d && s.closest('.lt-tools') && s.closest('.lt-tools') === d.closest('.lt-tools')),
                  download_row: !!(d && d.closest('.lt-tools'))}; }""", [LINKS_SEARCH, LINKS_DOWNLOAD])
        sorts = {b.get_attribute("data-sort"): b.evaluate("(b) => b.closest('th').getAttribute('aria-sort')")
                 for b in self.page.locator(f"{LINKS} th button[data-sort]").all()}
        return {"heading": _words(section.locator(".lt-head")), "search": self.page.locator(LINKS_SEARCH).count() > 0,
                "download": _words(self.page.locator(LINKS_DOWNLOAD)), **tools,
                "range": self._range() or None, "prev": self._enabled(LINKS_PREV), "next": self._enabled(LINKS_NEXT),
                "sorts": sorts, "rows": [r.get("Who") for r in self.page_rows()]}

    def _rows_now(self) -> list:
        return [r.get("Who") for r in self.page_rows()]

    def _settle(self, before: list, *, timeout_s: float = 5.0) -> list:
        """The rows in view once they have moved from `before` (or after `timeout_s` when they never do)."""
        deadline = timeout_s * 1000
        waited = 0
        rows = self._rows_now()
        while rows == before and waited < deadline:
            self.page.wait_for_timeout(100)
            waited += 100
            rows = self._rows_now()
        return rows

    def search(self, term: str) -> dict:
        """Types `term` into the search box; the rows and the range it leaves (088: search spans every link)."""
        before = self._rows_now()
        self.page.locator(LINKS_SEARCH).first.fill(term)
        rows = self._settle(before)
        return {"term": term, "rows": rows, "range": self._range() or None, "next": self._enabled(LINKS_NEXT)}

    def sort(self, column: str) -> dict:
        """A click on the `column` heading's button; its `th`'s `aria-sort` before and after, and the rows after."""
        button = self.page.locator(f"{LINKS} th button[data-sort='{column}']").first
        aria = lambda: button.evaluate("(b) => b.closest('th').getAttribute('aria-sort')")  # noqa: E731
        before, rows = aria(), self._rows_now()
        button.click()
        self.page.wait_for_function(
            "([sel, was]) => { const b = document.querySelector(sel); return b && "
            "b.closest('th').getAttribute('aria-sort') !== was; }",
            arg=[f"{LINKS} th button[data-sort='{column}']", before], timeout=5_000)
        return {"column": column, "before": before, "after": aria(), "rows": self._settle(rows, timeout_s=1.0)}

    def download(self, downloads) -> str:
        """*Download (.csv)* pressed through `downloads` (a press -> the file's text)."""
        return downloads(lambda: self.page.locator(LINKS_DOWNLOAD).first.click())

    def go_next(self) -> dict:
        """Next once (when it can be pressed): the range and the rows after, then back to the first page."""
        moved = self._turn(LINKS_NEXT)
        out = {"moved": moved, "range": self._range() or None, "rows": self._rows_now(),
               "next": self._enabled(LINKS_NEXT), "prev": self._enabled(LINKS_PREV)}
        self.first_page()
        return out

    def _kind_card(self, kind_label: str):
        return self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(kind_label)}$"))).first

    def _formats(self, dialog) -> dict:
        """Step 1: each format's radio -- checked, disabled, and the word on its right."""
        out = {}
        for radio in dialog.locator("[role=radio]").all():
            name = _safe_text(lambda r=radio: r.locator(".fmt__name").first.inner_text())
            # keel-web 069: only a greyed row carries its word (`b.fmt__na`); reading an absent one waited 30 s a row
            word = radio.locator("b")
            out[name] = {"checked": radio.get_attribute("aria-checked") == "true", "disabled": radio.is_disabled(),
                         "word": " ".join((word.first.text_content() or "").split()) if word.count() else None}
        return out

    def _step_one(self, dialog, fmt: str = "TEXT") -> dict:
        """Step 1: the formats as drawn, then `fmt` picked (keel-web 069: Text only, the AI interviewer, Let them
        choose) and *Continue · {format}*."""
        dialog.locator("[role=radiogroup] [role=radio]").first.wait_for(state="visible", timeout=10_000)
        self._shot("send-format")
        formats = self._formats(dialog)
        # keel-web 069 checks the AI interviewer first once it is recorded: the asked format is always pressed
        pattern = {"AI_INTERVIEWER": re.compile(r"^AI interviewer"), "CHOICE": re.compile(rf"^{CHOICE_NAME}"),
                   "TEXT": re.compile(rf"^({TEXT_ONLY}|Text)$")}[fmt]
        radio = dialog.locator("[role=radiogroup] [role=radio]", has=self.page.locator(".fmt__name", has_text=pattern))
        if radio.count() and radio.first.get_attribute("aria-checked") != "true":
            # spec 074 (keel-web 119 FR-2): the AI interviewer's row carries *Hear it* inside it, whose press opens the
            # popup and does not choose the row -- so the row is picked by its name, never its middle
            radio.first.locator(".fmt__name").first.click()
        dialog.get_by_role("button", name=f"Continue · {FORMAT_NAMES[fmt]}", exact=True).click()
        dialog.get_by_role("radiogroup", name="Who").wait_for(state="visible", timeout=10_000)
        return formats

    def send_someone(self, project_id: str, kind_label: str, person: str, fmt: str = "TEXT") -> dict:
        """*Send more* (or *Send the questions*) on a kind's row, for someone the founder knows: Text, their name, *Make
        their link*; returns the link drawn, the batch keel-web received, what it sent (`sent`) and step 1's formats.
        Spec 076 FR-3 (keel-web 127 FR-1): the step is the name alone -- the second box (*A short line the top of their
        page will show*, `#send-about`) is gone and the harness types no line; `about_boxes` counts any drawn."""
        with self._b.step(f"founder sends the questions to {person} from Sent") as h:
            if not self.page.url.split("?")[0].endswith(f"/p/{project_id}/interviews/sent"):
                self.land(project_id)
            card = self._kind_card(kind_label)
            card.locator(".btn.primary").click()
            dialog = self.page.get_by_role("dialog")
            formats = self._step_one(dialog, fmt)
            self._shot("send-who")
            dialog.get_by_role("radio", name=re.compile(rf"^{WHO_OWN}")).click()
            dialog.locator("#send-name").fill(person)
            about_boxes = dialog.locator("#send-about").count() + dialog.get_by_label(SEND_ABOUT_LABEL).count()
            batches: list = []
            keep = lambda r: batches.append(r) if (r.request.method == "POST"  # noqa: E731
                                                   and r.url.endswith("/invitations/batch")) else None
            self.page.on("response", keep)
            try:
                with self.page.expect_response(lambda r: r.request.method == "POST"
                                               and r.url.endswith("/invitations/batch"), timeout=30_000) as made:
                    dialog.get_by_role("button", name=SEND_MAKE_ONE, exact=True).click()
                response = made.value
                retried = []
                if response.status == 409 and (_json(response) or {}).get("rule") == "concurrency":
                    # keel-web 070 (DRIFT #88): a 409 concurrency is read again and sent once more, silently.
                    retried.append({"status": response.status, "body": _json(response),
                                    "sent": response.request.post_data_json})
                    for _ in range(60):
                        if len(batches) >= 2:
                            response = batches[-1]
                            break
                        self.page.wait_for_timeout(250)
            finally:
                self.page.remove_listener("response", keep)
            made_value = response
            batch = _json(made_value)
            if made_value.status >= 400:                     # refused: what keel-web received, and what it drew
                h.add_screenshot(self._b.screenshot(f"link-refused-{person.split()[0]}"))
                drawn = " ".join((dialog.text_content() or "").split())
                return {"url": None, "batch": batch, "status": made_value.status, "formats": formats,
                        "drawn": drawn, "sent": made_value.request.post_data_json, "retried": retried,
                        "about_boxes": about_boxes}
            box = dialog.locator(".linkbox").first
            box.wait_for(state="visible", timeout=20_000)
            url = (box.text_content() or "").strip()
            h.add_screenshot(self._b.screenshot(f"link-{person.split()[0]}"))
            drawn = " ".join((dialog.text_content() or "").split())
            dialog.get_by_role("button", name=SEND_DONE, exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return {"url": url, "batch": batch, "status": made_value.status, "formats": formats, "retried": retried,
                    "drawn": drawn, "sent": made_value.request.post_data_json, "about_boxes": about_boxes}

    def send_from_dataset(self, people: list[str], *, downloads) -> dict:
        """The popup C3's *Go to Sent -> Send more* opened (`?send=<kind>&dataset=<id>`): step 1's formats, step 2 with
        the dataset chosen and these people picked (and who was not pickable), *Make n links*, step 3's table, the
        batch's own .csv as downloaded, and Done (pressed twice when keel-web asks once, #42)."""
        with self._b.step(f"founder makes links for {len(people)} found people from Send more") as h:
            dialog = self.page.get_by_role("dialog")
            dialog.wait_for(state="visible", timeout=30_000)
            formats = self._step_one(dialog)
            who = {r.get_attribute("aria-checked"): _safe_text(lambda r=r: r.locator(".fmt__name").inner_text())
                   for r in dialog.get_by_role("radiogroup", name="Who").locator("[role=radio]").all()}
            dataset = dialog.locator("#send-dataset")
            chosen = dataset.locator("option:checked").text_content() if dataset.count() else None
            dialog.locator(".pickrow").first.wait_for(state="visible", timeout=20_000)
            rows = {}
            for row in dialog.locator(".pickrow").all():
                rows[_safe_text(lambda r=row: r.locator(".pickrow__who b").inner_text())] = {
                    "disabled": row.get_attribute("aria-disabled") == "true",
                    "tag": _safe_text(lambda r=row: r.locator(".pickrow__tag").inner_text())
                    if row.locator(".pickrow__tag").count() else ""}
            for name in people:
                dialog.locator(".pickrow", has=self.page.locator(".pickrow__who b", has_text=name)).first.click()
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.endswith("/invitations/batch"), timeout=30_000) as made:
                dialog.get_by_role("button", name=f"Make {len(people)} links", exact=True).click()
            batch = _json(made.value)
            table = self.page.locator(".pop table.ppl--tight")
            table.wait_for(state="visible", timeout=20_000)
            drawn = [[" ".join((c.text_content() or "").split()) for c in tr.locator("td").all()]
                     for tr in table.locator("tr").all()]
            h.add_screenshot(self._b.screenshot("links-batch"))
            csv = downloads(lambda: dialog.get_by_role("button", name=SEND_LINKS_DOWNLOAD, exact=True).click())
            dialog.get_by_role("button", name=SEND_DONE, exact=True).click()
            if dialog.count() and dialog.is_visible():
                dialog.get_by_role("button", name=SEND_DONE, exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return {"formats": formats, "who": who, "dataset": chosen, "rows": rows, "batch": batch,
                    "status": made.value.status, "table": drawn, "csv": csv,
                    "title": SEND_LINKS_TITLE}

    def make_new_link(self, person: str) -> dict:
        """*New link, {person}* on `person`'s row (keel-web 088; *Make a new link* in the status cell before it), the
        row paged to: the relink keel-web received and the link drawn."""
        with self._b.step(f"founder makes a new link for {person} on Sent") as h:
            row = self._row(person)
            # keel-cloud 104 (Discovered 5): right after a return the THEMES housekeeping can move the revision, so the
            # page's first relink may meet 409 and keel-web retries it once (`withOneRetry`, DRIFT #88's); every relink
            # response is kept and the one the dialog drew -- the last -- is the relink
            seen: list = []

            def on_response(response) -> None:
                if response.request.method == "POST" and response.url.endswith("/relink"):
                    seen.append(response)
            self.page.on("response", on_response)
            try:
                with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/relink"),
                                               timeout=30_000):
                    row.get_by_role("button", name=row_action(NEW_LINK, person), exact=True).click()
                dialog = self.page.get_by_role("dialog", name=f"A new link for {person}")
                dialog.wait_for(state="visible", timeout=20_000)
            finally:
                self.page.remove_listener("response", on_response)
            url = (dialog.locator(".linkbox").first.text_content() or "").strip()
            h.add_screenshot(self._b.screenshot(f"relink-{person.split()[0]}"))
            dialog.get_by_role("button", name=RELINK_DONE, exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            last = seen[-1]
            return {"url": url, "relinked": _json(last), "status": last.status,
                    "retried": [r.status for r in seen[:-1]]}

    def status_cell_offers(self, person: str) -> list[str]:
        """The words of the action on `person`'s row (keel-web 088: its own last column), the row paged to."""
        row = self._row(person)
        offers = _safe_all_texts(row, "td:last-child button")
        self.first_page()
        return offers


class Contacts:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

    def open(self, project_id: str, query: str = "") -> dict:
        """Contacts as drawn: the NOT_B2B card, the own-AI line, or the tabs."""
        self.page.goto(f"{self.base}/p/{project_id}/interviews/contacts{query}", wait_until="load")
        self.page.locator(".contacts__tabs, .ccard__title, .intro[role=note], .wtstrip").first.wait_for(
            state="visible", timeout=60_000 * self.patience)
        if self.page.locator(".wtstrip").count():
            return {"walkthrough": True}
        if self.page.locator(".contacts__tabs").count() == 0:
            return {"card": _safe_text(lambda: self.page.locator(".ccard__title").first.inner_text())
                    if self.page.locator(".ccard__title").count() else "",
                    "line": _safe_text(lambda: self.page.locator(".intro[role=note]").first.inner_text())
                    if self.page.locator(".intro[role=note]").count() else ""}
        return {"tabs": _safe_all_texts(self.page, ".contacts__tabs .toggle button"),
                "current": _safe_text(lambda: self.page.locator(".contacts__tabs .toggle button.on").inner_text())}

    def tab(self, kind_label: str) -> dict:
        self.page.locator(".contacts__tabs .toggle button", has_text=re.compile(
            rf"^{re.escape(kind_label)} · ")).first.click()
        self.page.locator(".contacts__kind .role__label", has_text=kind_label).first.wait_for(timeout=10_000)
        base = self.page.locator(".dsrow--base").first
        return {"datasets": [_safe_text(lambda r=r: r.locator(".role__label").inner_text())
                             for r in self.page.locator(".dsrow:not(.dsrow--base)").all()],
                "base": {"title": _safe_text(lambda: base.locator(".role__label").inner_text()),
                         "query": _safe_text(lambda: base.locator(".dsrow__q").inner_text())
                         if base.locator(".dsrow__q").count() else "",
                         "sized": _safe_text(lambda: base.locator(".dsrow__n").inner_text())}}

    def start_from_base(self) -> dict:
        """*Start from it*: C2 with Keel's base query's chips."""
        self.page.locator(".dsrow--base").get_by_role("button", name=START_FROM_IT, exact=True).click()
        self.page.locator(".dseditor").wait_for(state="visible", timeout=20_000)
        return self.chips()

    def chips(self) -> dict:
        out = {}
        for row in self.page.locator(".dseditor .prow").all():
            label = " ".join((row.locator(".prow__label").first.text_content() or "").split())
            out[label] = [" ".join((c.text_content() or "").replace("×", "").split())
                          for c in row.locator(".qchip:not(.qchip--add):not(.qchip--implied)").all()]
        return out

    def remove_all_but_places(self) -> dict:
        """The founder removes every chip but where: titles, level, companies (industries and sizes)."""
        for _ in range(40):
            rows = [r for r in self.page.locator(".dseditor .prow").all()
                    if " ".join((r.locator(".prow__label").first.text_content() or "").split()) != CHIP_ROW_PLACES
                    and r.locator(".qchip__x").count()]
            if not rows:
                break
            rows[0].locator(".qchip__x").first.click()
        return self.chips()

    def name(self, text: str) -> None:
        self.page.locator("#dsname").fill(text)

    def size_it(self, *, again: bool = False) -> dict:
        """*Size it* (create or PATCH, then size) or *Size it again*: the size keel-web received and what C2 drew. A
        chip changed after sizing forgets the size, so C2 offers *Size it* again rather than *Size it again* (068's
        `dirty`); `again` presses whichever of the two is drawn."""
        label = SIZE_IT
        if again and self.page.get_by_role("button", name=SIZE_IT_AGAIN, exact=True).count():
            label = SIZE_IT_AGAIN
        with self._b.step(f"founder presses {label}") as h:
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/size"),
                                           timeout=30_000) as sized:
                self.page.get_by_role("button", name=label, exact=True).click()
            self.page.get_by_role("button", name=SIZE_IT_AGAIN, exact=True).wait_for(state="visible", timeout=20_000)
            self.page.locator(".keeltest__t:not(.keeltest__t--empty)").first.wait_for(timeout=10_000)
            h.add_screenshot(self._b.screenshot("sized"))
            return {"summary": _json(sized.value), "drawn": _safe_text(lambda: self.page.locator(
                ".keeltest__t").first.inner_text()), "url": self.page.url}

    def show_first_enabled(self) -> bool:
        button = self.page.get_by_role("button", name=SHOW_FIRST)
        return button.count() > 0 and button.first.is_enabled()

    def show_first(self) -> dict:
        """*Show the first 25 · 150 credits*: the receipt (or the refusal) keel-web received."""
        return self._fetch(lambda: self.page.get_by_role("button", name=SHOW_FIRST).click(), "show-first")

    def find_more(self) -> dict:
        return self._fetch(lambda: self.page.get_by_role("button", name=FIND_MORE).click(), "find-more")

    def _fetch(self, press, slug: str) -> dict:
        with self._b.step(f"founder asks for a page of names ({slug})") as h:
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/fetch"),
                                           timeout=30_000) as fetched:
                press()
            status = fetched.value.status
            body = _json(fetched.value)
            if status == 200 and body.get("page"):
                self.page.locator(".picklist .pickrow").first.wait_for(state="visible", timeout=20_000)
                want = [row.get("fullName") for row in body["page"]]
                for _ in range(40):                           # the view re-reads the dataset after the fetch
                    if _safe_all_texts(self.page, ".picklist .pickrow .pickrow__who b") == want:
                        break
                    self.page.wait_for_timeout(250)
                drawn = {"title": _safe_text(lambda: self.page.locator(".dsopen__title").inner_text()),
                         "names": _safe_all_texts(self.page, ".picklist .pickrow .pickrow__who b")}
            elif status == 200:                               # an empty page: no names view, C3 again
                drawn = {**self.dataset(), "names": []}
            else:
                drawn = self.credits_refusal()
            h.add_screenshot(self._b.screenshot(slug))
            return {"status": status, "body": body, "drawn": drawn}

    def select_all_and_clear(self) -> dict:
        """keel-web 070 F4 on the page of names: *Select all* ticks every name on the page in view and the Save button
        counts them; *Clear* unticks them and the button counts none. Returns what each press drew."""
        with self._b.step("founder presses Select all, reads the count, then Clear") as h:
            tools = {"select_all": self.page.get_by_test_id("names-select-all"),
                     "clear": self.page.get_by_test_id("names-clear")}
            tools["select_all"].wait_for(state="visible", timeout=10_000)
            rows = self.page.locator(".picklist .pickrow")
            out = {"rows": rows.count(), "pager": self.page.get_by_test_id("names-pager").count() > 0,
                   "labels": {k: _safe_text(lambda b=b: b.inner_text()).strip() for k, b in tools.items()},
                   "before": {k: b.is_enabled() for k, b in tools.items()}}
            tools["select_all"].click()
            button = self.page.get_by_role("button", name=SAVE_PICKED)
            button.wait_for(state="visible", timeout=10_000)
            out["all"] = {"button": _safe_text(lambda: button.inner_text()),
                          "ticked": self.page.locator(".picklist .pickrow[aria-checked=true]").count(),
                          "tools": {k: b.is_enabled() for k, b in tools.items()}}
            h.add_screenshot(self._b.screenshot("names-select-all"))
            tools["clear"].click()
            self.page.wait_for_function(
                "() => !document.querySelector('.picklist .pickrow[aria-checked=true]')", timeout=5_000)
            save = self.page.locator("button", has_text=re.compile(r"^Save \d+ picked"))
            out["cleared"] = {"ticked": self.page.locator(".picklist .pickrow[aria-checked=true]").count(),
                              "button": _safe_text(lambda: save.first.inner_text()) if save.count() else None,
                              "save_enabled": save.first.is_enabled() if save.count() else None,
                              "tools": {k: b.is_enabled() for k, b in tools.items()}}
            return out

    def save_picked(self, names: list[str], *, tools: bool = False) -> dict:
        """The page of names: tick these, *Save n picked and get their emails*; the receipt or the refusal. With `tools`
        the page's *Select all* and *Clear* are pressed first (keel-web 070 F4), and what they drew comes back."""
        drawn_tools = self.select_all_and_clear() if tools else None
        with self._b.step(f"founder saves {len(names)} picked and gets their emails") as h:
            for name in names:
                self.page.locator(".pickrow", has=self.page.locator(".pickrow__who b", has_text=name)).first.click()
            button = self.page.get_by_role("button", name=SAVE_PICKED)
            label = _safe_text(lambda: button.inner_text())
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/save"),
                                           timeout=30_000) as saved:
                button.click()
            status = saved.value.status
            drawn = self.credits_refusal() if status != 200 else self.dataset()
            h.add_screenshot(self._b.screenshot("saved"))
            return {"status": status, "body": _json(saved.value), "button": label, "drawn": drawn, "tools": drawn_tools}

    def dataset(self) -> dict:
        """C3: the head line and every saved person's row (after *Show all*)."""
        self.page.locator(".dsopen__title").first.wait_for(state="visible", timeout=20_000)
        self.page.locator("table.ppl").first.wait_for(state="visible", timeout=20_000)
        more = self.page.locator("table.ppl tr.ppl__more button", has_text=re.compile(r"^Show all"))
        if more.count():
            more.first.click()
        rows = [_cells(r) for r in self.page.locator("table.ppl tbody tr:not(.ppl__more)").all()]
        return {"title": _safe_text(lambda: self.page.locator(".dsopen__title").inner_text()),
                "line": _safe_text(lambda: self.page.locator(".dsopen__line").inner_text()),
                "rows": rows,
                "find_more": self.page.get_by_role("button", name=FIND_MORE).count() > 0,
                "copy_as_new": self.page.get_by_role("button", name=COPY_AS_NEW).count()}

    def open_dataset(self, project_id: str, dataset_id: str, view: str = "") -> None:
        self.page.goto(f"{self.base}/p/{project_id}/interviews/contacts/{dataset_id}{view}", wait_until="load")
        self.page.locator(".dsopen__title, .dseditor").first.wait_for(state="visible", timeout=30_000)

    def go_to_send_more(self, *, guide: dict | None = None) -> None:
        self.page.get_by_role("button", name=GO_TO_SEND_MORE, exact=True).click()
        self.page.wait_for_url(re.compile(r"/interviews/sent"), timeout=20_000)
        pass_interviews_sheet(self.page, self._b.recorder, self.base, guide=guide)

    def credits_refusal(self) -> dict:
        """The *Not enough credits* popup: its title and sentence; closed with its one button."""
        popup = self.page.locator("dialog.credits-refusal")
        popup.wait_for(state="visible", timeout=20_000)
        drawn = {"title": _safe_text(lambda: popup.locator(".credits-refusal__title").inner_text()),
                 "sentence": _safe_text(lambda: popup.locator(".credits-refusal__body").inner_text()),
                 "buttons": _safe_all_texts(popup, "button")}
        popup.get_by_role("button").first.click()
        popup.wait_for(state="hidden", timeout=10_000)
        return drawn
