# paper-v5: feedback_v5 (surrogate), GA, nhiều seed — kế hoạch cài đặt

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Cài `feedback_v5` (xếp hạng ứng viên T1 bằng surrogate hiệu chỉnh từ phản hồi T4, bước đi nhiều kệ, pha khởi động), baseline `genetic`, seed tìm kiếm theo instance, 4 dạng mặt bằng, báo cáo theo quy mô và cấu hình paper-v5 — chỉ sửa mã và kiểm thử, không chạy thực nghiệm.

**Architecture:** Mọi tùy chọn mới là trường `None` của `JointConfig`/`DatasetSpec`, bị bỏ khỏi dạng chuẩn khi vắng, nên cấu hình v3/v4 giữ nguyên hash và hành vi. Surrogate và GA là module riêng trong `application/feedback/`, coordinator chỉ nối. Engines không đổi.

**Tech Stack:** Python 3.12, Pydantic, networkx (`engines/navigation`), shapely, pytest, ruff, mypy.

**Spec:** `docs/research/EXPERIMENT_DESIGN_DEEPMG.md` mục 12.

## Global Constraints

- Không commit/push/reset (AGENTS.md); không chạy campaign/thực nghiệm; chỉ test và smoke test trong pytest.
- Vắng mặt tùy chọn mới = hành vi paper-v4: `JointConfig`/`DatasetSpec` dump không chứa khóa mới; `generate()` mặc định giữ hash: tiny `99882f1e…16c2`, small `309499d7…22c5`, medium `9aa0b7cc…1878` (seed 101, facings 6/4/3).
- Ranh giới: `application -> engines/contracts`; engines không import application.
- Đơn vị SI; seed tất định (không dùng `hash()` của Python).
- Surrogate chỉ để xếp hạng; chấp nhận vẫn bằng mô phỏng (giảm chặt).
- Mặc định: `surrogate_pool` 96 khi bật surrogate; `population` 8; `mutation_edits` 2; GA thử lai tối đa 50 lần.
- paper-v5: holdout `HOLDOUT`, seed instance 8001+, 4 dạng, W1 = 864 job, W2 = 144 job, tổng 1.008 job.
- Đồng bộ: `datasets/schemas/optimization.schema.json`, `campaign.schema.json`, docs, runbook, HANDOFF; kiểm tra tiếng Việt sau khi sửa bằng script.

## Review Focus

- Instance có kệ khóa hết (local_trap): pha khởi động và bước đi nhiều kệ không có ứng viên → bỏ qua, hạ dốc vẫn chạy (test ở Task 4).
- Mọi ứng viên T1 sai topology (surrogate trả `None`): không crash, chỉ còn nước T2 (test ở Task 3).
- Nhóm hàng có `fixed_shelf_id`: surrogate dùng kệ cố định (test ở Task 2).
- Hết `search_time_s` trong lúc xếp hạng/khởi động: dừng `SEARCH_TIME_LIMIT`, vẫn có kết quả (test ở Task 4).
- GA có `population` > ngân sách: dừng ở ngân sách, không lai (test ở Task 5).

## File Structure

| File | Trách nhiệm |
|---|---|
| `backend/src/smart_retail/contracts/feedback.py` (sửa) | Trường v5, mode `genetic`, `V5_CONTROLS`, kiểm tra hợp lệ |
| `backend/src/smart_retail/application/feedback/restarts.py` (sửa) | `search_seed()` |
| `backend/src/smart_retail/application/feedback/surrogate.py` (mới) | heat, quãng đường, giá trị, xếp hạng |
| `backend/src/smart_retail/application/feedback/neighborhood.py` (sửa) | `t1_pool()`; `actions(..., pool_seed=)` |
| `backend/src/smart_retail/application/feedback/genetic.py` (mới) | GA trạng thái ổn định |
| `backend/src/smart_retail/application/feedback/coordinator.py` (sửa) | seed, pha khởi động, gọi pool/GA |
| `backend/src/smart_retail/contracts/experiments.py`, `application/experiments/generators.py` (sửa) | `layout_family` |
| `backend/src/smart_retail/application/experiments/analysis.py`, `reports.py` (sửa) | tham chiếu random_search, scales |
| `scripts/build_paper_v5_configs.py` (mới), `scripts/run_paper_campaigns.py` (sửa) | paper-v5 |
| `backend/tests/unit/test_joint_search_v5.py`, `test_layout_families.py` (mới), `test_held_out_evaluation.py` (sửa), `scripts/tests/test_paper_v5_configs.py` (mới) | test |
| `frontend/src/features/research/ResearchPage.tsx` (sửa) | option `genetic` |

