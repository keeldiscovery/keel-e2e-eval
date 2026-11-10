You write one synthetic video call between a founder and a respondent, as a script whose truth is written before its words. A copilot will listen to the call and must tell which of the founder's questionnaire questions is being asked (in the founder's own words), read the respondent's answer against that question's options, tag follow-ups to the question just asked, and follow the founder when they move on. Your script is the referee's ground truth, so the truth on every turn must be exactly right.

Reply with one JSON object and nothing else, in this form:
{"id": "<the id given>", "round": <the round given>, "questionnaire": "<the questionnaire name given>", "turns": [{"t": <seconds from the start, when the turn starts>, "who": "founder" | "them", "text": "<the words said>", "silence_after": <seconds of silence after the turn>, "kind": "<the catalogue kind this turn was written for, or null>", "truth": {"q": "<item id>" | null, "verdict": <see below>, "option": <see below>, "tier": "sure" | "likely" | "unsure" | null, "state_after": "listening" | "answered" | "follow_up" | "note" | "paused" | "done"}}]}

The truth on a founder turn:
- q: the questionnaire item the founder is asking or following up on; null for a note or back-channel that belongs to no question.
- verdict, exactly one of: as_written (Keel's spoken question as written, a preface or a restart before it allowed), same_meaning (reworded, the meaning kept: the time window, the subject and any number kept), options_own_words (asked with the options offered in the founder's own words, reordered, or one left out), meaning_changed (close, but the window, the subject or the number dropped or changed), stacked (two questions in one breath; q is the first), leading (the question suggests its answer), follow_up (digs into the answer just given, tagged to that question), own_note (the founder asks or prompts something of their own that belongs to no Keel question; a greeting, a thank-you or "that is all I needed" is NOT an own note but a back_channel), back_channel (right, okay, yeah: opens nothing), nothing (the founder says something that is not a question and not an answer, such as saying the answer for them).
- option and tier: null on every founder turn. A founder never answers for the respondent, even when they say "so that's a yes".

The truth on a respondent turn ("them"):
- An answer: q the item answered, verdict null, option the answer read against that item's options, tier how sure a careful listener would be.
- A reply to a follow-up: q the item, verdict follow_up, option null, tier null.
- A counter-question or a turn that is not the respondent's answer (a second person on their side): q the item, verdict nothing, option null, tier null.
- option, in exactly these shapes: {"picks": [n]} with n the 1-based number of the item's option ({"picks": [n, m]} on a pick-two item); {"escape": true} when they take the escape; {"value": v} on a number item; {"unclear": true} when nothing can be read. On a free-text item the option is null (the words are the answer).
- tier: sure when one reading clearly fits; likely when it fits but with a hedge, or when it had to be read from a story; unsure when it cannot be read (option {"unclear": true}).

state_after, the state the copilot's box should be in after the turn: listening (a question is current, no answer yet), answered (the current question's answer was read), follow_up (inside the current question's follow-ups), note (an own note), paused (after five minutes with no one speaking), done (the founder has ended).

The rules your script is checked against, mechanically:
- t never goes backwards: each turn starts at or after the previous turn's start plus its silence_after. Leave 0.3 to 1.5 s of silence after most turns, as people do; a turn talked over has silence_after 0.
- A verbatim turn is the item's spoken stem, word for word (the anchor first when the item has one).
- An options_own_words turn says none of Keel's option labels as written.
- A restart breaks off with "..." and starts again. A respondent turn talked over ends with "--".
- A follow_up turn comes only after its question has been answered.
- A back-channel turn carries no question mark.
- A counter-question ends with a question mark.
- Every kind named for this script appears on at least one turn, with "kind" set to it on that turn -- except any_order, which the order of the asked questions shows.
- The call's length is the round's.

Write the founder as a real person on a call: they read from a card and drift from it, preface, restart, ask in their own words, and move on by asking the next question when they choose. Write the respondent as a real person in their trade, answering the founder's words, not Keel's. Keep every name of a person, a company or a product out of the words unless the questionnaire's own wording carries it. Do not explain the script; the JSON is the whole reply.
