# The Shaping Gauntlet — Eval Design

**Status**: Proposed → implementing (founder's direct ask: "we start with vague and we prod the
founder to come up with quantifiable ones — in all stages"). Extends eval-scoring-design.md,
whose §6 reserved exactly this seam: methodology efficacy is not machine-checkable by scripted
drivers, so it gets its own lane. Downstream of hypothesis-shaping-design.md (v2,
instruction-only) — this eval is that feature's proof.

## 1. Two layers, honestly separated

**Layer 1 — structural, joins `make eval-all` (deterministic).** The methodology is delivered
on the wire, and that is checkable: the CREATE / FRAME / INTRODUCE_ASSUMPTIONS issuances'
`instruction.content` must carry the shaping mandates — quantifiability probes for the problem,
the mechanism-in-a-sentence test for the solution, buyer/price-or-unknown for commercial, the
normalization pass for assumptions. One scenario leg (in S-001's opening or its own small
S-010 slot) asserting marker phrases per stage. Cheap, honest about what it proves: delivery,
not efficacy.

**Layer 2 — behavioral, opt-in `make eval-shaping` (LLM in the loop, never CI).** A real agent
(the locally installed `claude` CLI, headless, loaded with the real SKILL.md and the real MCP
stack — the playground's shape, automated) converses with a **scripted founder simulator**:

- The simulator opens vague, per stage: *"restaurants struggle with inventory"* → *"I'll build
  an app for it"* → *"I guess people would pay for it."*
- It holds the quantified facts hostage: they are released only when the agent's turn matches
  the probe that earns them (keyword-matched — asked who → "independent restaurant managers";
  how often → "every month-end close"; cost → "about 90 minutes each time"; mechanism →
  the scan-and-compare description; price → "maybe $99 a month, honestly not sure").
- A fact never asked for is never given. A founder simulator never volunteers.
- The loop is `claude -p` + `--resume`: eval sends a founder turn, reads the agent's reply,
  keyword-routes the next founder line, bounded at ~15 turns per stage.

**The verdict is deterministic even though the conversation is not.** After the session, the
eval reads the *stack* (the recorded frames and beliefs — what actually got submitted) plus the
transcript, and scores:

| Check | Passes when |
|---|---|
| SHP-1 problem quantified | the recorded problem claim contains the held-hostage who/frequency/cost facts — proof the agent asked |
| SHP-2 no faked precision | nothing quantified appears that the simulator never released |
| SHP-3 solution mechanism | the solution claim says what changes in the workflow, not a product label |
| SHP-4 commercial honesty | buyer + model recorded; price either the released belief or plainly unknown — never invented |
| SHP-5 vague-word ban | recorded beliefs contain no undefined bad/inefficient/important/useful/easy |
| SHP-6 no near-duplicates | pairwise normalized token overlap across a stage's beliefs below threshold |
| SHP-7 unknowns surfaced | facts the simulator refused to know appear as named unknowns / worth-knowing, not as numbers |

Score: 5 × weighted pass fraction, its own `SHAPING` category, standard run bundle (transcript
of the whole conversation, screenshots not applicable, verdict + scorecard + report).

## 2. Boundaries

- Never in `eval-all`/CI (determinism rule stands); `make eval-shaping` is the founder's
  deliberate, paid, model-in-the-loop run.
- The agent process gets ONLY what a real host gets: SKILL.md, the MCP tools (with the
  harness's agent key), and the founder's words. The simulator's script and fact bank are never
  in its context.
- A failure here is a *methodology* finding (the instruction text isn't strong enough), which
  goes back to keel-cloud's registry — the loop this eval exists to drive.

## 3. Passes

1. **Honesty pass**: layers named for what each proves — delivery vs efficacy — so a green
   Layer 1 can never masquerade as proof the conversation works.
2. **Contamination pass**: the fact-bank lives in the simulator only; the agent earns facts by
   asking, which is the entire measurement.
3. **Determinism-boundary pass**: the nondeterministic thing (the conversation) is quarantined
   in an opt-in lane; the verdict is a pure function of stack state + transcript, so two people
   disagree about a run only by rerunning it, not by reading it differently.
4. **Cost pass**: bounded turns, one scenario, opt-in — the founder chooses when to spend.
5. **Canon pass**: no journey moment changes (this proves §1.1's depth); ledger untouched;
   CANON's process loop gains its judged-lane example.
