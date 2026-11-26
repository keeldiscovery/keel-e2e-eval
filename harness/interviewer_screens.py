"""keel-web 069's AI interviewer, as page objects (spec 044 T003; keel-web master `d23895f`), and keel-web 072's answer
path (spec 048 T003, contract 18: no *That's my answer*, the three tiers, the hold, Back, Test your mic).

Machinery, not judgement: every class here acts and reads, and asserts nothing -- `evals/interviewer_leg.py` judges.
The words are copied from keel-web `src/lib/translate.ts`; the selectors are the ones 069's tasks.md names for this
repository (*Selectors (for keel-e2e-eval 044)*) and 072's spec names (`ai-yes`, `ai-back`, `ai-mic-test`,
`ai-mic-heard`, `start-talking` -- `ai-start` since keel-web 256, spec 160).

Spec 160 (keel-web 256, the player pared down): the first screen's one button (*Test your mic*, `ai-mic-test`, becomes
*Start the interview*, `ai-start`, once hello is heard; never both), the refused microphone a block (`ai-mic-block`, no
Start), the intro's headline *{founder} has {n} questions for you.* with the spoken line under it, three chips and the
closed *What happens to your answers* (`ai-intro-answers`); the film's two icons (`ai-film-pause`, `ai-film-again`), the
board tapped for the words (`ai-film-board`, `story-read`) and *Begin the interview* (`ai-film-begin`); the replay mark
(`ai-replay`) where *Say it again* (`ai-again`) was; the speaker's two sizes (`data-size` on `ai-orb` / `ai-facecol`),
the words lit (`ai-words`); the face's chip *{name} · AI interviewer* (`face_mark`); the last page's tick
(`ai-done-tick`) over *Done. Your answers have gone to {founder}.*

Spec 170 (keel-web 266, the entry screen): the name line and one sentence (`ai-intro-line`), then one button in three
states -- *Test your mic* (`ai-mic-test`) -> the wave and *Say anything.* (`ai-mic-say`) -> *Your mic works.*
(`ai-mic-heard`) above **Begin** (`ai-start`); the mic passes on sound, so the hello's words are no longer read; a screen
still showing 256's words is a DRIFT capture note (`entry_drift`), never a fault of the walk.

* `Persona`   -- Sent's persona line (`[data-testid=persona-line]`, `data-state`), its progress bar, *Change who asks* /
                 *Record the interviewer* and the popup (`[data-testid=change-face-popup]`, the carousel,
                 `[data-testid=change-face-confirm]`), the role cards' *Try it yourself*, Send more's format row read
                 and cancelled, L1 revisited; since keel-web 088 the band's *Hear <name>* (`persona-hear`) and the
                 absence of *How it works* (the replay of W1 is gone, spec 059).
* `Player`    -- the AI interviewer's page for a stranger or the founder's dry run: the intros (072: *Test your mic*),
                 the stage (`data-phase`, the one `<video>`, the pills, End, the ship mark), the sheet (options, field,
                 escape, preview, heard, status, Back, *Yes, that's it*, *Save and next* for typed words, *Finish* on
                 the pilot, *Type instead*) and the end screens. 072: an utterance ends on a final result (the seam's
                 recogniser then ends, as Chrome's does); the cloud's classifier decides (`classify`); a confident read
                 is **held** two seconds and the interview goes on by itself (`hold`), a word of protest reopens it
                 (`veto`), an unsure one asks "Is that right?" (`yes`), and *Back* reopens the last question (`back`).
* `SPEECH_SEAM` -- the init script that stands in for the browser's recorder and microphone through the test build's
                 own seam (`window.__keelSpeech`, present only under `vite --mode test`, which the stack serves): keel-web's
                 own `tests/fixtures/interviewer/fakeSpeech.ts`, restated in JavaScript. `__say(text, final)` is the
                 stranger speaking into the window the page records (spec 074: keel-web 115's one recorded path). No
                 microphone is opened. **No `classify` or `answer` is put on the seam** (spec 048 judgement call 1): the
                 page calls the real routes, and the stack's keel-cloud writes the recording down with its
                 `FakeTranscriber` (keel-cloud 136 FR-2: the recording's bytes are the words said) and reads it with its
                 `FakeClassifier` -- what staging runs for eval founders too.

Spec 049 (keel-web 073, *hear them out*): nothing lights or fills while they speak, and an utterance is read
`QUIET_MS` (1.5 s) after the recogniser's end after a final -- the page restarts the recogniser for that gap, so a
final said within it joins the same utterance. `say()` keeps what the sheet showed while the words were heard
(`hearing`: nothing newly lit, the field and the preview untouched); `ear()` counts a recogniser as listening only while
the page still hands it results (keel-web's `__listening()`, 073 D-04: recogniser counts now grow on every final's end);
the earcons are switched off on the seam (073 FR-8). (073 FR-6's *tapped checkboxes wait for *Save and next** no longer
applies to any item since keel-web 135: Importance's ticks go on by themselves at the second tap and contract 47 serves
no other multi -- spec 090 FR-2, H-8; `save` / `save_state` stay for typed words.)

Spec 050 (keel-web 074 + 075): the gap is 4.0 s on every window (the walk still encodes none); the story says how to
end it (`STORY`) and its *Save and next* reads it at once; a yes to *Is that right?* is held (`data-unsure="false"`,
`ai-ring`); the live waveform `ai-mic-on` while a window listens; after the problem and the idea passages a 2.0 s
**beat** (`data-phase="beat"`, the status *Take a moment.*, the pill *pause*, nothing listening) -- the timeline keeps
each beat as it was drawn and the seam stamps every recogniser started, so the leg can say nothing listened in it;
*Microphone off* (`ai-mic-off`) on the end screens once everything is released.

Spec 051 (keel-web 076, contract 19): the one follow-up -- on the AI page the sheet's `data-step="followUp"`, the
`ai-where` pill (*One more thing* since keel-web 126), the story's window, `ai-skip`; on the text page `SpeakOrTypeBox` (`.sot[data-state]`,
the `iv-mic` pill, the listening card `iv-listening` with `ai-mic-on`, `iv-mic-clock`, `iv-mic-cancel`, `iv-mic-done`)
driven through `text_seam` (a microphone that counts its acquisitions, refused on request, and a recorder whose level
the walk sets) -- `SpeakBox` reads and drives it. (Spec 074: the AI page's seam is the recorder itself now; the
`RECORDER_SEAM` that a refusing recogniser fell back to is gone.)

Spec 058 (keel-web 087, contract 23): **tap to hear** -- a tap on an unpicked card of the carousel picks it and plays
her hello in a `video` inside the card (`face-hear`, the play glyph on each unpicked card), and the respondent's intro
plays it under *Hear <name>* (`intro-hear`). `HEAR_JS` listens for every `video`'s media events on the document (they do
not bubble; a capture listener hears them) and polls the choice buttons while it plays; `hear_card` / `Player.hear`
tap, wait for the clip's `ended` and the still's return, and return what was heard, for IM28 / IM29 to judge.

Spec 059 (keel-web 088, contract 24): Sent's persona line is the **who-asks band** (`.ivband`): READY draws *Hear
<name> · 5 s* (`persona-hear`, the name, never a pronoun; absent for a retired face), which plays the 087 hello in the
band's circle (`video.pface-hello__clip`) while the band carries `data-hearing`; `HEAR_JS` tags an event inside the band
`band`, and `Persona.hear_band` taps it and waits for the end. *How it works* is gone from Sent (the page's pill replaced
it), so `walkthrough_again` retired with it -- `how_it_works()` counts the controls of that name (none). `Persona.sent`
opens Sent through `interviews_screens.pass_interviews_sheet`, which skips 088's first-open sheet when drawn.

Spec 074 (keel-web 115, keel-cloud 136): **one recorded path**. The browser's recogniser is retired, and so are its
fake, `ear()` / `wait_ear`, the recogniser's counts and the `not-allowed` leg: every window records (`recorder()`,
`wait_listening`), `__say` pulses the recorder's level and puts the words in the recording, and each read is a `POST
.../answer` whose words `Player.classified` keeps (`decode_said`). While a question's window records the status reads
*Recording your answer. Pause when you're done.* (`RECORDING`) and the heard line *Hearing you…*. The text page's box
(`text_seam`) drives the same recorder by a level; `follow_up_cap_seam` shortens the AI follow-up's silent window.
Keel-web 116: the microphone is let go when the thank-you clip ends (`__micReleasedAt`, the timeline's `ended`).

Every write a press makes returns the response keel-web received, so the leg holds the wire the page was handed.
"""

from __future__ import annotations

import re
import time

from playwright.sync_api import Page

from harness import interviews_screens as _iv
from harness import three_surfaces as _ts
from harness.browser import _BrowserStep, _safe_text

# ---- spec 161 (keel-cloud 269 / 270, contract 87; keel-web 258): the four questions' words, one script on every surface
#: The gate after the film -- the orb, the face and the Copilot card alike -- found by its words (spec 169 FR-1,
#: keel-cloud 277: *In {window}, have you encountered this issue?*): `three_surfaces.GATE_WORDS`, one match.
GATE_WORDS = _ts.GATE_WORDS
#: keel-cloud 269 FR-3: Frequency's five rows, in order, letters A-E.
FREQUENCY_LABELS = ("Every time", "Most times", "About half the time", "Now and then", "Never")
#: Spec 161 FR-4 (keel-web 258 FR-2b): the order on a film link -- the opening passage, the screener (its own counted
#: step), the film ending on the pain scene, *Begin*, then the gate; without a screener the opening, the film, the gate.
FILM_LINK_ORDER = ("opening", "screener", "film", "begin", "gate")
FILM_LINK_ORDER_NO_SCREENER = ("opening", "film", "begin", "gate")

# ---- keel-web d23895f `translate.ts`
PERSONA_RECORDING = "Recording now, usually ready in about five minutes. You can leave this page."
PERSONA_NOT_RECORDED = "No interviewer recorded yet."
TRY_IT_YOURSELF = "Try it yourself"
TRY_IT_YOURSELF_RECORDING = "Try it yourself · recording"
#: Spec 154 (keel-web 187 FR-5, `translate.ts`): the kind card's one button and its words -- *Set up the AI interviewer ·
#: 1,500 once* (no price once the project has paid), *Try it yourself · soon* while that kind records, *Try it yourself*
#: once READY, *Try again* on FAILED; the line's tail *Daphne asks* / *Daphne is recording*; the progress words.
TRY_IT_YOURSELF_SOON = "Try it yourself · soon"
TRY_AGAIN_RECORDING = "Try again"
SETUP_INTERVIEWER = "Set up the AI interviewer"
SETUP_NOT_NOW = "Not now"
#: Spec 159 FR-4 (keel-web 253 FR-4, `RECORDING_MEANWHILE`): the TEXT format is *Keel's voice* -- it read *Read and tap
#: links can be made meanwhile.* (`RECORDING_MEANWHILE_BEFORE_253`).
RECORDING_MEANWHILE = "Keel's voice links can be made meanwhile."
RECORDING_MEANWHILE_BEFORE_253 = "Read and tap links can be made meanwhile."
FORMAT_RECORDING_SOON = "Recording · a few minutes"
SETUP_ALREADY_PAID = "Already paid for this project."


def setup_interviewer(price: int | None) -> str:
    return SETUP_INTERVIEWER if price is None else f"{SETUP_INTERVIEWER} · {price:,} once"


def setup_interviewer_kicker(kind_label: str) -> str:
    return f"{kind_label} · AI interviewer"


def setup_interviewer_title(people: str | None) -> str:
    return f"Who asks {(people or '').strip() or 'them'} the questions?"


def record_face(face: str, price: int | None) -> str:
    """187 `recordFace`: *Record Daphne · 1,500 credits*; *Record Daphne* once paid."""
    return f"Record {face}" if price is None else f"Record {face} · {price:,} credits"


def kind_asks(face: str) -> str:
    return f"{face} asks"


def kind_recording(face: str) -> str:
    return f"{face} is recording"


def recording_started(face: str) -> str:
    return f"{face} is recording, about five minutes. {RECORDING_MEANWHILE}"


def credits_refusal_for_recording(required: int, available: int) -> str:
    return f"Setting up the AI interviewer is {required:,} credits. You have {available:,}."
TRY_NOTHING_STORED = "Nothing was stored."
#: Spec 118 FR-4c(f) (keel-web 156 FR-2): the text route is *Read and tap* wherever the format is named -- the role
#: card's primary while the interviewer records (`SEND_TEXT_ONLY_LINKS`, it read *Send text-only links*).
SEND_TEXT_ONLY_LINKS = "Send read-and-tap links"
SEND_LINKS = "Send links"
SEND_FORMAT_RECORDED = "The interviewer is already recorded for this project."
#: keel-web 156 FR-2 (T007): renamed (*Read and tap is ready now*) and no longer drawn -- the status line under each row
#: (`FORMAT_STATUS`) says it; kept for a page before 156. `SEND_FORMAT_RECORDED` the same (still in keel-web's copy).
SEND_FORMAT_RECORDING = "The interviewer is still recording; Read and tap is ready now."
SEND_FORMAT_RECORD_ON_PICK = ("The interviewer is recorded when you first pick them, in about five minutes; Read and tap "
                              "is ready now.")
#: Spec 118 FR-4c(f) (keel-web 156 FR-2, `FORMAT_STATUS`, `format-status[data-format]`): the line under each option on an
#: account on Keel's AI -- in place of the bare *recording* tag and the foot sentences.
FORMAT_STATUS_RECORDING = "Still recording · ready in a few minutes"
FORMAT_STATUS_READY = "Ready now"
FORMAT_STATUS = "[data-testid='format-status']"
SEND_FORMAT_TITLE = "[data-testid='send-format-title']"


def format_status_when_ready(face: str) -> str:
    """keel-web 156 `FORMAT_STATUS.whenReady`: Let them choose while the face records -- *Ready when {Name} is*."""
    return f"Ready when {face} is"


def kind_people_plural(label: str | None, label_short: str | None = None) -> str | None:
    """keel-web 159 FR-1 (`kindPeoplePlural`): the kind's people in the plural by the lock step's rule
    (`vectors_screens.people_plural`) -- the served long `label` first, its `labelShort` where no label is served."""
    from harness.vectors_screens import people_plural                    # noqa: PLC0415
    return (people_plural(label) if label else None) or (people_plural(label_short) if label_short else None)


