"""The journey's **host abstraction**, held stackless (spec `019-journey-through-a-host`).

The Copilot instance has had tests since spec 016 (`tests/test_s012_copilot_host.py`), for the
reason stated there: a live run is the wrong place to discover that a flag name was wrong. Spec
019 adds a second host, and with it a second kind of mistake that only a paid run would otherwise
find -- **a difference between the two that nobody meant**. So these tests put the two command
lines side by side and assert what must be the same, what must differ, and why.

Nothing here shells `claude` or `copilot`, and nothing here needs a stack, a browser or a model.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from harness import agent_host, claude_host, copilot_host

REPO = Path(__file__).resolve().parent.parent
SCENARIO = (REPO / "evals" / "test_s012_journey_through_a_host.py").read_text()
MAKEFILE = (REPO / "Makefile").read_text()


# ------------------------------------------------------------------------------ which host

def test_the_default_is_copilot_so_todays_command_still_means_what_it_meant():
    """`make eval-live K=s012` with no `HOST=` produced the spec 016 run of record. A default that
    silently moved it to the other host would make every earlier run record ambiguous."""
    assert agent_host.journey_host({}) == "copilot"
    assert agent_host.journey_host({"KEEL_JOURNEY_HOST": ""}) == "copilot"
    assert agent_host.DEFAULT_HOST == "copilot"


@pytest.mark.parametrize("raw,expected", [("claude", "claude"), ("copilot", "copilot"),
                                           ("Claude", "claude"), ("  COPILOT  ", "copilot")])
def test_a_hosts_name_is_read_the_way_a_founder_types_it(raw, expected):
    """Whitespace and case off a Makefile are a founder's typing, not a different intention."""
    assert agent_host.journey_host({"KEEL_JOURNEY_HOST": raw}) == expected


def test_a_typo_is_refused_by_name_rather_than_run_as_the_other_host():
    """The one place this could silently cost money: a `HOST=copliot` that fell back to the
    default would spend the founder's plan on a measurement nobody asked for and file it under a
    name nobody chose."""
    with pytest.raises(agent_host.UnknownHost) as exc:
        agent_host.journey_host({"KEEL_JOURNEY_HOST": "copliot"})
    assert "copliot" in str(exc.value)
    assert "claude" in str(exc.value) and "copilot" in str(exc.value)


def test_the_makefile_passes_host_through_and_defaults_it_to_copilot():
    assert "KEEL_JOURNEY_HOST=$(if $(HOST),$(HOST),$(if $(KEEL_JOURNEY_HOST),$(KEEL_JOURNEY_HOST),copilot))" in MAKEFILE, (
        "`make eval-live K=s012 HOST=claude` no longer reaches the scenario")
    assert "-m live" in MAKEFILE


# ---------------------------------------------------------------------------- the bundle's name

def test_the_bundle_carries_the_host():
    """`runs/<stamp>-s012-journey-<host>/`. The matrix uploads one bundle per cell and a reader
    looking at eighteen of them has only the directory name to go on until they open one."""
    assert agent_host.bundle_slug("claude", "full") == "s012-journey-claude"
    assert agent_host.bundle_slug("copilot", "full") == "s012-journey-copilot"


# ------------------------------------------------------------------ how far it goes (spec 021)

def test_the_default_length_is_the_whole_journey():
    """`make eval-live K=s012` with no `LEGS=` is spec 016's and spec 019's own command, and it
    means what it meant: both legs, three stages, the person, the reading, the brief."""
    assert agent_host.journey_legs({}) == "full"
    assert agent_host.journey_legs({"KEEL_JOURNEY_LEGS": ""}) == "full"
    assert agent_host.DEFAULT_LEGS == "full"


@pytest.mark.parametrize("raw,expected", [("short", "short"), ("FULL", "full"),
                                          (" Short ", "short")])
def test_the_length_is_read_case_and_space_insensitively(raw, expected):
    assert agent_host.journey_legs({"KEEL_JOURNEY_LEGS": raw}) == expected


def test_an_unknown_length_raises_rather_than_quietly_spending_the_wrong_amount():
    """A typo that ran `full` where the founder asked for `short` spends about thirteen premium
    requests instead of two; a typo the other way files a cheap measurement under a name that
    promises an expensive one. Neither is a thing to guess at."""
    with pytest.raises(agent_host.UnknownLegs) as excinfo:
        agent_host.journey_legs({"KEEL_JOURNEY_LEGS": "half"})
    assert "half" in str(excinfo.value) and "short" in str(excinfo.value)


def test_only_the_short_bundle_carries_a_suffix():
    """The full journey's bundle name does not move: `s012-journey-copilot` means today what it
    meant yesterday, and a reader who finds a name without `-short` knows what they have."""
    assert agent_host.bundle_slug("claude", "short") == "s012-journey-claude-short"
    assert agent_host.bundle_slug("copilot", "short") == "s012-journey-copilot-short"
    assert agent_host.bundle_slug("claude", "full") == "s012-journey-claude"


def test_the_makefile_passes_the_length_through():
    assert "KEEL_JOURNEY_LEGS=$(if $(LEGS),$(LEGS),$(if $(KEEL_JOURNEY_LEGS),$(KEEL_JOURNEY_LEGS),full))" in MAKEFILE, (
        "`make eval-live K=s012 LEGS=short` no longer reaches the scenario")


