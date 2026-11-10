"""Spec 151 FR-6: the bars, as the methodology page proposes them (2026-11-10) -- the founder's to change, here and
nowhere else. Each cell: the number it reads, `>=` or `<=`, the bar. The order is the order a failing cell is named in.
`ROUND_CELLS` says which numbers each round gates: R1 teaches A and B alone (with E's hand-over and G's clocks), R2 and
R3 add C and D, R4 adds F; a cell outside its round is *not applicable*, never a fault."""

BARS = [
    # A -- mapping the founder's words to Keel's questions
    ("A.same_meaning", ">=", 95.0, "same-meaning rewords (and as written) mapped right"),
    ("A.options_own_words", ">=", 95.0, "options in the founder's own words mapped right"),
    ("A.meaning_changed", ">=", 90.0, "meaning changed caught"),
    ("A.precision", ">=", 95.0, "a real Keel question never filed as a follow-up, a note or nothing"),
    # B -- the answer read against Keel's options (quiet room)
    ("B.offered", ">=", 100.0, "closed answers right when the options were offered"),
    ("B.not_offered", ">=", 90.0, "closed answers right when they were not"),
    ("B.confident_wrong", "<=", 2.0, "answers read sure and wrong"),
    # C -- follow-ups tagged
    ("C.tagged", ">=", 90.0, "follow-ups tagged to the right question"),
    ("C.boundaries", ">=", 85.0, "follow-up stretches with the right boundaries"),
    # D -- following the founder
    ("D.false_move", "<=", 2.0, "false moves per question"),
    ("D.keys", "<=", 33.4, "keys per question (one per three)"),
    ("D.behind_s", "<=", 2.0, "seconds behind the founder's move (median)"),
    # E -- hand-over when unsure
    ("E.unsure", "<=", 10.0, "answers called unsure"),
    ("E.honest", ">=", 80.0, "unsure calls that were truly unclear"),
    # F -- the limits (R4)
    ("F.late_mapping", ">=", 95.0, "questions mapped right after 30 minutes"),
    ("F.limits", ">=", 100.0, "the pause shown where the envelope says"),
    # G -- time to match
    ("G.question_s", "<=", 1.5, "question recognised, median seconds after the founder stops"),
    ("G.answer_s", "<=", 2.0, "answer shown, median seconds after the respondent stops"),
    ("G.worst_s", "<=", 4.0, "worst of either clock"),
]

ROUND_CELLS = {
    1: ("A", "B", "E", "G"),
    2: ("A", "B", "C", "D", "E", "G"),
    3: ("A", "B", "C", "D", "E", "G"),
    4: ("A", "B", "C", "D", "E", "F", "G"),
}

BARS_DATE = "2026-11-10"
