"""`python -m stack.stub_oidc --port 18090 --key runs/.stack/oidc-key.pem` -- what
`stack/oidc.py:up()` spawns, and what a person can run by hand to poke at the thing.

Defaults come from `stack/oidc.py` (the identities, the client id and secret) so those live in
exactly one place, which is the design's own instruction (§10.2).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stack.stub_oidc.keys import load_or_generate
from stack.stub_oidc.server import make_server


def main(argv: list[str] | None = None) -> int:
    from stack import oidc  # imported here so `--help` needs no config at all

    parser = argparse.ArgumentParser(prog="python -m stack.stub_oidc", description=__doc__)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--key", type=Path, required=True,
                        help="PEM the key is read from, and written to when it is not there yet")
    parser.add_argument("--issuer", default=None,
                        help="the origin the discovery document names (default "
                             "http://localhost:<port>)")
    parser.add_argument("--client-id", default=oidc.CLIENT_ID)
    parser.add_argument("--client-secret", default=oidc.CLIENT_SECRET)
    args = parser.parse_args(argv)

    key = load_or_generate(args.key)
    httpd = make_server(
        port=args.port, key=key, client_id=args.client_id, client_secret=args.client_secret,
        identities=oidc.STUB_IDENTITIES, issuer=args.issuer,
    )
    origin = httpd.stub.issuer
    print(f"[stub-oidc] serving {origin} -- identities "
          f"{[i.id for i in oidc.STUB_IDENTITIES]}, client {args.client_id}", file=sys.stderr,
          flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - `make down` kills the process group
        pass
    finally:
        httpd.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
