# Hướng dẫn chạy thực nghiệm bài báo (hướng A)

Cập nhật: 2026-10-26 (paper-v3). Tài liệu này dành cho người chạy tiếp thực nghiệm. Thiết kế
và lý do nằm ở [EXPERIMENT_DESIGN_DEEPMG.md](EXPERIMENT_DESIGN_DEEPMG.md) (mục 10 cho
paper-v3); trạng thái mới nhất ở mục đầu [HANDOFF.md](../../HANDOFF.md).

## 0. Tình trạng khi bàn giao

| Hạng mục | Trạng thái |
|---|---|
| Code paper-v3 (multistart sửa lỗi, random_search, annealing, ngân sách theo lượt đánh giá, hiệu chỉnh tải, `order_rate`, X1 hai pha với exact trên miền hợp nghiệm heuristic, phân tích theo instance) | Xong, **chưa commit** |
| Kiểm thử | 207 pytest pass (có MongoDB cục bộ); ruff, mypy, kiểm tra kiến trúc PASS. Frontend (ESLint/build/Vitest) **chưa chạy** vì thiếu `frontend/node_modules` |
| Cấu hình bài báo | **Đã sinh**: `experiments/configs/paper-v3/` (`index.json`, `calibration.json`, 1.416 job + 20 job X1b dựng sau pha 1) |
| Chạy chính paper-v3 | **Chưa chạy** (chờ chủ dự án cho phép) |
| Lượt cũ, giữ lại để đối chiếu | paper-v2 (`experiments/configs/paper-v2/`, kết quả 4.276 job đã đánh giá trong `Ket_qua_thuc_nghiem_lan_1.docx`); số liệu multistart của paper-v2 không dùng được (lỗi đã sửa) |

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

Lần khởi động đầu, kiểm tra kết nối có thể báo lỗi vì `mongod` chưa sẵn sàng; chạy lại
`.\.venv\Scripts\python.exe -m smart_retail.infrastructure.mongodb.health` sau vài giây.

Kiểm tra nhanh trước khi chạy dài (khoảng 3 phút):

```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -q -p no:cacheprovider --basetemp var\pytest-<tên-mới>
```

Kỳ vọng: `207 passed`. Nếu số test khác, mã nguồn đã thay đổi so với lúc bàn giao; xem mục 6.

## 2. Sinh lại cấu hình (chỉ khi cần)

Cấu hình đã có ở `experiments/configs/paper-v3/`. Chỉ sinh lại khi đổi thiết kế. Script từ chối
ghi đè thư mục có sẵn, nên phải đổi `OUT` trong `scripts/build_paper_configs.py` sang thư mục
mới và đổi `CONFIGS`, `RESULTS`, `REPORTS` trong `scripts/run_paper_campaigns.py` cho khớp.
Khi sinh, script hiệu chỉnh tải cho từng quy mô (chạy pipeline tuần tự vài lần, khoảng 1 phút),
ghi bằng chứng vào `calibration.json`. Cấu hình X1b (pha 2) **không** sinh ở bước này: runner gọi
`scripts/build_x1_union_configs.py` sau khi X1 pha 1 COMPLETED, ghi `x1-union-spaces.json` và nối
khối `X1b` vào `index.json`. Có thể chạy tay script đó nếu runner báo `NOT_BUILT`.

```powershell
.\.venv\Scripts\python.exe scripts\build_paper_configs.py
```

Nội dung `paper-v3` (thứ tự chạy X1 → X1b → X4 → X2 → X5 → X6 → X3). Ngân sách tìm kiếm tính bằng
số lượt đánh giá (mỗi lượt = mô phỏng 2 kịch bản), bằng nhau giữa các phương án trong cùng quy mô:
Tiny 40, Small 30, Medium 16. Trần thời gian/job chỉ là giới hạn an toàn.

| Khối | Mã | Instance | Giao thức | Phương án | Job | Trần/job |
|---|---|---|---|---|---:|---:|
| X1 | E17 | `local_trap` | 30 seed, không CV | như paper-v2 (E13) | 150 | 60 s |
| X1 | E41 | tiny ×10 (seed 5001–5010) | 2 seed, không CV | pha 1: seq_milp, random_search, annealing, feedback | 80 | 300 s |
| X1b | E41 | cùng 10 instance | 2 seed | pha 2: exact trên miền hợp các nghiệm pha 1 (runner tự dựng cấu hình khi pha 1 COMPLETED) | 20 | 900 s |
| X4 | E21 | tiny/small/medium ×3; large ×1 (tải chưa hiệu chỉnh) | không CV | seq_milp, annealing, feedback (large: baseline, seq_milp) | 31 | 300/600/900 s |
| X2 | E18 | tiny ×10, small ×10 | 5 fold, `order_rate=population`; tiny 2 lượt, small 1 | baseline, seq_milp, random_search, annealing, feedback | 750 | 300/600 s |
| X2 | E19 | medium ×4 | holdout thời gian 80/20 | 5 phương án | 20 | 900 s |
| X5 | E22 | small ×5 | 5 fold | seq_milp, feedback T1/T2/T3/combined (cùng ngân sách) | 125 | 600 s |
| X6 | E23–E33 | small ×5 | holdout thời gian | seq_milp và feedback; picker 1/2/4, khách 15/30/60, trọng số chờ 0/0,2/1, tải ρ≈0,5/0,9 | 110 | 600 s |
| X3 | E20 | instance khóa (seed 9001+, 9101+) ×10 mỗi quy mô | holdout thời gian 80/20; tiny 2 lượt, small 1 | 5 phương án | 150 | 300/600 s |

