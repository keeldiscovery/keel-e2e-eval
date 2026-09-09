"""keel-e2e-eval's stub OIDC issuer (keel-cloud `canon/designs/google-sign-in-design.md` §10.1).

`stack/oidc.py` is the lifecycle wiring -- what `make up` starts and `make down` stops, the two
identities, and the environment keel-cloud is pointed at it with. This package is the server
itself: `server.py` (the four routes) and `keys.py` (one RSA key and RS256, standard library
only). `python -m stack.stub_oidc --port 18090` runs it.
"""

from stack.stub_oidc.server import Identity, StubIssuer, make_server, pkce_challenge

__all__ = ["Identity", "StubIssuer", "make_server", "pkce_challenge"]