---

### Task 1: Hợp đồng `JointConfig` v5 và `search_seed`

**Files:** Modify `contracts/feedback.py`, `application/feedback/restarts.py`; Test `backend/tests/unit/test_joint_search_v5.py`

**Interfaces:**
- Produces: `JointConfig` trường mới `surrogate: Literal["walk","walk_heat"]|None`, `surrogate_pool: int|None (1..2000)`, `compound_moves: int|None (0..500)`, `restart_samples: int|None (1..2000)`, `restart_evaluations: int|None (1..20000)`, `search_seed_scope: Literal["job","instance"]|None`, `population: int|None (2..200)`, `mutation_edits: int|None (1..50)`; mode thêm `"genetic"`; `V5_CONTROLS: tuple[str, ...]` (8 tên trên).
- Produces: `restarts.search_seed(sections: dict, seed: int, scope: str | None) -> int`.

- [ ] **Step 1: Viết test hỏng** trong `test_joint_search_v5.py` (dùng lại `JOINT` và fixture `tiny` như `test_joint_search_v4.py`):
  - `test_absent_v5_controls_keep_the_paper_v4_canonical_form`: `JointConfig(**JOINT, mode="feedback").model_dump(mode="json")` không giao `V5_CONTROLS`; với `surrogate="walk_heat", population=4` thì hai khóa này có trong dump.
  - `test_restart_controls_are_validated`: `ValueError` khi `restart_evaluations=3` thiếu `restart_samples`, khi `restart_evaluations=5, restart_samples=4`; hợp lệ khi `restart_samples=8, restart_evaluations=3`.
  - `test_search_seed_scope`: `search_seed(s, 1, None) == 1 == search_seed(s, 1, "job")`; `search_seed(s, 1, "instance")` khác với instance seed 102 cùng quy mô, bằng nhau khi gọi lại, khác `search_seed(s, 2, "instance")`; không phụ thuộc khóa `optimization`.
- [ ] **Step 2:** `.venv/Scripts/python.exe -m pytest backend/tests/unit/test_joint_search_v5.py -q -p no:cacheprovider --basetemp var/pytest-v5-t1` → FAIL (import/attribute).
- [ ] **Step 3: Cài.** Serializer bỏ khóa `None` của `V4_CONTROLS + V5_CONTROLS`. `search_seed`: scope `"instance"` → `int(sha256(f"{canonical_hash({k: sections[k] for k in sorted(sections) if k != 'optimization' and not k.startswith('_')})}:{seed}").hexdigest()[:12], 16)`; ngược lại trả `seed`.
- [ ] **Step 4:** chạy lại lệnh Step 2 → PASS; chạy `backend/tests/unit/test_joint_search_v4.py` → PASS.
- [ ] **Step 5:** Không commit (AGENTS.md).

### Task 2: Surrogate `walk_heat`

**Files:** Create `application/feedback/surrogate.py`; Test `test_joint_search_v5.py`

