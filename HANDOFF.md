# Current handoff - paper-v4: search improvements after the paper-v3 results, 2026-10-28

Request: review Ket_qua_thuc_nghiem_lan_2.docx (paper-v3 results), then "thực hiện các cải thiện
bạn đề xuất ... không chạy thực nghiệm lại". No experiment was run. Uncommitted; no commit/push
authorized. Design and diagnosis: docs/research/EXPERIMENT_DESIGN_DEEPMG.md section 11.

Milestone 2 (2026-10-28, user: "Làm cách A ... thêm khối large theo cách C ... Cách B ... làm cái
này đi"; still no experiment run, still uncommitted):
- Job cap 900 s -> 3,600 s: OptimizationInput.time_limit_s, CampaignSpec.job_time_limit_s,
  feedback/cli.py, frontend ResearchPage.tsx. Worker lease (30 s) is renewed every loop while the
  child runs (workers/runner.py), so long jobs keep their lease; campaign ceiling stays 14,400 s.
- Option C: JointConfig.search_time_s (no new evaluation after it; termination SEARCH_TIME_LIMIT).
- Option B: JointConfig.screen_seeds/screen_margin; coordinator.assess screens on the seed prefix
  against a reference plan (feedback descent state, annealing current, random_search best; kicks
  and init never screened), SCREENED_OUT rejections, budget `spent` in full-evaluation equivalents
  (equals evaluation count without screening), result `budget_spent`/`screened_out`;
  evaluator.evaluate(context_seeds=...) keeps the cache identity so promotion reuses the screened
  seed (tested: T4 hit), evaluator.prefix_score.
- paper-v4 regenerated (old dir moved to var/paper-v4-configs-superseded-20261028): medium budget 40
  at 3,600 s (5 jobs/part), new VL large x3 equal wall time 3,000 s, new V5 screening on medium x10;
  1,269 jobs, order V2 V4 V3 V1 VL V5; 427 treatments validated; large holdout split checked
  (1,600/400 orders). Estimate ~80 h one worker.
- Schemas regenerated (optimization +147/-1, campaign max 900 -> 3600).
- Verification: pytest backend/tests --basetemp var/pytest-v4-full-03: 186 passed, 29 skipped,
  5 failed - all BLOCKED_MONGODB_RUNTIME (rechecked var/pytest-v4-fail-03); ruff PASS; mypy 105
  PASS; architecture PASS (var/architecture-v4-03.json); paper-v3 configs re-dump identical
  (0 mismatch, 328 joint treatments without new keys). NOT run: frontend lint/build/tests
  (no node_modules), any experiment, a large-scale evaluation-cost probe.
- MongoDB rerun (2026-10-28, user started scripts/start_mongodb.ps1; health verified):
  pytest backend/tests -q -p no:cacheprovider --basetemp var/pytest-v4-mongo-01: 220 passed,
  0 failed, 0 skipped, 1 existing Starlette/httpx warning (154 s). Persistence/worker integration
  verified with the v4 changes.

Diagnosis from source (not from the report numbers; reports/paper-v3-unlimited-time2-20261026 is not
on this machine): random_search = pre-filtered multi-edit random walk with steps up to 3 grid cells,
feedback = single +-1 cell moves without prefilter; T4 uses only shelf:face, so most T3 edits are
objective-neutral; duplicates never spend budget; local_trap has one locked shelf (multistart
RESTART_UNAVAILABLE by design); default patience=1.

Implemented (all new JointConfig fields default None and are omitted from dumps; paper-v3 configs
re-validate with no new keys, 353 joint treatments checked):
- contracts/feedback.py: t1_steps, geometry_prefilter, t3_scope, layer_allocation, kicks,
  kick_edits, restart_max_step (+ V4_CONTROLS, serializer, t1_steps validation).
- feedback/neighborhood.py: multi-step T1 moves, geometry prefilter (engines/t1_layout violations),
  objective-scoped T3, interleave() with smooth weighted round-robin.
- feedback/restarts.py: max_step and edits parameters (defaults unchanged).
- feedback/coordinator.py: adaptive per-layer success weights (trace `layer_weights`), iterated
  local search kicks (`ILS_KICK` events, separate descent state and best), restart_max_step.
- experiments/analysis.py: PRIMARY_METRICS and `holm_primary_wilcoxon_exact_p` (objective-only Holm
  family) beside the existing full-table column.
- datasets/schemas/optimization.schema.json regenerated (additive, +103 lines).
- scripts/build_paper_v4_configs.py -> experiments/configs/paper-v4/ (1,210 jobs: V2 step x guidance
  250, V4 leave-one-out ablation 70, V3 budget grid 90, V1 main 800; fresh seeds 7001-7510; reuses
  paper-v3 calibration, no simulation). All 343 treatments validated through JointConfig/to_domain.
- scripts/run_paper_campaigns.py: `--set paper-v3|paper-v4` (default paper-v3 unchanged).
- Docs: HOW_TO_RUN_JOINT_OPTIMIZATION.md (new controls), PAPER_EXPERIMENT_RUNBOOK.md (paper-v4).
- Tests: backend/tests/unit/test_joint_search_v4.py (8), primary-Holm assertions in
  test_held_out_evaluation.py.

Verification 2026-10-28 (repo root, MongoDB NOT available on this machine):
- pytest backend/tests --basetemp var/pytest-v4-full-02: 182 passed, 29 skipped, 5 failed; all 5
  failures and the skips are BLOCKED_MONGODB_RUNTIME (test_experiment_platform x4,
  test_joint_no_incumbent x1) - persistence not verified here, rerun with MongoDB.
- ruff (backend + v4 scripts) PASS; mypy 105 files PASS; architecture PASS (var/architecture-v4-02.json).
- NOT run: any experiment, frontend checks.

Limitations: kicks/restarts edit T1 only (no help on locked-layout local_trap); large has only 3
uncalibrated instances; screen_margin 0.02 is a declared assumption; runtime estimate ~80 h is extrapolated from 2026-10-26 per-evaluation costs.
Next: owner reviews feedback_v4 settings and authorizes the paper-v4 run (runbook section 2), with
MongoDB running; then rerun the MongoDB integration tests.

Merge 2026-10-28 with origin/main 96f354d (2026-10-27: first-fit repair, unlimited-memory option,
job cap 1800 s / campaign 28800 s): kept job cap 3600 s, took memory_limit_mb None and max_wall_s
28800; test_extended_timeouts.py bounds moved to 3601; schemas regenerated after the merge.
Note: the 2026-10-27 section below was written on the machine that ran paper-v3.

# Current handoff - authorized source publication scope, 2026-10-27

User explicitly requested committing/pushing everything except experiment results.
Publication includes all current source, tests, JSON schemas, experiment configs,
README/runbook/handoff and previously ignored experiments source/docs/visualization.
Updated .gitignore to share those source paths while retaining experiments/results,
experiments/reports, var, runtime/databases/backups/cache/logs locally. Generated
x1-union-spaces.json summaries are excluded; finite exact configurations remain inputs.
No result tree or local data is deleted. Prior source changes are intentionally included.

Before staging: fetched origin; HEAD/origin/main divergence 0/0. Backend source hash
still equals the verified 9/9 T3 repair acceptance receipt (no code changes since
that verification). Publication checks: git diff --check, staged scope/size/secret
inspection and remote HEAD comparison after push. Do not present historical test
counts as fresh tests in this publication turn. Commit/push are explicitly authorized;
outcome receipt will be recorded locally under var/git-publication-20261027/.

---

# Current handoff - nine persistent T3 failures repaired and replayed, 2026-10-27

User explicitly requested source fixes based on the two failed retry rounds. Fresh
comparison confirmed 9 main failures + 18 additional failures, all deterministic
baseline SLOTTING_FAILED at T3. Only four synthetic instances affected; fixed category
assignment, dimensions, facings and loads were preserved. Root cause: demand-first
first-fit fragments two 1.9 m strips; total required widths are 3.6964-3.7924 m on
3.8 m of capacity. A width-only reorder recovered only 4/9 in diagnostic probes.
This was constructive search failure, not proven infeasibility or insufficient RAM/time.

Source repair: engines/t3_slotting/repair.py implements deterministic width-ordered
backtracking on the single failed shelf, max 20000 nodes / 64 products; respects
cancellation/deadline, allowed kinds, orientations, fixed facings, maximum layers/depth,
per-face widths and shared per-level loads. engine.py invokes it only on first-fit
failure and replaces that shelf's partial placements. Normal first-fit successes retain
the original path/status. New status FEASIBLE_FIRST_FIT_REPAIRED makes the repair explicit;
no MILP fallback, assignment edits or relaxed physical constraints. Independent replay
still validates every placement. Runtime T3 model version bumped to
facing-strip-milp-1.2-first-fit-repair. No schema shape changed.

Added 9 recorded physical regression witnesses in datasets/samples/t3_first_fit_fragmentation.json
and unit regressions for bounded search, cancellation, deadline, unchanged success path
and shared loads across faces. Before source repair: all 9 reproduction tests FAILED;
after: all 9 PASS. Full backend + adaptive tests: 227 passed, 1 existing Starlette/httpx
warning, 141.84 s (var/t3-repair/pytest-full). Initial mypy found two local variable typing
issues; fixed by renaming the optional shelf and adding a narrowing assertion (no algorithm
change). Final T3/planogram/engine tests: 38 passed, 0.86 s (pytest-final-unit-v2), including
a strengthened shared-load witness. Final mypy PASS 106 files, Ruff PASS, architecture
PASS 106 Python / 40 frontend modules (var/t3-repair/architecture-final.json). Frontend
not changed or re-tested in this repair. git diff --check PASS.

Ran scripts/replay_failed_campaign_jobs.py through production durable queue and killable
workers, same original plans/configs/job budgets/seeds/folds and physical snapshots,
current source identity. Newly initialized plans narrowed to only the original failed
job keys before any jobs ran; full plan/selection receipts retained. Output:
experiments/results/paper-v3-t3-repair-20261027/ (4 campaigns). Fresh acceptance 07:40 UTC+7:
9/9 SUCCEEDED, all planogram statuses FEASIBLE_FIRST_FIT_REPAIRED, all independent
validation PASS, all held-out evaluation COMPLETED, all 4 campaign integrity checks PASS.
Recoveries: small_f4_s102 folds 1/2/3/4 (4), small_f4_s110 folds 0/1/3 (3),
small_f4_s9101 fold 0 (1), small_f4_s9109 fold 0 (1).
Source SHA256: 9a373584ba102f19750ac958366d872ec3586d802c38852078f8974274a7deb7;
ledger runtime equals current runtime at final verification. Physical inputs compare
identically after stripping only _runtime. Original 73 main/retry integrity manifests
and Git index bytes remain unchanged. Existing dirty work preserved; no staging/commit/push.

Verified external pre-change snapshot: C:/Users/admin/SmartRetailBackups/t3-repair-20261027-072927.
Receipts: var/t3-repair/{before-evidence.json,acceptance.json,recovered-jobs.csv}; full
replay details in experiments/results/paper-v3-t3-repair-20261027/replay-ledger.json.
README and runbook describe the new baseline and boundedness. Original 1436-job reports
remain 1427 successes + 9 failures; never splice these 9 new-source results into the old
scientific comparison. This completes recovery of the requested 9 jobs, not acceptance
of a new full research campaign. A future same-source comparative campaign is separate scope.

Actual commands: python -m pytest backend/tests/unit/test_first_fit_repair.py (9 failures
before fix); python -m pytest backend/tests scripts/tests/test_paper_adaptive.py -q
-p no:cacheprovider --basetemp var/t3-repair/pytest-full; python -m pytest
backend/tests/unit/test_first_fit_repair.py backend/tests/unit/test_planogram_replay.py
backend/tests/unit/test_engines.py -q -p no:cacheprovider --basetemp
var/t3-repair/pytest-final-unit-v2; python -m mypy --config-file backend/pyproject.toml
backend/src/smart_retail; python scripts/verify_architecture.py --output
var/t3-repair/architecture-final.json; python -u scripts/replay_failed_campaign_jobs.py
--source experiments/results/paper-v3-unlimited-time2-20261026
--output experiments/results/paper-v3-t3-repair-20261027.

---

# Current handoff - paper-v3 doubled-timeout run COMPLETED, 2026-10-27

Fresh status read at 2026-10-27 07:22 UTC+7: all 1436 planned jobs recorded across
65 campaigns, all checkpoints COMPLETED, no incomplete started campaigns. 1427
SUCCEEDED with independent validation PASS; 9 FAILED / SLOTTING_FAILED / NO_SOLUTION,
all baseline at T3 (X2: 7, X3: 2). These first-fit failures are not proof of
infeasibility. Zero recorded timeout or RAM-limit failures. No failed jobs rerun.

Last campaign completed 2026-10-27 02:15:49 UTC+7; runner verified integrity and
reported X1 (pooled X1/X1b), X4, X2, X5, X6 and X3, finishing 03:34:06 UTC+7.
Launcher PID 23068 no longer alive. finished.json is COMPLETED. Refreshed stale
status.json from RUNNING/empty active to COMPLETED using finished.json; preserved
previous status in var/paper-v3-adaptive-time2/status-before-completion-refresh.json.
The resource measurements in the final status are historical samples, not live RAM.

Block records: X1 230/230 succeeded; X1b 20/20; X4 31/31; X2 770/770 attempted,
763 succeeded + 7 failed; X5 125/125 succeeded; X6 110/110; X3 150/150 attempted,
148 succeeded + 2 failed. Adaptive scheduler journal confirms automatic reduction
to 2 at 2026-10-26 16:10:10 UTC+7 and restoration to 3 at 16:52:41 UTC+7.

Actual read-only verification: parsed every config index entry/checkpoint/record,
counted validation/error statuses, checked finished marker and runner process,
read report journal and confirmed results.json/statistics.json in all six report
folders. Did not rerun the runner's final full integrity pass (already journaled
VERIFIED_REPORTED for all six groups) or any application tests this status turn.
Report artifact counts: X1 381, X2 627, X3 527, X4 171, X5 152, X6 577 files.
One matplotlib tight_layout UserWarning in stderr: margins could not accommodate
all plot decorations. Reports exist, but publication figure layout is not visually
accepted. No scientific superiority/effectiveness conclusion assessed in this turn.

