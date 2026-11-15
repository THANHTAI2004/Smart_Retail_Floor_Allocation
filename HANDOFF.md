# Current handoff - authorized Git publication prepared, 2026-11-15 ICT

User explicitly requested pushing with their account. Git Credential Manager lists THANHTAI2004; origin is https://github.com/THANHTAI2004/Smart_Retail_Floor_Allocation.git and main was 0/0 with fetched origin/main at 6317aaeb. Found 417 already-staged source/test/script/config/document paths and no unstaged or untracked changes. Verified external snapshot C:/Users/admin/SmartRetailBackups/git-push-20261115-142957 includes all 417 working files (4,290,331 bytes), SHA256 manifest and original index. Publication includes inherited function comments, scoped refactor/test, campaign configs/runners and workflow documents/images; no generated experiment results, reports, database, var runtime or private deployment files are staged. Filename/private-key/token screening found no flagged files; this is a bounded screen, not an exhaustive secret audit.

Fresh checks: Ruff PASS; focused pytest backend/tests/contracts backend/tests/unit/test_architecture.py backend/tests/unit/test_campaign_record_index.py: 51 passed, 1 existing Starlette deprecation warning; architecture PASS (108 Python / 40 frontend modules); frontend lint PASS, Vitest 4 passed, build PASS. Initial pytest invocation had 9 temporary-directory setup errors because its parent did not exist; created the ignored parent and the complete rerun passed. git diff --cached --check reports 354 trailing-whitespace lines in the two generated workflow SVGs; retained original images without cosmetic rewriting. No full MongoDB integration, browser E2E or numerical campaign run. No service restart or experiment launch. Commit/push authorized to main with THANHTAI2004; verify remote commit after push.

---

# Current handoff - authorized Git pull complete, 2026-11-15 ICT

User requested pulling this checkout. Fetched origin and fast-forwarded main from b646c31c to 6317aaeb (docs: sync README with paper-v4 and paper-v5 research capabilities); incoming commit changed README.md only. Verified external snapshot C:/Users/admin/SmartRetailBackups/git-pull-20261115-142513 contains 1,190 existing tracked/untracked files, original Git index and status. Preserved the local README cleanup-note prefix above the complete upstream README. Temporarily restored only backed-up README to its indexed version to permit fast-forward, then reapplied the combined content. All other 1,189 files matched snapshot SHA256 after pull, before this additive HANDOFF entry. No staged changes before or after; HEAD...origin/main is 0/0. No reset, clean, stash, commit, push, service restart or numerical run.

Validation: git diff --check after handoff update; runtime tests not run because incoming changes are documentation only. Upstream README historical test counts and descriptions of unrun paper-v5 configs are not fresh validation or current local campaign evidence; consult newer local handoff milestones for operational state. Snapshot contains manifests, resolved README and pull logs. Next: review documentation; T1 SEARCH_EXHAUSTED remains a separate issue.

---

# Current handoff - function-level comments completed, 2026-11-15 ICT

User explicitly replaced exhaustive line-by-line comments with function-level comments and selective internal explanations. Covered 253 authored source/test/script paths; changed 233. Removed 24,236 redundant generated comment lines identified against pre-line-comment and pre-refactor snapshots. Retained original meaningful comments/docstrings and selective constraints/cache/budget/replay notes; shortened function headers and documented named frontend helpers. 845 Python functions retain adjacent comments or docstrings; named TS function/method coverage check has no missing notes. Source lines reduced 53974 -> 29270. Existing safe-refactor code and tests remain intact; no file deletion.

Verified external snapshot C:/Users/admin/SmartRetailBackups/function-comments-20261115-090245 contains target source, prior HANDOFF and Git index; 1,180 existing Git-listed files hashed for preservation. Before publishing edits, verified Python AST/non-comment tokens for 189 files, TS AST/emitted JavaScript for 52, PowerShell tokens for 8 and HTML/CSS content for 4. Final verification again confirms Python/TS equality; unchanged final PS/HTML/CSS bytes match verified proposals. No API/algorithm/config/dependency/data changes, campaign launch/resume, database/service operations or Git index/stage/commit/push. Original research/locks/configs and non-target files hash unchanged, except this additive HANDOFF milestone. Large ignored numerical artifacts remain outside full hash boundary and were not written.

Actual checks: .venv/Scripts/python.exe -m ruff check --config backend/pyproject.toml backend/src backend/tests PASS; npm.cmd --prefix frontend run lint PASS; npm.cmd --prefix frontend run build PASS; npm.cmd --prefix frontend run test 4 passed; .venv/Scripts/python.exe -m pytest backend/tests/contracts backend/tests/unit/test_architecture.py backend/tests/unit/test_campaign_record_index.py -q --basetemp var/function-comments/20261115-090245/pytest-temp --junitxml var/function-comments/20261115-090245/pytest.xml: 51 passed, 1 Starlette deprecation warning; scripts/verify_architecture.py PASS; git diff --check PASS. Recovery tests dependent on missing historical files, MongoDB integration, numerical campaigns and browser E2E were not run.

Evidence: var/function-comments/20261115-090245/report.md, completion.json, language verification JSON, function coverage and command logs. Limit: source byte identity changes with comment edits; no historical identity rewrite or forced resume. Next: maintain function comments and add internal comments only for non-obvious reasoning.

---

# Current handoff - scoped safe clean-code refactor complete, 2026-11-15 ICT

Latest user attachment supersedes the earlier test-removal request: preserve tests/fixtures/verification and all existing Vietnamese comments; no deletion or approval-block bypass. Audited 204 source/script paths with static metrics/imports/duplicate AST inventory; snapshot verified for all 1,179 Git-listed existing regular files including related untracked content plus Git index at C:/Users/admin/SmartRetailBackups/safe-refactor-20261115-083059. Initial expanded Git status: 254 modified and 152 untracked files; none treated as garbage.

One three-file group completed: extracted private _records_by_job in backend/src/smart_retail/application/experiments/cli.py to share identical left/right record indexing; introduced three private TypeScript interfaces in frontend/src/features/research/api.ts to name nested ResearchSpec shapes; added backend/tests/unit/test_campaign_record_index.py with 9 cases using temporary JSON fixtures only, no DB/worker/solver/campaign. Existing comment text preserved (142 Python, 37 frontend comments in touched source). No script consolidation or numerical/persistence refactor.

Fresh baseline/after: Ruff PASS, ESLint PASS, mypy PASS, TypeScript/Vite build PASS, Vitest 4 passed each, architecture PASS (108 Python / 40 frontend), git diff --check PASS. Selected independent pytest: before 79 passed/3 failed, after 88 passed/same 3 failed, one Starlette deprecation warning each; failures are unchanged RecoveryTests FileNotFoundError for absent historical 20261023-paper-v2/paper-x2b-small/configuration.json. New 9 cases also passed against original source before refactor. No full numerical, MongoDB integration or browser E2E run.

Equivalence: after inlining helper, complete Python module AST equals original; frontend exported types structurally equal, export list unchanged and emitted module JavaScript identical. All three built JS/CSS asset SHA256 values match baseline. Source identity changes with Python byte edits as designed; no historical identity rewrite or forced resume. Existing files outside two source edits and this HANDOFF are SHA256-protected; new test intentionally added. Git index unchanged. Ignored large numerical artifacts are outside full hash scope; no command wrote their roots. No MongoDB/GridFS access, campaign launch/resume, service changes, dependency edits or Git publication.

Reports: var/code-cleanup/20261115-083059/report.md and audit.md; raw source-audit.json, semantic-verification.json, type-equivalence.json, before/after command receipts/logs, per-file diffs and completion.json. Deferred: long coordinator/campaign responsibilities, duplicate CLI trees and historical-fixture recovery tests. Next: review this bounded refactor; design isolated regression evidence before larger changes.

---

# Current handoff - test-source cleanup blocked before deletion, 2026-11-15 ICT

User explicitly requested deleting test files while preserving application source. Inventoried four test roots (backend/tests, frontend/tests, scripts/tests, experiments/scripts/tests), two frontend test-runner configs and ten test-only verification/audit scripts: 60 authored files plus 40 bytecode cache files, 100 files / 1,979,963 bytes total. Kept runtime validation/replay/checksum modules, experiment runners, research datasets/configs and static architecture inspection outside deletion scope. Verified external snapshot C:/Users/admin/SmartRetailBackups/test-source-cleanup-20261115-082117 contains every target and proposed config/doc edit plus original Git index with matching SHA256.

The direct PowerShell Remove-Item -LiteralPath inventory operation was rejected before process creation by automatic approval review: blocked by policy. No deletion occurred and no alternate deletion mechanism was attempted. Fresh post-rejection inspection verifies all 100 files still exist with unchanged SHA256; 726 protected source/data/config paths and Git index match their preflight hashes. No npm/tsconfig/pytest/CI changes were applied because the tests remain. No tests or build were run; no application change or experiment launch, stage/commit/push.

Receipts: var/test-source-cleanup/inventory.json, receipt.json and review.md. Status BLOCKED_BY_POLICY, deleted 0/100. Next: user can review and remove the listed paths manually in File Explorer; only after actual deletion synchronize test-only npm commands, TypeScript include, pytest config, CI and current documentation. Do not bypass the rejection through a different tool or shell.

---

# Current handoff - line and function comments completed, 2026-11-15 ICT

User clarified that comments must explain each code line and every function. Covered all 252 current authored source/test/script paths (backend 141, frontend 54, scripts 41, experiments 16); 232 paths received additional text, while comment-only package markers already explain their role. Added 24,998 explanatory comment lines plus 510 import-spacing lines. Python coverage includes 833 functions, methods and nested helpers; comments explain signatures, fields, assignments, calls, conditions, loops, exceptions and returns. JavaScript/TypeScript, PowerShell, CSS and HTML lines are also documented. Two frontend result-view components were omitted by the prior generic directory-name filter; both are included now. No data/generated results/dependencies/retired application edits.