def test_the_scenario_reads_its_length_once_at_import_and_branches_on_it_by_name():
    assert "LEGS = agent_host.journey_legs()" in SCENARIO
    assert 'SHORT = LEGS == "short"' in SCENARIO


def test_the_short_journey_asserts_the_card_through_the_very_same_function():
    """The founder's own rule: *"assertions in short mode are the same ones the full journey makes
    up to that point"*. It is held by `_land_the_card` being one function called from two places,
    rather than by two blocks that look alike today."""
    assert SCENARIO.count("def _land_the_card(") == 1
    assert SCENARIO.count("_land_the_card(page, recorder, _get, project_id") == 1
    assert "chat, _card = _land_the_card(" in SCENARIO, (
        "the full journey's walk goes through it too, or the two would be free to drift")


def test_the_short_journey_still_leaves_by_the_founders_own_door():
    """Whatever else it skips, it never skips `keel disconnect` -- a runtime left running is a
    runtime the next cell inherits."""
    tail = SCENARIO.split("if SHORT:", 1)[1]
    assert "disconnect_via_skill_script" in tail
    assert "zero refusals, every job COMPLETED" in tail, (
        "the wire checks are made by both lengths, not only by the long one")


# ------------------------------------------------------------ whose founder walks it (spec 021)

def test_the_default_founder_is_the_lullaby_entry():
    assert agent_host.journey_entry({}) == "03-lullaby"
    assert agent_host.journey_entry({"KEEL_JOURNEY_ENTRY": ""}) == "03-lullaby"
    assert agent_host.journey_entry({"KEEL_JOURNEY_ENTRY": " 05-paidly "}) == "05-paidly"


def test_an_unknown_entry_is_refused_by_the_corpus_reader_and_not_here():
    """This repository carries no list of the corpus's filenames and should not grow one: the one
    reader that opens the corpus already refuses an id by name, with the ids there actually are,
    and that is the refusal the six scripted scenarios get too."""
    from harness import corpus_script

    assert agent_host.journey_entry({"KEEL_JOURNEY_ENTRY": "99-nope"}) == "99-nope"
    source = (REPO / "harness" / "corpus_script.py").read_text()
    assert "no corpus entry {entry_id!r}" in source
    assert hasattr(corpus_script, "entry_for")


def test_the_makefile_passes_the_entry_through():
    assert "KEEL_JOURNEY_ENTRY=$(if $(ENTRY),$(ENTRY),$(if $(KEEL_JOURNEY_ENTRY),$(KEEL_JOURNEY_ENTRY),03-lullaby))" in MAKEFILE


def test_the_scenario_reads_its_founder_through_the_scripted_scenarios_own_reader():
    """Reuse, not a copy (the founder's own word). `founder_inputs` already refuses an entry with
    a missing statement by name and `person_inputs` already refuses a person offered an anchor
    their role is not asked; a second reader here would be a second chance to be wrong about
    both."""
    assert "corpus, entry = corpus_script.entry_for(stack.keel_cloud, ENTRY_ID)" in SCENARIO
    assert "founder = corpus_script.founder_inputs(entry)" in SCENARIO
    # Amended 2026-09-13: the people come through the same reader, five of them on `full`.
    assert "people_chosen, people_skipped = corpus_script.people_to_invite(entry, PEOPLE)" in SCENARIO
    assert "person = people_chosen[0]" in SCENARIO
    assert "payroll_exceptions" not in SCENARIO, (
        "the smoke's fixture stays the smoke's; S-012 no longer borrows it")


def test_the_founder_types_the_entrys_own_title_market_and_three_statements():
    """What `founder_inputs` hands back, checked against the entry the journey defaults to --
    through the real corpus, so a corpus edit that emptied a statement fails here."""
    from harness import corpus_script
    from stack.config import load_config

    _, entry = corpus_script.entry_for(load_config(validate=False).keel_cloud, "03-lullaby")
    founder = corpus_script.founder_inputs(entry)
    assert founder.project_name == entry.title
    assert founder.market.country == "GB"
    assert founder.correction is None, "the correction is S-001's turn, not the journey's"
    for stage in ("PROBLEM", "SOLUTION", "COMMERCIAL"):
        assert founder.statement(stage).strip()
        assert founder.statement(stage) == entry.statements[stage.lower()].strip()


def test_the_one_person_is_the_entrys_first_and_brings_their_own_words():
    from harness import corpus_script
    from evals.test_s012_journey_through_a_host import _story_texts
    from stack.config import load_config

    _, entry = corpus_script.entry_for(load_config(validate=False).keel_cloud, "03-lullaby")
    person = corpus_script.person_inputs(entry)[0]
    assert person.person == "Amira Saleh"
    stories = _story_texts(person)
    assert len(stories) == 3, "she wrote under all three of her role's anchors"
    assert stories[0].startswith("Last night. Up at one")
    assert all(s.strip() for s in stories)


