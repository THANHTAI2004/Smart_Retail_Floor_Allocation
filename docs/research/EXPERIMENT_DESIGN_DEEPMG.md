# Thiết kế thực nghiệm cho bài báo (hướng A, theo phương pháp deepmg)

Ngày: 2026-10-23. Trạng thái: **ĐÃ CÀI ĐẶT hạ tầng (mục 7.1–7.5)**, pilot 7.6 xem
mục 9. paper-v2 đã chạy và được đánh giá; thiết kế chạy chính hiện hành là **paper-v3,
mục 10** (chưa chạy).

Nguồn phương pháp: deepmg 1.0.33 (Met2Img, Thanh-Hai Nguyen),
<https://pypi.org/project/deepmg/>. deepmg là framework *phân loại* metagenomics;
dự án này là bài toán *tối ưu + mô phỏng*. Vì vậy tài liệu này chuyển các
**nguyên tắc** thực nghiệm của deepmg sang bài toán tối ưu, không chép các chỉ số
phân loại (ACC/AUC/MCC) vốn không áp dụng được.

Phạm vi bài báo (hướng A): tối ưu tích hợp T1 bố trí kệ → T2 phân bổ nhóm hàng →
T3 xếp SKU → T4 mô phỏng, với các chế độ sequential / feedback / exact / hybrid,
kiểm tra ràng buộc độc lập và tái lập bằng checksum. Không tuyên bố tối ưu toàn
cục ngoài không gian hữu hạn đã khai báo, không tuyên bố kiểm chứng thực địa.

## 1. Ánh xạ nguyên tắc deepmg sang dự án

| Nguyên tắc deepmg | Tùy chọn deepmg (mặc định) | Áp dụng cho dự án |
|---|---|---|
| Lặp lại k-fold phân tầng: "10 times with 10-stratified-cross-validation" | `-k/--n_folds` (10), `--run_time` (1) | Chia **tập đơn hàng/nhu cầu** thành k fold phân tầng theo nhóm hàng và khung giờ. Tối ưu bằng nhu cầu của k−1 fold, **đánh giá T4 trên fold còn lại**. Lặp R lần với thứ tự xáo khác nhau. |
| Seed liên tiếp, có ghi lại | `--seed_value_begin` (1) | Seed của lượt r = `seed_begin + r`. Seed này quyết định cách chia fold, seed thuật toán và seed mô phỏng. Ghi vào snapshot. |
| Holdout | `--test_size` | **Holdout theo thời gian**: tối ưu trên 80% đơn hàng đầu, đánh giá trên 20% cuối. |
| Kiểm định ngoài | `--test_ext`, `--ext_data` (`*z_x.csv`) | **Bộ instance ngoài** được khóa từ đầu, không dùng khi phát triển hay tinh chỉnh: (a) instance tổng hợp với dải seed generator riêng; (b) instance có nhu cầu lấy từ Instacart/dunnhumby nếu có. Chỉ chạy một lần, ở cuối. |
| Mọi bộ học dùng cùng cách chia | SVM/RF/kNN/CNN trên cùng các fold | Mọi phương pháp chạy trên **cùng instance × lượt × fold** (thiết kế ghép cặp). |
| Tinh chỉnh tham số bằng CV lồng | `--grid_coef_time` (5), `--cv_coef_time` (4), `--metric_selection` (roc_auc) | Tinh chỉnh `max_iterations`, `candidate_count`, trọng số mục tiêu **chỉ bằng CV bên trong tập huấn luyện**. Tiêu chí chọn khai báo trước: `holdout_objective`. Không bao giờ tinh chỉnh trên fold kiểm tra. |
| Báo cáo theo fold và trung bình theo lượt | `*_file_eachfold.txt`, `*_file_mean_*.txt`, `--save_folds`, `--save_avg_run` | Mỗi dòng trong `runs.json` có `cv_run` và `cv_fold`. Thêm `fold_results.json`, `run_means.json` và `summary.json`. |
| Ghi tham số để tái lập | `--save_para=y` | Đã có: snapshot đầu vào bất biến, `configuration.json`, danh tính source/dependency và checksum. |
| Bỏ qua thí nghiệm đã xong, đánh dấu hoàn tất | `--search_already` (y), hậu tố `_ok` | Đã có: hàng đợi bền vững có tạm dừng/tiếp tục. Thêm trạng thái hoàn tất rõ ràng cho từng campaign. |
| Ma trận nhầm lẫn bên cạnh độ chính xác | confusion matrix | **Ma trận trạng thái**: đếm SUCCEEDED / INFEASIBLE / PROBLEM_LIMIT / FAILED / WORKER_* theo phương pháp × quy mô. Không coi PROBLEM_LIMIT là bằng chứng vô nghiệm. |

## 2. Câu hỏi nghiên cứu

- **RQ1 – Đúng đắn:** mọi lời giải được chấp nhận có qua được kiểm tra ràng buộc
  độc lập với 0 vi phạm không? MILP có khớp với exact ở quy mô Tiny không?
- **RQ2 – Chất lượng/chi phí:** MILP, greedy, first-fit kém exact bao nhiêu (gap)?
  Từ quy mô nào exact vượt ngân sách?
- **RQ3 – Lợi ích tích hợp và tổng quát hóa:** feedback/hybrid có tốt hơn
  sequential trên **dữ liệu nhu cầu chưa thấy** (fold kiểm tra, holdout, instance
  ngoài) không?
- **RQ4 – Đóng góp thành phần và độ nhạy:** bỏ từng thành phần thì mất bao nhiêu?
  Kết luận có giữ khi thay đổi từng yếu tố một không?

## 3. Chỉ số

Chỉ số chính, khai báo trước như `--metric_selection`: **`holdout_objective`**
(hàm mục tiêu tích hợp đánh giá trên fold kiểm tra).

