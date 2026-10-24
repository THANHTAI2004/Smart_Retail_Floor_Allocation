# Hướng dẫn chạy thực nghiệm bài báo (hướng A)

Cập nhật: 2026-10-23. Tài liệu này dành cho người chạy tiếp thực nghiệm. Thiết kế và lý do
nằm ở [EXPERIMENT_DESIGN_DEEPMG.md](EXPERIMENT_DESIGN_DEEPMG.md); trạng thái mới nhất ở
mục đầu [HANDOFF.md](../../HANDOFF.md).

## 0. Tình trạng khi bàn giao

**Mốc mới 23/10/2026, 13:35 UTC+7:** người dùng đã yêu cầu chạy tiếp. Lượt chính
đã khởi động tại checkout hiện tại; xem mục đầu HANDOFF và
[biên bản tiếp tục](CONTINUATION_20261023.md). Dữ liệu thô của 18 job trong bảng
lịch sử dưới đây không có trên máy này, nên lượt hiện tại chạy từ đầu vào thư mục
paper-v2 còn trống. Không khởi động thêm runner khi tiến trình hiện tại còn sống.
Kiểm chứng mới sau sửa báo cáo gộp: **198 pytest, 4 Vitest, lint/build frontend,
Ruff/mypy/architecture đều đạt**. Bảng dưới là trạng thái trước mốc chạy lại.

| Hạng mục | Trạng thái |
|---|---|
| Code (k-fold, đánh giá trên tập thử, thống kê, xuất kết quả kiểu deepmg, ân hạn worker, trần 900 s) | Xong, **chưa commit** |
| Kiểm thử | 197 pytest pass; ruff, mypy, kiểm tra kiến trúc PASS. Frontend (ESLint/build/Vitest) **chưa chạy** vì thiếu `frontend/node_modules` |
| Pilot | `experiments/results/20261023-pilot-cv-03`: 80/80 thành công; báo cáo ở `experiments/reports/20261023-pilot-cv-03` |
| Cấu hình bài báo | **Đã sinh**: `experiments/configs/paper-v2/` (20 file + `index.json`, 4.276 job) |
| Chạy chính | **Chưa chạy.** `experiments/results/20261023-paper-v2/paper-x1-exact` dừng có chủ đích ở 18/150 job; có thể chạy tiếp từ đó |
| Lượt bị thay thế, giữ lại để đối chiếu | `experiments/results/20261023-paper/` (v1: feedback medium bị dừng do ân hạn 2 s), `pilot-cv-01`, `pilot-cv-02` |

## 1. Chuẩn bị môi trường (một lần mỗi máy)

Chạy mọi lệnh từ thư mục gốc repo, PowerShell trên Windows.

```powershell
# Python 3.12
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r backend\requirements-lock.txt
.\.venv\Scripts\python.exe -m pip install -e backend --no-deps
# MongoDB cục bộ (tải bản 8.0.16 chính thức, kiểm SHA-256, chỉ nghe 127.0.0.1)
powershell -ExecutionPolicy Bypass -File scripts\start_mongodb.ps1 -InstallPortable
```

Nếu máy đã có `.venv` và `var/tools/mongodb-8.0.16`, chỉ cần khởi động MongoDB:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_mongodb.ps1
```

Kiểm tra nhanh trước khi chạy dài (khoảng 2 phút):

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var\pytest-<tên-mới>
```

Kỳ vọng: `197 passed`. Nếu số test khác, mã nguồn đã thay đổi so với lúc bàn giao; xem mục 6.

## 2. Sinh lại cấu hình (chỉ khi cần)

Cấu hình đã có ở `experiments/configs/paper-v2/`. Chỉ sinh lại khi đổi thiết kế. Script từ chối
ghi đè thư mục có sẵn, nên phải đổi `OUT` trong `scripts/build_paper_configs.py` sang thư mục
mới (ví dụ `paper-v3`) và đổi `CONFIGS`, `RESULTS`, `REPORTS` trong `scripts/run_paper_campaigns.py`
cho khớp.

```powershell
.\.venv\Scripts\python.exe scripts\build_paper_configs.py
```

Nội dung `paper-v2` (thứ tự chạy X1 → X4 → X2 → X2b → X5 → X6 → X3):