**Interfaces:**
- Consumes: `engines.navigation.navigation`, `contracts.inputs.to_domain`, feedback `sku_pick_counts` của `diagnostics.analyze`.
- Produces:
  - `heat(feedback: dict, sections: dict, weighted: bool) -> dict[str, float]` — nhóm → số đơn vị lấy + 1; `weighted=False` → 1.0.
  - `distances(sections: dict, poses: dict[str, list], deadline: float = math.inf) -> dict[str, float] | None` — kệ → quãng đường ngắn nhất (m, Dijkstra trọng số `weight`) từ `start` tới điểm lấy hàng gần nhất trong mọi mặt; `None` khi `navigation` ném `EngineError` khác `TIMEOUT`/`CANCELLED` (hai mã này ném lại).
  - `value(sections: dict, distance: dict[str, float], heat: dict[str, float]) -> float` — nhóm `fixed_shelf_id` dùng d của kệ đó; nhóm còn lại xếp heat giảm dần ghép với d tăng dần, danh sách kệ lặp khi thiếu.
  - `rank(candidates: list[dict], sections: dict, heat: dict[str, float], deadline: float = math.inf) -> list[dict]` — bỏ ứng viên `distances is None`, gắn `action["surrogate"] = value`, sắp theo `(value, canonical_hash(decisions))`.

- [ ] **Step 1: Viết test hỏng:**
  - `test_surrogate_value_is_the_optimal_one_to_one_pairing`: trên tiny, `d = distances(sections, initial poses)`; với heat tùy ý (vd `{"C0": 9, "C1": 1, "C2": 4}`) `value` == min trên mọi đơn ánh nhóm → kệ (`itertools.permutations`) của Σ h·d (sai số 1e-9).
  - `test_surrogate_respects_fixed_category_shelves`: đặt `fixed_shelf_id = "S3"` cho nhóm nóng nhất → `value` dùng `d["S3"]` cho nhóm đó, bằng tính tay.
  - `test_surrogate_heat_weighting`: `heat(feedback, sections, False)` toàn 1.0; `heat(..., True)["C0"] == 1 + Σ pick của SKU thuộc C0`.
  - `test_surrogate_rank_drops_invalid_topology(monkeypatch)`: monkeypatch `navigation` ném `EngineError("UNREACHABLE", ...)` cho một layout → `rank` loại nó và giữ thứ tự tăng của các ứng viên còn lại.
- [ ] **Step 2:** chạy test → FAIL.
- [ ] **Step 3:** Cài `surrogate.py` theo Interfaces; `navigation(..., required_faces={s.id: set(range(s.faces))})`, khóa target `"{id}:{face}"`, min theo mặt; `to_domain(sections)` một lần mỗi lời gọi `rank`.
- [ ] **Step 4:** chạy test → PASS.
- [ ] **Step 5:** Không commit.

### Task 3: Tập ứng viên T1 xếp hạng (`t1_pool`)

**Files:** Modify `application/feedback/neighborhood.py`; Test `test_joint_search_v5.py`

**Interfaces:**
- Consumes: `surrogate.heat`, `surrogate.rank`, `restarts.restart`.
- Produces: `t1_pool(state: dict, feedback: dict, sections: dict, config: JointConfig, pool_seed: int, deadline: float = math.inf) -> list[dict]`; `actions(state, feedback, sections, config, weights=None, pool_seed=None, deadline=math.inf)`. Khi `config.surrogate_pool or config.surrogate` có giá trị và `pool_seed` khác `None`, hàng đợi T1 = `t1_pool(...)`; ngược lại giữ nguyên v4.