Results: experiments/results/paper-v3-unlimited-time2-20261026/;
reports: experiments/reports/paper-v3-unlimited-time2-20261026/;
receipts/logs: var/paper-v3-adaptive-time2/. Prior partial runs remain intact.
Next: inspect instance_comparisons.csv, status_matrix.csv and figures before using
numbers in the paper; report 9 baseline failures explicitly. No source edits,
reruns, service restarts, staging, commit or push during this status check.

---

# Current handoff - paper-v3 main and bounded retries completed, 2026-10-27

Main runner finished 2026-10-27 03:34:06 UTC+7. All 1436 original jobs executed:
1427 SUCCEEDED, 9 FAILED (all baseline SLOTTING_FAILED at T3; heuristic failure,
not proven infeasibility). All 65 campaigns have integrity PASS receipts; final
runner VERIFIED_REPORTED journal confirms X1 (pooled with X1b), X4, X2, X5, X6, X3.
Reports: experiments/reports/paper-v3-unlimited-time2-20261026/.

After verified runner/worker exit, ran var/paper_v3_retry.py sequentially using
production durable queue and killable worker processes. Original specs retained;
newly initialized retry plans selected only failed job keys. Regenerated plan/input
hashes, runtime/config identity and final normalized record input hashes all matched
originals. Two additional attempts per failed job: 18 retries, all 18 FAILED with
SLOTTING_FAILED, zero recovered, nine persistent failures. Eight retry campaigns
integrity PASS, original integrity manifests unchanged. Original job count stays1436.
Results: experiments/results/paper-v3-unlimited-time2-20261026-retries/attempt-1
and attempt-2. Master ledger: var/paper-v3-retry/ledger.json.

An initial retry helper preflight incorrectly compared pre-normalization plan hashes
to runtime-stamped record hashes; it stopped before launching any jobs. Corrected
the helper to compare plan-to-plan before execution and record-to-record after;
all18 actual retry input hashes matched originals. No backend source edits.

Final evidence: var/paper-v3-monitor/20261027-034525/summary.json, jobs.csv,
retry-results.csv, retry-ledger.json and logs. Main stderr has a Matplotlib
joint-convergence tight_layout warning; plots were not visually reviewed. Do not
claim all jobs succeeded or retry fixed the first-fit limitation. Any algorithm
change requires a new source identity/experiment design decision. No commit/push
or index mutation. Monitoring automation confirmed PAUSED after bounded retries completed.

---

# Current handoff - doubled timeouts, adaptive 3/2, unlimited RAM, 2026-10-26

User explicitly chose doubling both job and campaign timeouts. Job budgets are now
120/600/1200/1800 s instead of 60/300/600/900; worker wall caps are respectively
135/660/1320/1980 s, retaining max(15 s, 10%) finalization grace. Campaign max_wall_s
is doubled per config, hard maximum now 28800 s (8 h). Evaluation counts, seeds,
objective, treatments and RAM admission policy are unchanged. No per-job RSS cutoff.

Stopped only the owned adaptive runner tree, launcher PID 26800, before modifying
backend contracts (new source identity). Previous unlimited run retains 92 recorded
outcomes at experiments/results/paper-v3-unlimited-20261026. Preserved original capped
run too. Active children were terminated during transition; these partial runs must
not be pooled with the new run. Verified external source/docs snapshot and record
hash manifests: C:/Users/admin/SmartRetailBackups/timeout-increase-20261026-102548.

Updated input/campaign time bounds, synchronized optimization/campaign JSON schemas,
frontend bounds, README and runbook, and pooled deepmg campaign budget cap. Copied all
55 configs to experiments/configs/paper-v3-unlimited-time2-20261026 and verified only
job_time_limit_s/max_wall_s differ (both exactly x2); still 1416 jobs plus X1b later.
Adaptive runner --generated-time-multiplier 2 also doubles newly generated X1b budgets
and keeps index metadata synchronized. Original configs/results remain unchanged.

Started launcher PID 23068 at 2026-10-26 10:29:40 UTC+7, command:
.venv/Scripts/python.exe -u scripts/run_paper_adaptive.py
--configs experiments/configs/paper-v3-unlimited-time2-20261026
--results experiments/results/paper-v3-unlimited-time2-20261026
--reports experiments/reports/paper-v3-unlimited-time2-20261026
--state var/paper-v3-adaptive-time2 --generated-time-multiplier 2
PID receipt/log/status/journal now in var/paper-v3-adaptive-time2/ (old state path is
historical). Observed 3 active campaigns, RAM 65%, 12 SUCCEEDED records, empty stderr.
Live immutable inputs show 600 s for tiny phase-1; campaign configs show trap 120 s,
tiny 600 s; campaign caps 19500/24400 s. Evidence is launch verification, not completion.

Fresh checks: mypy PASS 105 files; architecture PASS 105 Python/40 frontend;
frontend lint/build PASS, Vitest 4 passed; Ruff PASS; git diff --check PASS. Full backend
plus adaptive test run: 214 passed and 1 failed (139.05 s) because a pre-existing test
still rejected 901 s. Updated that obsolete expectation to reject 1801 s; reran the
entire held-out unit module, new timeout contract tests and adaptive test: 28 passed,
1 existing Starlette/httpx warning, 2.31 s. Backend application source did not change
after the full test execution; no claim of a second full-suite green run.
Commands: python -m pytest backend/tests scripts/tests/test_paper_adaptive.py -q
-p no:cacheprovider --basetemp var/pytest-timeout2-20261026; then python -m pytest
backend/tests/unit/test_held_out_evaluation.py backend/tests/contracts/test_extended_timeouts.py
scripts/tests/test_paper_adaptive.py -q -p no:cacheprovider
--basetemp var/pytest-timeout2-boundary-20261026. New tests cover 1800 s acceptance,
1801 s rejection, 28800/28801 s campaign bounds, roundtrip and 1980 s worker wall budget.

Next: monitor the NEW state/results paths, retain 3->2 above 90% RAM and 2->3 below
80%, sample every 5 s and yield optional third slot at job boundaries. Do not change
backend/src or pull source mid-run. Verify integrity/reports after completion.
No staging, commit or push. Prior handoff sections below are historical.

Monitoring milestone 2026-10-26 10:45 UTC+7: ran
`.venv/Scripts/python.exe var/paper_v3_monitor.py` (read-only campaign inspection).
Snapshot: 179/1436 planned jobs SUCCEEDED, zero recorded job/operational errors,
2 jobs in progress; trap COMPLETED 150/150, tiny parts 15/40 and 14/40.
X1b 20 jobs remain provisional pending union construction. Reconstructed all
1416 currently configured job keys; exported CSV/JSON and empty retry queue to
var/paper-v3-monitor/20261026-104538/. Integrity verify trap PASS (11585 files).
Verified live launcher 23068 creation time/command line and child campaign processes;
runner stderr empty. RAM 65%, admission slots 3 but only two unfinished X1 campaigns.
Updated 30-minute heartbeat to current time2 paths; no retries needed/launched.
Historical 152/92 outcomes excluded. Next: continue monitoring X1 completion, union
build and later blocks; do not change running backend source or overwrite results.

Monitoring milestone 2026-10-26T11:17:22.348542+07:00:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; refreshed live rows after
checksum collection. 238/1436 SUCCEEDED, zero job/operational errors.
X1 COMPLETED 230/230; X1b union configs built, exact phase running.
All 1436 configured job keys unique and exported with status in
var/paper-v3-monitor/20261026-111441/. Integrity PASS on trap, both tiny phase-1
campaigns and exact tiny seeds 5001-5003 (6 campaigns). Verified launcher 23068
command/creation time, child processes, three live worker leases; stderr empty.
No retries needed/launched; next monitor X1b then X4. No backend source changes.

Monitoring milestone 2026-10-26 11:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; snapshot collected
11:44:54-11:45:25. 273/1436 SUCCEEDED; zero job/operational errors.
X1 230/230 and X1b 20/20 COMPLETED; X4 active, tiny/small completed.
Evidence and all 1436 unique job statuses: var/paper-v3-monitor/20261026-114454/.
Verified newly completed campaigns via checksum; prior PASS receipts explicitly
labeled PREVIOUS_PASS_NOT_RERUN in summary (no new checksum claim for them).
Live launcher 23068 identity/creation time verified; stderr empty. Medium worker
RUNNING with live lease; large worker SUCCEEDED awaiting campaign record/finalization
at health observation, so expired lease on that terminal run is not a worker fault.
No retries needed/launched. Next: monitor X4 finalization and transition to X2.
Only var monitoring helper and this handoff updated; running backend unchanged.

Monitoring milestone 2026-10-26 12:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 12:14:41-12:14:53.
280/1436 SUCCEEDED, zero recorded job/operational errors.
X1/X1b remain completed; X4-large completed 4/4, medium still active.
Evidence: var/paper-v3-monitor/20261026-121441/ (1436 unique job keys, CSV/JSON,
PID command/creation evidence, empty stderr, worker-health and retry ledger).
Launcher 23068 alive; medium active job RUNNING, live lease, elapsed 312 s at health
observation (within configured 1800 s job budget). No retry launched/needed.
New checksum check for completed X4-large PASS; older PASS receipts labeled historical.
Next monitor medium completion and transition to X2; do not change running source.

Monitoring milestone 2026-10-26 12:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collected 12:44:40-12:45:02.
362/1436 SUCCEEDED; 0 recorded job errors;
0 operational errors. X4 now completed; X2 active.
Evidence: var/paper-v3-monitor/20261026-124440/, with 1436 unique job rows,
process command/creation identity, stderr, worker-health and retry ledger.
Launcher 23068 alive. Worker observed RUNNING/PENDING with live lease during slot
transition; no claim of stalled worker from missing supervisor at launch boundary.
New completed-campaign checksum results in summary; prior PASS receipts explicitly
historical. No retries launched. Next continue monitoring X2 and newly recorded errors.

Monitoring milestone 2026-10-26 13:18 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; sequential collection
13:14:43-13:17:46. 485/1436 SUCCEEDED, 0 recorded job
errors, 0 operational errors. X2 continues; X1/X1b/X4 complete.
Evidence: var/paper-v3-monitor/20261026-131443/ (1436 unique job keys, CSV/JSON,
PID/command/creation identity, empty stderr, worker-health and retry ledger).
Launcher 23068 verified alive. Observed three worker leases live (two RUNNING,
one SUCCEEDED finalizing). New checksum checks for X2 tiny parts 03-06 PASS;
older checks explicitly recorded as historical receipts, not rerun.
No retries needed/launched. Next monitor X2 progression and failure queue;
source/configs/results unchanged. Counts are sequential observations, not atomic.

Monitoring milestone 2026-10-26 13:49 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; sequential collection
13:44:46-13:48:44. 614/1436 SUCCEEDED, 0 recorded job
errors, 0 operational errors. X2 active; X1/X1b/X4 complete.
Evidence: var/paper-v3-monitor/20261026-134446/ (1436 unique job rows, CSV/JSON,
launcher command/creation time, empty stderr, worker-health and retry ledger).
Launcher 23068 verified alive. Observed running workers with live leases and
supervisor evidence. New completed checksum checks PASS as listed in summary;
older PASS receipts explicitly historical, not rerun. No retries needed/launched.
Next monitor X2 progression and failure queue. Counts are sequential observations;
source/configs/results unchanged, no Git index mutation.

Monitoring milestone 2026-10-26 14:17 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; sequential collection
14:14:45-14:16:39. 697/1436 SUCCEEDED, 0 recorded job
errors, 0 operational errors. X2 active; X1/X1b/X4 complete.
Evidence: var/paper-v3-monitor/20261026-141445/ with 1436 unique job rows,
launcher command/creation evidence, empty stderr, worker health and retry ledger.
Launcher 23068 verified alive. Three observed leases live (two RUNNING,
one SUCCEEDED finalizing). Newly completed X2 tiny parts 13-15 checksum PASS;
previous PASS receipts explicitly historical, not rerun. No retries needed/launched.
Next continue X2 monitoring, retaining original results and running source identity.