Verified pre-edit external snapshot: C:/Users/admin/SmartRetailBackups/line-comments-20261115-080950, including 252 source paths, prior HANDOFF and Git index. Prior dirty/untracked content preserved. Git index SHA256 unchanged. No commit/push, experiment launch, service changes or historical result changes.

Fresh verification: .venv/Scripts/python.exe var/comment-code-work/line-comments/verify_all.py PASS for 188 Python AST and executable token streams, 3 HTML structures with inline script/style, 1 CSS and UTF-8/index checks. node.exe var/comment-code-work/line-comments/typescript_lines.cjs PASS for 52 JS/TS/TSX AST-printer output and emitted JavaScript equality. powershell -NoProfile -ExecutionPolicy Bypass -File var/comment-code-work/line-comments/powershell_lines.ps1 PASS for 8 parsed scripts and identical executable tokens. Import-comment spacing was adjusted without changing Python AST/tokens; ruff then PASS. Multiline literal contents and explicit physical-line continuations remain intact; JSX lines have individual numbered explanations above their enclosing expression to avoid altering the React tree. Original executable statements and existing docstrings are unchanged.

Actual checks: .venv/Scripts/python.exe -m ruff check --config backend/pyproject.toml backend/src backend/tests --output-format concise PASS; npm.cmd --prefix frontend run lint PASS; npm.cmd --prefix frontend run test 4 passed; npm.cmd --prefix frontend run build PASS; .venv/Scripts/python.exe scripts/verify_architecture.py --output var/comment-code-work/line-comments/architecture.json PASS (108 Python, 40 frontend modules); git -c core.safecrlf=false diff --check PASS. .venv/Scripts/python.exe -m pytest backend/tests/contracts backend/tests/unit/test_architecture.py scripts/tests --ignore=scripts/tests/test_paper_recovery.py -q --basetemp var/comment-code-work/line-comments/pytest: 70 passed, 1 Starlette deprecation warning. RecoveryTests were explicitly excluded because the preceding run established all three require absent historical experiments/results/20261023-paper-v2/paper-x2b-small/configuration.json. No full numerical/MongoDB/browser E2E suite run.

Evidence and per-file/line coverage: var/comment-code-work/line-comments/completion.json, verification.json, python-coverage.json, typescript-coverage.json, powershell-coverage.json, markup-coverage.json. Limit: comments change runtime_identity source_sha256; do not rewrite prior identity or force old campaign resume. Next: review the annotated source; use a new output namespace for any separately authorized fresh experiment.

---

# Current handoff - Vietnamese source comments completed, 2026-11-15 ICT

User requested comments across all current project source. Added 475 Vietnamese comment lines to 250 authored source/test/script files: backend 141, frontend 52, scripts 41, experiments 16. Each file now explains its responsibility; selected functions and blocks explain T1-T4 constraints, cache identity, train/holdout boundaries, joint budgets, immutable campaign inputs, revision updates and worker fencing. Existing executable code, docstrings and inherited dirty/untracked content were retained. JSON/data/generated outputs/dependencies and retired application sources were outside the editing scope. Snapshot and SHA256 verification preceded edits: C:/Users/admin/SmartRetailBackups/comments-20261115-075821 (250 source paths, original HANDOFF and Git index). Index SHA256 remains unchanged. No commit/push, numerical campaign, service start/stop or result deletion.

Fresh checks: var/comment-code-work/verify.py PASS on all 250 paths (inserted comment lines only; 188 Python AST and non-comment token streams identical to snapshot). TypeScript parser/printer with comments removed PASS on 50 JS/TS/TSX files. PowerShell parser and non-comment token comparison PASS on 8 scripts; remaining 4 paths are HTML/CSS with comment-only additions. Commands and results in var/comment-code-work/completion.json; coverage.json and verification.json list every file.

Commands: .venv/Scripts/python.exe -m ruff check --config backend/pyproject.toml backend/src backend/tests PASS; npm.cmd --prefix frontend run lint PASS; npm.cmd --prefix frontend run build PASS; npm.cmd --prefix frontend run test 4 passed; .venv/Scripts/python.exe scripts/verify_architecture.py --output var/comment-code-work/architecture.json PASS (108 Python, 40 frontend modules); git -c core.safecrlf=false diff --check PASS. Focused pytest command .venv/Scripts/python.exe -m pytest backend/tests/contracts backend/tests/unit/test_architecture.py scripts/tests -q --basetemp var/comment-code-work/pytest: 70 passed, 3 failed, 1 Starlette deprecation warning. All three failures are RecoveryTests setup FileNotFoundError for missing experiments/results/20261023-paper-v2/paper-x2b-small/configuration.json; no historical output was recreated. Full numerical/MongoDB/browser E2E suites were not run.

Limit: runtime_identity hashes Python source bytes, so these comments change source_sha256 despite identical executable syntax. Do not force resume old campaigns across this identity change; retain old evidence and use a fresh output namespace for any separately authorized new experiment. Next: review comments in source; repairing the historical-fixture recovery tests is separate work.

---

# Current handoff - F copy complete and verified, 2026-11-12 09:34 ICT

Full requested copy completed at09:29:47 ICT. F:/results contains447196 files/343013856138 bytes; F:/reports contains1254 files/299446985 bytes. Total448450 files/343313303123 bytes. Sources retained unchanged by copy; no destination-only files found or removed. Robocopy copy completed results09:24:13 and reports09:24:41; read-only verification finished09:27:22 with copied-needed0, mismatch0, failed0, extras0 for both roots. Independent Python comparison found zero missing or metadata mismatches (size/mtime,2-second tolerance). All1560 scoped SHA256 pairs matched (1290 results metadata/records files;270 report JSON/CSV/MD files); freshly rechecked both D/F against saved hash manifest at09:34. Other artifact contents are metadata verified, not full-tree SHA256. No live copy/verification processes remain; stderr empty.

Receipts: var/copy-to-F-20261112-073252/completion.json, scoped-sha256.json, copy-*.log and verify-*.log. Final state COMPLETE_METADATA_AND_SCOPED_HASH_VERIFIED. Duration from07:33:44 launch to09:29:47 verified completion approximately1h56m03s. User-facing completion notification and pause of heartbeat gi-m-s-t-copy-k-t-qu-sang-f-ng-y-12-11 requested as final monitoring step. No numerical work/source/config/index modifications or Git publication. Next: use completed F copy; preserve D originals unless separately authorized.

---

# Current handoff - full experiment results copy to F running, 2026-11-12 07:33 ICT

User requested copying all experiment results to F. Inventoried current D:/Smart_Retail_Floor_Allocation/experiments/results (447196 files,343013856138 bytes, includes capped pilot and main V5) and reports (1254 files,299446985 bytes), zero reparse points. F NTFS healthy,499989663744 bytes initially free; no existing results/reports roots at preflight. Destinations F:/results and F:/reports. Copy preserves D sources and destination-only files, uses Robocopy /E /XJ /Z /MT:16 /COPY:DAT /DCOPY:DAT /BYTES /R:2 /W:3; no mirror/purge/move. Hidden PowerShell supervisor PID13716 launched07:33:44 ICT; copy currently in results phase, no stderr observed. This is RUNNING, not a completion claim.

Durable driver var/copy-to-F-20261112-073252/copy.ps1 copies both roots, treats exit>=8 as failure, then read-only Robocopy /L checks and verify.py compare all source files by relative path/size/mtime (2-second tolerance), preserve/report destination extras, and SHA256-check all record JSON, identity/configuration/checkpoint/integrity JSON and report JSON/CSV/MD. Other artifact contents are metadata-verified only, not full-tree SHA256. Receipt completion.json/status COMPLETE_METADATA_AND_SCOPED_HASH_VERIFIED exists only after verification succeeds; failures write FAILED. Logs copy-results.log/copy-reports.log, verify-results.log/verify-reports.log, console.err.log, scoped-sha256.json. Inventory/process/status evidence in same directory. Do not start duplicate copy. Next: monitor meaningful changes/errors and inspect completion.json plus Robocopy summaries before claiming completion. No numerical jobs started; main experiment remains complete/stopped. No source/config/index changes or commit/push.

---

# Current handoff - user stop request; run already complete, 2026-11-12 06:43 ICT

User requested stopping after current jobs. Fresh inspection found no live Python processes and main status COMPLETED_INTEGRITY_VERIFIED dated2026-11-11T20:46:24Z (2026-11-12 03:46:24 ICT). Direct record inventory confirms1008/1008 SUCCEEDED, independent validation PASS and heldout COMPLETED; all68 campaign checkpoints COMPLETED. Coordinator journal records VERIFIED_REPORTED for W2 and W1;1174 report files present across pooled outputs. This turn did not rerun full artifact hashing or scientific analysis; integrity completion is the coordinator receipt, while counts/status fields were freshly read. Created state/stop.request to prevent further admissions and state/user-stop-20261112.json with direct inventory and Git index hash. No active jobs needed draining, no processes terminated, no new numerical jobs started. Preserve completed results/reports; do not resume/retry/start new experiments without explicit user authorization. No source/config/index changes or numerical suite run. Next: remain stopped; completed reports are available for a requested scientific summary.

---

# Current handoff - user-authorized start pipeline, 2026-11-11 17:46 ICT

User explicitly requested starting experiments, superseding the16:38 stop. Same V5 main output, three campaign slots/one worker each/no RAM cap, unchanged numerical budgets. Preflight runtime/source/dependencies and all69 saved effective config/index hashes matched;268 existing records inventoried. Verified external snapshot C:/Users/admin/SmartRetailBackups/paper-v5-start-20261111-174603 (53 state/control/checkpoint/HANDOFF files with matching SHA256 plus record/index boundary). Authenticated MongoDB health PASS after startup readiness race. No pre-existing Python experiment processes at launch; no backend/config/dependency/index changes.