Chỉ số phụ: `mean_distance_m`, `mean_wait_s`, `joint_objective` (trên tập huấn
luyện), **khoảng cách tổng quát hóa** = `holdout_objective − joint_objective`,
`gap_to_exact` = (z − z*)/|z*| khi có exact, `joint_evaluations`,
`joint_iterations_to_best`, `wall_s`, `peak_child_rss_bytes`, ma trận trạng thái.
Đơn vị SI (m, s, byte).

## 4. Các khối thực nghiệm

Phương pháp so sánh (M): `seq-greedy` (greedy + first-fit + sequential),
`seq-milp` (MILP + MILP + sequential), `feedback`, `hybrid`, `exact` (chỉ Tiny,
không gian hữu hạn).

Instance: dùng `seed` khác nhau của DatasetSpec để sinh **nhiều instance cho
mỗi quy mô**, thay vì một instance chạy nhiều seed.

| Khối | RQ | Instance | Đánh giá | Phương pháp | Số job (ước tính) |
|---|---|---|---|---|---|
| X1 Đúng đắn và exact | RQ1, RQ2 | Tiny × 10 | 30 seed, không CV | 5 | 10×5×30 = 1.500 |
| X2 So sánh chính | RQ3 | Tiny × 3, Small × 3 đại diện | **10 lượt × 10 fold** (giống mặc định deepmg) | 4 (+exact ở Tiny) | Tiny 3×5×100 = 1.500; Small 3×4×100 = 1.200 |
| X2b Mở rộng instance | RQ3 | Tiny × 10, Small × 10, Medium × 5 | 5 lượt × 2 fold (5×2cv) | 4 | 25×4×10 = 1.000 |
| X3 Holdout và kiểm định ngoài | RQ3 | Khóa riêng: tổng hợp × 10, thực × n | holdout thời gian 80/20, 10 seed | 4 | ~400 + n |
| X4 Khả năng mở rộng | RQ2 | Tiny/Small/Medium/Large × 5 | 10 seed, không CV | 4 | 20×4×10 = 800 |
| X5 Ablation | RQ4 | Small × 3 | 5×2cv | feedback bỏ lần lượt: feedback, wait weight, multistart, local search | 3×5×10 = 150 |
| X6 Độ nhạy (từng yếu tố một) | RQ4 | Small × 3 | fold cố định, 10 seed | 2 (seq-milp, feedback) × mỗi mức của tốc độ khách đến, số nhân viên, hệ số nhu cầu, trọng số | ~3×2×10×(4 yếu tố × 3 mức) = 720 |

Giới hạn hiện tại là 1.000 job mỗi campaign, nên mỗi khối lớn phải **tách thành
nhiều campaign** theo instance hoặc phương pháp, mỗi campaign có thư mục output
mới. Thời gian chạy phải ước lượng lại bằng pilot (xem mục 7). Không dùng số
liệu cũ thay cho số đo mới.

Sửa nhiễu của E06: X6 chỉ đổi **một** yếu tố mỗi lần. Không đổi tốc độ khách
đến cùng lúc với số nhân viên.

## 5. Phân tích thống kê

deepmg chỉ báo trung bình theo fold và theo lượt. Bài báo cần thêm kiểm định:

1. **Đơn vị phân tích.** Các fold trong cùng một lượt dùng chung dữ liệu huấn
   luyện nên không độc lập. Trong một instance, dùng **kiểm định t hiệu chỉnh
   lấy mẫu lại Nadeau–Bengio** cho R×k kết quả. Giữa các instance, lấy trung bình
   theo instance rồi kiểm định.
2. **Hai phương pháp:** Wilcoxon signed-rank ghép cặp theo instance, kèm cỡ hiệu
   ứng Vargha–Delaney A12 và khoảng tin cậy 95% bootstrap của trung vị chênh lệch.
3. **Từ 3 phương pháp trở lên:** Friedman → hậu nghiệm Nemenyi, hoặc Wilcoxon
   với hiệu chỉnh Holm; vẽ biểu đồ critical difference.
4. **Đa so sánh:** giữ hiệu chỉnh Holm như `analysis.py` đang làm, áp dụng cho
   từng họ giả thuyết khai báo trước.
5. Giữ mọi job thất bại hoặc vượt giới hạn trong mẫu số khi tính tỷ lệ; chỉ số
   lời giải chỉ tính trên kết quả hợp lệ (như giả định hiện có).

Hiện trạng: `analysis.py` dùng t-test ghép cặp + d_z + Holm, lấy trung bình
seed trước khi ghép cặp. Chưa có Wilcoxon, Friedman, Nadeau–Bengio, A12 hay
bootstrap.

## 6. Bảng và hình cho bài báo

- Bảng 1: đặc trưng instance theo quy mô (số kệ, nhóm hàng, SKU, đơn hàng).
- Bảng 2: ma trận trạng thái (tương tự confusion matrix của deepmg).
- Bảng 3: gap so với exact (X1), trung vị [IQR].
- Bảng 4: `holdout_objective` mean ± sd theo fold và theo lượt (X2), cùng p Holm và A12.
- Hình: boxplot quãng đường/thời gian chờ; biểu đồ CD; log thời gian chạy theo
  quy mô (X4); thanh ablation (X5); đường độ nhạy (X6); sơ đồ mặt bằng trước/sau.
- Mục "Threats to validity": dữ liệu tổng hợp, T4 chưa hiệu chỉnh bằng dữ liệu
  thật, không gian exact hữu hạn, máy đo không kiểm soát tải.

## 7. Phần cần cài đặt trước khi chạy

1. **Chia fold đơn hàng** trong `application/experiments`: thêm vào DatasetSpec
   các trường `split` = `kfold` | `temporal_holdout` | `none`, `n_folds`,
   `cv_run`, `cv_fold`, `test_size`. Phân tầng theo nhóm hàng và khung giờ.
   Ghi chỉ số đơn hàng của từng fold và checksum vào snapshot.
