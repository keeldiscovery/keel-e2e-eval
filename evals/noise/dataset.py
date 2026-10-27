"""The noisy-environment check's dataset (2026-10-26): five questions, one per control type, in the product's own
shapes (SpokenItem kinds; the labels are the web fixtures' payroll set and the home's own question), thirty spoken
answers across them -- plain, hesitant, corrected, partial, escaped, unclear -- each with the answer a careful human
would record. The free-text story (the gate's story: never classified, the transcript is the answer) carries its
reference words and the tokens whose loss changes the meaning (negations, numbers, who did it).

Expected forms (the 2026-10-16 check's): {"picks":[n..]} 1-based, order-free; {"escape":True}; {"value":v};
{"unclear":True}; {"any":[...]} any of several. The story: {"text": reference, "critical": [tokens]}.
"""

ITEMS = {
    # control: yes / no (the home's own phone question)
    "gate": {"control": "yes/no", "kind": "gate", "escape": None,
             "question": "In the last month, did you chase a late invoice?", "options": ["Yes", "No"]},
    # control: a number (0..30)
    "days": {"control": "number", "kind": "number", "range": [0, 30], "escape": "I can't recall", "options": [],
             "question": "How many days ago did you last chase one?"},
    # control: a radio group, one of three
    "better": {"control": "radio", "kind": "single", "escape": "I can't tell",
               "question": "If someone had caught that for you, would it have made things better, no difference, or worse?",
               "options": ["It would have made things better", "No difference", "It would have made things worse"]},
    # control: a checkbox group, pick two of five
    "importance": {"control": "checkbox", "kind": "multi", "pick": 2, "escape": "None of these",
                   "question": "Which two of these take the most of your week?",
                   "options": ["Catching errors before the payroll is approved", "Chasing missing timesheets",
                               "Explaining payslips to staff", "Keeping up with tax changes",
                               "Reconciling payroll with the ledger"]},
    # control: a text box, spoken continuously (the gate's story)
    "story": {"control": "free text", "kind": "free", "escape": None, "options": [],
              "question": "What happened the last time you chased a late invoice?"},
}

P = lambda *n: {"picks": sorted(n)}
E = {"escape": True}
U = {"unclear": True}
V = lambda v: {"value": v}
def ANY(*xs): return {"any": list(xs)}
def T(text, *critical): return {"text": text, "critical": list(critical)}

# (id, item, said, expected, tag)   tag: plain | hesitant | corrected | partial | escape | unclear | story
UTTERANCES = [
    ("g1", "gate", "Yeah, I did. Twice, actually.", P(1), "plain"),
    ("g2", "gate", "No, not this month.", P(2), "plain"),
    ("g3", "gate", "Um... yes... no, actually no. That was the month before.", P(2), "corrected"),
    ("g4", "gate", "I think so, yes.", P(1), "hesitant"),
    ("g5", "gate", "Not really, no.", P(2), "hesitant"),
    ("g6", "gate", "Hmm, chase... what do you mean exactly?", U, "unclear"),

    ("n1", "days", "About three days ago.", V(3), "plain"),
    ("n2", "days", "Um, twelve... no, fourteen. Two weeks.", V(14), "corrected"),
    ("n3", "days", "Yesterday.", V(1), "plain"),
    ("n4", "days", "I honestly don't remember.", E, "escape"),
    ("n5", "days", "Twenty five. Twenty five days.", V(25), "plain"),
    ("n6", "days", "It was, like, a month ago.", V(30), "hesitant"),

    ("r1", "better", "It would have made things better, definitely.", P(1), "plain"),
    ("r2", "better", "No difference, honestly.", P(2), "plain"),
    ("r3", "better", "Better, I think... actually, no difference.", P(2), "corrected"),
    ("r4", "better", "Honestly it would make it harder, so, worse.", P(3), "hesitant"),
    ("r5", "better", "Um, I can't really tell.", E, "escape"),
    ("r6", "better", "The first one.", P(1), "plain"),

    ("c1", "importance", "The timesheets one and the tax changes.", P(2, 4), "plain"),
    ("c2", "importance", "Uh, the, the payslip one, and um, keeping up with the tax stuff.", P(3, 4), "hesitant"),
    ("c3", "importance", "Catching errors before payroll, and reconciling with the ledger.", P(1, 5), "plain"),
    ("c4", "importance", "The tax one... no, sorry, the timesheets. And explaining payslips.", P(2, 3), "corrected"),
    ("c5", "importance", "Chasing the missing timesheets.", P(2), "partial"),
    ("c6", "importance", "None of these, really.", E, "escape"),

    ("s1", "story", "So the invoice was, um, forty-five days late, and I had to call them three times before anyone picked up, and in the end they said they never got it.",
     T("so the invoice was um forty-five days late and I had to call them three times before anyone picked up and in the end they said they never got it", "forty-five", "three", "never"), "story"),
    ("s2", "story", "Honestly I didn't chase it, my colleague did, because I was out that week. It took about two weeks and we did not get paid until the end of the month.",
     T("honestly I didn't chase it my colleague did because I was out that week it took about two weeks and we did not get paid until the end of the month", "didn't", "colleague", "two", "not"), "story"),
    ("s3", "story", "It was a small one, maybe two hundred dollars. I just sent a reminder email and they paid it the next day, no drama.",
     T("it was a small one maybe two hundred dollars I just sent a reminder email and they paid it the next day no drama", "two hundred", "next day"), "story"),
    ("s4", "story", "Um, so I called the accounts team, they said the PO number was wrong, so I had to reissue it, which took, I don't know, another ten days.",
     T("um so I called the accounts team they said the PO number was wrong so I had to reissue it which took I don't know another ten days", "wrong", "ten"), "story"),
    ("s5", "story", "The client wasn't unhappy, they just forgot, so one message fixed it. But it's the fourth time this year, so it's not nothing.",
     T("the client wasn't unhappy they just forgot so one message fixed it but it's the fourth time this year so it's not nothing", "wasn't", "fourth", "not"), "story"),
    ("s6", "story", "I ended up driving over there, which is ridiculous for a six hundred euro invoice, but after that they paid within forty-eight hours.",
     T("I ended up driving over there which is ridiculous for a six hundred euro invoice but after that they paid within forty-eight hours", "six hundred", "forty-eight"), "story"),
]

# The other voices in a cafe: unrelated talk, with the words that could leak into an answer (numbers, no, the option words).
BABBLE = [
    "Can I get a flat white and one of those almond croissants, please?",
    "I told him the meeting moved to Thursday, but he never checks his calendar.",
    "No, no, the other one, the blue one, next to the window.",
    "It was like forty dollars for two drinks, I'm not going back there.",
    "She said the train was twenty minutes late again, so we just walked.",
    "Honestly the first one was better, the second season lost me completely.",
    "Yes, three of them, and one without sugar.",
    "We did the payroll thing on Friday, the timesheets were a mess as usual.",
]

# OpenAI gpt-4o-mini-tts voices: two per utterance, rotated so every voice is heard across the set.
VOICES = ["alloy", "onyx", "nova", "sage", "echo", "shimmer"]
BABBLE_VOICES = ["ash", "ballad", "coral", "fable", "verse", "alloy", "onyx", "nova"]

# The environments: five synthesized beds at four signal-to-noise ratios, and the quiet room.
BEDS = ["construction", "traffic", "cafe", "music", "wind"]
SNRS = [20, 10, 5, 0]

def voices_for(i):
    return [VOICES[i % len(VOICES)], VOICES[(i + 3) % len(VOICES)]]