Started hidden var/paper-v5-unlimited-parallel-20261110/start_remaining.py at17:46:50 ICT, launcher4860. Logs start-20261111-1746.log and .err.log; start-process.json and start-boundary.json retain evidence. Pipeline first uses production CLI resume --max-new-jobs1 for medium parts19/20 to recover their already-SUCCEEDED durable outcomes (not numerical reruns), then reviews exact historical medium timing records using result canonical digest/runtime/receipt child exit0/full40 evaluations and recorded independent PASS/heldout COMPLETED. Writes timing-review-start-20261111.json; only matching record hashes can bypass their historical timing warning. Verifies268 old hashes and Git index again, archives only current stop.request into external snapshot, then invokes existing coordinator. Coordinator performs full startup campaign integrity verification before new admissions; fresh timing/errors/drift still stop. Current phase is recovery, not yet proof of three active numerical workers. Pipeline exits STOPPED_NEEDS_REVIEW on any error. Do not launch duplicate coordinator. Next: read status/logs for recovery completion, startup integrity and active workers. No fresh numerical suite run; startup helper py_compile PASS. No scientific completion claim.

---

# Current handoff - user requests stop; already stopped, 2026-11-11 16:38 ICT

User requested stopping experiments after current jobs finish. Fresh process command-line inspection found no live Smart Retail experiment coordinator/supervisor/numerical worker; unrelated Python tests in E:/Van_Phong_So_Kho_Tai_Lieu_Thong_Minh are preserved. Main state remains STOPPED_NEEDS_REVIEW from 14:30:03 ICT due to medium feedback_v5 wall2460.547s. No current experiment job exists to drain. Created state/stop.request to prevent further admissions and recorded request/state plus all268 record hashes and Git index hash in var/paper-v5-unlimited-parallel-20261110/user-stop-20261111-1638.json. No processes terminated, resumed or retried. Existing failure/partial-attempt evidence preserved; do not describe this as a fresh graceful drain. Do not resume/retry/remove stop.request until explicit user continuation. Main progress268/1008; experiment remains incomplete. Existing30-minute reporting remains read-only. No code/config/index changes. Verification: process command lines, state JSON and record inventory; git diff --check. Next: remain stopped until requested.

---

# Current handoff - reviewed timing alerts and resume launched, 2026-11-11 11:58 ICT

User explicitly requested continuing experiments. Found coordinator STOPPED_NEEDS_REVIEW at 09:44:39 ICT due to medium part17 feedback_v5 wall2487.672s exceeding the conservative2430s warning. It had SUCCEEDED, child exit0, all40 evaluations, independent validation PASS and heldout COMPLETED. Part16 also had a succeeded durable result (wall2580.485s) without its record because the earlier stop killed its supervisor during finalization. Recovered only that result through production CLI resume --max-new-jobs1; command exited0, same run_id, no numerical rerun. Main boundary now252/1008 SUCCEEDED;756 jobs remain. W2 complete144/144, W1 medium108/144. Part19 has an expired RUNNING lease without receipt; production resume must handle WORKER_LOST using its existing bounded retry policy, retaining the old attempt.

Verified external snapshot C:/Users/admin/SmartRetailBackups/paper-v5-review-resume-20261111-110443 (46 state/checkpoint/runner/document files with matching SHA256, plus record and index boundary). Runtime/source/dependencies match saved identity; all69 effective config/index hashes and all251 pre-existing record hashes match. All27 initialized campaign configurations/identities checked. No backend/config/dependency changes. Added coordinator --timing-review: only the exact SHA256 of an explicitly reviewed historical record can pass its timing warning; invalid outcomes, new timing alerts and campaign projected-wall checks still stop. Reviewed both records using matching canonical result digests, runtime, child receipts, full40 evaluations and recorded independent/heldout validation. Review manifest var/paper-v5-unlimited-parallel-20261110/timing-review-20261111.json. Eight focused timing-guard tests PASS (5.55s); ruff with backend config and py_compile PASS. No full numerical suite rerun. Read-only preliminary full-integrity audit passed medium parts01-03 then was stopped to avoid duplicating the coordinator's startup audit; do not claim all27 full-tree checks completed yet.

Started hidden coordinator at11:58:50 ICT, launcher26056, same three slots/one worker/no per-job RAM cap and original budgets. Current phase RESUMING_INTEGRITY_CHECK: coordinator independently verifies every initialized campaign before admitting W1 jobs. Startup per-campaign integrity events now logged. Logs var/paper-v5-unlimited-parallel-20261110/resume-review-20261111-115850.log and .err.log; identity/record and process receipts review-identity-verification.json and review-resume-process.json. MongoDB authenticated health PASS after initial readiness race. Git index unchanged; no stage/commit/push. Next: verify startup completes, three distinct workers become active, expired part19 lease recovers, and new outcomes remain valid. Historical stop receipts below remain preserved.

---

# Current handoff - user-authorized resume launched, 2026-11-11 07:43 ICT

User explicitly requested continuing experiments, superseding the prior pause. Same main run paper-v5-unlimited-parallel-20261110, 3 slots / one worker per campaign, no per-job RAM cap, original budgets. Fresh preflight verified runtime/source/dependency identity, all effective config/index hashes and verify_integrity on all 26 initialized campaigns. Starting boundary 243/1008 records; all 243 record hashes and Git index hash rechecked unchanged after launch. Verified external state snapshot C:/Users/admin/SmartRetailBackups/paper-v5-resume-20261111-074227; moved only current stop.request into snapshot as stop.request-resumed. MongoDB startup initially raced readiness; subsequent .venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.health PASS.

Started hidden existing coordinator at 07:43:03 ICT, launcher32072 / actual coordinator13760. Logs var/paper-v5-unlimited-parallel-20261110/resume-20261111-074227.log and .err.log; preflight and process receipts under resume-*-latest.json. Startup integrity verification completed; at 07:53:38 ICT coordinator admitted W1 medium parts16/17/18. Fresh status RUNNING at 07:54:25, three numerical child workers11220/25260/33048 confirmed under three distinct campaign supervisors24604/6352/20780; stderr empty. Existing243 records remain unchanged. No application/config changes or fresh test-suite run. Next: monitor new genetic/feedback records, failures, timing and integrity; 765 designed jobs remained at resume. Preserve old stop receipts as historical; do not launch a duplicate coordinator.

---

# Current handoff - user stop after current jobs completed, 2026-11-11 06:48:46 ICT

Latest user request: stop experiments after current jobs finish. stop.request was created and retained. Coordinator immediately drained admissions (pending0); all three existing annealing jobs in W1 medium parts16/17/18 finished naturally, SUCCEEDED, worker exit0. Their campaign supervisors each exited0 / PAUSED_PARTIAL. Coordinator wrote fresh DRAINED_STOP at 2026-11-10T23:48:46.833322Z (2026-11-11 06:48:46 ICT) and exited. Verified no live Python campaign workers/coordinator remain; no forced termination or cancellation was issued for this stop.

Final main-run progress 243/1008 SUCCEEDED (240 before request +3 drained); 765 planned jobs remain. All record validation fields PASS and held-out evaluation fields COMPLETED. All 240 pre-request record SHA256 hashes unchanged; new receipts match recorded result digests and show worker exit0. Journal has no START after stop.request timestamp. Existing coordinator code independently ran verify_integrity on each finished slice before EXIT; no additional full-tree rehash performed for this stop. Git index SHA256 unchanged. Config/source and previous pilot evidence retained. No complete experiment acceptance or scientific conclusion.

Receipts under var/paper-v5-unlimited-parallel-20261110/pause-20261111-064010/: request.json and completion.json. Fresh verification command .venv/Scripts/python.exe -u var/paper-v5-unlimited-parallel-20261110/pause-20261111-064010/verify_stop.py exited0. Main state/status.json now PAUSED_AFTER_CURRENT_JOBS. Runbook synchronized; git diff --check PASS. No numerical test suite rerun for this runtime stop. MongoDB retained unchanged. Do not resume, retry, remove stop.request or start numerical jobs until the user explicitly requests continuation. Future resume must preserve source/dependency/config identity and existing records; three slots and no per-job RAM cap remain the saved configuration.

---

# Current handoff - user requested stop after current jobs, 2026-11-11 06:40 ICT

User requested "xong job dung thuc nghiem". Current state stop.request created; coordinator confirmed DRAINING with pending0. Boundary: 240/1008 SUCCEEDED, W1 medium parts16/17/18 active. Finish their existing one-job slices naturally, admit no new work, retain all evidence. Do not resume/retry or remove stop.request without a new user instruction. Stop verification pending: var/paper-v5-unlimited-parallel-20261110/pause-20261111-064010/{request,completion}.json; completion.json exists only after fresh process/receipt/record verification. Old stopped.json and old pause receipts are historical until refreshed by the current coordinator. No application source changes or process termination requested.

---

# Current handoff - Paper V5 resumed by user, 2026-11-10 20:48:20 ICT

User explicitly requested continuing experiments; this supersedes the prior pause instruction. Same main output experiments/results/paper-v5-unlimited-parallel-20261110, fixed three campaign slots, one queue worker per campaign and memory_limit_mb null. Original numerical/time budgets retained. Starting boundary 87/1008 SUCCEEDED; 921 jobs remained. Preflight runtime/source/dependency identity equals saved state and all six campaign identities; all 69 effective config/index file hashes equal the saved manifest. No existing Python workers/coordinator at preflight. Existing 87 completed record hashes rechecked unchanged after restart. External state snapshot with verified file copies: C:\Users\admin\SmartRetailBackups\paper-v5-resume-20261110-204235 (14 files plus manifest/preflight; includes prior pause receipts and journal). Moved only the current state stop.request into this snapshot as stop.request-resumed; unrelated old cancellation barriers and incomplete pilot directory untouched.

