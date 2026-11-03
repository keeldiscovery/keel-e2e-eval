"""Spec 130 FR-2 (the contract mirror) and the pieces of FR-1 / FR-3 that need no stack: keel-cloud 201's contract 58
and document version 36, keel-web 163's words and selectors, `harness/sharing.py`'s rules,.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from harness import sharing
from stack.config import load_config

CONFIG = load_config(validate=False)
KEEL_CLOUD = Path(CONFIG.keel_cloud)
KEEL_WEB = Path(CONFIG.keel_web)


def _cloud(path: str) -> str:
    full = KEEL_CLOUD / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_CLOUD}")
    return full.read_text(encoding="utf-8")


def _web(path: str) -> str:
    full = KEEL_WEB / path
    if not full.is_file():
        pytest.skip(f"no {path} at {KEEL_WEB}")
    return full.read_text(encoding="utf-8")


def _contract() -> dict:
    text = _cloud("canon/openapi-v2.yaml")
    if int(re.search(r"x-keel-contract: (\d+)", text).group(1)) < sharing.CONTRACT:
        pytest.skip("keel-cloud before 201: contract below 58")
    return yaml.safe_load(text)


# ------------------------------------------------------------------------------------- FR-2: contract 58

def test_contract_58_serves_the_sharing_routes():
    spec = _contract()
    paths = spec["paths"]
    assert sharing.LISTS in paths and "get" in paths[sharing.LISTS]
    for read in sharing.PUBLIC_READS:
        assert "get" in paths[f"/v2/s/{{token}}{read}"], read
    for name, (method, path) in sharing.OWNER_ROUTES.items():
        route = path.replace("{id}", "{projectId}")
        assert method.lower() in paths[route], (name, route)
        assert "sharing" in paths[route][method.lower()]["tags"], name
    assert len([p for p in paths if p.startswith("/v2/s/")]) == len(sharing.PUBLIC_READS)


def test_contract_58_names_the_shapes_the_journeys_read():
    schemas = _contract()["components"]["schemas"]
    assert set(schemas["SharingState"]["required"]) == {"viewers", "coFounders"}
    on = lambda keys: {"on" if k is True else k for k in keys}         # noqa: E731 - YAML 1.1 reads `on` as true
    assert on(schemas["SharingLink"]["required"]) == {"on", "token", "url"}
    assert set(schemas["SharingGrant"]["required"]) == {"email", "since"}
    assert on(schemas["SharingLinkRequest"]["properties"]) == {"on", "rotate"}
    assert schemas["SharingAddressRequest"]["required"] == ["email"]
    assert set(schemas["ProjectLists"]["required"]) == {"mine", "sharedProjects", "sharedOverviews"}
    row = schemas["SharedProjectListRow"]["allOf"][1]
    assert row["required"] == ["sharedBy"] and set(row["properties"]["sharedBy"]["required"]) == {"firstName", "name"}
    assert schemas["SharedRoot"]["required"] == ["projectId"]
    overview = schemas["Overview"]["properties"]
    assert tuple(overview["access"]["enum"]) == sharing.ACCESS
    assert {"credits", "sharedBy"} <= set(overview)
    assert "access" not in (schemas["Overview"].get("required") or []), "optional: a cloud before 58 serves none"


def test_document_version_36():
    text = _cloud("src/main/java/com/keeldiscovery/cloud/infrastructure/persistence/project/ProjectDocument.java")
    assert f"static final int SCHEMA_VERSION = {sharing.DOCUMENT_VERSION};" in text
    assert "static final int MIN_READABLE_VERSION = 21;" in text


# ------------------------------------------------------------------------- keel-web 163: words, selectors

def test_the_words_are_keel_webs():
    text = _web("src/lib/translate.ts")
    for name, value in (("SHARE_LABEL", sharing.SHARE_LABEL), ("SHARED_LABEL", sharing.SHARED_LABEL),
                        ("SHARE_NOT_EMAIL", sharing.SHARE_NOT_EMAIL), ("SHARE_OWN_ADDRESS", sharing.SHARE_OWN_ADDRESS),
                        ("SHARED_LINK_GONE", sharing.SHARED_LINK_GONE), ("NAV_NOT_SHARED", sharing.NAV_NOT_SHARED),
                        ("SHARED_TRY_KEEL", sharing.SHARED_TRY_KEEL),
                        ("PROJECTS_NONE_MATCH", sharing.PROJECTS_NONE_MATCH),
                        ("PROJECTS_NONE_SHARED", sharing.PROJECTS_NONE_SHARED)):
        assert f'export const {name} = "{value}";' in text, name
    assert "export const sharedByBrand = (name: string, firstName: string): string => `${name} (shared by " \
           "${firstName})`;" in text
    assert "export const namesPageOf = (n: number, of: number): string => `Page ${n} of ${of}`;" in text
    for tab, words in (("Mine", "My projects"), ("Shared", "Projects shared with me"),
                       ("Overviews", "Overviews shared with me")):
        assert f"export const projectsTab{tab} = (n: number, of?: number): string => `{words} · " in text, tab
    assert f"export const ROWS_PER_PAGE = {sharing.PAGE_SIZE};" in _web("src/lib/sharing.ts")


def test_every_selector_is_drawn_by_keel_web():
    sources = "\n".join(p.read_text(encoding="utf-8") for p in (KEEL_WEB / "src").rglob("*.tsx")) \
        if (KEEL_WEB / "src").is_dir() else pytest.skip("no keel-web")
    templated = {"share-what-overview": "share-what-${option}", "share-what-project": "share-what-${option}",
                 "share-who-viewers": "share-who-${kind}", "share-who-coFounders": "share-who-${kind}",
                 "projects-tab-mine": "projects-tab-${key}", "projects-tab-sharedProjects": "projects-tab-${key}",
                 "projects-tab-sharedOverviews": "projects-tab-${key}"}
    for testid in sharing.TESTIDS:
        assert f'data-testid="{testid}"' in sources or templated.get(testid, "\0") in sources, testid
    assert '<Route path="/s/:token/*" element={<SharedLinkRoute />} />' in _web("src/routes/AppRoutes.tsx")
    assert '"brandrow"' in _web("src/routes/founder/ProjectShell.tsx") and '"hint"' in \
        _web("src/routes/founder/ProjectShell.tsx")


# ----------------------------------------------------------------------------- harness/sharing.py's rules

def test_the_lines_are_composed_as_keel_web_composes_them():
    assert sharing.share_summary(link_on=True, viewers=0, co_founders=0) == "link on"
    assert sharing.share_summary(link_on=True, viewers=2, co_founders=1) == "link on · 2 can view · 1 works on it"
    assert sharing.share_summary(link_on=False, viewers=0, co_founders=3) == "3 work on it"
    assert sharing.share_summary(link_on=False, viewers=0, co_founders=0) == ""
    assert sharing.shared_brand("Paidly", "Daphne", "United States") == "Paidly (shared by Daphne) · United States"
    assert sharing.shared_brand("Paidly", "Daphne", None) == "Paidly (shared by Daphne)"
    assert sharing.tab_label("mine", 6) == "My projects · 6"
    assert sharing.tab_label("sharedOverviews", 1, 2) == "Overviews shared with me · 1 of 2"
    assert sharing.tab_label("sharedProjects", 0, 3) == "Projects shared with me · 0 of 3"
    assert (sharing.page_label(1, sharing.pages_of(6)), sharing.pages_of(5), sharing.pages_of(0)) == \
        ("Page 1 of 2", 1, 1)


def test_the_search_reads_the_project_and_the_owner():
    row = {"name": "Countly", "sharedBy": {"firstName": "Eval", "name": "Eval 1102 local"}}
    assert sharing.matches_search(row, "count") and sharing.matches_search(row, "EVAL 1102")
    assert not sharing.matches_search(row, "zqxjv")
    assert sharing.matches_search(row, "  ")


def test_the_wire_helpers():
    assert sharing.first_name("Eval 1102 local") == "Eval" and sharing.first_name(None) == ""
    assert sharing.token_of("https://eval.keeldiscovery.com/s/AbC_123-xyz9876") == "AbC_123-xyz9876"
    assert sharing.token_of("https://x/s/short") is None and sharing.token_of(None) is None
    assert sharing.owner_route("remove_viewer", "p1", "a@b.co") == ("DELETE", "/v2/projects/p1/sharing/viewers/a@b.co")
    assert sharing.public_path("tok", "/calibration/{vector}", "COMMERCIAL") == "/v2/s/tok/calibration/COMMERCIAL"
    assert sharing.bare_404(404, "") and not sharing.bare_404(404, '{"rule":"x"}') and not sharing.bare_404(403, "")
    payload = {"people": [{"invitationId": "i1", "personName": "Person 1", "email": None},
                          {"invitationId": "i2", "personName": "Priya Natarajan", "email": "p@x.co"}],
               "line": "Priya skipped it"}
    assert sharing.names_out(payload, ["Priya Natarajan", "Tom Okafor"]) == ["Priya Natarajan"]
    assert sharing.names_out({"line": "Person 2 skipped"}, ["Priya Natarajan"]) == []
    assert sharing.person_fields_out(payload) == ["$.people[1].email"]