def send_format_title(label: str | None, label_short: str | None = None) -> str:
    """keel-web 156 FR-2 / 159 FR-1 (`sendFormatTitle(label, labelShort)`): Send more's heading names the kind's people
    in the plural -- *How should startup founders answer?* for a kind labelled *Startup founder* (cycle 5's *How should
    founder answer?*), a plural already said kept; *How should they answer?* only with no people to name."""
    people = kind_people_plural(label, label_short)
    return f"How should {people} answer?" if people else "How should they answer?"


#: keel-web 156 FR-1 / FR-2 (`INTERVIEWER_IS`): what the interviewer is -- the lock step's hint opens on it.
INTERVIEWER_IS = ("Keel's AI interviewer asks each question aloud on video, and every question is also written on the "
                  "screen, so people can read it and type or tap instead of talking.")
#: keel-web 156 FR-1 (`BEFORE_SEND_LATER`, `send-later`): the one line under the faces on the lock step.
BEFORE_SEND_LATER = ("When you send the links you can still offer a read-and-tap interview, where people speak or type "
                     "into any box, or let each person choose.")
#: keel-web 156 FR-2 (`SEND_FORMATS_069.TEXT`): the read-and-tap row's line, before keel-web 253.
READ_AND_TAP_LINE = ("They read each question and tap their answer. Where there is a box to fill, they can speak into it "
                     "or type.")
#: Spec 159 FR-4 (keel-web 253 FR-4, `SEND_FORMATS.TEXT.line` / `SEND_FORMATS_069.TEXT`): *Keel's voice*'s line.
KEELS_VOICE_LINE = ("Keel asks each question aloud in its own voice, and every question is also written on the screen. "
                    "They answer by talking or tapping. Nothing to set up.")   # keel-web 254: nothing typed


def before_interviewer_title(people: str | None) -> str:
    """keel-web 156 FR-1 (`beforeInterviewerTitle`): *Who should ask {actor_plural} your questions?* -- any length, never
    *them* but while the context is not read."""
    return f"Who should ask {(people or '').strip() or 'them'} your questions?"


def before_interviewer_sub(face: str, other: str, other_object: str, credits: int | None = None) -> str:
    """keel-web 156 FR-1 (`beforeInterviewerSub`): the lock step's hint -- what the interviewer is, the face picked and
    the other, what the recording costs whichever is picked, the text message. *The voice goes with the face* is gone."""
    cost = "Keel's credits" if credits is None else f"{credits} credits"
    return (f"{INTERVIEWER_IS} {face} is picked for you; tap {other} to hear {other_object} and switch. Keel records the "
            f"voice you pick once for this project: {cost}, whichever you choose. People get the link by text message "
            "either way.")


def send_ai_claim(subject: str, plural: bool = False) -> str:
    """keel-web 156 FR-2 (`sendAiClaim`): the accuracy claim with its subject, no example places."""
    return (f"{subject[:1].upper()}{subject[1:]} {'catch' if plural else 'catches'} every spoken answer in a quiet room, "
            "and more than 9 in 10 where it is loud.")


def face_hear_line(face: str, seconds: int = 5) -> str:
    """keel-web 156 FR-1 (`introHear`, `face-hear-line`): *▶ Hear {Name} · 5 s* on both faces of the lock step (the glyph
    is drawn apart from the words)."""
    return f"Hear {face} · {seconds} s"
#: Spec 092 FR-4a (keel-web 131 FR-3, `FORMAT_CREDITS_NOTE`): since 131 the first line under Send more's format rows, on
#: an account on Keel's AI (`format-credits`), is one interview's price in every way of answering -- in place of spec
#: 130's AI-only note. `SEND_FORMAT_RECORDED` / `SEND_FORMAT_RECORDING` above are unchanged and still drawn, under it.
FORMAT_CREDITS_NOTE = "Each person who answers uses 30 credits, whichever way they answer."
FORMAT_CREDITS = "[data-testid='format-credits']"
CHANGE_FACE_TITLE = "Change who asks"
RECORD_FACE_TITLE = "Record the interviewer"
#: keel-web 068's replay of W1 on Sent's header, gone with keel-web 088 FR-1 (spec 059): never on Sent again.
HOW_IT_WORKS = "How it works"
WALKTHROUGH_GOT_IT = "Got it"
#: The orb's chip, the served `InterviewerPlayer.mark` (`aiMarkWords`; a dry run adds *· try run*). Spec 160 (keel-web 256
#: FR-6, judgement call 9): the face's chip reads her own name -- `face_mark`.
MARK = "Keel · AI interviewer"
MARK_TRY = "Keel · AI interviewer · try run"
TRY_MARK_SUFFIX = "try run"


def face_mark(name: str, *, try_run: bool = False) -> str:
    """keel-web 256 FR-6 (`aiFaceMark`, `aiMarkWords`): the face's chip -- *{name} · AI interviewer* (*· try run* on a dry
    run), in her caption band while she speaks and under her portrait once the sheet opens."""
    words = f"{name} · AI interviewer"
    return f"{words} · {TRY_MARK_SUFFIX}" if try_run else words


# ---- spec 159 (keel-web 253 FR-1 / FR-2, keel-cloud 267 FR-2): one player, the orb in the face's place
#: `Interview.interviewer.speaker` (contract 84) and the player's `data-speaker`.
SPEAKER_ORB = "ORB"
SPEAKER_AVATAR = "AVATAR"
#: Spec 160 (keel-web 256 FR-1, `ORB_INTRO_NAME`): the orb's name in the intro's two sentences is *Keel*; the stage keeps
#: *Keel AI* (`AI_STAGE_LABEL_ORB`). 253's *Keel AI will ask you N questions.* / *It is an AI interviewer, not a person.*
#: are gone: the line under the headline names the speaker. Spec 170 (keel-web 266 FR-1): that one line is
#: `ai_intro_line` (`aiIntroLine`).
ORB_NAME = "Keel"
ORB_STAGE_NAME = "Keel AI"
ORB_STAGE_LABEL = "Keel AI, the AI interviewer"


#: keel-web `listSizeWord`: a count in words up to ten, digits past.
SIZE_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten")


def ai_intro_line(name: str, minutes: int | None = None, questions: int | None = None) -> str:
    """Spec 170 FR-1 (keel-web 266 FR-1, `aiIntroLine`): the one sentence under the name line -- *Keel* on the orb, her
    name on the face; *them* the questions (*it* on a one-question link); the minutes where served, in words up to ten,
    digits past (`listSizeWord`)."""
    them = "it" if questions == 1 else "them"
    if minutes:
        count = SIZE_WORDS[minutes] if 0 <= minutes < len(SIZE_WORDS) else str(minutes)
        return (f"{name} asks {them} aloud and listens, about {count} minute{'' if minutes == 1 else 's'}, so your mic "
                "has to be on.")
    return f"{name} asks {them} aloud and listens, so your mic has to be on."


#: Spec 170 FR-1 (keel-web 266 FR-1): the intro's one line (`ai-intro-line`); 256's study line, asks line and chips are
#: gone -- their ids are read only to say a screen still draws them (`ENTRY_IDS_BEFORE_266`, a DRIFT capture note).
INTRO_LINE_ID = "ai-intro-line"
ENTRY_IDS_BEFORE_266 = ("ai-intro-study", "ai-intro-asks", "ai-intro-chips")
#: keel-web 256 FR-1: the microphone line, verbatim, inside the closed *What happens to your answers* (`ai-intro-answers`)
#: with the transcriber line (`INTRO_TRANSCRIBED`) and the served consent.
AI_INTRO_MIC_LINE = "Your microphone is used only while you answer, and only your answers are kept."
INTRO_ANSWERS = "ai-intro-answers"
CONSENT_HEADING = "What happens to your answers"
#: The orb on the intro (`intro-orb`, the still orb where the face's hello was) and on the stage (`ai-orb`, with its state
#: line `ai-orb-state`); each wraps keel-web's `story-orb` (`KeelOrb still`). Spec 160 (keel-web 256 FR-3): the film's dim
#: orb (`ai-story-orb`) is gone -- no speaker above the board; kept here as the id the walk holds is never drawn.
INTRO_ORB = "intro-orb"
STAGE_ORB = "ai-orb"
STAGE_ORB_STATE = "ai-orb-state"
FILM_ORB = "ai-story-orb"
#: keel-web 256 FR-6: the face's column (`data-size`), its caption band while she speaks, its state line.
FACE_COL = "ai-facecol"
FACE_CAPTION = "ai-caption"
FACE_STATE = "ai-face-state"
#: keel-web 256 FR-5 / FR-6: the speaker's two sizes (`data-size` on `ai-orb` / `ai-facecol`) and the words lit as they
#: are said (`ai-words`, one `<span data-lit>` a word).
SIZE_LARGE = "large"
SIZE_SMALL = "small"
WORDS = "ai-words"
#: keel-web 256 FR-3: the respondent's film -- two icons, the board tapped for the words, *Begin the interview* at its end.
FILM_PAUSE = "ai-film-pause"
FILM_AGAIN = "ai-film-again"
FILM_BOARD = "ai-film-board"
FILM_BEGIN = "ai-film-begin"
FILM_READ = "story-read"
FILM_PAUSE_LABEL = "Pause the story"
FILM_RESUME_LABEL = "Play the story"
FILM_BEGIN_WORDS = "Begin the interview"
#: Spec 159's (keel-web 253's) *Go on to the question* -- gone with keel-web 256 FR-3; never drawn.
FILM_GO_ON_RETIRED = "ai-story-go-on"
#: keel-web 256 FR-4: the replay mark before the question (`AI_REPLAY_LABEL`); *Say it again* (`ai-again`) is gone.
REPLAY = "ai-replay"
REPLAY_LABEL = "Hear the question again"
AGAIN_RETIRED = "ai-again"
#: keel-web 256 FR-7: the last page's green tick and title.
DONE_TICK = "ai-done-tick"
WHAT_IS_KEEL = "What is Keel?"


def ai_done_title(founder: str) -> str:
    """keel-web 256 FR-7 (`aiDoneTitle`): the last page's title, over the tick (the served first name, else the name)."""
    return f"Done. Your answers have gone to {founder}."


#: keel-web 253 FR-4: the kind card's *Try it yourself* on Keel's voice, beside its set-up, where no face is READY.
TRY_KEEL_VOICE = "try-keel-voice"
#: Spec 160 (keel-web 256 FR-2, the founder's hard block for now): the microphone refused, absent or nothing heard --
#: the block (`ai-mic-block`, `AI_MIC_BLOCK` and its how line), no Start, the button stays *Test your mic*. 254's
#: fallback (`ai-mic-fallback`, *You can tap your answers instead*, the taps-only walk) is gone.
MIC_BLOCK_ID = "ai-mic-block"
MIC_FALLBACK_RETIRED = "ai-mic-fallback"
#: Spec 159 FR-3: a box that takes typed words, anywhere on the link's page (keel-web 254: none).
TYPED_BOXES = "textarea, input[type=text]"
LAST_QUESTION = "Last question"
#: keel-web 070's press after an answer, gone with keel-web 072 FR-5: never in the DOM again.
THATS_MY_ANSWER = "That’s my answer"
FINISH = "Finish"
#: keel-web 070 F1 / 072 FR-5: typed words keep an explicit press.
SAVE_AND_NEXT = "Save and next"
# ---- keel-web 072 `translate.ts` (spec 072 FR-7, FR-9)
MIC_TEST = "Test your mic"
#: Spec 170 FR-1 (keel-web 266 FR-2, FR-3): one button, three states -- *Test your mic* (`ai-mic-test`); while it
#: listens the wave (`ai-mic-level`) and *Say anything.* (`ai-mic-say`) in the button's place; once a sound is heard (the
#: level, never the words: the mic passes on sound alone) the tick line *Your mic works.* (`ai-mic-heard`, no words
#: shown back) above **Begin** (`ai-start`). The block (`ai-mic-block`) says one of two lines: nothing heard in 8 s, or
#: the microphone refused or absent. The hello's words are no longer read: the walk's seam still makes a sound
#: (`MIC_SOUND`, said through `__say`), and what it said is never asserted.
BEGIN = "Begin"
SAY_ANYTHING = "Say anything."
MIC_SAY_ID = "ai-mic-say"
MIC_WORKS = "Your mic works."
MIC_NOT_HEARD = "We did not hear you. Check your mic is not muted, then try again."
MIC_BLOCK = "This interview needs your microphone. Allow it for this page in your browser, then try again."
MIC_SOUND = "hello"
#: Spec 170 FR-1: keel-web 256's entry words (*Say hello*, the mic label, *Heard: {words}*, *Start the interview*, the
#: block's two lines). They are read only to say a screen still shows them: a DRIFT capture note (`entry_drift`), never a
#: fault of the walk -- the walk presses the same ids on either screen.
ENTRY_WORDS_BEFORE_266 = ("Say hello, so we know your mic works.", "Say hello", "Heard: ", "Start the interview",
                          "Allow the microphone for this page in your browser, then test your mic again.")
