"""The spoken-answer cases (spec 048 FR-3; re-copied by spec 049 FR-1 / FR-8), copied whole from keel-cloud
canon/designs/spoken-classifier-check-2026-10-16/cases.py at keel-cloud-docs d2f00d4 (the file is unchanged since
e20d8aa, spec 100: 18 `readaloud` cases, 170 in all; the canon keeps the record, this repository owns the copy from now
on). Read by harness/classifier_guard.py. The original docstring follows.
"""

"""The spoken-answer check: what people say aloud against one closed question each, with the answer a careful human
would record. Labels are the real generated shapes (the web fixtures: payroll, b2b, practitioner). Expected forms:
  {"picks":[n..]}  option numbers (1-based), order-free; {"escape":True}; {"value":v,"unit":"HOURS"|"AMOUNT"};
  {"unclear":True}; {"agree":True}; several allowed answers as a list under "any".
"""

ITEMS = {
    "gate": {"kind": "gate", "options": ["Yes", "No"], "escape": None},
    "days": {"kind": "number", "options": [], "escape": "I can't recall", "range": [0, 30]},
    "importance": {"kind": "multi", "pick": 2, "escape": "None of these", "options": [
        "Catching errors before the payroll is approved", "Chasing missing timesheets", "Explaining payslips to staff",
        "Keeping up with tax changes", "Reconciling payroll with the ledger"]},
    "better": {"kind": "single", "escape": "I can't tell", "options": [
        "It would have made things better", "No difference", "It would have made things worse"]},
    "benefits": {"kind": "multi", "pick": 0, "escape": None, "options": [
        "Catching errors before the payroll is approved", "Less time checking the register line by line", "Less worry on approval day"]},
    "twoBenefits": {"kind": "multi", "pick": 0, "escape": None, "options": [
        "Catching errors before the payroll is approved", "Less time checking the register line by line"]},
    "cost": {"kind": "amount_or_hours", "options": [], "escape": "I can't recall"},
    "budget": {"kind": "single", "escape": "I don't know", "options": [
        "A budget line we already had", "A new budget line someone signed off", "There was no budget for it"]},
    "approval": {"kind": "single", "escape": "I can't recall", "options": [
        "Yes, and it took a long time", "Yes, but it was quick", "No, I decided on my own", "Someone else decided, not me"]},
    "effort": {"kind": "single", "escape": "I can't recall", "options": [
        "Caught everything, but it took a lot of effort", "Caught everything, with a little extra effort",
        "Got it right after one wrong guess", "It took a few tries to find it"]},
    "taxrules": {"kind": "multi", "pick": 2, "escape": "None of these", "options": [
        "Keeping tax and deduction rules up to date", "Working out holiday pay for part-timers",
        "Correcting a payslip after it has gone out", "Answering staff questions about their deductions",
        "Getting the year-end filing right first time"]},
}

P = lambda *n: {"picks": sorted(n)}
E = {"escape": True}
U = {"unclear": True}
H = lambda v: {"value": v, "unit": "HOURS"}
A = lambda v, c="USD": {"value": v, "unit": "AMOUNT", "currency": c}
def ANY(*xs): return {"any": list(xs)}

