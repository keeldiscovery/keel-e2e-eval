# Spec 061 -- The sample project keeps its people's names (060 FR-2 amended)

The founder, 2026-10-22, on the home page's sample: *"Instead of using Person 1-11 can we use real looking names."*
The twenty respondents of S-006 (05-paidly) are the corpus entry's scripted, fictional people -- Nadia Petrova, Omar
Farouk, Petra Novak, Quentin Roux, Rosa Alvarez, Sven Larsen, Talia Ben-David, Umar Siddiqui, Vera Kowalski, Wen
Zhang, Xavier Dubois, Yara Haddad (the translators) and Kate Alder, Mo Birch, Sara Cedar, Tariq Dune, Uma Elm, Viktor
Fern, Wanda Gorse, Yusuf Hazel (the agencies). Spec 060 FR-2 replaced them with *Person 1* … *Person 20* because the
landing design's §18.8 said *names withheld*, written when the sample was imagined as a real founder's project. For
scripted people there is nothing to protect; the guide's own example report already shows these same names; the sample
bar says the project was played by Keel's own test run; and the landing FAQ promises the report shows *"each person's
name as you gave it"*, which the sample then demonstrates instead of contradicting. Design of record:
`keel-cloud-docs/canon/designs/landing-page-design.md` §18.11 (the operator adds the dated note). **Scope:
keel-e2e-eval only (`evals/sample_export.py`, its tests); keel-web's matching fixture change is keel-web spec 092 FR-1,
built separately. Build lean: one `make unit`, one `make sample` run, the snapshot handed back (the operator commits it
in keel-web).**

## Rules

- **FR-1 Names kept.** `sample_export` no longer replaces any person's name: `personName` in every file and a pilot
  person's `name` in `standings.json` are written as the founder API served them. Everything else 060 FR-2 withholds
  still is: emails removed, the founder's own name and email removed from every file, invitation tokens and links
  written as `withheld`. The *Person n* aliasing code and its ordering go; no flag, no option.
- **FR-2 The survivors grep.** The refusal (060 FR-2's "nothing survives") keeps checking emails, the founder's name
  and email, and tokens, and stops checking the people's names. A unit test asserts every one of the entry's twenty
  names IS present in the output, and that no email, founder name or token is.
- **FR-3 Nothing else moves.** FR-1's file set, FR-3's verdict gate, FR-4's manifest and `make sample`, FR-5 (no mark,
  step or version moved) are unchanged. 060's tests are edited one for one, not deleted; the fixture
  `tests/fixtures/sample/s006-reads.json` is unchanged.
- **FR-4 Notes.** `evals/sample_export.py`'s docstring and `specs/060-sample-project/spec.md` FR-2 get a dated
  *superseded by 061* line; `specs/060-sample-project/tasks.md` is not rewritten.

## Acceptance

1. `make unit` green; the withholding test now asserts the names survive and the rest does not.
2. `make sample` green on the local stack (the checkout `stack.toml` names; the export lands in keel-web's
   `public/sample/` as 060 wrote it). Hand back: the run's directory, the manifest's `exportedAt` and `cloud`, the
   decision label, pilot count and price line, and `grep -c "Nadia Petrova" public/sample/people.json` ≥ 1 and
   `grep -c "Person 1\"" public/sample/people.json` = 0. **Do not commit anything in keel-web**; the operator does,
   together with spec 092.
3. No mark or version moved (060 FR-5 still holds).