Thuật toán `t1_pool`:
```text
singles = mọi kệ không khóa: dời ±k·grid theo t1_steps (4 hướng), xoay; mọi cặp hoán đổi; bỏ vi phạm violations()
rng = Random(pool_seed); pool = rng.sample(singles, min(len, surrogate_pool or 96))
compound: i = 1..compound_moves: restart(state, sections, pool_seed, i, max_step, edits=rng.randint(2, max(2, movable)))
  -> action type "T1_COMPOUND" (bỏ assignment/placements), bỏ None
khử trùng theo canonical_hash(decisions)
config.surrogate -> rank(pool, sections, heat(feedback, sections, surrogate == "walk_heat"), deadline)
không surrogate -> rng.shuffle(pool)
```
- [ ] **Step 1: Viết test hỏng:**
  - `test_pool_samples_every_shelf_and_is_deterministic(initial)` (small, `surrogate_pool=96`, không surrogate): tập kệ `changed` của pool phủ ≥ 8/12 kệ; cùng `pool_seed` → giống hệt; khác seed → thứ tự khác; mọi pose qua `violations()`.
  - `test_pool_ranked_by_surrogate(initial)`: `surrogate="walk_heat"` → giá trị `surrogate` không giảm dọc danh sách T1 của `actions(..., pool_seed=1)`.
  - `test_compound_moves_change_several_shelves(initial)`: `compound_moves=8` → có ≥1 `T1_COMPOUND`, mỗi cái `len(changed) >= 2`.
  - `test_pool_without_valid_topology_keeps_t2_actions(initial, monkeypatch)`: `surrogate.distances` luôn `None` → không có hành động T1, vẫn có T2, không lỗi.
  - `test_v4_neighborhood_unchanged_without_pool(initial)`: `actions(...)` với cấu hình v4 bằng hệt khi truyền `pool_seed=5`.
- [ ] **Step 2:** chạy → FAIL.
- [ ] **Step 3:** Cài theo Interfaces; hàng đợi T2/T3/T4 không đổi.
- [ ] **Step 4:** chạy test v5 + v4 → PASS.
- [ ] **Step 5:** Không commit.

### Task 4: Coordinator — seed, pha khởi động, pool

**Files:** Modify `application/feedback/coordinator.py`; Test `test_joint_search_v5.py`

**Interfaces:**
- Consumes: Task 1–3.
- Produces: trace event `action: "SURROGATE_RESTART"` (status `EVALUATING`/`FAILED`, `variant`, `surrogate` nếu có); `result["joint"]["restart_evaluations"]` khi bật.

Thay đổi:
- `seed = search_seed(sections, data.config.seed, config.search_seed_scope)` thay mọi chỗ dùng `data.config.seed` trong random_search, `anneal`, `kick`.
- Trước vòng hạ dốc (mode feedback) khi `config.restart_evaluations`: sinh `restart(initial, sections, seed, v, max_step=max_step)` với v = 1..`restart_samples`, bỏ `None`/trùng `seen`; có surrogate → `rank` bằng heat của `analyze(best, sections)`; đánh giá tối đa `restart_evaluations` ứng viên đầu bằng `assess(decision, reference=best)` (lỗi khác TIMEOUT/CANCELLED → event FAILED, tiếp tục; TIMEOUT/CANCELLED → dừng như vòng chính); `local = best = ứng viên tốt nhất`.
- Gọi `actions(local, feedback, sections, config, weights, pool_seed=seed * 1000003 + 15485863 * iteration, deadline=min(deadline, search_deadline))`.

- [ ] **Step 1: Viết test hỏng** (tiny, `max_evaluations=6`, `time_limit_s` đủ, như `test_iterated_local_search_kicks_after_local_convergence`):
  - `test_restart_phase_spends_declared_evaluations(tiny)`: `restart_samples=8, restart_evaluations=3, surrogate="walk_heat", surrogate_pool=24` → đúng 3 event `SURROGATE_RESTART` có `status` EVALUATING hoặc FAILED, `joint["evaluations"] == 6`, `incumbent_curve` giảm dần, best ≤ initial.
  - `test_feedback_v5_is_deterministic(tiny)`: chạy hai lần cùng cấu hình → cùng `best["score_fraction"]` và cùng chuỗi `candidate_id`.
  - `test_restart_phase_skips_locked_layouts(tiny)`: mọi kệ `locked: true` → không có event `SURROGATE_RESTART` EVALUATING, kết quả có `best`, không lỗi.
  - `test_v5_search_time_limit(tiny)`: `search_time_s=1e-3` → `joint["status"] == "SEARCH_TIME_LIMIT"` và có `best`.
  - `test_instance_seed_scope_changes_random_search_stream(tiny)`: random_search `max_evaluations=4` với `search_seed_scope="instance"` trên tiny seed 101 và 102 → chuỗi `changed` của event MULTISTART_RESTART khác nhau; với scope vắng thì giống nhau (chỉ T1 poses đổi theo cùng `variant`).
