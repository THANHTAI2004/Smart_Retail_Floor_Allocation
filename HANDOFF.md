# Current handoff - repeated k-fold held-out evaluation (deepmg protocol), 2026-10-23

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