Monitoring milestone 2026-10-26 14:50 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; sequential collection
14:44:44-14:49:48. 817/1436 recorded outcomes: 813 SUCCEEDED,
4 errors; 0 operational errors. X2 active; X1/X1b/X4 complete.
New 4 FAILED baseline jobs in paper-x2-small-part02, small_f4_s102 seed 1,
folds 1-4, error SLOTTING_FAILED at T3 (P5/P35/P24/P24 respectively).
First-fit packing failure is not proven infeasibility. Original records preserved;
4 jobs queued WAITING_MAIN_RUNNER in retry-ledger.json, no retry launched.
Evidence: var/paper-v3-monitor/20261026-144444/ with 1436 unique job rows,
error details/statistics, process identity and worker health. Launcher 23068 alive,
observed RUNNING workers with live leases; stderr empty. Newly completed campaigns
checksum PASS as listed in summary; historical PASS receipts explicitly labeled.
Next monitor X2 and error queue; after main runner ends, retry only failed jobs into
separate output, preserve protocol/identity and cap at 2 additional attempts/job.
No source/config/result replacement or Git index mutation.

Monitoring milestone 2026-10-26 15:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 15:14:46-15:15:05.
832/1436 recorded outcomes, 828 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active, prior X1/X1b/X4 complete. Evidence and 1436 unique job rows:
var/paper-v3-monitor/20261026-151446/. Error first_seen carried forward, retry
ledger remains WAITING_MAIN_RUNNER; no retries launched. Launcher 23068 alive,
command/creation verified, stderr empty. Medium term health: RUNNING worker has
live lease; SUCCEEDED job with expired lease is terminal finalization, not failure.
Checksum status explicitly distinguishes new checks from historical PASS receipts.
Next continue X2/error monitoring; retry only failed jobs after main runner ends.
No source/config/result replacement or Git index mutation.

Monitoring milestone 2026-10-26 15:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 15:44:45-15:45:08.
860/1436 recorded outcomes: 856 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active, X1/X1b/X4 complete. Evidence: var/paper-v3-monitor/20261026-154445/
with 1436 unique job rows, error history/statistics, pending retry ledger and
worker health. Launcher 23068 command/creation verified; 3 observed RUNNING
workers with live leases, stderr empty. Checksum verification results and historical
receipts distinguished in summary. No retry launched while main runner active.
Next monitor X2 small campaigns, preserve inputs/results/source and retry failed
jobs separately after main runner ends. No Git index mutation.

Monitoring milestone 2026-10-26 16:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 16:14:49-16:15:22.
894/1436 recorded outcomes: 890 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active; X1/X1b/X4 complete. RAM observed 95%, policy correctly reduced slots
to 2, active small parts 05/06; both RUNNING with live leases and supervisor evidence.
Launcher 23068 command/creation verified; stderr empty. Evidence and 1436 unique
job rows: var/paper-v3-monitor/20261026-161449/. Newly completed campaign checksum
checks PASS as listed, historical receipts labeled. Retry queue WAITING_MAIN_RUNNER,
no retry launched while main active. Next monitor RAM recovery, X2 and failure queue.
No source/config/result replacement or Git index mutation.

Monitoring milestone 2026-10-26 16:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 16:44:46-16:45:01.
903/1436 recorded outcomes: 899 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active; X1/X1b/X4 complete. RAM 90%, slots remain 2 under hysteresis (restore
3 below 80%); active small parts 05/06, live leases, elapsed 177/75 s at health check.
Launcher 23068 command/creation verified; stderr empty. Evidence and 1436 unique
job rows: var/paper-v3-monitor/20261026-164446/. Integrity receipts in summary;
retry queue WAITING_MAIN_RUNNER, no retry launched. Next monitor RAM/X2/failures.
No source/config/result replacement or Git index mutation.

Monitoring milestone 2026-10-26 17:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 17:14:50-17:15:05.
925/1436 recorded outcomes: 921 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
RAM recovered to 69%, slots restored to 3, active small parts 06/04/07.
Launcher 23068 command/creation verified; all 3 observed workers RUNNING with live
leases, stderr empty. Evidence: var/paper-v3-monitor/20261026-171450/ with 1436
unique job rows, errors/first_seen history, pending retry ledger and checksum receipts.
No retry launched while main runner active; original source/config/results preserved.
Next monitor X2 progression and errors, then retry failed jobs separately after main.

Monitoring milestone 2026-10-26 17:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 17:44:46-17:45:01.
956/1436 recorded outcomes: 952 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active; RAM 71%, slots 3, active small parts 08/04/07. Launcher 23068 command/
creation verified; all 3 observed workers RUNNING with live leases, stderr empty.
Evidence: var/paper-v3-monitor/20261026-174446/, 1436 unique job rows, error history,
retry ledger, worker health and checksum receipts. No retry launched while main active.
Next monitor X2 and pending failures; original source/config/results preserved.

Monitoring milestone 2026-10-26 18:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 18:14:49-18:15:05.
982/1436 recorded outcomes: 978 SUCCEEDED,
4 job errors, 0 new versus prior check; 0 operational errors.
X2 active; RAM 68%, slots 3, active small parts 08/09/07. Launcher 23068 command/
creation verified; observed RUNNING worker live lease and 2 SUCCEEDED finalizations,
no expired-terminal-lease fault inferred; stderr empty. Evidence:
var/paper-v3-monitor/20261026-181449/, 1436 unique job rows, error history,
retry ledger and checksum receipts. No retry launched while main active.
Next monitor X2 progression/failures; original source/config/results preserved.

Monitoring milestone 2026-10-26 18:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 18:44:47-18:45:11.
1013/1436 recorded outcomes: 1006 SUCCEEDED,
7 job errors, 3 new versus prior check; 0 operational errors.
X2 active, now medium part01 started; RAM 70%, slots 3. Launcher 23068 command/
creation verified; 2 observed workers RUNNING with live leases and 1 SUCCEEDED
finalization, stderr empty. Evidence: var/paper-v3-monitor/20261026-184447/
with 1436 unique job rows, error history, pending retry ledger and checksum receipts.
No retries launched while main runner active. Next monitor medium/remaining small
campaigns and retry failed jobs separately after main ends; source/results preserved.

Monitoring milestone 2026-10-26 19:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 19:15:02-19:15:15.
1030/1436 recorded outcomes: 1023 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X2 active (both medium parts plus small part10), RAM 71%, slots 3.
Launcher 23068 command/creation verified, 3 observed workers RUNNING with live
leases/supervisors; stderr empty. Evidence: var/paper-v3-monitor/20261026-191502/
with 1436 unique job rows, error history/statistics, pending retry ledger and checksum
receipts. No retries launched while main runner active. Next monitor X2 tail and
transition to X5; preserve source/configs/results and Git index.

Monitoring milestone 2026-10-26 19:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 19:44:49-19:44:58.
1042/1436 recorded outcomes: 1035 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X2 small part10 complete, both medium campaigns remain. RAM 68%, slots 3 but
only 2 campaign processes. Launcher 23068 command/creation verified; both observed
jobs SUCCEEDED awaiting campaign finalization, expired terminal leases not faults.
Evidence: var/paper-v3-monitor/20261026-194449/ with 1436 unique job rows,
errors/history, retry queue and checksum receipts; stderr empty. No retries launched.
Next monitor medium completion/transition X5; preserve source/config/results/index.

Monitoring milestone 2026-10-26 20:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 20:14:59-20:15:13.
1048/1436 recorded outcomes: 1041 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X2 both medium campaigns active, RAM 61%, slots 3 but 2 campaign processes.
Launcher 23068 command/creation verified. Observed medium02 RUNNING/live lease
(elapsed 390 s); medium01 job SUCCEEDED awaiting record, expired terminal lease
not a worker fault. Evidence: var/paper-v3-monitor/20261026-201459/ with 1436
unique job rows, errors/history, pending retry ledger and checksum receipts.
Stderr empty; no retries launched while main active. Next monitor X2 tail/transition
X5, preserving source/config/results and Git index.

Monitoring milestone 2026-10-26 20:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 20:44:50-20:45:00.
1069/1436 recorded outcomes: 1062 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X2 fully executed (7 failed jobs remain separate); X5 now active, parts 01-03.
RAM 63%, slots 3, launcher 23068 command/creation verified. Three observed workers
RUNNING with live leases/supervisors; stderr empty. Evidence:
var/paper-v3-monitor/20261026-204450/, 1436 unique job rows, errors/history,
retry ledger and checksum receipts. No retries launched while main active.
Next monitor X5 and pending failures; preserve source/config/results and index.

Monitoring milestone 2026-10-26 21:15 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 21:14:54-21:14:58.
1090/1436 recorded outcomes: 1083 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X5 active parts 01-03, RAM 63%, slots 3. Launcher 23068 command/creation verified;
observed 2 workers RUNNING/live leases and 1 SUCCEEDED finalizing, stderr empty.
Evidence: var/paper-v3-monitor/20261026-211454/ with 1436 unique job rows,
error history/statistics, retry queue and integrity receipts; no retry launched while
main active. Next monitor X5 and pending failures, preserve source/config/results/index.

Monitoring milestone 2026-10-26 21:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 21:44:53-21:44:58.
1119/1436 recorded outcomes: 1112 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X5 active parts 01-03, RAM 59%, slots 3. Launcher 23068 command/creation verified;
observed 2 RUNNING/live leases and 1 SUCCEEDED finalization, stderr empty.
Evidence: var/paper-v3-monitor/20261026-214453/ with 1436 unique job rows,
error history/statistics, pending retry ledger and integrity receipts. No retries
launched while main active; next monitor X5 completion/remaining campaigns.
Source/config/results and Git index preserved.

Monitoring milestone 2026-10-26 22:18 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; sequential collection
22:15:16-22:17:40. 1147/1436 recorded outcomes: 1140 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X5 parts01-03 complete, 04/05 active; RAM 62%, slots3 but 2 campaigns left.
Launcher23068 command/creation verified; observed RUNNING/live lease and SUCCEEDED
finalization; stderr empty. Evidence: var/paper-v3-monitor/20261026-221516/,
1436 unique job rows, errors/history, pending retry ledger and integrity receipts.
New checksum checks for X5 parts01-03 PASS; prior receipts historical. No retries
launched while main active. Next monitor X5 tail/transition X6; preserve source/data/index.

Monitoring milestone 2026-10-26 22:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 22:45:19-22:45:23.
1162/1436 recorded outcomes: 1155 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X5 parts04/05 active, RAM59%, slots3 but only2 campaign processes. Launcher23068
command/creation verified; observed RUNNING/live lease and SUCCEEDED finalization,
stderr empty. Evidence: var/paper-v3-monitor/20261026-224519/, 1436 unique job rows,
errors/history, retry ledger and integrity receipts. No retries launched while main active.
Next monitor X5 tail/transition X6; source/config/results and Git index preserved.

Monitoring milestone 2026-10-26 23:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 23:15:21-23:15:36.
1185/1436 recorded outcomes: 1178 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X5 fully completed; X6 active demand parts01-03, RAM60%, slots3. Launcher23068
command/creation verified; 3 observed RUNNING workers/live leases, stderr empty.
Evidence: var/paper-v3-monitor/20261026-231521/ with1436 unique job rows, errors,
retry ledger and integrity receipts. New X5 parts04/05 checksum PASS; prior receipts
historical. No retries launched while main active. Next monitor X6 then X3, preserve
source/config/results and Git index.

Monitoring milestone 2026-10-26 23:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 23:45:20-23:45:23.
1227/1436 recorded outcomes: 1220 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X6 demand parts01-03 active, RAM61%, slots3. Launcher23068 command/creation verified;
observed 1 RUNNING/live lease and 2 SUCCEEDED finalizations (expired terminal leases
not faults), stderr empty. Evidence: var/paper-v3-monitor/20261026-234520/,
1436 unique job rows, error history, pending retry ledger and checksum receipts.
No retries launched while main active. Next monitor X6 progression, preserve
source/config/results and Git index.

Monitoring milestone 2026-10-27 00:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 00:15:22-00:15:35.
1271/1436 recorded outcomes: 1264 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X6 demand parts01-03 complete; 04/05/load active, RAM61%, slots3. Launcher23068
command/creation verified; 2 jobs observed RUNNING/live leases during sample,
stderr empty. Evidence: var/paper-v3-monitor/20261027-001522/, 1436 unique job rows,
error history, retry ledger and checksum receipts. New checksum checks PASS for
completed demand01-03; older receipts historical. No retries launched while main active.
Next monitor X6 then X3, preserve source/config/results and Git index.

Monitoring milestone 2026-10-27 00:46 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 00:45:20-00:45:42.
1352/1436 recorded outcomes: 1345 SUCCEEDED,
7 job errors, 0 new versus prior check; 0 operational errors.
X6 completed; X3 tiny parts01-03 active, RAM62%, slots3. Launcher23068 command/
creation verified; 3 observed RUNNING workers/live leases, stderr empty. Evidence:
var/paper-v3-monitor/20261027-004520/ with1436 unique job rows, error history,
retry ledger and checksum receipts. Newly completed X6 checks PASS, prior receipts
historical. No retries launched while main active. Next monitor X3 then retry queue;
source/config/results and Git index preserved.

