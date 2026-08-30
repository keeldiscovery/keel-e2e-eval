# Eval Scoring — Design

**Status**: Proposed. Extends `e2e-eval-design.md` (feature 001, built). That feature answered
*"does the workflow complete?"*; this one answers the user's sharper question: **for a founder
who has never seen the framework, does every interaction tell them where they are and what to do
next — and does everything they type survive every hop without loss?** Scored, per interaction,
out of 5.

## 1. What the built framework has, and doesn't

Has (feature 001): a folder per execution (`runs/<id>/`), screenshots on every browser step, a
step-level `transcript.jsonl`, a regenerable `report.html`, a binary verdict.

Doesn't have — the whole of this feature:
- no notion of an **interaction** (steps are finer-grained plumbing);
- no **rubric**: nothing judges orientation, guidance, fidelity, or clarity;
- no **fact tracing**: nobody checks that what the founder typed reaches the UI, the
  participant, the interpret context, and the brief intact;
- no **score**: verdict is pass/fail, not 4.5/5;
- no visual for **protocol interactions**: the agent↔founder conversation is raw JSON in a
  collapsible block, not something reviewable at a glance.

## 2. Interactions

An **interaction** is one founder-meaningful exchange; steps get an `interaction` tag so the
existing transcript keeps being the single source of truth. Types:

| Type | What it spans | Party |
|---|---|---|
| `agent-cycle` | one issuance: get_next → context → (clarify) → submit → outcome | agent+founder |
| `agent-handoff` | one handoff: reason + display + what the founder was told | agent+founder |
| `ui-visit` | one founder screen visit (overview, stage, invite, invitations, brief) | founder |
| `participant-page` | the stranger's consent + questions + submit | participant |

Every interaction is visually reviewable: `ui-visit`/`participant-page` by their screenshots
(already captured), `agent-cycle`/`agent-handoff` by a **conversation card** the report renders —
instruction and requirements as the agent would voice them, the founder's scripted reply, the
outcome — so "a screenshot of each interaction" holds on both surfaces.

## 3. The rubric — four attributes, deterministic checks

Every check is `{id, attribute, weight, pass, evidence}` where evidence points at step seqs and
screenshot files. No LLM judges anything; each attribute is measured by proxies a machine can
check, and the proxies are the policy (§5).

**ORIENTATION** — *does the founder know where they are?*
- agent-cycle: `instruction.content` non-empty and names its purpose; issuance `detail` locates
  the work (stage / invitation) when the action is stage- or invitation-scoped.
- agent-handoff: `display` non-empty and names the destination (screen or "waiting").
- ui-visit: the screen shows the project identity and its own location cues (stage name on a
  stage page, screen heading elsewhere) — checked via the page objects' selectors.
- participant-page: the stranger sees who is asking (founder display name) and the about-line.

**GUIDANCE** — *does the founder know what to do next?*
- agent-cycle: `requirements` present and founder-phrased (heuristics: sentences, no
  camelCase/JSON field names, no raw enums beyond the two licensed action names).
- agent-handoff: `display` says what to do, not just what happened.
- ui-visit: the screen surfaces a next-step affordance when one exists (need chips, review
  prompt, invite button, "waiting on N" line); terminal/brief screens state the outcome.
- participant-page: question flow reaches submit without dead ends; the thank-you confirms.

**FIDELITY** — *no loss of information, hop by hop.* The scenario declares a **fact registry**:
every founder-entered or participant-entered text gets an id and a set of expected hops.
Default hops per fact kind:

| Fact | Hops checked |
|---|---|
| stage statements | agent echo (get_state/context) → stage screen → brief claims |
| role labels | roles context → stage screen → invite screen |
| assumption texts | assumptions context → stage screen → participant questions → brief lines (per policy) |
| about-line | invite screen → participant page |
| participant answers | interpret `response` context (verbatim) → stage screen evidence view |
| interpretations | verdicts on overview/stage screens |

Matching is normalized (whitespace, quotes, case) but **verbatim-by-default**: a summarized or
truncated rendering counts as loss unless the policy carries an explicit, referenced waiver
(§5) saying that hop is allowed to summarize.

**CLARITY** — *plain English, no internals leaking.* UI pages and founder-facing protocol text
contain no raw enum tokens (`LOAD_BEARING`, `READY_TO_BUILD`, verdict/need/state names…), no
JSON punctuation, no field names — the run-time twin of keel-web's own no-raw-enum sweep, now
also applied to what the agent surface tells the founder. (URL path segments are exempt.)

