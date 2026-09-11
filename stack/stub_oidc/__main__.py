"""`python -m stack.stub_oidc --port 18090 --key runs/.stack/oidc-key.pem` -- what
`stack/oidc.py:up()` spawns, what the container image's entrypoint runs, and what a person can
run by hand to poke at the thing.

Defaults (the identities, the client id and secret) come from `stack/stub_oidc/identity.py`, so
they live in exactly one place -- which is the design's own instruction (google-sign-in-design.md
§10.2) -- and so this module imports nothing outside its own package: the staging twin runs it in
a container with no `requests`, no `stack.config` and no sibling checkout anywhere.

**The two staging flags** (e2e-matrix-design.md §4.2, §4.3), neither of which the local profiles
pass:

    --gated              refuse /authorize and the registry routes without an X-Keel-Gate-User
                         header -- the one Caddy sets from the basic auth in front of it
    --registry <path>    keep the identity registry in that JSON file instead of in memory
"""

from __future__ import annotations

import argparse
import os
from typing import Mapping
import sys
from pathlib import Path

from stack.stub_oidc.identity import CLIENT_ID, CLIENT_SECRET, STUB_IDENTITIES
from stack.stub_oidc.keys import load_or_generate
from stack.stub_oidc.registry import Registry
from stack.stub_oidc.server import make_server


def client_from_env(env: "Mapping[str, str]") -> tuple[str, str]:
    """The (client id, client secret) the stub should accept: the env pair keel-cloud is given,
    when both are set and non-blank; the built-in pair otherwise. Never one of each -- a mixed
    pair would accept nothing and say nothing about why."""
    cid = (env.get("KEEL_GOOGLE_CLIENT_ID") or "").strip()
    secret = (env.get("KEEL_GOOGLE_CLIENT_SECRET") or "").strip()
    if cid and secret:
        return cid, secret
    return CLIENT_ID, CLIENT_SECRET


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m stack.stub_oidc", description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--key", type=Path, required=True,
                        help="PEM the key is read from, and written to when it is not there yet")
    parser.add_argument("--issuer", default=None,
                        help="the origin the discovery document names (default "
                             "http://localhost:<port>)")
    # The client keel-cloud presents. In a container the pair arrives through the same rendered
    # env file keel-cloud reads (KEEL_GOOGLE_CLIENT_ID / KEEL_GOOGLE_CLIENT_SECRET), so the secret
    # never sits in argv or `docker inspect`; a flag still wins, and the built-in pair is what the
    # local profiles get with neither. (Staging's first sign-in, 2026-09-11: POST /token 401 --
    # keel-cloud presented the parameter-store secret, the stub checked its built-in one.)
    client_id_default, client_secret_default = client_from_env(os.environ)
    parser.add_argument("--client-id", default=client_id_default)
    parser.add_argument("--client-secret", default=client_secret_default)
    parser.add_argument("--host", default="127.0.0.1",
                        help="the address to bind (default 127.0.0.1; a container needs 0.0.0.0, "
                             "where the only thing that can reach it is the compose network)")
    parser.add_argument("--gated", action="store_true",
                        help="refuse /authorize and the registry without an X-Keel-Gate-User "
                             "header (e2e-matrix-design.md §4.2) -- staging only")
    parser.add_argument("--registry", type=Path, default=None,
                        help="the JSON file the identity registry lives in (default: in memory, "
                             "which is what the eval and playground profiles want)")
    args = parser.parse_args(argv)

    key = load_or_generate(args.key)
    httpd = make_server(
        port=args.port, key=key, client_id=args.client_id, client_secret=args.client_secret,
        identities=STUB_IDENTITIES, issuer=args.issuer, host=args.host,
        registry=Registry(args.registry) if args.registry else None,
        gated=args.gated,
    )
    origin = httpd.stub.issuer
    registered = [entry.identity.id for entry in httpd.stub.registry.newest_first()]
    print(f"[stub-oidc] serving {origin} -- identities "
          f"{[i.id for i in STUB_IDENTITIES]}, client {args.client_id}"
          f"{', gated' if args.gated else ''}"
          f"{f', registry {args.registry} ({len(registered)} registered)' if args.registry else ''}",
          file=sys.stderr, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - `make down` kills the process group
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