MongoDB was not running at initial check. scripts/start_mongodb.ps1 initial health probe raced readiness; subsequent .venv/Scripts/python.exe -m smart_retail.infrastructure.mongodb.health PASS. Started hidden .venv/Scripts/python.exe -u scripts/run_paper_v5_parallel.py --configs experiments/configs/paper-v5-unlimited-parallel-20261110 --results experiments/results/paper-v5-unlimited-parallel-20261110 --reports experiments/reports/paper-v5-unlimited-parallel-20261110 --state var/paper-v5-unlimited-parallel-20261110. Coordinator PID 26380. Production coordinator independently reverified all six initialized W2 campaign integrity manifests before admitting jobs at 20:47:19 ICT. Current RUNNING: W2 parts04/05/06; three distinct live numerical workers confirmed. No duplicate/re-run of the existing 87 records. Resume receipts, archived-state pointer, runtime and process evidence under state/resume-*-latest.json; stdout resume-20261110-204235.log, stderr resume-20261110-204235.err.log (empty at check).

No backend/config source changes or fresh numerical test-suite run; this is execution/resume verification only. Runbook updated; git diff --check PASS. No scientific conclusion or completion claim. Earlier capped five-job pilot remains separate. State/status.json is authoritative; old stopped.json and pause-completion.json describe the prior pause, not current activity. Next: monitor record failures, integrity/source drift, first W2 completion and first medium timing; coordinator retains existing stop-on-error/time-review behavior. To drain current jobs on a future user pause, create state/stop.request. Do not edit backend source/configs/dependencies during execution. Git index and unrelated local work preserved; no stage/commit/push.

---

# Current handoff - user pause after current jobs completed, 2026-11-10 16:31:20 ICT

User requested pausing after the current jobs. Created var/paper-v5-unlimited-parallel-20261110/stop.request; coordinator immediately stopped admissions and drained its three one-job slices. Starting boundary 84 completed records +3 active jobs. All three finished naturally; all slice supervisors exited code 0 and coordinator wrote DRAINED_STOP at 2026-11-10 16:28:27 ICT. Final main-run progress 87/1008 SUCCEEDED, with independent validation PASS and held-out COMPLETED for every record. No cancellation or forced process termination during this pause. No active campaign supervisors or coordinator remain. Six initialized campaign trees passed verify_integrity; all 84 pre-request record SHA256 hashes unchanged. Other 921 planned jobs remain unexecuted; no complete pooled report or scientific conclusion.

Receipts: state/pause-request.json (active boundary and prior hashes), stopped.json, pause-completion.json (final checksum and process verification); status.json now PAUSED_AFTER_CURRENT_JOBS. Verification command: .venv/Scripts/python.exe -u var/paper-v5-unlimited-parallel-20261110/verify_pause.py -> exit0, 87 completed, 3 drained, 6 campaign integrity checks PASS. No numerical test suite rerun for a runtime stop. Runbook updated; git diff --check PASS. Results, inputs/configs, three-slot/unlimited-RAM settings, Git index and unrelated local work preserved. MongoDB service retained; it was not part of the pause request.

Do not resume, retry, launch monitors that admit jobs, remove stop.request or restart numerical work until the user explicitly requests continuation. A future resume must retain the same config/source/dependency identity and immutable records, and must not count the separate five capped pilot records as part of this main run. Next step: wait for user instruction.

---

# Current handoff - Paper V5 fixed three slots, no per-job RAM cap, 2026-11-10 13:45:45 ICT

Latest explicit user requests: configure 3 concurrent experiment streams, then "khong gioi han ram" (no RAM limit). Started fixed three isolated campaign processes, each using one production queue worker and one-job slices. No RAM-based concurrency reduction. All original V5 time/search/evaluation budgets retained. New immutable effective configs experiments/configs/paper-v5-unlimited-parallel-20261110: 68 campaigns / 1008 jobs; every config equals its original except memory_limit_mb 2048 -> null. New results experiments/results/paper-v5-unlimited-parallel-20261110; reports same suffix under experiments/reports. This is a fresh main run, not mixed with capped results.

Handover: original guard stopped without killing the active worker. Admission barriers prevented old coordinator starting numerical work in later campaigns. Waited for the active worker's SUCCEEDED receipt, then requested campaign cancellation at the next job boundary; all 5 completed records SUCCEEDED and old campaign integrity PASS. Old coordinator stopped only after current supervisor lock disappeared. Original five records remain separately under experiments/results/paper-v5 as capped pilot evidence, excluded from the new 1008-job design. Old part02 contains an incomplete initialization only. Automatic approval review rejected the attempted cleanup/snapshot/control-removal command with blocked by policy; it did not run. No retry or workaround. Old partial directory and cancellation controls retained; new namespace avoids altering them.

Implementation: new scripts/run_paper_v5_parallel.py; existing backend/config sources unchanged. Checks: ruff PASS, py_compile PASS, --check-only validates 68 configs /1008 jobs/3 slots; runtime identity matches live campaigns; current process status RUNNING with 3 distinct campaign supervisors in W2 parts01/02/03, coordinator PID 32688. Fresh live per-campaign configurations show memory_limit_mb null. Earlier 146 V5 preflight tests belong to the same backend source and were not rerun for this coordinator-only change; do not claim a new full suite. Startup receipt preserves hashes of all five pilot records. Logs, effective-config comparison, source/runtime identity, hashes, process events and status in var/paper-v5-unlimited-parallel-20261110. Primary status.json is the new state; old single-slot state marked superseded.

The coordinator detects record failures, invalid replay/holdout, unexpected solver status, source/config drift, projected campaign wall >=90% cap or medium wall >=2430 s, and stops all owned active process trees for review. It verifies every completed slice's integrity and existing record hashes before resuming; no duplicate campaign can occupy two slots. It verifies all campaigns then pools W2/W1 reports after all jobs finish. Create state/stop.request to drain current one-job slices; state/cancel.request requests immediate stop. Local process only; no scheduled chat messages or reboot recovery. No full experiment completion or scientific conclusion. Next: inspect actual throughput and review first W2 and medium records under three-way contention. Git index and unrelated local work preserved; no commit/push.

---

# Current handoff - paper-v5 new run started, 2026-11-10 13:35:21 ICT

User explicitly requested running new experiments after pulling main b646c31c. This supersedes the historical no-run instruction in the 2026-11-03/09 sections. New outputs, no resume of deleted V3/V4 evidence. Config validation PASS: 68 campaigns / 1008 jobs (W2 144 first, W1 864 with medium then small then tiny); original budgets, 2048 MiB per job and one production durable-queue worker retained. Runtime/source/dependency identity and 71 config/runner/guard file hashes saved under var/paper-v5-launch-20261110. All campaign inputs/configuration/plans/runtime/checksums are produced immutably by the existing production runner.

Fresh preflight: scripts/start_mongodb.ps1 initially raced readiness and reported BLOCKED_MONGODB_RUNTIME; subsequent python -m smart_retail.infrastructure.mongodb.health PASS. Targeted command: .venv/Scripts/python.exe -m pytest backend/tests/unit/test_joint_search_v5.py backend/tests/unit/test_paper_v5_smoke.py backend/tests/unit/test_layout_families.py backend/tests/unit/test_held_out_evaluation.py scripts/tests/test_paper_v5_configs.py -q -p no:cacheprovider --basetemp var/pytest-v5-launch-20261110 -> 146 passed, 1 Starlette/httpx deprecation warning, 111.70 s. This is targeted verification, not a new full-suite acceptance. Guard py_compile PASS.

Started at 13:34:33 ICT via hidden var/paper-v5-launch-20261110/guard.py; guard actual PID 25932, repository runner PID 18120. Runner command: .venv/Scripts/python.exe -u scripts/run_paper_campaigns.py --set paper-v5. At this check first W2 campaign RUNNING, 3 completed records, all SUCCEEDED / independent validation PASS / held-out COMPLETED; source identity still equal to campaign snapshot. No full campaign completion or scientific conclusion yet. Logs var/paper-v5-run.log and .err.log; guard status/process/manifest/tests/preflight under var/paper-v5-launch-20261110; results experiments/results/paper-v5, reports experiments/reports/paper-v5 (reports created after all campaigns).

Background guard polls every 5 s and checks durable records, checkpoint and runner journal; stops the runner's process tree on failed/unexpected/invalid outcomes, medium record wall >=2430 s (90% of 2700 s training allowance), or projected campaign wall >=90% of cap, as a conservative implementation of runbook review thresholds. Stop preserves evidence and requires investigation; no automatic retries beyond production's configured worker-crash/lost retries. Local monitoring only: no scheduled chat notifications or automatic Windows-reboot recovery. To request immediate stop, create var/paper-v5-launch-20261110/stop.request; guard records STOPPED_NEEDS_REVIEW. On complete run it independently verifies all campaign integrity files. Do not edit backend Python/configs/dependencies while running. Runbook's ~70 h is a pre-run estimate, not a current ETA. Next step: inspect first W2 part and first W1 medium part; review stop status/errors before any restart, then verify pooled reports after completion. Application source/configs/index and unrelated local work preserved; no staging/commit/push.

---

# Current handoff - experiment outputs deleted, archive residual remains, 2026-11-10

User requested deleting all experimental results. Scoped local deletion completed: 43 targets, 504626 files / 342735839216 logical bytes; experiments/results, experiments/reports and generated V3/V4 campaign state/logs removed. All 43 targets absent after deletion. Measured D free-space gain 343903113216 bytes during the operation (includes allocation effects and concurrent disk changes; not a precise logical-size total). No active Python/Robocopy existed at preflight. Temporary local MongoDB startup wrapper reported BLOCKED_MONGODB_RUNTIME; direct authenticated connection succeeded. Dropped exactly 225 sr_campaign_ databases; zero remain, all 775 non-campaign database names preserved. Shut down only the local MongoDB instance started for this operation.