> **Amendment, 2026-08-30 (003-eval-set, policy v2).** "Founder-facing protocol text" above was
> read too broadly by policy v1: it swept `instruction.content` and `requirements` — an
> agent-cycle issuance's two texts — with the same founder-language yardstick as a handoff's
> `display`. Re-reading the shipped contract (keel-cloud's `ActionSchemas.requirements`, and
> `InstructionRegistry`'s own javadoc: "one line the founder never sees, and one paragraph the
> executing client alone reads") shows `instruction` and `requirements` are addressed to the
> **agent**, not relayed to the founder raw — legitimately naming `CONTRADICTED`, `askedOf`,
> `goingAhead`. The only protocol text a founder actually receives is a handoff's `display`.
>
> Policy v2 therefore narrows CLA-A1's and GUI-A2's protocol-text sweep to `display` only:
> `instruction.content` keeps its presence check (`ORI-A1`: non-empty, names a purpose, never
> vocabulary-swept) and `requirements` keeps its presence/sentence-shape check (`GUI-A1`) — neither
> is swept for raw enums or field names any more. `CLA-A1` and `GUI-A2` both move to sweep a
> handoff's `display` (GUI-A2 is new there; CLA-A1 already checked it). This is a recalibration of
> what "founder-facing" means for this attribute, not a loosened bar: the twenty S-001 failures
> that CLA-A1/GUI-A2 raised against `instruction`/`requirements` under v1 were mismeasurement
> (re-adjudicated as DRIFT #4 — see `runs/DRIFT.md`), and a seeded raw enum in a handoff `display`
> still fails both checks under v2. `POLICY_VERSION` → 2 (`evals/policy.py`); see that module's
> docstring, judgement call 3, for the full mechanics.

## 4. Scoring

- Check results roll up per interaction per attribute: `5 × Σweight(passed) / Σweight`,
  rounded to halves.
- Category score = weighted mean across the interactions that carry that attribute.
- **Run score** = weighted mean of the four categories (weights in policy; fidelity heaviest),
  reported as `X/5` — plus a **completion gate**: a run that did not finish the workflow keeps
  its category scores (they describe what was seen) but the verdict stays failed and the run
  score is capped at 2/5, so a beautiful half-run can't outscore an ugly complete one.
- `scorecard.json` per run: policy version, per-interaction check results with evidence refs,
  category scores, run score. `verdict.json` gains `score` and `policy_version`.
- `report.html` gains: score header (big X/5 + four category bars), per-interaction cards
  (screenshots or conversation card + inline check list), and the scorecard table.

## 5. Policy

`evals/policy.py` is the single versioned home of: check definitions and weights, category
weights, clarity token lists, normalization rules, and **waivers** — each waiver names the hop,
the reason, and a reference. First shipped waiver: brief findings summarize counts
(keel-cloud `api-design.md` §6a records the known gap), so assumption-text fidelity at the
brief hop is waived-with-reference rather than silently passed. `policy_version` starts at
`1`; any change to checks, weights, or waivers bumps it, because scores are only comparable
under one policy.

## 6. What this is not

No LLM-as-judge in evals (determinism rule stands). A qualitative judge pass by the operator
agent over the evidence bundle can be layered later as a separate, explicitly-labeled score;
the deterministic scorecard never depends on it. And this feature changes no product repo:
where a check exposes a product gap (an unclear display string, a leaked enum), that is a
DRIFT.md finding and a low score — never a local workaround.

## 7. Five passes

1. **Reality pass**: reviewed the built harness before designing — the step/interaction
   granularity mismatch surfaced here, and the fix (tag steps, don't restructure the
   transcript) keeps feature 001's report regenerable from the transcript alone.
2. **Measurability pass**: "the founder knows what to do" is not machine-checkable as stated —
   split into presence + founder-phrasing proxies, with the honest boundary drawn in §6
   rather than smuggling an LLM judge into CI.
3. **Fidelity-definition pass**: "no loss" made falsifiable — fact registry, declared hops,
   normalized-verbatim matching, and waivers that must cite a reference; this pass re-found
   api-design §6a's Brief.findings gap from the other side, which is exactly the kind of
   catch the attribute exists for.
4. **Scoring-integrity pass**: scores must be comparable across runs and honest about
   failure — versioned policy, half-point rounding, and the completion gate capping
   incomplete runs at 2/5.
5. **Review-ergonomics pass**: a score nobody can interrogate is noise — every check carries
   evidence refs into the scorecard and the report renders them inline per interaction; the
   conversation card closes the "screenshot of each interaction" promise for the surface that
   has no pixels of its own.

## 8. Open decisions

1. Should GUIDANCE penalize a missing next-step affordance on screens where the aggregate has
   no need (all approved, waiting)? — No: checks are conditional on a need existing; "nothing
   to do, said calmly" is a pass.
2. Half-run scoring cap value (2/5) — a judgement call, adjustable in policy without design
   change.