#: keel-web 115 FR-3 (spec 074 FR-1): the intro's line loses its condition -- the page records wherever it can listen.
INTRO_TRANSCRIBED = "Keel's transcription provider writes your answer down and keeps nothing."
GOT_THAT = "Got that…"
WRITING_DOWN = "Writing it down…"
HELD = "Got it. Moving on… say no to change"
#: keel-web 073 FR-3: the status through the quiet gap (`AI_STATUS.heard`), and a tap's or a Save's 500 ms advance
#: (`AI_STATUS.answered`); the heard line's tags (`AI_TAG_HEARING`, `AI_TAG_NOT_TAKEN`).
HEARING = "Listening. Pause when you’re done."
#: keel-web 115 (spec 074 FR-1): the recorded path's status while a question's window records (`AI_STATUS.recording`),
#: the one path now -- nothing is heard before it is written down, so the heard line says *Hearing you…* meanwhile.
RECORDING = "Recording your answer. Pause when you’re done."
ANSWERED = "Got it."
TAG_HEARING = "hearing"
TAG_NOT_TAKEN = "not taken"
#: keel-web 073 FR-2 `QUIET_MS` (`src/lib/answerPath.ts`): the gap after a final before the utterance is read -- 1.5 s
#: at 073, 4.0 s on every window from keel-web 074 (the founder's decision, 2026-10-16), and two gaps from keel-web 082
#: (D36): the option questions (yes/no, number, list, amount or hours, the pilot ask, the confirmations) close after
#: `QUIET_OPTION_MS` 2.0 s, free text (the story, the follow-up, the speak-or-type box) after `QUIET_FREE_MS` 4.0 s.
#: The seam: `quietMs` is the option gap, `quietFreeMs` the free one (absent -> `quietMs`). The walk encodes neither:
#: it waits for the held / unsure status or the next question, with timeouts that tolerate the longest gap here plus
#: the 2.0 s hold (spec 049 judgement call 6). The one fixed wait is IM20's: a tapped tick must not go on by itself.
QUIET_OPTION_MS = 2_000
QUIET_FREE_MS = 4_000
GAP_TOLERATED_MS = max(QUIET_OPTION_MS, QUIET_FREE_MS)
TAP_WAIT_MS = 1_500
IS_THAT_RIGHT = "Is that right? Say yes, or tell me the right one"
YES_THATS_IT = "Yes, that’s it"
#: The words a stranger says for each move (design §3-§4).
#: keel-web 074 FR-2 (`AI_STATUS.story`): the story's window says how to end it -- since keel-web 274 FR-1 (spec 172
#: FR-2, `AI_LONG.status`) a pause no longer ends it; 074's sub is `STORY_BEFORE_274`, no longer read.
STORY = 'Take your time. Say "that\'s it" when you are done, or tap Save.'
STORY_BEFORE_274 = "Take your time. Pause for a few seconds when you’re done, or tap Save."
#: Spec 172 FR-2 (keel-web 274 FR-1 to FR-3, `AI_LONG`): the respondent's long answers -- the story and a follow-up --
#: never close on a pause: after `LONG_WAIT_MS` of quiet the orb turns amber and Keel's one ask stands (`ai-story-ask`,
#: once); a close word heard last closes it (`DONE_WORDS`, stripped from what is sent) and Keel acknowledges it
#: (`ai-story-got-it`, *Got it. Thank you.*; at the two-minute cap *That is two minutes. I have kept every word.*) -- no
#: veto hold, no *say no to change* on the story (`HELD` stays the short answers'). Every passage is captioned
#: (`ai-passage-caption`). The pause the walk's strangers leave inside the story (`STORY_PAUSE_S`): past the page's
#: `PAUSE_MS` (2.5 s, the recording cut there), short of the eight seconds.
LONG_ASK = 'Anything else? Say "that\'s it" when you are done.'
LONG_GOT_IT = "Got it. Thank you."
LONG_CAP = "That is two minutes. I have kept every word."
LONG_ASK_ID = "ai-story-ask"
LONG_GOT_IT_ID = "ai-story-got-it"
PASSAGE_CAPTION = "ai-passage-caption"
NO_WORDS_ID = "ai-no-words"
LONG_WAIT_MS = 8_000
STORY_CAP_MS = 120_000
STORY_PAUSE_S = 4.0
#: The close word the strangers say last (spec 161's *that's it*, keel-web 274 FR-1).
LONG_DONE_WORD = "That's it."


def story_parts(words: str, parts: int = 2) -> list[str]:
    """Spec 172 FR-2: a story as a stranger says it in `parts` -- split at a sentence's end as near the middle as it
    falls (the whole where it is one sentence), the done word after the last part."""
    text = " ".join(str(words or "").split())
    if text and text[-1] not in ".!?,;:":
        text += "."                                  # keel-web's `DONE_AT_END`: the done word after a sentence's end
    if parts < 2:
        return [f"{text} {LONG_DONE_WORD}".strip()]
    cuts = [m.end() for m in re.finditer(r"[.!?](?=\s)", text)]
    if not cuts:
        return [f"{text} {LONG_DONE_WORD}".strip()]
    cut = min(cuts, key=lambda c: abs(c - len(text) / 2))
    return [text[:cut].strip(), f"{text[cut:].strip()} {LONG_DONE_WORD}"]
#: keel-web 075 FR-1: the beat after the PROBLEM and SOLUTION passage clips (`BEAT_MS`, `AI_STATUS.beat`, the pill's
#: `AI_STATE.beat`); the seam's `beatMs` is left at the page's default on the stack (spec 050 judgement call 3).
BEAT = "Take a moment."
BEAT_PILL = "pause"
BEAT_MS = 2_000
#: keel-web 075 FR-4 (`AI_STATUS.micOff`): the end screens once every holder of the microphone has let go.
MIC_OFF = "Microphone off"
VETO = "no"
SAY_YES = "yes"
GO_BACK = "go back"
#: keel-web 076 `translate.ts` (spec 051): the follow-up and the speak-or-type box, restated where the walks read them.
#: keel-web 126 FR-5 (spec 075 FR-5): the one kicker, on the spot and at the end -- the AI sheet's kicker and header
#: where-word, the text link's kicker (124's *About that* and 076's *One last thing* are gone).
FOLLOW_UP_KICKER = "One more thing"
#: keel-web 124 (keel-cloud 142, `MAX_FOLLOW_UPS`): at most two follow-ups an interview, a skipped one counted.
MAX_FOLLOW_UPS = 2
FOLLOW_UP_NOTE = "In your own words. A sentence or two is plenty."
FOLLOW_UP_SKIP = "Skip this one"
FOLLOW_UP_HINT = "The only extra question."
SPEAK_HINT_STORY = "A few lines is plenty."
SPEAK_OR_TYPE_PLACEHOLDER = "Type here, or tap the mic and just talk."
SPEAK_TYPE_PLACEHOLDER = "Type here."
SPEAK_LABEL = "Speak"
SPEAK_ADD_MORE = "Add more"
SPEAK_LISTENING = "Listening. Take your time."
SPEAK_LISTENING_NOTE = "Pause for a few seconds when you’re done, or tap Done."
SPEAK_HEARD = "Heard you. Fix anything that’s wrong."
#: keel-web 082 FR-3 (D35, `HEARING_YOU`): the recorded path's status once a sound came in -- the AI sheet's heard line
#: (`ai-heard`) and the box's listening card (`iv-mic-say`); *Nothing heard yet* only while nothing has.
HEARING_YOU = "Hearing you…"
#: keel-web 143 (spec 099 FR-1): the AI sheet's heard line (`ai-heard`) carries its state, `data-heard` --
#: `listening` (*Listening…*, `AI_HEARD_LISTENING`: a window open, nothing heard), `hearing` (*Hearing you…*), `writing`
#: (*Writing down what you said…*, `AI_HEARD_WRITING_DOWN`: from the send to the transcript), `words` (the tag and the
#: words), `nothing` (*Heard so far: nothing yet*, `AI_HEARD_NOTHING`: only after an empty transcript). The status
#: line's `WRITING_DOWN` (*Writing it down…*, `AI_WRITING_DOWN`) is another string and unchanged. *Test your mic*'s
#: writing line (`ai-mic-writing-line`) says the same `AI_HEARD_WRITING_DOWN`.
HEARD_LISTENING = "Listening…"
HEARD_WRITING_DOWN = "Writing down what you said…"
HEARD_NOTHING = "Heard so far: nothing yet"
HEARD_STATES = ("listening", "hearing", "writing", "words", "nothing")
SPEAK_MIC_OFF = "The microphone is off, so it’s typing on this one."
#: keel-web 126 FR-4 (spec 075 FR-5): the box's `asking` state while the microphone is asked for (`SPEAK_ASKING`, the
#: card `iv-mic-asking`: the line and *Cancel*, no waveform, no clock), before *listening*.
SPEAK_ASKING = "Allow the microphone…"
#: keel-web 126 FR-3: a free window's (the story's, the follow-up's) empty transcript -- the red line
#: (`AI_REASON_DIDNT_CATCH`) and the second miss's status (`AI_SECOND_MISS_FREE`). Read by no walk; the dry run's
#: story is held to be none of them.
AI_REASON_DIDNT_CATCH = "I didn't catch that. Say it again."      # keel-web 254: nothing typed
AI_SECOND_MISS_FREE = "Say it again."
#: keel-web 072's closed-question miss (`AI_REASON_NO_MATCH`): what the dry run's story read before keel-web 126 FR-2
#: (an empty transcript taken for a miss, though a story has no options).
AI_REASON_NO_MATCH = "That didn't match an option. Say it again, or tap one."
#: keel-web 076: the box's two caps as the clock says them (`clockOf(capMs)`): the story's minute, the follow-up's two.
STORY_CAP = "1:00"
FOLLOW_UP_CAP = "2:00"
#: keel-web `answerPath.ts`: the recorded path's quiet after the last sound -- 4.0 s on every window from 074, by window
#: kind from 082 (D36: `SILENCE_OPTION_MS` 2.0 s, `SILENCE_FREE_MS` 4.0 s; the seam's `silenceMs` overrides both) --
#: and the follow-up's cap (`FOLLOW_UP_RECORD_CAP_MS`, two minutes) -- held to the source by a unit test. The walks
#: measure only free-text windows on the recorded path (the story's box, the follow-up), so they read the free one.
SILENCE_OPTION_MS = 2_000
SILENCE_FREE_MS = 4_000
FOLLOW_UP_RECORD_CAP_MS = 120_000
#: Spec 051 judgement call 2: the AI follow-up's silent window is shortened through the seam (`followUpCapMs`); the
#: real two minutes are held on the wire (`maxSeconds: 120`) and in keel-web's source.
FOLLOW_UP_SEAM_CAP_MS = 9_000
#: A level the recorder hears as a sound (`LEVEL_THRESHOLD` is 0.02) and how long the walk speaks for.
SOUND = 0.3
SPEAK_MS = 1_200


def entry_drift(*screens: dict | None) -> list[str]:
    """Spec 170 FR-1: what of keel-web 256's entry screen is still drawn on the intros read (`Player.intro`): its words
    (`ENTRY_WORDS_BEFORE_266`) and its ids (`ENTRY_IDS_BEFORE_266`) -- [] on keel-web 266's screen. A DRIFT capture note,
    never a fault of the walk."""
    found: list[str] = []
    for screen in screens:
        text = " ".join(str((screen or {}).get("text") or "").split())
        for words in ENTRY_WORDS_BEFORE_266:
            if words in text and words not in found and not any(words in f for f in found):
                found.append(words)
        for testid in (screen or {}).get("retired") or []:
            if testid not in found:
                found.append(testid)
    return found


def back_to(question: int) -> str:
    return f"‹ Back to question {question}"

#: Spec 046 FM5: the stage's timeline, kept by the page itself from before the app runs -- every `data-phase` the stage
#: takes (`performance.now()`), every `play` of a clip on the stage's `<video>`, and every press of `ai-next` with the
#: words it carried (spec 074: and every clip's `ended`). `window.__keelFlow()` hands it back. Spec 048 (keel-web 072): every change of the sheet's status
#: words (`ai-status`) in order, `window.__keelPhases()`; every press of a button on the sheet with its words; and
#: whether *That's my answer* (`ai-answer`) was ever in the DOM, `window.__keelSawAnswer()`. Spec 099 (keel-web 143):
#: every change of the sheet's heard line (`ai-heard`: its `data-heard` state and words, under its question),
#: `window.__keelHeard()` -- the line sampled through the send as the status is.
FLOW_TIMELINE = r"""
(() => {
  const events = [];
  const statuses = [];
  const heards = [];
  let heardKey;
  let phase = null;
  let status = null;
  let sawAnswer = false;
  const beats = [];
  let beat = null;
  let lastClip = null;
  const read = () => {
    const stage = document.querySelector('[data-testid=ai-stage]');
    const now = stage ? stage.getAttribute('data-phase') : null;
    if (now !== phase) {
      const t = performance.now();
      if (beat && phase === 'beat') { beat.t1 = t; beat.next = now; beat = null; }
      phase = now; events.push({ t, kind: 'phase', value: now });
      if (now === 'beat') {
        beat = { t0: t, t1: null, next: null, after: lastClip, statuses: [], pills: [], micOn: false,
                 question: false, options: false, buttons: [] };
        beats.push(beat);
      }
    }
    const line = document.querySelector('[data-testid=ai-status]');
    const words = line ? (line.textContent || '').trim() : null;
    if (beat) {
      // spec 050 (keel-web 075 FR-1): what the beat drew, every time the page changed while it lasted
      const pill = document.querySelector('[data-testid=ai-state]');
      const pillWords = pill ? (pill.textContent || '').trim() : null;
      if (words !== null && beat.statuses[beat.statuses.length - 1] !== words) beat.statuses.push(words);
      if (pillWords !== null && beat.pills[beat.pills.length - 1] !== pillWords) beat.pills.push(pillWords);
      if (document.querySelector('[data-testid=ai-mic-on]')) beat.micOn = true;
      if (document.querySelector('[data-testid=ai-sheet] .iv-q')) beat.question = true;
      if (document.querySelector('[data-testid=ai-options]')) beat.options = true;
      for (const b of document.querySelectorAll('[data-testid=ai-sheet] button')) {
        const id = b.getAttribute('data-testid') || (b.textContent || '').trim();
        if (!beat.buttons.includes(id)) beat.buttons.push(id);
      }
    }
    if (words && words !== status) {
      status = words;
      const q = document.querySelector('[data-testid=ai-sheet] .iv-q');
      statuses.push({ t: performance.now(), status: words, question: q ? (q.textContent || '').trim() : null });
    }
    // spec 099 (keel-web 143): every change of the heard line -- its state (`data-heard`, null when it is not drawn)
    // and its words -- with the question it stood under, so the marks can read each recorded window's states
    const heard = document.querySelector('[data-testid=ai-sheet] [data-testid=ai-heard]');
    const heardState = heard ? heard.getAttribute('data-heard') : null;
    const heardWords = heard ? (heard.textContent || '').replace(/\s+/g, ' ').trim() : null;
    const key = JSON.stringify([heardState, heardWords]);
    if (key !== heardKey) {
      heardKey = key;
      const q = document.querySelector('[data-testid=ai-sheet] .iv-q');
      heards.push({ t: performance.now(), state: heardState, words: heardWords,
                    question: q ? (q.textContent || '').trim() : null });
    }
    if (!sawAnswer && document.querySelector('[data-testid=ai-answer]')) sawAnswer = true;
  };
  new MutationObserver(read).observe(document, { subtree: true, childList: true, attributes: true,
                                                 characterData: true });
  document.addEventListener('play', (e) => {
    const v = e.target;
    if (v && v.tagName === 'VIDEO') {
      lastClip = v.getAttribute('data-clip');
      events.push({ t: performance.now(), kind: 'play', clip: lastClip });
    }
  }, true);
  // spec 074 (keel-web 116 FR-1): a clip's end too -- the thank-you's end is when the microphone is let go
  document.addEventListener('ended', (e) => {
    const v = e.target;
    if (v && v.tagName === 'VIDEO') events.push({ t: performance.now(), kind: 'ended', clip: v.getAttribute('data-clip') });
  }, true);
  document.addEventListener('click', (e) => {
    const b = e.target && e.target.closest ? e.target.closest('[data-testid=ai-next]') : null;
    if (b) events.push({ t: performance.now(), kind: 'next', value: (b.textContent || '').trim() });
    const any = e.target && e.target.closest ? e.target.closest('[data-testid=ai-sheet] button, [data-testid=ai-sheet] .opt') : null;
    if (any) events.push({ t: performance.now(), kind: 'press', testid: any.getAttribute('data-testid'),
                           value: (any.textContent || '').trim() });
  }, true);
  window.__keelFlow = () => events.slice();
  window.__keelPhases = () => statuses.slice();
  window.__keelHeard = () => heards.slice();
  window.__keelSawAnswer = () => sawAnswer;
  window.__keelBeats = () => beats.map((b) => Object.assign({}, b));
})();
"""