2. **Đánh giá trên tập kiểm tra:** T4 chạy trên đơn hàng của fold kiểm tra với
   layout đã tối ưu trên tập huấn luyện. Hiện tại `holdout_seeds` chỉ đổi seed
   kịch bản, chưa tách tập đơn hàng.
3. **Mở rộng sinh campaign:** tự sinh R×k job từ một cấu hình, tách campaign khi
   vượt 1.000 job.
4. **Phân tích:** thêm `fold_results.json`, `run_means.json`, Wilcoxon, Friedman/
   Nemenyi, Nadeau–Bengio, A12 và bootstrap. Cập nhật schema JSON, fixture và
   tài liệu đi kèm.
5. **Kiểm thử:** fold không chồng lấn và phủ đủ tập; cùng seed cho cùng cách chia;
   cách chia giống nhau giữa các phương pháp; dữ liệu kiểm tra không lọt vào
   khâu tối ưu.
6. **Pilot:** chạy 1 lượt × 10 fold trên một instance Tiny và một Small để đo
   thời gian mỗi job, rồi mới chốt số lượt, số instance và ngân sách.

### Đã cài đặt (2026-10-23)

| Mục | Vị trí | Ghi chú |
|---|---|---|
| Hợp đồng campaign | `contracts/experiments.py`: `EvaluationSpec` (`split`, `n_folds`, `test_size`, `budget_fraction`, `stratify`), `CampaignSpec.evaluation`, `schema_version` "1.1", `planned_jobs`; `DatasetSpec.facings` | Seed của campaign = một lượt lặp (giống `--seed_value_begin`/`--run_time`). Cấu hình 1.0 không đổi dạng chuẩn/hash. |
| Chia fold | `application/experiments/splits.py` | Phân tầng theo nhóm hàng chiếm nhiều đơn vị nhất trong đơn; round-robin trên các tầng đã xáo bằng seed; kích thước fold lệch ≤ 1. Kế hoạch ghi bất biến ở `datasets/<id>/splits/<seed>.json` kèm SHA-256. |
| Ước lượng nhu cầu và đánh giá | `application/evaluation.py`; `OptimizationInput.evaluation` | Nhu cầu SKU = đơn vị đặt trong tập con × số đơn tổng / số đơn tập con. `to_domain` gỡ `evaluation` nên engine không thấy đơn kiểm tra. Tối ưu dùng `(1 − budget_fraction)` ngân sách; phần còn lại dùng để chạy lại T1–T4 với quyết định cố định trên đơn kiểm tra, cùng tiến trình worker có thể dừng. |
| Thống kê | `application/experiments/analysis.py` | Đơn vị ghép cặp `(seed, cv_fold)`; Wilcoxon, Nadeau–Bengio, A12, bootstrap CI trung vị, Friedman + Nemenyi (khối = trung bình theo dataset; khối theo đơn vị chỉ thăm dò), Holm riêng từng họ kiểm định. |
| Báo cáo | `reports.py` | Thêm `fold_results.csv`, `run_means.csv`, `status_matrix.csv`, `rankings.csv`; `analyze` nhận nhiều campaign (cùng danh tính source, không trùng job). |
| Tách campaign | `partition.py`; CLI `split-config --config X --output-dir D --max-jobs 1000` | Đơn vị không tách: một dataset × một nhóm seed, giữ mọi phương pháp và fold cùng campaign. |

Phát hiện khi cài đặt, cần đưa vào thiết kế:

1. **Instance mặc định bị suy biến.** Với `facings=1`, toàn bộ nhóm hàng của Tiny/Small
   vừa trên một kệ gần cửa nên mọi hành trình có cùng quãng đường; không phương pháp nào
   khác được phương pháp nào. Thực nghiệm bài báo phải dùng `facings` ≥ 4 (Small) hoặc
   ≥ 6 (Tiny) để ràng buộc sức chứa có hiệu lực.
2. **Hàm mục tiêu phải cùng định nghĩa.** Phương án không joint chấm bằng mục tiêu tích hợp
   (`integrated-v1`), phương án joint chấm bằng mục tiêu joint 4 thành phần. Mỗi record ghi
   `objective_definition`; phân tích bỏ kiểm định khi hai phương án khác định nghĩa. Vì vậy
   mọi phương án so sánh trên `test_objective` nên chạy dưới dạng joint (mode `sequential`
   cho baseline). `test_mean_distance_m`/`test_mean_wait_s` vẫn so sánh được.
3. **Khoảng tổng quát hóa bị nhiễu bởi tải.** Fold kiểm tra ít đơn hơn tập huấn luyện nên
   tải T4 thấp hơn; `generalization_gap` chỉ dùng để so sánh giữa phương pháp trên cùng
   fold, không đọc như sai số tuyệt đối.
4. **exact/hybrid** cần `finite_space` khai báo riêng cho từng instance; instance sinh tự
   động chưa có nên X1 phải dùng instance `datasets/joint/*` hoặc bổ sung không gian.

## 8. Thứ tự thực hiện

Mục 7.1–7.5 → pilot 7.6 → X1 → X4 → X2 → X2b → X5 → X6 → X3 (chạy sau cùng,
một lần duy nhất) → phân tích → viết bài.

## 9. Kết quả pilot (2026-10-23)

Cấu hình `experiments/configs/pilot_cv.json`: `tiny_f6` (Tiny, `facings=6`) và
`small_f4` (Small, `facings=4`); 4 phương án đều chấm bằng cùng hàm mục tiêu joint:
`baseline` (sequential, greedy + first-fit), `seq_milp`, `multistart` (3 ứng viên),
`feedback`; 1 lượt × 10 fold = 80 job; 60 s/job; `budget_fraction` 0,25.

Campaign `experiments/results/20261023-pilot-cv-03`: **80/80 SUCCEEDED**, mọi đánh giá
trên tập thử COMPLETED, tổng 1.382 s. Kết quả theo bố cục deepmg nằm ở
`experiments/reports/20261023-pilot-cv-03/results/<prefix>/` (8/8 phương án `_file_sum_ok`).

