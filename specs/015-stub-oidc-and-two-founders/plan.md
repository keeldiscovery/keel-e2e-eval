# Implementation Plan: A stub issuer, and two founders — the first half

**Branch**: `015-stub-oidc-and-two-founders` | **Date**: 2026-09-09 | **Spec**: [spec.md](./spec.md)

**Input**: [spec.md](./spec.md) and keel-cloud `canon/designs/google-sign-in-design.md` §3, §3.6,
§7, §10.1–§10.3, §10.8, §12 step 4, decisions 10 and 11.

**On the artefact set.** `spec.md` + `plan.md` + `tasks.md`, the shape specs 004–013 use. This
feature adds one package, one lifecycle module, one config field, one port per profile, four
environment variables and one stackless test file. It moves no versioned constant:
`POLICY_VERSION` does not move, because nothing about *scoring* changed, and `MARKS_VERSION` does
not move, because the instruction eval does not know this exists.

## Summary

keel-cloud's login is about to become one code path whose only variable is *which issuer*. This
half builds the other end of that variable — an OIDC issuer small enough to read in one sitting,
strict enough that a defect in keel-cloud's half fails rather than passes, and reachable only
because a configuration variable names it.

**Technical approach**: build the issuer, not a fixture. Every refusal in §10.1 is implemented,
the picker is a real page with real buttons, and the ID token is a real RS256 JWS over a real
2048-bit key. The one place this repository economises is the *key*: `openssl` makes it, and the
signing and verifying arithmetic is thirty lines of `pow()` — see the spec's first clarification.

**And it lands alone.** Nothing in keel-cloud reads `KEEL_OIDC_ISSUER` yet, so every assertion
here is against the stub itself. That is the point of §12 step 4: keel-cloud's step starts against
something already proven, and if the two halves are ever bisected apart, this one still passes.

## Technical Context

**Language/Version**: Python 3.11+ for the harness, as ever. The stub is standard library only —
`http.server`, `hashlib`, `secrets`, `base64`, `json`, `urllib.parse`.

**Dependencies**: unchanged, deliberately. `requirements.txt` is not touched. `openssl` is a
system tool the stub shells once per boot and names in its error when it is absent.

**Testing**: `make unit`. There is no scenario in this half — the live proof is a `make up`, four
gates, a `curl` and a fifteen-line walk, recorded in [tasks.md](tasks.md).

**Constraints**: this repo owns no product code, never writes to a sibling repository, and reports
cross-repo gaps as `runs/DRIFT.md` entries with a bundle. None was found: nothing in a sibling was
run against this half.

## The six changes, and why each is where it is

### 1. `stack/stub_oidc/keys.py` — one RSA key, and RS256

Split from the server because it is the only file in this repository doing arithmetic, and because
its decision (openssl for the key, `pow()` for the signature) needs the room to be argued in
place. It exports `verify_rs256` for the test's benefit: the test must verify with the *public*
half alone, or it is asserting that the signer agrees with itself.

### 2. `stack/stub_oidc/server.py` — the four routes

`StubIssuer` holds the state and the answers with no HTTP in it, and `_Handler` is the wire. That
split is what lets a test ask `/token`'s question directly and the same question over a socket.
Roughly the two hundred lines §10.8 asks for, and the prohibitions are quoted in its docstring so
the next person to add something reads them first.

### 3. `stack/oidc.py` — the lifecycle, and the identities

The house shape exactly (`cloud.py`, `web.py`): a `NAME`, a profile-suffixed `_process_name`,
`is_up`, `up` — `require_port_free` → `ensure_key` → `spawn` → `wait_for_http`. `is_up` checks
that the discovery document names *this profile's* origin, so a playground stub answering on an
eval port reads as down rather than as up. There is no `down`: the stub is stateless, so the
process group dying is the whole teardown.

The two identities live here because §10.2 says one place, and `stack/stub_oidc/__main__.py`
imports them from here rather than taking them on argv, so there is no second copy on a command
line to drift.

### 4. The ports, and `StackConfig.oidc_port`

Eval `18090`, playground `18091` — fixed, like every other port here, in `stack.toml`,
`DEFAULT_PORTS` and `DEFAULT_PLAYGROUND_PORTS`. The field is defaulted and last on the frozen
dataclass so a `StackConfig` built by hand before this feature still constructs.

### 5. `lifecycle` / `processes` — a fourth gate and a third pid file

`boot()` becomes five gates with `oidc.up` first (§10.3's ordering note: keel-cloud will fetch
discovery lazily, so nothing depends on the order — but the first login of a run should never also
be the first discovery of a dead port). `quick_gates_pass` gains it, because once the login is
Google sign-in a stack with no issuer is a stack nobody can log into, and `make eval` attaching to
one would be a puzzling red.

### 6. `stack/cloud.py:build_env` — four variables, wired early

The one change here that keel-cloud will consume. It is inert today — an unknown environment
variable is not a boot failure — and it means spec 032's first run needs no change in this
repository. `stack/oidc.py:cloud_env` owns the four so the test can assert the exact set, and the
absence of `KEEL_GOOGLE_ALLOWED_DOMAIN` is asserted as deliberately as the presence of the rest.

## Risks, and what each is worth

- **The four variables sit unread for as long as spec 032 takes.** Cheap to carry, and the
  alternative — landing them with the second half — would put the harness's first Google login and
  its first configuration of one in the same commit. Rejected for the same reason §12 does.
- **`openssl` is assumed.** It ships with macOS and every Linux this repo has run on, including
  both acceptance beds. If it ever is not there, the failure is a named error at `make up` with
  the install command in it, not a mystery at login.
- **The picker's markup is a contract the second half will click.** `<button>` labelled with the
  identity's own name, asserted here — so a change to the page that would break
  `get_by_role("button", name="Eval Founder")` goes red in `make unit` rather than in a browser
  scenario nobody has written yet.
- **Two ports more to collide.** 18090/18091 join the fixed set; `require_port_free` names the
  owner as it already does for the other three.