- [ ] **Step 2:** chạy → FAIL.
- [ ] **Step 3:** Cài như trên; không đổi đường đi khi các trường v5 vắng.
- [ ] **Step 4:** chạy v5 + v4 + `test_joint_no_incumbent*` → PASS.
- [ ] **Step 5:** Không commit.

### Task 5: Baseline `genetic`

**Files:** Create `application/feedback/genetic.py`; Modify `coordinator.py`; Test `test_joint_search_v5.py`

**Interfaces:**
- Produces: `evolve(initial: dict, sections: dict, config: JointConfig, seed: int, assess, seen: set, archive: list, event, exhausted) -> tuple[dict, str]` (best, termination ∈ `EVALUATION_LIMIT`, `NEIGHBORHOOD_EXHAUSTED`, `TIMEOUT`, `CANCELLED`). Coordinator: `elif config.mode == "genetic": best, termination = evolve(best, ...)`.

Thuật toán (rng = `Random(seed * 1000003 + 3)`):
```text
pop = [initial] + đánh giá restart(initial, sections, seed, v, max_step) với v = 1.. đến khi đủ population-1 cá thể hoặc hết ngân sách
lặp khi chưa exhausted():
  A, B = giải đấu 2 (mỗi lần lấy 2 ngẫu nhiên, chọn điểm thấp hơn)
  tối đa 50 lần: con[kệ] = pose của A hoặc B (rng.random() < 0.5); nhận khi violations() rỗng
  không có con hợp lệ -> con = poses của cha mẹ tốt hơn
  con = restart({"decisions": {"poses": con, "routing_policy": A}}, sections, seed + 104729, lượt, max_step, edits=mutation_edits or 2)
  trùng seen -> bỏ, không tốn ngân sách (DUPLICATE_LIMIT liên tiếp -> NEIGHBORHOOD_EXHAUSTED)
  đánh giá; event action "GA_OFFSPRING"; tốt hơn cá thể kém nhất -> thay
```
- [ ] **Step 1: Viết test hỏng:**
  - `test_genetic_respects_budget_and_is_deterministic(tiny)`: `mode="genetic", max_evaluations=8, population=4` → `evaluations == 8`, status `EVALUATION_LIMIT`, có event `GA_OFFSPRING`, chạy lại cùng best; mọi poses trong `integrated["candidates"]` không vi phạm `violations()`.
  - `test_genetic_population_larger_than_budget(tiny)`: `population=8, max_evaluations=4` → `evaluations == 4`, không có `GA_OFFSPRING`.
- [ ] **Step 2:** chạy → FAIL.
- [ ] **Step 3:** Cài `genetic.py`; nối coordinator.
- [ ] **Step 4:** chạy → PASS.
- [ ] **Step 5:** Không commit.

### Task 6: Dạng mặt bằng `layout_family`

**Files:** Modify `contracts/experiments.py`, `application/experiments/generators.py`; Test `backend/tests/unit/test_layout_families.py`

**Interfaces:**
- Produces: `DatasetSpec.layout_family: Literal["grid","corner_entrance","wide","columns"] | None`, bỏ khỏi dump khi `None`.