| Instance | Phương án | `test_objective` TB | `test_mean_distance_m` TB | Wall TB / max (s) |
|---|---|---:|---:|---:|
| tiny_f6 | baseline / seq_milp / multistart | 0,0633 | 7,670 | 2,4–2,8 / 2,9 |
| tiny_f6 | feedback | 0,0497 | 5,774 | 16,8 / 18,2 |
| small_f4 | baseline / seq_milp / multistart | 0,1336 | 14,270 | 4,8–8,5 / 8,6 |
| small_f4 | feedback | 0,1281 | 13,498 | 49,2 / 49,7 |

**Lỗi đã sửa ngày 26/10/2026 — multistart trước đó không có hiệu lực.** Instance sinh tự động
có `layout_mode: "fixed"`, nên `variant` của T1 bị ép về 0 và 3 ứng viên joint multistart
giống hệt nhau (vì vậy pilot và paper-v2 có multistart = seq_milp trên 813/813 cặp). Từ bản
sửa, mỗi variant ≥ 1 là random walk có seed trên vị trí kệ, mỗi bước kiểm tra hình học
(`application/feedback/restarts.py`), sau đó T2/T3 tối ưu lại. Số liệu multistart cũ ở
dưới và trong paper-v2 không còn đại diện cho phương án này.

So feedback với baseline trên 10 fold (thăm dò, một lượt):

| Instance | Chỉ số | Chênh TB | Bootstrap CI95 trung vị | Wilcoxon p | Nadeau–Bengio p | Holm-NB | A12 |
|---|---|---:|---|---:|---:|---:|---:|
| tiny_f6 | test_objective | −0,0136 | [−0,0214; −0,0051] | 0,0098 | 0,019 | 0,153 | 0,15 |
| small_f4 | test_objective | −0,0055 | [−0,0071; −0,0035] | 0,0020 | 0,0013 | 0,014 | 0,33 |

Nhận xét dùng để chốt thiết kế:

- Ba phương án sequential cho **cùng một kế hoạch** trên cả hai instance; khác biệt
  chỉ đến từ feedback. Cần thêm instance (nhiều `seed` của DatasetSpec, nhiều mức
  `facings`) để kiểm tra điều này có còn đúng không.
- Friedman trên đơn vị fold: p = 2,3e-8, feedback khác 3 phương án còn lại theo Nemenyi.
  Ở mức trung bình dataset chỉ có 2 khối nên chưa kết luận được (p = 0,11), cần ≥ 5–10
  instance như X2b.
- Feedback trên Small dùng 49,7 s / 60 s, ngân sách gần chạm trần: X2 trên Small/Medium
  nên đặt `job_time_limit_s` ≥ 120.
- Ước tính thời gian cho 10 lượt × 10 fold × 4 phương án mỗi instance: Tiny ≈ 2.440 s
  (~41 phút), Small ≈ 6.730 s (~1,9 giờ). Số liệu chỉ tính trên máy này, chạy tuần tự
  một worker.
- Lượt chạy bị thay thế, vẫn giữ lại: `pilot-cv-01` (dừng ở 55/80 vì mã nguồn bị sửa
  trong lúc chạy, cơ chế chống drift hoạt động đúng); `pilot-cv-02` (3 job feedback lỗi
  EXECUTION_ERROR do lỗi SimPy/`EngineError`, đã sửa trước pilot-cv-03).

## 10. paper-v3 (2026-10-26): sửa thiết kế sau đánh giá paper-v2

Nguồn: đánh giá của chủ dự án `Ket_qua_thuc_nghiem_lan_1.docx` (8 vấn đề). paper-v3 thay
paper-v2 làm thiết kế chạy chính; kết quả paper-v2 chỉ còn là bằng chứng thăm dò và **không
gộp** với paper-v3 (khác mã nguồn và định nghĩa thực nghiệm). Cấu hình:
`experiments/configs/paper-v3/` (sinh bằng `scripts/build_paper_configs.py`), cách chạy:
[PAPER_EXPERIMENT_RUNBOOK.md](PAPER_EXPERIMENT_RUNBOOK.md).