Monitoring milestone 2026-10-27 01:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 01:15:21-01:15:45.
1400/1436 recorded outcomes: 1392 SUCCEEDED,
8 job errors, 1 new versus prior check; 0 operational errors.
X3 tiny campaigns complete, small parts01/02 active; RAM60%, slots3 but2 campaigns.
Launcher23068 command/creation verified; both observed workers RUNNING/live leases,
stderr empty. Evidence: var/paper-v3-monitor/20261027-011521/, 1436 unique job rows,
error history, pending retry ledger and checksum receipts. Newly completed X3 tiny
checks PASS, prior receipts historical. No retries launched while main active.
Next monitor X3 tail then retry only failed jobs separately; preserve source/data/index.

Monitoring milestone 2026-10-27 01:45 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 01:45:22-01:45:23.
1421/1436 recorded outcomes: 1413 SUCCEEDED,
8 job errors, 0 new versus prior check; 0 operational errors.
X3 small parts01/02 active, RAM60%, slots3 but2 campaigns. Launcher23068 command/
creation verified; observed 1 RUNNING/live lease and 1 SUCCEEDED finalization,
stderr empty. Evidence: var/paper-v3-monitor/20261027-014522/, 1436 unique job rows,
error history, pending retry ledger and integrity receipts. No retries launched while
main active. Next monitor X3 tail and retry failed jobs separately after main ends;
source/config/results and Git index preserved.

Monitoring milestone 2026-10-27 02:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 02:15:23-02:15:29.
1435/1436 recorded outcomes: 1426 SUCCEEDED,
9 job errors, 1 new versus prior check; 0 operational errors.
X3 small01 complete, small02 only campaign left, RAM58%, slots3. Launcher23068
command/creation verified; observed job SUCCEEDED awaiting campaign finalization,
expired terminal lease not a fault; stderr empty. Evidence:
var/paper-v3-monitor/20261027-021523/, 1436 unique job rows, errors/history,
retry ledger and checksum receipts. No retries launched while main still active.
Next verify main completion/process exit, then retry failed jobs separately, max2
additional attempts per job. Source/config/results and Git index preserved.

Main-job milestone 2026-10-27 02:16 UTC+7: final X3 checkpoint completed
2026-10-26T19:15:49Z; all 1436 jobs now recorded: 1427 SUCCEEDED, 9 FAILED.
Latest monitor snapshot var/paper-v3-monitor/20261027-021619/ (02:16:19-02:16:25),
last campaign checksum PASS. Ninth error is baseline small_f4_s9109 seed1,
SLOTTING_FAILED at T3, P0, paper-x3-small-part02; added to pending retry queue.
Launcher23068 still generating pooled reports; wait for process exit/worker quiescence
before running failed-job retries, max2 additional attempts each. Do not declare
full task completion from all campaigns COMPLETED; failures/retries/reports remain.

Monitoring milestone 2026-10-27 02:46 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 02:45:29-02:45:42.
All1436 outcomes present:1427 SUCCEEDED,9 FAILED(SLOTTING_FAILED); 0 new errors.
Main runner still alive (launcher23068, interpreter12552), no numerical workers
observed. Journal VERIFIED_REPORTED X1 at02:27:52 and X4 at02:28:58; currently
verifying/exporting remaining blocks. Do not restart or retry concurrently.
Evidence: var/paper-v3-monitor/20261027-024529/, 1436 unique job rows, process
command/creation/I-O evidence, errors/history, pending retry ledger and checksum
receipts. Stderr empty, no operational errors. No retries launched while main active.
Next await runner exit/report completion, then execute nine failed-job retries in
separate output (max2 additional attempts/job), preserving original data/source/index.

Monitoring milestone 2026-10-27 03:16 UTC+7:
Ran `.venv/Scripts/python.exe var/paper_v3_monitor.py`; collection 03:15:22-03:15:28.
All1436 outcomes:1427 SUCCEEDED,9 FAILED; no new job/operational errors.
Runner23068/interpreter12552 still alive, verified command/creation; no numerical
workers. Reports VERIFIED_REPORTED remain X1/X4; current read-transfer counter
283690875246 bytes vs119959728896 at02:45 (process I/O, not unique file volume),
so evidence shows continued read work. Stderr empty; finished.json absent.
Evidence: var/paper-v3-monitor/20261027-031522/, 1436 unique job rows, process I/O,
errors/history, checksum receipts and pending retry ledger. Nine retries remain
WAITING_MAIN_RUNNER_REPORTS; none launched concurrently. Next await reporting exit,
then retry only failed jobs separately (max2 additional/job), preserve source/data/index.

---

# Current handoff - adaptive three/two campaigns, unlimited RSS, 2026-10-26

User requested: remove per-job RAM limit; run 3 campaigns, reduce to 2 above 90%
system RAM, return to 3 below 80%. Implemented strict thresholds with hysteresis;
80-90% retains current level, samples every 5 s. No CPU admission threshold.
Two continuous campaign supervisors plus a third using max_new_jobs=1: reduction
lets the optional slot finish its current job, then withholds replacement. Jobs
remain in killable processes through the durable queue, with time budgets retained.

Stopped the owned sequential runner tree (PID 16872) before source changes. Its
paper-x1-trap completed 150/150; 2 tiny phase-1 records also completed. Preserved
all 152 recorded outcomes; a subsequent active child was terminated during the
transition. No old record was rewritten. Verified external source/docs snapshot
and prior record hashes: C:/Users/admin/SmartRetailBackups/adaptive-unlimited-20261026-101700.
Old results remain experiments/results/paper-v3 and must not be pooled with the new run.

Contracts now accept memory_limit_mb=null; worker skips only the RSS cutoff when
null. Existing numeric limits/defaults retain enforcement. Regenerated optimization
and campaign schemas; frontend type/rendering handles null. No input data replaced.
Copied the 55 campaign configs into experiments/configs/paper-v3-unlimited-20261026
with null memory limits; original configs preserved. X1b generated configs are also
converted to null before running. This changes backend runtime identity, so all jobs
restart separately at experiments/results/paper-v3-unlimited-20261026; reports go to
experiments/reports/paper-v3-unlimited-20261026. Scientific parameters otherwise retained.

New runner scripts/run_paper_adaptive.py started 2026-10-26 10:21:39 UTC+7, launcher
PID 26800. PID receipt/log/status/journal in var/paper-v3-adaptive/. Three campaigns
observed active: paper-x1-trap, paper-x1-tiny-part01, paper-x1-tiny-part02; RAM 69%.
First 12 finished job receipts all have memory_limit_mb=null. Optional third slot
has completed and resumed one-job slices successfully. Threshold transitions tested
with synthetic measurements; the physical machine has not been driven above 90%.

Fresh validation: backend + adaptive policy pytest 211 passed, 1 existing Starlette/
httpx warning, 141.00 s (var/pytest-adaptive-unlimited-20261026); real worker tests
use synthetic 16 GiB RSS readings to verify null succeeds and 2048 stops with
RESOURCE_LIMIT. Ruff PASS; mypy PASS 105 files; architecture PASS 105 Python/40 frontend;
frontend lint/build PASS; Vitest 4 passed. Additional scripts/tests: 9 passed, 3 failed
because legacy paper-v2 recovery tests require absent historical result configuration;
new runner does not import/use paper_recovery. No fixes to that unrelated historical suite.
Commands: python -m pytest backend/tests scripts/tests/test_paper_adaptive.py -q
-p no:cacheprovider --basetemp var/pytest-adaptive-unlimited-20261026;
python -m ruff check --config backend/pyproject.toml backend/src
backend/tests/integration/test_unlimited_memory.py scripts/run_paper_adaptive.py
scripts/tests/test_paper_adaptive.py; python -m mypy --config-file
backend/pyproject.toml backend/src/smart_retail; python scripts/verify_architecture.py
--output var/paper-v3-adaptive-architecture.json; npm.cmd --prefix frontend run
lint/build/test. git diff --check PASS. No staging, commit or push.

Next: monitor var/paper-v3-adaptive/status.json and error.json; do not edit backend/src
or pull source while running. stop.request in that state directory drains work without
cancelling current jobs. Verify campaign integrity and pooled reports after completion.
Runbook now documents the active command and paths; historical notes below are superseded.

---

# Current handoff - paper-v3 run started on D:, 2026-10-26

User explicitly authorized running experiments after updating to c199fd03.
Started the documented sequential paper-v3 runner from D:/Smart_Retail_Floor_Allocation
at 2026-10-26 10:08 UTC+7. PID 16872; var/paper-v3-run.pid.json records ownership.
Do not launch another runner or edit backend/src while this process is active.
MongoDB was stopped initially; scripts/start_mongodb.ps1 started it successfully.
No prior paper-v3 result/report directory or experiment runner was found.

Fresh preflight: pip check PASS; Ruff backend/src, backend/tests and the three paper
scripts PASS; architecture PASS (105 Python / 40 frontend modules); pytest backend/tests
208 passed, 1 Starlette/httpx deprecation warning, 116.11 s. Command: .venv/Scripts/python.exe
-m pytest backend/tests -q -p no:cacheprovider --basetemp
var/pytest-paper-v3-preflight-20261026-1010. Validated 55 campaign configs via CampaignSpec
and planned_jobs: 1,416 jobs, plus expected 20 X1b jobs built after X1 phase 1.
Using the checked-in first_improvement policy; no experiment design changes.

Launch command: Start-Process .venv/Scripts/python.exe -ArgumentList '-u',
'scripts/run_paper_campaigns.py' -WindowStyle Hidden, with working directory at this root
and stdout/stderr redirected to var/paper-v3-run.log / var/paper-v3-run.err.log.
Runner uses the durable queue, killable worker processes, immutable inputs and runtime
identities. Source/package/config hashes and original config index receipt are in
var/paper-v3-launch-20261026/. MongoDB stays running for this campaign.
Initial observed progress: paper-x1-trap RUNNING, 14/150 completed, all 14 SUCCEEDED;
stderr empty at that observation. This is launch verification, not completed experiments.
Next: monitor checkpoints/journal and worker health; after completion verify every campaign
with experiments CLI verify and inspect pooled reports. Historical ~29-hour estimate is
unconfirmed on this machine. No source/config edits, commit or push in this launch.

---

# Current handoff - paper-v3: all fixes from the paper-v2 review, 2026-10-26

Git (2026-10-26): user authorized push to main. Merged origin/main (9 commits incl. the
2026-10-24 decision to keep the whole experiments/ directory out of Git): paper-v3 configs
stay local in experiments/configs/paper-v3; tracked experiments files deleted by the merge
were restored to the working tree only. Ket_qua_thuc_nghiem_lan_1.docx left untracked.

