# Current handoff - paper experiments restarted on this checkout, 2026-10-23

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
