# Spec 134 FR-4 -- the corpus review: every gallery row held to its card

The fourteen gallery entries (`instructions/gallery_names.toml`: 08-fresco to 21-codyco) read row by row against the
cards in `quality/readers/dimensions.md`, on keel-cloud-docs master `c456c0b3` (`canon/designs/measured-beliefs/backtest/
<entry>.yaml`, **revision 23**). Built 2026-11-04 (ET) on branch `spec-134`. **A review only** (the coordinator's
correction of 2026-11-04): nothing in keel-cloud-docs is edited and no eval fixture or pin moves on this branch; a
keel-cloud spec applies Table 1 to the YAMLs and bumps the revision, and the coordinator moves Table 2's quotes when
that lands.

## How to read it

- **Field** is the YAML path under the entry: `founder_calibration.<key>.answer.items[<i>]` (`code`), its `label`, and
  where the row carries one its `asked` clause. A row that fits its card is not listed; every other word of the entry
  stays. The founder's voice is kept; the readers' `instead` notes of cycle 11 (`quality/scores/*/20261104-*-e485abe-*`)
  were the starting point where they hold.
- **Codes stay** (each row keeps its `code`), so every person's recorded `picks` still point at the same row; each
  reworded Importance rival keeps the aim the people who pick it describe in their stories (every code of the fourteen is
  picked by someone). Where a row is dropped or split, the change to `items`, `picked` and the `respondent_questions`
  codes is said in the row.
- The `belief_sentence` / `belief_phrase` beside a list that quotes a reworded row is re-derived by the cloud's own rule
  (`BeliefSentence`) when the YAML moves -- listed under *Beliefs that quote a moved row* below, not reworded here.
- Rules, by the short name used in the table:

| Rule | The card's words |
|---|---|
| `imp-moment` | Importance: each other row a difficulty these same people meet themselves, in their own part of the work, at that moment -- never another role's, setting's or channel's |
| `imp-cause` | Importance: no two overlap, none a part or a cause of another; never a cause or cost as a row (pitfall *too few linemen*) |
| `imp-backwards` | Importance: never a bad outcome that reads backwards after *made easier*, never a wish (pitfall *losing the thread*) |
| `imp-own` | Importance: the own item is the founder's problem whole -- never the circumstance said again |
| `imp-one` | Importance (stranger's options): one thing, no list inside |
| `cs-measure` | Current solution: one measure -- every rung a step on the one scale of the cost the Answer names, never a stand-in (when the log was finished, yield alone) or a method |
| `cs-joined` | Current solution: no rung joins two states with *and* or *or* |
| `cs-working` | Current solution: the first rung is today's way getting the job done |
| `cs-fail` | Current solution: the last rung is today's way failing outright (it never got done) |
| `cmp-subject` | Compatibility: a verb phrase with no subject of its own (reads whole after *Most {actor_plural}*; pitfall: the doubled subject) |
| `cmp-settled` | Compatibility: none already true of everyone the study is about, by the founder's segment or the usual way of doing the job |
| `cmp-core` | Compatibility: the step the idea depends on most never missing |
| `cmp-one` | Compatibility: one whole act with one thing to weigh (two things joined are two conditions) |
| `cmp-clipped` | Compatibility pitfall: qualifiers dropped (*two days* for *one to two business days*) |
| `ra-one` | Relative advantage: one benefit a row, a noun phrase (pitfall: rows bundling two gains) |
| `af-one` | Adoption friction: each row one effort |
| `af-self` | Adoption friction: a step these people take themselves -- never another role's sign-off or a permission |
| `af-ground` | Adoption friction: none a condition another screen already tests (fitting what they use now is Compatibility, getting it bought Purchase friction) |
| `pf-offer` | Purchase friction: never the founder's own offer, pitch, trial, pilot, guarantee or onboarding |
| `pf-object` | Purchase friction: a noun phrase of at most 9 words with its object (*a security review of an agent on every node*) |
| `pf-purchase` | Purchase friction: a step between wanting it and buying it, never the purchase itself (*a signed contract*) |
| `pf-overlap` | Purchase friction: no step containing or repeating another |

## Table 1 -- the rows that break a card rule (128)

| Entry | Dimension | Field in the yaml | Before | After | Rule |
|---|---|---|---|---|---|
| 08-fresco | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`schedule`) | Keeping the job on schedule | Planning tomorrow's work and crews | `imp-moment` |
| 08-fresco | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`subs`) | Getting subs to show up and finish | Lining up subs to show up tomorrow | `imp-moment`, `imp-cause` |
| 08-fresco | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`safety`) | Keeping the site safe | Following up on safety issues from the walk | `imp-moment` |
| 08-fresco | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Log done on site | Done on site, no time after the walk | `cs-measure` |
| 08-fresco | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Finished at home or the next morning | Took the rest of the evening | `cs-joined`, `cs-measure` |
| 08-fresco | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Never got written up properly | Never got written up that day | `cs-fail`, `cs-measure` |
| 08-fresco | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`job_on_procore`) | The job kept its logs in Procore or ACC | could stop to film and talk on the walk {asked: could you have stopped for a few seconds to film and talk on that walk} | `cmp-settled`, `cmp-core`, `cmp-subject` |
| 08-fresco | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[0]` (`trial_live_job`) | A trial on one live job | *(dropped)* -- the pick moves to `procore_check` (the walk already sends that, `vectors_script.kept_picked`), the founder's 2 weeks kept; `items` 3 -> 2 | `pf-offer` |
| 08-fresco | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[2]` (`security_review`) | A security review | A security review of the site videos | `pf-object` |
| 09-karsa | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`bills`) | Keeping up with rising bills | Deciding how much to keep back for bills | `imp-moment` |
| 09-karsa | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`income`) | Earning more each month | Getting the leftover rupees to earn something | `imp-moment`, `imp-backwards` |
| 09-karsa | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`abroad`) | Paying for things abroad | Getting dollars together for a payment abroad | `imp-moment` |
| 09-karsa | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Bought dollars at a fair rate, no hassle | Bought dollars at the fair rate | `cs-joined`, `cs-measure` |
| 09-karsa | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Got some after trying several places | Paid well over the rate | `cs-measure` |
| 09-karsa | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Paid a big premium or took a risk | Paid a big premium on every dollar | `cs-joined` |
| 09-karsa | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Could not get dollars and kept rupees | Could not get any dollars | `cs-joined` |
| 09-karsa | Adoption friction | adoption_friction steps: `founder_calibration.solution.adoption_friction.answer.items[1]` (`upload_proof`) | Upload an ID card and a photo of payment | Upload a photo of each payment {asked: you'd upload a photo of each payment you make} | `af-one`, `af-ground` |
| 10-palus | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Earned a good rate with no effort | Earned a market rate after fees | `cs-joined`, `cs-measure` |
| 10-palus | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Earned a fair rate, a little upkeep | Earned a bit under market after fees | `cs-joined`, `cs-measure` |
| 10-palus | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Earned a low rate, never revisited | Earned well under market after fees | `cs-joined`, `cs-measure` |
| 10-palus | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Earned little after fees and effort | Earned next to nothing after fees | `cs-joined`, `cs-measure` |
| 10-palus | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`plaid_link`) | Their bank could link through Plaid | could keep their current bank while the reserve sat elsewhere {asked: could your company have kept its current bank while its long-term reserve sat with another provider} | `cmp-settled`, `cmp-core`, `cmp-subject` |
| 10-palus | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`wait_two_days`) | They could wait two days for their cash | could wait one to two business days for their cash | `cmp-clipped` |
| 10-palus | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`bonds_allowed`) | Their policy allowed bonds beyond Treasuries | had a cash policy that allowed bonds beyond Treasuries | `cmp-subject` |
| 10-palus | Relative advantage | relative_advantage benefits: `founder_calibration.solution.relative_advantage.answer.items[0]` (`less_help_needed`) | Higher yield without hiring for treasury | Higher yield on cash not needed for months + No treasury hire to manage it (two rows) | `ra-one` |
| 10-palus | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[2]` (`tax_advice`) | A tax adviser's sign-off | A tax adviser's sign-off on the bonds | `pf-object` |
| 11-issen | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`study_time`) | Finding time to study at all | Fitting a practice session into the day | `imp-moment`, `imp-cause` |
| 11-issen | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Spoke as much as needed, easily | Spoke as much as they needed | `cs-joined` |
| 11-issen | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Spoke a little; costly or hard to book | Spoke only a little | `cs-joined`, `cs-measure` |
| 11-issen | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Barely spoke; practised alone instead | Barely spoke a word | `cs-joined`, `cs-measure` |
| 11-issen | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Found nobody to speak with | Did not speak at all | `cs-measure`, `cs-fail` |
| 11-issen | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`simple_conversation`) | They could already hold a simple conversation | could set aside time for a spoken practice session {asked: could you have set aside time for a spoken practice session that day}; the pick moves to speak_aloud | `cmp-settled` |
| 11-issen | Relative advantage | relative_advantage benefits: `founder_calibration.solution.relative_advantage.answer.items[0]` (`less_help_needed`) | Speaking practice any time, no tutor to book | Speaking practice any time + No tutor to book (two rows) | `ra-one` |
| 12-transload | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`short_staffed`) | Running the shift short-staffed | Covering the doors with the crew on hand | `imp-cause` |
| 12-transload | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`damaged_freight`) | Handling damaged freight and claims | Handling damaged freight on the dock | `imp-moment`, `imp-one` |
| 12-transload | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Measured only the ones that looked wrong | Only a handful got measured | `cs-measure` |
| 12-transload | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Nothing measured; the paperwork was taken | Nothing got measured | `cs-joined` |
| 12-transload | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`cameras_cover_doors`) | Cameras already covered the doors where freight was scanned | had cameras already covering the doors where freight was scanned | `cmp-subject` |
| 12-transload | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`every_unit_scanned`) | Every handling unit was scanned as it moved | scanned every handling unit as it crossed the dock | `cmp-subject` |
| 12-transload | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`footage_shared`) | The footage could be shared with an outside firm | could share camera footage with an outside firm | `cmp-subject` |
| 12-transload | Adoption friction | adoption_friction steps: `founder_calibration.solution.adoption_friction.answer.items[1]` (`cameras_measure`) | Let the dock cameras be used to measure | Keep the door cameras clear and in place {asked: you'd keep the cameras over your doors clear and in place} | `af-self`, `af-ground` |
| 12-transload | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[1]` (`head_office_contract`) | A contract signed by head office | A legal review of using the camera footage | `pf-purchase` |
| 13-aircaps | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`phone_calls`) | Following phone and video calls | Lipreading when people turn away | `imp-moment` |
| 13-aircaps | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`listening_fatigue`) | Not being worn out by listening | Staying fresh enough to keep listening | `imp-backwards` |
| 13-aircaps | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`announcements`) | Catching announcements in shops and stations | Knowing who is talking in a group | `imp-moment` |
| 13-aircaps | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Missed a little, caught up quickly | Missed only a little | `cs-joined` |
| 13-aircaps | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Caught the gist, missed the details | Caught only the gist | `cs-joined` |
| 13-aircaps | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Lost the thread and mostly nodded along | Missed most of it | `cs-joined` |
| 13-aircaps | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`phone_online`) | Their phone was with them and online | had their phone with them {asked: was your phone with you} + had their phone online {asked: was your phone connected to the internet} (two rows; the pick stays on the first) | `cmp-one`, `cmp-subject` |
| 13-aircaps | Relative advantage | relative_advantage benefits: `founder_calibration.solution.relative_advantage.answer.items[0]` (`less_help_needed`) | Following more without asking anyone to repeat | More of the talk followed without asking for repeats | `ra-one` |
| 13-aircaps | Adoption friction | adoption_friction steps: `founder_calibration.solution.adoption_friction.answer.items[0]` (`wear_paired`) | Wear the glasses, paired to the phone | Wear the caption glasses in conversations {asked: you'd wear the caption glasses in your conversations} | `af-one`, `af-ground` |
| 14-code-four | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`response_times`) | Getting to calls without a long wait | Getting back on the road for the next call | `imp-moment` |
| 14-code-four | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`short_staffed`) | Covering shifts with too few officers | Taking extra calls when the shift is short | `imp-cause` |
| 14-code-four | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`court_prep`) | Getting ready for court dates | Pulling evidence for an upcoming court date | `imp-moment` |
| 14-code-four | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`training`) | Keeping up with required training | Logging the evidence from the call | `imp-moment` |
| 14-code-four | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Left for the next shift with details fading | Left for the next shift | `cs-joined` |
| 14-code-four | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Still not written; the reports keep piling up | Still not written days later | `cs-joined` |
| 14-code-four | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`footage_uploaded`) | The footage was uploaded before the shift ended | had the call's footage uploaded before the shift ended | `cmp-subject` |
| 14-code-four | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`records_typed`) | The report was typed into the records system | could paste a drafted report into the records system {asked: could you have pasted a drafted report into your department's records system} | `cmp-settled`, `cmp-subject` |
| 14-code-four | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`time_to_review`) | There was time to read a draft closely | had time to read a draft closely | `cmp-subject` |
| 14-code-four | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[0]` (`side_by_side_trial`) | A side-by-side trial against Axon's tool | The department's own comparison against Axon's tool | `pf-offer` |
| 15-voltair | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`storm_restoration`) | Getting the power back on after storms | Getting pulled off patrol for storm work | `imp-moment` |
| 15-voltair | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`trouble_calls`) | Answering outage and trouble calls | Answering trouble calls while on patrol | `imp-moment`, `imp-one` |
| 15-voltair | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`crew_short`) | Covering the work with too few linemen | Splitting the circuit among the crew on hand | `imp-cause` |
| 15-voltair | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`vegetation`) | Keeping trees clear of the lines | Spotting trees growing into the lines | `imp-moment` |
| 15-voltair | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Checked from the truck with binoculars only | Many checked only from a distance | `cs-measure` |
| 15-voltair | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`tops_visible`) | The pole tops could be seen from above | had poles whose tops were clear of tree cover | `cmp-subject` |
| 15-voltair | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`pad_site`) | There was a spot for a charging pad | had a pole or substation on the route for a charging pad | `cmp-subject` |
| 15-voltair | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`work_orders`) | Findings went into the work order system | put their findings into the work order system | `cmp-subject` |
| 16-pairio | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`planned_work`) | Keeping up with planned maintenance | Juggling planned work around the breakdown | `imp-moment` |
| 16-pairio | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`short_handed`) | Covering the shift with too few technicians | Covering other machines during the breakdown | `imp-cause` |
| 16-pairio | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Found the fix fast and logged it properly | Found the fix fast | `cs-joined`, `cs-measure` |
| 16-pairio | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Found it, logged a line or two | Found it after a short search | `cs-joined`, `cs-measure` |
| 16-pairio | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Hunted through manuals, logged almost nothing | Hunted through the manuals for hours | `cs-joined`, `cs-measure` |
| 16-pairio | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Trial and error while the line stayed down | Never found the fix that shift | `cs-measure`, `cs-fail` |
| 16-pairio | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`phone_allowed`) | A phone was allowed at the machine | were allowed to use a phone at the machine | `cmp-subject` |
| 16-pairio | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`manuals_as_files`) | The machine's manuals existed as files | had the machine's manuals as files, not only paper | `cmp-subject` |
| 16-pairio | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`quiet_enough`) | It was quiet enough to speak to a phone | could speak into a phone over the machine noise | `cmp-subject` |
| 16-pairio | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[1]` (`it_security_review`) | An IT security review | An IT security review of the app | `pf-object` |
| 17-expanse | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[0]` (`sizing_jobs`) | Guessing memory, GPUs and run time before submitting | Sizing a job to neither fail nor waste GPUs | `imp-own` |
| 17-expanse | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`allocation_hours`) | Running out of the group's allocation | Keeping within the group's GPU-hour allocation | `imp-backwards`, `imp-cause` |
| 17-expanse | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Sized from past runs; it ran as planned | Ran first time, sized about right | `cs-joined`, `cs-measure` |
| 17-expanse | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Padded it a little; it ran, a little idle | Ran, holding about twice what it used | `cs-joined`, `cs-measure` |
| 17-expanse | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Doubled everything to be safe; much sat idle | Ran, holding three times what it used | `cs-joined`, `cs-measure` |
| 17-expanse | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Guessed low; it died and was resubmitted | Failed partway and had to be resubmitted | `cs-joined`, `cs-measure` |
| 17-expanse | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Copied an old script and hoped | Never ran to the end | `cs-fail`, `cs-measure` |
| 17-expanse | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`usual_scheduler`) | The job went through SLURM or Kubernetes as usual | could run a monitoring agent on the job's node {asked: could your job have run with a monitoring agent on its node} | `cmp-settled`, `cmp-subject` |
| 17-expanse | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`source_on_cluster`) | The source code sat on the cluster | kept the job's source code on the cluster | `cmp-subject` |
| 17-expanse | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`python_code`) | The job's code was written in Python | wrote the job's code in Python | `cmp-subject` |
| 17-expanse | Relative advantage | relative_advantage benefits: `founder_calibration.solution.relative_advantage.answer.items[0]` (`fewer_attempts`) | The job runs first time, no resubmits | A job that runs to the end first time | `ra-one` |
| 17-expanse | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[1]` (`code_access`) | Letting it read job scripts and source code | *(dropped)* -- folded into *A security review of an agent on every node* (it is a part of that review); `items` 3 -> 2, the pick (0) unmoved | `pf-overlap`, `pf-object` |
| 17-expanse | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[2]` (`department_budget`) | A budget line for the department's pilot | A budget line in the department's plan | `pf-offer` |
| 18-careforce | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`phones`) | Answering the phones and refill requests | Answering refill requests on the phone | `imp-one` |
| 18-careforce | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`list_from_emr`) | The list came straight out of the EMR | got the outreach list straight out of the EMR | `cmp-subject` |
| 18-careforce | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`open_slots`) | There were open slots to book patients into | had open slots to book patients into | `cmp-subject` |
| 18-careforce | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`patients_pick_up`) | Patients picked up calls from unknown numbers | had patients who pick up calls from unknown numbers | `cmp-subject` |
| 18-careforce | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[0]` (`hipaa_review`) | A HIPAA security review | A HIPAA security review of the AI caller | `pf-object` |
| 18-careforce | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[2]` (`board_vote`) | A vote by the board | A board vote on the new service | `pf-object` |
| 19-veles | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`pipeline`) | Keeping enough pipeline to hit quota | Keeping other deals moving meanwhile | `imp-moment` |
| 19-veles | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`forecasting`) | Keeping the CRM and forecast current | Updating the deal in the CRM | `imp-moment`, `imp-one` |
| 19-veles | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`legal_review`) | Getting contracts through the buyer's legal review | Answering the buyer's questions on the quote | `imp-moment` |
| 19-veles | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`procurement`) | Getting through the buyer's procurement process | Filling in the buyer's vendor forms | `imp-moment` |
| 19-veles | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Priced in minutes, approved the first time | Approved within the hour | `cs-joined`, `cs-measure` |
| 19-veles | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Built from the price sheet, one quick approval | Approved the same day | `cs-joined`, `cs-measure` |
| 19-veles | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Rebuilt the spreadsheet and chased an approval | Approved after a few days of chasing | `cs-joined`, `cs-measure` |
| 19-veles | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[3]` (`works_poorly`) | Guessed a discount, fixed the terms afterwards | Approved after a week or more | `cs-joined`, `cs-measure` |
| 19-veles | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[4]` (`no_reliable_way`) | Worked out over email chains, terms unclear | Sent out without an approved price | `cs-joined`, `cs-fail` |
| 19-veles | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`deal_in_crm`) | The deal was already set up in the CRM | had the deal set up in the CRM before pricing | `cmp-subject` |
| 19-veles | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`price_book`) | There was a written price book to follow | had a written price book to follow | `cmp-subject` |
| 19-veles | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`one_tool`) | The quote was built in one tool | built the quote in one tool | `cmp-subject` |
| 20-lemma | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`shipping`) | Shipping new features on schedule | Pausing feature work to chase the failure | `imp-moment` |
| 20-lemma | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[2]` (`model_costs`) | Keeping model and inference costs down | Keeping the fix from raising model costs | `imp-moment`, `imp-one` |
| 20-lemma | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[3]` (`latency`) | Keeping the agent fast enough for users | Keeping the agent fast while fixing it | `imp-moment` |
| 20-lemma | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`hiring`) | Hiring enough engineers | Finding an engineer free to dig in | `imp-moment`, `imp-cause` |
| 20-lemma | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | An alert caught it and we fixed it fast | Caught by an alert within minutes | `cs-joined`, `cs-measure` |
| 20-lemma | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[1]` (`mostly_works`) | Our evals caught it, fixed within the day | Caught by our evals the same day | `cs-joined`, `cs-measure` |
| 20-lemma | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[2]` (`hit_and_miss`) | Found it digging through logs, hours later | Found in the logs hours later | `cs-measure` |
| 20-lemma | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`runs_traced`) | Every run of the agent was already traced | already traced every run of the agent | `cmp-subject` |
| 20-lemma | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`prompts_in_repo`) | The prompts lived in the code repository | kept the prompts in the code repository | `cmp-subject` |
| 20-lemma | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`traces_shareable`) | Traces could be sent to an outside service | could send traces to an outside service | `cmp-subject` |
| 21-codyco | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[1]` (`guest_requests`) | Handling guests' requests at the desk | Handling changes to existing bookings | `imp-moment` |
| 21-codyco | Importance | problem.importance list: `founder_calibration.problem.importance.answer.items[4]` (`check_in_rush`) | Getting through the check-in and check-out rush | Answering guests' questions about their stay | `imp-moment` |
| 21-codyco | Current solution | current_solution rungs: `founder_calibration.problem.current_solution_satisfaction.answer.items[0]` (`works_well`) | Every call answered or called back in minutes | Every booking call answered live | `cs-joined` |
| 21-codyco | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[0]` (`forward_calls`) | Unanswered calls could be forwarded to another number | could forward unanswered calls to another number | `cmp-subject` |
| 21-codyco | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[1]` (`pms_open`) | The PMS took bookings from outside systems | used a PMS that takes bookings from outside systems | `cmp-subject` |
| 21-codyco | Compatibility | compatibility conditions: `founder_calibration.solution.compatibility.answer.items[2]` (`rates_loaded`) | Rates and room types were up to date | had current rates and room types in the PMS | `cmp-subject` |
| 21-codyco | Adoption friction | adoption_friction steps: `founder_calibration.solution.adoption_friction.answer.items[0]` (`ai_answers`) | Let an AI answer guests in the hotel's voice | Hand their missed booking calls to the AI {asked: you'd hand your missed booking calls to an AI that answers in your hotel's name} | `af-self` |
| 21-codyco | Purchase friction | purchase_friction steps: `founder_calibration.commercial.purchase_friction.answer.items[2]` (`one_hotel_trial`) | A trial at one hotel first | *(dropped)* -- the pick (0, the data protection review) unmoved; `items` 3 -> 2 | `pf-offer` |