Request: review Ket_qua_thuc_nghiem_lan_1.docx (user's paper-v2 assessment), then "sữa hết đi"
(fix everything); do NOT run experiments yet. Uncommitted; no commit/push authorized.
Design and issue-by-issue mapping: docs/research/EXPERIMENT_DESIGN_DEEPMG.md section 10;
how to run: docs/research/PAPER_EXPERIMENT_RUNBOOK.md (rewritten for paper-v3).

Milestone 3 - X1 option A (user: "làm X1 theo A + B (sẽ sinh lại cấu hình X1)"):
- FiniteSpace bundles: `layouts` (whole pose sets) and `allocations` (assignment + all SKU
  rows) as single domains (contracts/optimality.py, formulation.py, verifier.py with an
  independent assembly and `inside()` membership; coordinator validate_space/member). Spaces
  without bundles dump unchanged (local-trap digest preserved, tested).
- `finite_spaces.union_space` replaces the neighborhood space. X1 is two-phase: phase 1
  `paper-x1-tiny` (E41, 10 tiny instances, seeds 1-2: seq_milp, random_search, annealing,
  feedback); phase 2 block X1b = one campaign per instance with exact over distinct layouts x
  allocations x policies of all phase-1 best solutions (scripts/build_x1_union_configs.py,
  state cap 400). The runner builds X1b after X1 completes (journaled BUILT/NOT_BUILT) and
  pools X1 + X1b into one report. Hybrid dropped from X1-tiny (needs the space up front).
- analysis: when an `exact` arm exists, instance_comparisons also uses reference `exact`
  (heuristic gap to the certified union optimum).
- Pre-existing defect fixed: pooled reports of >1 joint campaign failed with FileExistsError
  on joint-comparison.csv (joint_reports.export now writes once for all campaigns).
- Option B (global lower bound) analysed, not implemented: shelves only need 0.5 m clearance
  from the entrance, so a valid distance bound is ~1-2 m/journey vs 7-14 m observed (gap
  bound >= 75-90%); documented in the design doc section 10.
- Smoke (integration, not a paper experiment): var/x1-smoke-02, tiny_f6_s5001, seed 1, budget 6:
  phase 1 COMPLETED 3/3, X1b built (2 states), exact GLOBAL_OPTIMAL_CERTIFIED 0.064524 <=
  feedback 0.064524 = gap 0, annealing/seq_milp 0.064901; pooled report written. A first
  attempt (var/x1-smoke-01) hung because the scratch script lacked a __main__ guard for spawn
  workers; its two processes were stopped.
- Verification: pytest backend 207 passed (basetemp var/pytest-x1-full-01, 210 s, MongoDB
  local); ruff (backend + 3 paper scripts) PASS; mypy 105 files PASS; architecture PASS
  (var/architecture-x1-01.json). paper-v3 configs regenerated: 1,416 jobs (+20 X1b later);
  479 templates validated.

Milestone 2 (after the multistart fix below):
- Joint modes `random_search` and `annealing` (contracts/feedback.py, coordinator.py) with
  equal `max_evaluations` budgets; `joint.incumbent_curve` and `joint.evaluations_to_best`
  in every joint result; campaign metric `joint_evaluations_to_best`.
- Load calibration: DatasetSpec `orders`, `order_interval_s` (Poisson order arrivals, separate
  RNG stream so products/lines are unchanged), `picker_count`; generator horizon capped at
  86,400 s; `application/experiments/calibration.py` targets picker utilization.
- `EvaluationSpec.order_rate="population"` (splits.py `arrival_rate`/`rescale`): k-fold subsets
  are time-rescaled to the population order rate (a 1/k fold was simulated at 1/k load).
- `application/experiments/finite_spaces.py`: declared 162-state neighborhood space per
  generated tiny instance for X1 exact/hybrid.
- analysis.py `instance_comparisons` (instance unit, seq_milp reference, exact Wilcoxon, per
  scale + pooled, Holm), written as `instance_comparisons.csv` by reports.py.
- All new contract fields are omitted when None: paper-v2 and other existing configs dump
  byte-identically (checked: 37 configs, 0 mismatches). Schemas regenerated (additive diff only).
- scripts/build_paper_configs.py rewritten for paper-v3; scripts/run_paper_campaigns.py points
  to configs/results/reports `paper-v3`. Frontend: two mode options in ResearchPage.tsx.
- Configs generated: `experiments/configs/paper-v3/` (70 campaign files, index.json,
  calibration.json; 1,456 jobs). Calibration: tiny 12.58 s -> utilization 0.751, small 16.85 s
  -> 0.752, medium 23.37 s -> 0.777. All 499 dataset x treatment templates validated through
  contracts, split and to_domain (scratch script, not committed).
- Open decision for the owner: feedback uses `policy="first_improvement"` in paper-v3 (v2 used
  best_improvement) because 24-action best-improvement sweeps exhaust 16-40 evaluation budgets.
- Probes (not experiments): per-evaluation cost tiny ~1 s, small ~6 s, medium ~39 s; estimate
  ~29 h for paper-v3. X1 probe: exact optimum inside the declared space (~0.10) is worse than
  feedback outside it (0.077), so X1 cannot measure the gap to a global optimum.

Verification milestone 2 (2026-10-26, repo root, MongoDB local running):
- `.venv/Scripts/python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var/pytest-v3-full-01`:
  206 passed, 1 existing Starlette/httpx warning (171 s).
- ruff (backend/pyproject.toml) on backend + both paper scripts PASS; mypy src 105 files PASS
  (one arg-type error in generators.py fixed first); verify_architecture
  `--output var/architecture-v3-01.json` PASS (105 Python, 40 frontend modules).
- NOT run: frontend ESLint/build/Vitest (`frontend/node_modules` absent).

Next: owner confirms the open decision and authorizes the run; then start the runner per the
runbook section 3 (no backend/src edits while it runs).

Milestone 1 - multistart fix:

Root cause of "multistart identical to seq_milp on 813/813 pairs": generated instances use
`layout_mode: "fixed"` (`application/experiments/generators.py`), and `stage_workflow.py`
forces the T1 `variant` to 0 for fixed layouts, so all joint multistart candidates were the
same plan. Feedback moved shelves anyway via explicit `poses` decisions, so paper-v2 compared
a layout-editing arm against arms that could not edit layout.
Fix: new `application/feedback/restarts.py` (seeded random walk of geometry-valid move/rotate/
swap edits on unlocked shelf poses, seed = job seed * 1000003 + variant; T2/T3 re-optimized;
topology still checked on evaluation). `coordinator.py` multistart now evaluates these
restarts, emitting `MULTISTART_RESTART` trace events (FAILED with RESTART_UNAVAILABLE/
DUPLICATE when none). Non-joint `workflow.py` multistart unchanged. README/design doc updated.
All paper-v2 and pilot multistart numbers are superseded for this arm.

Verification (2026-10-26, repo root):
- New test `test_multistart_restarts_differ_on_generated_fixed_layout` failed before the fix
  (1 distinct layout of 3) and passes after.
- `.venv/Scripts/python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var/pytest-ms-full-03`:
  198 passed, 1 existing Starlette/httpx warning (166 s) with local MongoDB started by
  scripts/start_mongodb.ps1 (an earlier run without MongoDB: 165 passed, 4 failed, 29 skipped).
- ruff (backend/pyproject.toml) PASS; mypy src 103 files PASS;
  `scripts/verify_architecture.py --output var/architecture-ms-01.json` PASS.
- Probe only (not an experiment): tiny_f6 / small_f4, seeds 1-3, candidate_count 3: all
  restarts feasible; selected restart improves on candidate 0 in 5/6 cases; 0.8 s / 6 s.

Next (from the review, not started): equal-budget baseline counted in evaluations (random
search/SA on poses), evaluation-count budgets instead of wall seconds, re-run X5 ablation,
calibrate T4 arrival rate to utilization 0.6-0.85, more orders per test fold, then a small
pilot before regenerating paper configs.

---

# Current handoff - paper experiments restarted on this checkout, 2026-10-23

LATEST 2026-10-24: user cancelled the full experiment publication and requested
all project files EXCEPT the root experiments/ directory on GitHub. This replaces
the earlier full-archive instruction below. Stopped only publication Python/gh
processes; numerical finalizer, application services and original E data remain
untouched. Publication status is CANCELLED_BY_USER. Remove the newly created
experiments-2026-10-24 draft release and its uploaded assets, and untrack the
entire root experiments/ directory while preserving every local file. Added a
root-anchored .gitignore rule to prevent accidental future staging. Git history
is retained; removing this folder from main does not purge older commits.
Release 422727820 deletion verified by authenticated HTTP 404; its four uploaded
ZIP assets were removed with it. No matching remote tag existed. Exclusion commit
0e908377 pushed successfully. Git now tracks zero entries in root experiments/;
all 1805 formerly tracked local entries remain (1803 regular files and two
pre-existing broken pytest aliases, verified with lexists). No publisher/upload
process remains. The publication entrypoint now refuses to start while status is
CANCELLED_BY_USER; this refusal was freshly tested without changing that status.
No runtime application source or experiment result was changed by this reversal.
Next step: keep experiments/ local unless the user explicitly changes this scope.

2026-10-24 GitHub publication explicitly authorized, including raw experiments.
Primary checkout E:/Smart_Retail_Floor_Allocation; owner/credential identity
THANHTAI2004 freshly verified using Git Credential Manager and authenticated API.
Original local commit 65c1d35e is recoverable at
refs/archive/pre-publication-20261024; the original index is copied to ignored
var/github-publication/index.before-publication. Three >100 MiB migration
inventories/logs are preserved on disk and moved from the proposed Git tree to
the complete experiments release payload, because ordinary GitHub blobs cannot
accept them. No original scientific files were edited or deleted.
Fresh verification: backend Ruff PASS; source diff whitespace check PASS;
test_experiment_platform.py: 29 passed, 1 existing Starlette deprecation warning
in 71.67 s. Generated SVG whitespace is retained to preserve report artifacts.
Full experiment archive/publication runs via scripts/publish_experiment_archive.py.
Check var/github-publication/status.json and stdout/stderr logs for actual state;
do not claim full upload until COMPLETE and all remote asset digests match.
Release target: experiments-2026-10-24 in the existing owner repository. It stays
draft until independent ZIP replay and remote SHA256/size verification finish.
Next step: push main, complete the archive upload, verify the published release.

2026-10-24 cleanup recovery: primary worker paused at 648908 deleted files because
disk_usage raised WinError21 (device not ready) while sampling volume free space.
E application/data remained accessible. D:/Smart_Retail_Floor_Allocation is now
absent; do not recreate it or claim this worker removed it. Patched optional
free-space sampling to tolerate unavailable volumes, skip absent source roots,
resume cumulative counts/logs and leave first-pass retained files for post-pass.
Resumed cleanup wrapper 36368; updated finishing PID is in process.json. Old error
completion receipt archived under duplicate-cleanup/history. After resume, status
RUNNING, 660172 deleted, zero per-file delete errors. Primary E reports checksum
manifest and all 20 campaign metadata sentinels freshly PASS before resume.

Backup scope clarification: only current experiment C-origin files were fully
consolidated (742103); this does NOT mean all historic SmartRetailBackups archives
from 20261021/22/23 have standalone equivalents in E. Unproven database/ZIP/patch
history remains retained pending content matching; never blanket-delete it merely
because the current research results are present on E.

2026-10-24 cleanup clarification: user asked why C runtime/backup directories
remained. C:/Users/admin/Documents/SmartRetailRuntime was only a junction to the
old D runtime. Removed that junction itself after confirming no process used it;
no target data was deleted and E/experiments/runtime/external remains present.
Receipt: experiments/migration/duplicate-cleanup/removed-old-runtime-junction.json.
Backup cleanup is still RUNNING; at this check 457420 duplicate files deleted,
C free-space gain ~61.26 GiB, zero errors. First-pass retained count 9524 consists
of unmatched historical backups, database/zip/patch files and old evidence; these
are pending the verified-content post-pass, not blanket authorization to delete
all backup history. Empty directories are removed only at the end.

LATEST 2026-10-24 18:37 UTC+7: user explicitly authorized deleting outside-E
files already present on E to reclaim disk space. This supersedes earlier blanket
instructions to retain the old D checkout/C snapshots for byte-identical copies;
different or unproven versions remain protected. Running cleanup sources are ONLY
C:/Users/admin/Documents/SmartRetailBackups and D:/Smart_Retail_Floor_Allocation.
Primary E project is never a deletion source. System Python/user folders outside
these named roots are excluded, and no reparse-directory traversal is allowed.

Each source deletion follows independent E-volume SHA256 equality and stable
source/target stat checks; locked/read-only files have bounded retries, otherwise
are retained/reported. No directory recursive-delete command is used. A finishing
worker content-matches retained paths against verified E hashes and removes only
empty outside-E directories. Different versions and unique historical archives
are retained. E application and research finalizer remain running.

Primary cleanup wrapper PID 11216; finishing wrapper 32288 (read current
experiments/migration/duplicate-cleanup/process.json before acting). Tools:
experiments/migration/cleanup_verified_duplicates.py and finish_duplicate_cleanup.py.
Progress/action logs/automatic completion receipt live in
experiments/migration/duplicate-cleanup/. At 18:37: 146432 checked, 136908 deleted,
19024180340 logical bytes deleted, no errors; C free-space increased about 17.8 GiB.
This was IN PROGRESS, not a claim all duplicates were already removed. The task
continues in background and keeps Windows awake. Final completion.json records
retained versions and measured free-space changes; do not delete unproven leftovers.

2026-10-24 17:30 UTC+7 C-origin completeness follow-up: fresh receipt-based E stat
audit checked every file in the 20 C-origin campaigns: 741446 files, zero missing,
zero size mismatches. Added 632 runtime files and 5 standalone runtime files.
Found 20 historical paper-*.sha256.json parent manifests that had remained outside
campaign roots in the C snapshot; copied them to experiments/results/20261023-paper-v2
with source/destination SHA256 equality, preserving C originals. Total accounted
C-origin files 742103, original logical bytes 116567224410, matching the original
C inventory exactly. Only runtime progress/process.json differs in size because
the current E PID/root metadata was updated. This is not a scientific artifact.
No source C file missing on E in this audit. Method is presence/size for all
campaign/runtime manifest entries, SHA256 for the manifests and root files;
do not claim a new full-byte hash of every 108.56 GiB artifact. Finalizer continues
VERIFYING. Report: experiments/migration/C-to-E-final-audit/BAO_CAO.md and summary.json.

LATEST 2026-10-24 17:13 UTC+7: user requested merging thuc_nghiem into experiments.
There was only one physical data tree: experiments was a junction to thuc_nghiem.
Removed that junction alone and atomically renamed the physical tree on E to
`experiments/`. It is now a real directory; `thuc_nghiem/` no longer exists on E.
No scientific artifact contents were rewritten or copied. Updated six local
documentation/runtime aliases, 46 operational supplemental config paths, the
two active script references and current user-facing documentation/ignore rules.
Historical immutable artifacts/receipts retain their recorded paths and hashes.
External pre-change metadata snapshot:
C:/Users/admin/Documents/SmartRetailBackups/20261024-experiments-single-root.

Application/API/worker/MongoDB stayed running. Paused only the finalizer/dashboard
for the rename and restarted them against experiments. Current wrappers:
finalizer 35732, dashboard 31116; inspect current process metadata before using IDs.
Logs: experiments/runtime/var/paper-unattended/single-root-finalizer.*.log and
experiments/runtime/external/progress/single-root-server.*.log. Backup target is
E:/Smart_Retail_Floor_Allocation/experiments/backups. Finalizer remains VERIFYING;
do not treat this layout migration as final research-integrity/backup completion.

Fresh checks: 11 path/resource/recovery tests PASS, Ruff on changed scripts PASS,
frozen runtime identity MATCH, user-statistics manifest hashes PASS, 4276 unique
job records preserved (4228 success / 48 failure). API healthy, worker online,
frontend HTTP200, dashboard 4276/4276. Git index preserved during the rename.
Receipts: experiments/migration/rename-to-experiments/receipt.json and
verification.json. Current location guide: experiments/VI_TRI_DU_LIEU.md.

LATEST 2026-10-24 17:03 UTC+7: user authorized completing the transfer and running
on E. Application is now live at http://127.0.0.1:5173, API 8010 healthy,
worker_online=true, and MongoDB process 26784 uses E/var/mongodb/data. Recorded
app wrappers: API 33528, worker 33800, frontend 7116 (recheck var/services.json
and process identity before any stop). Opened and inspected the real browser UI;
existing saved projects load and the worker-ready indicator is visible.

Filled audited gaps without overwriting originals: 235304 real files readback-SHA256
verified, comprising 5481 long-path evidence files and 229823 loose Git objects.
Initial copy stopped on .git/objects/3a/tmp_obj_huVr7y, a source temporary file
that vanished naturally. Resumed after handling only this temporary-name case;
one source temp is recorded as gone, not counted as restored user data. The
second pass verified 177850 already copied files and copied the remaining 57454.
All D source files were read-only inputs. E Git index remained
787306c7a767f26750a2488f4e04f66935899b64abf438157712111de25e2ac4.

Regenerated console/gui launchers and activation scripts directly for E using
the existing environment, preserving numerical libraries and versions. Updated
editable origin and corresponding installed RECORD hashes. No D reference remains
in .venv/Scripts. pip.exe, pytest.exe, uvicorn.exe and activation now use E.
Snapshots of pre-change environment files are external at
C:/Users/admin/Documents/SmartRetailBackups/20261024-E-completion.
Checked 11215 cold MongoDB files by SHA256 against D before first E startup;
all matched. First immediate startup health raced MongoDB recovery; subsequent
health/cutover checks PASS and application startup succeeded. Original D retained.

Fresh checks: frozen complete runtime identity MATCH, pip check PASS, 11 recovery/
resource unittests PASS, 2 real-process integration tests PASS (queue/worker/replay/
report and deep Unicode subprocess write), zero skips; known Starlette/httpx
deprecation warning. Git fsck connectivity PASS. No full backend suite rerun.
Receipt: thuc_nghiem/migration/E-completion/readiness.json (READY_ON_E), with
copy manifest, before-start DB comparison and fresh-process-tests.xml alongside.
VS Code workspace: Smart_Retail_E.code-workspace; project-local interpreter set.
Scientific results unchanged (4276 unique jobs); their finalizer remains VERIFYING
and was not interrupted by launcher repair/copy. Final artifact integrity/backup
completion is separate from this completed transfer/readiness milestone.

2026-10-24 D-to-E read-only audit: 1784 tracked D files all present on E; 1782
SHA256-identical, only .gitignore/HANDOFF differ due documented relocation updates.
789 physical source/assets checked, four expected content changes including the
E path guide/dashboard. Canonical experiment results (1006001 files,
135380429037 bytes), reports (980 files) and database exports (244 files) have
matching file paths and sizes. Full byte comparison of all large artifacts was
not repeated; finalizer remains VERIFYING. Current six Git refs and 50967 reachable
objects match; E fsck connectivity exit 0. No source/config/canonical experiment
file missing in the audited inventory.

The raw copy is NOT fully identical: extended-path retry found 5481 old long-path
test/evidence files (69930056 bytes) absent on E; 229824 loose Git object files
(2058909881 bytes) also absent, none needed by any current ref. Do not delete D
or treat these as worthless. Some copied venv launchers (pip/pytest/uvicorn.exe,
activate.bat/activate) still embed D. Verified pip.exe from E runs D pip, whereas
E python -m pip/import smart_retail use E correctly. No repair/copy/delete/reset
performed in this audit; defer environment rebuild until safe with active finalizer.
Report: thuc_nghiem/migration/audit-D-to-E-20261024T093214Z/BAO_CAO_DOI_CHIEU.md;
CSV lists all missing long-path and Git files. Git indexes unchanged during audit.

CURRENT CHECKOUT 2026-10-24: user explicitly selected
`E:/Smart_Retail_Floor_Allocation` as the authoritative working project after
copying to the larger drive. Do not resume work against the D: checkout. The
previous D: tree and external C: recovery snapshots are preserved untouched.

The preceding consolidation process completed FILES_CONSOLIDATED at 14:48 UTC+7:
20 original campaign folders plus external runtime receipts, 742078 verified files,
108.55 GiB copied/readback-verified. Primary files now reside in `thuc_nghiem/`.
That receipt describes the verified C-to-D consolidation before the user copied
the project to E; it is not a full-byte verification of the user's E: copy.

Copying converted local junctions into empty ordinary directories. Rebuilt only
those aliases inside E to E/thuc_nghiem; no alias points to D. Repaired the copied
venv's editable .pth (it initially imported backend from D), operational supplemental
config paths and the dashboard root/runtime paths. All historical scientific
artifacts and recorded paths remain unchanged. Snapshot of changed operational
files: C:/Users/admin/Documents/SmartRetailBackups/20261024-E-relocation.
E Git index SHA256 remains 8836e4f36df73a84df64d8a5a7e3d7a19106b2dbcf9cc680fcc2888184506760.

Fresh E checks: smart_retail imports from E/backend, complete runtime identity
matches the frozen baseline, 11 recovery/resource checks PASS, Ruff PASS.
Existing-results finalizer wrapper 25700 runs from E with --runner-pid 0;
no scientific rerun is requested. Backup destination E/thuc_nghiem/backups;
source hashing streams with ZIP compression and a 2 GiB free-space guard.
Progress server wrapper 28068 at http://127.0.0.1:8766 reads E data.
Latest logs: thuc_nghiem/runtime/var/paper-unattended/E-finalizer.*.log;
thuc_nghiem/runtime/external/progress/E-server.*.log. Check current metadata
before using any PID. Full integrity verification / final backup still pending.

2026-10-24 13:49 UTC+7 results milestone: all 4276 unique planned jobs have terminal
outcomes. Explicit latest-requested-follow-up selection yields 4228 SUCCEEDED
(all recorded independent validation PASS), 48 baseline T3 SLOTTING_FAILED
(38 X2b, 10 X3), zero unexecuted. Original 3496 attempts + 852 supplemental attempts
= 4348 attempts; supplemental contains 823 target attempts and 29 paired extras.
Original failures 43; all-attempt failures 91 (90 slotting + historical ENOSPC).
Original/follow-up input snapshot hashes match where both exist; generated plan
hashes and normalized worker snapshot hashes have different scopes, so compare
like-for-like. No original outcome overwritten or duplicate job counted.

User requested statistics. New read-only export script `scripts/summarize_paper_results.py`
and report artifacts at
`experiments/reports/20261023-paper-v2/user-statistics-20261024T064920Z/`:
Vietnamese report, JSON selected records and summary, six descriptive CSV tables,
checksums. Fresh uniqueness/count/record-validation/failure-code/CSV/text/checksum
checks PASS; Ruff PASS. No backend/dependency change or fresh full backend suite.
Paired successful test-objective reduction feedback vs baseline: X2 12.94% (450),
X2b 10.66% (180), X3 14.13% (90), X6 28.54% (360). Descriptive only; unsuccessful
baseline pairs excluded from score comparisons but retained in feasibility rates.
X1 exact/hybrid 60/60 finite certificate checks PASS. X5 T1-only exceeds combined
on this small sample; avoid claiming uniform algorithm superiority.

Numerical schedule ended 13:04 UTC+7. Watcher still VERIFYING at export time;
no final all-artifact integrity/report/backup completion receipt yet. Preserve
that distinction when reporting completion and do not interrupt the verifier.

2026-10-24 09:54 UTC+7 diagnostic update: user asked whether higher CPU utilization
could accelerate the batch. Read-only measurements show ~38.5% total CPU, RAM 73%,
~6.2 GiB available. In the last 11 X6 intervals, mean completion intervals were
608.4 s / 442.6 s, versus worker wall times 7.56 s / 20.90 s. Significant time lies
outside recorded worker execution; independent replay, JSON/artifact processing
and full-root fingerprints are candidates, not yet individually profiled. Snapshot
process counters showed both X6 supervisors reading ~8-9 MB/s; physical disk 4%
busy, queue 0 (single sample). Other processes also consume total CPU, including
Defender. No affinity, priority, security, power, campaign limit or engine changes.
Evidence: `var/paper-parallel/throughput-diagnosis-20261024.json`.

LATEST 2026-10-24 06:52 UTC+7: user authorized rerunning budget-limited states
and failed jobs. Explicit additional-budget recovery is now RUNNING alongside X6.
Coordinator wrapper 27196 adopted both X6 supervisors without terminating them;
watcher wrapper 32764 is MONITORING with keep-awake. Latest logs:
`var/paper-parallel/recovery-runner.*.log`,
`var/paper-unattended/recovery-watcher.*.log`; authoritative PID metadata unchanged
in location. Dashboard process metadata remains in SmartRetailRuntime/progress.

`scripts/paper_recovery.py` created 21 small immutable campaigns for 590 requested
keys (557 previously unexecuted + 33 failed). Their full fold configurations execute
618 jobs, including 28 explicitly labelled paired-fold duplicates, excluded from
the 4276 unique-job progress. Every generated job key and input SHA256 was checked
against the frozen original plan. Original configurations, inputs, spent budgets,
records and scientific source remain unchanged; new shards have their own 14400 s
campaign budget, namespace, configs and provenance. Data is under new retry-* roots
on D:, avoiding additional pressure on the original C: campaign storage.

Recovery index/configs: `var/paper-parallel/recovery/`. Coverage records original
and follow-up outcomes separately, plus unique primary-job coverage. Baseline may
deterministically fail again; no algorithm substitution is allowed in this rerun.
Historical outcomes are never silently replaced or dropped from the original reports.
Watcher verifies and reports supplemental campaigns separately and includes coverage
in final receipts/backups. Original partial report counts remain historical; use
the explicit coverage manifest to account for missing jobs and diagnostic retries.

Scheduler now runs X6+RECOVERY before X3 and discovers additional omissions/new
failures when original campaigns finish. Recovery target keys are scheduled once,
not retried forever on deterministic baseline failures. Adaptive three-to-two cap
and one-job optional slot remain. The live dashboard includes recovery ownership,
target progress and previously missing keys without counting paired duplicates.

Fresh verification: 11 tests PASS (input reconstruction/paired folds/deterministic
shards plus resource guard), Ruff PASS, frozen runtime and Git index unchanged.
First retried disk-error key SUCCEEDED on identical input; no claim all recovery
jobs have finished. No full backend suite rerun for these orchestration changes.
Pre-handover verified external snapshot:
`C:/Users/admin/Documents/SmartRetailRuntime/recovery-handover-20261024/`.

LATEST 2026-10-24 06:38 UTC+7: inspected all 33 FAILED canonical records.
32 are baseline T3 SLOTTING_FAILED in paper-x2b-small: first-fit exhausted its
placement choices under size/facings/load checks, not a proof of infeasibility.
The same 32 dataset/seed/fold/repetition combinations all SUCCEEDED under each
of seq_milp, multistart and feedback (upstream decisions may differ). Failed
baseline workers used ~125.4-126.6 MiB peak RSS and ~1.97-2.31 s; none of these
records reports OOM, CPU timeout or crash. Remaining failure is historical ENOSPC,
whose exact-input diagnostic recovery receipt remains verified. No engine edit
or replacement of original outcomes was performed for this diagnosis.
X6 campaigns are live, watcher MONITORING; 2849/4276 terminal records at 06:37.
SEPARATE OPEN ISSUE: campaign wall-budget stops left 557 jobs unexecuted across
X2 tiny part01 (486/800), X2 small (397/600), X2b small (360/400). These are not
part of the 33 FAILED records. Current watcher excludes NOT_EXECUTED_RESOURCE_LIMIT
from automatic restart, so current schedule alone cannot claim all 4276 executed.
Do not silently reset spent budgets or alter frozen configurations; continuation
requires explicit provenance for the additional campaign budget and omitted job keys.
Evidence: `var/paper-parallel/failure-diagnosis-20261024.json`.

LATEST 21:40 UTC+7: user explicitly requested uninterrupted continuation through
the entire batch, not a stop after X2. Verified existing live coordinator iterates
all groups X1, X4, X2+X2b, X5, X6, X3, with no X2 stop gate. Both coordinator
and watcher ownership PIDs are alive, watcher MONITORING and keep-awake true;
frozen runtime identity still matches. All 20 campaigns / 4276 planned jobs remain
scheduled, with adaptive 3-to-2 resource control retained. On completion the watcher
verifies integrity, generates/verifies pooled reports and attempts a verified backup
to E:/SmartRetailBackups. Historical failed outcomes remain in the final accounting.
No process restart or algorithm/config change was needed for this instruction.
Receipt: `var/paper-parallel/continuous-authorization.json`.

LATEST 21:34 UTC+7: user authorized three simultaneous campaigns with automatic
fallback to two on RAM pressure / CPU contention. New coordinator wrapper 30860
adopted both live X2 supervisors without stopping any scientific process; watcher
wrapper 32348 is MONITORING with keep-awake accepted. Current logs are
`var/paper-parallel/three-slot-runner-v2.*.log` and
`var/paper-unattended/three-slot-watcher-v2.*.log`; process metadata is authoritative.
X2 and X2b now share the available slots (independent fixed-input campaigns); other
block barriers remain and X3 still runs last. Scientific source/configs/budgets unchanged.

`var/paper-parallel/concurrency.json` requests 3 slots. OS sampling every 5 seconds
latches the cap to 2 if RAM >=90% or available RAM <2 GiB for 15 seconds, CPU >=95%
for 120 seconds, or a new terminal memory/resource/worker-crash outcome appears
(TIMEOUT counts only alongside sampled CPU >=90%). These are conservative triggers,
not proof of the failure cause. Pre-existing failures do not trigger this transition.
Optional third-slot launches use `--max-new-jobs 1`: on fallback the current job
finishes, then no replacement starts until at most two campaigns remain. No current
job is cancelled and the original result is retained. The cap stays at 2 across restarts.
This adds per-job resume/integrity overhead for the optional slot; throughput gains
are not yet measured, and concurrency can affect wall-budget-limited outcomes.

Verified external pre-change copies at
`C:/Users/admin/Documents/SmartRetailRuntime/three-slot-handover-20261023T213110/`.
First new coordinator launch rejected a UTF-8 BOM in the control JSON; corrected
the new metadata to UTF-8 without BOM and restarted only the coordinator/watcher.
Both original campaigns continued throughout; failed launch logs retained.
Fresh validation: 8 resource-policy tests PASS, Ruff on four changed/new orchestration
and test scripts PASS, runtime identity matches frozen baseline. Live third campaign
completed two one-job slices and resumed successfully; initial sample CPU ~37%, RAM
68%, available ~7.6 GiB. No full backend suite rerun for this scripts-only milestone.
Receipt: `var/paper-parallel/three-slot-handover.json`; subsequent live verification
is recorded at `var/paper-parallel/three-slot-verification.json`.

LATEST 18:57:43 UTC+7: resumed two X2 Tiny campaign processes after disk-full outage.
Coordinator wrapper PID 19324; watcher wrapper 3708, backup root E:/SmartRetailBackups.
Current logs `var/paper-parallel/storage-recovery-runner.*.log` and
`var/paper-unattended/storage-recovery-watcher.*.log`. Latest PID metadata files
supersede all historical PID instructions below. Keep-awake and MONITORING verified.

Live progress dashboard OPEN: http://127.0.0.1:8766 (read-only, refresh every 5 s).
Source `scripts/paper_progress/server.py` + `index.html`; process metadata at
C:/Users/admin/Documents/SmartRetailRuntime/progress/process.json. It shows real
record counts, block bars, active campaign ownership, errors and disk capacity.

At ~18:02 D: filled, MongoDB exited, coordinator/watcher stopped. 758 canonical
records survived: 757 SUCCEEDED, 1 EXECUTION_ERROR explicitly caused by ENOSPC.
User subsequently freed D: space. Verified relocation of all 20 campaign directories
(full file SHA-256 comparison) to C:/Users/admin/Documents/SmartRetailRuntime/paper-v2-results;
original D: campaign paths now junctions. Entire campaign roots were relocated so
integrity confinement remains valid. Because resolved-root hash determines DB name,
copied original campaign DBs to the new namespaces via verified BSON backup/restore,
checked all recorded job run IDs, collection counts and existing integrity manifests
for all 20 campaigns. Old DB namespaces retained. Engine/dependency identity unchanged.
Receipts: `var/paper-storage-recovery.json`, external `relocation.json`,
`database-relocation/journal.json` and `completion.json` under SmartRetailRuntime.

The failed canonical multistart/seed2/fold1 job was replayed in a separate 10-fold
diagnostic campaign at SmartRetailRuntime/disk-job-recovery-v2: 10/10 SUCCEEDED,
independent validation PASS, identical input SHA-256 for the failed job. Original
failed record is retained, not replaced or silently excluded from statistics.
Initial diagnostic helper lacked the Windows multiprocessing main guard; that
attempt is retained separately at disk-job-recovery and was corrected for v2.
No primary experiment code or prior scientific result was changed.

Scheduler now refuses to start another campaign below 2 GiB free on actual storage
and skips orphaned log filenames after ENOSPC. Fresh Ruff checks PASS; actual new
canonical jobs SUCCEEDED after resume, old records' hashes remain available in the
storage receipt for verification. New dashboard and storage changes do not alter the
historical 198-test verification scope. No commit/push/index changes performed.

User authorization at ~17:00 UTC+7: diagnose/fix failed jobs and continue without
asking again for routine repairs; preserve originals and verify any patch. No job
failure present at this milestone (331/331 recorded jobs SUCCEEDED). Watcher now
scans terminal job outcomes every 30 s, writes immutable classified alerts and
copies input/error/receipt/progress evidence to `var/paper-unattended/job-errors/`.
Resource limits/search outcomes remain distinct from code defects. Campaign already
retries WORKER_CRASH/WORKER_LOST within its configured cap; watcher also retries DB
health three times before a bounded supervisor resume. Unknown software faults are
NEEDS_CODE_DIAGNOSIS, not automatically patched by the Python watcher. An active
assistant must reproduce/test the fix and use a new source identity/output namespace
if backend/dependencies change; never mix patched and original scientific results.
Updated watcher PID/start time is in `var/paper-unattended/process.json`; logs are
`live-alerts-watcher.out.log` and `live-alerts-watcher.err.log`. Numerical coordinator
and children were not restarted. Ruff plus classification/evidence/idempotence/
original-retention checks PASS; backend runtime identity remains frozen.

CURRENT EXECUTION MODE (user authorized parallelism, 14:03:45 UTC+7): two independent
campaign processes via `scripts/run_paper_parallel.py`, wrapper PID 27548, actual
coordinator PID 3232. This supersedes sequential-runner PID instructions below.
Active initially: X4 small and X4 medium part01; two slots maximum, barriers between
blocks, X3 remains last. Each campaign still has workers=1 and its own DB/artifacts.
No backend source, dependency, objective, input config or job budgets changed.

Controlled handover: external readback/hash-verified snapshot (266 entries) at
`C:/Users/admin/Documents/SmartRetailBackups/20261023T070215Z-parallel-handover/`.
Waited for X4 small checkpoint to advance to 23 completed jobs, then set owned
campaign cancellation flags at the post-job fingerprint boundary. Sequential
runner exited normally; cleared only those owned flags after exit. All 233
completed records remained SUCCEEDED; 235 pre-existing immutable record/identity
files match their snapshot hashes. No numerical job was cancelled mid-execution.
Future campaigns have zero-job CANCELLED checkpoints from this controlled pause;
the parallel coordinator resumes them. They are pending, not abandoned experiments.

New progress/logs: `var/paper-parallel/status.json`, `journal.json`, `runner.out.log`,
`runner.err.log`, per-campaign attempt logs. `var/paper-v2-run.pid.json` now points
to the new coordinator; old sequential log/journal retained as transition history.
Old X4 root report is PARTIAL from handover. Final verified report paths will be
listed in `var/paper-unattended/completion.json`; do not treat that partial X4
report as the complete result. Watcher recreates incomplete reports in new dirs.

Unattended watcher wrapper PID 37416 (actual 8092); keep_awake=true confirmed.
It resumes with `--runner-script scripts/run_paper_parallel.py`, preserves the
two-slot mode on bounded retry, verifies/reports/backups after all supervisors exit.
Final reports include an execution-mode receipt and per-campaign scheduling log.
Do not pool sequential/parallel wall times as a controlled speed comparison;
concurrency may affect time-bounded search outcomes. Source identity stays fixed.

Validation: Ruff scripts PASS, 20 configs/4,276 jobs recognized; two-slot/barrier
checks PASS; both resumed campaigns have new SUCCEEDED jobs, with two active
campaign supervisors observed. Available RAM about 11 GiB at initial measurement;
no observed resource-limit failure. Whole-run throughput/ETA not yet remeasured.
Historical 198-test engine verification remains historical for unchanged backend;
no full suite rerun for this script-only scheduling change.

Unattended authorization (23/10, user will leave machine on): execute the full
paper batch. Existing runner retained; do not launch a duplicate. Added
`scripts/watch_paper_campaigns.py`, started 06:50:44Z with runner PID 30636;
watcher wrapper PID 36480, actual watcher PID 11564 (verify live identities).
Status `var/paper-unattended/status.json`, process/lock/logs in the same directory.
Windows keep-awake request accepted (`keep_awake: true`); AC sleep already disabled,
machine plugged in at 100% battery. No global power settings changed.
Watcher waits for all numerical supervisors to exit, allows at most two bounded
lease-aware resumptions after interruptions, verifies campaign and report hashes,
then creates/readback-verifies an external ZIP under
`C:/Users/admin/Documents/SmartRetailBackups/<UTC>-paper-complete/`.
Final receipt: `var/paper-unattended/completion.json`; exceptions are recorded in
`failure.json` and status NEEDS_ATTENTION. Missing jobs, unsuccessful jobs or
incomplete held-out evaluations produce FINISHED_WITH_LIMITATIONS, never a false PASS.
Ruff script PASS; check-only recognizes all 20 configs / 4,276 jobs, completed-X1
verification PASS (150 records), X1 report 110-file checksum check PASS, small
backup/write/readback probe PASS. Final unattended completion has not yet occurred.
Numerical backend/dependency identity still matches verified preflight.

User requested code review and continuation of experiments. Started from clean main
at b94b2f706c1ceec1af89b8025cfd56fd1778a3a6. The paper-v2 raw-results directory
and stopped-run PID files described below were absent on this machine, so this is
a fresh paper-v2 run, not a resume of the historical 18 jobs. Historical results
remain unchanged. No commit/push/index changes authorized or performed.

Fixed and regression-tested pooled reporting before the numerical run: aggregate
joint CSV/trace/convergence exports across all campaigns once (previously the second
campaign raised FileExistsError), and retain all seed partitions in exported deepmg
arm configs. A real two-campaign worker test checks CSV/trace coverage and exact job
key reconstruction from the exported config. No solver/objective/config changes.

Fresh verification on frozen source: 198 pytest PASS, 0 FAIL/SKIP in 106.12 s
(`var/continue-20261023-01/pytest-frozen.xml`); Ruff backend+scripts PASS, mypy 102
files PASS, architecture 102 Python/40 frontend modules PASS; frontend lint/build
PASS and 4 Vitest PASS; pip check PASS; 7 stored input schemas match contracts.
Preflight validated all 4,276 job inputs in 20 paper-v2 configs and saved source
and dependency identity plus file hashes in `var/continue-20261023-01/`.
Unsuccessful preliminary checks and their causes are recorded in
`docs/research/CONTINUATION_20261023.md`; do not count them as passing checks.
Playwright/Compose were not rerun at this milestone.

Paper runner started 2026-10-23T06:35:59Z (13:35:59 UTC+7), initial PID 30636,
using `.venv/Scripts/python.exe -u scripts/run_paper_campaigns.py`, hidden/detached.
PID/start time/HEAD/index hash: `var/paper-v2-run.pid.json`; logs:
`var/paper-v2-run.log`, `var/paper-v2-run.err.log`. Results:
`experiments/results/20261023-paper-v2/`; reports:
`experiments/reports/20261023-paper-v2/`. Order X1, X4, X2, X2b, X5, X6, X3.
Check current processes/checkpoints before any further launch; do not duplicate the
runner or edit backend/src Python/dependencies while it runs. The complete batch
is NOT yet verified; historical ~27 h is only an estimate. Next: verify completed
campaign integrity/results and report per block; retain every failure/timeout.
Details and current evidence: `docs/research/CONTINUATION_20261023.md`.

Milestone 13:45 UTC+7: X1 COMPLETED 150/150 SUCCEEDED, all independent validations
PASS, 548.548 s campaign wall. Integrity PASS for 12,095 manifest JSON files.
All 30 exact and 30 hybrid jobs have GLOBAL_OPTIMAL_CERTIFIED with certificate
verification PASS; their scores match per seed. Separate offline exact seed-1
certificate replay PASS (4 states), receipt `var/continue-20261023-01/offline-proof.json`.
Report `experiments/reports/20261023-paper-v2/X1/`: 150 rows, 5/5 arms complete,
6 PNG/SVG figures; all 110 files in report manifest verified by SHA-256.
Mean objective: baseline/multistart 0.1527143397, feedback 0.1427143397,
exact/hybrid 0.1027143397. These are local_trap synthetic results, not held-out
generalization findings. Runner has advanced to X4 tiny (15/60 at 06:45:58Z).
Machine-readable receipts: `var/continue-20261023-01/verification.json`,
`x1-summary.json`, `preflight.json`; frozen-source.zip readback/hash verified.

---

# Previous handoff - repeated k-fold held-out evaluation (deepmg protocol), 2026-10-23

Request: direction A paper experiments designed after deepmg (pypi.org/project/deepmg):
repeated stratified k-fold over orders, deepmg-style result files. Design and findings:
docs/research/EXPERIMENT_DESIGN_DEEPMG.md. Uncommitted; no commit/push authorized.

Implemented: campaign schema 1.1 `evaluation` (kfold/temporal_holdout; seed = repetition),
`DatasetSpec.facings`, `application/experiments/splits.py` (stratified folds, immutable
`datasets/<id>/splits/<seed>.json`), `application/evaluation.py` (demand re-estimated from
training orders; optimization on (1-budget_fraction) budget; fixed decisions replayed and
independently verified on held-out orders in the same killable worker process; engines never
see held-out orders because `to_domain` strips `optimization.evaluation`), analysis
(pairing unit (seed, cv_fold), Wilcoxon, Nadeau-Bengio, A12, bootstrap CI, Friedman/Nemenyi,
Holm per family, objective-definition guard), reports (fold_results/run_means/status_matrix/
rankings CSV, pooled multi-campaign analyze), `partition.py` + CLI `split-config`, and
`deepmg_export.py`: `<report>/results/<prefix>/<prefix>_file_sum[_ok].txt`, `_file_eachfold.txt`,
`_file_mean_test_objective.txt`, `_file_mean_test_distance.txt`, `_config.json` (repeats the arm
with identical job keys). Optimization/input schemas regenerated. Inputs and campaign
manifests without `evaluation` keep their previous canonical form.

Two pre-existing defects found and fixed: (1) SimPy re-raises process failures as
`type(exc)(*exc.args)`, so every T4 TIMEOUT surfaced as EXECUTION_ERROR (EngineError now
keeps args=(code, message)); (2) unvalidated int defaults of CampaignSpec job_time_limit_s/
max_wall_s hashed differently after a JSON round trip (defaults now float).
Generator finding: default `facings=1` instances are degenerate (all categories fit one shelf,
identical routes); experiments must use facings >= 4/6.

Environment set up on this checkout: `.venv` (Python 3.12, requirements-lock, editable backend)
and portable MongoDB 8.0.16 via scripts/start_mongodb.ps1 -InstallPortable (credentials in
ignored var/mongodb/private.json). core.autocrlf is true here.

Verification (actual commands, from repo root):
- `.venv/Scripts/python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var/pytest-cv-full-05`:
  196 passed, 1 existing Starlette/httpx deprecation warning (113 s).
- `ruff check backend`: PASS; `mypy src` (in backend): no issues in 102 files;
  `scripts/verify_architecture.py --output var/architecture-cv-03.json`: PASS.
  `ruff check experiments scripts` reports 16 pre-existing findings in untouched files.
- Pilot `experiments/configs/pilot_cv.json` (2 instances x 4 joint-scored arms x 1 repetition x
  10 folds = 80 jobs, 60 s/job, budget_fraction 0.25):
  `experiments/results/20261023-pilot-cv-03` COMPLETED 80/80 SUCCEEDED, all held-out
  evaluations COMPLETED, 1,382 s. Report and deepmg layout: `experiments/reports/20261023-pilot-cv-03`
  (8/8 arms `_file_sum_ok`).
  Superseded, retained: pilot-cv-01 (FAILED at 55/80: source edited during run, drift guard
  correct); pilot-cv-02 (80 jobs, 3 feedback jobs EXECUTION_ERROR from defect (1)).
- Pilot observations (one repetition, exploratory, SYNTHETIC): greedy/MILP/multistart sequential
  arms gave identical plans on both instances; feedback lowered held-out objective
  (tiny -0.0136, small -0.0055; Wilcoxon p 0.0098/0.0020, Nadeau-Bengio p 0.019/0.0013,
  Holm-NB 0.153/0.014). Mean wall per job: tiny 2.4-16.8 s, small 4.8-49.2 s (feedback small
  max 49.7 s of 60 s, budget nearly binding).

Main paper run STARTED 2026-10-23: `scripts/build_paper_configs.py` generated 16 configs
(4,276 jobs; X2 tiny auto-split into 2 parts) in `experiments/configs/paper/` (index.json).
Runtime probes before sizing: medium facings=4 and large facings=4 are INFEASIBLE (a category
exceeds one shelf's 3.8 m); medium f=3 sequential 36-39 s, feedback hits a 225 s budget after
10 evaluations; large f=2 cannot finish T4 within the 300 s contract cap (kept in X4 with 4 jobs
to document the limit). Detached runner: `scripts/run_paper_campaigns.py` (pid in
var/paper-run.pid.json, log var/paper-run.log), order X1, X4, X2, X2b, X5, X6, X3; resumable
(rerun the same command); results `experiments/results/20261023-paper/<campaign>/`, journal
`experiments/results/20261023-paper/journal.json`, pooled reports with deepmg layout
`experiments/reports/20261023-paper/<block>/`. Estimated ~20 h sequential.
Do NOT edit backend/src Python files until the runner exits (drift guard).

SUPERSEDED by paper-v2 (same day): in run v1 every medium feedback job ended TIMED_OUT at
302 s, mostly after reaching stage COMPLETE, because the worker allowed only 2 s grace after
the solver budget for verification/result writing. User chose: add finalization grace and raise
the cap to 900 s. Changes: `workers/runner.py` `wall_budget(limit) = limit + max(15, 0.1*limit)`;
`OptimizationInput.time_limit_s` and `CampaignSpec.job_time_limit_s` cap 300 -> 900 (schemas
regenerated); feedback CLI and ResearchPage.tsx limits 900 (frontend lint/build/Vitest NOT run:
frontend node_modules absent in this checkout). Verification: 197 pytest passed (basetemp
var/pytest-cv-full-06), ruff backend+scripts PASS, mypy PASS, architecture PASS (cv-04).
v1 run stopped by killing runner pid 11652 and its worker children; its partial results stay in
`experiments/results/20261023-paper/` (X1, X4 tiny/small COMPLETED, X4-medium partial) as
superseded evidence. Run v2: configs `experiments/configs/paper-v2/` (900 s medium/large,
split into <=24-job parts to stay below the 4 h campaign wall ceiling; 4,276 jobs), runner
pid in var/paper-v2-run.pid.json, log var/paper-v2-run.log, results
`experiments/results/20261023-paper-v2/`, reports `experiments/reports/20261023-paper-v2/<block>/`.
Resume command: `.venv/Scripts/python.exe scripts/run_paper_campaigns.py`.

STOPPED at user request ("chỉ sinh lại thôi"): configs are generated, the v2 run was stopped
deliberately (runner pid 5000 and children killed) with paper-x1-exact at 18/150; nothing else
started. Step-by-step instructions for whoever runs it next:
docs/research/PAPER_EXPERIMENT_RUNBOOK.md.

---

# Bàn giao hiện hành — 23/10/2026

## Phạm vi được ủy quyền

Người dùng yêu cầu viết lại README tiếng Việt dựa trên source, sau đó mở rộng
phạm vi sang dọn các thành phần persistence không còn sử dụng trong mã nguồn và
tài liệu hiện hành. Người dùng chọn giữ nguyên bằng chứng lịch sử trong bản lưu
ngoài dự án. Không có ủy quyền commit/push cho công việc này.

Ứng dụng hiện hành dùng MongoDB/PyMongo đồng bộ, GridFS, durable worker queue và
process con. Không thay thuật toán, objective, input contracts hoặc business data.
`backend/src/`, `frontend/src/`, datasets và scientific results được giữ nguyên.

## Bản lưu và thay đổi

Trước chỉnh sửa: Git worktree sạch tại HEAD
`7c47eca2d7d4377968d1380a6b1fbdb5f0d32afc`. Snapshot ngoài dự án:

```text
C:/Users/admin/Documents/SmartRetailBackups/20261023-documentation-cleanup-c0a98c35/
```

`tracked-before.zip` chứa 1.664 tệp; mọi mục ZIP được đọc lại và kiểm tra SHA-256.
`manifest.json` ghi hash tệp và archive. 66 tệp nguyên bản được chuyển sang
`historical-files/` với kiểm tra SHA trước/sau; `relocation-plan.json` liệt kê
chính xác. Một số đường dẫn tài liệu được tạo lại bằng nội dung hiện hành.
Hồ sơ cũ không bị sửa để giả làm kết quả mới.

Đã gỡ nhánh deployment verifier không còn thuộc phạm vi, giữ CLI `compose`;
gỡ wrapper riêng, cập nhật env examples và phạm vi các verification collectors.
Archive helper bảo toàn dữ liệu chỉ dành cho audit cũ được chuyển cùng hồ sơ
vì phụ thuộc một biên bản đã rời checkout. Mypy chạy không incremental và không
ghi cache; kiểm tra kiến trúc vẫn bảo vệ ranh giới persistence.

README được xây lại đủ 24 phần, 17 Mermaid, 23 bảng, gồm mô hình dữ liệu,
MongoDB, T1–T4, feedback/exact/hybrid, UI/API, E01–E15, Windows/Compose,
replay, kiểm thử và giới hạn khoa học. Các tài liệu hiện hành và inbound links
được cập nhật; báo cáo audit còn lại được đánh dấu bản tóm lược lịch sử.

## Kiểm chứng mới

- Ruff theo `backend/pyproject.toml`: PASS cho backend/source/tests và bốn script
  đã thay đổi. Lần gọi ban đầu thiếu `--config` áp dụng rules toàn cục ngoài
  cấu hình dự án và báo lỗi ở script; lần đúng cấu hình PASS.
- `.venv/Scripts/python.exe -m mypy --config-file backend/pyproject.toml backend/src/smart_retail`:
  PASS, 98 source files.
- `.venv/Scripts/python.exe -m pip check`: PASS.
- `.venv/Scripts/python.exe scripts/verify_architecture.py --output var/architecture-current-20261023-01.json`:
  PASS, 98 Python modules và 40 frontend modules.
- `npm.cmd --prefix frontend run test`: 4/4 Vitest PASS.
- Full backend: `.venv/Scripts/python.exe -m pytest backend/tests -q --tb=short
  --basetemp var/current-verification-95a87e2b/pytest
  --junitxml var/current-verification-95a87e2b/pytest.xml`:
  **178 PASS, 0 FAIL, 0 SKIP**, 87,22 giây, một warning Starlette TestClient/httpx.
  Receipt/log ở `var/current-verification-95a87e2b/`.
- Lượt backend đầu dùng runtime mặc định không truy cập được database: 146 PASS,
  3 FAIL và 29 SKIP do thiếu kết nối. Lượt sau dùng process MongoDB thử nghiệm
  riêng, cổng trống, data directory mới và prefixes riêng; process đã dừng trong
  `finally`. Không restart dịch vụ chính và không ghi vào database nghiệp vụ.
- Markdownlint kiểm tra README; cho phép dòng bảng/JSON dài, explicit HTML anchors
  và heading trình bày. Mermaid 11.12.2 parse và render 17/17 trong Chromium.
  Công cụ QA, HTML, screenshot và JSON kết quả đặt ngoài dự án trong bản lưu trên.
- README cuối: 1.339 dòng, 24 chương, 17 sơ đồ, 23 bảng; 24 anchor duy nhất,
  86 liên kết hợp lệ, bảy ví dụ JSON được validate bằng chính contracts và
  `to_domain`. Không có liên kết nội bộ hỏng trong các tài liệu còn lại.
- Quét toàn bộ tệp văn bản được quản lý còn tồn tại và tệp mới: không còn tham
  chiếu các thành phần người dùng yêu cầu gỡ. UTF-8, dấu tiếng Việt và
  `git diff --check` PASS. Git HEAD/index khớp trước thao tác.
- So SHA-256 với snapshot trước sửa: giữ nguyên 98 tệp backend source, 41 tệp
  frontend source, 19 dataset/schema files, 16 experiment configs, 434 tệp
  kết quả và 580 tệp báo cáo đã được Git quản lý.
- Policy từ chối xóa một thư mục bằng chứng đã rỗng. Tệp nguyên bản bên trong
  đã được lưu ngoài và kiểm tra hash; thư mục rỗng còn giữ tại checkout.
  Không dùng phương thức khác để vượt qua việc từ chối.

## Phạm vi kết luận

Các kết quả 178/4/10 và 24 gates ngày 22/10 trong tài liệu audit là lịch sử.
Lượt hôm nay có backend 178 và Vitest 4 như ghi ở trên, chưa chạy lại Playwright
ứng dụng, Docker Compose build/runtime hoặc toàn bộ campaign nghiên cứu.
Render Mermaid là kiểm chứng tài liệu, không phải kiểm chứng UI sản phẩm.

Không sửa thư viện hệ thống, môi trường dependency, cơ sở dữ liệu chính hoặc
lịch sử Git. Các working-tree removals chưa được stage/commit/push.
Lịch sử nguyên bản và địa chỉ bản lưu: [HISTORICAL_ARCHIVE](docs/architecture/HISTORICAL_ARCHIVE.md).
Kiểm tra cuối về đường dẫn, UTF-8, phạm vi thay đổi và Git diff được ghi cùng
receipt QA bên ngoài. Bước triển khai tiếp theo chỉ cần khi người dùng yêu cầu;
không tự khởi động lại dịch vụ hoặc công bố source.
