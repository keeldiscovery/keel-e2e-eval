# Spec 095 -- S-003 and S-010 on the remote profile: the harness registers the identity it signs in as, and a sign-in that lands on the issuer is not a sign-in

On 2026-10-30 the whole non-live set ran against staging for the first time. S-003 (every door) and S-010 (two founders)
failed at *founder visits the landing* (no `.hello`): both sign in as the built-in `founder-a` (`stack/auth.py:74-75`,
`evals/conftest.py:138-158`), which the gated staging stub refuses for the `harness` gate user by design (rule M6,
`stack/stub_oidc/server.py:107-120`, 403 *'harness' may not sign in as 'founder-a'*); and `Auth.sign_in`'s success
check (`harness/browser.py:651-655`: the URL starts with the base and has no `/login`) counts the 403 page as signed in
because the remote issuer shares keel-web's origin (`<web>/oidc`). Neither scenario had ever run remotely (every earlier
bundle is local). The seven corpus journeys register a fresh identity through `remote.identity_to_sign_in_as`
(`stack/remote.py:197-206`) and passed.

## Rules

- **FR-1 The identity is registered.** S-003 signs in as `remote.identity_to_sign_in_as(stack, cell, fallback=founder_one)`;
  S-010 as two distinct registered identities on the remote profile (its two founders), the built-ins on local profiles
  as today. Every other caller of the built-ins on a browser path is listed in tasks.md.
- **FR-2 A landing on the issuer is a refusal.** `Auth.sign_in` (and `sign_in_with_code`) treat a final URL under the
  issuer's base (`config.oidc_url`) as a failed sign-in and raise with the page's one line, never record `ok: true`; a
  unit test on the predicate with the 403 page's URL.
- **FR-3 Nothing else moves.** The local profiles, the stub, the seven journeys.

## Acceptance

`make unit` green with ZERO failed; `make eval K=s003 PROFILE=remote` and `K=s010 PROFILE=remote` green against staging
(the coordinator runs them). Build on the founder's word, after cycle 3 (the fix list).
