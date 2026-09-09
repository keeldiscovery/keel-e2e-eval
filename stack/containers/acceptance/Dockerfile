# B1, the CLI stage: Linux in Docker, both architectures, from the founder's Mac.
#
# keel-cloud `canon/designs/keel-skill-design.md` §10.2 is the whole of this file. It is built
# twice -- `--platform linux/arm64` (native on Apple silicon) and `--platform linux/amd64`
# (emulated) -- and run against a keel-cloud on the **host**, reached at
# `http://host.docker.internal:18080`.
#
# What it is for, in one sentence: **does a copied skill still work after an installer moved it**,
# on a machine that has never heard of this repository, with no checkout to fall back on.
#
# The build context is keel-connect-skill's `dist/bare/` -- the tree with no manifest at all --
# so the only bytes that enter this image are the ones `make dist` wrote. Build it with:
#
#   docker build --platform linux/arm64 \
#     -f stack/containers/acceptance/Dockerfile \
#     -t keel-acceptance:arm64 ../keel-connect-skill/dist/bare
#
# `stack/containers/acceptance/run-acceptance.sh` (and `make acceptance`) does that for you.
#
# **No secret is baked in** (T-5). `ANTHROPIC_API_KEY` and `COPILOT_GITHUB_TOKEN` arrive at
# `docker run` time, by name, from the caller's shell; nothing here copies a credentials file,
# and `~/.claude/.credentials.json` is not the supported path and is not used.
#
# **No `KEEL_RUNTIME_PATH` and no `KEEL_HOME` are set anywhere in this image** (T-1, and design
# §6.3): the runtime must be the one that travelled inside the skill, and the home must be the one
# keel-runtime derives from the address it resolved -- `~/.keel/<host-slug>/`. An image that named
# either would be measuring a path no founder is on, which is the failure `runs/DRIFT.md` #48
# records for this repository's own scenarios.

FROM debian:12-slim

# **One source tree, both hosts** (D1, enforced by a `COPY` -- T-3). The context is
# `dist/bare/`, so `keel-connect/` here is exactly the tree `install.sh` would copy, and the two
# destinations are the two personal skill directories §8.3 names. Two `COPY`s of one path is the
# strongest form of "these are the same bytes" a Dockerfile can state.
COPY keel-connect /root/.claude/skills/keel-connect
COPY keel-connect /root/.copilot/skills/keel-connect

# The skill's own copy of itself, at a path the run script can name without knowing which host
# directory it is asserting about. Same bytes again, and nothing reads it but the stackless half.
COPY keel-connect /opt/keel-connect

# **The `COPY`s come first, and that is a workaround with a reason** (`runs/DRIFT.md` #50). With
# the legacy builder and `--platform`, a `COPY` whose *destination* is an image produced by a
# `RUN` is rejected -- *"image ... was found but does not provide the specified platform
# (linux/amd64)"* -- because the daemon cannot confirm the intermediate image's platform.
# Measured 2026-09-09: the same Dockerfile with its `COPY`s ahead of every `RUN` builds cleanly on
# both architectures. It costs nothing here (the skill is the payload, not a build input) and it
# is the difference between an amd64 row that exists and one that does not.

# **The layer cache has to be told which architecture this is** (`runs/DRIFT.md` #50, this repo's
# own grip). There is no `buildx` on the founder's Docker (29.5.2 -- `docker buildx` is *unknown
# command*), so these builds go through the legacy builder, which keys its cache by instruction
# text alone and **not by platform**: build arm64, then build amd64, and the second build is
# handed the first one's layers until a `COPY` fails with *"image ... does not provide the
# specified platform (linux/amd64)"*. Naming the platform in an `ARG` that the first `RUN`
# consumes puts it into the cache key, which is what BuildKit would have done unasked. Without
# this, one architecture's "green" is the other architecture's image.
ARG BUILD_PLATFORM=unknown
RUN echo "$BUILD_PLATFORM" > /etc/keel-acceptance-platform

# Debian 12 ships Python 3.11, comfortably above the 3.9 floor. `Dockerfile.floor` beside this one
# is the other half of that claim: Debian 11 ships 3.9 itself.
#
# `curl`, `ca-certificates` and `xz-utils` are for fetching Node below and for the container's own
# `curl $KEEL_BASE_URL/v2/me` check; `git` because both host CLIs expect it to exist.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      ca-certificates curl xz-utils python3 git \
 && rm -rf /var/lib/apt/lists/* \
 && python3 --version

# Node 22 -- the floor GitHub's own install page declares for Copilot CLI (read 2026-09-08).
# Taken from nodejs.org's own tarball rather than a third-party apt repository: one URL, one
# checksum-able artifact, and the same bytes on both architectures' own builds.
ARG NODE_VERSION=22.14.0
RUN set -eux; \
    case "$(dpkg --print-architecture)" in \
      amd64) node_arch=x64 ;; \
      arm64) node_arch=arm64 ;; \
      *) echo "unsupported architecture: $(dpkg --print-architecture)" >&2; exit 1 ;; \
    esac; \
    curl -fsSL "https://nodejs.org/dist/v${NODE_VERSION}/node-v${NODE_VERSION}-linux-${node_arch}.tar.xz" \
      -o /tmp/node.tar.xz; \
    tar -xJf /tmp/node.tar.xz -C /usr/local --strip-components=1; \
    rm /tmp/node.tar.xz; \
    node --version; \
    npm --version

# Both host CLIs, with their versions printed into the image (T-6) so a run's record can name
# which ones it measured. `|| true` is deliberate on the *version* lines only -- a CLI that
# refuses to print a version without a network or a token must not fail a build whose other half
# is the stackless check.
RUN npm install -g --no-fund --no-audit @anthropic-ai/claude-code @github/copilot \
 && { claude --version || true; } > /opt/claude-version.txt 2>&1 \
 && { copilot --version || true; } > /opt/copilot-version.txt 2>&1 \
 && cat /opt/claude-version.txt /opt/copilot-version.txt

WORKDIR /root
CMD ["/bin/sh", "-c", "echo 'this image is driven by stack/containers/acceptance/run-acceptance.sh'"]
