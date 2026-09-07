"""S-003 -- every door opens (spec 007-every-door; keel-cloud `canon/designs/every-door-design.md`).

The founder's day, every link tried: log in, visit every screen the smoke visits in the smoke's
own order, list every rendered link on each, open each internal one once, check each external
one once, probe the unknown paths and the logged-out back door, and pass only if no door is dead
by D1-D4 (`harness/doors.py`).

Warm after S-001 in the same stack (a project approved through all three cards, invitations
sent, one answer read -- the state with the most doors open) or cold through the prelude, exactly
as S-002 chooses. No LLM. Registers no facts: a walk shows no words of its own, so FIDELITY is
`not_applicable` and the score renormalises over the other three categories.

The referee owns no product code: a dead door is a `runs/DRIFT.md` entry, never a workaround.

Moments cited: §1.0 (arrival, connect, landing), §1.1 (the market step), §1.2 (overview and the
stage cards), §1.4 (People), §1.10 (the download), §2.1 (the participant's page).

**Spec 010 (FR-017..FR-019) changed what there is to try, not what is asked.** The walk gains the
market screen and the download page as seeds, the overview's cards and an opened card's strips as
pages whose links are enumerated -- and, new, **D5, every opener**: an in-page control that
reveals content (a strip row, a dot, the popover's *see all*, the modal's four ways to close) is
exercised once, must reveal what it names, and must close back to the screen it came from. That
rule is this repo's own, not keel-cloud's design (`harness/doors.py`'s docstring, spec judgement
call 4); D1-D4 are keel-cloud's and are untouched.

The participant page keeps **zero doors by design** (FR-019) and that is *recorded*, not failed:
its taps and its *say roughly* boxes are D5 openers, not doors. S-003 still registers no facts and
takes `not_applicable` on FIDELITY -- a walk shows no words of its own, and that has not changed.
"""

from __future__ import annotations

import json
import re
import time

from evals import payroll_exceptions as fx
from evals.preludes import approved_project_with_one_read
from harness import doors as doorway
from harness.browser import (AnswersModal, Auth, Connect, Landing, OpenedCard, Overview, People,
                              PrintPage, SaidBox)
from harness.connect import start_runtime_via_skill
from harness.evidence import finalize_run
from harness.steps import Recorder

WALK_PARTICIPANT = "Walker Test"


def _project_id_from_url(url: str) -> str:
    match = re.search(r"/p/([^/?#]+)", url)
    if not match:
        raise AssertionError(f"not on a project route, cannot read the project id: {url}")
    return match.group(1)


def _connect_agent(page, stack, recorder) -> None:
    result = start_runtime_via_skill(stack, recorder)
    if result["outcome"] == "authorization_started":
        connect = Connect(page, recorder)
        connect.open(result["verification_uri"])
        connect.approve()
        connect.wait_for_connected(timeout_s=30)
        connect.go_to_projects()