## 3. Chạy

```powershell
$p = Start-Process -FilePath ".\.venv\Scripts\python.exe" -ArgumentList "-u","scripts\run_paper_campaigns.py" -WorkingDirectory (Get-Location) -RedirectStandardOutput "var\paper-v3-run.log" -RedirectStandardError "var\paper-v3-run.err.log" -WindowStyle Hidden -PassThru
@{pid=$p.Id; started=(Get-Date).ToUniversalTime().ToString('o')} | ConvertTo-Json | Set-Content var\paper-v3-run.pid.json -Encoding utf8
```

- Tiến trình chạy độc lập, có thể đóng cửa sổ. Ước tính **khoảng 29 giờ** chạy tuần tự, dựa trên
  phép đo ngày 26/10: một lượt đánh giá mất khoảng 1 s (Tiny, 150 đơn), 6 s (Small, 300 đơn),
  39 s (Medium, 500 đơn). Phần nặng nhất là X2-small (khoảng 8 giờ) và X5 (khoảng 5 giờ).
- Lệnh trên **tự chạy tiếp**: campaign đã `COMPLETED` được bỏ qua, campaign dở dang được resume,
  job đã có kết quả không chạy lại.
- Nếu resume báo `Unresolved worker lease; wait for expiry` hoặc `Worker lease is still live`,
  job trước đó bị dừng giữa chừng: chờ khoảng 6 phút rồi chạy lại lệnh.
- Muốn dừng: dừng tiến trình có pid trong `var/paper-v3-run.pid.json` và các tiến trình python
  con của nó; sau đó chạy lại lệnh ở trên để tiếp tục.

**Trong lúc chạy tuyệt đối không sửa file `.py` trong `backend/src`.** Campaign so danh tính mã
nguồn trước mỗi job và sẽ dừng với `Source/dependency drift during campaign` (đã xảy ra ở
`pilot-cv-01`). Sửa tài liệu, cấu hình hoặc script trong `scripts/` thì không sao.

## 4. Theo dõi

```powershell
Get-Content var\paper-v3-run.log -Tail 20              # job vừa xong và campaign đang chạy
Get-Content experiments\results\paper-v3\journal.json   # trạng thái từng campaign
Get-ChildItem experiments\results\paper-v3 -Directory | ForEach-Object {
  $c = Get-Content "$($_.FullName)\checkpoint.json" -Raw | ConvertFrom-Json
  "$($_.Name): $($c.completed)/$($c.planned) $($c.status)" }
```

Ý nghĩa trạng thái job: `SUCCEEDED`; `FAILED` kèm `error.code`; `TIMED_OUT` (worker dừng tiến
trình con sau `ngân sách + max(15 s, 10%)`); `RESOURCE_LIMIT` (vượt 2.048 MB). Tất cả đều được
giữ lại trong kết quả, không phải lỗi của đợt chạy. `NOT_EXECUTED_BUDGET` ở cột
`evaluation_status` nghĩa là tối ưu xong nhưng không còn thời gian đánh giá trên tập thử.

Với paper-v3, `joint_status` của các phương án tìm kiếm nên là `EVALUATION_LIMIT` (dùng hết ngân
sách) hoặc `CONVERGED_LOCAL` (feedback dừng ở cực tiểu cục bộ trước khi hết ngân sách). Nếu
nhiều job ra `TIMEOUT`, trần thời gian đang chi phối thay vì ngân sách đánh giá: ghi nhận và
báo lại, không gộp với các job khác như thể cùng ngân sách.

Trạng thái campaign `NOT_EXECUTED_RESOURCE_LIMIT` nghĩa là chạm trần 4 giờ/campaign: ghi lại,
không resume được với cùng cấu hình; cần tách nhỏ hơn và chạy campaign mới.

## 5. Sau khi chạy xong

1. **Kiểm tra toàn vẹn** từng campaign:
   ```powershell
   Get-ChildItem experiments\results\paper-v3 -Directory | ForEach-Object {
     .\.venv\Scripts\python.exe -m smart_retail.application.experiments.cli verify $_.FullName }
   ```
   Mọi dòng phải là `'status': 'PASS'`. Lưu kết quả này làm biên nhận xác minh trước khi chốt số liệu.