def test_their_pick_prefers_their_own_answer_and_falls_back_to_the_pages_first():
    """On a live run the option list is the model's, not the corpus's, so a corpus value is used
    where it is offered and the page's own first option where it is not. Which of the two happened
    goes into the bundle; neither is ever asserted (FR-007)."""
    from evals.test_s012_journey_through_a_host import _their_pick
    from harness import corpus_script

    person = corpus_script.PersonInputs(
        person="Amira Saleh", role_id="parent",
        picks=[corpus_script.Pick(selection_id="S2", values=["3 to 4"]),
               corpus_script.Pick(selection_id="S4", values=["no"])])
    assert _their_pick(person, ["1 to 2", "3 to 4", "5 or more"]) == ("3 to 4", True)
    assert _their_pick(person, ["  3 TO 4 ", "other"]) == ("  3 TO 4 ", True)
    assert _their_pick(person, ["daily", "weekly"]) == ("daily", False)


def test_the_bundle_says_whose_founder_and_how_far():
    """A reader of eighteen bundles needs the founder and the length beside the host, or two
    bundles from two sets look like the same run that disagreed."""
    assert 'write_block(run_dir, "journey", {' in SCENARIO
    for key in ('"entry": entry.id', '"entry_sha256": entry.sha256', '"legs": LEGS'):
        assert key in SCENARIO, key
    assert "the journey's founder" in SCENARIO and "the journey's length" in SCENARIO


def test_the_scenario_names_its_own_bundle_and_finalises_under_the_same_name():
    """Two places name the bundle -- the marker the `run_dir` fixture reads, and `finalize_run`'s
    slug, which is what `verdict.json` says the scenario was. They must be the same string or a
    bundle's directory and its verdict would disagree about which cell it is."""
    assert "@pytest.mark.bundle(BUNDLE)" in SCENARIO
    assert "finalize_run(run_dir, slug=BUNDLE" in SCENARIO
    assert "BUNDLE = agent_host.bundle_slug(HOST, LEGS, INSTALL)" in SCENARIO


def test_the_run_dir_fixture_honours_the_marker():
    conftest = (REPO / "evals" / "conftest.py").read_text()
    assert 'get_closest_marker("bundle")' in conftest
    assert "bundle(slug)" in (REPO / "pytest.ini").read_text(), (
        "an unregistered marker is a warning today and an error under -W error")


# -------------------------------------------------------------------- the two command lines

class _Recorded:
    """Captures the argv a host would run, without running it."""

    def __init__(self):
        self.argv = None
        self.cwd = None

    def __call__(self, argv, **kwargs):
        self.argv = argv
        self.cwd = kwargs.get("cwd")
        raise RuntimeError("not run on purpose")


def _host(name: str, tmp_path: Path, **kw):
    return agent_host.build_host(
        name, home=tmp_path / f"{name}-home", keel_home=tmp_path / "keel-home",
        base_url="http://localhost:18080", artifacts=tmp_path / "artifacts",
        work_dir=tmp_path / "cwd",
        base_env={"PATH": "/usr/bin", "KEEL_RUNTIME_PATH": "/somewhere/keel-runtime",
                  "CLAUDECODE": "1", "CLAUDE_CODE_MESSAGING_SOCKET": "/tmp/sock",
                  "CLAUDE_CODE_OAUTH_TOKEN": "a-token", "AI_AGENT": "claude-code/2.1.268",
                  "COPILOT_AGENT_SESSION_ID": "leaked-from-an-ancestor",
                  "ANTHROPIC_API_KEY": "a-key", "COPILOT_GITHUB_TOKEN": "another-key",
                  "KEEL_HOME": "/the/founders/home", "KEEL_BASE_URL": "http://elsewhere:1"},
        **kw)