Hình học (n kệ, kệ 2 × 0,6 m; x, y là góc dưới trái):
| Dạng | cols | vị trí kệ i | biên (W × H) | lối vào | rotation |
|---|---|---|---|---|---|
| `None`/`grid` | ⌈√n⌉ | (2 + 3·(i mod cols), 2 + 2,5·⌊i/cols⌋) | (3·cols+4) × (2,5·rows+4) | (0; H/2) | 0 |
| `corner_entrance` | như grid | như grid | như grid | (0; 1,0) | 0 |
| `wide` | ⌈1,5·√n⌉ | như grid | như grid | (0; H/2) | 0 |
| `columns` | ⌈√n⌉ | (2 + 2,5·(i mod cols), 2 + 3·⌊i/cols⌋) | (2,5·cols+4) × (3·rows+4) | (0; H/2) | 90 |

- [ ] **Step 1: Viết test hỏng:**
  - `test_default_generator_hash_unchanged`: hash `generate()` seed 101 tiny/small/medium bằng ba giá trị trong Global Constraints; `DatasetSpec(id="x").model_dump()` không có `layout_family`.
  - `test_layout_families_are_valid` (tham số hóa family × tiny/small/medium): `violations()` rỗng, `validate_topology` không lỗi; `grid` cho cùng hình học với mặc định; `corner_entrance` có entrance `(0, 1.0)`; `columns` mọi kệ rotation 90; `wide` có W/H lớn hơn grid.
- [ ] **Step 2:** chạy → FAIL.
- [ ] **Step 3:** Cài theo bảng; manifest `limitations` thêm dòng `Layout family: <tên>` khi có.
- [ ] **Step 4:** chạy → PASS; `backend/tests/unit/test_engines.py` → PASS.
- [ ] **Step 5:** Không commit.

### Task 7: Báo cáo theo quy mô và tham chiếu random_search

**Files:** Modify `application/experiments/analysis.py:186-192`, `application/experiments/reports.py:74-93`; Test `backend/tests/unit/test_held_out_evaluation.py`

**Interfaces:**
- Produces: `reports.dataset_scales(roots: list[Path]) -> dict[str, str]` (đọc `datasets/*/manifest.json`, `dataset_id -> spec.scale`, bỏ manifest không có `spec`); `report()` gọi `analyze(rows, selected, dataset_scales(roots))`. `instance_comparisons` thêm `"random_search"` làm tham chiếu khi có trong arms và chưa là tham chiếu.

- [ ] **Step 1: Viết test hỏng** (theo mẫu có sẵn ở `test_held_out_evaluation.py:407`):
  - `test_random_search_is_a_second_instance_reference`: rows có seq_milp, random_search, feedback_v5 → có record `reference == "random_search", treatment == "feedback_v5"` và record reference `seq_milp` giữ nguyên.
  - `test_dataset_scales_from_manifests(tmp_path)`: hai manifest giả (`{"dataset_id": "a", "spec": {"scale": "small"}}`, một không `spec`) → `{"a": "small"}`.
- [ ] **Step 2:** chạy → FAIL.
- [ ] **Step 3:** Cài.
- [ ] **Step 4:** chạy toàn bộ `test_held_out_evaluation.py` → PASS.
- [ ] **Step 5:** Không commit.

### Task 8: Cấu hình paper-v5, runner, frontend, schema

**Files:** Create `scripts/build_paper_v5_configs.py`, `scripts/tests/test_paper_v5_configs.py`; Modify `scripts/run_paper_campaigns.py` (`SETS["paper-v5"] = ["W2", "W1"]`), `frontend/src/features/research/ResearchPage.tsx`, `datasets/schemas/optimization.schema.json`, `datasets/schemas/campaign.schema.json`