Rows reworded per entry: 08-fresco 9 · 09-karsa 8 · 10-palus 9 · 11-issen 7 · 12-transload 9 · 13-aircaps 9 · 14-code-four 10 · 15-voltair 8 · 16-pairio 10 · 17-expanse 13 · 18-careforce 6 · 19-veles 12 · 20-lemma 10 · 21-codyco 8.


## Beliefs that quote a moved row

Re-derived by the cloud's rule when the YAML moves (the record's own sentence, never hand-written here):

| Entry | Field | Quotes |
|---|---|---|
| 08-fresco | `founder_calibration.commercial.purchase_friction.belief_sentence` | *A trial on one live job* |
| 10-palus | `founder_calibration.solution.compatibility.belief_sentence` | *They could wait two days for their cash* |
| 10-palus | `founder_calibration.solution.relative_advantage.belief_phrase` | *Higher yield without hiring for treasury* |
| 11-issen | `founder_calibration.solution.compatibility.belief_sentence` | *They could already hold a simple conversation* |
| 11-issen | `founder_calibration.solution.relative_advantage.belief_phrase` | *Speaking practice any time, no tutor to book* |
| 12-transload | `founder_calibration.solution.compatibility.belief_sentence` | *Cameras already covered the doors where freight was scanned* |
| 13-aircaps | `founder_calibration.solution.compatibility.belief_sentence` | *Their phone was with them and online* |
| 13-aircaps | `founder_calibration.solution.relative_advantage.belief_phrase` | *Following more without asking anyone to repeat* |
| 13-aircaps | `founder_calibration.solution.adoption_friction.belief_sentence` | *Wear the glasses, paired to the phone* |
| 14-code-four | `founder_calibration.solution.compatibility.belief_sentence` | *The footage was uploaded before the shift ended* |
| 14-code-four | `founder_calibration.commercial.purchase_friction.belief_sentence` | *A side-by-side trial against Axon's tool* |
| 15-voltair | `founder_calibration.solution.compatibility.belief_sentence` | *The pole tops could be seen from above* |
| 16-pairio | `founder_calibration.solution.compatibility.belief_sentence` | *A phone was allowed at the machine* |
| 17-expanse | `founder_calibration.problem.importance.belief_sentence` | *Guessing memory, GPUs and run time before submitting* |
| 17-expanse | `founder_calibration.solution.compatibility.belief_sentence` | *The source code sat on the cluster* |
| 17-expanse | `founder_calibration.solution.relative_advantage.belief_phrase` | *The job runs first time, no resubmits* |
| 18-careforce | `founder_calibration.solution.compatibility.belief_sentence` | *The list came straight out of the EMR* |
| 18-careforce | `founder_calibration.commercial.purchase_friction.belief_sentence` | *A HIPAA security review* |
| 19-veles | `founder_calibration.solution.compatibility.belief_sentence` | *The deal was already set up in the CRM* |
| 20-lemma | `founder_calibration.solution.compatibility.belief_sentence` | *Every run of the agent was already traced* |
| 21-codyco | `founder_calibration.solution.compatibility.belief_sentence` | *Unanswered calls could be forwarded to another number* |
| 21-codyco | `founder_calibration.solution.adoption_friction.belief_sentence` | *Let an AI answer guests in the hotel's voice* |