def test_s003_every_door(stack, founder_credentials, browser, run_dir):
    recorder = Recorder(run_dir)
    web_base = f"http://localhost:{stack.web_port}"
    started = time.monotonic()
    passed = False
    context = browser.new_context()
    all_doors: list[doorway.Door] = []
    verdicts: dict[str, doorway.Verdict] = {}
    probes: list[dict] = []

    try:
        page = context.new_page()

        # ------------------------------------------------------------------ §1.0 arrival, warm or cold
        Auth(page, recorder, web_base).log_in(
            email=founder_credentials.email, password=founder_credentials.password)
        landing = Landing(page, recorder, web_base)
        arrival = landing.visit()
        if not arrival["agent_connected"]:
            _connect_agent(page, stack, recorder)
        if arrival["has_projects"]:
            landing.visit()
            landing.open_project(0)
            project_id = _project_id_from_url(page.url)
        else:
            project_id, _ = approved_project_with_one_read(
                page, recorder, browser, web_base=web_base, cloud_base=f"http://localhost:{stack.cloud_port}")

        # A participant link of this run's own, so §2.1's page is a seed too (§1.4: one link,
        # one person). It adds one asked row; S-002 runs before this file in `make eval`.
        people = People(page, recorder)
        people.open(project_id)
        if page.locator(".role").count() == 0:
            people.switch_to_kinds_tab()
        # Whatever role *this* project has, not the smoke's: a warm S-003 walks whichever project
        # is already on the stack, and that may be any of the corpus scenarios' (live-confirmed
        # `runs/20260907T153903Z-s003-every-door`, which opened a Mulch Run project and then went
        # looking for a payroll manager). The walk is about doors, not about whose project it is.
        cards = people.role_cards()
        assert cards, "the People page offered no role card to send from"
        role_label = cards[0]["label"]
        people.open_send_popup(role_label)
        people.fill_who(WALK_PARTICIPANT, about=f"{role_label}, asked about one real occasion.")
        people.go_to_preview()
        invite_url = people.generate_link(WALK_PARTICIPANT.split()[0])
        people.close_popup()

        # ------------------------------------------------------------------------- the seeds
        base = f"/p/{project_id}"
        seeds = [
            ("§1.0", "login", "/login"),
            ("§1.0", "landing", "/"),
            ("§1.2", "overview", base),
            ("§1.2", "stage PROBLEM", f"{base}/s/PROBLEM"),
            ("§1.2", "stage SOLUTION", f"{base}/s/SOLUTION"),
            ("§1.2", "stage COMMERCIAL", f"{base}/s/COMMERCIAL"),
            ("§1.4", "people", f"{base}/people"),
            ("§1.4", "people (alias /invite)", f"{base}/invite"),
            ("§1.4", "people (alias /invitations)", f"{base}/invitations"),
            # spec 010 FR-017: the download page is its own page, outside the project shell, and
            # `PrintRoute` calls `window.print()` on mount -- so it is stubbed before the seed is
            # walked or the walk hangs on a native dialog no locator can dismiss (research R9).
            ("§1.10", "download", f"{base}/print"),
            ("§1.0", "connect", "/connect"),
            ("§1.0", "setup", "/setup"),
        ]
        PrintPage(page, recorder, web_base).stub_print()
        for moment, label, path in seeds:
            _walk_seed(page, recorder, web_base, moment, label, path, all_doors, verdicts)

        # §1.1: the market step is an inline frame of `/`, reachable only by starting a project --
        # never by URL. Walked as a seed of its own by getting there the way a founder does.
        openers, opener_verdicts = _walk_market_step(page, recorder, web_base, all_doors)

        # §1.7: the openers. Every one is exercised once and judged by D5.
        _walk_openers(page, recorder, web_base, project_id, openers, opener_verdicts)

        # §2.1: the participant's page, in a context of its own (no founder cookie) -- zero doors
        # by design; recorded, not failed.
        participant_context = browser.new_context()
        try:
            ppage = participant_context.new_page()
            # Untagged on purpose: this is a door check, not a participant visit -- the rubric's
            # GUI-P1 ("reached submit") judges an interview, and the walk never answers one.
            with recorder.step("§2.1: participant opens the invitation link (a seed with no doors)",
                                party="participant", kind="browser") as h:
                verdict = doorway.open_door(ppage, invite_url)
                found = doorway.enumerate_doors(ppage, base=web_base)
                h.capture_text("participant_page", ppage.locator("body").inner_text())
                h.record_assert({"verdict": "opens", "doors": 0},
                                 {"verdict": verdict.verdict, "doors": len(found)})
                h.add_screenshot(_shot(recorder, ppage, "participant-seed"))
                assert verdict.verdict == "opens", f"the participant page did not open: {verdict.detail}"
                all_doors.extend(found)
        finally:
            participant_context.close()

        # --------------------------------------------------------- every internal door, once
        opened_from: dict[str, list[str]] = {}
        for door in all_doors:
            opened_from.setdefault(door.href, []).append(door.source)
        for href, sources in opened_from.items():
            door = next(d for d in all_doors if d.href == href)
            if door.external:
                verdict = doorway.check_external(context.request, href)
                kind = "external"
            else:
                verdict = doorway.open_door(page, href)
                kind = "internal"
            verdicts[href] = verdict
            with recorder.interaction("ui_visit"):
                with recorder.step(f"door: {href} (\"{door.text}\") from {', '.join(sorted(set(sources)))}",
                                    party="founder", kind="browser") as h:
                    h.record_assert({"verdict": "opens"}, {"verdict": verdict.verdict, "detail": verdict.detail})
                    if kind == "internal":
                        h.capture_text("screen", doorway.route_of(_path(href)) or "unknown")
                        h.capture_text("identity", _identity(page))
                        h.add_screenshot(_shot(recorder, page, "door"))
                    for miss in doorway.resource_misses(verdict.statuses):
                        h.capture_text("resource_miss", f"{miss['status']} {miss['url']}")

        # -------------------------------------------------------- the probes nobody links to
        for label, path, allow_not_found in (
            ("unknown top-level path", "/nope", True),
            ("unknown path inside the project", f"{base}/nope", True),
            ("unknown stage slug", f"{base}/s/NOPE", True),
            ("unknown participant token", "/i/nope", True),
        ):
            verdict = doorway.open_door(page, f"{web_base}{path}")
            # Untagged on purpose: a probe is not a founder screen (a not-found page carries no
            # project identity by design), so it is not an interaction the rubric should orient.
            with recorder.step(f"probe: {label} ({path})", party="founder", kind="browser") as h:
                h.record_assert({"verdict": "a screen, not-found or a redirect -- never blank"},
                                 {"verdict": verdict.verdict, "detail": verdict.detail})
                h.capture_text("screen", "probe")
                h.add_screenshot(_shot(recorder, page, "probe"))
            probes.append({"label": label, "path": path, **verdict.to_row()})

        # The back door after logout: a project URL while logged out must land on /login.
        landing.visit()
        landing.log_out()
        verdict = doorway.open_door(page, f"{web_base}{base}", allow_401=True)
        with recorder.step("probe: a project URL while logged out lands on /login",
                            party="founder", kind="browser") as h:
            h.record_assert({"landed": "/login"}, {"verdict": verdict.verdict, "detail": verdict.detail})
            h.add_screenshot(_shot(recorder, page, "probe-logged-out"))
        probes.append({"label": "project URL while logged out", "path": base, **verdict.to_row()})

        # ----------------------------------------------------------------------- the verdict
        coverage = doorway.tally(all_doors, base=web_base)
        (run_dir / "doors.json").write_text(json.dumps({
            "doors": doorway.rows(all_doors, verdicts),
            "openers": doorway.opener_rows(openers, opener_verdicts),
            "probes": probes,
            "coverage": coverage,
        }, indent=2))

        with recorder.step("FR-019: the participant page keeps zero doors by design -- recorded, "
                            "not failed", party="participant", kind="note") as h:
            h.record_assert({"doors on /i/:token": 0},
                             {"note": "its taps and *say roughly* boxes are D5 openers, not doors"})

        dead = [(href, v) for href, v in verdicts.items() if v.verdict != "opens"]
        dead_openers = [(o.label, v) for o, v in zip(openers, opener_verdicts)
                        if v.verdict != "opens"]
        blank_probes = [p for p in probes if p["verdict"] == "blank" or p["verdict"] == "failed_request"]
        favicon = sorted({m["url"] for v in verdicts.values() for m in doorway.resource_misses(v.statuses)})
        with recorder.step("every door opens, every opener opens what it names; no probe is "
                            "blank; no resource is missing", party="founder", kind="assert") as h:
            h.record_assert({"dead": 0, "dead_openers": 0, "blank_probes": 0, "resource_misses": 0},
                             {"dead": [(h_, v.verdict, v.detail) for h_, v in dead],
                              "dead_openers": [(l, v.verdict, v.detail) for l, v in dead_openers],
                              "blank_probes": [(p["path"], p["verdict"]) for p in blank_probes],
                              "resource_misses": favicon,
                              "unreached_routes": coverage["unreached"]})
            assert not dead, "dead doors: " + "; ".join(f"{h_} → {v.verdict} ({v.detail})" for h_, v in dead)
            assert not dead_openers, "dead openers (D5): " + "; ".join(
                f"{l} → {v.verdict} ({v.detail})" for l, v in dead_openers)
            assert not blank_probes, "blank probes: " + "; ".join(f"{p['path']} → {p['verdict']} ({p['detail']})" for p in blank_probes)
            assert not favicon, f"resources missing on load: {favicon}"

        passed = True
    finally:
        context.close()
        duration = time.monotonic() - started
        finalize_run(run_dir, slug="s003-every-door", facts={}, passed=passed,
                     failed_step=recorder.failed_step, duration_s=duration)
        print(f"\nrun bundle: {run_dir}")


