# Thống kê thực nghiệm ngày 24/10/2026

Chốt số liệu lúc 13:49 UTC+7 từ bản ghi gốc và bản ghi chạy bổ sung. Đã thực hiện
đủ 4.276/4.276 job duy nhất. Tính theo lần chạy lại được yêu cầu khi có, có 4.228
job thành công (98,88%) và 48 job thất bại tìm cách xếp hàng (1,12%). Tất cả job
thành công trong bảng đều có kiểm tra độc lập PASS trong bản ghi.

Lượt tính toán cuối kết thúc lúc 13:04 ngày 24/10. Tại thời điểm chốt, bộ giám sát
đang VERIFYING; chưa có biên nhận hoàn tất kiểm tra toàn bộ hoặc sao lưu cuối.

## Tiến độ theo phần

| Phần | Số job | Thành công | Thất bại | Chưa chạy |
|---|---:|---:|---:|---:|
| X1 — Đúng đắn và exact | 150 | 150 | 0 | 0 |
| X2 — So sánh chính | 1.800 | 1.800 | 0 | 0 |
| X2b — Mở rộng instance | 872 | 834 | 38 | 0 |
| X3 — Holdout cuối cùng | 400 | 390 | 10 | 0 |
| X4 — Khả năng mở rộng | 184 | 184 | 0 | 0 |
| X5 — Ablation | 150 | 150 | 0 | 0 |
| X6 — Độ nhạy | 720 | 720 | 0 | 0 |
| **Tổng** | **4.276** | **4.228** | **48** | **0** |

## Chất lượng nghiệm

Điểm mục tiêu càng thấp càng tốt. Mỗi hàng dưới đây dùng các cặp cùng experiment,
dataset, seed, fold và repetition, chỉ khi cả baseline và feedback có nghiệm và
có điểm trên tập kiểm tra. Đây là tỷ lệ giảm của hai điểm trung bình ghép cặp,
không phải trung bình phần trăm từng job, cũng không phải kết quả kiểm định ý nghĩa.

| Phần | Số cặp | Baseline | Feedback | Giảm điểm mục tiêu |
|---|---:|---:|---:|---:|
| X2 | 450 | 0,088617 | 0,077145 | 12,94% |
| X2b | 180 | 0,161570 | 0,144342 | 10,66% |
| X3 holdout | 90 | 0,091466 | 0,078541 | 14,13% |
| X6 | 360 | 0,063885 | 0,045652 | 28,54% |

Feedback tốt hơn baseline trên 436/450 cặp X2, 180/180 cặp X2b,
88/90 cặp X3 và 359/360 cặp X6. Các cặp mà baseline thất bại không xuất hiện
trong bảng điểm; chúng vẫn nằm trong mẫu số tỷ lệ thành công.

Trong X2b, baseline thành công 180/218 job, còn seq_milp, multistart và feedback
đều thành công 218/218. Trong X3, baseline thành công 90/100, các phương pháp còn
lại đều thành công 100/100. Do đó không dùng trực tiếp trung bình trên 180 hay 90
job baseline để so với trung bình trên toàn bộ 218 hay 100 job của phương pháp khác.

X1 dùng một fixture tổng hợp và 30 seed mỗi phương pháp. Điểm joint trung bình:
baseline/multistart 0,152714; feedback 0,142714; exact/hybrid 0,102714. Exact/hybrid
giảm 32,74% so với baseline; 60/60 chứng chỉ tương ứng có kiểm tra PASS. Phạm vi
chứng chỉ là miền hữu hạn đã khai báo, không phải tối ưu toàn cục mọi mặt bằng.

X5 cho thấy T1-only giảm điểm tập kiểm tra 10,03% so với baseline, combined giảm
4,69%, T2-only tăng 0,13% và T3-only không thay đổi. Mẫu chỉ gồm 30 cặp trên ba
instance; kết quả chưa chứng minh nguyên nhân của thứ hạng này.

Trong X2, thời gian worker trung bình: baseline 3,27 giây; seq_milp 3,20 giây;
multistart 5,53 giây; feedback 32,85 giây. Feedback có chất lượng tốt hơn với chi
phí tính toán cao hơn. Đây không phải thời gian toàn campaign: kiểm tra, ghi dữ
liệu và checksum có thể chiếm thời gian lớn bên ngoài worker.

## Thất bại và chạy bù

48 thất bại ở lần chạy mới nhất đều là baseline T3 SLOTTING_FAILED: 38 ở X2b và
10 ở X3. First-fit không tìm được cách xếp thỏa kích thước, facings và tải trọng;
điều này không chứng minh bài toán vô nghiệm. Không có lỗi RAM/CPU/crash trong
48 bản ghi cuối này. Lỗi hết dung lượng lịch sử đã chạy lại thành công.

Đợt gốc ghi 3.496 lượt chạy, trong đó 43 thất bại. Đợt bổ sung ghi 852 lượt,
gồm 823 lượt cho job cần bù/chạy lại và 29 lượt fold đi kèm. Có 780 job chưa chạy
trong đợt gốc đã được bù; 43 job lỗi gốc có kết quả chạy lại. Vì thế:

- Tổng lượt thực thi được ghi: 3.496 + 852 = 4.348.
- Tổng job duy nhất: 4.276; không cộng lượt chạy lại và fold đi kèm thành job mới.
- Toàn lịch sử có 91 lượt lỗi: 90 SLOTTING_FAILED và một lỗi hết dung lượng.
- Khi dùng kết quả chạy lại được yêu cầu, còn 48 job thất bại duy nhất.

Bản ghi gốc giữ nguyên. `selected-records.json` ghi rõ nguồn original/followup;
`original-failure-followups.csv` liên kết thất bại gốc với lần chạy lại.

## Giới hạn diễn giải

Các bảng trên là thống kê mô tả. Chưa chạy thêm kiểm định hiệu chỉnh cho báo cáo
này; các fold chia sẻ dữ liệu huấn luyện không độc lập. Lịch chạy đồng thời và
ngân sách thời gian campaign bổ sung đã thay đổi, nên không dùng số đo thời gian
như một so sánh tốc độ trong điều kiện hoàn toàn kiểm soát. Dữ liệu là tổng hợp;
chưa có xác nhận hiệu quả ngoài cửa hàng thực tế hoặc năng lực triển khai production.

Tệp đi kèm: `summary.json`, `block-summary.csv`, `method-summary.csv`,
`paired-comparisons.csv`, `latest-failures.csv`, `original-failure-followups.csv`,
`selected-records.json` và `checksums.json`.
