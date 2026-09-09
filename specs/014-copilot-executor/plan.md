# Plan: Every mark, on both hosts

**Input**: [spec.md](spec.md). **Design of record**: keel-cloud
`canon/designs/keel-skill-design.md` §5 (two hosts), §5.4 (`CopilotExecutor`), §5.5 (the
four-part "supported" gate, whose third part is this repository's).

## The shape of the change

The instruction eval is six hundred lines that assemble a prompt, send it, and score what comes
back. Exactly one of those three verbs is host-specific, and the plan is to keep it that way.

```
corpus  ─┐
contract ├─> context.py ─> prompts.payload_for ──┐
marks   ─┘                                       │
                                                 ├─> prompts.render(host) ──> runner.ask ──> score
        keel-runtime build_prompt ────────────────┘        │                     │
        keel-runtime _render_copilot_prompt ───────────────┘                     │
                                                                                 │
        get_executor(host)  ──────────────────────────────────────────────────────
```

Everything left of `render` is one thing on both hosts, and must be: a comparison whose sides were
sent different contexts, different contracts or different marks measures nothing. Everything right
of `ask` is one thing on both hosts, including the tie-breaking judge, for the same reason. What
the host decides is which of keel-runtime's two renderings comes out of `render`, which CLI
`preflight` requires, and which executor `get_executor` hands back.

## Five decisions, and why each went the way it did

**1. `get_executor`, not a class name.** `run.py` used to say `executor_module.ClaudeCodeExecutor(
home=run_dir)`. A two-host version of that line is a `{host: class}` table, and this repository has
recorded the cost of holding its own copy of something a sibling owns five times
(`runs/DRIFT.md` #33, #36, #41, #44, #45). `get_executor` is the function `keel_runtime.cli` itself
calls for `--executor`, so the alias, the caps and the constructor arguments stay one decision made
once, in the repository that owns them. The same reasoning puts the binary name in
`EXECUTOR_BINARIES` rather than in a dict here: `claude-code` is a host and `claude` is a binary,
and this repo must not be the second place that knows it.

**2. The prompt is rendered per host, through the runtime's own renderer.** This is the one place
the design says the two hosts genuinely differ, and it would have been easy to get wrong in the
comfortable direction — record `build_prompt`'s output in both bundles and call the prompt
"shared". It is shared *as a body*; the `SYSTEM` and `RESPONSE` sections are real text that Copilot
really receives. So `render` takes the host, and a keel-runtime without `_render_copilot_prompt`
stops the run rather than substituting the other host's prompt. Underscore-prefixed names across a
repository boundary are a smell; a second copy of a prompt renderer is a fault, and this trade is
the same one `prompts.load_runtime` already made.

**3. A `manifest.json`, written twice.** The bundle had `versions.json` (the siblings),
`verdict.json` (the marks) and `scorecard.json` (the numbers) — and nothing written *before* the
first call. A run that dies at case one now still names its host, its CLI, its rubric and its
caps. It is written again at the end only to fill in the model the CLI reported, which is not
knowable until something answered.

**4. Dollars and premium requests are never converted.** `CopilotExecutor` deliberately carries no
`total_cost_usd` (C-7). Summing `answer.total_cost_usd or 0.0` across a Copilot run therefore
produces `$0.00`, which reads as *free* beside a run that really spent a hundred and thirty-one
requests of the founder's plan. The verdict carries one field or the other, `_spend` renders
whichever it has, and neither is derived from the other.

**5. The register is titled first, not last.** The register is the page a person reads with their
own judgement, and register — the thing it is for — is precisely what two different models differ
on. A reader comparing Copilot's paragraphs against a memory of Claude's without being told would
be the most expensive quiet mistake in the bundle, so the host is in the `<title>`, in the `<h1>`
and in the first line under it. `rescore` reads the host off the bundle for the same reason: a
register rewritten under a future rubric must not come back wearing the wrong name.

## What is deliberately not built

- **No `HOST=both`.** Two hosts' runs are different measurements; a target that produced them in
  one invocation would invite one summary line over the pair, which is the one thing §5.5 forbids.
- **No mark moved, and no `MARKS_VERSION` bump.** §5.5: *"lower a mark — **not** acceptable; a mark
  that moves to accommodate a result has stopped being a mark."* The rubric is what makes the two
  runs comparable at all.
- **No `--model` pinned.** C-5 asks for one and keel-runtime spec 005 measured that this account's
  CLI accepts none. `KEEL_COPILOT_MODEL` is the way in when a machine has a slug that works; the
  bundle records `pinned_model: null` rather than pretending.
- **No retry, no second pass, no iteration.** One run, at `N=1`, on the founder's own plan.

## Order of work

1. `prompts.render`/`build_cases` take the host (nothing can be measured before the prompt is
   right).
2. `runner.preflight`/`binary_for`/`_copilot_ready` take the host.
3. `run.py`: `--host`, `get_executor`, the model block, the manifest, the premium sum.
4. `report.py`: `start_bundle` suffix, `write_manifest`, `_spend`, both pages titled.
5. `rescore.py`: the host survives a re-score.
6. `Makefile`: `HOST`, documented at the target.
7. `tests/test_instruction_host.py`.
8. Two dry runs — one per host — then the single real Copilot run.