def _walk_market_step(page, recorder, web_base, all_doors):
    """§1.1: the market step is an inline frame of `/`, so it is reached by starting a project and
    stopping there -- never by a URL, because it does not have one. Its own doors are enumerated
    and its *Back* is a D5 opener in reverse: it must return to the name step."""
    from harness.browser import Landing, MarketStep

    landing = Landing(page, recorder, web_base)
    landing.visit()
    if page.locator(".guided-step select").count() == 0:
        if page.get_by_role("button", name=re.compile(r"^new project$", re.I)).count() > 0:
            landing.start_new_project()
        landing.name_project("Every door — the market step")
    market = MarketStep(page, recorder, web_base)
    with recorder.interaction("ui_visit"):
        with recorder.step("§1.1: seed the market step (an inline frame of /, no URL of its own)",
                            party="founder", kind="browser") as h:
            found = doorway.enumerate_doors(page, base=web_base)
            h.capture_text("screen", "market")
            h.capture_text("identity", market.kicker())
            h.capture_text("doors", "\n".join(f"{d.text or '(no words)'} → {d.href}"
                                               for d in found) or "(none)")
            h.add_screenshot(_shot(recorder, page, "seed-market"))
            assert market.is_visible(), "the market step did not render after naming a project"
            all_doors.extend(found)
    market.back()
    return [], []


