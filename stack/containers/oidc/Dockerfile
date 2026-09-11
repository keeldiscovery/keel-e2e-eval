# The stub issuer as a container -- the one service the staging twin runs that production does
# not (keel-cloud `canon/designs/e2e-matrix-design.md` §3).
#
# What this image is, in one sentence: **the same `stack/stub_oidc/` package the eval profile
# spawns as a local process**, with `--gated` and `--registry` on, behind Caddy, on the compose
# network only. Not a second implementation, not a fork, not a "staging version" -- if the two
# ever diverge, the thing the matrix signs in through stops being the thing the local suite
# refereed, and every cell's green stops meaning what a local green means.
#
# Build it for the box's own architecture (a `t4g.micro` is arm64):
#
#   make oidc-image TAG=<sha>              # buildx, linux/arm64, tagged keel-oidc:<sha>
#   make oidc-image TAG=<sha> PUSH=1       # ... and pushed, when OIDC_IMAGE_REPO names an ECR repo
#
# Run it the way the compose overlay does:
#
#   docker run --rm -p 18090:18090 -v /opt/keel/oidc:/var/lib/keel-oidc keel-oidc:<sha> \
#     --port 18090 --host 0.0.0.0 --issuer https://eval.keeldiscovery.com/oidc \
#     --key /var/lib/keel-oidc/oidc-key.pem --registry /var/lib/keel-oidc/identities.json --gated
#
# **No secret is baked in and none is needed** (invariant M4). The client id and secret are the
# same fixed non-secret strings the local profiles use -- two processes agreeing on a string --
# and the signing key is generated on first start into the mounted volume, where it signs tokens
# for an issuer that exists only because `KEEL_OIDC_ISSUER` names it. The *gate's* passwords are
# Caddy's, in `/keel/staging/`, and this image never sees one: all it ever learns is the user
# name Caddy forwards in `X-Keel-Gate-User` (§4.2).

FROM python:3.12-slim

# `openssl` is the one external tool the stub uses, once, to generate its RSA key
# (`stack/stub_oidc/keys.py` explains why the *arithmetic* is pure Python and only the keygen
# shells out). Installing it explicitly rather than trusting the base image to carry the binary
# is the difference between a container that starts and one that fails on its first sign-in.
# **No `pip install`**: the package imports nothing outside the standard library.
RUN apt-get update \
 && apt-get install -y --no-install-recommends openssl \
 && rm -rf /var/lib/apt/lists/* \
 && openssl version

WORKDIR /app

# The whole payload, and the reason `stack/stub_oidc/identity.py` exists: this package imports
# nothing from `stack/` but its own `__init__`, so the image carries no `requests`, no
# `stack.config`, no sibling checkout and no scenario.
COPY stack/__init__.py /app/stack/__init__.py
COPY stack/stub_oidc /app/stack/stub_oidc

# The registry and the signing key live on a volume, so the identities survive a redeploy and
# the monthly reset is `rm` of one directory (§8).
VOLUME ["/var/lib/keel-oidc"]
EXPOSE 18090

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1

# The entrypoint is the module, so every flag is the flag the local profile passes by the same
# name and `docker run ... --help` prints the same help a founder reads on their Mac.
ENTRYPOINT ["python", "-m", "stack.stub_oidc"]
CMD ["--port", "18090", "--host", "0.0.0.0", \
     "--key", "/var/lib/keel-oidc/oidc-key.pem", \
     "--registry", "/var/lib/keel-oidc/identities.json", \
     "--gated"]