| # | Vấn đề paper-v2 | Thay đổi paper-v3 |
|---|---|---|
| 1 | Không có baseline cùng ngân sách; multistart trùng seq_milp 813/813 cặp | Lỗi multistart: instance sinh tự động có `layout_mode: "fixed"` nên variant T1 bị ép về 0. Sửa bằng restart ngẫu nhiên có seed trên vị trí kệ (`application/feedback/restarts.py`). Thêm 2 mode joint: `random_search` (restart độc lập tới hết ngân sách) và `annealing` (cùng neighborhood với feedback nhưng chọn bước ngẫu nhiên đều, nhận bước xấu theo Metropolis, T0 = 1% điểm ban đầu, làm nguội hình học về 1% T0). So sánh feedback với annealing tách được giá trị của chẩn đoán T4 khỏi giá trị của việc tìm kiếm thêm |
| 2 | Feedback bị trần thời gian cắt, phụ thuộc tốc độ máy | Ngân sách = số lượt đánh giá (`max_evaluations`), bằng nhau giữa random_search/annealing/feedback trong cùng quy mô: Tiny 40, Small 30, Medium 16. Trần thời gian/job (300/600/900 s) chỉ là giới hạn an toàn. Kết quả có `joint.incumbent_curve` (lượt, giây, điểm mỗi lần cải thiện) và `joint_evaluations_to_best` |
| 3 | Ablation trái câu chuyện tích hợp; T1-only và combined đều chạm trần | X5 chạy lại trên 5 instance Small, 5 fold, mọi biến thể feedback cùng 30 lượt |
| 4 | T4 chỉ ở 2 chế độ cực đoan (ρ 0,11–0,37 hoặc ≈1) | Hiệu chỉnh tải theo quy mô (`application/experiments/calibration.py`): đo thời gian phục vụ picker ở tải nhẹ trên nghiệm tuần tự, chọn khoảng cách đơn Poisson cho ρ mục tiêu 0,75; đạt 0,751 / 0,752 / 0,777 (Tiny/Small/Medium, xem `calibration.json`). X6 thêm mức tải ρ≈0,5 và ≈0,9 |
| 5 | Tập kiểm tra quá nhỏ (2–10 đơn/fold) | Tiny 150, Small 300, Medium 500 đơn; 5 fold → 30/60/100 đơn mỗi fold kiểm tra. `EvaluationSpec.order_rate="population"` co giãn thời gian đặt đơn của mỗi fold về tốc độ đến của toàn bộ đơn, nên fold 1/5 không bị mô phỏng ở 1/5 tải |
| 6 | Tỷ lệ % gộp dễ hiểu nhầm; tên baseline không thống nhất | `instance_comparisons.csv`: đơn vị là instance, tham chiếu `seq_milp`, Wilcoxon chính xác, tách theo quy mô và gộp, Holm toàn bảng, có cột p nhỏ nhất có thể. Id `seq_milp` dùng thống nhất ở mọi khối; X2 có 10 instance mỗi quy mô (p tối thiểu 0,002) |
| 7 | X1 chỉ 1 fixture, không có seq_milp | X1 hai pha trên 10 instance Tiny sinh tự động (thí nghiệm E41, 2 seed). Pha 1: seq_milp, random_search, annealing, feedback. Pha 2 (khối X1b, `scripts/build_x1_union_configs.py`, runner tự gọi): mỗi instance một miền hữu hạn **dạng gói** = các layout khác nhau × các allocation (phân bổ + xếp SKU) khác nhau × các chính sách đi lại lấy từ mọi nghiệm pha 1 (`FiniteSpace.layouts`/`allocations`, `application/experiments/finite_spaces.py`); exact duyệt hết và có chứng chỉ. Mọi nghiệm heuristic thuộc miền nên khoảng cách heuristic − exact ≥ 0; `instance_comparisons.csv` có thêm tham chiếu `exact` |
| 8 | Lệch so với thiết kế | X6 chạy trên Small. Large chỉ chạy phương án tuần tự với tải chưa hiệu chỉnh và được tuyên bố **ngoài phạm vi** kết luận về feedback. Medium dùng holdout thời gian (4 instance) vì 5 fold × 16 lượt × 39 s/lượt vượt ngân sách tính toán |

Quyết định cần chủ dự án xác nhận trước khi chạy:

- Feedback trong paper-v3 dùng `policy="first_improvement"` (paper-v2: `best_improvement`).
  Với ngân sách 16–40 lượt, một vòng best-improvement 24 hành động gần như dùng hết ngân sách
  cho một bước. Nếu muốn giữ định nghĩa cũ, đổi tham số này trong `arms()` của script và sinh lại.
- Mục tiêu ρ = 0,75 và các ngân sách theo quy mô là lựa chọn thiết kế, ghi trong script.

Giới hạn còn lại (phải ghi trong bài):

- Exact ở X1 chỉ tối ưu trong **miền hợp các nghiệm heuristic** đã khai báo, không phải tối ưu
  toàn cục. Cận dưới toàn cục (phương án B) đã được xem xét: vị trí kệ chỉ bị ràng buộc cách lối
  vào 0,5 m nên cận hợp lệ cho quãng đường chỉ khoảng 1–2 m/hành trình so với 7–14 m thực tế,
  tức cận khoảng cách ≥ 75–90%, không đủ thông tin để đưa vào bài.
- Hiệu chỉnh tải dựa trên nghiệm tuần tự của một instance tham chiếu mỗi quy mô; ρ thực tế của
  từng job nằm trong `picker_utilization`.
- Toàn bộ dữ liệu vẫn là SYNTHETIC.

Ước tính chạy (đo 26/10, một worker): Tiny ~1 s/lượt, Small ~6 s/lượt, Medium ~39 s/lượt;
tổng 1.416 job (+20 job X1b) khoảng 28 giờ.

## 11. paper-v4 (2026-10-28): cải tiến sau kết quả paper-v3

Nguồn: `Ket_qua_thuc_nghiem_lan_2.docx` (kết quả paper-v3) và đối chiếu với mã nguồn.
Chưa chạy thực nghiệm nào với paper-v4.

### 11.1. Chẩn đoán từ mã nguồn

- Random search dùng `restarts.restart()`: đi ngẫu nhiên tối đa N thay đổi T1 (N = số kệ
  di chuyển được), mỗi lần dịch tới ±3 ô lưới hoặc hoán đổi, **lọc trước bằng `violations()`**,
  T2/T3 giải lại bằng MILP. Feedback paper-v3 chỉ dịch một kệ ±1 ô, không lọc trước. So sánh
  feedback–random search vì vậy trộn cỡ bước, lọc trước và dẫn hướng. Annealing dùng đúng lân cận
  của feedback nhưng chọn đều: feedback −8,3% so với annealing −4,65% (E18) là bằng chứng sạch về
  giá trị tín hiệu T4.
- T4 chỉ dùng `shelf_id:face` của SKU; tầng kệ, vị trí x, hướng và số mặt chỉ tác động qua
  thành phần thiếu hụt sức chứa. Kết quả 0/1.701 nước T3 cải thiện là hệ quả cấu trúc mô hình.
- Nước trùng lặp bị loại trước `assess()` nên không tốn ngân sách; chỉ khoảng 30% nước FAILED
  tốn ngân sách.
- `local_trap` có kệ duy nhất `locked: true`, nên multistart (chỉ đổi pose T1) luôn
  `RESTART_UNAVAILABLE` theo thiết kế.
