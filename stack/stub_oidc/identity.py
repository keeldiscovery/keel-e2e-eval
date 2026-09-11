"""Who the stub will sign in as, and the client it answers -- the stub package's own
configuration, in one module that imports nothing.

**Why this is not in `stack/oidc.py` any anymore.** It was, and for the local profiles that was the
right place: one list, beside the lifecycle that spawns the process. Spec 018 puts the same
server in a container on the staging twin (e2e-matrix-design.md §3), where `stack/oidc.py` cannot
follow -- it imports `requests`, `stack.config` and `stack.processes`, none of which a stub
issuer needs to serve a discovery document. So the data moved down into the package that uses it
and `stack/oidc.py` re-exports the same objects under the same names: `oidc.FOUNDER_A`,
`oidc.STUB_IDENTITIES`, `oidc.CLIENT_ID` are all still there, still the one source of truth, and
still what `stack/auth.py` builds `FOUNDER_ONE`/`FOUNDER_TWO` from.

The container image (`stack/containers/oidc/Dockerfile`) therefore copies `stack/__init__.py` and
`stack/stub_oidc/` and nothing else, and installs no Python package at all.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Identity:
    """One person the stub will sign in as. `id` is the harness's handle for it (`?identity=`),
    `sub` is what keel-cloud keys the account on (google-sign-in-design.md §3.4), and `name` is
    what the picker's button is labelled with -- which is how a browser scenario chooses (§10.2).

    `label` is the registry's own field (e2e-matrix-design.md §4.3) and is `None` for the two
    built-in identities below: the long form the picker shows under the button and the cell
    patches its verdict into. `name` stays the short form, because it is what keel-web greets the
    founder by and what a participant page carries.
    """

    id: str
    sub: str
    email: str
    name: str
    picture: str | None = None
    hd: str | None = None
    label: str | None = None

    def matches(self, hint: str) -> bool:
        return hint in (self.id, self.sub, self.email)


#: The client keel-cloud presents to the stub. Fixed, non-secret, and the same on both local
#: profiles -- it is a string two local processes agree on, not a credential
#: (google-sign-in-design.md §7's "the eval stack never has one at all"). A real client id and
#: secret live in a founder's own `.envrc` and never here; the staging twin's are stub values in
#: `/keel/staging/`, which is invariant M4.
CLIENT_ID = "keel-eval-client"
CLIENT_SECRET = "keel-eval-client-secret"  # noqa: S105 - see above: not a secret, by construction

#: The two founders, in one place (google-sign-in-design.md §10.2). Founder A keeps today's
#: `stack/auth.py` `FOUNDER_NAME` and `FOUNDER_EMAIL` on purpose: those strings are already in
#: greetings, participant pages and screenshots, and nothing about Google sign-in is a reason to
#: churn them. `picture` is `None` for both, so the header's no-picture fallback is the state the
#: whole eval set runs in.
FOUNDER_A = Identity(
    id="founder-a",
    sub="stub-founder-1",
    email="eval-founder@keel-e2e-eval.test",
    name="Eval Founder",
)
FOUNDER_B = Identity(
    id="founder-b",
    sub="stub-founder-2",
    email="second-founder@keel-e2e-eval.test",
    name="Nour Haddad",
)
STUB_IDENTITIES = [FOUNDER_A, FOUNDER_B]
