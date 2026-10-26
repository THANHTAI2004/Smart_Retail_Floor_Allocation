# Current handoff - paper-v3: all fixes from the paper-v2 review, 2026-10-26

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