def persona_asks(face: str) -> str:
    return f"{face} asks your questions."


def persona_progress(done: int, total: int) -> str:
    return f"{done} of {total} clips done"


def change_who_asks(credits: int) -> str:
    return f"Change who asks · {credits:,} AI credits"


def pick_who_asks(credits: int) -> str:
    return f"Record the interviewer · {credits:,} AI credits"


def walkthrough_asks_title(face: str) -> str:
    return f"{face} asks your questions"


def ai_intro_heading(founder: str, questions: int) -> str:
    """keel-web 256 FR-1 `aiIntroHeadline` (it was 109's `aiIntroHeading`, *{face} will ask you N questions.*): the
    headline names the founder (the served first name, else the name -- `intro_founder`) and the count (keel-cloud 133
    FR-9: *1 question* for one)."""
    return f"{founder} has {questions} question{'' if questions == 1 else 's'} for you."


def intro_founder(interview: dict) -> str:
    """keel-web 256 judgement call 3: the founder the intro's headline and the last page's title name -- the served
    `founderFirstName`, else `founderName`."""
    return str(interview.get("founderFirstName") or "").strip() or str(interview.get("founderName") or "").strip()


#: Spec 074 FR-1 (keel-web 115 FR-5, one recorded path): keel-web `tests/fixtures/interviewer/fakeSpeech.ts`
#: `installFakeSpeech`, restated in JavaScript -- **the fake recorder and the always-granted fake microphone**; the
#: browser's recogniser, its fake (`Recognition`, `__speechError`, `__speechEnd`, `__recognisers`, `__speechStarts`) and
#: the `not-allowed` leg are gone with it. **`__say(text, final = true)`** is *the person said `text` in this window*: the
#: recorder's level pulses above the threshold for `SAY_TICKS` ticks (ten a second, as the real one) and falls silent, so
#: the page stops the window as it would (two seconds after the last sound, four on free text); the next `stop()` hands
#: back the UTF-8 bytes of what was said **followed by zero bytes up to 20 KiB**, base64, as `audio/webm` -- past the
#: answer route's silence threshold (keel-cloud 099) -- and keel-cloud 136 FR-2's `FakeTranscriber` trims the padding and
#: hears the words, so they reach the stack's FakeClassifier through the real `POST .../interview/answer` (or
#: `transcribe`) as the page sends them. `final = false` keeps the level up and the words provisional. A window in which
#: nothing was said (a level set through `__level`, the walk's "sound") hands back the zeros alone, which the fake hears
#: as its `otherwise`, `FAKE_TRANSCRIPT` on this stack. `__listening()` is *the recorder runs on this window*.
#:
#: The harness's own additions, as before: **no `classify` or `answer` stand-in** (spec 048 judgement call 1: the page
#: calls the real routes), `earcons: false` (073 FR-8), the page's own quiet and beat (no `quietMs`, `beatMs`); every
#: start, stop and cancel stamped (`performance.now()`) on `__recordStarts` / `__recordStops` / `__recordCancels`, every
#: level set on `__levels`, the last loud tick on `__soundAt`, every release of the microphone counted on
#: `__micReleased` and stamped on `__micReleasedAt` (keel-web 116: the release follows the thank-you's end) -- so the leg
#: can say nothing recorded in a beat or after the thanks.
_RECORDER = r"""
  const stamps = (name) => (window[name] = window[name] || []);
  const SAY_TICKS = 3;
  const SOUND = 0.3;
  const THRESHOLD = 0.02;
  const PADDED_BYTES = 20 * 1024;
  window.__levelNow = 0;
  let ticker; let held = false; let waiting = null; let recording = false;
  let said = []; let speaking = ''; let pulse = 0;
  const forget = () => { said = []; speaking = ''; pulse = 0; };
  const encode = (text) => {
    const words = new TextEncoder().encode(text);
    const bytes = new Uint8Array(Math.max(PADDED_BYTES, words.length));
    bytes.set(words);
    let binary = '';
    for (let i = 0; i < bytes.length; i += 0x8000) binary += String.fromCharCode(...bytes.subarray(i, i + 0x8000));
    return btoa(binary);
  };
  const recorder = {
    start: async (onLevel) => {
      stamps('__recordStarts').push(performance.now());
      clearInterval(ticker);
      recording = true;
      ticker = setInterval(() => {
        let level = window.__levelNow;
        if (pulse > 0) { pulse -= 1; level = SOUND; } else if (speaking) level = SOUND;
        if (level > THRESHOLD) window.__soundAt = performance.now();
        if (onLevel) onLevel(level);
      }, 100);
      return true;
    },
    stop: async () => {
      clearInterval(ticker);
      recording = false;
      stamps('__recordStops').push(performance.now());
      const text = [...said, speaking].filter(Boolean).join(' ');
      forget();
      if (held) await new Promise((resolve) => { waiting = resolve; });
      return { audio: encode(text), mimeType: 'audio/webm' };
    },
    cancel: () => {
      clearInterval(ticker);
      recording = false;
      stamps('__recordCancels').push(performance.now());
      forget();
    },
  };
  window.__say = (text, final = true) => {
    if (final) { said.push(text); speaking = ''; pulse = SAY_TICKS; } else speaking = text;
    stamps('__said').push([performance.now(), text, !!final]);
    return true;
  };
  window.__listening = () => recording;
  window.__level = (rms) => { window.__levelNow = rms; stamps('__levels').push([performance.now(), rms]); };
  window.__holdStop = () => { held = true; };
  window.__releaseStop = () => { held = false; if (waiting) { const w = waiting; waiting = null; w(); } };
  window.__micAcquired = 0; window.__micReleased = 0;
  const mic = (level, refused) => ({
    acquire: async () => { window.__micAcquired += 1; stamps('__micAcquiredAt').push(performance.now());
                           // keel-web 126 FR-4 (`installHeldMic`): the permission sheet still up -- the box stays
                           // *asking* until `__grantMic()`
                           if (window.__micHeld) await new Promise((resolve) => (window.__grantMic = resolve));
                           // spec 160 FR-2: `__micRefused` refuses it until the walk allows it (`Player.allow_mic`)
                           return !refused && !window.__micRefused; },
    level,
    release: () => { window.__micReleased += 1; stamps('__micReleasedAt').push(performance.now()); },
  });
"""

#: The AI page's seam: the recorder above, the microphone always granted with keel-web's steady level (0.12, the
#: waveform's bucket 2), the earcons off. Nothing else: the page's quiet, beat and caps are its own.
SPEECH_SEAM = "(() => {" + _RECORDER + """
  window.__keelSpeech = { recorder, mic: mic(() => 0.12, false), earcons: false };
})();
"""


def speech_seam(*, refused: bool = False) -> str:
    """`SPEECH_SEAM`, or (spec 159 FR-3, `refused`) the same recorder with the microphone **refused** -- the harness's
    refusal hook on the AI page. Spec 160 FR-2 (keel-web 256 FR-2): *Test your mic* then ends at the block (no Start);
    the refusal is `window.__micRefused` (keel-web's own fixture's name, `installRefusedMic`), so the walk can allow the
    microphone again (`Player.allow_mic`) and test once more."""
    if not refused:
        return SPEECH_SEAM
    return "(() => { window.__micRefused = true;" + _RECORDER + """
  window.__keelSpeech = { recorder, mic: mic(() => 0.12, false), earcons: false };
})();
"""


def text_seam(*, refused: bool = False, held: bool = False) -> str:
    """The text page's seam (keel-web 076, 115 FR-4: the box has one ear, the recorder): the same recorder, the
    microphone counted (`__micAcquired`, 0 until the pill is tapped) and refused when `refused` (T6), its level what the
    walk sets (`__level`). The quiet and the caps are left at the page's defaults (4 s free text, 60 s, 120 s). The box
    is driven by a level, not by words, so its recording is the zeros alone: the stack's fake hears `FAKE_TRANSCRIPT`.
    `held` (spec 075 FR-5, keel-web 126 FR-4's `installHeldMic`): the first acquire waits on the permission sheet until
    the walk calls `__grantMic()` (`SpeakBox.grant`), so the box's *asking* state can be read."""
    return ("(() => {" + (" window.__micHeld = true;" if held else "") + _RECORDER + """
  window.__keelSpeech = { recorder, mic: mic(() => window.__levelNow, %s), earcons: false };
})();
""" % ("true" if refused else "false"))


def follow_up_cap_seam(follow_up_cap_ms: int) -> str:
    """Spec 051 judgement call 2: the AI follow-up's silent window shortened through the seam (`followUpCapMs`; the
    wire's `maxSeconds` stays 120), installed after `SPEECH_SEAM`. Spec 074: the recorder is the seam's own since
    keel-web 115, so this adds the cap alone (it was `recorder_seam`, which added the recorder a refusing recogniser
    fell back to)."""
    return f"(() => {{ window.__keelSpeech.followUpCapMs = {int(follow_up_cap_ms)}; }})();\n"


def _audio_bytes(audio_b64: str | None) -> int:
    import base64                                                             # noqa: PLC0415

    try:
        return len(base64.b64decode(audio_b64 or ""))
    except Exception:  # noqa: BLE001 - not base64
        return 0


def decode_said(audio_b64: str | None) -> str:
    """What a recording the seam made carried: the said words, the zero padding trimmed -- keel-cloud 136 FR-2's
    `FakeTranscriber.text` rule and keel-web 115's `decodeSaid` -- or "" for none."""
    import base64                                                             # noqa: PLC0415

    if not audio_b64:
        return ""
    try:
        raw = base64.b64decode(audio_b64)
    except Exception:  # noqa: BLE001 - not base64: heard as nothing
        return ""
    return raw.rstrip(b"\x00").decode("utf-8", errors="replace")


def _json(response) -> dict:
    try:
        body = response.json()
    except Exception:  # noqa: BLE001 - an empty or non-JSON body
        return {"status": response.status}
    return body if isinstance(body, dict) else {"status": response.status, "body": body}


def _words(locator) -> str:
    """The locator's words, or "" -- read once, at most two seconds: a line the page takes away between the count and
    the read (the heard line as the hold ends) is read as gone, never waited for thirty."""
    try:
        return " ".join((locator.text_content(timeout=2_000) or "").split()) if locator.count() else ""
    except Exception:  # noqa: BLE001 - gone between the count and the read
        return ""


# ------------------------------------------------------------------------------------- tap to hear (087)

#: keel-web 087's test ids: the play glyph on an unpicked card, the intro's *Hear <name>*; keel-web 088's twin on the
#: who-asks band (`persona-hear`, *Hear Daphne · 5 s*).
FACE_HEAR = "face-hear"
INTRO_HEAR = "intro-hear"
PERSONA_HEAR = "persona-hear"
#: keel-web 087 FR-5 `introHear(name, seconds)`: the intro's button starts *Hear <name>* (its seconds after a dot).
HEAR_PREFIX = "Hear "

#: Installed once a page: every `video`'s play / playing / pause / ended / error, heard on the document in the capture
#: phase, with the card (`data-face`) or the intro it plays in, `muted`, the clock, the duration and the source; and
#: `poll(selectors)` -- every 100 ms, whether each selector's element is there and enabled -- until `stop()`.
HEAR_JS = r"""() => {
  if (!window.__keelHear) {
    const log = {events: [], polls: [], timer: null};
    const snap = (v, type) => {
      const card = v.closest('[data-face]');
      log.events.push({type, t: performance.now(), face: card ? card.getAttribute('data-face') : null,
                       intro: !!v.closest('[data-testid=ai-intro]'), band: !!v.closest('[data-testid=persona-line]'),
                       hearing: (v.closest('[data-testid=persona-line]') || {getAttribute: () => null})
                                  .getAttribute('data-hearing'), muted: v.muted, paused: v.paused,
                       currentTime: v.currentTime, duration: Number.isFinite(v.duration) ? v.duration : null,
                       src: v.currentSrc || v.src || '', error: v.error ? v.error.code : null});
    };
    for (const type of ['play', 'playing', 'pause', 'ended', 'error']) {
      document.addEventListener(type, (e) => { if (e.target instanceof HTMLVideoElement) snap(e.target, type); }, true);
    }
    log.reset = () => { log.events = []; log.polls = []; };
    log.poll = (selectors) => {
      log.stop();
      log.timer = setInterval(() => {
        log.polls.push({t: performance.now(), enabled: selectors.map((sel) => {
          const el = document.querySelector(sel);
          return el ? !el.disabled : null; })});
      }, 100);
    };
    log.stop = () => { if (log.timer) clearInterval(log.timer); log.timer = null; };
    log.read = () => ({events: log.events.slice(), polls: log.polls.slice(), now: performance.now()});
    window.__keelHear = log;
  }
  window.__keelHear.reset();
  return true;
}"""

#: Whether a container shows a `video` (laid out) and its still (`role=img`, laid out) -- the clip in place of the still.
_SHOWING_JS = r"""(el) => {
  const shown = (x) => { if (!x) return false; const r = x.getBoundingClientRect(); const cs = getComputedStyle(x);
    return r.width > 0 && r.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none' && cs.opacity !== '0'; };
  const videos = Array.from(el.querySelectorAll('video'));
  return {video: videos.some(shown), videos: videos.length, still: Array.from(el.querySelectorAll('[role=img]')).some(shown)};
}"""

#: The ended (or an error) of a clip in `where` -- a card's code, "intro", or "band" (088's who-asks band).
_ENDED_JS = r"""(where) => (window.__keelHear ? window.__keelHear.events : []).some((e) =>
  (e.type === 'ended' || e.type === 'error') && (where === 'intro' ? e.intro : where === 'band' ? e.band
                                                  : e.face === where))"""