def _argv(name: str, tmp_path: Path, **kw) -> tuple[list[str], str]:
    host = _host(name, tmp_path, **kw)
    recorded = _Recorded()
    real = subprocess.run
    subprocess.run = recorded
    try:
        with pytest.raises(RuntimeError):
            host.say("keel connect", slug="probe", timeout=1)
    finally:
        subprocess.run = real
    return recorded.argv, recorded.cwd


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_both_hosts_are_asked_the_founders_own_three_words(name, tmp_path):
    """`-p "keel connect"`, and nothing that names the skill, the plugin or the script. A prompt
    that said "run the connect script" would prove the *shell* works and nothing about whether the
    host recognised what a founder means -- and it must be the same three words on both hosts, or
    the two cells are not running the same scenario."""
    argv, _ = _argv(name, tmp_path)
    # The binary is resolved through PATH now (a Windows `.cmd` shim cannot be launched by its
    # bare name), so the first element is the resolved path whose basename is the host's CLI.
    import os as _os
    assert _os.path.basename(argv[0]).split(".")[0] == name
    if name == "codex":
        # `codex exec "<prompt>"`: the CLI's non-interactive verb (keel-runtime spec 008).
        assert argv[1] == "exec"
    else:
        assert argv[1] == "-p"
    assert argv[2] == "keel connect"
    joined = " ".join(argv).lower()
    for word in ("keel_connect_check", "skill.md", "scripts/"):
        assert word not in joined, f"{name}'s prompt or flags name {word!r}; the founder does not"


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_neither_host_is_run_from_inside_this_repository(name, tmp_path):
    """**The referee's own instructions must never reach the thing under referee.** Both CLIs
    discover instructions from the working directory and its git root, and a run bundle lives
    inside keel-e2e-eval, whose `AGENTS.md` describes this harness and what its scenarios assert.
    Copilot has `--no-custom-instructions` and still passes it; Claude Code has no such flag, so
    for that host the working directory is the whole of the rule."""
    argv, cwd = _argv(name, tmp_path)
    assert cwd == str(tmp_path / "cwd")
    assert not str(cwd).startswith(str(REPO)), cwd
    if name == "copilot":
        assert "--no-custom-instructions" in argv


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_no_flag_that_would_hide_the_skill_is_ever_passed(name, tmp_path):
    """spec 013's T-2 trap, on both hosts. `--bare` skips skill auto-discovery on Claude Code and
    does not exist on Copilot's CLI at all, and the three beside it reach the same end by another
    road. Leg one *is* skill discovery, so a flag that switched it off would make the whole
    scenario a very expensive way of proving a shell works."""
    argv, _ = _argv(name, tmp_path)
    host_type = agent_host.host_type(name)
    assert "--bare" in host_type.forbidden_flags
    for flag in host_type.forbidden_flags:
        assert flag not in argv
    for blanket in ("--allow-all-tools", "--allow-all", "--yolo",
                    "--dangerously-skip-permissions", "--dangerously-bypass-approvals-and-sandbox"):
        assert blanket not in argv, f"{blanket} would hide what the skill actually needed"


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_each_host_grants_exactly_the_two_tools_the_skill_needs(name, tmp_path):
    """One skill, two spellings: `Skill` + `Bash(python3:*)` on Claude Code, `skill` +
    `shell(python3:*)` on Copilot. Nothing else is approved, because leg one records the tools the
    host actually called and a blanket grant would make *"the skill only needed python3"*
    unobservable."""
    argv, _ = _argv(name, tmp_path)
    if name == "claude":
        assert argv[argv.index("--allowedTools") + 1] == "Skill,Bash(python3:*)"
        assert argv[argv.index("--permission-mode") + 1] == "dontAsk"
    elif name == "codex":
        # Codex has no per-tool grant. What stands between the skill and the runtime is the
        # sandbox (a write under ~/.keel and the network, measured refused), so the journey
        # names the sandbox off explicitly and every command still lands in the stream as a
        # `command_execution` item, which is what keeps "what the skill needed" observable.
        assert argv[argv.index("--sandbox") + 1] == "danger-full-access"
        assert "--json" in argv and "--skip-git-repo-check" in argv
    else:
        grants = [argv[i + 1] for i, a in enumerate(argv) if a == "--allow-tool"]
        assert grants == ["shell(python3:*)", "skill"]


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_each_run_is_machine_readable_so_the_bundle_carries_more_than_prose(name, tmp_path):
    """Both transcripts have to name the tools that were called and what the run cost, or the
    bundle's only evidence about leg one is the model's own sentence."""
    argv, _ = _argv(name, tmp_path)
    if name == "codex":
        assert "--json" in argv
        return
    fmt = argv[argv.index("--output-format") + 1]
    if name == "claude":
        # `json` would carry the cost and the model but not the tool calls.
        assert fmt == "stream-json" and "--verbose" in argv
    else:
        assert fmt == "json" and "--usage-output-file" in argv


def test_only_claude_is_told_which_settings_to_load_and_it_is_the_fresh_homes_own():
    """`claude plugin install` declares the plugin in `<CLAUDE_CONFIG_DIR>/settings.json`
    (measured), which is the `user` source -- so `user` is exactly enough to see the plugin and
    exactly little enough to keep this repository's project and local settings out."""
    assert claude_host.SETTING_SOURCES == "user"


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_the_model_is_pinned_only_when_there_is_one(name, tmp_path):
    """C-5: `--model` is passed when a slug is pinned and **absent** when it is not. A run that
    sent `--model auto` would be claiming a pin it does not have -- and the Claude journey is
    unpinned by default, so this is the branch it takes."""
    flag = "-m" if name == "codex" else "--model"
    argv, _ = _argv(name, tmp_path, model=None)
    assert flag not in argv
    assert "auto" not in argv
    argv, _ = _argv(name, tmp_path, model="a-slug")
    assert argv[argv.index(flag) + 1] == "a-slug"


# --------------------------------------------------------------------------- the two homes

@pytest.mark.parametrize("name,variable", [("claude", "CLAUDE_CONFIG_DIR"),
                                            ("copilot", "COPILOT_HOME"),
                                            ("codex", "CODEX_HOME")])