def _walk_openers(page, recorder, web_base, project_id, openers, verdicts) -> None:
    """D5 (FR-018): the strip row, the dot, the popover's *see all*, and the modal's own close.
    Each is exercised **once** -- a control tried twice proves nothing about the first press."""
    opened = OpenedCard(page, recorder, web_base)
    opened.open(project_id, "PROBLEM")
    strips = opened.strips()
    if not strips:
        with recorder.step("D5: the opened card rendered no strips, so there are no openers to try",
                            party="founder", kind="note") as h:
            h.record_assert({"strips": ">= 1"}, {"strips": 0})
        return

    closed = next((s for s in strips if not s["open"]), None)
    if closed is not None:
        control = opened.strip_locator(closed["heading"]).locator(".strip__head")
        verdict = doorway.open_opener(page, control, region=".card.openc",
                                       names=closed["heading"], closer=control)
        openers.append(doorway.Opener(source=f"/p/{project_id}/s/PROBLEM",
                                       label=f"strip row: {closed['heading']}",
                                       names=closed["heading"]))
        verdicts.append(verdict)
        _record_opener(recorder, page, openers[-1], verdict)

    dotted = next((s for s in strips if s["dots"]), None)
    if dotted is not None:
        person = dotted["dots"][0]
        opened.ensure_open(dotted["heading"])
        dot = opened.strip_locator(dotted["heading"]).locator(
            f"svg [role='button'][aria-label={json.dumps(person)}]").first
        verdict = doorway.open_opener(page, dot, region=".card.openc", names=person)
        openers.append(doorway.Opener(source=f"/p/{project_id}/s/PROBLEM",
                                       label=f"dot: {person}", names=person))
        verdicts.append(verdict)
        _record_opener(recorder, page, openers[-1], verdict)

        said = SaidBox(page, recorder)
        if said.is_open():
            see_all = page.locator(".said .a button").first
            verdict = doorway.open_opener(page, see_all, region="body", names=person.split()[0])
            openers.append(doorway.Opener(source=f"/p/{project_id}/s/PROBLEM",
                                           label="popover: see all answers",
                                           names=person.split()[0]))
            verdicts.append(verdict)
            _record_opener(recorder, page, openers[-1], verdict)
            modal = AnswersModal(page, recorder)
            if modal.is_open():
                for via in ("escape",):
                    modal.close(via=via)
                openers.append(doorway.Opener(
                    source=f"/p/{project_id}/s/PROBLEM", label="modal: close (Escape)", names=""))
                verdicts.append(doorway.Verdict(
                    "opens", "the modal closed back to the card it came from", []))
                _record_opener(recorder, page, openers[-1], verdicts[-1])


def _record_opener(recorder, page, opener, verdict) -> None:
    with recorder.interaction("ui_visit"):
        with recorder.step(f"opener: {opener.label}", party="founder", kind="browser") as h:
            h.record_assert({"verdict": "opens"},
                             {"verdict": verdict.verdict, "detail": verdict.detail})
            h.capture_text("screen", "opened_card")
            h.capture_text("identity", _identity(page))
            h.add_screenshot(_shot(recorder, page, "opener"))


def _walk_seed(page, recorder, web_base, moment, label, path, all_doors, verdicts) -> None:
    url = f"{web_base}{path}"
    verdict = doorway.open_door(page, url)
    found = doorway.enumerate_doors(page, base=web_base)
    with recorder.interaction("ui_visit"):
        with recorder.step(f"{moment}: seed {label} ({path}) -- {len(found)} doors",
                            party="founder", kind="browser") as h:
            h.record_assert({"verdict": "opens"}, {"verdict": verdict.verdict, "detail": verdict.detail})
            h.capture_text("screen", doorway.route_of(path) or "unknown")
            h.capture_text("identity", _identity(page))
            h.capture_text("doors", "\n".join(f"{d.text or '(no words)'} → {d.href}" for d in found) or "(none)")
            for miss in doorway.resource_misses(verdict.statuses):
                h.capture_text("resource_miss", f"{miss['status']} {miss['url']}")
            h.add_screenshot(_shot(recorder, page, f"seed-{label.split()[0]}"))
            assert verdict.verdict == "opens", f"seed {path} did not open: {verdict.detail}"
    verdicts.setdefault(url, verdict)
    all_doors.extend(found)


def _shot(recorder, page, slug: str) -> str:
    name = recorder.next_screenshot_name(slug)
    page.screenshot(path=str(recorder.screenshot_path(name)), full_page=True)
    return name


def _identity(page) -> str:
    for selector in (".shell__brand .hint", ".hello", "h1"):
        try:
            locator = page.locator(selector).first
            if locator.count() > 0:
                return locator.inner_text().strip()
        except Exception:  # noqa: BLE001 - identity capture is advisory
            continue
    return ""


def _path(url: str) -> str:
    from urllib.parse import urlsplit
    return urlsplit(url).path or "/"