Preserved source, configs, experiment tools, research documents and historical software QA evidence. SHA256 before/after matched for 723 protected files; Git index hash unchanged. Inherited dirty HANDOFF.md, untracked configs and scripts preserved. No staging, reset, clean, commit, push or new result backup. External F copy has a historical COMPLETE_METADATA_VERIFIED receipt dated 2026-11-02, but F was unavailable today and was neither reverified nor modified. Prior handoff sections below are historical: their D result/checkpoint paths no longer exist and cannot be resumed/replayed.

Partial overall cleanup: 39 old publication ZIP/partial/metadata/inventory files remain under var/github-publication, 1727996185 bytes. Their deletion was previously blocked by automatic policy review; no retry or workaround was attempted. Receipts: var/experiment-cleanup-20261110/{inventory,completion,protected-before,databases-inventory,databases-completion,blocked-publication-archives}.json. Verified removal and protected hashes through the PowerShell cleanup script, direct PyMongo prefix-scoped deletion and post-list comparison; documentation checks recorded in final-verification.json. No numerical tests run because application code was not changed. Next step: resolve blocked publication-archive removal if permitted; any new experiments must start in new output paths. Never restart old monitors against deleted checkpoints.

---

# Current handoff - all experiment results copied to F and verified, 2026-11-02 15:41 ICT

User requested copying final replay outputs. Supplemental Robocopy /E /XJ /Z /MT:16 copied142 updated/new files /1045288399 bytes, skipped499900. Final metadata verify PASS: F:/results500042 files342244623843 bytes; F:/reports2257 files452523410 bytes; both copied-needed0 mismatch0 failed0 extras0, verify exit0. Total502299 files342697147253 bytes. Final replay ledger on F COMPLETED6/6. Scoped SHA256 comparison PASS for4 files only: replay-ledger, final checkpoint, final integrity manifest and final job record. Not full-tree SHA256. Source D and destination extras preserved; no deletion. Receipts via var/copy-to-F-latest.txt -> var/copy-to-F-final-20261102-153801. Copy automation can now pause; numerical experiment monitoring already paused. Main reports still unchanged and predate replay integration. No more copy needed for current bounded outputs.

---

# Current handoff - V4 final replay completed, 2026-11-02 15:14 ICT verification

Fresh inspection: replay-ledger.json COMPLETED, attempted6 succeeded6; six unique original job keys, all SUCCEEDED, independent validation PASS, held-out evaluation COMPLETED, all six campaign integrity receipts PASS (helper verified them before final ledger). Runtime still equal to ledger. Last large_f2_s7603 campaign paper-v4-vl-large-part03-final-20261102 checkpoint COMPLETED1/1 at14:51:45 ICT, worker succeeded14:24, final helper exited with no errors. Main evidence remains1263 SUCCEEDED+6 intentional CANCELLED; separate replay recovers all6, do not count attempts as extra designed jobs or overwrite main reports. Main six-block reports predate replay and were not regenerated or scientifically analyzed here. Latest outputs still require F supplemental synchronization managed by separate copy automation. Experimental monitoring automation can be paused now; no more numerical jobs required for this bounded run. No fresh full-tree hash verification was repeated this check; referenced integrity receipts were produced by final helper. No source changes.

---

# Current handoff - baseline F copy verified, final replay delta pending, 2026-11-02 13:41 ICT

Resumed copy and read-only verification PASS at13:33:57: F:/results 499903 files/341199343923 bytes, copied-needed0 mismatch0 failed0; F:/reports 2257 files/452523410 bytes, copied-needed0 mismatch0 failed0. Metadata comparison only; not full SHA256. No active Robocopy at13:41. New final retry directory was initialized after scan/copy, final job now running; these new artifacts and final ledger still need supplemental transfer after completion. Therefore baseline transfer accepted, whole latest-result transfer NOT yet complete. Keep 10-minute automation active. Receipts under latest pointer resume-20261102-130218; awaiting-final-replay.json records boundary. Preserve all source and destination-only files.

---

# Current handoff - final retry worker running, 2026-11-02 13:36 ICT

Initial helper missed Windows multiprocessing main guard; spawned import hit live-supervisor guard and child exited. Stopped that helper (PIDs2096/23968), preserved its attempt artifacts under original part03. Corrected local helper main guard; fresh isolated single-job campaign paper-v4-vl-large-part03-final-20261102 initialized with same spec and exact selected original job, full-plan receipt preserved. Launcher24152 / supervisor9544 / worker34648, run a8c85b11-381c-4473-b50c-9bf4b112f8a2. Supervisor evidence observed at 13:36:39, input SHA2565730cc8d23891859815de5beacca07b60498f8533e9160b6251dc3c5757798b3. Logs var/paper-v4-last-retry-20261102-v2.log/.err.log. Final helper appends this new directory to original five-job ledger only after independent checks and six successful-campaign integrity verifications. Earlier interrupted part03 retained outside final successful selection. No experiment source edits. Must await final ledger status before declaring six recovered. Supplemental F copy required for new directory/output after finish.

---

# Current handoff - final V4 retry restarted, 2026-11-02 13:35 ICT

User explicitly requested last missing retry. Fresh runtime identity matches replay ledger; MongoDB was stopped, started through scripts/start_mongodb.ps1 and health PASS after readiness retry. Existing run 2d1a26fe-ed8a-4cc9-909b-eeeb794ba3b3 RUNNING with expired lease and dead owner/child, no live Python workers. Verified external ledger snapshot C:/Users/admin/SmartRetailBackups/v4-retry-ledger-20261102-133552. Started var/finish_paper_v4_retry.py hidden launcher PID2096, logs var/paper-v4-last-retry-20261102.log/.err.log. It asserts same runtime and single selected job identical to original plan, resumes only VL part03 via production campaign recovery, verifies physical input and integrity, then appends sixth record and finalizes existing ledger. Five successful jobs untouched. Do not claim completion until receipt/ledger checks pass. Copy monitoring remains responsible for supplemental F synchronization after output updates. No backend/config changes, no Git index changes.

---

# Current handoff - F drive returned; resumable copy queued, 2026-11-02 13:02 ICT

10-minute copy heartbeat found F returned (volume DANH, ~500 GB, external WDC disk Online); F:/reports and F:/results present, sample V1 summary.md SHA256 matches source (sample only, no full hash claim). F free 235264073728 bytes. Read-only Robocopy inventory results-reconnect-before.log is still scanning PID25428. Hidden worker25128 waits for this scan then starts supplemental /E /XJ /Z /MT:16 copy and final read-only verification via original copy.ps1. Latest receipt pointer now points to var/copy-to-F-20261102-094743/resume-20261102-130218. Original failure receipts preserved. No deletion, mirroring or source change. Not complete; inspect final verify, source replay remains RUNNING 5 recovered jobs and may change. Automation remains active.

---

# Current handoff - F copy interrupted by device loss, 2026-11-02 11:31 ICT

Copy worker ended 11:24 with Robocopy exit 9, ERROR 1117 I/O device error; F volume absent from Win32_LogicalDisk and external disk absent from Get-Disk at 11:31. Reported copied 420579 files /262890072729 bytes; failed 79324 /78309271194 bytes. These are transfer counters, NOT verified durable destination content. Earlier reports copy verify PASS; now destination unavailable. No source deletion. No active Robocopy. Receipt var/copy-to-F-20261102-094743/interruption.json. Await user reconnect of intended F disk; validate destination identity/content and capacity before resumable /E /XJ /Z supplemental copy, never /MIR. Existing 10-minute monitor remains active to detect return; do not repeatedly notify unchanged disconnected state. Do not mark transfer complete.

---

# Current handoff - copy all experiment results to F in progress, 2026-11-02

User requested copying all experimental results to F. Source inventory: experiments/results 499903 files /341199343923 bytes; experiments/reports 2257 files /452523410 bytes (live metadata at 09:47 ICT). F free 499989667840 bytes, targets F:/results and F:/reports. Started hidden PowerShell copy worker PID 28028 at 09:48 ICT; receipts var/copy-to-F-20261102-094743 (pointer var/copy-to-F-latest.txt). Uses Robocopy /E /XJ /Z /MT:16 /BYTES /R:2 /W:3, then read-only /E /L verification for each folder. Preserves D source and destination-only files; no mirroring/deletion. Status is COMPLETE_METADATA_VERIFIED only when copy exit <8 and final comparison exit 0 or2; otherwise NEEDS_REVIEW. No SHA256 claim. Copy is still in progress at initial check, not completed. Retry campaign remains RUNNING, so live source can change; reconcile final comparison before accepting complete transfer. Inspect process.json, status.json, *-copy.log, *-verify.log and runner.err.log. No source/code/config/index edits except this handoff.

---

# Current handoff - paper-v4 resumed again, 2026-11-01 18:51 ICT

User explicitly requested continuing experiments. Fresh runtime comparison matches saved identity; MongoDB health PASS. No existing campaign/monitor processes before launch. Archived stop/error/status/cancel controls under var/paper-v4-adaptive-20261028/resume-20261101-185058, removed only stop/cancel controls and old error. Same runner resumed, launcher PID 8020; 3 VL campaigns admitted, state RUNNING, RAM 77%. Logs var/paper-v4-resume-20261101.log/.err.log. Initial position 1210 SUCCEEDED +6 intentional CANCELLED /1269; 53 jobs without records. Each campaign verifies integrity before running. Cancelled records remain original evidence and are skipped by main resume; six cancellations are scheduled for separate replay after main/report completion through existing monitor. Local 30-minute monitor resumed PID 17888; logs var/paper-v4-monitor-resume-20261101.log/.err.log, initial snapshot successful. Existing stop-after-current watcher remains stopped. No backend/config changes or new full test run; no Git staging/commit/push. Verify child progress and final report/integrity before claiming completion.

---

# Current handoff - immediate user pause, 2026-11-01

User superseded drain request with immediate pause ("tam dung ... xiu chay lai"). Stopped stop-after-current watcher, issued cancel.request for all three VL campaigns with stop.request retained. Verified no Python processes remain after cancellation. All three VL campaign checkpoints CANCELLED; successful results preserved. Receipt var/paper-v4-adaptive-20261028/user-pause-20261101.json records final counts. Jobs have no mid-solver resume: cancelled jobs require a fresh replay in separate evidence when user requests continuation. Do not restart coordinator, watcher, monitor or retries until user requests resume. No source changes, staging, commit or push.

