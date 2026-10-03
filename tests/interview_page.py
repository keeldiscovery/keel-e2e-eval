"""A real Keel Interview, in a real browser, from a small description of its occasions.

**Why a fixture and not a string.** What keel-web spec 042 changed is a *shape*: the participant's
single scroll became a pager, and three of this harness's page-object reads went stale on the move
(`runs/DRIFT.md` #71). A shape cannot be shown with string comparison -- the words the old locators
matched are mostly still on the page, just on another screen or under another class -- so the tests
that hold `ParticipantPage` to the pager drive the pager, the way
`tests/test_participant_submit_sent.py` and `tests/test_doors_d5_reveal_regions.py` have always
driven real DOM.

**It mirrors `ParticipantRoute.tsx`, and only the parts a page object touches**: the chrome
(`div.iv-page` > `header.iv-head` + `div.iv-progress` + `main.iv-body` + `footer.iv-foot`), the
three screens (opening / one per occasion / `.iv-done`), `AnchorBlock`'s fragment (a `div.q` with
the story box, then `div.picks` as its **sibling**), `SelectionBlock`'s keyed option rows, the one
`BLANK_ANCHOR_NUDGE` (global-once, on the first *Next* or *Send my answers* pressed with a blank
story in that part), the `.stale` refusal, and `localStorage`'s **Continue**. It is not keel-web and
makes no claim to be: every class and label in it is copied from that route and from
`src/lib/translate.ts`, and a copy change in either shows up here as a failing test rather than as a
dead wait on a live run.
"""

from __future__ import annotations

import json
from typing import Any

# Copied from keel-web `src/lib/translate.ts` (spec 042). The harness has its own copies of the
# labels it presses (`harness/browser.py`); these are the page's side of the same words.
HEAD_WHAT = "Research interview"
METHOD = ("Each part asks about one particular time something happened — the most recent one. If it "
          "hasn't happened to you, say so; that's an answer too.")
CONSENT_HEADING = "What happens to your answers"
CONSENT_LINE = "Your answers go to Eval Founder and nobody else. Nothing here asks for your name."
FACTS = "About 20 minutes · 3 parts · You can skip any question."
WHY = ("There's no right answer. Eval Founder chose who to ask and sent you this link; what's "
       "useful is what actually happened, even if it was ordinary.")
BEGIN = "Begin"
CONTINUE = "Continue"
DRAFT_LINE = "What you've answered so far is still here."
NEXT = "Next"
BACK = "Back"
SEND = "Send my answers"
DONE_TITLE = "That's it."
TAP_NOTE_HASNT_HAPPENED = "Thanks — that answers this part. On to the next."
TAP_NOTE_ESTIMATE = ("You can still answer the picks below roughly; they'll be kept as estimates, "
                     "not as something that happened.")
NUDGE = "Can you think of one specific time this happened? When was it, roughly?"
OTHER_SAY_WHAT = "other, say what"