def _showing(locator) -> dict:
    return locator.evaluate(_SHOWING_JS) if locator.count() else {"video": False, "videos": 0, "still": False}


def _heard(page: Page, where: str, start, *, wait_s: float, polls: list[str] | None = None) -> dict:
    """Tap (`start()`), then wait for the clip in `where` to end and the still to return; what the listener heard."""
    page.evaluate(HEAR_JS)
    if polls:
        page.evaluate("(sels) => window.__keelHear.poll(sels)", polls)
    t0 = page.evaluate("() => performance.now()")
    start()
    ended = True
    try:
        page.wait_for_function(_ENDED_JS, arg=where, timeout=wait_s * 1000)
    except Exception:  # noqa: BLE001 - a clip that never ends is the mark's to fail, not the walk's
        ended = False
    page.evaluate("() => window.__keelHear.stop()")
    log = page.evaluate("() => window.__keelHear.read()")
    for e in log["events"]:
        e["ms"] = round(e.pop("t") - t0)
    return {"ended": ended, "events": log["events"],
            "polls": [p["enabled"] for p in log["polls"]], "elapsed_ms": round(log["now"] - t0)}


def _still_back(container, *, wait_s: float) -> dict:
    """The container's still back and no clip showing, waited for up to `wait_s` after the end."""
    deadline = wait_s * 1000
    waited = 0
    shown = _showing(container)
    while (shown["video"] or not shown["still"]) and waited < deadline:
        container.page.wait_for_timeout(100)
        waited += 100
        shown = _showing(container)
    return {**shown, "waited_ms": waited}


def hear_card(page: Page, scope, face: str, *, wait_s: float) -> dict:
    """keel-web 087 FR-2: a tap on `face`'s card in the carousel under `scope` -- what the card was (picked, its glyph,
    its still), what played inside it and in any other card, and the card after the clip's end (picked, the still
    back, no clip showing). Every unpicked card's glyph is counted too."""
    carousel = scope.get_by_test_id("face-carousel") if scope.get_by_test_id("face-carousel").count() else scope
    card = carousel.locator(f'[data-face="{face}"]')
    card.wait_for(state="visible", timeout=10_000)
    cards = carousel.locator('button[role="radio"]')
    before = {"picked": card.get_attribute("aria-checked") == "true",
              "glyph": card.get_by_test_id(FACE_HEAR).count() > 0, **_showing(card),
              "glyphs": {c.get_attribute("data-face"): c.get_by_test_id(FACE_HEAR).count() > 0
                         for c in cards.all() if c.get_attribute("aria-checked") != "true"}}
    heard = _heard(page, face, card.click, wait_s=wait_s)
    after = {"picked": card.get_attribute("aria-checked") == "true", **_still_back(card, wait_s=5)}
    return {"face": face, "before": before, **heard, "after": after,
            "checked": [c.get_attribute("data-face") for c in cards.all() if c.get_attribute("aria-checked") == "true"]}


# --------------------------------------------------------------------------------------------- the founder

class Persona:
    def __init__(self, page: Page, recorder, base_url: str, *, patience: float = 1.0, guide: dict | None = None):
        self.page = page
        self.base = base_url.rstrip("/")
        self.patience = patience
        self._b = _BrowserStep(recorder, page, "founder")
        self.recorder = recorder
        #: Spec 059: the journey's guide record, where the Sent-open helper keeps each pass of 088's sheet.
        self.guide = guide

    def sent(self, project_id: str) -> None:
        """Sent, opened when not already on it, with keel-web 088's first-open sheet passed by (spec 059 FR-4)."""
        if not self.page.url.split("?")[0].endswith(f"/p/{project_id}/interviews/sent"):
            self.page.goto(f"{self.base}/p/{project_id}/interviews/sent", wait_until="load")
        self.page.locator(".sent__kinds").wait_for(state="visible", timeout=60_000 * self.patience)
        _iv.pass_interviews_sheet(self.page, self.recorder, self.base, guide=self.guide)

    # spec 154 (keel-web 187 FR-5): `line`, `wait_state`, `record` (the persona line and its popup), `formats_now` (Send
    # more's rows), `hear_band` (the band's Hear) and `l1_again` (L1's carousel) are gone with their doors; the kind card
    # is `card`, `wait_card_state`, `set_up`; New link's rows are `interviews_screens.Interviews.formats_for`.
    KIND_TRY_AGAIN = "kind-try-again"

    def cards(self) -> list[dict]:
        """Each kind's card: its label, *Try it yourself* (enabled or not, its words) and the primary's words."""
        out = []
        for card in self.page.locator(".sent__kinds .role").all():
            tryit = card.get_by_test_id("try-it-yourself")
            out.append({"label": _words(card.locator(".role__label").first),
                        "try": {"text": _words(tryit), "enabled": tryit.is_enabled()} if tryit.count() else None,
                        "primary": _words(card.locator(".btn.primary").first)})
        return out

    def how_it_works(self) -> int:
        """Spec 059: the controls on Sent named *How it works* -- keel-web 088 removed the replay of W1 (none)."""
        return self.page.get_by_role("button", name=HOW_IT_WORKS, exact=True).count() + \
            self.page.get_by_role("link", name=HOW_IT_WORKS, exact=True).count()

    def card(self, kind_label: str) -> dict:
        """The kind card as drawn (`kind-card[data-role][data-interviewer]`): its label, role id, the interviewer state the
        card reads (NOT_SET_UP / RECORDING / READY / FAILED / OWN_AI), the line's tail (`kind-asks`: *Daphne asks* /
        *Daphne is recording*), the primary button (its testid, words, enabled), the progress bar and its words
        (`kind-progress`), the failure line, and *Read their questions*."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(kind_label)}$"))).first
        card.wait_for(state="visible", timeout=20_000)
        primary = card.locator(".btn.primary").first
        bar = card.locator("[data-testid=kind-progress] [role=progressbar]")
        progress = card.locator("[data-testid=kind-progress]")
        return {"label": _words(card.locator(".role__label").first), "role_id": card.get_attribute("data-role"),
                "state": card.get_attribute("data-interviewer"),
                # keel-web 187 (`SentPage`): the span carries its own separator, *· {Face} asks* -- read without it
                "asks": re.sub(r"^·\s*", "", _words(card.get_by_test_id("kind-asks")) or "") or None,
                "primary": {"id": primary.get_attribute("data-testid"), "text": _words(primary),
                            "enabled": primary.is_enabled()} if primary.count() else None,
                "progress": {"now": bar.get_attribute("aria-valuenow"), "max": bar.get_attribute("aria-valuemax"),
                             "label": bar.get_attribute("aria-label"), "words": _words(progress.locator(".hint"))}
                if bar.count() else None,
                "failure": _words(card.get_by_test_id("kind-failure")) or None,
                "count": _words(card.get_by_test_id("role-count")), "text": _words(card)}

    def wait_card_state(self, kind_label: str, *states: str, timeout_s: float = 45) -> dict:
        """The kind's card reaching one of `states` (keel-web polls `GET interviewer` while a kind records)."""
        role_id = self.card(kind_label)["role_id"]
        selector = ", ".join(f'[data-testid=kind-card][data-role="{role_id}"][data-interviewer="{s}"]' for s in states)
        self.page.locator(selector).first.wait_for(state="attached", timeout=timeout_s * 1000 * self.patience)
        return self.card(kind_label)

    def set_up(self, kind_label: str, face: str, *, expect_status: int | None = None,
               hear_s: float | None = None) -> dict:
        """Spec 154 FR-3 (keel-web 187 FR-6; keel-cloud 247 FR-3): *Set up the AI interviewer* on the kind's card -> the
        face step (`set-up-interviewer-popup`: kicker, title, the carousel, the cost box with `data-paid`) -> the face
        tapped (`hear_s`: the tap heard, as 058's) -> *Record {Face} · 1,500 credits* (`set-up-record`) -> `POST
        interviewer/kinds/{roleId}/record {face}`: what the popup drew, what keel-web sent and received; on a refusal
        the popup's words (it stays open; *Not now* closes it)."""
        with self._b.step(f"founder sets up the AI interviewer for {kind_label} -- {face.title()} -- from the kind's "
                          "card") as h:
            card = self.card(kind_label)
            button = self.page.locator(f'[data-testid=kind-card][data-role="{card["role_id"]}"] '
                                       '[data-testid=set-up-interviewer]').first
            words_before = _words(button)
            button.click()
            popup = self.page.get_by_test_id("set-up-interviewer-popup")
            popup.wait_for(state="visible", timeout=10_000)
            cost = popup.get_by_test_id("set-up-cost")
            drawn = {"kicker": _words(popup.locator(".pop__kicker")), "title": _words(popup.get_by_test_id("set-up-title")),
                     "faces": [b.get_attribute("data-face") for b in popup.locator('button[role="radio"]').all()],
                     "checked": [b.get_attribute("data-face") for b in
                                 popup.locator('button[role="radio"][aria-checked="true"]').all()],
                     "cost": _words(cost) if cost.count() else None,
                     "paid": cost.first.get_attribute("data-paid") if cost.count() else None,
                     "role_id": popup.get_attribute("data-role"), "button_before": words_before}
            heard = None
            if hear_s is None:
                popup.locator(f'[data-face="{face}"]').click()
            else:
                heard = hear_card(self.page, popup, face, wait_s=hear_s)
                h.add_screenshot(self._b.screenshot(f"heard-{face.lower()}"))
            confirm = popup.get_by_test_id("set-up-record")
            drawn["confirm"] = _words(confirm)
            drawn["not_now"] = _words(popup.get_by_test_id("set-up-not-now"))
            route = f"/interviewer/kinds/{card['role_id']}/record"
            with self.page.expect_response(lambda r: r.request.method == "POST" and r.url.endswith(route),
                                           timeout=30_000) as posted:
                confirm.click()
            out = {"popup": drawn, "sent": posted.value.request.post_data_json, "status": posted.value.status,
                   "body": _json(posted.value), "route": route, "role_id": card["role_id"]}
            if heard is not None:
                out["hear"] = heard
            if posted.value.status >= 400:
                refusal = self.page.locator(".remedy, [role=alert], .banner, [data-testid=credits-refusal], .pop h2")
                refusal.first.wait_for(state="visible", timeout=10_000)
                out["refusal"] = _words(refusal.first)
                out["popup_text"] = _words(popup)
                h.add_screenshot(self._b.screenshot("set-up-refused"))
                close = self.page.get_by_role("button", name="Close", exact=True)
                if close.count():
                    close.first.click()
                popup.get_by_test_id("set-up-not-now").click()
            else:
                popup.wait_for(state="hidden", timeout=10_000)
            h.add_screenshot(self._b.screenshot(f"set-up-{face.lower()}"))
            return out

    def try_it(self, project_id: str, role_label: str) -> None:
        """*Try it yourself* on the kind's card: the dry run's route."""
        card = self.page.locator(".sent__kinds .role",
                                 has=self.page.locator(".role__label", has_text=re.compile(
                                     rf"^{re.escape(role_label)}$"))).first
        card.get_by_test_id("try-it-yourself").click()
        self.page.wait_for_url(re.compile(rf"/p/{project_id}/interviews/try/"), timeout=20_000)


# --------------------------------------------------------------------------------------------- the player

#: Spec 160 (keel-web 256 FR-3): the respondent's film read in one evaluate -- see `Player.film`.
FILM_JS = r"""() => {
  const story = document.querySelector('[data-testid=ai-story]');
  if (!story) return { drawn: false };
  const t = (el) => (el ? (el.textContent || '').replace(/\s+/g, ' ').trim() : null);
  const player = story.querySelector('[data-testid=story-player], [data-testid=idea-story-player]');
  const board = story.querySelector('[data-testid=story-board]');
  // spec 162 (keel-web 261's eval mirrors): a film in pictures plays on `story-stage` in the board's place, its caption
  // (`story-line`) inside the stage, one <img> a scene (the shown one `data-on`)
  const stage = story.querySelector('[data-testid=story-stage]');
  // spec 167 FR-2 (keel-web 263 FR-3): above 720 px a portrait film's frame (`story-film`) is a grid and the caption and
  // the pill are drawn in the words' column beside the stage (`story-side-line`, `story-side-chapter`; the stage's own
  // not drawn); on a phone, and around a landscape film, `display: contents` and the stage's own are drawn
  const film = story.querySelector('[data-testid=story-film]');
  const display = film ? getComputedStyle(film).display : null;
  const column = display === 'grid' && !!stage && !stage.hasAttribute('data-ask');
  const capEl = column ? film.querySelector('[data-testid=story-side-line]')
    : (stage ? stage.querySelector('[data-testid=story-line]') : null);
  const chapEl = column ? film.querySelector('[data-testid=story-side-chapter]')
    : story.querySelector('[data-testid=story-chapter]');
  const pause = story.querySelector('[data-testid=ai-film-pause]');
  const tap = story.querySelector('[data-testid=ai-film-board]');
  const read = story.querySelector('[data-testid=story-read]');
  const begin = story.querySelector('[data-testid=ai-film-begin]');
  const sp = document.querySelector('[data-testid=ai-orb], [data-testid=ai-facecol]');
  let covered = null;
  if (sp) {
    const r = sp.getBoundingClientRect();
    if (r.width > 0 && r.height > 0) {
      const at = document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 40));
      covered = !!(at && story.contains(at));
    }
  }
  return {
    drawn: true, kind: story.getAttribute('data-kind'), first: story.hasAttribute('data-first'),
    state: player ? player.getAttribute('data-state') : null,
    pause: !!pause, pauseLabel: pause ? pause.getAttribute('aria-label') : null,
    paused: pause ? pause.getAttribute('data-paused') : null, pauseDisabled: pause ? pause.disabled : null,
    again: !!story.querySelector('[data-testid=ai-film-again]'),
    begin: !!begin, beginWords: t(begin),
    board: !!tap, expanded: tap ? tap.getAttribute('aria-expanded') : null,
    read: !!read, lines: read ? [...read.querySelectorAll('li')].map(t) : [],
    worded: [...story.querySelectorAll('button')].map(t).filter(Boolean),
    sig: board ? { on: board.querySelectorAll('.on').length, off: board.querySelectorAll('.off').length,
                   gone: board.querySelectorAll('.gone').length,
                   line: t(story.querySelector('[data-testid=story-line]')) }
      : stage ? { on: stage.querySelectorAll('img[data-testid=story-picture][data-on]').length,
                  off: stage.querySelectorAll('img[data-testid=story-picture]:not([data-on])').length, gone: 0,
                  line: t(capEl),
                  shown: (stage.querySelector('img[data-testid=story-picture][data-on]') || { getAttribute: () => null })
                    .getAttribute('data-asset') } : null,
    mode: stage ? 'pictures' : board ? 'sticks' : null,
    chapter: t(chapEl),
    layout: stage ? (column ? 'column' : 'over') : null, filmDisplay: display,
    ratio: stage ? stage.getAttribute('data-ratio') : null,
    stageBox: stage ? (() => { const r = stage.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) }; })() : null,
    captionFrom: stage ? (column ? 'story-side-line' : 'story-line') : null,
    inside: { orb: story.querySelectorAll('[data-testid=story-orb], [data-testid=ai-story-orb], [data-testid=ai-orb]').length,
              face: story.querySelectorAll('[data-testid=ai-face], [data-testid=ai-facecol]').length,
              video: story.querySelectorAll('video').length },
    covered,
  };
}"""