- Mặc định `patience=1`, `max_actions=24` chia vòng tròn T1/T2/T3: mỗi vòng quét chỉ khoảng 8 nước T1.

### 11.2. Tùy chọn mới của `JointConfig` (vắng mặt = hành vi paper-v3, không ghi vào dạng chuẩn)

| Trường | Ý nghĩa | Mặc định khi vắng |
|---|---|---|
| `t1_steps` | độ dài bước T1 theo số ô lưới | `[1]` |
| `geometry_prefilter` | bỏ nước T1 vi phạm biên/lối vào/lối đi trước khi đánh giá | tắt |
| `t3_scope: "objective"` | chỉ giữ T3_FACE, hoán đổi khác mặt, tăng facings khi thiếu sức chứa | `"all"` |
| `layer_allocation: "adaptive"` | chia danh sách nước theo tỷ lệ thành công làm trơn (a+1)/(n+2) | vòng tròn |
| `kicks`, `kick_edits` | ILS: khi hội tụ cục bộ, đá bằng `kick_edits` thay đổi T1 hợp lệ từ lời giải tốt nhất | 0 / 3 |
| `restart_max_step` | bước tối đa của random walk (random_search, multistart, kick) | 3 |
| `search_time_s` | so sánh cùng thời gian: hết số giây này thì không bắt đầu lượt đánh giá mới (`SEARCH_TIME_LIMIT`) | không giới hạn riêng |
| `screen_seeds`, `screen_margin` | sàng lọc hai mức: chạy trước `screen_seeds` kịch bản, chỉ đánh giá đủ khi điểm ≤ (1 + margin) × điểm của plan tham chiếu; ngân sách tính theo lượt đánh giá đầy đủ quy đổi | tắt |

Trần mỗi job nâng từ 900 s lên 3.600 s (contract, CLI, frontend). Lease worker 30 s được gia hạn
liên tục khi job chạy, nên job dài không mất lease; trần campaign vẫn 14.400 s, nên part có
trần 3.600 s chứa 5 job.

Không cải tiến multistart trên `local_trap`: kick và restart chỉ thay đổi T1, nên vẫn
`RESTART_UNAVAILABLE` trên instance có kệ khóa. Đây là giới hạn đã khai báo.

### 11.3. Thiết kế paper-v4 (`scripts/build_paper_v4_configs.py`)

Instance mới (seed 7001–7510), chưa dùng để chỉnh thuật toán; tải dùng lại
`paper-v3/calibration.json`. `feedback_v4` = feedback paper-v3 + `t1_steps [1,2,3]`,
`geometry_prefilter`, `t3_scope objective`, `layer_allocation adaptive`, `kicks 10`,
`kick_edits 3`, `patience 2`.

| Khối | Mã | Instance | Giao thức | Phương án | Job |
|---|---|---|---|---|---:|
| V2 | E52 | small ×10 (7301–7310) | 5 fold | seq_milp, random_step1, random_step3, guided_step1, guided_step3 | 250 |
| V4 | E54 | small ×10 (7501–7510) | holdout | seq_milp, feedback_v4, bỏ lần lượt steps/prefilter/t3_scope/adaptive/kicks | 70 |
| V3 | E53 | small ×10 (7401–7410) | holdout | seq_milp, random_search và feedback_v4 với ngân sách 16/30/40/80 | 90 |
| V1 | E51 | tiny ×10 (2 lượt), small ×10, medium ×10 | 5 fold (medium holdout) | seq_milp, random_search, annealing, feedback, feedback_v4 | 800 |

| VL | E55 | large ×3 (7601–7603, tải mặc định chưa hiệu chỉnh) | holdout | seq_milp, random_search, feedback_v4; cùng thời gian tìm kiếm 3.000 s, trần 3.600 s | 9 |
| V5 | E56 | medium ×10 (7701–7710) | holdout | seq_milp, random_search(±screen), feedback_v4(±screen); `screen_seeds 1`, `screen_margin 0,02` | 50 |

Medium dùng ngân sách 40 như tiny (trần 3.600 s/job), nên V1 có cùng ngân sách ở mọi quy mô.
Tổng 1.269 job, thứ tự V2 → V4 → V3 → V1 → VL → V5. Ước tính thô (chi phí đo 26/10): khoảng
80 giờ một worker (V1 medium ~17 h, V5 ~17 h, VL ~6 h). Giới hạn còn lại: số lượt đánh giá của
large chưa đo (VL so sánh theo thời gian nên không cần số này); large chỉ có 3 instance và tải
chưa hiệu chỉnh; margin sàng lọc 2% là giả định khai báo, chưa hiệu chỉnh.
Họ kiểm định chính cho Holm: các chỉ số mục tiêu (`test_objective`; `joint_objective` khi không có
tập thử tách riêng); chỉ số phụ báo cáo riêng.

## 12. paper-v5 (2026-11-03): surrogate hiệu chỉnh bằng phản hồi T4, GA, nhiều seed

Nguồn: phân tích kết quả paper-v4 (mục đầu HANDOFF.md, 2026-11-03). Chủ dự án chọn hướng B
(surrogate), thêm GA làm baseline, ngân sách chạy 3–5 ngày, chỉ sửa mã và kiểm thử, **không
chạy thực nghiệm**. Mục tiêu bài báo Q2–Q3.

### 12.1. Chẩn đoán từ kết quả paper-v4 và mã nguồn

- random_search thắng feedback_v4 ở 30/30 instance (tiny −25,9%, small −12,6%, medium −10,0% so
  với seq_milp; feedback_v4 −21,5/−4,7/−2,2%), nhưng mọi instance cùng quy mô có cùng hình học
  và mọi job dùng seed tìm kiếm 1 (tiny thêm seed 2): cùng một chuỗi ứng viên lặp lại, small chọn
  ứng viên #8 ở 50/50 job. Đây là một lần bốc ngẫu nhiên, không phải độ tin cậy của phương pháp.