def test_each_host_is_moved_to_this_runs_own_home(name, variable, tmp_path):
    env = _host(name, tmp_path).env()
    assert env[variable] == str(tmp_path / f"{name}-home")
    assert env["KEEL_HOME"] == str(tmp_path / "keel-home")
    assert env["KEEL_BASE_URL"] == "http://localhost:18080"


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_the_runtime_path_is_scrubbed_on_both_hosts(name, tmp_path):
    """Invariant T-1, in the one place the journey can lose it. The founder's own shell exports
    `KEEL_RUNTIME_PATH` (keel-connect-playground's settings do), and an inherited one would put
    the *checkout* back in place of the runtime that travelled inside the plugin."""
    assert "KEEL_RUNTIME_PATH" not in _host(name, tmp_path).env()


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_the_session_this_harness_runs_in_never_reaches_the_host(name, tmp_path):
    """**The subject is a founder's own CLI, and a founder's CLI is not running inside another
    one.** It is not hygiene: the skill's own host detection reads exactly these names and *"two
    different answers means no answer"*, so an inherited `COPILOT_AGENT_SESSION_ID` beside the
    `CLAUDECODE=1` this harness runs under would make the skill decline to name a host, the
    runtime fall through to `source=ambiguous-path`, and leg two's assertion measure this
    repository's shell instead of the skill's line."""
    env = _host(name, tmp_path).env()
    for leaked in ("CLAUDECODE", "AI_AGENT", "COPILOT_AGENT_SESSION_ID",
                   "CLAUDE_CODE_MESSAGING_SOCKET"):
        assert leaked not in env, f"{leaked} reached {name}"
    # The other host's home is gone too; each host puts its own back.
    homes = {"claude": "CLAUDE_CONFIG_DIR", "copilot": "COPILOT_HOME", "codex": "CODEX_HOME"}
    for other_host, other in homes.items():
        if other_host != name:
            assert other not in env, f"{other} reached {name}"


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_a_credential_in_the_callers_shell_is_never_scrubbed(name, tmp_path):
    """The one exception to the sweep, and it is a credential rather than a session handle:
    `claude setup-token` mints `CLAUDE_CODE_OAUTH_TOKEN` for exactly the case a Claude cell is in.
    Scrubbing it would break the only subscription-shaped way to authenticate one."""
    env = _host(name, tmp_path).env()
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "a-token"
    assert env["ANTHROPIC_API_KEY"] == "a-key"
    assert env["COPILOT_GITHUB_TOKEN"] == "another-key"


def test_only_copilots_runtime_pin_travels_on_the_environment(tmp_path):
    """`KEEL_COPILOT_MODEL` is keel-runtime's own way in for the Copilot executor.
    `ClaudeCodeExecutor` takes no model at all, so a Claude run that set one would be naming a
    variable the runtime ignores and recording a pin that never happened."""
    assert _host("copilot", tmp_path, runtime_model="gpt-5.6-luna").env()["KEEL_COPILOT_MODEL"] \
        == "gpt-5.6-luna"
    assert "KEEL_COPILOT_MODEL" not in _host("copilot", tmp_path, runtime_model=None).env()
    claude_env = _host("claude", tmp_path, runtime_model="a-slug").env()
    assert "KEEL_COPILOT_MODEL" not in claude_env
    assert not [k for k in claude_env if k.endswith("_MODEL")]


@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_the_fresh_keel_home_names_its_keel(name, tmp_path):
    """`keel status` and the skill's own door out take no `--base-url`, so a home that does not
    name its Keel answers `environment: null` -- and the journey asserts `environment` reads this
    stack's own address."""
    path = _host(name, tmp_path).write_home_config()
    assert json.loads(path.read_text())["base_url"] == "http://localhost:18080"


# ------------------------------------------------------- one marketplace, two install commands

@pytest.mark.parametrize("name", agent_host.HOSTS)
def test_both_hosts_install_from_the_one_public_marketplace(name, tmp_path):
    """`keeldiscovery/keel-marketplace` carries `.claude-plugin/marketplace.json` and a
    byte-identical `.github/plugin/marketplace.json`, so **one repository serves both hosts** --
    and the two argvs are identical but for the binary. A run that had to name a different source
    for a different host would be evidence that claim had broken."""
    host = _host(name, tmp_path)
    assert host._marketplace_argv(agent_host.MARKETPLACE_SOURCE) == [
        "plugin", "marketplace", "add", "keeldiscovery/keel-marketplace"]
    # Codex's one different verb, measured: `codex plugin add keel@keel` installs the release
    # branch's tree from the marketplace's Codex-shaped manifest (keel-runtime spec 008).
    verb = "add" if name == "codex" else "install"
    assert host._install_argv(agent_host.PLUGIN_SPEC) == ["plugin", verb, "keel@keel"]


def test_the_scenario_installs_from_the_marketplace_and_never_from_a_checkout():
    """FR-002, and the matrix design's decision 5: *"the cells install from the public
    marketplace, never from a checkout -- a cell that used a checkout would test a plugin no
    founder has."*"""
    for forbidden in ("--plugin-dir", "--add-dir", "dist/plugin", "copytree"):
        assert forbidden not in SCENARIO, f"S-012 names {forbidden!r}"
    assert "add_marketplace()" in SCENARIO and "install_plugin()" in SCENARIO


# ---------------------------------------------------- reading each CLI's proof that it is there

def test_claude_reads_the_skill_out_of_the_plugins_own_inventory():
    """There is no `claude skill list`. `claude plugin details keel` prints a component
    inventory, and because the inventory is **that plugin's**, a name found in it came from the
    plugin by construction -- which is a stronger reading than the Copilot side's, where an
    explicit `source` field is needed to rule out a skill of the same name somewhere else."""
    measured = (
        "Keel Connect (keel) 1.0.0\n"
        "  Description: Connect the local Keel runtime to Keel Cloud...\n"
        "  Source: keel@keel\n"
        "\n"
        "Component inventory\n"
        "  Skills (1)  keel-connect\n"
        "  Agents (0)\n"
        "  Hooks (0)\n")
    assert claude_host.skills_in_details(measured) == ["keel-connect"]


def test_a_plugin_with_no_skills_reads_as_no_skills_rather_than_a_guess():
    assert claude_host.skills_in_details("Component inventory\n  Skills (0)\n  Agents (0)\n") == []
    assert claude_host.skills_in_details("") == []
    assert claude_host.skills_in_details("nothing about components here\n") == []