| Khối | Mã | Instance | Giao thức | Phương án | Job | Ngân sách/job |
|---|---|---|---|---|---:|---:|
| X1 | E17 | `local_trap` (có không gian hữu hạn) | 30 seed, không CV | baseline, multistart, feedback, exact, hybrid | 150 | 60 s |
| X4 | E21 | tiny/small/medium ×3, large ×1 | không CV | 4 phương án (large: 2) | 184 | 60 s / 900 s |
| X2 | E18 | tiny_f6 ×3, small_f4 ×3 | tiny 10 lượt × 10 fold; small 5 × 10 | baseline, seq_milp, multistart, feedback | 1.800 | 60 s |
| X2b | E19 | tiny ×10, small ×10, medium ×3 | 5×2cv (medium 3×2) | 4 phương án | 872 | 60 s / 900 s |
| X5 | E22 | small_f4 ×3 | 5×2cv | ablation feedback theo tầng | 150 | 60 s |
| X6 | E23–E34 | tiny_f6 ×3 | 5×2cv | baseline (= seq_milp) và feedback ở 3 mức × 4 yếu tố | 720 | 60 s |
| X3 | E20 | instance khóa (seed 9001+, 9101+) | holdout thời gian 80/20, 10 seed | 4 phương án | 400 | 60 s |

## 3. Chạy

```powershell
$p = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-u","scripts\run_paper_campaigns.py" -WorkingDirectory (Get-Location) -RedirectStandardOutput "var\paper-v2-run.log" -RedirectStandardError "var\paper-v2-run.err.log" -WindowStyle Hidden -PassThru
@{pid=$p.Id; started=(Get-Date).ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content var\paper-v2-run.pid.json -Encoding utf8
```

- Tiến trình chạy độc lập, có thể đóng cửa sổ. Thời gian ước tính **khoảng 27 giờ** chạy tuần tự
  trên máy 16 GB RAM (ước lượng từ pilot; medium feedback có thể dùng gần trọn 900 s/job).
- Lệnh trên **tự chạy tiếp**: campaign đã `COMPLETED` được bỏ qua, campaign dở dang được resume,
  job đã có kết quả không chạy lại.
- Nếu resume báo `Unresolved worker lease; wait for expiry` hoặc `Worker lease is still live`,
  job trước đó bị dừng giữa chừng: chờ khoảng 6 phút rồi chạy lại lệnh.
- Muốn dừng: dừng tiến trình có pid trong `var/paper-v2-run.pid.json` và các tiến trình python
  con của nó; sau đó chạy lại lệnh ở trên để tiếp tục.

**Trong lúc chạy tuyệt đối không sửa file `.py` trong `backend/src`.** Campaign so danh tính mã
nguồn trước mỗi job và sẽ dừng với `Source/dependency drift during campaign` (đã xảy ra ở
`pilot-cv-01`). Sửa tài liệu, cấu hình hoặc script trong `scripts/` thì không sao.

## 4. Theo dõi

```powershell
Get-Content var\paper-v2-run.log -Tail 20              # job vừa xong và campaign đang chạy
Get-Content experiments\results\20261023-paper-v2\journal.json   # trạng thái từng campaign
Get-ChildItem experiments\results\20261023-paper-v2 -Directory | ForEach-Object {
  $c = Get-Content "$($_.FullName)\checkpoint.json" -Raw | ConvertFrom-Json
  "$($_.Name): $($c.completed)/$($c.planned) $($c.status)" }
```

Ý nghĩa trạng thái job: `SUCCEEDED`; `FAILED` kèm `error.code`; `TIMED_OUT` (worker dừng tiến
trình con sau `ngân sách + max(15 s, 10%)`); `RESOURCE_LIMIT` (vượt 2.048 MB). Tất cả đều được
giữ lại trong kết quả, không phải lỗi của đợt chạy. `NOT_EXECUTED_BUDGET` ở cột
`evaluation_status` nghĩa là tối ưu xong nhưng không còn thời gian đánh giá trên tập thử.

Trạng thái campaign `NOT_EXECUTED_RESOURCE_LIMIT` nghĩa là chạm trần 4 giờ/campaign: ghi lại,
không resume được với cùng cấu hình; cần tách nhỏ hơn và chạy campaign mới.

## 5. Sau khi chạy xong

1. **Kiểm tra toàn vẹn** từng campaign:
   ```powershell
   Get-ChildItem experiments\results\20261023-paper-v2 -Directory | ForEach-Object {
     .\.venv\Scripts\python.exe -m smart_retail.application.experiments.cli verify $_.FullName }
   ```
   Mọi dòng phải là `'status': 'PASS'`.
2. **Báo cáo** được runner tự tạo ở `experiments/reports/20261023-paper-v2/<khối>/` (gộp các phần
   cùng khối). Nếu một khối báo `REPORT_ERROR` trong `journal.json`, chạy tay vào thư mục mới:
   ```powershell
   .\.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze <campaign-1> <campaign-2> --output experiments\reports\<thư-mục-mới>
   ```
