# Thiết kế thực nghiệm cho bài báo (hướng A, theo phương pháp deepmg)

Ngày: 2026-10-23. Trạng thái: **ĐÃ CÀI ĐẶT hạ tầng (mục 7.1–7.5)**, pilot 7.6 xem
mục 9. Các khối X1–X6 chưa chạy.

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