def test_more_than_one_skill_in_the_inventory_is_read_as_more_than_one():
    assert claude_host.skills_in_details("  Skills (2)  keel-connect, keel-other\n") == [
        "keel-connect", "keel-other"]


def test_the_installed_plugins_are_read_structurally():
    """The measured shape of `claude plugin list --json` (2.1.268), plus a plausible neighbour:
    this repository does not own that JSON's schema, and a referee pinned to one would go red on a
    rename while the plugin was perfectly installed."""
    measured = [{"id": "keel@keel", "version": "1.0.0", "scope": "user", "enabled": True}]
    assert "keel@keel" in claude_host.installed_plugin_ids(measured)
    assert "keel@keel" in claude_host.installed_plugin_ids({"plugins": {"user": measured}})
    assert claude_host.installed_plugin_ids(None) == []


def test_claudes_final_answer_is_the_clis_own_result_event():
    events = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "checking"}]}},
              {"type": "assistant", "message": {"content": [
                  {"type": "tool_use", "name": "Skill", "input": {}}]}},
              {"type": "result", "result": "Keel is connected on localhost:18080.",
               "total_cost_usd": 0.42, "num_turns": 3,
               "modelUsage": {"claude-fable-5": {"inputTokens": 10}}}]
    run = claude_host.ClaudeRun(argv=["claude"], exit_code=0,
                                 reply_text=claude_host._final_answer(events), events=events)
    assert run.reply_text == "Keel is connected on localhost:18080."
    assert run.tools_used == ["Skill"]
    assert run.model == "claude-fable-5"
    assert run.spend() == {"unit": "USD (the CLI's own total_cost_usd; never converted into "
                                    "anything else)",
                           "total_cost_usd": 0.42, "num_turns": 3}


def test_an_interrupted_claude_stream_still_shows_what_was_said():
    events = [{"type": "assistant", "message": {"content": [{"type": "text", "text": "started it"}]}}]
    assert claude_host._final_answer(events) == "started it"
    assert claude_host._final_answer([]) == ""


def test_the_two_units_are_never_converted_into_each_other():
    """keel-runtime spec 005's C-7, generalised: Copilot reports premium requests against a plan
    and Claude reports dollars against an account. A referee that turned one into the other would
    be inventing an exchange rate nobody published, so each `spend()` names its own unit and
    neither carries the other's key."""
    claude = claude_host.ClaudeRun(argv=[], exit_code=0, reply_text="",
                                    events=[{"type": "result", "total_cost_usd": 1.0}]).spend()
    copilot = copilot_host.CopilotRun(argv=[], exit_code=0, reply_text="",
                                       usage={"totalPremiumRequestCost": 2}).spend()
    assert "premium_requests" not in claude and "total_cost_usd" in claude
    assert "total_cost_usd" not in copilot and copilot["premium_requests"] == 2


# ------------------------------------------- what each host's per-job envelope can and cannot say

def test_only_copilots_job_envelope_names_the_executor_that_wrote_it():
    """`CopilotExecutor._envelope` stamps `executor`; `ClaudeCodeExecutor` passes the CLI's own
    `result` event through unchanged and that event names none. The scenario therefore makes the
    per-job cross-check on one host and **records the absence** on the other, rather than quietly
    asserting less on both."""
    assert copilot_host.CopilotHost.envelope_names_its_executor is True
    assert claude_host.ClaudeHost.envelope_names_its_executor is False
    assert "if host.envelope_names_its_executor:" in SCENARIO
    assert "names no executor" in SCENARIO


def test_each_envelope_is_read_for_what_it_actually_carries(tmp_path):
    copilot_facts = _host("copilot", tmp_path).envelope_facts(
        {"executor": "copilot", "model": "gpt-5.6-luna", "premium_requests": 2, "is_error": False})
    assert copilot_facts["executor"] == "copilot"
    assert copilot_facts["premium_requests"] == 2

    claude_facts = _host("claude", tmp_path).envelope_facts(
        {"type": "result", "total_cost_usd": 0.5, "is_error": False,
         "modelUsage": {"claude-fable-5": {}}})
    assert claude_facts["executor"] is None
    assert claude_facts["model"] == "claude-fable-5"
    assert claude_facts["total_cost_usd"] == 0.5
    assert "names no executor" in claude_facts["why"]


# ------------------------------------------------------------- the journey's own promises, both

def test_the_scenario_reads_its_host_from_the_environment_and_nowhere_else():
    assert "HOST = agent_host.journey_host()" in SCENARIO
    assert "EXPECTED_EXECUTOR = agent_host.EXECUTOR_FOR_HOST[HOST]" in SCENARIO


def test_each_host_expects_its_own_executor_and_they_are_the_canonical_names():
    """The skill sends `claude-code` for Claude -- a permanent accepted alias -- and keel-runtime
    canonicalises it before it prints the startup line, so what a log actually says is `claude`."""
    assert agent_host.EXECUTOR_FOR_HOST == {"claude": "claude", "copilot": "copilot", "codex": "codex"}
    assert copilot_host.CopilotHost.executor == "copilot"
    assert claude_host.ClaudeHost.executor == "claude"
    from harness import codex_host
    assert codex_host.CodexHost.executor == "codex"