def anchor(prompt: str, *, taps: list[str] | None = None,
           selections: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """One occasion's story box and the controls under it. `selections` entries are
    `{prompt, options, escapes?, other?}`."""
    return {"prompt": prompt, "taps": list(taps or []), "selections": list(selections or [])}


def selection(prompt: str, options: list[str], *, escapes: list[str] | None = None,
              other: bool = False) -> dict[str, Any]:
    return {"prompt": prompt, "options": list(options), "escapes": list(escapes or []),
            "other": bool(other)}


def part(title: str, anchors: list[dict[str, Any]]) -> dict[str, Any]:
    return {"title": title, "anchors": list(anchors)}


def interview_html(parts: list[dict[str, Any]], *, intro: str = "Eval Founder asked if you'd "
                   "answer a few questions about getting a baby back to sleep.",
                   done_lead: str = "Thanks, Yara Haddad. Your answers have gone to Eval Founder.",
                   presses_to_send: int = 1, refusal: str = "", draft_at: int | None = None) -> str:
    """The whole interview as one page.

    `presses_to_send` is how many presses of *Send my answers* the server takes before the
    completion screen -- `99` is the genuine dead end, a send that never sends however often it is
    pressed, which is the companion case that keeps `send()` from being credulous. `refusal` renders
    the `.stale` notice keel-cloud shows when it refuses a response; it is on the part screens from
    the start, exactly as a refused send leaves it. `draft_at` is a kept draft in `localStorage`:
    the gate reads **Continue**, `p.iv-draft` is drawn under it, and pressing it resumes at that
    part (0-based).
    """
    data = json.dumps({"parts": parts, "intro": intro, "doneLead": done_lead,
                       "pressesToSend": presses_to_send, "refusal": refusal,
                       "draftAt": draft_at}, ensure_ascii=False)
    words = json.dumps({
        "headWhat": HEAD_WHAT, "method": METHOD, "consentHeading": CONSENT_HEADING,
        "consentLine": CONSENT_LINE, "facts": FACTS, "why": WHY, "begin": BEGIN,
        "continue": CONTINUE, "draftLine": DRAFT_LINE, "next": NEXT, "back": BACK, "send": SEND,
        "doneTitle": DONE_TITLE, "tapHasnt": TAP_NOTE_HASNT_HAPPENED,
        "tapEstimate": TAP_NOTE_ESTIMATE, "nudge": NUDGE, "other": OTHER_SAY_WHAT,
    }, ensure_ascii=False)
    return _PAGE.replace("__DATA__", data).replace("__WORDS__", words)


_PAGE = r"""
<div id="root"></div>
<script>
const DATA = __DATA__;
const W = __WORDS__;
const root = document.getElementById("root");
const M = DATA.parts.length;

// The page's own state, exactly what `OpenForm` holds: which screen, every story and tap, every
// pick, and the one nudge with the part it fired on.
const state = {
  screen: "opening",           // "opening" | 0..M-1 | "done"
  resumeAt: DATA.draftAt === null ? 0 : DATA.draftAt,
  anchors: {},                 // prompt -> {text, tap}
  picks: {},                   // selection prompt -> [label]
  nudgedAt: null,
  nudgeSpent: false,
  presses: 0,
};

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
                  .replace(/"/g, "&quot;");
}

function anchorState(prompt) {
  if (!state.anchors[prompt]) state.anchors[prompt] = { text: "", tap: undefined };
  return state.anchors[prompt];
}

function tapKindOf(a, word) {
  // The contract's own order decides, never the word (`tapKind(index)`).
  const i = (a.taps || []).indexOf(word);
  return i === 0 ? "HASNT_HAPPENED" : i === 1 ? "CANT_RECALL" : "RATHER_NOT_SAY";
}

function rowHtml(label, escape) {
  const on = false;
  const more = /say roughly$/i.test(label) ? "roughly how much?"
             : /say what$/i.test(label) ? "what?" : null;
  const classes = ["opt", escape ? "esc" : null].filter(Boolean).join(" ");
  return '<div>'
    + '<div class="' + classes + '" role="radio" aria-checked="' + on + '" tabindex="0">'
    + '<i></i>' + esc(label) + '</div>'
    + (more ? '<div class="opt__more" hidden><input placeholder="' + esc(more)
              + '" aria-label="' + esc(more) + '"></div>' : '')
    + '</div>';
}

function selectionHtml(sel) {
  const body = (sel.options || []).concat(sel.other ? [W.other] : []);
  const rows = body.map((l) => rowHtml(l, false)).join("")
             + (sel.escapes || []).map((l) => rowHtml(l, true)).join("");
  return '<div class="q"><p>' + esc(sel.prompt) + '</p>'
    + '<div class="opts" role="radiogroup" aria-label="' + esc(sel.prompt) + '">'
    + rows + '</div></div>';
}

function anchorHtml(a) {
  const st = anchorState(a.prompt);
  const kind = st.tap ? tapKindOf(a, st.tap) : undefined;
  const hide = kind === "HASNT_HAPPENED";
  const dim = kind === "CANT_RECALL" || kind === "RATHER_NOT_SAY";
  let html = '<div class="q"><p>' + esc(a.prompt) + '</p>'
    + '<textarea class="' + (st.tap ? "box off" : "box") + '" aria-label="' + esc(a.prompt) + '">'
    + esc(st.tap ? "" : st.text) + '</textarea>';
  if ((a.taps || []).length) {
    html += '<div class="taps">'
      + a.taps.map((w) => '<span role="button" tabindex="0" class="'
          + (st.tap === w ? "chip on" : "chip") + '">' + esc(w) + '</span>').join("")
      + '</div>';
  }
  if (kind) html += '<p class="iv-tapnote">' + esc(hide ? W.tapHasnt : W.tapEstimate) + '</p>';
  html += '</div>';
  if (!hide) {
    html += '<div class="' + (dim ? "picks off" : "picks") + '">'
      + (a.selections || []).map(selectionHtml).join("") + '</div>';
  }
  return html;
}

function bodyHtml() {
  if (state.screen === "opening") {
    const kept = DATA.draftAt !== null;
    return '<main class="iv-body">'
      + '<p class="iv-intro">' + esc(DATA.intro) + '</p>'
      + '<p class="iv-method">' + esc(W.method) + '</p>'
      + '<section class="iv-consent"><h2>' + esc(W.consentHeading) + '</h2>'
      + '<p>' + esc(W.consentLine) + '</p></section>'
      + '<p class="iv-facts">' + esc(W.facts) + '</p>'
      + '<p class="iv-why">' + esc(W.why) + '</p>'
      + '<div class="iv-actions"><button type="button" class="btn primary" id="primary">'
      + esc(kept ? W.continue : W.begin) + '</button></div>'
      + (kept ? '<p class="iv-draft">' + esc(W.draftLine) + '</p>' : '')
      + '</main>';
  }
  if (state.screen === "done") {
    return '<main class="iv-body"><div class="iv-done">'
      + '<h1>' + esc(W.doneTitle) + '</h1>'
      + '<p class="iv-done__lead">' + esc(DATA.doneLead) + '</p>'
      + '<p class="iv-done__next">Eval Founder reads them alongside everyone else\'s.</p>'
      + '<a class="iv-done__what" href="/">What is Keel? →</a>'
      + '</div></main>';
  }
  const i = state.screen;
  const p = DATA.parts[i];
  const last = i === M - 1;
  return '<main class="iv-body">'
    + '<p class="iv-n">' + (i + 1) + ' of ' + M + '</p>'
    + '<h1 class="iv-sect">' + esc(p.title) + '</h1>'
    + (p.anchors || []).map(anchorHtml).join("")
    + (DATA.refusal ? '<div class="stale" role="alert">' + esc(DATA.refusal) + '</div>' : '')
    + '<div class="iv-actions">'
    + (i > 0 ? '<button type="button" class="btn link" id="back">' + esc(W.back) + '</button>' : '')
    + '<button type="button" class="btn primary" id="primary">'
    + esc(last ? W.send : W.next) + '</button></div>'
    + (state.nudgedAt === i ? '<p class="iv-nudge">' + esc(W.nudge) + '</p>' : '')
    + '</main>';
}

function nudgeOnce(i) {
  if (state.nudgeSpent) return false;
  const anchors = (DATA.parts[i].anchors || []);
  const blank = anchors.some((a) => {
    const st = anchorState(a.prompt);
    return !st.text.trim() && !st.tap;
  });
  if (!blank) return false;
  state.nudgeSpent = true;
  state.nudgedAt = i;
  return true;
}

function render() {
  root.innerHTML = '<div class="iv-page">'
    + '<header class="iv-head"><span>KEEL</span>'
    + '<span class="iv-head__what">' + esc(W.headWhat) + '</span></header>'
    + '<div class="iv-progress" aria-hidden="true"><i></i></div>'
    + bodyHtml()
    + '<footer class="iv-foot"><span>Keel</span><span aria-hidden="true">·</span>'
    + '<a href="/privacy">Privacy</a></footer>'
    + '</div>';
  wire();
}

function wire() {
  for (const el of root.querySelectorAll("main.iv-body textarea.box")) {
    const prompt = el.getAttribute("aria-label");
    el.addEventListener("input", () => { anchorState(prompt).text = el.value; });
  }
  for (const block of root.querySelectorAll("main.iv-body div.q")) {
    const promptEl = block.querySelector(":scope > p");
    const box = block.querySelector(":scope > textarea.box");
    if (!promptEl || !box) continue;
    const prompt = promptEl.innerText.trim();
    const a = (DATA.parts[state.screen] || { anchors: [] }).anchors
                .find((x) => x.prompt === prompt) || { taps: [] };
    for (const chip of block.querySelectorAll(".taps > .chip")) {
      const word = chip.innerText.trim();
      chip.addEventListener("click", () => {
        const st = anchorState(prompt);
        st.tap = st.tap === word ? undefined : word;
        if (st.tap) st.text = "";
        render();
      });
    }
    void a;
  }
  for (const row of root.querySelectorAll("main.iv-body .opts .opt")) {
    row.addEventListener("click", () => {
      const group = row.closest(".opts");
      for (const other of group.querySelectorAll(".opt")) {
        other.classList.remove("on");
        other.setAttribute("aria-checked", "false");
        const box = other.parentElement.querySelector(".opt__more");
        if (box) box.hidden = true;
      }
      row.classList.add("on");
      row.setAttribute("aria-checked", "true");
      const box = row.parentElement.querySelector(".opt__more");
      if (box) box.hidden = false;
    });
  }
  const back = root.querySelector("#back");
  if (back) back.addEventListener("click", () => { state.screen = state.screen - 1; render(); });
  const primary = root.querySelector("#primary");
  if (primary) primary.addEventListener("click", () => {
    if (state.screen === "opening") { state.screen = state.resumeAt; render(); return; }
    const i = state.screen;
    if (i === M - 1) {
      if (nudgeOnce(i)) { render(); return; }
      state.presses += 1;
      if (state.presses >= DATA.pressesToSend && !DATA.refusal) state.screen = "done";
      render();
      return;
    }
    if (nudgeOnce(i)) { render(); return; }
    state.screen = i + 1;
    render();
  });
}

render();
</script>
"""