---

# Current handoff - stop after current jobs requested, 2026-11-01

User requested stopping after current job(s), without interrupting them. stop.request created to prevent new coordinator admissions; local monitor processes stopped to prevent retries. Three currently running VL jobs identified explicitly in var/paper-v4-stop-after-current-20261101.json. Background watcher var/paper_v4_stop_after_current.py (launcher PID 8260) waits for each current worker receipt.json (written only after terminal DB publication and child exit), then writes that campaign cancel.request so its next job is not started. This timing preserves current job completion; no cancel request was issued while current child was running. Worker/campaign source unchanged. Coordinator may log Campaign failed on CANCELLED campaign terminal status; that is expected control-flow handling of the requested stop. Watcher writes STOPPED_AFTER_CURRENT_JOBS only after all three campaign supervisor locks are no longer live. Inspect its receipt and var/paper-v4-stop-after-current.err.log before claiming fully stopped. No further resume or retries until requested. All results retained.

---

# Current handoff - paper-v4 resumed by user, 2026-10-31

User explicitly requested continuing experiments. Runtime identity comparison PASS (source, Python, dependencies, solver and model versions equal to var/paper-v4-adaptive-20261028/runtime.json). MongoDB started; initial startup health raced readiness, subsequent health PASS. Archived stop.request/error.json/status.json and campaign cancel.request evidence under state/resume-20261031-214740; cleared only stop/cancel controls and stale error. Existing records retained. Started same adaptive runner at 21:47 ICT, launcher PID 9864; three V3 campaign supervisors admitted, RAM 68%, status RUNNING. Stdout/stderr var/paper-v4-resume-20261031.log and .err.log. Each campaign performs its own checksum and identity checks before resuming; extra full-tree preflight was stopped as redundant before completion, do not claim full-tree checksum PASS. No backend changes or fresh test-suite run. Starting position 341 SUCCEEDED + 3 intentional CANCELLED records /1269. Completed records (including cancellations) are skipped by main runner; three cancellations remain for separate replay after main completion via existing monitor policy. Local 30-minute file monitor restarted PID 3272, logs var/paper-v4-monitor-resume-20261031.log/.err.log; this does not send scheduled chat messages. Verify progress and child logs after initialization, review report/integrity after completion. No Git staging/commit/push.

---

# Current handoff - user stopped experiments and monitoring, 2026-10-28

User explicitly selected stopping both experiments and monitoring. Created stop.request, requested cancellation on all three active V3 budget campaigns, stopped monitor processes. Active campaign checkpoints CANCELLED; coordinator exited with Campaign failed because its terminal-status handling excludes CANCELLED. This was an intentional user stop, not a new solver defect. All recorded outputs retained. Stop receipt: var/paper-v4-adaptive-20261028/user-stop-receipt.json. Do not resume or retry until user requests it.

---

# Current handoff - paper-v4 30-minute monitor, 2026-10-28

User requested 30-minute progress/failure checks and retries. Started hidden local monitor `var/paper_v4_monitor.py` PID 1792 at 08:56 ICT, interval 1800 seconds. It writes timestamped JSON snapshots and latest.json under var/paper-v4-monitor-20261028, including block/campaign/record totals, recorded error codes/messages, runner resource state and retry ledger; monitor stdout/stderr at var/paper-v4-monitor-run.log and var/paper-v4-monitor-run.err.log. Initial snapshot 15/1269 records, all SUCCEEDED, no recorded failures. py_compile PASS; initial live snapshot PASS. Causes are reported as recorded errors, not asserted root causes. Existing runner does its own bounded worker-crash/lost retries; after main finished.json the monitor runs one separate failed-record replay via scripts/replay_failed_campaign_jobs.py into experiments/results/paper-v4-retry-20261028, and stops after the replay. Retry waits for main completion to avoid bypassing 2/3-slot resource governance. If coordinator stops before finished.json or replay fails, inspect runner_error, monitor-errors.log, retry.log and ledger; monitor does not automatically restart coordinator or retry replay. This is a local background process, no automatic chat messages or restart after Windows shutdown. Do not mix retry and main evidence.

---

# Current handoff - paper-v4 adaptive run, 2026-10-28

User requested V3-style operation. Old capped sequential paper-v4 campaign was cancelled through cancel.request: checkpoint CANCELLED, 6/25 records, 19 not executed; original result tree retained at experiments/results/paper-v4. Its sequential supervisor was stopped after cancellation. New independent run uses scripts/run_paper_v4_adaptive.py, derived from V3 adaptive runner with V4 block order V2/V4/V3/V1/VL/V5; configurations at experiments/configs/paper-v4-unlimited-adaptive-20261028. All 77 configs compared equal to V4 originals after restoring only memory_limit_mb: unlimited RSS, original V4 job time/search budgets retained. No mixing with old results.

Started background `.venv/Scripts/python.exe -u scripts/run_paper_v4_adaptive.py --configs experiments/configs/paper-v4-unlimited-adaptive-20261028 --results experiments/results/paper-v4-unlimited-adaptive-20261028 --reports experiments/reports/paper-v4-unlimited-adaptive-20261028 --state var/paper-v4-adaptive-20261028`; launcher PID 508. Logs var/paper-v4-adaptive-run.log and .err.log; state/status.json and journal.json under state directory. First status RUNNING V2, three active campaigns, 56% RAM, third is one-job slice. At >90% RAM reduce to two; <80% restore three; 80-90% keep prior state, sample every 5s. Verification: runner --check-only 77 campaigns/1269 jobs; config comparison 0 differences beyond RSS; `python -m pytest scripts/tests/test_paper_adaptive.py -q -p no:cacheprovider --basetemp var/pytest-v4-adaptive-20261028` 1 passed, tests original shared V3 hysteresis function; new runner startup/status separately observed. No full experiment completion or scientific conclusion yet. Inspect state and per-campaign logs; verify integrity and reports after completion. Do not edit backend source during the run.

---

# Current handoff - paper-v4 campaign started, 2026-10-28

User authorized running paper-v4. Started MongoDB with `powershell -ExecutionPolicy Bypass -File scripts\start_mongodb.ps1`; initial health check raced startup, then `.venv\Scripts\python.exe -m smart_retail.infrastructure.mongodb.health` PASS. Started `.venv\Scripts\python.exe -u scripts\run_paper_campaigns.py --set paper-v4` as background process PID 23632 at 08:45 ICT. Logs: `var/paper-v4-run.log`, `var/paper-v4-run.err.log`, PID receipt `var/paper-v4-run.pid.json`. Results: `experiments/results/paper-v4`; reports: `experiments/reports/paper-v4`. Fresh start, V2 first; first checkpoint RUNNING, 1/25 completed, first job SUCCEEDED. Whole design 1,269 jobs, sequential runner, rough estimate 80 hours, not a completion claim. Historical 220-test result below is not a new test run. Do not modify backend source while running; inspect process, checkpoints, journal and errors before intervention. After completion verify each campaign and review failure/status and comparison reports before research conclusions.

---

# Current handoff - paper-v5 implementation complete, final review fixed (not run), 2026-11-03