- `seq_milp` không tối ưu T1 (`layout_mode: fixed` giữ lưới của bộ sinh); mọi cải thiện đến từ
  sắp xếp lại kệ. T3 không có nước nào được chấp nhận.
- Lân cận feedback xếp theo kệ nóng rồi cắt ở `max_actions` = 24: với 12 kệ có 156 nước dời
  (4 hướng × 3 bước + xoay) đứng trước 66 nước hoán đổi, nên mỗi vòng chỉ dời 1–2 kệ nóng nhất
  0,5 m; layout tốt nhất của random_search xoay 3 kệ và hoán đổi nhiều kệ cùng lúc.
- Nước đi sai topology vẫn tốn một lượt đánh giá (`assess` cộng ngân sách trước khi giải).
- T2 phân lại nhóm hàng sau mỗi thay đổi T1 theo khoảng cách chim bay có trọng số nhu cầu;
  T4 tính quãng đường trên lưới đi bộ. Dựng lưới đo được: 23/44/120/307 ms cho tiny/small/
  medium/large, so với khoảng 1/6/30 s một lượt mô phỏng.
- Báo cáo không truyền `scales` vào `instance_comparisons` (mọi dòng `unknown`).

### 12.2. Surrogate `walk_heat` (`application/feedback/surrogate.py`)

Với một layout ứng viên: dựng lưới bằng `engines.navigation` (layout không liên thông hoặc có
kệ không lấy hàng được bị loại, không tốn ngân sách); quãng đường ngắn nhất d_s từ lối vào tới
điểm lấy hàng của từng kệ; độ nóng h_c của nhóm hàng c = số đơn vị lấy trong lần mô phỏng gần
nhất của plan hiện tại + 1. Ghép nhóm nóng nhất với kệ gần nhất, mỗi nhóm một kệ
(bất đẳng thức sắp xếp lại): surrogate = Σ h_(i) × d_(i) với h giảm dần, d tăng dần; nhóm có
`fixed_shelf_id` dùng d của kệ cố định, khi số nhóm vượt số kệ thì danh sách kệ được lặp lại. `walk` dùng
h_c = 1 (ablation "bỏ độ nóng"). Đơn vị mét × đơn vị hàng; chỉ dùng để xếp hạng.

Giả định khai báo: bỏ qua hàng đợi, đường đi nối nhiều kệ trong một đơn, sức chứa T2 và ràng
buộc gần/xa; giả định T2 xếp lý tưởng. Mọi chấp nhận và mọi kết luận dựa trên mô phỏng.
Nới lỏng: nhóm không cố định được ghép với toàn bộ danh sách kệ, kể cả kệ đã dành cho nhóm cố
định, nên với instance có gán cố định surrogate hơi lạc quan (paper-v5 không có instance như vậy).

### 12.3. `feedback_v5` = feedback_v4 + các tùy chọn mới

Tùy chọn mới của `JointConfig` (vắng mặt = hành vi paper-v4, không ghi vào dạng chuẩn):

| Trường | Ý nghĩa | Mặc định khi vắng |
|---|---|---|
| `surrogate` | `walk_heat` hoặc `walk`: xếp hạng ứng viên T1 bằng surrogate | tắt |
| `surrogate_pool` | số ứng viên T1 lấy mẫu đều mỗi vòng (mọi kệ: dời theo `t1_steps`, xoay, hoán đổi) trước khi xếp hạng | tắt; khi bật surrogate: 96 |
| `compound_moves` | số bước đi ngẫu nhiên dời 2..N kệ cùng lúc (từ plan hiện tại) thêm vào tập | 0 |
| `restart_samples`, `restart_evaluations` | pha khởi động: sinh `restart_samples` bước đi ngẫu nhiên từ plan ban đầu (như random_search), xếp hạng bằng surrogate (không có surrogate: giữ thứ tự sinh), mô phỏng `restart_evaluations` ứng viên đầu, hạ dốc từ ứng viên tốt nhất | tắt |
| `search_seed_scope` | `instance`: seed tìm kiếm = hàm băm (nội dung instance, seed job); áp dụng cho random_search, annealing, genetic, khởi động, kick và lấy mẫu tập ứng viên | `job` (seed job) |
| `drop_identical_swaps` | `true`: bỏ nước hoán đổi T1 giữa hai kệ giống hệt nhau về vật lý (mọi trường trừ `id`, `x`, `y`, `rotation`, `locked`) khi không nhóm hàng nào cố định (`fixed_shelf_id`) vào một trong hai kệ; trong tập ứng viên có pool còn bỏ bước đi phức hợp chỉ hoán vị các kệ giống nhau của plan hiện tại. Nước như vậy chỉ đổi nhãn kệ: điểm không đổi nhưng tốn một lượt đánh giá (khoảng 29% tập ứng viên small; khoảng 50% nước của annealing ở small, ≥ 78% ở medium) | tắt |

Khi bật `surrogate_pool` mà tắt surrogate (ablation "bỏ surrogate"), tập ứng viên được xáo
trộn có seed rồi cắt ở `max_actions`. T2 vẫn xen kẽ theo `layer_allocation`, quy tắc chấp nhận
(giảm chặt trên mô phỏng), `policy`, `patience`, kick như paper-v4. Thời gian dựng lưới cho
surrogate tính vào wall time của job (đo khi cài đặt: một vòng `actions()` có pool khoảng 6 s ở
small, 22 s ở medium; sinh 128 bước đi khởi động khoảng 12,5 s mỗi job medium, xếp hạng chúng
khoảng 17 s ở medium). Khi đã hết ngân sách, vòng có pool không được tính nữa; việc sinh bước đi
khởi động dừng ở hạn thời gian tìm kiếm.

### 12.4. Baseline `genetic`

