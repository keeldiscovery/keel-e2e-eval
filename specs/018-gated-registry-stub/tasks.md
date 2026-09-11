# Tasks: the gated registry stub

**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md) | **Branch**:
`remote-profile-and-gated-stub`

`make unit`: **638** before, **712** after (34 of the new ones are this spec's), green. No stack
was started; no model was called; nothing was pushed to any registry.

## Phase 1 — read before writing anything

- [X] T001 keel-cloud `canon/designs/e2e-matrix-design.md` in full — §2 (what is true today), §4
      (the gate and the registry, the whole section), §5.3 (what a cell is), §6.4 (where a verdict
      is recorded), §11 (what changes by repository), §12 (M4, M5, M6, M7).
- [X] T002 keel-cloud `canon/designs/google-sign-in-design.md` §10 — the stub's existing contract,
      §10.1's four routes, §10.2's picker and `login_hint`, §10.8's prohibitions. **The contract
      this feature may not break**, and the reason `tests/test_stub_oidc.py` is untouched.
- [X] T003 `stack/stub_oidc/server.py`, `keys.py`, `__main__.py`, `stack/oidc.py`,
      `tests/test_stub_oidc.py` — read in full. Finding that shaped the plan: `__main__` imports
      `stack.oidc` for its defaults, which drags `requests`, `stack.config` and `stack.processes`
      into anything that runs the stub.
- [X] T004 `stack/containers/acceptance/Dockerfile` — the house shape for a container in this
      repository, and `runs/DRIFT.md` #50 on why a platform belongs in the cache key.

## Phase 2 — the package stands alone

- [X] T005 `stack/stub_oidc/identity.py`: the `Identity` record (with the new `label` field), the
      client id and secret, `FOUNDER_A`/`FOUNDER_B`/`STUB_IDENTITIES`.
- [X] T006 `stack/oidc.py` re-exports all five names, and `issuer_url` reads the config's own base
      URL (shared with spec 017). Spec 015's tests, which assert `oidc.FOUNDER_A` and friends,
      pass unedited — the proof that the move was a move and not a rewrite.
- [X] T007 `stack/stub_oidc/__main__.py` imports from `identity.py` only. Verified by reading the
      import list: the package now imports nothing outside itself.

## Phase 3 — the registry

- [X] T008 `stack/stub_oidc/registry.py`: `Entry` (identity + `registered_by` + `registered_at`),
      `Registry` (file or memory, newest-first, atomic write), `RegistryError` (status + message).
- [X] T009 The derived `sub` (`cell-<id>`), the narrow id pattern, the reserved built-in ids, and
      **label-only** relabelling.
- [X] T010 `StubIssuer.registry`/`gated`, `identities` as a property, `may_sign_in_as` (M6) and
      `may_register`.

## Phase 4 — the routes and the gate

- [X] T011 `GET /identities`, `POST /identities`, `PATCH /identities/<id>` on the handler, each
      behind the gate when gated.
- [X] T012 The gate at the top of `/authorize`, and the authorization of the *choice* after the
      identity is resolved.
- [X] T013 The picker: registrations newest first, built-ins last, `<p class="label">` after each
      registered button, escaped.
- [X] T014 **A defect found while testing**: a refusal that did not drain the request body poisoned
      the next request on a keep-alive connection. `do_POST`/`do_PATCH` read the body first now;
      `test_a_refused_write_does_not_poison_the_keep_alive_connection` is the regression.

## Phase 5 — the image

- [X] T015 `stack/containers/oidc/Dockerfile`: `python:3.12-slim`, `openssl` (the one external tool
      `keys.py` uses, and installed explicitly rather than assumed), two `COPY`s, a volume for the
      key and the registry, `ENTRYPOINT ["python", "-m", "stack.stub_oidc"]`, and a `CMD` that is
      the staging invocation.
- [X] T016 `make oidc-image TAG=<tag> [PLATFORM=] [PUSH=1]` — `linux/arm64` by default (the box is
      a `t4g.micro`), `DOCKER_HOST` defaulting to the founder's Colima socket. **Additive only**:
      the Makefile's existing targets are untouched, because another branch is in this file at the
      same time.
- [X] T016a **Measured, and it changed the target**: the design says buildx, and this Mac's Docker
      (29.5.2, through Colima) answers `docker: unknown command: docker buildx` — the same finding
      `runs/DRIFT.md` #50 records for the acceptance bed. So the target probes: buildx where there
      is one (a CI runner), the legacy builder with `--platform` where there is not, and it prints
      which it used. A target that assumed buildx would have failed on the machine it was written
      on.
- [X] T017 **The image was built and run**, `linux/arm64`, on this Mac (2026-09-10, legacy builder
      against Colima). Measured against the running container: discovery **200**; `/authorize`
      with no gate header **403**; `POST /identities` as `harness` **201** with
      `"sub": "cell-cell-1"` derived and `"registered_by": "harness"` recorded; the startup line
      names the registry file and `gated`. No `pip install` anywhere in the build. Pushing it to
      ECR and bringing it up behind Caddy is step 2 of the design's §13 order and lives in
      keel-cloud's spec `036-staging-twin`.

## Phase 6 — the tests

- [X] T018 `tests/test_stub_oidc_registry.py`, 34 stackless tests on a real ephemeral socket:
      the ungated twins (four), the gate (six), the registry rules (nine), the picker (five), the
      file (five), the defaults (two), plus the keep-alive regression.
- [X] T019 `tests/test_stub_oidc.py` **unedited and green** — the whole of FR-003.
- [X] T020 `make unit`: 712 passed.

## What the next spec needs from this one

- keel-cloud `036-staging-twin` builds this image, pushes it as `keel-oidc:<sha>`, mounts
  `/opt/keel/oidc` at `/var/lib/keel-oidc`, and puts the §4.2 Caddy block in front of it.
- Spec `020-matrix-workflow` is what actually calls `POST /identities` eighteen times a week;
  spec 017's `stack/remote.py` is the code that does it.
