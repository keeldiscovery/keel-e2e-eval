"""keel-web 068's Interviews section, as page objects (spec 043's second commit).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/corpus_scenario.py` (the
links every journey makes) and `evals/contacts_leg.py` (the contacts leg) judge what they read. The labels a page
object presses are spelled once, below, copied from keel-web `src/lib/translate.ts` at `752a8c4`; the selectors are
the ones 068's spec names for this repository (`.side-nav__group a.side-nav__item`, `.side-nav__item--sub`,
`.role .btn.primary`, `[role=radio]`, `.pop table.ppl--tight`, *Make a new link* in the status cell) plus the
section's own class names (`table.ppl--sent`, `.dsrow`, `.prow`, `.qchip__x`, `.pickrow`, `dialog.credits-refusal`).

* `Interviews` -- `/p/{id}/interviews/sent`: W1 the walkthrough (once per account), the side nav's group, the
                  register (newest first), the rows per kind, *Send more* (format -> who -> links) for someone the
                  founder knows or for a dataset's people, and *Make a new link*.
* `Contacts`   -- `/p/{id}/interviews/contacts`: the tabs per kind, Keel's base query (*Start from it*), C2's chips,
                  *Size it* / *Size it again* / *Show the first 25*, the page of names (`?view=names`) and *Save n
                  picked*, C3 (the saved people, *Find 25 more*, *Go to Sent -> Send more*), the *Not enough credits*
                  popup, the NOT_B2B card and the own-AI line.

Every action that writes returns the response keel-web received for it, so the leg holds the wire the page was
handed and the screen it drew from it.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page

from harness.browser import _BrowserStep, _safe_all_texts, _safe_text

# ---- keel-web 752a8c4 `translate.ts`
NAV_INTERVIEWS = "Interviews"
SUBPAGES = ["Sent", "Contacts", "Keel-managed"]
WALKTHROUGH_TITLE = "Your study is ready. Here is how the interviews happen."
WALKTHROUGH_GOT_IT = "Got it"
SEND_MORE = "Send more"
SEND_THE_QUESTIONS = "Send the questions"
MAKE_A_NEW_LINK = "Make a new link"
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
        out[label] = " ".join((cell.text_content() or "").split())
    return out


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


class Interviews:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")

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

    def land(self, project_id: str) -> dict | None:
        """Sent, with W1 got through first when it plays; returns what W1 drew, or None."""
        seen = None
        if self.open(project_id) == "walkthrough":
            seen = self.walkthrough()
        self.page.locator(".sent__kinds").wait_for(state="visible", timeout=30_000 * self.patience)
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

    def register(self) -> list[dict]:
        """Every row of the Sent register as drawn, after *Show all* when the first six hide some."""
        more = self.page.locator("table.ppl--sent tr.ppl__more button")
        if more.count():
            more.first.click()
            self.page.locator("table.ppl--sent tr.ppl__more").wait_for(state="detached", timeout=10_000)
        return [_cells(r) for r in self.page.locator("table.ppl--sent tbody tr:not(.ppl__more)").all()]

    def kinds(self) -> list[dict]:
        out = []
        for card in self.page.locator(".sent__kinds .role").all():
            out.append({"label": _safe_text(lambda c=card: c.locator(".role__label").first.inner_text()),
                        "button": _safe_text(lambda c=card: c.locator(".btn.primary").first.inner_text()),
                        "line": _safe_text(lambda c=card: c.locator(".actions .hint").first.inner_text())})
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
        formats = self._formats(dialog)
        # keel-web 069 checks the AI interviewer first once it is recorded: the asked format is always pressed
        pattern = {"AI_INTERVIEWER": re.compile(r"^AI interviewer"), "CHOICE": re.compile(rf"^{CHOICE_NAME}"),
                   "TEXT": re.compile(rf"^({TEXT_ONLY}|Text)$")}[fmt]
        radio = dialog.locator("[role=radiogroup] [role=radio]", has=self.page.locator(".fmt__name", has_text=pattern))
        if radio.count() and radio.first.get_attribute("aria-checked") != "true":
            radio.first.click()
        dialog.get_by_role("button", name=f"Continue · {FORMAT_NAMES[fmt]}", exact=True).click()
        dialog.get_by_role("radiogroup", name="Who").wait_for(state="visible", timeout=10_000)
        return formats

    def send_someone(self, project_id: str, kind_label: str, person: str, about: str | None = None,
                     fmt: str = "TEXT") -> dict:
        """*Send more* (or *Send the questions*) on a kind's row, for someone the founder knows: Text, their name
        (and the line when given), *Make their link*; returns the link drawn, the batch keel-web received and step
        1's formats."""
        with self._b.step(f"founder sends the questions to {person} from Sent") as h:
            if not self.page.url.split("?")[0].endswith(f"/p/{project_id}/interviews/sent"):
                self.land(project_id)
            card = self._kind_card(kind_label)
            card.locator(".btn.primary").click()
            dialog = self.page.get_by_role("dialog")
            formats = self._step_one(dialog, fmt)
            dialog.get_by_role("radio", name=re.compile(rf"^{WHO_OWN}")).click()
            dialog.locator("#send-name").fill(person)
            if about is not None and dialog.locator("#send-about").count():
                dialog.locator("#send-about").fill(about)
            with self.page.expect_response(lambda r: r.request.method == "POST"
                                           and r.url.endswith("/invitations/batch"), timeout=30_000) as made:
                dialog.get_by_role("button", name=SEND_MAKE_ONE, exact=True).click()
            batch = _json(made.value)
            if made.value.status >= 400:                     # refused: what keel-web received, and what it drew
                h.add_screenshot(self._b.screenshot(f"link-refused-{person.split()[0]}"))
                drawn = " ".join((dialog.text_content() or "").split())
                return {"url": None, "batch": batch, "status": made.value.status, "formats": formats,
                        "drawn": drawn, "sent": made.value.request.post_data_json}
            box = dialog.locator(".linkbox").first
            box.wait_for(state="visible", timeout=20_000)
            url = (box.text_content() or "").strip()
            h.add_screenshot(self._b.screenshot(f"link-{person.split()[0]}"))
            dialog.get_by_role("button", name=SEND_DONE, exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return {"url": url, "batch": batch, "status": made.value.status, "formats": formats}

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
        """*Make a new link* in the status cell of `person`'s row: the relink keel-web received and the link drawn."""
        with self._b.step(f"founder makes a new link for {person} on Sent") as h:
            self.register()
            row = self.page.locator("table.ppl--sent tbody tr", has=self.page.locator("td b", has_text=person)).first
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith("/relink"),
                                           timeout=30_000) as made:
                row.get_by_role("button", name=MAKE_A_NEW_LINK, exact=True).click()
            dialog = self.page.get_by_role("dialog", name=f"A new link for {person}")
            dialog.wait_for(state="visible", timeout=20_000)
            url = (dialog.locator(".linkbox").first.text_content() or "").strip()
            h.add_screenshot(self._b.screenshot(f"relink-{person.split()[0]}"))
            dialog.get_by_role("button", name=RELINK_DONE, exact=True).click()
            dialog.wait_for(state="hidden", timeout=10_000)
            return {"url": url, "relinked": _json(made.value), "status": made.value.status}

    def status_cell_offers(self, person: str) -> list[str]:
        row = self.page.locator("table.ppl--sent tbody tr", has=self.page.locator("td b", has_text=person)).first
        return _safe_all_texts(row, "td:last-child button")


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

    def save_picked(self, names: list[str]) -> dict:
        """The page of names: tick these, *Save n picked and get their emails*; the receipt or the refusal."""
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
            return {"status": status, "body": _json(saved.value), "button": label, "drawn": drawn}

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
                "find_more": self.page.get_by_role("button", name=FIND_MORE).count() > 0}

    def open_dataset(self, project_id: str, dataset_id: str, view: str = "") -> None:
        self.page.goto(f"{self.base}/p/{project_id}/interviews/contacts/{dataset_id}{view}", wait_until="load")
        self.page.locator(".dsopen__title, .dseditor").first.wait_for(state="visible", timeout=30_000)

    def go_to_send_more(self) -> None:
        self.page.get_by_role("button", name=GO_TO_SEND_MORE, exact=True).click()
        self.page.wait_for_url(re.compile(r"/interviews/sent"), timeout=20_000)

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