Mode mới `genetic`, cùng ngân sách số lượt đánh giá. Mã hóa: tọa độ và góc của mọi kệ (T2/T3 giải
lại khi đánh giá). Quần thể ban đầu: plan ban đầu + (`population` − 1) bước đi ngẫu nhiên như
random_search. Trạng thái ổn định: chọn cha mẹ giải đấu 2; lai đều theo kệ (mỗi kệ lấy tọa độ của
cha hoặc mẹ); con vi phạm hình học được thử lại tối đa 50 lần rồi chỉ đột biến; đột biến bằng
bước đi ngẫu nhiên `mutation_edits` kệ; con trùng không tốn ngân sách; con thay cá thể kém nhất nếu
tốt hơn. Trường mới: `population` (mặc định 8), `mutation_edits` (mặc định 2).

### 12.5. Bộ sinh: `DatasetSpec.layout_family`

Vắng mặt = lưới hiện tại (dạng chuẩn và hash không đổi). `corner_entrance`: lối vào ở
(0; 1,0) gần góc tây nam. `wide`: số cột = ⌈1,5·√n⌉, mặt bằng rộng và nông hơn. `columns`: kệ
xoay 90°, bước 2,5 m theo x và 3 m theo y. Mọi dạng được kiểm tra hình học/topology bằng test.
Tải dùng lại `paper-v3/calibration.json` theo quy mô (không mô phỏng khi sinh cấu hình); ρ thực tế
lệch theo dạng mặt bằng là giới hạn khai báo, `picker_utilization` có trong từng job.

### 12.6. Thiết kế paper-v5 (`scripts/build_paper_v5_configs.py`, chưa chạy)

Holdout thời gian 80/20, `search_seed_scope: instance` cho mọi phương án ngẫu nhiên, instance mới
(seed 8001+), 4 dạng mặt bằng (lưới, corner_entrance, wide, columns).

| Khối | Mã | Instance | Seed tìm kiếm | Phương án | Job |
|---|---|---|---|---|---:|
| W1 | E61 | tiny 4 dạng × 3 | 1–5 | seq_milp, random_search, annealing, genetic, feedback_v4, feedback_v5 | 360 |
| W1 | E61 | small 4 dạng × 3 | 1–5 | như trên | 360 |
| W1 | E61 | medium 4 dạng × 2 | 1–3 | như trên | 144 |
| W2 | E62 | small 4 dạng × 2 | 1–3 | seq_milp, feedback_v5, v5_no_surrogate, v5_no_compound, v5_no_restart, v5_no_heat | 144 |

Ngân sách như paper-v4 (tiny 40, small 30, medium 40). feedback_v5 trên mỗi quy mô:
`surrogate walk_heat`, `surrogate_pool 96`, `compound_moves 32`, `restart_samples 128`,
`restart_evaluations` = 25% ngân sách (tiny 10, small 8, medium 10), `drop_identical_swaps
true`; mọi phương án ablation `v5_no_*` giữ `drop_identical_swaps`. Phương án `annealing` có
thêm `drop_identical_swaps true` và `t3_scope objective` (khai báo: annealing khác định nghĩa
paper-v4, là baseline mạnh hơn, chỉ dùng nước có thể đổi điểm; nước đổi nhãn kệ và nước T3
level/position không đổi điểm từng chiếm phần lớn ngân sách của nó). `feedback_v4`,
`random_search`, `genetic` giữ định nghĩa trước. Ước tính thời gian job
khoảng 70 giờ (tiny 5, small 19, medium 38, W2 8), từ chi phí đo trong paper-v4 cộng chi phí
surrogate; chưa có pilot paper-v5 nên các phần medium của W1 đứng đầu chỉ mục (medium → small →
tiny; khối W2 vẫn chạy trước W1) để thời gian job medium lộ ra sớm. Bỏ large, sàng lọc và lưới
ngân sách (đã có ở paper-v4).

### 12.7. Phân tích

`reports.report` lấy quy mô từ manifest dataset và truyền vào `instance_comparisons` (bảng theo
quy mô và gộp). Khi có `random_search`, nó là tham chiếu thứ hai (như `exact`), để kiểm định trực
tiếp feedback_v5 so với random_search (không lặp lại cặp đối xứng random_search → seq_milp).
Khi có phương án ablation `v5_no_*` (W2), `feedback_v5` cũng là tham chiếu, để so trực tiếp
phương án đầy đủ với từng phương án bỏ một thành phần (cũng không có dòng đối xứng). Đơn
vị suy luận vẫn là instance (trung bình qua seed tìm kiếm). Họ chính khai báo trước
(`holm_primary_wilcoxon_exact_p`) chỉ gồm các chỉ số mục tiêu (`test_objective`; `joint_objective`
khi không có tập thử tách riêng) trên nhóm gộp `all` (hoặc nhóm quy mô duy nhất khi khối chỉ có
một quy mô); mỗi quy mô có cột Holm riêng
(`holm_scale_wilcoxon_exact_p`, suy luận phụ); cột Holm toàn bảng giữ để đối chiếu. Mọi kiểm
định vẫn là thăm dò (`descriptive_paired_exploratory`), không phải khẳng định hiệu quả trên tổng
thể; "họ chính" chỉ là họ được khai báo trước khi chạy. Lý do chọn họ này: gộp mọi dòng theo quy
mô vào một họ (~45 dòng) khiến quy mô 8 instance (p nhỏ nhất 0,0078) không bao giờ đạt 0,05. W2
(8 instance, một quy mô) có 5 dòng `test_objective` so với seq_milp + 4 dòng feedback_v5 so với
`v5_no_*` = 9 dòng trong họ chính: p nhỏ nhất sau hiệu chỉnh 0,0078 × 9 ≈ 0,070 > 0,05, nên W2
không thể đạt 0,05 và chỉ được báo cáo ở dạng mô tả (độ lớn hiệu ứng, số instance thắng/hòa).
Không viết "tối ưu toàn cục" hay "kiểm chứng thực tế"; surrogate thất bại xếp hạng không phải
bằng chứng vô nghiệm.