## Shape changes beside the rewording

- **Splits (one row becomes two):** 10-palus Relative advantage (1 -> 2 benefits; the second takes a new code, e.g.
  `no_treasury_hire`); 11-issen Relative advantage (1 -> 2, e.g. `no_tutor_to_book`); 13-aircaps Compatibility (3 -> 4
  conditions, e.g. `phone_online` -> `phone_with_them` + `phone_online`, the pick on the first). Relative advantage's
  respondent item is code's four answers, so no `answers[*].picks` moves; Compatibility's pick index stays 0.
- **Rows dropped:** 08-fresco and 21-codyco Purchase friction's own trial (the cloud already leaves it off, L32);
  17-expanse *Letting it read job scripts and source code* (inside the security review). 08-fresco's pick moves to
  the Procore check with the founder's 2 weeks (what the walk sends today).
- **A pick moves:** 11-issen Compatibility, from the segment-settled *simple conversation* (the segment is
  *intermediate level or above*) to *They could speak aloud where they were*, the step the idea depends on most; the
  new first row replaces the settled one.
- **The own trial in 14-code-four and 17-expanse** is reworded into the buyer's own step (*The department's own
  comparison against Axon's tool*, *A budget line in the department's plan*), so L32 no longer fires on them; after
  this review no gallery entry types the founder's own offer (`vectors_script.offer_rows` empty on all fourteen).