3. **Đọc kết quả** trong mỗi báo cáo:
   - `results/<phương-án>/*_file_sum_ok.txt`: tham số, từng fold, tổng kết (bố cục deepmg; thiếu
     `_ok` nghĩa là phương án chưa đủ job).
   - `*_file_eachfold.txt`, `*_file_mean_test_objective.txt`, `*_file_mean_test_distance.txt`,
     `*_config.json` (chạy lại đúng phương án đó).
   - `statistics.json` / `comparisons.csv`: so với `baseline`. Với dữ liệu k-fold dùng
     `nadeau_bengio_p` và `holm_nadeau_bengio_p`, không dùng `exploratory_p`; kèm `wilcoxon_p`,
     `a12_treatment_greater`, `median_difference_bootstrap_ci95`.
   - `rankings.csv`: Friedman/Nemenyi; mức `dataset_means` là mức suy luận, `units` chỉ thăm dò.
   - `status_matrix.csv`: số job theo trạng thái (đưa vào bài như bảng trạng thái).
4. **Ghi HANDOFF.md**: lệnh đã chạy, thời gian, số job thành công/thất bại theo khối, giới hạn.
5. **Viết bài** (gợi ý bảng/hình ở mục 6 của EXPERIMENT_DESIGN_DEEPMG.md). Không viết "tối ưu
   toàn cục" ngoài các phương án `exact`/`hybrid` có `GLOBAL_OPTIMAL_CERTIFIED` trên không gian
   hữu hạn đã khai báo; không viết "kiểm chứng thực tế" (dữ liệu SYNTHETIC).

## 6. Lưu ý đã biết

- `facings=1` làm instance suy biến (mọi phương án như nhau); cấu hình dùng tiny f=6, small f=4,
  medium f=3, large f=2. Medium/large với f=4 vô nghiệm (một nhóm hàng > 3,8 m/kệ).
- Mọi phương án so sánh trên `test_objective` phải cùng định nghĩa hàm mục tiêu (đều chạy dạng
  joint); phân tích tự bỏ kiểm định nếu khác (`objective_definition`).
- `generalization_gap` bị nhiễu bởi tải (fold thử ít đơn hơn), chỉ so giữa phương án trên cùng fold.
- Large: probe với trần 300 s không chạy xong T4; với 900 s chưa đo. X4-large chỉ 4 job để ghi
  nhận giới hạn.
- Nếu sửa mã nguồn giữa chừng (sửa lỗi), các campaign đã xong và chưa xong có danh tính khác nhau
  và **không gộp được** trong cùng báo cáo (`Campaigns differ in source/dependency identity`).
  Khi đó chạy lại toàn bộ vào thư mục kết quả mới (đổi `RESULTS`/`REPORTS` trong runner).
- Không commit/push khi chưa được chủ dự án cho phép (AGENTS.md). `experiments/results/*/`
  bị `.gitignore` bỏ qua (dữ liệu thô vài GB); `experiments/reports/` thì không. Nên sao lưu
  `experiments/results/20261023-paper-v2` ra ngoài repo sau khi chạy xong.
> Cập nhật vận hành 2026-10-23 21:34 UTC+7: theo yêu cầu người dùng, giới hạn
> hiện tại là 3 campaign đồng thời, tự hạ và giữ ở mức 2 khi áp lực RAM/CPU
> kéo dài hoặc xuất hiện lỗi tài nguyên mới. X2 và X2b được chạy xen kẽ để
> dùng suất thứ ba; X3 vẫn chạy sau cùng. Suất thứ ba chạy từng job để có
> thể thu hồi sau job hiện tại mà không hủy nó. Xem `HANDOFF.md` và
> `var/paper-parallel/concurrency.json` cho ngưỡng, trạng thái và giới hạn.
> Các mô tả chạy 2 campaign bên dưới là lịch sử trước lần chuyển này.

> Cập nhật 2026-10-24: đã mở đợt chạy bù riêng cho các job chưa chạy do hết
> tổng thời gian campaign và các job lỗi. Đầu vào và thời gian từng job giữ nguyên;
> thời gian campaign bổ sung được ghi trong `var/paper-parallel/recovery/index.json`.
> X6 và phần chạy bù chạy trước X3. Kết quả gốc, kết quả chạy lại và các fold đi
> kèm được phân biệt rõ; không cộng lượt trùng vào tổng 4.276 job.