class Player:
    """The AI interviewer's page, for a stranger (a link) or the founder (Try it yourself): driven through the speech
    seam, a tap, a typed field or *Type instead*, the way a person would."""

    def __init__(self, page: Page, recorder, *, party: str = "participant", patience: float = 1.0):
        self.page = page
        self.patience = patience
        self._b = _BrowserStep(recorder, page, party)
        self.requests: list[dict] = []
        #: Spec 049: every read the page sent, its body, in order (the read-aloud step counts its reads here). Spec 074
        #: (keel-web 115): every spoken window is recorded and read by `POST .../answer` (the stranger's `interview/answer`,
        #: the founder's `interviewer/answer`) -- kept with the words its recording carried (`heard`, the padding
        #: trimmed, as keel-cloud 136's fake hears them); a `classify` the page no longer sends would still be kept.
        self.classified: list[dict] = []
        #: Spec 049 (keel-web 073 FR-1): what the sheet showed a moment after each final said on a question's or a
        #: confirmation's window, inside the quiet gap -- before the utterance was read.
        self.hearing: list[dict] = []
        page.on("request", self._keep)

    def _keep(self, request) -> None:
        if "/v2/" in request.url and request.method != "GET":
            self.requests.append({"method": request.method, "url": request.url})
            path = request.url.split("?")[0]
            if path.endswith(("/classify", "/interview/answer", "/interviewer/answer")):
                try:
                    body = request.post_data_json
                except Exception:  # noqa: BLE001 - a body that is not JSON
                    body = None
                if isinstance(body, dict) and "audio" in body:
                    body = {**{k: v for k, v in body.items() if k != "audio"}, "heard": decode_said(body.get("audio")),
                            "audio_bytes": _audio_bytes(body.get("audio"))}
                self.classified.append({"url": request.url, "body": body})

    # ---- arriving
    def open(self, url: str) -> dict:
        self.page.goto(url, wait_until="load")
        intro = self.page.get_by_test_id("ai-intro")
        intro.wait_for(state="visible", timeout=30_000)
        return self.intro()

    def intro(self) -> dict:
        """The AI intro as drawn now. Spec 160 (keel-web 256 FR-1, FR-2): the headline (`heading`), the closed
        disclosure (`answers`: open or not, its three lines), the mic test's line and block, and the one button --
        `buttons` finds *Test your mic* (`ai-mic-test`) before a sound is heard and **Begin** (`ai-start`) after, never
        both. Spec 170 FR-1 (keel-web 266 FR-1, FR-2): the one sentence under the name line (`line`, `ai-intro-line`),
        the button's words (`start_words`), the tick line (`mic_heard`: *Your mic works.*, no words of the hello), the
        block's one line, and 256's retired ids still drawn (`retired`: the study line, the asks line, the chips)."""
        intro = self.page.get_by_test_id("ai-intro")
        start = self.page.get_by_test_id("ai-start")
        heard = self.page.get_by_test_id("ai-mic-heard")
        answers = self.page.get_by_test_id(INTRO_ANSWERS)
        block = self.page.get_by_test_id(MIC_BLOCK_ID)
        return {"intro": intro.get_attribute("data-intro"), "heading": _words(intro.locator("h1").first),
                "text": _words(intro),
                # spec 159 (keel-web 253 FR-2): who asks -- the face's hello, or the still orb in its place
                "speaker": intro.get_attribute("data-speaker"),
                "orb": self.page.locator(f"[data-testid={INTRO_ORB}] [data-testid=story-orb]").count(),
                "line": _words(self.page.get_by_test_id(INTRO_LINE_ID)),
                "retired": [t for t in ENTRY_IDS_BEFORE_266 if self.page.get_by_test_id(t).count()],
                "answers": {"drawn": answers.count() > 0,
                            "open": bool(answers.count() and answers.first.evaluate("(d) => d.open")),
                            "summary": _words(answers.locator("summary").first),
                            "lines": [_words(self.page.get_by_test_id(t)) for t in
                                      ("ai-intro-mic-line", "ai-intro-transcribed", "ai-intro-consent")]},
                "buttons": [t for t in ("ai-mic-test", "ai-start", "start-talking", "choice-talk", "choice-write")
                            if self.page.get_by_test_id(t).count()],
                "mic_test": self.page.get_by_test_id("ai-mic-test").count() > 0,
                "mic_test_words": _words(self.page.get_by_test_id("ai-mic-test")) or None,
                "mic_state": self.page.get_by_test_id("ai-mic").first.get_attribute("data-state")
                if self.page.get_by_test_id("ai-mic").count() else None,
                "mic_heard": _words(heard) or None,
                "start_words": _words(start) or None,
                "block": {"drawn": block.count() > 0, "line": _words(block.locator(".aiv-mic__block-line").first)},
                "fallback": self.page.get_by_test_id(MIC_FALLBACK_RETIRED).count(),
                # keel-web 256 FR-2 / 266 FR-2: Begin is not drawn until a sound is heard -- not drawn is not enabled
                "start_enabled": start.is_enabled() if start.count() else False}

    def hear(self, *, wait_s: float) -> dict:
        """keel-web 087 FR-3: *Hear <name>* (`intro-hear`) on the intro -- its words, the clip that played in place of
        the round still, the still after the end, and the choice buttons' enabled state polled every 100 ms from the
        tap to the end (`polls`: one [talk, write] pair a poll)."""
        intro = self.page.get_by_test_id("ai-intro")
        button = self.page.get_by_test_id(INTRO_HEAR)
        button.wait_for(state="visible", timeout=10_000)
        before = {"words": _words(button), "label": button.get_attribute("aria-label"), **_showing(intro),
                  "buttons": {t: self.page.get_by_test_id(t).is_enabled() for t in ("choice-talk", "choice-write")
                              if self.page.get_by_test_id(t).count()}}
        heard = _heard(self.page, "intro", button.click, wait_s=wait_s,
                       polls=["[data-testid=choice-talk]", "[data-testid=choice-write]"])
        after = {**_still_back(intro, wait_s=5),
                 "buttons": {t: self.page.get_by_test_id(t).is_enabled() for t in ("choice-talk", "choice-write")
                             if self.page.get_by_test_id(t).count()}}
        return {"before": before, **heard, "after": after}

    def mic_test(self, sound: str = MIC_SOUND, *, timeout_s: float = 20) -> dict:
        """Spec 170 FR-1 (keel-web 266 FR-2, FR-3): *Test your mic* pressed -> the seam's microphone (always granted) ->
        the wave and *Say anything.* (`ai-mic-say`) in the button's place -> a sound made through the seam (`sound`
        said: its words are never read back) -> *Your mic works.* (`ai-mic-heard`) above **Begin** (`ai-start`),
        enabled. What the intro drew before and after, and the block while it listened (`listening`). keel-web 266
        passes on 300 ms of sound and sends the recording to the transcriber in the background, unread: there is no
        `writing` state to catch (spec 099's held stop is gone)."""
        before = self.intro()
        made = self.recorder()["count"]
        self.page.get_by_test_id("ai-mic-test").click()
        deadline = timeout_s * 1000 * self.patience
        self.wait_listening(newer_than=made, timeout_s=timeout_s)
        self.page.locator("[data-testid=ai-mic][data-state=listening] [data-testid=ai-mic-wave]").wait_for(
            state="attached", timeout=deadline)
        listening = self.mic_block()
        said = self.say(sound, True)
        self.page.get_by_test_id("ai-mic-heard").wait_for(state="visible", timeout=deadline)
        # keel-web 256 FR-2 / 266 FR-2: the one button becomes **Begin** in the same place once a sound is heard
        self.page.locator("[data-testid=ai-start]:not([disabled])").wait_for(timeout=deadline)
        return {"before": before, "listening": listening, "said": said, "after": self.intro()}

    def refused_mic_test(self, *, timeout_s: float = 20, hold_s: float = 2.0) -> dict:
        """Spec 160 FR-2 (keel-web 256 FR-2): *Test your mic* with the microphone refused (`speech_seam(refused=True)`)
        ends at the block (`ai-mic-block`: since keel-web 266 the one line *This interview needs your microphone. Allow
        it for this page in your browser, then try again.*) -- the button stays *Test your mic*, no **Begin**. Read once the block is drawn and again `hold_s` later (nothing
        starts by itself): what the intro drew before, at the block and after the wait, and whether the stage ever
        showed."""
        before = self.intro()
        self.page.get_by_test_id("ai-mic-test").click()
        deadline = timeout_s * 1000 * self.patience
        block = self.page.get_by_test_id(MIC_BLOCK_ID)
        block.wait_for(state="visible", timeout=deadline)
        at = self.intro()
        self.page.wait_for_timeout(int(hold_s * 1000))
        stage = self.page.get_by_test_id("ai-stage")
        return {"before": before, "block": at["block"], "at": at, "after": self.intro(),
                "stage_shown": bool(stage.count() and stage.first.is_visible()),
                "sheet": self.page.get_by_test_id("ai-sheet").count(), "phase": self.phase()}

    def allow_mic(self) -> None:
        """Spec 160 FR-2: the microphone allowed again (the seam's `__micRefused` cleared), as a person would in the
        browser's site settings before pressing *Test your mic* once more."""
        self.page.evaluate("() => { window.__micRefused = false; }")

    # ---- spec 160 (keel-web 256 FR-3, FR-4, FR-5 / FR-6): the film, the replay mark, the speaker's size
    def film(self) -> dict:
        """The film on the stage as drawn now (`FILM_JS`): its kind, the player's state, the pause icon's label and
        `data-paused`, *Start over*, *Begin the interview*, the board's `aria-expanded` and the lines under it, the
        drawing's progress (`sig`: the strokes lit, erased, gone, and the line said), and what is inside it or above it
        -- a speaker (`story-orb`, `ai-face`, a `<video>`, `ai-orb`) inside the film, and whether the speaker's own box,
        where it has a size, is under the film (`covered`) or seen over it."""
        return self.page.evaluate(FILM_JS)

    def speaker_box(self) -> dict:
        """keel-web 256 FR-5 / FR-6: the speaker's own box (`ai-orb` or `ai-facecol`) -- whether it is seen, its size
        (`data-size`), its box."""
        return self.page.evaluate("""() => {
            const el = document.querySelector('[data-testid=ai-orb], [data-testid=ai-facecol]');
            if (!el) return { drawn: false };
            const r = el.getBoundingClientRect();
            const seen = (el.checkVisibility ? el.checkVisibility() : true) && r.width > 0 && r.height > 0;
            const at = seen ? document.elementFromPoint(r.left + r.width / 2, r.top + Math.min(r.height / 2, 40)) : null;
            const story = document.querySelector('[data-testid=ai-story]');
            return { drawn: true, id: el.getAttribute('data-testid'), size: el.getAttribute('data-size'), seen,
                     covered: !!(at && story && story.contains(at)), w: Math.round(r.width), h: Math.round(r.height) };
        }""")

    def now_ms(self) -> float:
        """The page's clock (`Date.now()`), the one `ORB_INTERVIEW_WATCH` stamps its plays with."""
        return float(self.page.evaluate("() => Date.now()"))

    def speaker(self) -> str | None:
        """Spec 159: the stage's `data-speaker` (ORB or AVATAR), None off the stage."""
        stage = self.page.get_by_test_id("ai-stage")
        return stage.first.get_attribute("data-speaker") if stage.count() else None

    def orb_state(self) -> str | None:
        """Spec 159 FR-1: the stage orb's `data-state` -- since keel-web 274 FR-4 (spec 172 FR-2) the founder's four
        states and paused (asking, hearing, waiting, thinking, paused; 272's six read through `story_screens.orb_state`)."""
        orb = self.page.get_by_test_id(STAGE_ORB)
        return orb.first.get_attribute("data-state") if orb.count() else None

    def typed_boxes(self) -> list[dict]:
        """Spec 159 FR-3: every box on the page that takes typed words (`TYPED_BOXES`) -- its test id and tag."""
        return self.page.evaluate("""(sel) => [...document.querySelectorAll(sel)].map((el) => ({
            id: el.getAttribute('data-testid'), tag: el.tagName.toLowerCase(), type: el.getAttribute('type') }))""",
                                  TYPED_BOXES)

    def mic_block(self) -> dict:
        """Spec 099 (keel-web 143 FR-3): *Test your mic*'s block as drawn now, read in one evaluate -- its state
        (`ai-mic[data-state]`), the wave inside `ai-mic-level` (`ai-mic-wave` listening; its bars and `data-level`), the
        retired meter (`.aiv__level`), any `ai-mic-on` on the intro, the heard line and whether **Begin** is enabled.
        Spec 170 (keel-web 266 FR-2): the line under the wave (`say`, `ai-mic-say`: *Say anything.*) and whether *Test
        your mic* is still drawn (`test_button`: not while it listens); 143's writing line is gone."""
        return self.page.evaluate("""() => {
            const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : null;
            const block = document.querySelector('[data-testid=ai-mic]');
            const level = document.querySelector('[data-testid=ai-mic-level]');
            const wave = level ? level.querySelector('[data-testid=ai-mic-wave], [data-testid=ai-mic-writing]') : null;
            const intro = document.querySelector('[data-testid=ai-intro]');
            const say = document.querySelector('[data-testid=ai-mic-say]');
            const start = document.querySelector('[data-testid=ai-start]');
            return { state: block ? block.getAttribute('data-state') : null,
                     wave: wave ? wave.getAttribute('data-testid') : null,
                     wave_state: wave ? wave.getAttribute('data-state') : null,
                     bars: wave ? wave.querySelectorAll('i').length : 0,
                     level: wave ? wave.getAttribute('data-level') : null,
                     meter: document.querySelectorAll('.aiv__level').length,
                     mic_on: intro ? intro.querySelectorAll('[data-testid=ai-mic-on]').length : 0,
                     say: words(say),
                     test_button: document.querySelectorAll('[data-testid=ai-mic-test]').length,
                     mic_heard: words(document.querySelector('[data-testid=ai-mic-heard]')),
                     start_enabled: start ? !start.disabled : false };
        }""")

    def start(self, testid: str = "ai-start") -> None:
        """The intro's button -- pressed again while the page is still the intro: a press that lands before the app
        has hydrated is lost (seen once on S-006: the intro drawn, the stage never left it). Since keel-web 072 it is
        enabled by *Test your mic*; since keel-web 256 FR-2 it is drawn only once the mic is heard (`ai-start`, in
        *Test your mic*'s place; **Begin** since keel-web 266), so the leg tests the mic first."""
        button = self.page.get_by_test_id(testid)
        for _ in range(5):
            button.click()
            try:
                self.page.get_by_test_id("ai-intro").wait_for(state="detached", timeout=3_000)
                return
            except Exception:  # noqa: BLE001 - still the intro: press again
                if not button.count():
                    return
        raise AssertionError(f"the intro never left on {testid}")

    # ---- the stage
    def phase(self) -> str | None:
        stage = self.page.get_by_test_id("ai-stage")
        return stage.get_attribute("data-phase") if stage.count() else None

    def wait_phase(self, *phases: str, timeout_s: float = 30) -> str:
        sel = ", ".join(f'[data-testid=ai-stage][data-phase="{p}"]' for p in phases)
        self.page.locator(sel).first.wait_for(state="attached", timeout=timeout_s * 1000 * self.patience)
        return self.phase() or ""

    def stage(self) -> dict:
        video = self.page.locator("video.aiv-stage__video")
        return {"phase": self.phase(), "where": _words(self.page.get_by_test_id("ai-where")),
                "state": _words(self.page.get_by_test_id("ai-state")),
                "mark": _words(self.page.get_by_test_id("ship-mark")),
                "videos": video.count(), "clip": video.first.get_attribute("data-clip") if video.count() else None,
                "band": self.band()}

    def band(self) -> dict:
        """keel-web 113 FR-3 (spec 073 FR-5): the face box's own classes for the crop -- `aiv-stage__face--band` and
        `data-band` for a face in the picture table, the band's one video and the blurred still -- read, never judged:
        the crop's frames are keel-web's."""
        face = self.page.get_by_test_id("ai-face")
        classes = (face.first.get_attribute("class") or "").split() if face.count() else []
        return {"band": face.first.get_attribute("data-band") if face.count() else None,
                "classed": "aiv-stage__face--band" in classes,
                "band_video": self.page.locator("[data-testid=ai-band] video.aiv-stage__video.aiv-band__video").count(),
                "blur": self.page.get_by_test_id("ai-band-blur").count()}

    # ---- the sheet
    def sheet(self) -> dict:
        sheet = self.page.get_by_test_id("ai-sheet")
        options = sheet.locator("[data-testid=ai-options] .opt")
        field = sheet.get_by_test_id("ai-field")
        return {"question": _words(sheet.locator(".iv-q").first), "kicker": _words(sheet.locator(".iv-kicker").first),
                "options": [{"label": _words(o), "checked": o.get_attribute("aria-checked") == "true",
                             "role": o.get_attribute("role"), "unsure": o.get_attribute("data-unsure")}
                            for o in options.all()],
                "field": field.input_value() if field.count() else None,
                "chip": _words(sheet.locator(".iv-chips .chip").first) or None,
                # spec 117 FR-4 (keel-web 152 FR-1): the story's sheet draws every chip the gate serves, in the served
                # order -- *I can't recall one particular {occasion}* still first (`chip`), then *I'd rather not say*
                "chips": [_words(c) for c in sheet.locator(".iv-chips .chip").all()],
                "preview": _words(sheet.get_by_test_id("ai-preview")),
                "heard": _words(sheet.get_by_test_id("ai-heard")),
                "status": _words(sheet.get_by_test_id("ai-status")),
                "banner": _words(sheet.get_by_test_id("ai-banner")) or None,
                # spec 118 FR-4c(b) (keel-web 156 T015, J-13): which ask the sheet is on (`main`, `under`, `over`,
                # `plan`, `planUnder`, `planOver`) and, on a second step, the rows greyed and the side's line
                "ask": sheet.first.get_attribute("data-ask") if sheet.count() else None,
                "greyed": [_words(o) for o in sheet.locator("[data-testid=ai-options] [data-greyed=true]").all()]}

    def ask(self) -> str | None:
        """Spec 118 FR-4c(b) (keel-web 156 J-13): the sheet's `data-ask` -- `main` on a question's first ask, `under` /
        `over` on Price's second step (`planUnder` / `planOver` on the plan's), None where the sheet draws none."""
        sheet = self.page.get_by_test_id("ai-sheet")
        return sheet.first.get_attribute("data-ask") if sheet.count() else None

    def wait_ask(self, *asks: str, timeout_s: float = 30) -> str | None:
        """Until the sheet's `data-ask` is one of `asks` (the second step opened), and which."""
        deadline = time.monotonic() + timeout_s * self.patience
        while time.monotonic() < deadline:
            now = self.ask()
            if now in asks:
                return now
            self.page.wait_for_timeout(100)
        raise AssertionError({"the sheet never asked": asks, "ask": self.ask(), "question": self.question()})

    def say(self, text: str, final: bool = True, *, look: bool = True) -> bool:
        """The stranger speaks into the window the page records (spec 074, keel-web 115 FR-5: the level pulses, then
        silence; the recording carries the words). The page stops the window two seconds after the last sound (four on
        free text) and Keel writes it down and reads it; nothing is pressed after it. On a question's or a
        confirmation's window (`listening` / `confirming`) a final is looked at inside that quiet (`look`): what was
        ticked, filled and previewed before the words and 250 ms after them, kept on `hearing` -- `still` when the page
        is still recording (*Recording your answer.*) and says *Hearing you…* (or, once the pause has sent it, keel-web
        143's *Writing down what you said…*), nothing read yet."""
        phase = self.phase() if final and look else None
        before = self._drawn() if phase in ("listening", "confirming") else None
        said = bool(self.page.evaluate("([t, f]) => window.__say(t, f)", [text, final]))
        if before is not None and said:
            self.page.wait_for_timeout(250)
            after = self._drawn()
            self.hearing.append({"said": text, "phase": phase, "before": before, "after": after,
                                 "still": self.phase() == phase and after["status"] == RECORDING
                                 and after["heard"] in (HEARING_YOU, HEARD_WRITING_DOWN)})
        return said

    def _drawn(self) -> dict:
        """The sheet's ticks, field, preview, heard line and status, read in one evaluate (inside the gap it must be
        quick)."""
        return self.page.evaluate("""() => {
            const sheet = document.querySelector('[data-testid=ai-sheet]');
            const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : '';
            if (!sheet) return { lit: [], field: null, preview: '', heard: '', status: '' };
            const lit = [...sheet.querySelectorAll('[data-testid=ai-options] .opt[aria-checked="true"]')].map(words);
            const field = sheet.querySelector('[data-testid=ai-field]');
            return { lit, field: field ? field.value : null,
                     preview: words(sheet.querySelector('[data-testid=ai-preview]')),
                     heard: words(sheet.querySelector('[data-testid=ai-heard]')),
                     status: words(sheet.querySelector('[data-testid=ai-status]')) };
        }""")

    def checked(self) -> list[str]:
        """The rows ticked on the sheet now (`aria-checked="true"`)."""
        return list(self._drawn()["lit"])

    def recorder(self) -> dict:
        """Spec 074 (keel-web 115): the seam's recorder -- how many recordings the page has begun (`__recordStarts`),
        whether one runs on the current window now (`__listening()`), and the microphone's releases so far."""
        return self.page.evaluate("""() => ({ count: (window.__recordStarts || []).length,
            live: !!(window.__listening && window.__listening()), released: window.__micReleased || 0 })""")

    def wait_listening(self, *, newer_than: int | None = None, timeout_s: float = 20) -> dict:
        """A window recording -- one begun after `newer_than` recordings when given (a window opened again after a
        clip). It replaces the recogniser's `wait_ear` (keel-web 115 retired the recogniser)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            now = self.recorder()
            if now["live"] and (newer_than is None or now["count"] > newer_than):
                return now
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"no window recording": self.recorder(), "newer than": newer_than,
                              "phase": self.phase(), "status": self.status()})

    def status(self) -> str:
        return _words(self.page.get_by_test_id("ai-status"))

    def question(self) -> str:
        return _words(self.page.get_by_test_id("ai-sheet").locator(".iv-q").first)

    def second_ask(self) -> str:
        """Spec 090 FR-2 (keel-web 135 H-1): Importance's second ask as the sheet writes it --
        `[data-testid=ai-sheet] [data-testid=second-ask]` (`p.iv-second`, the served `secondAsk.question`, *And one
        more?*) under the rows; `.iv-q` stays the item's question and the status never says it. "" while not drawn."""
        line = self.page.get_by_test_id("ai-sheet").get_by_test_id("second-ask")
        return _words(line.first) if line.count() else ""

    def chip_pressed(self) -> list[str]:
        """keel-web 135 H-7: the chips pressed on the sheet (`.iv-chips` `aria-pressed="true"`) -- *Nothing else* once
        it is the answer."""
        chips = self.page.get_by_test_id("ai-sheet").locator(".iv-chips [aria-pressed=true]")
        return [_words(c) for c in chips.all()]

    def wait_status(self, *words: str, timeout_s: float = 20) -> str:
        """The sheet's status line reading one of `words` (keel-web 072 FR-9)."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            now = self.status()
            if any(w in now for w in words):
                return now
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"status never read": words, "it read": self.status(), "phase": self.phase()})

    def wait_missed(self, *, timeout_s: float = 20) -> str:
        """keel-web 073: a miss is read after the quiet gap -- the heard line tagged *not taken*, or her asking again.
        What the heard line or the status then read."""
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            drawn = self._drawn()
            if TAG_NOT_TAKEN in drawn["heard"] or "asks again" in drawn["status"] or "Say it again" in drawn["status"]:
                return drawn["preview"] or drawn["heard"] or drawn["status"]
            self.page.wait_for_timeout(100)
            waited += 100
        raise AssertionError({"the miss was never read": self._drawn(), "phase": self.phase()})

    def say_story(self, words: str, *, parts: int = 2, pause_s: float = STORY_PAUSE_S,
                  timeout_s: float = 30) -> dict:
        """Spec 172 FR-2 (keel-web 274 FR-1, FR-2): a long answer told -- the story in `parts` (two: a pause of `pause_s`,
        under eight seconds, between them; a follow-up in one), the done word after the last, then Keel's
        acknowledgement read (`ai-story-got-it`). What it drew: the parts said, whether the window stayed open across the
        pause (`open_across`), the ask seen in it (`asked`), the acknowledgement's words and kind (`ack`, `ack_kind`),
        and whether the short answers' hold (`HELD`) stood instead (`held`)."""
        said = story_parts(words, parts)
        out: dict = {"parts": said, "open_across": None, "asked": False, "ack": None, "ack_kind": None, "held": False}
        self.say(said[0])
        if len(said) > 1:
            self.page.wait_for_timeout(int(pause_s * 1000))
            out["asked"] = self.page.get_by_test_id(LONG_ASK_ID).count() > 0
            out["open_across"] = self.page.get_by_test_id(LONG_GOT_IT_ID).count() == 0 and HELD not in self.status()
            self.wait_listening(timeout_s=timeout_s)
            self.say(said[1])
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline:
            ack = self.page.get_by_test_id(LONG_GOT_IT_ID)
            if ack.count():
                out["ack"] = _words(ack.first)
                out["ack_kind"] = ack.first.get_attribute("data-ack")
                break
            if HELD in self.status():
                out["held"] = True
            self.page.wait_for_timeout(100)
            waited += 100
        return out

    def long_close(self, *, timeout_s: float = 20) -> dict:
        """Spec 172 FR-2 (keel-web 274 FR-2): a long answer closed (the done word, Save, or the cap) -- Keel's
        acknowledgement on the status line (`ai-story-got-it`, *Got it. Thank you.*; `data-ack` its kind), no veto
        hold, then the next step by itself. What it drew, in `hold`'s shape (`status` the acknowledgement's words) with
        `held` where the short answers' *Got it. Moving on...* stood instead."""
        before = self.question()
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        out: dict = {"question": before, "status": None, "ack": None, "ack_kind": None, "held": False, "heard": "",
                     "phase": None}
        while waited <= deadline:
            ack = self.page.get_by_test_id(LONG_GOT_IT_ID)
            if ack.count():
                out.update(status=_words(ack.first), ack=_words(ack.first), ack_kind=ack.first.get_attribute("data-ack"),
                           phase=self.phase())
                break
            if HELD in self.status():
                out["held"] = True
            if self.question() != before:
                break
            self.page.wait_for_timeout(100)
            waited += 100
        while waited <= deadline and self.question() == before and self.page.get_by_test_id(LONG_GOT_IT_ID).count():
            self.page.wait_for_timeout(100)
            waited += 100
        out["next"] = self.question()
        out["went_on"] = out["next"] != before
        return out

    def hold(self, *, timeout_s: float = 20) -> dict:
        """A confident read held (keel-web 072 FR-4): the status reads *Got it. Moving on… say no to change* with the
        pick lit, and -- nothing said, nothing tapped -- the question goes on by itself. What the hold drew, and the
        question that came after it."""
        before = self.question()
        status = self.wait_status(HELD, timeout_s=timeout_s)
        phase = self.phase()
        sheet = self.sheet()
        rings = self.page.locator("[data-testid=ai-sheet] .aiv__ring, [data-testid=ai-ring]").count()
        finish = self.page.get_by_test_id("ai-finish")
        finish_shown = finish.count() > 0 and finish.first.is_visible()
        deadline = timeout_s * 1000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        return {"question": before, "status": status, "lit": [o["label"] for o in sheet["options"] if o["checked"]],
                "unsure": [o["unsure"] for o in sheet["options"] if o["checked"]], "phase": phase,
                "heard": sheet["heard"], "ring": rings > 0, "finish": finish_shown, "next": self.question(),
                "went_on": self.question() != before or HELD not in self.status()}

    def veto(self, word: str = VETO, *, final: bool = True) -> dict:
        """A word of protest in the hold (FR-4): the hold ends and the question reopens, the pick still lit. Spec 074
        (keel-web 115): the hold records too -- a sound pauses it, and the recording, written down two seconds after the
        last sound, is read as a veto -- so the word is said as a final (an interim would hold the level up, and the
        recording, open)."""
        before = self.question()
        self.wait_status(HELD)
        self.wait_listening()                           # the hold's own recording
        self.say(word, final)
        waited = 0
        while waited < 5_000 * self.patience and HELD in self.status():
            self.page.wait_for_timeout(100)
            waited += 100
        reopened = self.question() == before and HELD not in self.status()
        return {"question": before, "said": word, "reopened": reopened, "status": self.status(),
                "lit": [o["label"] for o in self.sheet()["options"] if o["checked"]]}

    def confirming(self, *, timeout_s: float = 20) -> dict:
        """An unsure read (FR-2): *Is that right? Say yes, or tell me the right one*, the pick lit, the Yes chip."""
        status = self.wait_status(IS_THAT_RIGHT, timeout_s=timeout_s)
        sheet = self.sheet()
        unsure = [_words(o) for o in self.page.locator('[data-testid=ai-sheet] .opt[data-unsure="true"]').all()]
        yes = self.page.get_by_test_id("ai-yes")
        return {"question": self.question(), "status": status,
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "unsure": unsure,
                "yes": _words(yes) if yes.count() else None}

    def yes(self, *, by: str = "say") -> None:
        """Agreeing to "Is that right?": *Yes, that's it* tapped, or "yes" said -- straight on, no hold."""
        if by == "tap":
            self.page.get_by_test_id("ai-yes").click()
        else:
            self.say(SAY_YES, True)

    def back(self, *, by: str = "tap") -> dict:
        """The way back (FR-6): *‹ Back to question n* tapped, or "go back" said, from the next question -- the previous
        question reopens with its answer lit, no clip replayed."""
        before = self.question()
        button = self.page.get_by_test_id("ai-back")
        drawn = _words(button) if button.count() else None
        if by == "say":
            self.say(GO_BACK, True)
        else:
            button.click()
        deadline = 10_000 * self.patience
        waited = 0.0
        while waited <= deadline and self.question() == before:
            self.page.wait_for_timeout(100)
            waited += 100
        sheet = self.sheet()
        return {"from": before, "button": drawn, "by": by, "to": self.question(),
                "lit": [o["label"] for o in sheet["options"] if o["checked"]], "field": sheet["field"]}

    def timeline(self) -> list[dict]:
        """`FLOW_TIMELINE`'s events, or none where the init script was not installed."""
        try:
            return list(self.page.evaluate("() => window.__keelFlow ? window.__keelFlow() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def statuses(self) -> list[dict]:
        """`FLOW_TIMELINE`'s status words, in order (`window.__keelPhases`)."""
        try:
            return list(self.page.evaluate("() => window.__keelPhases ? window.__keelPhases() : []") or [])
        except Exception:  # noqa: BLE001
            return []

    def heard_lines(self) -> list[dict]:
        """Spec 099 (keel-web 143): `FLOW_TIMELINE`'s heard line, every change in order (`window.__keelHeard`) --
        `{t, state, words, question}`, `state` the line's `data-heard` (None while it is not drawn)."""
        try:
            return list(self.page.evaluate("() => window.__keelHeard ? window.__keelHeard() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def saw_thats_my_answer(self) -> bool | None:
        try:
            return self.page.evaluate("() => window.__keelSawAnswer ? window.__keelSawAnswer() : null")
        except Exception:  # noqa: BLE001
            return None

    def beats(self) -> list[dict]:
        """Spec 050 (keel-web 075 FR-1): every beat the timeline kept -- its start and end (`performance.now()`), the clip
        played before it, the statuses and pills it drew, and whether the waveform, a question, the options or a sheet
        button were ever in it."""
        try:
            return list(self.page.evaluate("() => window.__keelBeats ? window.__keelBeats() : []") or [])
        except Exception:  # noqa: BLE001 - a page that has gone
            return []

    def starts(self) -> dict:
        """Spec 050: when every recording was begun (`performance.now()`) -- spec 074: the page's one ear since keel-web
        115 (the recogniser's starts are gone) -- and when the microphone was let go (`released`, keel-web 116)."""
        try:
            return dict(self.page.evaluate(
                "() => ({ record: (window.__recordStarts || []).slice(), "
                "released: (window.__micReleasedAt || []).slice() })"))
        except Exception:  # noqa: BLE001
            return {"record": [], "released": []}

    def mic_off(self, *, timeout_s: float = 10) -> dict:
        """keel-web 075 FR-4: *Microphone off* (`ai-mic-off`, `role=status`) on the done or the ended screen once every
        holder of the microphone has let go; and the seam's recorder no longer running (spec 074: keel-web 115's one
        ear), with the microphone's releases so far (`released`; keel-web 116: the thanks lets go when its clip ends)."""
        line = self.page.get_by_test_id("ai-mic-off")
        try:
            line.first.wait_for(state="visible", timeout=timeout_s * 1000 * self.patience)
        except Exception:  # noqa: BLE001 - not drawn: reported, the leg judges
            pass
        shown = line.count() > 0 and line.first.is_visible()
        return {"shown": shown, "text": _words(line.first) if shown else None,
                "role": line.first.get_attribute("role") if shown else None,
                "listening": bool(self.page.evaluate("() => window.__listening ? window.__listening() : false")),
                "released": int(self.page.evaluate("() => window.__micReleased || 0")),
                "at": float(self.page.evaluate("() => performance.now()"))}

    def save(self) -> None:
        """*Save and next* -- typed words keep their explicit press (072 FR-5), and since keel-web 073 FR-6 tapped
        checkboxes finish on it too."""
        self.page.get_by_test_id("ai-sheet").get_by_role("button", name=SAVE_AND_NEXT, exact=True).click()

    def save_state(self) -> dict:
        """keel-web 073 FR-6: *Save and next* (`ai-save`) -- drawn or not, enabled or not, its words; and the hold's ring
        (`ai-ring`), which a tick never starts."""
        button = self.page.get_by_test_id("ai-save")
        shown = button.count() > 0 and button.first.is_visible()
        return {"shown": shown, "enabled": button.first.is_enabled() if shown else None,
                "words": _words(button.first) if shown else None,
                "ring": self.page.get_by_test_id("ai-ring").count() > 0, "phase": self.phase(),
                "checked": self.checked()}

    def finish(self) -> None:
        """*Finish* on the pilot ask (072 FR-2). Since keel-web 073 FR-7 the pilot's yes is held and goes on by itself:
        *Finish* only ends that hold early, and after a tap it is on the sheet for the tap's 500 ms alone (073 D-03) --
        the walk waits for the thanks instead of pressing it."""
        button = self.page.get_by_test_id("ai-sheet").get_by_role("button", name=FINISH, exact=True)
        button.wait_for(state="visible", timeout=10_000 * self.patience)
        button.click()

    def tap(self, label: str) -> None:
        self.page.get_by_test_id("ai-sheet").locator("[data-testid=ai-options] .opt", has_text=re.compile(
            rf"^\s*{re.escape(label)}\s*$")).first.click()

    def tap_chip(self) -> None:
        self.page.get_by_test_id("ai-sheet").locator(".iv-chips .chip").first.click()

    def tap_chip_named(self, label: str) -> None:
        """A chip by its words -- Importance's second ask draws *Nothing else* in *None of these*' place (keel-cloud 158
        T010, keel-web 135 FR-2); the story's *I'd rather not say*, its second chip since keel-web 152 (spec 117 FR-4),
        which ends the interview as the first does (`anchorChip: RATHER_NOT_SAY`, the same chip-only body)."""
        self.page.get_by_test_id("ai-sheet").locator(".iv-chips .chip", has_text=re.compile(
            rf"^\s*{re.escape(label)}\s*$")).first.click()

    def type_instead(self, text: str) -> None:
        """*Type instead*, the words typed; *Save and next* (`save`) sends them on."""
        self.page.get_by_test_id("ai-type").click()
        self.page.get_by_test_id("ai-typed").fill(text)

    def fill_field(self, value: str) -> None:
        self.page.get_by_test_id("ai-field").fill(value)

    def unit(self, mode: str) -> None:
        """The amount-or-hours toggle: *Hours*, or *Amount* (its label carries the currency)."""
        name = re.compile(r"^Hours$") if mode == "HOURS" else re.compile(r"^Amount")
        self.page.get_by_test_id("ai-sheet").get_by_role("radiogroup", name="Hours or amount").get_by_role(
            "radio", name=name).click()

    def end(self) -> None:
        self.page.get_by_test_id("ai-end").click()

    def done(self, *, timeout_s: float = 20) -> dict:
        done = self.page.get_by_test_id("ai-done")
        done.first.wait_for(state="visible", timeout=timeout_s * 1000)
        return {"text": _words(done.first), "tryRun": done.first.get_attribute("data-try-run") == "true"}

    def where_it_stood(self) -> dict:
        """What the page drew when a wait gave up: the stage, the sheet, the intro or the end, and the requests."""
        out: dict = {"url": self.page.url}
        try:
            out["stage"] = self.stage()
            if self.page.get_by_test_id("ai-sheet").count():
                out["sheet"] = self.sheet()
            out["body"] = " ".join((self.page.locator("body").text_content() or "").split())[:1500]
        except Exception as broken:  # noqa: BLE001 - a diagnostic never hides the failure it explains
            out["unreadable"] = repr(broken)
        out["requests"] = self.requests[-10:]
        return out

    def screenshot(self, name: str):
        return self._b.screenshot(name)

    def step(self, name: str):
        return self._b.step(name)


# ------------------------------------------------------------------------------------- speak or type (076)

class SpeakBox:
    """keel-web 076's `SpeakOrTypeBox` on a text page (the story's, or the follow-up's): `.sot[data-state]` around the
    textarea and its footer (`.sot__bar`: the hint / the heard line / the mic-off line, and the `iv-mic` pill), the
    listening card (`iv-listening`: `ai-mic-on`, `iv-mic-clock`, `iv-mic-cancel`, `iv-mic-done`) and the writing card
    drawn over it -- and since keel-web 126 FR-4 the `asking` card (`iv-mic-asking`: *Allow the microphone…*, *Cancel*)
    between the tap and the recorder running. Driven through `text_seam`: `speak` sets the recorder's level to a sound,
    `quiet` back to nothing, `grant` answers a held permission sheet; what the seam counted is `counts()`. Reads and
    acts; judges nothing."""

    def __init__(self, page: Page, scope: str = "main"):
        self.page = page
        self.scope = scope

    def _sot(self):
        return self.page.locator(f"{self.scope} .sot").first

    def now(self) -> float:
        return float(self.page.evaluate("() => performance.now()"))

    def read(self) -> dict:
        """What the box draws now, read in one evaluate."""
        return self.page.evaluate("""(scope) => {
            const words = (el) => el ? (el.textContent || '').replace(/\\s+/g, ' ').trim() : null;
            const sot = document.querySelector(scope + ' .sot');
            if (!sot) return { state: null };
            const text = sot.querySelector('textarea');
            const card = sot.querySelector('[data-testid=iv-listening]');
            const bar = sot.querySelector('.sot__bar');
            const pill = sot.querySelector('[data-testid=iv-mic]');
            const writing = sot.querySelector('.sot__writing');
            const asking = sot.querySelector('[data-testid=iv-mic-asking]');
            return { state: sot.getAttribute('data-state'), placeholder: text ? text.getAttribute('placeholder') : null,
                     value: text ? text.value : null, caret: text ? text.selectionStart : null,
                     caretEnd: text ? text.selectionEnd : null, focused: !!text && document.activeElement === text,
                     pill: words(pill), footer: bar ? words(bar.querySelector('span')) : null,
                     card: !!card, cardWords: words(card), wave: !!(card && card.querySelector('[data-testid=ai-mic-on]')),
                     clock: words(sot.querySelector('[data-testid=iv-mic-clock]')),
                     cancel: !!sot.querySelector('[data-testid=iv-mic-cancel]'),
                     done: !!sot.querySelector('[data-testid=iv-mic-done]'),
                     writing: words(writing), note: words(sot.querySelector('.sot__note')),
                     asking: asking ? words(asking.querySelector('[data-testid=iv-mic-say]')) : null };
        }""", self.scope)

    def counts(self) -> dict:
        """The seam's stamps: microphone acquisitions, recordings started / stopped / cancelled, levels set."""
        return self.page.evaluate("""() => ({ acquired: window.__micAcquired || 0,
            acquiredAt: (window.__micAcquiredAt || []).slice(), starts: (window.__recordStarts || []).slice(),
            stops: (window.__recordStops || []).slice(), cancels: (window.__recordCancels || []).slice(),
            levels: (window.__levels || []).slice(), released: window.__micReleased || 0 })""")

    def wait_state(self, *states: str, timeout_s: float = 20) -> dict:
        sel = ", ".join(f'{self.scope} .sot[data-state="{s}"]' for s in states)
        self.page.locator(sel).first.wait_for(state="attached", timeout=timeout_s * 1000)
        return self.read()

    def tap(self) -> None:
        self._sot().get_by_test_id("iv-mic").click()

    def done(self) -> None:
        self._sot().get_by_test_id("iv-mic-done").click()

    def grant(self) -> None:
        """Spec 075 FR-5 (keel-web 126 FR-4): the held permission sheet answered -- the acquire resolves."""
        self.page.evaluate("() => { window.__micHeld = false; if (window.__grantMic) window.__grantMic(); }")

    def speak(self, ms: int = SPEAK_MS) -> float:
        """The person talks for `ms`: the recorder hears a sound; returns when the sound began."""
        at = self.now()
        self.page.evaluate(f"() => window.__level({SOUND})")
        self.page.wait_for_timeout(ms)
        return at

    def quiet(self) -> float:
        """The person stops: the recorder hears nothing from now on; returns when."""
        at = self.now()
        self.page.evaluate("() => window.__level(0)")
        return at

    def hold_stop(self) -> None:
        self.page.evaluate("() => window.__holdStop()")

    def release_stop(self) -> None:
        self.page.evaluate("() => window.__releaseStop()")