## Judged to fit (read and left as they are)

- 08-fresco: *Chasing RFIs and submittals* (one trailer task at that moment); Relative advantage and Adoption friction
  whole (the readers' faults there were Keel's draws, not the rows).
- 09-karsa: Compatibility's *would* rows (a habit the idea must fit, no segment settles them).
- 10-palus: the Importance list (the readers faulted Keel's own row, not the corpus's); Adoption friction's *Move the
  long-term reserve out of the bank's treasury* (the move is the finance lead's own effort; the approval is Purchase
  friction's *Board approval of the cash policy*, already its own row).
- 16-pairio: *Photograph the fault and ask the app first* (one act: asking the app with a photo).
- 18-careforce: Current solution's five rungs (one measure, working first, failure last).
- 21-codyco: *Callers answered when the desk is busy* (a gain apart from the missed calls turned into bookings).
- Every entry's Commitment, Buyer and payer and money rows: outside FR-4's six dimensions.

## Table 2 -- the eval files that quote a moved row (move them when the cloud change lands)

Not changed on this branch: `make unit` stays green against revision 23. *Count* is the number of lines quoting the row
(*A security review* counted only where it is Fresco's bare row, not *... of an agent on every node* or 05-paidly's).
Run records under `tests/fixtures/` (a recorded run's `backtest.json`, `inputs.json`, `export/*.json`, the `runs/`,
typist and cycle fixtures) are what was served on their day; the pins and mirror tests read the corpus.
`quality/readers/dimensions.md` quotes Fresco's *The job kept its logs in Procore or ACC* and Codyco's *Handling guests'
requests at the desk* as its **bad** examples, and `AGENTS.md` quotes rows in its history: those stay as written.

