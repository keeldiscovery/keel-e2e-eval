"""keel-e2e-eval's stub OIDC issuer (keel-cloud `canon/designs/google-sign-in-design.md` §10.1).

`stack/oidc.py` is the lifecycle wiring -- what `make up` starts and `make down` stops and the
environment keel-cloud is pointed at it with. This package is the server itself and everything it
needs: `identity.py` (the `Identity` record, the client, the two built-in founders),
`server.py` (the routes), `keys.py` (one RSA key and RS256, standard library only) and
`registry.py` (the staging twin's per-cell identity list). `python -m stack.stub_oidc --port
18090` runs it, and **the package imports nothing outside itself**, which is what lets the same
code be a container on the staging twin (e2e-matrix-design.md §3).
"""

from stack.stub_oidc.identity import Identity
from stack.stub_oidc.registry import Entry, Registry, RegistryError
from stack.stub_oidc.server import StubIssuer, make_server, pkce_challenge

__all__ = ["Entry", "Identity", "Registry", "RegistryError", "StubIssuer", "make_server",
           "pkce_challenge"]