def test_the_runtimes_pin_is_per_host_and_one_of_them_is_honestly_nothing():
    """keel-runtime's Claude executor takes no model: `_build_argv` never passes `--model` and
    there is no `KEEL_CLAUDE_MODEL`. Inventing a pin the runtime ignores would put a fact about
    the referee into the bundle."""
    from evals import test_s012_journey_through_a_host as s012

    assert s012.RUNTIME_MODEL_FOR_HOST == {"copilot": "gpt-5.6-luna", "claude": None, "codex": None}
    assert s012.HOST_MODEL_FOR_HOST["claude"] is None
    # Codex: unpinned on both sides until the gate says which model to measure on; the account's
    # default (measured gpt-6-astra) answers and the runtime's line says model=default.
    assert s012.HOST_MODEL_FOR_HOST["codex"] is None
    assert s012.RUNTIME_MODEL_ENV_FOR_HOST == {"copilot": "KEEL_COPILOT_MODEL", "codex": "KEEL_CODEX_MODEL"}


def test_the_bundle_records_the_host_the_cli_and_the_models():
    """The matrix defines a cell by its OS, its Python and its **host**, and uploads one bundle
    per cell. A bundle that did not name which host, which CLI version and which models is one a
    reader cannot place in the grid."""
    assert "write_host(run_dir, {" in SCENARIO
    assert '"cli": ready["version"]' in SCENARIO
    assert "the journey's host" in SCENARIO, "facts.json carries the one-line version too"
    for key in ('"host": HOST', '"model (the host\'s own --model)"', '"model (the runtime\'s)"'):
        assert key in SCENARIO, key


def test_write_host_merges_rather_than_replacing(tmp_path):
    """`versions.json` is written by the `run_dir` fixture before a scenario has resolved a thing,
    so the host block has to arrive later without losing the five repositories already there."""
    from harness.evidence import write_host

    (tmp_path / "versions.json").write_text(json.dumps({"keel-cloud": {"commit": "abc"}}))
    write_host(tmp_path, {"host": "claude"})
    write_host(tmp_path, {"cli": "2.1.268"})
    body = json.loads((tmp_path / "versions.json").read_text())
    assert body["keel-cloud"]["commit"] == "abc"
    assert body["host"] == {"host": "claude", "cli": "2.1.268"}


def test_a_note_in_facts_json_is_never_read_back_as_a_fact(tmp_path):
    """S-012 is unscored, so its `facts.json` would otherwise be `{}`. The one line it writes is a
    *string*, which `read_facts` skips -- a note a reader sees and the scorer does not."""
    from harness.scoring import read_facts, write_facts

    write_facts(tmp_path, {"the journey's host": "claude · 2.1.268 · unpinned"})
    assert json.loads((tmp_path / "facts.json").read_text())["the journey's host"].startswith(
        "claude")
    assert read_facts(tmp_path) == {}


# ---------------------------------------------------------------------- spec 017 follow-up
# The scenario names the stack by `stack.web_base_url`/`cloud_base_url` now, and asserts the
# runtime's `environment` against what keel-runtime derives from that address -- mirrored, not
# imported (the referee never imports the runtime it judges).

def test_environment_of_mirrors_the_runtime_for_local_and_remote_addresses():
    from evals.test_s012_journey_through_a_host import _environment_of

    assert _environment_of("http://localhost:18080") == "localhost:18080"
    assert _environment_of("https://eval.keeldiscovery.com") == "eval.keeldiscovery.com"
    assert _environment_of("https://eval.keeldiscovery.com:8443/") == "eval.keeldiscovery.com:8443"
    assert _environment_of("http://[::1]:18080") == "[::1]:18080"


def test_the_chooser_is_clicked_by_identity_id_not_by_name():
    from harness.browser import chooser_button_selector
    sel = chooser_button_selector("ubuntu-24.04-copilot-py3.9-20260911T044858-ab12")
    assert 'input[name="identity"][value="ubuntu-24.04-copilot-py3.9-20260911T044858-ab12"]' in sel
    assert sel.endswith('button[type="submit"]')
    assert 'value="a\\"b"' in chooser_button_selector('a"b')


def test_hosts_resolve_their_binary_through_path_lookup(monkeypatch):
    import shutil
    from harness import copilot_host, claude_host
    monkeypatch.setattr(shutil, "which", lambda name: None)
    assert copilot_host.readiness("copilot")["ok"] is False
    assert claude_host.readiness("claude")["ok"] is False
    seen = {}
    monkeypatch.setattr(shutil, "which", lambda name: r"C:\\tools\\%s.cmd" % name)
    import subprocess
    def fake_run(argv, **kw):
        seen["argv"] = argv
        raise OSError("stop here")
    monkeypatch.setattr(subprocess, "run", fake_run)
    copilot_host.readiness("copilot")
    assert seen["argv"][0].endswith("copilot.cmd")


def test_a_host_built_with_the_default_binary_still_resolves_it_through_path(monkeypatch, tmp_path):
    import shutil
    from harness import agent_host
    monkeypatch.setattr(shutil, "which", lambda name: r"C:\\tools\\%s.cmd" % name)
    host = agent_host.build_host("copilot", home=tmp_path / "h", keel_home=tmp_path / "k",
                                 base_url="http://localhost:18080", artifacts=tmp_path / "a")
    assert host.binary.endswith("copilot.cmd")


# ----------------------------------------------------------------- how the skill arrives (spec 022)

def test_the_default_install_is_the_marketplace_plugin():
    assert agent_host.journey_install({}) == "plugin"
    assert agent_host.journey_install({"KEEL_JOURNEY_INSTALL": ""}) == "plugin"