| File | Entry | Row quoted | Count |
|---|---|---|---|
| `AGENTS.md` | 08-fresco | *A trial on one live job* | 1 |
| `AGENTS.md` | 10-palus | *Higher yield without hiring for treasury* | 1 |
| `evals/corpus_scenario.py` | 13-aircaps | *Wear the glasses, paired to the phone* | 1 |
| `evals/corpus_scenario.py` | 16-pairio | *Found it, logged a line or two* | 1 |
| `harness/vectors_script.py` | 08-fresco | *A trial on one live job* | 1 |
| `harness/vectors_script.py` | 08-fresco | *Log done on site* | 1 |
| `harness/vectors_script.py` | 13-aircaps | *Their phone was with them and online* | 1 |
| `harness/vectors_script.py` | 17-expanse | *A budget line for the department's pilot* | 1 |
| `instructions/screen_entries.py` | 10-palus | *Higher yield without hiring for treasury* | 1 |
| `quality/readers/dimensions.md` | 08-fresco | *The job kept its logs in Procore or ACC* | 1 |
| `quality/readers/dimensions.md` | 21-codyco | *Handling guests' requests at the desk* | 1 |
| `tests/fixtures/cycle5/10-palus-solution.json` | 10-palus | *Their bank could link through Plaid* | 1 |
| `tests/fixtures/cycle5/10-palus-solution.json` | 10-palus | *Their policy allowed bonds beyond Treasuries* | 1 |
| `tests/fixtures/cycle5/10-palus-solution.json` | 10-palus | *They could wait two days for their cash* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` | 08-fresco | *Getting subs to show up and finish* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` | 08-fresco | *Keeping the job on schedule* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/backtest.json` | 08-fresco | *Keeping the site safe* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *A security review* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *A trial on one live job* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *Getting subs to show up and finish* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *Keeping the job on schedule* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *Keeping the site safe* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/plan.json` | 08-fresco | *The job kept its logs in Procore or ACC* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *A security review* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *A trial on one live job* | 4 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *Getting subs to show up and finish* | 4 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *Keeping the job on schedule* | 5 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *Keeping the site safe* | 3 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/export/standings.json` | 08-fresco | *The job kept its logs in Procore or ACC* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *A security review* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *A trial on one live job* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Finished at home or the next morning* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Getting subs to show up and finish* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Keeping the job on schedule* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Keeping the site safe* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Log done on site* | 2 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *Never got written up properly* | 1 |
| `tests/fixtures/gallery/20261022T164045Z-backtest-08-fresco/inputs.json` | 08-fresco | *The job kept its logs in Procore or ACC* | 2 |
| `tests/fixtures/gallery/expected-interview-fresco.json` | 08-fresco | *Getting subs to show up and finish* | 2 |
| `tests/fixtures/gallery/expected-interview-fresco.json` | 08-fresco | *Keeping the job on schedule* | 2 |
| `tests/fixtures/gallery/expected-interview-fresco.json` | 08-fresco | *Keeping the site safe* | 2 |
| `tests/fixtures/runs/08-fresco-choose-108/commercial.json` | 08-fresco | *A security review* | 3 |
| `tests/fixtures/runs/08-fresco-choose-108/commercial.json` | 08-fresco | *A trial on one live job* | 2 |
| `tests/fixtures/runs/13-aircaps-choose-108/solution.json` | 13-aircaps | *Their phone was with them and online* | 4 |
| `tests/fixtures/runs/13-aircaps-choose-108/solution.json` | 13-aircaps | *Wear the glasses, paired to the phone* | 2 |
| `tests/fixtures/runs/21-codyco-choose-104/solution.json` | 21-codyco | *Let an AI answer guests in the hotel's voice* | 3 |
| `tests/fixtures/runs/21-codyco-choose-104/solution.json` | 21-codyco | *Rates and room types were up to date* | 2 |
| `tests/fixtures/runs/21-codyco-choose-104/solution.json` | 21-codyco | *The PMS took bookings from outside systems* | 2 |
| `tests/fixtures/runs/21-codyco-choose-104/solution.json` | 21-codyco | *Unanswered calls could be forwarded to another number* | 2 |
| `tests/fixtures/typist/backtest-21-codyco-PROBLEM.json` | 21-codyco | *Every call answered or called back in minutes* | 3 |
| `tests/fixtures/typist/backtest-21-codyco-PROBLEM.json` | 21-codyco | *Getting through the check-in and check-out rush* | 7 |
| `tests/fixtures/typist/backtest-21-codyco-PROBLEM.json` | 21-codyco | *Handling guests' requests at the desk* | 7 |
| `tests/test_adoption_steps_112.py` | 21-codyco | *Let an AI answer guests in the hotel's voice* | 5 |
| `tests/test_advantage_belief_113.py` | 10-palus | *Higher yield without hiring for treasury* | 2 |
| `tests/test_after_130.py` | 21-codyco | *Let an AI answer guests in the hotel's voice* | 1 |
| `tests/test_after_131.py` | 13-aircaps | *Their phone was with them and online* | 1 |
| `tests/test_choose_by_label_104.py` | 21-codyco | *Let an AI answer guests in the hotel's voice* | 2 |
| `tests/test_choose_by_label_104.py` | 21-codyco | *Unanswered calls could be forwarded to another number* | 1 |
| `tests/test_cloud_200_mirror_129.py` | 13-aircaps | *Their phone was with them and online* | 1 |
| `tests/test_cloud_205_208_mirror_132.py` | 08-fresco | *A security review* | 3 |
| `tests/test_cloud_205_208_mirror_132.py` | 08-fresco | *A trial on one live job* | 6 |
| `tests/test_cloud_205_208_mirror_132.py` | 10-palus | *A tax adviser's sign-off* | 1 |
| `tests/test_cloud_205_208_mirror_132.py` | 17-expanse | *A budget line for the department's pilot* | 2 |
| `tests/test_cloud_205_208_mirror_132.py` | 21-codyco | *A trial at one hotel first* | 2 |
| `tests/test_cycle_5_to_the_end_119.py` | 21-codyco | *A trial at one hotel first* | 1 |
| `tests/test_dimension_cards_131.py` | 21-codyco | *Handling guests' requests at the desk* | 1 |
| `tests/test_money_cards_redrawn_118.py` | 08-fresco | *A trial on one live job* | 1 |
| `tests/test_phrase_is_the_peoples_093.py` | 21-codyco | *Let an AI answer guests in the hotel's voice* | 2 |
| `tests/test_reworded_founder_screens_116.py` | 13-aircaps | *Missed a little, caught up quickly* | 1 |
| `tests/test_reworded_row_108.py` | 08-fresco | *A trial on one live job* | 6 |
| `tests/test_reworded_row_108.py` | 13-aircaps | *Their phone was with them and online* | 1 |
| `tests/test_reworded_row_108.py` | 13-aircaps | *Wear the glasses, paired to the phone* | 3 |
| `tests/test_reworded_row_108.py` | 21-codyco | *The PMS took bookings from outside systems* | 1 |
| `tests/test_reworded_row_108.py` | 21-codyco | *Unanswered calls could be forwarded to another number* | 4 |
| `tests/test_seven_templates_115.py` | 08-fresco | *A trial on one live job* | 3 |
| `tests/test_seven_templates_115.py` | 12-transload | *Cameras already covered the doors where freight was scanned* | 1 |
| `tests/test_seven_templates_115.py` | 13-aircaps | *Their phone was with them and online* | 1 |
| `tests/test_seven_templates_115.py` | 17-expanse | *The source code sat on the cluster* | 1 |
| `tests/test_web_164_mirror_129.py` | 21-codyco | *A trial at one hotel first* | 1 |