2. **Báo cáo** được runner tự tạo ở `experiments/reports/paper-v3/<khối>/` (gộp các phần cùng
   khối). Nếu một khối báo `REPORT_ERROR` trong `journal.json`, chạy tay vào thư mục mới:
   ```powershell
   .\.venv\Scripts\python.exe -m smart_retail.application.experiments.cli analyze <campaign-1> <campaign-2> --output experiments\reports\<thư-mục-mới>
   ```
3. **Đọc kết quả** trong mỗi báo cáo:
   - `instance_comparisons.csv`: **bảng suy luận chính**. Đơn vị là instance (trung bình các
     seed/fold dùng chung với tham chiếu), tham chiếu là `seq_milp`, Wilcoxon chính xác hai phía,
     tách theo quy mô (`scale`) và gộp (`all`), Holm trên toàn bảng. Cột `smallest_attainable_p`
     cho biết p nhỏ nhất có thể với số instance đó.
   - `results/<phương-án>/*_file_sum_ok.txt`: tham số, từng fold, tổng kết (bố cục deepmg; thiếu
     `_ok` nghĩa là phương án chưa đủ job).
   - `comparisons.csv`: so theo cặp (seed, fold) với `baseline`, chỉ để thăm dò; với dữ liệu k-fold
     dùng `nadeau_bengio_p`, không dùng `exploratory_p`.
   - `joint_evaluations` và `joint_evaluations_to_best`: kiểm tra các phương án tìm kiếm thật sự
     dùng cùng ngân sách; đường cong incumbent nằm trong `result.joint.incumbent_curve` của từng job.
   - `rankings.csv`: Friedman/Nemenyi; mức `dataset_means` là mức suy luận, `units` chỉ thăm dò.
   - `status_matrix.csv`: số job theo trạng thái (đưa vào bài như bảng trạng thái).
4. **Ghi HANDOFF.md**: lệnh đã chạy, thời gian, số job thành công/thất bại theo khối, giới hạn.
5. **Viết bài** (gợi ý bảng/hình ở mục 6 của EXPERIMENT_DESIGN_DEEPMG.md). Không viết "tối ưu
   toàn cục" ngoài các phương án `exact`/`hybrid` có `GLOBAL_OPTIMAL_CERTIFIED` trên miền hữu
   hạn đã khai báo; không viết "kiểm chứng thực tế" (dữ liệu SYNTHETIC).

## 6. Lưu ý đã biết

- `facings=1` làm instance suy biến (mọi phương án như nhau); cấu hình dùng tiny f=6, small f=4,
  medium f=3, large f=2. Medium/large với f=4 vô nghiệm (một nhóm hàng > 3,8 m/kệ).
- Mọi phương án so sánh trên `test_objective` phải cùng định nghĩa hàm mục tiêu (đều chạy dạng
  joint); phân tích tự bỏ kiểm định nếu khác (`objective_definition`).
- Tải được hiệu chỉnh trên **nghiệm tuần tự** của một instance tham chiếu mỗi quy mô (ρ ≈ 0,75).
  Nghiệm tối ưu hơn rút ngắn thời gian phục vụ nên ρ thực tế thấp hơn một chút; các instance khác
  cùng quy mô dùng chung khoảng cách giữa các đơn. `picker_utilization` có trong kết quả từng job.
- `order_rate=population` co giãn thời gian đặt đơn của mỗi fold về tốc độ đến của toàn bộ đơn;
  holdout thời gian không cần vì khối liên tiếp đã có tốc độ đó.
- X1 tiny: exact chỉ tối ưu trong miền hợp các nghiệm pha 1 (layout × allocation × chính sách).
  Khoảng cách heuristic − exact luôn ≥ 0; nếu exact tốt hơn mọi heuristic, nghĩa là ghép tầng của
  các nghiệm khác nhau có lợi. Không phải khoảng cách tới tối ưu toàn cục. Báo cáo X1 gộp cả
  campaign pha 1 và pha 2; trong `instance_comparisons.csv` dòng có `reference=exact` là khoảng cách.
- Large: tải chưa hiệu chỉnh (ρ ≈ 1), chỉ chạy phương án tuần tự để ghi nhận giới hạn mở rộng.
- Nếu sửa mã nguồn giữa chừng (sửa lỗi), các campaign đã xong và chưa xong có danh tính khác nhau
  và **không gộp được** trong cùng báo cáo (`Campaigns differ in source/dependency identity`).
  Khi đó chạy lại toàn bộ vào thư mục kết quả mới (đổi `RESULTS`/`REPORTS` trong runner).
- Không commit/push khi chưa được chủ dự án cho phép (AGENTS.md). `experiments/results/*/`
  bị `.gitignore` bỏ qua (dữ liệu thô vài GB); `experiments/reports/` thì không. Nên sao lưu
  `experiments/results/paper-v3` ra ngoài repo sau khi chạy xong.