def test_the_speckit_install_is_read_and_named_in_the_bundle():
    assert agent_host.journey_install({"KEEL_JOURNEY_INSTALL": " SpecKit "}) == "speckit"
    assert agent_host.bundle_slug("claude", "short", "speckit") == "s012-journey-claude-short-speckit"
    assert agent_host.bundle_slug("claude", "full", "plugin") == "s012-journey-claude"


def test_an_unknown_install_is_refused_by_name():
    with pytest.raises(agent_host.UnknownInstall):
        agent_host.journey_install({"KEEL_JOURNEY_INSTALL": "pip"})


# ------------------------------------------------- how many people answer (spec 021, amended)

def test_the_full_journey_invites_five_people_by_default():
    """The founder, 2026-09-13: *"increase it to five, so that I see a completed brief."* The
    product calls a line *Too few to call* under five people; one person never finished a brief
    with a verdict in it."""
    assert agent_host.DEFAULT_PEOPLE == 5
    assert agent_host.journey_people("full", {}) == 5
    assert agent_host.journey_people("full", {"KEEL_JOURNEY_PEOPLE": ""}) == 5
    assert agent_host.journey_people(None, {"KEEL_JOURNEY_LEGS": "full"}) == 5


def test_people_can_be_set_by_the_environment_on_the_full_journey():
    assert agent_host.journey_people("full", {"KEEL_JOURNEY_PEOPLE": "2"}) == 2
    assert agent_host.journey_people("full", {"KEEL_JOURNEY_PEOPLE": " 12 "}) == 12


def test_the_short_journey_always_counts_one_whatever_the_environment_says():
    """The short journey never reaches the People page; a short bundle must not claim a count
    it did not pay for."""
    assert agent_host.journey_people("short", {}) == 1
    assert agent_host.journey_people("short", {"KEEL_JOURNEY_PEOPLE": "5"}) == 1
    assert agent_host.journey_people(None, {"KEEL_JOURNEY_LEGS": "short",
                                            "KEEL_JOURNEY_PEOPLE": "9"}) == 1


@pytest.mark.parametrize("raw", ["0", "-1", "five", "2.5"])
def test_a_people_count_that_is_not_a_whole_number_is_refused(raw):
    with pytest.raises(agent_host.UnknownPeople) as excinfo:
        agent_host.journey_people("full", {"KEEL_JOURNEY_PEOPLE": raw})
    assert raw in str(excinfo.value)


def test_the_make_target_and_the_scenario_carry_the_people_axis():
    assert "KEEL_JOURNEY_PEOPLE=$(if $(PEOPLE),$(PEOPLE),$(KEEL_JOURNEY_PEOPLE))" in MAKEFILE, (
        "`make eval-live K=s012 PEOPLE=n` no longer reaches the scenario")
    assert "PEOPLE = agent_host.journey_people(LEGS)" in SCENARIO
    assert "corpus_script.people_to_invite(entry, PEOPLE)" in SCENARIO
    for key in ('"people": people_names', '"people_count": len(people_chosen)'):
        assert key in SCENARIO, f"the journey block no longer records {key}"


def _lullaby():
    from harness import corpus_script
    from stack.config import load_config
    config = load_config(validate=False)
    keel_cloud = Path(config.keel_cloud)
    if not (keel_cloud / "canon" / "designs" / "measured-beliefs" / "corpus").is_dir():
        pytest.skip(f"no keel-cloud corpus at {keel_cloud}")
    return corpus_script.entry_for(keel_cloud, "03-lullaby")[1]


def test_the_first_five_people_are_taken_in_corpus_order():
    from harness import corpus_script
    entry = _lullaby()
    everyone = corpus_script.person_inputs(entry)
    chosen, skipped = corpus_script.people_to_invite(entry, 5)
    assert [p.person for p in chosen] == [p.person for p in everyone[:5]]
    assert all(p.written() for p in chosen)
    assert skipped == []
    one, _ = corpus_script.people_to_invite(entry, 1)
    assert [p.person for p in one] == [everyone[0].person]


def test_a_person_with_nothing_written_is_skipped_by_name():
    """A taps-only person cannot be typed for on a live page; they are named in the bundle's
    inputs rather than sent in with a blank page."""
    from dataclasses import replace
    from harness import corpus_script
    entry = _lullaby()
    everyone = corpus_script.person_inputs(entry)
    silent = replace(everyone[1], anchors=[replace(a, text=None, tap="HASNT_HAPPENED")
                                           for a in everyone[1].anchors])
    fake = [everyone[0], silent, *everyone[2:]]
    chosen, skipped = corpus_script.people_to_invite.__wrapped__(fake, 3) if hasattr(
        corpus_script.people_to_invite, "__wrapped__") else _invite_from(fake, 3)
    assert [p.person for p in chosen] == [everyone[0].person, everyone[2].person, everyone[3].person]
    assert skipped == [everyone[1].person]


def _invite_from(people, count):
    """`people_to_invite` over a list the test built, through the same rule."""
    from harness import corpus_script

    class Entry:
        pass

    class _Person:
        pass
    saved = corpus_script.person_inputs
    corpus_script.person_inputs = lambda entry: people
    try:
        return corpus_script.people_to_invite(Entry(), count)
    finally:
        corpus_script.person_inputs = saved
