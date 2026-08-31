"""The check engine (T004, contracts/policy-contract.md): walks derived interactions
(harness/interactions.py) and the scenario's fact registry (evals/scenario.py), and emits
CheckResults -- deterministic, evidence-carrying, exactly the checks the current policy version
defines (no more, no fewer; a check this module invents without a matching policy entry is a
bug). Policy v2 (evals/policy.py, 003-eval-set) recalibrated which interaction types carry
`CLA-A1`/`GUI-A2` -- see `_agent_cycle_checks`/`_agent_handoff_checks` below.

An empty interaction list (a transcript with no interaction tags -- analysis finding A2) or an
empty fact registry both evaluate cleanly to no checks, not an exception: `evaluate([], {})`
returns `([], {})`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from evals import policy
from evals.scenario import Fact
from harness.interactions import Interaction

# Actions whose get_next `detail` is expected to locate the work (ORI-A2's "applies to" scoping).
_SCOPED_ACTIONS = {"FRAME", "INTRODUCE_ASSUMPTIONS", "INTERPRET", "WITHDRAW_ASSUMPTION"}

# Words a handoff's `display` needs at least one of to count as "says what to do next" (GUI-H1),
# as opposed to a bare status report. Deliberately generous (a false negative here is a harsher
# score than the design intends) rather than an exhaustive parser of imperative mood.
_GUIDANCE_VERBS = (
    "read", "approve", "invite", "wait", "open", "ask", "review", "tell", "send", "reply",
    "answer", "start", "submit", "talk", "come back", "check",
)


@dataclass
class CheckResult:
    check_id: str
    attribute: str
    weight: float
    passed: bool
    detail: str
    evidence: dict[str, Any]
    waived: dict[str, str] | None = None


def _result(check_id: str, passed: bool, detail: str, ix: Interaction, *,
            attribute: str | None = None, weight: float | None = None,
            waived: dict[str, str] | None = None,
            fact_id: str | None = None, hop: str | None = None) -> CheckResult:
    spec = policy.CHECKS.get(check_id, {})
    evidence: dict[str, Any] = {"steps": list(ix.step_seqs), "screenshots": list(ix.screenshots)}
    if fact_id is not None:
        evidence["fact_id"] = fact_id
    if hop is not None:
        evidence["hop"] = hop
    return CheckResult(
        check_id=check_id,
        attribute=attribute or spec.get("attribute", "FIDELITY"),
        weight=weight if weight is not None else spec.get("weight", policy.DEFAULT_WEIGHT),
        passed=passed, detail=detail, evidence=evidence, waived=waived,
    )


# ------------------------------------------------------------------------------------ agent-cycle

def _ori_a1(ix: Interaction) -> CheckResult:
    instruction = (ix.conversation or {}).get("instruction") or {}
    content = (instruction.get("content") or "").strip()
    purpose = (instruction.get("purpose") or "").strip()
    passed = bool(content) and bool(purpose)
    detail = "instruction has a non-empty purpose and content" if passed \
        else f"instruction missing purpose or content (purpose={purpose!r}, content len={len(content)})"
    return _result("ORI-A1", passed, detail, ix)


def _ori_a2(ix: Interaction) -> CheckResult | None:
    action = (ix.conversation or {}).get("action")
    if action not in _SCOPED_ACTIONS:
        return None  # not applicable to this action -- contract scopes ORI-A2 to stage/invitation actions
    detail_dict = (ix.conversation or {}).get("detail") or {}
    located = bool(detail_dict.get("stage")) or bool(detail_dict.get("invitationId"))
    return _result("ORI-A2", located, f"detail={detail_dict}", ix)


def _gui_a1(ix: Interaction) -> CheckResult:
    requirements = (ix.conversation or {}).get("requirements") or []
    sentence_shaped = [r for r in requirements if isinstance(r, str) and len(r.split()) >= 3]
    passed = len(requirements) > 0 and len(sentence_shaped) == len(requirements)
    return _result("GUI-A1", passed, f"{len(requirements)} requirement(s), {len(sentence_shaped)} sentence-shaped", ix)


def _ori_a3(ix: Interaction) -> CheckResult:
    """Policy v3 (evals/policy.py judgement call 4): `SubmitResponse.display` now travels on
    *every* commit, not only a handoff -- checked exactly like `ORI-H1` checks a handoff's own.
    Read straight off `captured_text` (`harness/driver.py`'s `_capture_commit_voice`), not
    `ix.conversation` -- `_agent_cycle_conversation` (harness/interactions.py) never re-derives
    this field itself, the same pattern `_agent_refusal_checks` already uses for `rule`/`remedy`.
    """
    display = ix.captured_text.get("commit_display", "").strip()
    passed = len(display) >= 10
    return _result("ORI-A3", passed, f"display={display!r}", ix)


def _gui_a3(ix: Interaction) -> CheckResult:
    """Policy v3's literal contract (evals/policy.py judgement call 4): "when it points at a
    screen, contains a resolvable URL" -- conditional, not "always actionable". Live-confirmed
    (2026-08-30 eval-all run) that reusing `GUI-H1`'s guidance-verb heuristic here was a
    miscalibration: many commit continuations describe what the *agent* does next ("next, put
    your solution into words too", "Your roles are saved.") rather than instructing the founder,
    so requiring a verb failed legitimate, correct copy across every scenario. This check is
    about the door alone -- when a URL is present, it must be well-formed (`http(s)://`); when
    none is present, there is nothing to fail. The click-through itself is `FounderBrowser.
    follow_display_url`, a scenario assertion no static sweep can stand in for."""
    display = ix.captured_text.get("commit_display", "").strip()
    url_match = policy._URL_RE.search(display)
    passed = url_match is None or url_match.group(0).startswith(("http://", "https://"))
    detail = f"display={display!r}, url={'none' if url_match is None else url_match.group(0)}"
    return _result("GUI-A3", passed, detail, ix)


def _cla_a2_commit(ix: Interaction) -> CheckResult:
    """Policy v3: `CLA-A1`'s own recalibration said the vocabulary sweep follows founder-facing
    wire text wherever it travels -- `display` now travels on every commit, so this is `CLA-A1`'s
    companion for the hop `CLA-A1` itself does not cover (that one stays scoped to a handoff's
    `outcome`, per policy v2's judgement call 3)."""
    display = ix.captured_text.get("commit_display", "")
    violations = policy.clarity_violations(display)
    return _result("CLA-A2", not violations, f"violations={violations}" if violations else "clean", ix)


def _agent_cycle_checks(ix: Interaction) -> list[CheckResult]:
    """Policy v2 (evals/policy.py judgement call 3; design §2): `instruction.content` and
    `requirements` are agent-facing method/payload guidance, not founder-facing protocol text --
    so an agent-cycle interaction no longer carries `CLA-A1` or `GUI-A2` at all. Both checks move
    to sweep `display` instead (see `_agent_handoff_checks`/`_gui_a2_handoff` below), which only an
    agent-handoff interaction has. `GUI-A1` (presence/sentence-shape of `requirements`) and
    `ORI-A1` (non-empty instruction) are presence checks, not vocabulary sweeps, and are untouched.

    Policy v3 (judgement call 4) adds `ORI-A3`/`GUI-A3`/`CLA-A2`, scored only when a
    `commit_display` was actually captured -- a bundle scored before `SubmitResponse.display`
    existed (or a step that never reached a successful commit, e.g. a refusal-only interaction)
    emits none of the three rather than three automatic failures.
    """
    results = [_ori_a1(ix)]
    a2 = _ori_a2(ix)
    if a2 is not None:
        results.append(a2)
    results.append(_gui_a1(ix))
    if ix.captured_text.get("commit_display"):
        results.append(_ori_a3(ix))
        results.append(_gui_a3(ix))
        results.append(_cla_a2_commit(ix))
    return results


# ----------------------------------------------------------------------------------- agent-handoff

def _ori_h1(ix: Interaction) -> CheckResult:
    display = ((ix.conversation or {}).get("outcome") or "").strip()
    passed = len(display) >= 10
    return _result("ORI-H1", passed, f"display={display!r}", ix)


def _gui_h1(ix: Interaction) -> CheckResult:
    display = ((ix.conversation or {}).get("outcome") or "").strip()
    lower = display.lower()
    passed = bool(display) and any(verb in lower for verb in _GUIDANCE_VERBS)
    return _result("GUI-H1", passed, f"display={display!r}", ix)


def _cla_a1_handoff(ix: Interaction) -> CheckResult:
    display = (ix.conversation or {}).get("outcome") or ""
    violations = policy.clarity_violations(display)
    return _result("CLA-A1", not violations, f"violations={violations}" if violations else "clean", ix)


def _gui_a2_handoff(ix: Interaction) -> CheckResult:
    """Policy v2's new home for `GUI-A2`: the one protocol text a founder actually receives is a
    handoff's `display`, so this is where "founder-phrased, no raw enums/JSON" (GUIDANCE's half of
    the sweep -- CLA-A1 asks the same question under CLARITY) now lives, instead of `requirements`.
    """
    display = (ix.conversation or {}).get("outcome") or ""
    violations = policy.clarity_violations(display)
    return _result("GUI-A2", not violations, f"violations={violations}" if violations else "founder-phrased", ix)


def _agent_handoff_checks(ix: Interaction) -> list[CheckResult]:
    return [_ori_h1(ix), _gui_h1(ix), _cla_a1_handoff(ix), _gui_a2_handoff(ix)]


# --------------------------------------------------------------------------------- agent-refusal

def _ori_r1(ix: Interaction) -> CheckResult:
    """S-007 (design §3): the refusal names a rule a lost agent could look up -- one of the
    literal rule tokens the protocol actually uses (policy.RULE_LITERALS plus the aggregate's own
    short business-rule codes, e.g. A9 -- any non-blank rule name counts, since the full catalogue
    of aggregate rule ids is open-ended by design and this check is about *presence*, not
    membership in a closed list)."""
    rule = (ix.captured_text.get("rule") or "").strip()
    return _result("ORI-R1", bool(rule), f"rule={rule!r}" if rule else "no rule name captured", ix)


def _gui_r1(ix: Interaction) -> CheckResult:
    """S-007: is the *remedy* -- not the problem statement -- present and sentence-shaped? A
    remedy that only restates the problem tells a lost agent what's wrong, not what to do; the
    sentence-shape heuristic is the same generous one GUI-A1 uses for `requirements` (>= 3 words),
    deliberately not a stricter imperative-mood parser (a false negative here is a harsher score
    than the design intends, per GUI-H1's own docstring for the same trade-off). Agent-facing text
    (like `requirements`/`instruction.content` under policy v2) -- never vocabulary-swept; there is
    no CLA-R1.
    """
    remedy = (ix.captured_text.get("remedy") or "").strip()
    problem = (ix.captured_text.get("problem") or "").strip()
    sentence_shaped = len(remedy.split()) >= 3
    not_just_the_problem = policy.normalize(remedy) != policy.normalize(problem)
    passed = bool(remedy) and sentence_shaped and not_just_the_problem
    return _result("GUI-R1", passed, f"remedy={remedy!r}", ix)


def _agent_refusal_checks(ix: Interaction) -> list[CheckResult]:
    return [_ori_r1(ix), _gui_r1(ix)]


# ------------------------------------------------------------------------------------- arrival

def _cla_ar1(ix: Interaction) -> CheckResult:
    """Policy v4 (evals/policy.py judgement call 6): the arrival read's own server-composed
    greeting (`harness/driver.py`'s `arrive()`, captured under `arrival_display`) -- non-empty
    (the same >= 10 char threshold `ORI-H1`/`ORI-A3` use) and free of a raw project id in its own
    *prose*. A door the greeting names (a URL, exactly like a handoff's own `display` -- `GUI-A3`'s
    "when it points at a screen, contains a resolvable URL") legitimately carries the project id as
    a path segment; that is a door, not a leak, and is stripped first (`policy._strip_urls`, the
    same exemption `clarity_violations` already gives every enum/field-name sweep) before the raw-
    UUID check runs -- live-confirmed 2026-08-30 (eval-all run): an earlier draft of this check
    swept the whole sentence including its own embedded door and failed a founder greeting that
    named nothing but a project by name plus a resolvable link -- the same miscalibration `GUI-A3`'s
    own docstring records for reusing `GUI-H1`'s heuristic verbatim."""
    display = ix.captured_text.get("arrival_display", "").strip()
    non_empty = len(display) >= 10
    id_free = policy.UUID_RE.search(policy._strip_urls(display)) is None
    passed = non_empty and id_free
    detail = f"display={display!r}, non_empty={non_empty}, id_free={id_free}"
    return _result("CLA-AR1", passed, detail, ix)


def _arrival_checks(ix: Interaction) -> list[CheckResult]:
    return [_cla_ar1(ix)]


# ---------------------------------------------------------------------------------------- ui-visit

def _need_exists(ix: Interaction) -> bool | None:
    """Whether GUI-U1 expects a next-step affordance on this screen -- resolved entirely from
    this interaction's own captured_text (the get_state snapshot browser.py stashed under
    "state", plus the "screen"/"stage" it was captured for), per analysis finding A1: the check
    is self-contained, never reaching back out to a live driver at scoring time.

    Returns None (skip the check) when no state snapshot was captured -- happens for a bundle
    scored before this capture existed, or a screen where the harness couldn't reach get_state --
    rather than guessing.
    """
    raw_state = ix.captured_text.get("state")
    screen = ix.captured_text.get("screen")
    if not raw_state or not screen:
        return None
    try:
        state = json.loads(raw_state)
    except json.JSONDecodeError:
        return None
    stages = {s.get("stage"): s for s in state.get("stages", []) if isinstance(s, dict)}
    if screen == "stage":
        stage = ix.captured_text.get("stage")
        return stages.get(stage, {}).get("need") is not None
    if screen == "overview":
        return any(s.get("need") is not None for s in stages.values())
    if screen == "invitations":
        return (state.get("awaitingInterpretation") or 0) > 0 or \
            any(s.get("need") == "INVITE" for s in stages.values())
    if screen == "invite":
        # You navigate here precisely because an INVITE need exists; the form itself is the
        # affordance being acted on.
        return True
    if screen == "brief":
        # Terminal screen -- by design, nothing further to do.
        return False
    return None


def _cla_u3(ix: Interaction) -> CheckResult | None:
    """Policy v3: `verdictLabel`/`needLabel`, read off the same `state` JSON `GUI-U1`/`_need_exists`
    already parse (`FounderBrowser._capture_common`'s `get_state` snapshot -- analysis finding A1's
    mechanism, reused rather than re-plumbed). Once a stage is `approved`, its `verdictLabel` must
    be present and enum-clean; once its `need` is present and not `EVIDENCE` (`FounderVoice.
    needLabel` deliberately returns `null` there -- `verdictLabel` already carries the word),
    `needLabel` must be present and enum-clean too. Returns `None` (skip) when no `state` snapshot
    was captured, the same "don't guess" stance `_need_exists` takes.
    """
    raw_state = ix.captured_text.get("state")
    if not raw_state:
        return None
    try:
        state = json.loads(raw_state)
    except json.JSONDecodeError:
        return None
    problems: list[str] = []
    for stage in state.get("stages", []) or []:
        if not isinstance(stage, dict):
            continue
        name = stage.get("stage")
        if stage.get("approved"):
            label = stage.get("verdictLabel")
            if not label or not str(label).strip():
                problems.append(f"{name}: approved but verdictLabel missing")
            elif policy.clarity_violations(label):
                problems.append(f"{name}: verdictLabel {label!r} leaks {policy.clarity_violations(label)}")
        need = stage.get("need")
        if need is not None and need != "EVIDENCE":
            need_label = stage.get("needLabel")
            if not need_label or not str(need_label).strip():
                problems.append(f"{name}: need={need} but needLabel missing")
            elif policy.clarity_violations(need_label):
                problems.append(f"{name}: needLabel {need_label!r} leaks {policy.clarity_violations(need_label)}")
    return _result("CLA-U3", not problems, "; ".join(problems) if problems else "clean", ix)


def _ori_u3(ix: Interaction) -> CheckResult | None:
    """Policy v4 (evals/policy.py judgement call 6): the People nav section, while locked, must
    carry its own founder-worded one-line why -- captured by `harness/browser.py`'s
    `_capture_common` as `locked_reason` (`.side-nav__locked-why`) whenever a screen's side nav
    renders People locked. Skipped (None) when this visit's nav wasn't locked at all (the key is
    only ever captured when that element renders -- SideNav.tsx pairs `.side-nav__item--locked`
    with `.side-nav__locked-why` unconditionally) or on a pre-round-2 bundle that never captured
    the nav at all."""
    locked_reason = ix.captured_text.get("locked_reason")
    if locked_reason is None:
        return None
    why = locked_reason.strip()
    passed = len(why) >= 5 and not policy.clarity_violations(why)
    return _result("ORI-U3", passed, f"locked_reason={why!r}" if why else "no locked-People why captured", ix)


def _gui_u2(ix: Interaction) -> CheckResult | None:
    """Policy v4: the pointer-to-agent variant of the founder UI's own next-step box
    (`NextBox`'s `.next.agent`, "Now work out your solution with your Keel agent.") must be a
    sentence, not a link -- the absence of a URL is itself the assertion (founder-experience
    design §4 item 4). Captured separately from the generic `affordance` sweep as
    `pointer_to_agent` (`harness/browser.py`'s `_capture_common`, scoped to `.next.agent` alone) so
    this check never has to guess which affordance text is the agent variant. `_capture_common`
    itself already asserts live (DOM-level) that no `<a>` renders inside `.next.agent` -- this is
    the complementary text-level sweep the generic scoring pipeline can run on any bundle. Skipped
    (None) when this visit never rendered the pointer-to-agent variant at all."""
    pointer = ix.captured_text.get("pointer_to_agent")
    if pointer is None:
        return None
    has_url = policy._URL_RE.search(pointer) is not None
    return _result("GUI-U2", not has_url, f"pointer_to_agent={pointer!r}", ix)


def _ui_visit_checks(ix: Interaction) -> list[CheckResult]:
    results = []
    screen = ix.captured_text.get("screen")
    # ORI-U1 asks "does this screen orient the founder about *which project* this is" -- round 2's
    # own `/login`/`/setup` screens (`FounderBrowser.log_in`, `evals/conftest.py`'s virgin-instance
    # check) are visited before any project is even in view, so there is no project identity marker
    # for them to carry and none should be expected -- live-confirmed 2026-08-30 (eval-all run):
    # an earlier draft failed every scenario's own login step on exactly this inapplicable ground.
    if screen not in ("login", "setup"):
        identity = ix.captured_text.get("identity", "")
        results.append(_result("ORI-U1", bool(identity.strip()),
                                f"identity={identity!r}" if identity else "no project identity captured", ix))

    if ix.captured_text.get("screen") == "stage":
        stage_identity = ix.captured_text.get("stage_identity", "")
        results.append(_result("ORI-U2", bool(stage_identity.strip()),
                                f"stage_identity={stage_identity!r}" if stage_identity else "no stage identity captured", ix))

    need_exists = _need_exists(ix)
    if need_exists is not None:
        affordance = ix.captured_text.get("affordance", "").strip()
        passed = (not need_exists) or bool(affordance)
        detail = f"need_exists={need_exists}, affordance={'present' if affordance else 'absent'}"
        results.append(_result("GUI-U1", passed, detail, ix))

    cla_u3 = _cla_u3(ix)
    if cla_u3 is not None:
        results.append(cla_u3)

    ori_u3 = _ori_u3(ix)
    if ori_u3 is not None:
        results.append(ori_u3)

    gui_u2 = _gui_u2(ix)
    if gui_u2 is not None:
        results.append(gui_u2)

    combined_text = "\n".join(v for k, v in ix.captured_text.items() if k not in ("state",))
    enum_violations = policy.enum_violations(combined_text)
    results.append(_result("CLA-U1", not enum_violations, f"violations={enum_violations}" if enum_violations else "clean", ix))
    structural_violations = policy.structural_violations(combined_text)
    results.append(_result("CLA-U2", not structural_violations, f"violations={structural_violations}" if structural_violations else "clean", ix))
    return results


# ---------------------------------------------------------------------------------- participant-page

def _ori_p1(ix: Interaction) -> CheckResult:
    text = ix.captured_text.get("participant_page", "")
    passed = "asked if you" in text.lower() and len(text.strip()) > 30
    return _result("ORI-P1", passed, "founder name + about-line intro found" if passed
                   else "consent intro (founder name / about-line) not found", ix)


def _gui_p1(ix: Interaction) -> CheckResult:
    submitted = any(str(e.get("name", "")).startswith("participant submits") and e.get("ok")
                     for e in ix.entries)
    return _result("GUI-P1", submitted, "reached submit and the thank-you confirmed" if submitted
                   else "never reached a successful submit step", ix)


def _participant_page_checks(ix: Interaction) -> list[CheckResult]:
    text = ix.captured_text.get("participant_page", "")
    enum_violations = policy.enum_violations(text)
    structural_violations = policy.structural_violations(text)
    return [
        _ori_p1(ix),
        _gui_p1(ix),
        _result("CLA-U1", not enum_violations, f"violations={enum_violations}" if enum_violations else "clean", ix),
        _result("CLA-U2", not structural_violations, f"violations={structural_violations}" if structural_violations else "clean", ix),
    ]


# ------------------------------------------------------------------------------------- chat-visit

def _cla_c1(ix: Interaction) -> CheckResult:
    """Policy v5 (evals/policy.py judgement call 7): the same vocabulary/structural sweep every
    other founder-facing surface gets, run over the chat pane's own rendered turn text and any
    playback table's cell text combined."""
    combined = "\n".join(v for k, v in ix.captured_text.items()
                          if k in ("chat_turns", "chat_playback_table"))
    violations = policy.clarity_violations(combined)
    return _result("CLA-C1", not violations, f"violations={violations}" if violations else "clean", ix)


def _ori_c1(ix: Interaction) -> CheckResult | None:
    """Policy v5: presence-banner honesty -- the pane's own rendered claim (a shown banner means
    "disconnected"; its absence means "connected", design §5/§9's own words) must agree with the
    relay's own wire truth at the same moment (`chat_presence_state`, `ChatPane.capture` reading
    `FounderRelay.presence()` live). Skipped (None) when no presence reader was wired in."""
    raw_state = ix.captured_text.get("chat_presence_state")
    if not raw_state:
        return None
    try:
        state = json.loads(raw_state)
    except json.JSONDecodeError:
        return None
    banner_shown = bool(ix.captured_text.get("chat_presence_banner", "").strip())
    wire_connected = bool(state.get("connected"))
    honest = banner_shown != wire_connected
    detail = f"banner_shown={banner_shown}, wire_connected={wire_connected}"
    return _result("ORI-C1", honest, detail, ix)


def _gui_c1(ix: Interaction) -> CheckResult | None:
    """Policy v5: every link a chat turn carries must be well-formed (`http(s)://`) -- `GUI-A3`'s
    own door check, mirrored onto the chat surface. Skipped (None) when no agent turn ever carried
    a link at all."""
    raw_links = ix.captured_text.get("chat_turn_links")
    if not raw_links:
        return None
    links = [l for l in raw_links.splitlines() if l.strip()]
    malformed = [l for l in links if not l.startswith(("http://", "https://"))]
    return _result("GUI-C1", not malformed, f"malformed={malformed}" if malformed else f"{len(links)} link(s), all well-formed", ix)


def _chat_visit_checks(ix: Interaction) -> list[CheckResult]:
    results = [_cla_c1(ix)]
    ori_c1 = _ori_c1(ix)
    if ori_c1 is not None:
        results.append(ori_c1)
    gui_c1 = _gui_c1(ix)
    if gui_c1 is not None:
        results.append(gui_c1)
    return results


# --------------------------------------------------------------------------------------- fidelity

def _fid_checks(interactions: list[Interaction],
                 facts: dict[str, Fact]) -> tuple[dict[str, list[CheckResult]], list[Interaction]]:
    results: dict[str, list[CheckResult]] = {}
    extra: list[Interaction] = []
    unresolved = {"bucket": None}  # mutable cell; created lazily so a fully-resolved run adds no synthetic card

    def bucket() -> Interaction:
        if unresolved["bucket"] is None:
            ix = Interaction(id="FID-UNRESOLVED", type="fidelity-summary",
                              title="Fidelity checks with no matching interaction", party="stack")
            unresolved["bucket"] = ix
            extra.append(ix)
            results[ix.id] = []
        return unresolved["bucket"]

    for fact_id, fact in facts.items():
        for hop in fact.hops:
            check_id = f"FID-{fact_id}-{hop}"
            weight = policy.fid_weight(fact.kind, hop)
            waiver = policy.waiver_for(fact.kind, hop)
            candidate_types = policy.HOP_INTERACTION_TYPES.get(hop, ())
            candidates = [ix for ix in interactions if ix.type in candidate_types and ix.captured_text.get(hop)]

            if not candidates:
                target = bucket()
                results[target.id].append(_result(
                    check_id, False,
                    f"hop '{hop}' was never captured (no {candidate_types} interaction rendered it)",
                    target, attribute="FIDELITY", weight=weight, fact_id=fact_id, hop=hop,
                ))
                continue

            if waiver is not None:
                target = candidates[-1]
                results.setdefault(target.id, []).append(_result(
                    check_id, True, f"waived: {waiver['reason']}", target,
                    attribute="FIDELITY", weight=weight, waived=waiver, fact_id=fact_id, hop=hop,
                ))
                continue

            matched = next((c for c in candidates if policy.fact_reaches_hop(fact.text, c.captured_text[hop])), None)
            if matched is not None:
                results.setdefault(matched.id, []).append(_result(
                    check_id, True, f"fact found verbatim at '{hop}'", matched,
                    attribute="FIDELITY", weight=weight, fact_id=fact_id, hop=hop,
                ))
            else:
                target = candidates[-1]
                results.setdefault(target.id, []).append(_result(
                    check_id, False, f"fact not found verbatim at '{hop}' (checked {len(candidates)} interaction(s))",
                    target, attribute="FIDELITY", weight=weight, fact_id=fact_id, hop=hop,
                ))
    return results, extra


# ------------------------------------------------------------------------------------------ engine

def evaluate(interactions: list[Interaction],
             facts: dict[str, Fact] | None = None) -> tuple[list[Interaction], dict[str, list[CheckResult]]]:
    """Runs every applicable policy check over `interactions` plus the fact-registry-driven
    FID-* checks. Returns (interactions-including-any-synthetic-buckets, results-by-interaction-
    id) -- the caller (harness/scoring.py) rolls this up into category/run scores.
    """
    interactions = list(interactions)
    results: dict[str, list[CheckResult]] = {ix.id: [] for ix in interactions}

    for ix in interactions:
        if ix.type == "agent-cycle":
            results[ix.id].extend(_agent_cycle_checks(ix))
        elif ix.type == "agent-handoff":
            results[ix.id].extend(_agent_handoff_checks(ix))
        elif ix.type == "ui-visit":
            results[ix.id].extend(_ui_visit_checks(ix))
        elif ix.type == "participant-page":
            results[ix.id].extend(_participant_page_checks(ix))
        elif ix.type == "agent-refusal":
            results[ix.id].extend(_agent_refusal_checks(ix))
        elif ix.type == "arrival":
            results[ix.id].extend(_arrival_checks(ix))
        elif ix.type == "chat-visit":
            results[ix.id].extend(_chat_visit_checks(ix))

    fid_results, extra = _fid_checks(interactions, facts or {})
    for iid, checks in fid_results.items():
        results.setdefault(iid, []).extend(checks)
    interactions.extend(extra)
    return interactions, results