Request: "bạn hãy sữa lại thuật toán hay cải thiện đi mục tiêu là Q2 và Q3", "chỉ sửa và test
không chạy thực nghiêm nha". The user approved design option B (T4-calibrated surrogate + a genetic
algorithm baseline + multi-seed/multi-geometry instances, 3-5 day run budget). Spec:
docs/research/EXPERIMENT_DESIGN_DEEPMG.md section 12; plan docs/superpowers/plans/2026-11-03-paper-v5-surrogate.md;
executed task by task (ledger .superpowers/sdd/2026-11-03-paper-v5-surrogate/progress.md, git-ignored).
Tasks 1-9 are implemented and each task was reviewed; Task 9 was fixed after its review (doc
corrections, smoke-test assertions). The final whole-branch review (opus) answered "yes with fixes"
(no Critical; three Important findings); all its findings were fixed in one wave (section "Final
review fixes" below). **No experiment or campaign was run; nothing was committed or staged.**
Closing check 2026-11-04: scoped re-review of the fix wave found all 9 findings addressed, no new
breakage; with MongoDB started (scripts/start_mongodb.ps1) `pytest backend/tests scripts/tests -q
-p no:cacheprovider --basetemp var/pytest-v5-final-04`: 370 passed, 3 failed (pre-existing
scripts/tests/test_paper_recovery, paper-v2 results absent), 1 Starlette/httpx warning, 467.62 s;
optimization/campaign schemas equal the model schemas; `git diff --check` PASS.
Publication 2026-11-09: user authorized "Commit và push"; main was level with origin/main (0/0)
after fetch; source unchanged since the closing check. Committed source, tests, schemas, docs,
the plan and experiments/configs/paper-v5; Ket_qua_thuc_nghiem_lan_*.docx and the git-ignored
.superpowers/ and var/ stay local. The paper-v5 run is still not authorized.

Final review fixes (2026-11-03, after the whole-branch review):
- No-op swaps: every generated shelf is physically identical, so a T1 swap only relabels two
  shelves (same score, one evaluation; ~29% of the small pool, ~50% of annealing's uniform moves
  on small and >= 78% on medium). New JointConfig control `drop_identical_swaps` (V5_CONTROLS,
  omitted when None = paper-v4 behaviour): `neighborhood.t1_edits` skips a swap of two shelves
  equal in every field except id/x/y/rotation/locked unless a category is fixed to one of them;
  `t1_pool` also drops compound walks that only permute identical shelves (`relabel`). Set in
  feedback_v5, every v5_no_* ablation and the annealing arm, which also gets `t3_scope:
  objective` (declared: annealing differs from its paper-v4 definition, a stronger baseline).
  feedback_v4, random_search and genetic are unchanged.
- W2 gets direct rows: `instance_comparisons` adds `feedback_v5` as a reference when v5_no_* arms
  exist (secondary references meet only arms that are not earlier references: no mirrored rows).
  W2's primary family is now 5 (vs seq_milp) + 4 (feedback_v5 vs v5_no_*) = 9 test_objective rows;
  smallest adjusted p 0.0078 x 9 ~ 0.070 > 0.05, so W2 cannot reach 0.05 and is descriptive only.
- Medium timing (no pilot run): W1 index lists medium parts first, then small, then tiny (W2 still
  runs first); the pooled descent no longer calls actions() once the budget is spent (the unpooled
  paper-v4 path is unchanged); warm-start walk generation stops at the search deadline (TIMEOUT ->
  SEARCH_TIME_LIMIT before the job deadline). The runbook adds a check of the first W1 medium part
  (stop through the pid file if jobs approach 2,700 s of training time) and lets the owner authorize
  one medium feedback_v5 pilot job first.
- genetic.py: selection RNG is `Random(seed * 1000003 + SELECTION_SEED_OFFSET)` (7,340,033) instead
  of `+ 3`, which equalled restart walk variant 3.
- Wording: `holm_primary_wilcoxon_exact_p` is the "pre-declared primary family" (họ chính khai báo
  trước), still exploratory; it was called "confirmatory" before. Column names unchanged.
- New tests: identical-swap filter on/off, fixed-category exception, relabel detection, relabel
  compound dropped, annealing neighbourhood and run without swaps/T3_LEVEL/T3_POSITION, warm-start
  walks = random_search walks (common random numbers), no-surrogate warm start keeps generation
  order, pooled ranking skipped once the budget is spent (unpooled path still calls actions once),
  walk generation stops at the search deadline, golden paper-v4 trace hash (feedback_v4 settings,
  tiny, 6 evaluations: d2d53935...458d22, identical for HEAD 0b58d04 extracted with `git archive
  HEAD backend/src` and for this tree), feedback_v5 reference rows in instance_comparisons, medium
  smoke for `wide` (seed 8205) and `columns` (8207), on-disk configs equal the builder.
- Configs: the first generated set (never run) was moved to
  var/paper-v5-configs-superseded-20261103 (69 files, content digest identical before/after the
  move), then `$env:PYTHONPATH = "scripts"; .\.venv\Scripts\python.exe scripts\build_paper_v5_configs.py`
  -> 68 configs + index.json, 1,008 jobs (W1 864 in 60 parts, medium first; W2 144 in 8 parts);
  every config re-dumps through CampaignSpec with 0 mismatches and every treatment validates as
  JointConfig; compared with the superseded set only the declared keys and the index order differ.
  datasets/schemas/optimization.schema.json regenerated (adds drop_identical_swaps);
  campaign.schema.json regenerates byte-identically.

Final-fix verification (2026-11-03; MongoDB started with
`powershell -ExecutionPolicy Bypass -File scripts/start_mongodb.ps1` -> "MongoDB connection and
indexes verified"):
- `.venv/Scripts/python.exe -m pytest backend/tests scripts/tests -q -p no:cacheprovider --basetemp var/pytest-v5-full-02`
  -> 370 passed, 3 failed, 1 warning in 298.34 s (13:23-13:28 UTC). The 3 failures are the
  pre-existing scripts/tests/test_paper_recovery.py::RecoveryTests (paper-v2 results absent:
  FileNotFoundError on experiments/results/20261023-paper-v2/paper-x2b-small/configuration.json).
- Smoke alone (`--basetemp var/pytest-v5-final-06 --durations=5`): 12 passed in 90.52 s; sequential
  medium evaluation (2 scenario seeds) 29.0 s `wide`, 27.0 s `columns`.
- ruff (backend/src, backend/tests, the v5 builder and its test): first run flagged one import
  block (I001) in test_joint_search_v5.py, reformatted, then "All checks passed!" (the reformat came
  after the full suite; the module was re-run afterwards, see the final-fix report).
- mypy: "Success: no issues found in 108 source files". `scripts/verify_architecture.py --output
  var/architecture-v5-02.json`: "Architecture PASS: 108 Python modules, 40 frontend modules".
- paper-v3 (55) and paper-v4 (77) campaign configs re-dumped through CampaignSpec: 0 mismatches.
- Report with per-item file:line, commands and outputs:
  .superpowers/sdd/2026-11-03-paper-v5-surrogate/final-fix-report.md (git-ignored).

Implemented:
- contracts/feedback.py: JointConfig v5 controls `surrogate` (walk | walk_heat), `surrogate_pool`
  (default 96 with a surrogate), `compound_moves`, `restart_samples`, `restart_evaluations`
  (requires restart_samples and <= it; effective cap 2,000), `search_seed_scope` (job | instance),
  `population` (default 8), `mutation_edits` (default 2); mode `genetic`; `V5_CONTROLS`. Absent
  controls are omitted from dumps, so paper-v3/v4 configs keep their canonical form.
- application/feedback: `surrogate.py` (heat, walking distance on the navigation grid, rearrangement
  pairing, rank), `neighborhood.t1_pool` + `actions(pool_seed, deadline)`, `restarts.search_seed`
  (instance-scoped seeds) and shared constants, coordinator warm start (trace `SURROGATE_RESTART`,
  result `restart_evaluations`) and pooled descent, `genetic.py` (steady-state GA, trace
  `GA_INIT`/`GA_OFFSPRING`).
- Generator: `DatasetSpec.layout_family` (grid, corner_entrance, wide, columns); default
  generator hashes unchanged.
- Analysis: reports pass `dataset_scales` (per-scale instance comparisons); random_search is a second
  reference (no mirrored row), feedback_v5 a reference of the v5_no_* arms (final fixes);
  pre-declared primary Holm column `holm_primary_wilcoxon_exact_p` = primary
  metrics on the pooled "all" group (or the single scale), new per-scale secondary column
  `holm_scale_wilcoxon_exact_p`, whole-table `holm_wilcoxon_exact_p` kept for reference.
- Configs: scripts/build_paper_v5_configs.py generated experiments/configs/paper-v5 (68 configs,
  1,008 jobs: W1 864 = tiny 360 + small 360 + medium 144, W2 144); `scripts/run_paper_campaigns.py
  --set paper-v5` (order W2, W1); schemas datasets/schemas/{optimization,campaign}.schema.json
  regenerated; frontend ResearchPage.tsx option `genetic`.
- Tests: backend/tests/unit/test_joint_search_v5.py, test_layout_families.py,
  test_paper_v5_smoke.py (every layout family simulates on tiny and small; one feedback_v5 and one
  genetic run on a tiny `columns` instance), test_held_out_evaluation.py additions,
  scripts/tests/test_paper_v5_configs.py.
- Docs: design section 12 (+ fixed-shelf relaxation line in 12.2), runbook paper-v5 section (and the
  paper-v4 Holm sentence updated), HOW_TO_RUN_JOINT_OPTIMIZATION.md v5 controls table and genetic mode.

Task 9 verification (2026-11-03, before the final review and its fixes; superseded by the
final-fix verification above; MongoDB started with
`powershell -ExecutionPolicy Bypass -File scripts/start_mongodb.ps1`, health check OK):
- `.venv/Scripts/python.exe -m pytest backend/tests scripts/tests -q -p no:cacheprovider --basetemp var/pytest-v5-full-01`
  -> 354 passed, 3 failed, 1 warning in 257.74 s. The 3 failures are
  scripts/tests/test_paper_recovery.py::RecoveryTests (FileNotFoundError reading
  experiments/results/20261023-paper-v2/paper-x2b-small/configuration.json: the paper-v2 results are
  not on this machine; unrelated to paper-v5, recorded as pre-existing). The warning is the existing
  Starlette/httpx deprecation.
- Smoke test alone: `.venv/Scripts/python.exe -m pytest backend/tests/unit/test_paper_v5_smoke.py -q -p no:cacheprovider --basetemp var/pytest-v5-smoke-01 --durations=0`
  -> 10 passed in 34.16 s (sequential plan per family: tiny 0.6-0.8 s, small 4.4-5.5 s; feedback_v5
  4 evaluations with a 2-evaluation warm start 8.4 s; genetic 3.0 s). Re-run after the review fixes
  (genetic test now also asserts GA_INIT and GA_OFFSPRING in the trace): 10 passed in 35.34 s
  (`--basetemp var/pytest-v5-smoke-02`).
- `.venv/Scripts/python.exe -m ruff check --config backend/pyproject.toml backend/src backend/tests scripts/build_paper_v5_configs.py scripts/tests/test_paper_v5_configs.py`
  -> All checks passed.
- `.venv/Scripts/python.exe -m mypy --config-file backend/pyproject.toml backend/src/smart_retail`
  -> Success: no issues found in 108 source files.
- `.venv/Scripts/python.exe scripts/verify_architecture.py --output var/architecture-v5-01.json`
  -> Architecture PASS: 108 Python modules, 40 frontend modules.
- paper-v3 (55 campaign configs) and paper-v4 (77) re-dumped through CampaignSpec: 0 mismatches
  with the files (no new keys leak into old configs).
- `git diff --check` -> exit 0 (no whitespace errors). Plan-touched files were normalized from CRLF
  to LF to match the index blobs (the working tree is an autocrlf=true checkout; untouched tracked
  files stay CRLF); `git diff --stat` line counts did not change.
- Order of checks: the full suite, mypy, architecture and the config round-trip ran BEFORE the LF
  normalization and the final doc edits (no production code changed after them). After the
  normalization only a 95-test subset (backend/tests/contracts, test_held_out_evaluation.py,
  test_paper_v5_smoke.py, scripts/tests/test_paper_v5_configs.py: 95 passed) and ruff re-ran; after
  the review-fix edits the smoke test and ruff were re-run again (above). The full suite was not
  re-run after the normalization.

Limitations (declared, also in the runbook):
- Frontend lint/build was not run (no node_modules); the only frontend change is one `<option>`.
- The surrogate ranks only: it ignores queues, multi-shelf routes, T2 capacity and near/far
  constraints; it pairs free categories with the full shelf list including fixed shelves (a
  relaxation; paper-v5 has no fixed assignments). Every acceptance is by simulation.
- Load calibration (orders, interval, pickers) is reused per scale from paper-v3 calibration.json,
  measured on the grid family; it is not calibrated per layout family, so utilization differs by
  family (read `picker_utilization` of each job).
- The per-scale Holm column is secondary (medium has 8 instances, smallest exact p 0.0078); the
  pre-declared primary family is the pooled "all" group. All tests stay exploratory (configs:
  `descriptive_paired_exploratory`). Reports made before this change used the old definition.
- E61/E62 select only `test_objective` among the primary metrics, so W2 (8 instances, one scale)
  has 9 rows in its primary family (5 arms vs seq_milp + 4 v5_no_* arms vs feedback_v5). The
  smallest adjusted p is 0.0078 x 9 ~ 0.070 > 0.05: W2 cannot reach 0.05 and is reported as
  descriptive (effect sizes, wins/ties), matching the config's statistical_method
  `descriptive_paired_exploratory`.
- `drop_identical_swaps` assumes a relabel of identical shelves leaves the score unchanged (the
  final review measured equal scores); the annealing arm is declared stronger than in paper-v4.
- Warm start and random_search share the (seed, variant) walk stream (common random numbers).
- Worst-case part wall clamp: parts of 24 small jobs and 6 medium jobs reach the 14,400 s campaign
  ceiling if every job uses its full cap; check wall times after the first W2 part and after the
  first W1 medium part.
- Measured overheads that count toward job wall time: pooled actions() ~6 s per call on small and
  ~22 s on medium; warm-start walk generation ~12.5 s per job on medium; warm-start ranking of 128
  walks ~3/6/17 s on tiny/small/medium; one sequential medium evaluation 27-29 s (smoke). No
  full-budget medium feedback_v5 job was timed (no pilot allowed); the final review projected
  1,750-2,300 s against 2,700 s of training time. The ~70 h estimate (tiny 5, small 19, medium 38,
  W2 8) is not a measurement of a v5 run.

Next: the project owner reviews this work and authorizes the paper-v5 run (MongoDB running,
`--set paper-v5` command in docs/research/PAPER_EXPERIMENT_RUNBOOK.md); the owner may first
authorize a single medium feedback_v5 pilot job. The runner does not pause between parts: read
the records of the first W2 part and then of `paper-v5-w1-medium-part01` (wall_s, joint_status;
snippets in the runbook) while later parts run, and stop the runner through
var\paper-v5-run.pid.json if part wall times approach the 14,400 s cap or medium jobs approach
2,700 s of training time. Reports are written only after every campaign of every block has run.
The final whole-branch review and its fix wave are done (controller re-review of the fixes is up
to the controller). Do not edit backend/src while a campaign runs (source drift guard).

---

# Current handoff - paper-v4 results read and analysed (no rerun), 2026-11-03

Request: "kết quả thực nghiệm v4 đang ở ổ F bạn hãy đọc và phân tích". Read-only analysis; no
source, config or result changed; no experiment run. The run itself happened on another machine
(ledger source path D:\Smart_Retail_Floor_Allocation\experiments\results\...).
Copies on this machine: F:/results/paper-v4-unlimited-adaptive-20261028 (77 campaigns),
F:/results/paper-v4-retry-20261028 (6 CANCELLED jobs replayed, 6/6 SUCCEEDED, validation PASS,
same runtime identity 643aab175700 and config sha as the originals), F:/results/paper-v4 (an
early cancelled start, 6/25, unused) and reports F:/reports/paper-v4-unlimited-adaptive-20261028/{V1..V5,VL}.
The reports predate the retry (V3 has 7/10 random_search_b80, VL has 0/3 random_search).

Commands: two throwaway read-only scripts in the session scratchpad run with
.venv/Scripts/python.exe -I (results.csv/statistics.json/joint-trace.csv/raw result.json); per-scale
instance-level exact Wilcoxon on test_objective via scipy 1.18.1.

Status: 1,269 jobs; all SUCCEEDED except V3 random_search_b80 3 CANCELLED and VL random_search
3 CANCELLED (both recovered by the retry). V3 random_search_b80: 5 jobs TIMEOUT at 68-76 evaluations
under 3 concurrent campaigns, while the 3 replayed alone finished 80 in ~320 s (not a clean
equal-budget arm). VL feedback_v4 TIMEOUT after 13 evaluations (~220 s each).

Findings (test_objective, relative to seq_milp, per-instance mean, n=10 instances per scale):
- V1: random_search tiny -25.9%, small -12.6%, medium -10.0%; feedback_v4 -21.5/-4.7/-2.2%;
  feedback -14.9/-3.1/-1.6%; annealing -9.1/-1.3/-1.7%. feedback_v4 vs feedback: tiny -7.8%,
  small -1.6% (10/10, p=0.002), medium -0.6% (p=0.58). random_search beats feedback_v4 on 30/30.
- V2: step 3 helps random (-2.5% vs step 1, 9/10) but not guided (5 ties, p=0.31); random_step1
  beats guided_step1 by 7%: the gap is multi-shelf perturbation, not step length or prefilter.
- V4: kicks never fired at budget 30 (no_kicks identical to feedback_v4); prefilter and t3_scope
  each worth ~2.2% (p=0.016); adaptive ~1.9% (p=0.06); multi-step slightly harmful (no_steps
  -1.1%, p=0.16). feedback_v4 never evaluated a T3 move; T3 accepted 0 everywhere.
- V3: feedback_v4 keeps improving with budget (16/30/40/80: -3.0/-4.7/-6.1/-12.1%); random_search
  is flat (-13.4% at 16, -13.3% at 30/40, -14.4% at 80). feedback_v4_b80 ~ random_search_b40.
- V5: screening changed nothing (random identical 10/10, feedback 9/10 ties) and cost feedback
  +36% wall time.
- VL: rho = 1.00 and test wait ~3,700 s (unstable queue, uncalibrated load); 7-14 evaluations
  only; not usable for conclusions.

Validity threats found:
- All instances of a scale share the same floor geometry and the same seq_milp layout (one distinct
  t1_objective per scale), and every random_search job uses search seed 1 (tiny 1 and 2). The random
  stream is therefore identical across instances: in small the same candidate (#8) is best in 50/50
  jobs and the final layout is identical; tiny #20 (seed 1) and #5 (seed 2); medium #28/#36. The
  10/10 wins are one or two RNG draws replicated, not evidence of reliability across seeds. Tiny
  seed 1 vs seed 2 differs by ~9% for random_search, as large as method gaps.
- Production reports never pass `scales` to analysis.instance_comparisons, so every row has
  scale "unknown" and per-scale inference is missing (only the unit test passes scales).
- holm_wilcoxon_exact_p (full table) cannot reach 0.05 with 10 instances; use the primary column.

Next: decide (owner) whether to (1) regenerate reports with the retry campaigns and per-scale
scales, (2) rerun random_search/feedback_v4 with several search seeds and instances with varied
geometry before any random-vs-guided claim, (3) recalibrate large load. Nothing committed.

---

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


---

## Milestone 2026-11-14 — report workflow to V5 code mapping

User requested experimental code to match the workflow presented in the paper/report. Read both supplied DOCM/DOCX as OOXML text only (no macro execution), inspected current workflow/campaign/splits/evaluation/feedback/surrogate/neighborhood and reporting source. Added docs/research/WORKFLOW_REPORT_CODE_MAPPING.md with Mermaid workflow, input/function/output traceability and nine wording/config distinctions. Ran .venv/Scripts/python.exe -X utf8 - with CampaignSpec.model_validate and planned_jobs over all 68 current V5 configs: PASS, W1 864 + W2 144 = 1008 planned jobs, each index count matched; holdout 20%, reserved time 25%, fixed joint objective, no seed screening, feedback_v5 96/32 pool and 128 warm samples checked. Receipt var/workflow-report-audit-20261114/config-check.json. UTF-8/replacement-character and Mermaid fence checks passed. Static alignment only: embedded figures/OMML were not visually verified, historical result metrics were not recomputed and no experiments were launched. Original documents, engine, configs, results and Git index preserved; inherited dirty files retained. Next: use mapping for the report workflow; any exact numeric claim still requires corresponding historical artifact verification.


## Milestone 2026-11-14 — standalone Word workflow report

Created docs/research/Doi_chieu_workflow_va_code_thuc_nghiem_V5.docx (6 pages) from the inspected mapping: input/output overview, workflow figure, 16-row code traceability, interpretation distinctions, configuration checks and limits. Used bundled Python/python-docx/Pillow. Packaged render_docx.py was attempted but blocked by missing LibreOffice; exported using a separate hidden Microsoft Word COM instance, rasterized via bundled PyMuPDF and inspected all six pages. Corrected inherited title border and caption color, re-exported and reviewed affected pages. QA receipt var/workflow-report-audit-20261114/word-qa.json. Original supplied documents and research/source/config/results preserved. No experiments or Git publication.


## Milestone 2026-11-14 — requested experiment deletion blocked

User explicitly selected deleting only experiments/results and experiments/reports on D without a new backup; code/configs/datasets and the new Word report remain outside scope. Fresh preceding inventory: 447196 result files / 343013856138 bytes and 1254 report files / 299446985 bytes; no reparse entries; no tracked files in scope; no active experiment process observed. The guarded PowerShell Remove-Item command was rejected before execution by automatic policy review with only 'blocked by policy'; no detailed reason provided. No deletion started. Both directories still exist. Receipt var/experiment-cleanup-blocked-20261114/receipt.json. Do not claim cleanup completed or bypass rejection. No backups created, no source/config/index changes.