# (group, item, said, expected, previous_pick_or_None)
CASES = [
    # --- yes or no ---
    ("gate", "gate", "yeah I did", P(1)), ("gate", "gate", "yes", P(1)), ("gate", "gate", "no, never", P(2)),
    ("gate", "gate", "nope", P(2)), ("gate", "gate", "I didn't", P(2)), ("gate", "gate", "yes... no, actually no", P(2)),
    ("gate", "gate", "no wait, yes", P(1)), ("gate", "gate", "yeah I mean kind of, yes", P(1)),
    ("gate", "gate", "not really", P(2)), ("gate", "gate", "I think so", P(1)),
    ("gate", "gate", "hmm what do you mean", U), ("gate", "gate", "the weather was nice", U),
    ("gate", "gate", "sí", P(1)),
    # --- a number 0..30 ---
    ("number", "days", "about three, maybe four", ANY({"value": 3}, {"value": 4})), ("number", "days", "12", {"value": 12}),
    ("number", "days", "twenty five days", {"value": 25}), ("number", "days", "thirty", {"value": 30}),
    ("number", "days", "31", U), ("number", "days", "thirty-one", U),
    ("number", "days", "yesterday", {"value": 1}), ("number", "days", "last week", ANY({"value": 7}, {"value": 5}, {"value": 6})),
    ("number", "days", "a couple of weeks ago", {"value": 14}), ("number", "days", "about a month ago", {"value": 30}),
    ("number", "days", "I don't remember", E), ("number", "days", "I can't recall", E), ("number", "days", "quite a lot", U),
    ("number", "days", "three days, no wait, five", {"value": 5}), ("number", "days", "hace dos días", {"value": 2}),
    ("number", "days", "earlier today", {"value": 0}),
    # --- pick two of five (payroll importance) ---
    ("pick2", "importance", "the timesheets one and the tax changes", P(2, 4)),
    ("pick2", "importance", "the second and the fourth", P(2, 4)),
    ("pick2", "importance", "timesheets, payslips and the ledger", ANY(P(2, 3), U)),
    ("pick2", "importance", "none of these really", E),
    ("pick2", "importance", "chasing the missing timesheets", P(2)),
    ("pick2", "importance", "payroll errors", P(1)), ("pick2", "importance", "errors", P(1)),
    ("pick2", "importance", "the tax one", P(4)), ("pick2", "importance", "tax", P(4)),
    ("pick2", "importance", "time sheets", P(2)), ("pick2", "importance", "catching arrows before payroll", P(1)),
    ("pick2", "importance", "payroll", U),
    ("pick2", "importance", "the ledger thing and explaining pay slips", P(3, 5)),
    ("pick2", "importance", "the first one wait actually the third", P(3)),
    ("pick2", "importance", "option 4 instead of 3", P(4)), ("pick2", "importance", "not the second, the fourth", P(4)),
    ("pick2", "importance", "the tax one... no sorry the timesheets", P(2)),
    ("pick2", "importance", "uh the the uh payslip one and um keeping up with the tax stuff", P(3, 4)),
    ("pick2", "importance", "reconciling with the ledger I guess, and chasing people for timesheets", P(2, 5)),
    ("pick2", "importance", "honestly all of them are a pain", U),
    ("pick2", "importance", "the first and the second, that's my answer", P(1, 2)),
    # --- pick two of five, longer labels ---
    ("pick2", "taxrules", "holiday pay", P(2)), ("pick2", "taxrules", "the year end one and the deductions questions", P(4, 5)),
    ("pick2", "taxrules", "fixing payslips after they've gone out", P(3)),
    ("pick2", "taxrules", "deductions", U), ("pick2", "taxrules", "keeping the rules up to date and the filing", P(1, 5)),
    ("pick2", "taxrules", "part timers and corrections", P(2, 3)),
    ("pick2", "taxrules", "the last two", P(4, 5)),
    # --- one of three ---
    ("single", "better", "it would have made things better", P(1)), ("single", "better", "no difference", P(2)),
    ("single", "better", "the first one", P(1)), ("single", "better", "the last one", P(3)), ("single", "better", "option two", P(2)),
    ("single", "better", "honestly I can't tell", E), ("single", "better", "purple elephants", U),
    ("single", "better", "it would've helped a lot", P(1)), ("single", "better", "wouldn't change anything", P(2)),
    ("single", "better", "honestly it'd make it harder", P(3)), ("single", "better", "better I think... actually no difference", P(2)),
    ("single", "better", "probably better, yeah", P(1)), ("single", "better", "worse, definitely", P(3)),
    ("single", "better", "hmm let me think", U), ("single", "better", "what were the options again", U),
    ("single", "better", "mejor", P(1)),
    # --- any number of three ---
    ("multi", "benefits", "all of them", P(1, 2, 3)), ("multi", "twoBenefits", "both", P(1, 2)),
    ("multi", "benefits", "the first and the last", P(1, 3)), ("multi", "benefits", "less worry mostly", P(3)),
    ("multi", "benefits", "catching the errors, and less time on the register", P(1, 2)),
    ("multi", "benefits", "none", U), ("multi", "benefits", "the second one, the line by line one", P(2)),
    ("multi", "benefits", "all except the last", P(1, 2)),
    # --- an amount or hours ---
    ("cost", "cost", "$200", A(200)), ("cost", "cost", "two hundred dollars", A(200)), ("cost", "cost", "about 1,500 pounds", A(1500, "GBP")),
    ("cost", "cost", "5k dollars", A(5000)), ("cost", "cost", "three hours", H(3)), ("cost", "cost", "half a day", H(4)),
    ("cost", "cost", "a day", H(8)), ("cost", "cost", "two and a half hours", H(2.5)), ("cost", "cost", "90 minutes", H(1.5)),
    ("cost", "cost", "two days", H(16)), ("cost", "cost", "two hundred", U), ("cost", "cost", "10 kilometres per hour", U),
    ("cost", "cost", "40 percent", U), ("cost", "cost", "around 1000 hours thousand dollars", U), ("cost", "cost", "I can't recall", E),
    ("cost", "cost", "200 bucks", A(200)), ("cost", "cost", "about 3 hours", H(3)), ("cost", "cost", "a couple of hundred dollars", A(200)),
    ("cost", "cost", "maybe 50 quid a month", A(50, "GBP")), ("cost", "cost", "roughly a grand", ANY(A(1000), A(1000, "GBP"), U)),
    ("cost", "cost", "an afternoon", ANY(H(4), H(3), H(5))), ("cost", "cost", "the whole morning", ANY(H(4), H(3), H(5))),
    ("cost", "cost", "two hundred dollars, three hours", U), ("cost", "cost", "unos doscientos dólares", A(200)),
    ("cost", "cost", "a day and a half", H(12)), ("cost", "cost", "it cost us about five hundred", ANY(A(500), U)),
    ("cost", "cost", "three euros fifty", A(3.5, "EUR")), ("cost", "cost", "fifteen minutes", H(0.25)),
    # --- one of three, long labels (budget) ---
    ("long", "budget", "the first one", P(1)), ("long", "budget", "we already had it in the budget", P(1)),
    ("long", "budget", "new line, someone had to sign it off", P(2)), ("long", "budget", "there was none", P(3)),
    ("long", "budget", "no budget", P(3)), ("long", "budget", "existing", P(1)),
    ("long", "budget", "we had to get a new one approved", P(2)), ("long", "budget", "signed off", P(2)),
    ("long", "budget", "budget", U), ("long", "budget", "I don't know", E),
    # --- one of four, long labels (approval) ---
    ("long", "approval", "it took forever", P(1)), ("long", "approval", "yes quick", P(2)), ("long", "approval", "I just decided", P(3)),
    ("long", "approval", "my boss decided", P(4)), ("long", "approval", "yeah they had to agree but it was fast", P(2)),
    ("long", "approval", "yes", U), ("long", "approval", "no", U),
    ("long", "approval", "yes, and it took a long time", P(1)),
    # --- one of four, nine-word labels (effort) ---
    ("long", "effort", "caught everything but a lot of effort", P(1)), ("long", "effort", "caught it all, little extra", P(2)),
    ("long", "effort", "one wrong guess then got it", P(3)), ("long", "effort", "few tries", P(4)),
    ("long", "effort", "got it eventually after trying a few things", P(4)), ("long", "effort", "effort", U),
    ("long", "effort", "a lot of effort", P(1)), ("long", "effort", "caught everything", U),
    ("long", "effort", "the third", P(3)), ("long", "effort", "it took a few tries to find it", P(4)),
    # --- they read the question or the options aloud first, then answer (spec 100, the founder's try of 2026-10-16) ---
    ("readaloud", "better", "Did it make things better, no difference, or worse? Hmm. It would have made things better.", P(1)),
    ("readaloud", "better", "better, no difference, worse... hmm... no difference, I'd say", P(2)),
    ("readaloud", "better", "better or worse... hmm", U),
    ("readaloud", "better", "it would have made things better, no difference, it would have made things worse... worse. Actually no, no difference.", P(2)),
    ("readaloud", "gate", "did I, yes or no... um, no, I didn't", P(2)),
    ("readaloud", "gate", "yes or no... hmm, yes or no", U),
    ("readaloud", "approval", "Yes and it took a long time, yes but quick, no... someone else decided, not me.", P(4)),
    ("readaloud", "approval", "did anyone have to approve it... um... yes, but it was quick", P(2)),
    ("readaloud", "effort", "caught everything with a lot of effort, or with a little extra... a little extra effort, yeah", P(2)),
    ("readaloud", "effort", "caught everything with a lot of effort, or a little extra, or a few tries... hmm", U),
    ("readaloud", "importance", "catching errors, chasing timesheets, explaining payslips, tax changes, the ledger... OK, the timesheets and the tax changes", P(2, 4)),
    ("readaloud", "importance", "which two matter most... um, keeping up with tax changes, and, uh, reconciling with the ledger", P(4, 5)),
    ("readaloud", "benefits", "catching errors, less time on the register, less worry... the less worry one, mostly", P(3)),
    ("readaloud", "cost", "how much did it cost, money or hours... about three hours, I think", H(3)),
    ("readaloud", "cost", "money or hours... hmm", U),
    ("readaloud", "days", "how many days ago... um, five? No, about a week ago.", {"value": 7}),
    ("readaloud", "budget", "a budget line we already had, a new one someone signed off, or no budget... it was a new one, someone signed it off", P(2)),
    ("readaloud", "budget", "an existing budget line, or a new one, or none at all, hmm", U),
]

# confirmation turns: (item, previous pick numbers, said, expected)
CONFIRM = [
    ("importance", [4], "yes", {"agree": True}), ("importance", [4], "yep that's right", {"agree": True}),
    ("importance", [4], "correct", {"agree": True}), ("better", [1], "yeah", {"agree": True}),
    ("importance", [4], "no", U), ("importance", [4], "no, the second", P(2)),
    ("importance", [4], "actually the timesheets one", P(2)), ("better", [1], "yeah... no, the other one", U),
    ("importance", [4], "hmm", U), ("better", [1], "no, no difference", P(2)),
    ("importance", [2, 4], "yes but swap the tax one for the ledger", P(2, 5)),
    ("approval", [2], "no it took ages", P(1)), ("effort", [3], "that's right", {"agree": True}),
    ("gate", [1], "no", P(2)), ("days", None, "no, five", {"value": 5}),
]