**Interfaces:**
- Consumes: `build_paper_configs` (`CV_METRICS, HOLDOUT, SCALES, arm, campaign, experiment`), `build_paper_v4_configs` (`FEEDBACK, V4, V4_SCALES, finalize`).
- Produces: `build() -> list[tuple[str, dict]]`; `V5 = {**V4, "surrogate": "walk_heat", "surrogate_pool": 96, "compound_moves": 32, "restart_samples": 128, "search_seed_scope": "instance"}` cộng `restart_evaluations` = 10/8/10 (tiny/small/medium); ablation `v5_no_surrogate` (`surrogate` None, giữ `surrogate_pool` 96), `v5_no_compound` (`compound_moves` None), `v5_no_restart` (`restart_samples`, `restart_evaluations` None), `v5_no_heat` (`surrogate: "walk"`); `genetic` = `mode "genetic", population 8, mutation_edits 2`; random_search/annealing/genetic/feedback_v4 thêm `search_seed_scope: "instance"`. OUT `experiments/configs/paper-v5`, không ghi đè.

- [ ] **Step 1: Viết test hỏng** `test_paper_v5_configs.py`: `build()` → W1 có 3 campaign quy mô, tổng job sau `finalize` = 864 (W1) và 144 (W2); mỗi treatment qua `JointConfig.model_validate`; dataset có đủ 4 dạng mỗi quy mô; seed tìm kiếm [1..5] tiny/small, [1..3] medium/W2; không dataset seed nào < 8001.
- [ ] **Step 2:** chạy `.venv/Scripts/python.exe -m pytest scripts/tests/test_paper_v5_configs.py -q -p no:cacheprovider --basetemp var/pytest-v5-cfg` (với `PYTHONPATH=scripts`) → FAIL.
- [ ] **Step 3:** Cài; chạy `$env:PYTHONPATH="scripts"; .venv/Scripts/python.exe scripts/build_paper_v5_configs.py` → in tổng `1008`. Thêm `<option value="genetic">Genetic Algorithm — equal evaluation budget</option>`. Sinh lại hai schema bằng `json.dumps(Model.model_json_schema(), indent=2, ensure_ascii=False) + "\n"` (kiểm tra trước: tái tạo từ mã cũ cho bytes giống file hiện tại).
- [ ] **Step 4:** test → PASS; `backend/tests/contracts/test_inputs.py` → PASS.
- [ ] **Step 5:** Không commit.

### Task 9: Kiểm chứng toàn bộ và tài liệu

**Files:** Modify `docs/research/PAPER_EXPERIMENT_RUNBOOK.md`, `docs/research/HOW_TO_RUN_JOINT_OPTIMIZATION.md`, `HANDOFF.md`

- [ ] **Step 1:** Khởi động MongoDB `powershell -ExecutionPolicy Bypass -File scripts/start_mongodb.ps1`; `.venv/Scripts/python.exe -m pytest backend/tests scripts/tests -q -p no:cacheprovider --basetemp var/pytest-v5-full-01` → 0 failed (ghi số thật).
- [ ] **Step 2:** ruff `backend/src backend/tests scripts/build_paper_v5_configs.py scripts/tests/test_paper_v5_configs.py` PASS; mypy PASS; `scripts/verify_architecture.py --output var/architecture-v5-01.json` PASS.
- [ ] **Step 3:** Dump lại mọi config `experiments/configs/paper-v3` và `paper-v4` qua `CampaignSpec` → 0 khác biệt so với file (không khóa mới).
- [ ] **Step 4:** Runbook mục paper-v5 (lệnh sinh, lệnh chạy `--set paper-v5`, ước tính ~70 h, chưa chạy); HOW_TO_RUN bảng tùy chọn v5 và `genetic`; HANDOFF mục mới (lệnh, kết quả thật, giới hạn: frontend không lint/build vì thiếu `node_modules`, surrogate bỏ qua hàng đợi, tải không hiệu chỉnh theo dạng mặt bằng; bước tiếp: chủ dự án duyệt và chạy). Kiểm tra tiếng Việt (không có ký tự `�`, dấu đúng).
- [ ] **Step 5:** `git diff --check` PASS; không commit.
