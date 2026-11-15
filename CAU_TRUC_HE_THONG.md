# Cây thư mục và nhiệm vụ từng thành phần — Smart Retail Floor Allocation

Cập nhật theo hệ thống thực tế ngày **15/11/2026**, tại `D:\Smart_Retail_Floor_Allocation`.

Tài liệu này là bản đồ đọc mã nguồn và tài liệu. Ứng dụng hiện tại nằm trực tiếp trong `backend/` và `frontend/`. Các bộ cấu hình V3/V4/V5 nằm trong hệ thống thực nghiệm của ứng dụng này; tên phiên bản thiết kế không biểu thị một ứng dụng V2 riêng.

## 1. Phạm vi và cách đọc

Bản đồ này đã ẩn các mục test/kiểm thử theo yêu cầu. Đây là thay đổi cách trình bày trong tài liệu; các file thực tế vẫn giữ nguyên.

- Mỗi nhánh `├──` hoặc `└──` là một file/thư mục; phần sau `#` ghi nhiệm vụ.
- Liệt kê riêng **1,120 file** thuộc phạm vi tra cứu sau khi ẩn mã kiểm thử, cấu hình runner test và script chuyên chạy kiểm thử.
- Có **189 thư mục** được ghi nhiệm vụ, gồm các thư mục rỗng hiện có và các vùng gộp.
- Các vùng mang nhãn **[gộp nội dung sinh tự động/nội bộ]** có nhiệm vụ được mô tả ở nhánh thư mục, nhưng không mở rộng từng file bên trong: `.git`, `.venv`, `node_modules`, cache, build, kết quả trình duyệt và `var`. Vì vậy đây là cây đầy đủ của phần mã/config/dataset mẫu/tài liệu được kiểm kê, không phải danh sách mọi file hệ điều hành hay mọi dependency đã cài.
- Các tệp log, ảnh, JSON/XML trong `docs/**/evidence` vẫn được liệt kê từng file vì chúng thuộc bộ tài liệu được lưu. Tên/loại artifact và vị trí của chúng giúp nhận diện nhiệm vụ; nội dung lịch sử không được dùng để tuyên bố kiểm tra hiện tại đã đạt.
- Mô tả mã nguồn lấy từ phần giải thích đầu module và vai trò của module trong kiến trúc. Mô tả Markdown dùng tiêu đề tài liệu; cấu hình JSON dùng trường khai báo. Tệp nhị phân/ảnh được nhận diện theo loại và ngữ cảnh thư mục, không phải đã kiểm tra toàn bộ nội dung bên trong.
- Không đưa nội dung URI, mật khẩu hoặc các cấu hình bí mật vào bản đồ này. Những đường dẫn có thể tạo khi chạy nhưng chưa tồn tại không được vẽ thành thư mục đang có.

## 2. Điểm bắt đầu theo công việc

| Công việc | File cần đọc |
|---|---|
| Cài đặt và khởi động | [README.md](README.md), [scripts/setup.ps1](scripts/setup.ps1), [scripts/start.ps1](scripts/start.ps1) |
| API | [api/main.py](backend/src/smart_retail/api/main.py), [api/research.py](backend/src/smart_retail/api/research.py) |
| Luồng tối ưu T1–T4 | [workflow.py](backend/src/smart_retail/application/workflow.py), [stage_workflow.py](backend/src/smart_retail/application/stage_workflow.py) |
| Tối ưu liên tầng | [feedback/coordinator.py](backend/src/smart_retail/application/feedback/coordinator.py) |
| Hàng đợi và tiến trình tính toán | [workers/runner.py](backend/src/smart_retail/workers/runner.py) |
| Giao diện workspace | [AppShell.tsx](frontend/src/app/AppShell.tsx), [useWorkspace.tsx](frontend/src/app/useWorkspace.tsx) |
| Thực nghiệm qua CLI | [experiments/cli.py](backend/src/smart_retail/application/experiments/cli.py), [campaign.py](backend/src/smart_retail/application/experiments/campaign.py) |
| Điều phối Paper V5 ba slot | [scripts/run_paper_v5_parallel.py](scripts/run_paper_v5_parallel.py) — xem rõ tham số và identity trước khi chạy |
| Trạng thái bàn giao hiện tại | [HANDOFF.md](HANDOFF.md) |

Các đường dẫn trên phục vụ tra cứu. Việc đọc bản đồ không khởi chạy campaign hoặc dịch vụ. Engine chỉ giải từng phần; application sở hữu workflow; infrastructure triển khai persistence. Chứng nhận exact chỉ có phạm vi miền hữu hạn được khai báo.

## 3. Cây thư mục có chú thích

```text
Smart_Retail_Floor_Allocation/  # Mã ứng dụng, cấu hình, dữ liệu mẫu và tài liệu nghiên cứu.
├── .git/ [gộp nội dung sinh tự động/nội bộ]  # Dữ liệu Git: object, nhánh, index và cấu hình nội bộ; không liệt kê từng file quản trị.
├── .hypothesis/ [gộp nội dung sinh tự động/nội bộ]  # Cache ví dụ sinh bởi Hypothesis.
├── .mypy_cache/ [gộp nội dung sinh tự động/nội bộ]  # Cache kiểm tra kiểu Python.
├── .playwright-mcp/ [gộp nội dung sinh tự động/nội bộ]  # Artifact phiên trình duyệt hỗ trợ thao tác/kiểm tra trước đây.
├── .ruff_cache/ [gộp nội dung sinh tự động/nội bộ]  # Cache chạy Ruff.
├── .venv/ [gộp nội dung sinh tự động/nội bộ]  # Môi trường Python và package cài đặt; nội dung do công cụ quản lý, được gộp.
├── .vscode/  # Thiết lập trình soạn thảo cho workspace.
│   └── settings.json  # Thiết lập editor của workspace.
├── backend/  # Ứng dụng Python/FastAPI, domain, engine, persistence và worker.
│   ├── .pytest_cache/ [gộp nội dung sinh tự động/nội bộ]  # Cache pytest cho backend.
│   ├── .ruff_cache/ [gộp nội dung sinh tự động/nội bộ]  # Cache Ruff cho backend.
│   ├── migrations/  # Thư mục migration hiện có; không có file trong phần kiểm kê này.
│   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   └── versions/  # Vị trí dành cho các bản migration; thư mục hiện không có file trong kiểm kê.
│   │       └── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   ├── scripts/  # Thư mục công cụ backend hiện có; không có file trong phần kiểm kê này.
│   ├── src/  # Mã nguồn package Python cài qua pyproject.toml.
│   │   ├── smart_retail/  # Package ứng dụng hiện tại; tách API, application, domain/engine và infrastructure.
│   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   ├── api/  # Adapter HTTP: nhận yêu cầu, gọi application và trả phản hồi.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── __init__.py  # Điểm khai báo package api. Nhóm này tổ chức adapter HTTP; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── main.py  # Khai báo ứng dụng HTTP, kiểm tra yêu cầu và chuyển thao tác sang tầng application. Công việc tính toán được đưa vào hàng đợi để worker xử lý.
│   │   │   │   └── research.py  # Các endpoint cho danh mục dữ liệu, cấu hình, campaign và báo cáo nghiên cứu. Yêu cầu chạy tạo tiến trình giám sát; HTTP không trực tiếp giải bài toán số.
│   │   │   ├── application/  # Điều phối nghiệp vụ, quản lý dự án, đánh giá và thực nghiệm.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── experiments/  # Lập kế hoạch campaign, dữ liệu tổng hợp, chia tập, phân tích, báo cáo và CLI.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package application/experiments. Nhóm này tổ chức dịch vụ ứng dụng và điều phối; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── analysis.py  # Thống kê kết quả và so sánh ghép cặp theo đơn vị thực nghiệm. Giữ thông tin thất bại; không coi các fold hoặc lần lặp phụ thuộc là mẫu độc lập tùy ý.
│   │   │   │   │   ├── calibration.py  # Đo tải mô phỏng và hiệu chỉnh khoảng cách thời gian giữa các đơn để hướng đến mức sử dụng picker đã khai báo.
│   │   │   │   │   ├── campaign.py  # Lập kế hoạch campaign có thể tiếp tục, lưu đầu vào bất biến và đưa từng job qua hàng đợi production. Chỉ tiếp tục khi nguồn, cấu hình và dependency khớp nhận diện đã lưu.
│   │   │   │   │   ├── cli.py  # Điểm vào dòng lệnh cho chạy, tiếp tục, xác minh, phân tích và phát lại campaign. Verify kiểm tra tệp đã lưu; replay mới thực hiện tính lại.
│   │   │   │   │   ├── deepmg_export.py  # Xuất kết quả theo từng nhánh thuật toán và fold theo định dạng deepmg. Các bảng được dựng từ bản ghi thực nghiệm đã lưu.
│   │   │   │   │   ├── finite_spaces.py  # Dựng miền quyết định hữu hạn từ nghiệm heuristic đã ghi nhận để chạy tham chiếu exact. Chứng nhận chỉ có ý nghĩa trong miền được khai báo.
│   │   │   │   │   ├── generators.py  # Sinh bộ dữ liệu tổng hợp có seed và manifest nguồn gốc.
│   │   │   │   │   ├── joint_reports.py  # Trích đường hội tụ và bằng chứng chứng nhận từ kết quả joint đã lưu, phục vụ kiểm tra lại quá trình tìm kiếm.
│   │   │   │   │   ├── partition.py  # Chia thiết kế campaign quá lớn thành các phần nằm trong giới hạn tài nguyên, giữ nhóm so sánh ghép cặp cần thiết.
│   │   │   │   │   ├── process.py  # Tiến trình giám sát campaign do dịch vụ khởi tạo. Tiếp nhận tham số dòng lệnh và gọi luồng thực nghiệm ở tầng application.
│   │   │   │   │   ├── reports.py  # Tổng hợp bản ghi campaign thành bảng, thống kê và biểu đồ. Báo cáo phản ánh kết quả đã ghi nhận cùng trạng thái và phạm vi dữ liệu.
│   │   │   │   │   ├── service.py  # Dịch vụ cho dashboard nghiên cứu: tra danh mục, khởi chạy, dừng và đọc kết quả. Phần số chạy trong tiến trình worker riêng.
│   │   │   │   │   ├── splits.py  # Chia đơn theo seed cho k-fold hoặc temporal holdout và áp dụng tập tương ứng vào đầu vào job. Seed cố định giúp tái lập việc chia tập.
│   │   │   │   │   ├── storage.py  # Đọc và ghi bằng chứng campaign, tạo dấu vân tay và kiểm tra checksum. Phân biệt tệp bất biến với checkpoint được thay thế nguyên tử.
│   │   │   │   │   └── validation.py  # Kiểm tra độc lập các quyết định đã lưu từ dữ liệu vật lý. Không dùng lại ma trận ràng buộc của solver làm bằng chứng duy nhất.
│   │   │   │   ├── feedback/  # Tìm kiếm liên tầng; quản lý ứng viên, ngân sách, chẩn đoán và snapshot.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package application/feedback. Nhóm này tổ chức dịch vụ ứng dụng và điều phối; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── bootstrap.py  # Thử sửa tính khả thi trong ngân sách giới hạn khi phương án tuần tự chưa khởi tạo được vòng tối ưu liên tầng.
│   │   │   │   │   ├── cli.py  # Công cụ phát lại chứng nhận từ đầu vào worker và tệp bằng chứng đã xuất để kiểm tra độc lập.
│   │   │   │   │   ├── coordinator.py  # Điều phối tìm kiếm liên tầng với ngân sách, cache và trạng thái kết thúc rõ ràng. Tìm kiếm heuristic không tìm thấy nghiệm chưa chứng minh bài toán vô nghiệm.
│   │   │   │   │   ├── diagnostics.py  # Rút chẩn đoán từ hành trình và hàng chờ mô phỏng để đề xuất thay đổi quyết định. Các số liệu phản ánh giả định mô phỏng tổng hợp.
│   │   │   │   │   ├── evaluator.py  # Chạy đánh giá trên các seed kịch bản dùng chung và tính mục tiêu so sánh nhất quán. Các quyết định được kiểm tra trước khi được chọn.
│   │   │   │   │   ├── genetic.py  # Baseline di truyền dạng steady-state trên vị trí kệ của Paper V5. Quần thể, biến đổi và đánh giá đều chịu seed cùng ngân sách khai báo.
│   │   │   │   │   ├── neighborhood.py  # Sinh các thay đổi quyết định T1–T4 và sắp thứ tự theo chẩn đoán. Đề xuất vẫn cần được đánh giá và kiểm tra tính khả thi.
│   │   │   │   │   ├── restarts.py  # Sinh điểm khởi động lại có seed cho vị trí kệ, phục vụ multistart và các phương pháp tìm kiếm dùng chung quy tắc seed.
│   │   │   │   │   ├── state.py  # Đóng gói snapshot đã đánh giá bằng nội dung niêm phong. Mỗi lần đọc trả về bản sao để tránh ứng viên mới làm thay đổi nghiệm đang giữ.
│   │   │   │   │   └── surrogate.py  # Ước lượng khoảng cách đi bộ để xếp hạng bố trí trước khi mô phỏng đầy đủ. Giá trị surrogate dùng sàng lọc, còn kết quả chính lấy từ evaluator.
│   │   │   │   ├── __init__.py  # Điểm khai báo package application. Nhóm này tổ chức dịch vụ ứng dụng và điều phối; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── decisions.py  # Phát lại các quyết định bố trí, phân bổ và xếp hàng đã chọn qua bộ kiểm tra chính thức trước khi dùng trong pipeline.
│   │   │   │   ├── evaluation.py  # Ước lượng nhu cầu từ tập đơn huấn luyện và chấm phương án đã chọn trên đơn giữ lại. Tách hai tập giúp tránh đưa dữ liệu đánh giá vào bước tối ưu.
│   │   │   │   ├── projects.py  # Dịch vụ chỉnh sửa dự án, kiểm tra tham chiếu và tạo snapshot cho lần chạy. Revision được dùng để phát hiện cập nhật đồng thời.
│   │   │   │   ├── stage_workflow.py  # Điều phối một ứng viên qua các tầng T1–T4 và tái sử dụng cache theo đầu vào phụ thuộc. Engine từng tầng chỉ giải phần việc được giao.
│   │   │   │   └── workflow.py  # Chọn luồng sequential, multistart hoặc joint; quản lý ngân sách chung và chọn ứng viên hợp lệ tốt nhất trong số đã đánh giá.
│   │   │   ├── contracts/  # Hợp đồng Pydantic, kiểm tra dữ liệu, JSON Schema và chuyển đổi domain.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── __init__.py  # Điểm khai báo package contracts. Nhóm này tổ chức hợp đồng dữ liệu; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── experiments.py  # Hợp đồng Pydantic cho dataset, treatment, đánh giá và campaign. Kiểm tra tham chiếu cùng giới hạn thiết kế trước khi tạo kế hoạch job.
│   │   │   │   ├── feedback.py  # Hợp đồng mục tiêu và điều khiển tối ưu liên tầng, gồm seed, ngân sách và các tùy chọn tìm kiếm có giới hạn.
│   │   │   │   ├── inputs.py  # Bảy nhóm đầu vào có phiên bản, kiểm tra tham chiếu và chuyển sang domain. Các mô hình này cũng cung cấp JSON Schema.
│   │   │   │   ├── migration.py  # Chuẩn hóa rõ ràng phiên bản gói đầu vào của ứng dụng hiện tại, giữ nguyên dữ liệu nguồn được truyền vào.
│   │   │   │   ├── optimality.py  # Khai báo các miền quyết định hữu hạn cho kiểm tra tối ưu. Phạm vi chứng nhận phụ thuộc chính xác vào miền này.
│   │   │   │   ├── outputs.py  # Hợp đồng phản hồi HTTP cho dự án, lần chạy và lỗi. Giữ định dạng API tách khỏi cấu trúc lưu trữ nội bộ.
│   │   │   │   └── tabular.py  # Nhập và xuất CSV cho dữ liệu dạng bảng, giữ trường lồng nhau bằng ô JSON để có thể khôi phục đầy đủ.
│   │   │   ├── domain/  # Mô hình nghiệp vụ và đơn vị SI, độc lập với HTTP và driver lưu trữ.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── categories/  # Mô hình nghiệp vụ cho ngành hàng.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/categories. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho ngành hàng. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── demand/  # Mô hình nghiệp vụ cho nhu cầu và hành vi.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/demand. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho nhu cầu và kết quả mô phỏng. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── floorplan/  # Mô hình nghiệp vụ cho mặt bằng.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/floorplan. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho mặt bằng và nghiệm bố trí. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── optimization/  # Mô hình nghiệp vụ cho cấu hình tối ưu.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/optimization. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho cấu hình và lần tối ưu. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── orders/  # Mô hình nghiệp vụ cho đơn hàng.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/orders. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho đơn hàng và dòng sản phẩm. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── products/  # Mô hình nghiệp vụ cho sản phẩm.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/products. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho sản phẩm và planogram. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── projects/  # Mô hình nghiệp vụ cho dự án.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/projects. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho dự án, cửa hàng và vùng trưng bày. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── shelves/  # Mô hình nghiệp vụ cho kệ.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package domain/shelves. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── models.py  # Mô hình domain cho kệ và tầng kệ. Các kiểu nghiệp vụ không phụ thuộc HTTP hoặc driver lưu trữ; kích thước vật lý dùng đơn vị SI.
│   │   │   │   ├── __init__.py  # Điểm khai báo package domain. Nhóm này tổ chức mô hình nghiệp vụ; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── models.py  # Tập hợp API domain công khai; các định nghĩa cụ thể nằm trong module nghiệp vụ tương ứng.
│   │   │   │   ├── primitives.py  # Kiểu tọa độ dùng đơn vị SI và lỗi engine có mã trạng thái rõ ràng để application xử lý nhất quán.
│   │   │   │   └── workspace.py  # Gom các nhóm domain thành một RetailDataset để truyền đầu vào đã chuyển đổi cho luồng tối ưu.
│   │   │   ├── engines/  # Các thuật toán và bộ replay ràng buộc cho từng phần bài toán.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── joint_exact/  # Duyệt miền hữu hạn và tạo/kiểm tra chứng nhận trong đúng miền đó.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package engines/joint_exact. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── formulation.py  # Biên dịch miền Cartesian được khai báo thành quyết định có thể liệt kê. Giới hạn miền phải được phản ánh trong kết luận tối ưu.
│   │   │   │   │   ├── solver.py  # Duyệt miền hữu hạn và ghi bằng chứng các trạng thái đã xét. Tìm kiếm chưa hoàn tất chỉ cung cấp cận và nghiệm hiện có.
│   │   │   │   │   └── verifier.py  # Phát lại chứng nhận bằng chỉ số mixed-radix và kiểm tra miền độc lập với thuật toán tìm kiếm.
│   │   │   │   ├── t1_layout/  # T1: dựng/cải thiện vị trí kệ và kiểm tra hình học.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package engines/t1_layout. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── engine.py  # T1 dựng vị trí kệ theo lưới và kiểm tra hình học. Tọa độ, kích thước và khoảng cách dùng mét.
│   │   │   │   │   ├── geometry.py  # Dựng footprint và phát lại ràng buộc hình học của kệ: biên mặt bằng, vật cản, chồng lấn và khoảng trống.
│   │   │   │   │   └── search.py  # Cải thiện vị trí kệ bằng tìm kiếm lân cận có giới hạn. Mỗi phương án được xét phải đáp ứng kiểm tra hình học.
│   │   │   │   ├── t2_allocation/  # T2: phân bổ ngành hàng bằng greedy/MILP và replay độc lập.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package engines/t2_allocation. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── engine.py  # T2 phân bổ ngành hàng lên kệ bằng greedy hoặc MILP HiGHS. Sức chứa chiều rộng và quan hệ giữa ngành được kiểm tra trước khi trả nghiệm.
│   │   │   │   │   └── validation.py  # Phát lại phân bổ và tính mục tiêu từ quyết định ngành–kệ, độc lập với ma trận MILP.
│   │   │   │   ├── t3_slotting/  # T3: xếp SKU, đóng gói trên kệ, sửa first-fit và kiểm tra planogram.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package engines/t3_slotting. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── engine.py  # T3 xếp SKU bằng first-fit; khi mắc kẹt thử sắp lại kệ trong giới hạn. Kết quả phải thỏa kiểm tra kích thước và sức chứa.
│   │   │   │   │   ├── mip.py  # Mô hình đóng gói dải hữu hạn cho SKU, facings, chiều sâu tồn và lớp xếp. Kết luận tối ưu gắn với mô hình này.
│   │   │   │   │   ├── repair.py  # Sắp lại một kệ theo tìm kiếm hữu hạn để xử lý phân mảnh do first-fit, có kiểm tra hủy và thời hạn.
│   │   │   │   │   └── validation.py  # Phát lại planogram từ kích thước sản phẩm và kệ: kiểm tra trùng vị trí, tải trọng, facings và sức chứa.
│   │   │   │   ├── t4_simulation/  # T4: định tuyến lấy hàng và mô phỏng hàng chờ phục vụ.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package engines/t4_simulation. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── engine.py  # T4 kết hợp đường đi trên lưới và hàng chờ phục vụ kệ bằng SimPy. KPI được tính theo hành vi và tải tổng hợp đã khai báo.
│   │   │   │   │   └── routing.py  # Chọn thứ tự ghé điểm lấy hàng theo chính sách định tuyến trên khoảng cách đường đi hợp lệ.
│   │   │   │   ├── __init__.py  # Điểm khai báo package engines. Nhóm này tổ chức thuật toán từng tầng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   └── navigation.py  # Dựng đồ thị vùng đi được và kiểm tra liên thông, khả năng phục vụ. Hình học được kiểm tra độc lập với thuật toán định tuyến.
│   │   │   ├── infrastructure/  # Persistence, đường dẫn, cache và nhận diện nguồn/dependency.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── mongodb/  # PyMongo, repository, lease/fencing, GridFS và sao lưu BSON.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package infrastructure/mongodb. Nhóm này tổ chức lưu trữ và tích hợp hệ thống; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   ├── backup.py  # Sao lưu và phục hồi BSON gốc cùng GridFS cho database đã ngừng ghi. Kiểm tra checksum và điều kiện đích trước khi phục hồi.
│   │   │   │   │   ├── client.py  # Quản lý vòng đời client PyMongo và phạm vi sử dụng repository, cung cấp kết nối cho application.
│   │   │   │   │   ├── health.py  # CLI kiểm tra kết nối và index MongoDB, có kiểm tra cutover theo tùy chọn. Báo cáo tránh đưa thông tin xác thực ra ngoài.
│   │   │   │   │   ├── indexes.py  # Tạo index lặp lại an toàn cho truy vấn và chuyển trạng thái. Index không dùng TTL để tự xóa bằng chứng chạy.
│   │   │   │   │   ├── project_repository.py  # Lưu aggregate dự án bằng cập nhật nguyên tử và kiểm tra revision để tránh ghi đè thay đổi đồng thời.
│   │   │   │   │   ├── run_repository.py  # Lưu lần chạy và các chuyển trạng thái hàng đợi. Claim, lease và quyền công bố giúp ngăn worker cũ ghi kết quả sau khi mất quyền.
│   │   │   │   │   ├── serializers.py  # Tuần tự hóa payload giữ nguyên giá trị JSON; dùng vùng lưu overflow cho nội dung lớn thay vì cắt dữ liệu.
│   │   │   │   │   ├── settings.py  # Đọc cấu hình kết nối MongoDB cho runtime hiện tại và tập hợp các tùy chọn persistence.
│   │   │   │   │   └── worker_repository.py  # Lưu heartbeat và thông tin worker để theo dõi tiến trình xử lý hàng đợi.
│   │   │   │   ├── repositories/  # Giao diện repository và record thuần cho application.
│   │   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   │   ├── __init__.py  # Điểm khai báo package infrastructure/repositories. Nhóm này tổ chức lưu trữ và tích hợp hệ thống; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   │   └── contracts.py  # Record thuần và giao diện repository cho dự án, lần chạy và worker; tầng application phụ thuộc hợp đồng này.
│   │   │   │   ├── __init__.py  # Điểm khai báo package infrastructure. Nhóm này tổ chức lưu trữ và tích hợp hệ thống; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── database.py  # Cổng kết nối persistence MongoDB cho application và worker; chi tiết driver nằm trong module mongodb.
│   │   │   │   ├── filesystem.py  # Chuẩn hóa đường dẫn artifact, hỗ trợ đường dẫn Windows dài và công bố tệp bất biến an toàn.
│   │   │   │   ├── provenance.py  # Tính nhận diện runtime từ byte nguồn Python, phiên bản solver và package. Thêm comment cũng đổi source_sha256 của lượt chạy mới.
│   │   │   │   └── stage_cache.py  # Cache JSON theo nội dung đầu vào từng tầng, kiểm tra checksum khi đọc để phát hiện hỏng hoặc sửa tệp.
│   │   │   ├── reporting/  # Xuất dữ liệu lần chạy thành báo cáo và bảng planogram.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── __init__.py  # Điểm khai báo package reporting. Nhóm này tổ chức xuất báo cáo; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   └── export.py  # Xuất kết quả lần chạy sang báo cáo JSON và planogram CSV từ dữ liệu đã có.
│   │   │   ├── workers/  # Nhận job từ hàng đợi bền vững, giám sát tiến trình con và tài nguyên.
│   │   │   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   │   │   ├── __init__.py  # Điểm khai báo package workers. Nhóm này tổ chức xử lý hàng đợi trong tiến trình riêng; các định nghĩa cụ thể nằm trong file con.
│   │   │   │   ├── resources.py  # Đọc mức sử dụng CPU và bộ nhớ của tiến trình con từ hệ điều hành để supervisor áp dụng giới hạn.
│   │   │   │   └── runner.py  # Nhận job bằng claim nguyên tử, chạy số trong tiến trình con có thể dừng và công bố bằng lease. Receipt lưu trạng thái, checksum và tài nguyên quan sát được.
│   │   │   └── __init__.py  # Điểm khai báo package smart_retail. Nhóm này tổ chức các module chuyên trách; các định nghĩa cụ thể nằm trong file con.
│   │   └── smart_retail.egg-info/ [gộp nội dung sinh tự động/nội bộ]  # Metadata package Python sinh bởi công cụ đóng gói; nội dung được gộp.
│   ├── Dockerfile  # Build image Python chứa backend và entrypoint API; worker dùng cùng nền tảng.
│   ├── pyproject.toml  # Metadata package Python, dependency khai báo và cấu hình pytest/Ruff/mypy.
│   └── requirements-lock.txt  # Danh sách phiên bản package Python được chốt cho môi trường cài đặt.
├── configs/  # Mẫu cấu hình môi trường cục bộ của ứng dụng.
│   └── local.env.example  # Mẫu biến môi trường cho chạy cục bộ.
├── datasets/  # Đầu vào mẫu, miền đối chứng, manifest và JSON Schema.
│   ├── joint/  # Fixture tổng hợp và miền quyết định hữu hạn phục vụ kiểm tra joint.
│   │   ├── local-trap-space.json  # Miền quyết định hữu hạn cho fixture local-trap.
│   │   ├── local-trap.json  # Fixture đầu vào local-trap; dùng cho minh họa, kiểm tra hoặc đối chứng theo tên trường hợp.
│   │   ├── manifest.json  # Manifest nhận diện, nguồn gốc và danh mục dữ liệu manifest.
│   │   ├── two-shelves-space.json  # Miền quyết định hữu hạn cho fixture two-shelves.
│   │   └── two-shelves.json  # Fixture đầu vào two-shelves; dùng cho minh họa, kiểm tra hoặc đối chứng theo tên trường hợp.
│   ├── samples/  # Dữ liệu mẫu và trường hợp đặc biệt cho nhập liệu/kiểm thử.
│   │   ├── invalid_inputs.json  # Fixture đầu vào invalid_inputs; dùng cho minh họa, kiểm tra hoặc đối chứng theo tên trường hợp.
│   │   ├── small_store.json  # Fixture đầu vào small_store; dùng cho minh họa, kiểm tra hoặc đối chứng theo tên trường hợp.
│   │   └── t3_first_fit_fragmentation.json  # Fixture đầu vào t3_first_fit_fragmentation; dùng cho minh họa, kiểm tra hoặc đối chứng theo tên trường hợp.
│   ├── schemas/  # JSON Schema sinh từ các hợp đồng dữ liệu.
│   │   ├── campaign.schema.json  # JSON Schema cho CampaignSpec; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── categories.schema.json  # JSON Schema cho CategoriesInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── demand.schema.json  # JSON Schema cho DemandInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── floorplan.schema.json  # JSON Schema cho FloorplanInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── optimization.schema.json  # JSON Schema cho OptimizationInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── orders.schema.json  # JSON Schema cho OrdersInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   ├── products.schema.json  # JSON Schema cho ProductsInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   │   └── shelves.schema.json  # JSON Schema cho ShelvesInput; mô tả kiểu, trường và ràng buộc đầu vào.
│   ├── synthetic/  # Hướng dẫn nguồn gốc và cách dùng dữ liệu tổng hợp.
│   │   └── README.md  # Tài liệu: Dữ liệu tổng hợp.
│   ├── manifest-joint-v3.json  # Manifest nhận diện, nguồn gốc và danh mục dữ liệu manifest-joint-v3.
│   ├── manifest-research-v1.json  # Manifest nhận diện, nguồn gốc và danh mục dữ liệu manifest-research-v1.
│   └── manifest-research-v2.json  # Manifest nhận diện, nguồn gốc và danh mục dữ liệu manifest-research-v2.
├── docs/  # Tài liệu kiến trúc, API, nghiên cứu, kiểm chứng và bằng chứng lịch sử.
│   ├── api/  # Tài liệu các tuyến và cách dùng API.
│   │   └── routes.md  # Tài liệu: API cục bộ.
│   ├── architecture/  # Kiến trúc hiện tại, bản đồ phụ thuộc và lịch sử chuyển đổi.
│   │   ├── actual-tree.txt  # Bản ghi văn bản actual-tree của đợt/tài liệu tương ứng.
│   │   ├── changed-files.json  # Danh sách thay đổi ghi nhận trong đợt tương ứng.
│   │   ├── CURRENT_STATE.md  # Tài liệu: Trạng thái hệ thống ngày 23/10/2026.
│   │   ├── DEPENDENCY_MAP.md  # Tài liệu: Ranh giới phụ thuộc hiện hành.
│   │   ├── HISTORICAL_ARCHIVE.md  # Tài liệu: Hồ sơ lưu trữ ngoài dự án.
│   │   ├── migration.md  # Tài liệu: Tái cấu trúc trực tiếp tại thư mục gốc — 21/10/2026.
│   │   └── overview.md  # Tài liệu: Kiến trúc ứng dụng.
│   ├── data/  # Hợp đồng dữ liệu đầu vào và cách diễn giải.
│   │   └── input-contracts.md  # Tài liệu: Bảy nhóm dữ liệu đầu vào.
│   ├── decisions/  # Các quyết định kiến trúc có ghi lý do.
│   │   ├── 0001-modular-monolith.md  # Tài liệu: ADR 0001 — Modular monolith và công việc theo process.
│   │   └── 0002-mongodb-only.md  # Tài liệu: ADR 0002 — MongoDB là persistence duy nhất.
│   ├── migration/  # Tài liệu và bằng chứng chuyển đổi persistence/triển khai.
│   │   ├── evidence/  # Biên nhận, log và ảnh bằng chứng đã lưu theo từng lượt kiểm chứng; mang tính lịch sử.
│   │   │   ├── 20261022-mongodb-only-release-01/  # Nhóm bằng chứng 20261022-mongodb-only-release-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   ├── architecture.stderr.log  # Log lỗi/cảnh báo stderr của architecture; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── architecture.stdout.log  # Log đầu ra stdout của architecture; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── e2e.stderr.log  # Log lỗi/cảnh báo stderr của e2e; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── e2e.stdout.log  # Log đầu ra stdout của e2e; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── eslint.stderr.log  # Log lỗi/cảnh báo stderr của eslint; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── eslint.stdout.log  # Log đầu ra stdout của eslint; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── frontend-build.stderr.log  # Log lỗi/cảnh báo stderr của frontend-build; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── frontend-build.stdout.log  # Log đầu ra stdout của frontend-build; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── isolated-health.json  # Biên nhận sức khỏe dịch vụ trong môi trường kiểm tra cô lập.
│   │   │   │   ├── mypy.stderr.log  # Log lỗi/cảnh báo stderr của mypy; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── mypy.stdout.log  # Log đầu ra stdout của mypy; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── npm-audit.stderr.log  # Log lỗi/cảnh báo stderr của npm-audit; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── npm-audit.stdout.log  # Log đầu ra stdout của npm-audit; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pip-check.stderr.log  # Log lỗi/cảnh báo stderr của pip-check; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pip-check.stdout.log  # Log đầu ra stdout của pip-check; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.stderr.log  # Log lỗi/cảnh báo stderr của pytest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.stdout.log  # Log đầu ra stdout của pytest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   │   ├── ruff.stderr.log  # Log lỗi/cảnh báo stderr của ruff; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── ruff.stdout.log  # Log đầu ra stdout của ruff; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── vitest.stderr.log  # Log lỗi/cảnh báo stderr của vitest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── vitest.stdout.log  # Log đầu ra stdout của vitest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   ├── 20261022-mongodb-release-01/  # Nhóm bằng chứng 20261022-mongodb-release-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   └── isolated-health.json  # Biên nhận sức khỏe dịch vụ trong môi trường kiểm tra cô lập.
│   │   │   └── 20261022-mongodb-release-02/  # Nhóm bằng chứng 20261022-mongodb-release-02; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │       ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │       │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │       │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │       │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │       │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │       │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │       │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │       │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │       │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │       │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │       │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │       │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │       │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │       │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │       ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │       └── isolated-health.json  # Biên nhận sức khỏe dịch vụ trong môi trường kiểm tra cô lập.
│   │   ├── historical-science-preservation.json  # Biên nhận/cấu hình JSON historical-science-preservation trong ngữ cảnh docs/migration.
│   │   ├── mongodb-index-health.json  # Biên nhận/cấu hình JSON mongodb-index-health trong ngữ cảnh docs/migration.
│   │   ├── mongodb-only-history-restore.json  # Biên nhận/cấu hình JSON mongodb-only-history-restore trong ngữ cảnh docs/migration.
│   │   ├── mongodb-only-native-restore.json  # Biên nhận/cấu hình JSON mongodb-only-native-restore trong ngữ cảnh docs/migration.
│   │   ├── mongodb-restart-verification-02.json  # Biên nhận/cấu hình JSON mongodb-restart-verification-02 trong ngữ cảnh docs/migration.
│   │   ├── mongodb-restart-verification.json  # Biên nhận/cấu hình JSON mongodb-restart-verification trong ngữ cảnh docs/migration.
│   │   ├── MONGODB_BACKUP_RESTORE.md  # Tài liệu: Native MongoDB backup and restore.
│   │   ├── MONGODB_ONLY_ACCEPTANCE.md  # Tài liệu: Kiểm chứng persistence hiện hành.
│   │   └── MONGODB_OPERATIONS.md  # Tài liệu: Vận hành MongoDB.
│   ├── modules/  # Tài liệu trách nhiệm và ranh giới từng module.
│   │   ├── engines.md  # Tài liệu: T1–T4: trách nhiệm, hợp đồng và mức thực hiện.
│   │   └── input-modules.md  # Tài liệu: Module dữ liệu.
│   ├── release/  # Tiêu chí, quy trình và bằng chứng phát hành.
│   │   ├── evidence/  # Biên nhận, log và ảnh bằng chứng đã lưu theo từng lượt kiểm chứng; mang tính lịch sử.
│   │   │   ├── 20261022-atlas-01/  # Nhóm bằng chứng 20261022-atlas-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   ├── 20261022-compose-01/  # Nhóm bằng chứng 20261022-compose-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-01.
│   │   │   ├── 20261022-compose-02/  # Nhóm bằng chứng 20261022-compose-02; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-02.
│   │   │   ├── 20261022-compose-03/  # Nhóm bằng chứng 20261022-compose-03; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-03.
│   │   │   ├── 20261022-compose-04/  # Nhóm bằng chứng 20261022-compose-04; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── command-01.stderr.log  # Log lỗi/cảnh báo stderr của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-01.stdout.log  # Log đầu ra stdout của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-04.
│   │   │   ├── 20261022-compose-05/  # Nhóm bằng chứng 20261022-compose-05; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── command-01.stderr.log  # Log lỗi/cảnh báo stderr của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-01.stdout.log  # Log đầu ra stdout của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-02.stderr.log  # Log lỗi/cảnh báo stderr của command-02; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-02.stdout.log  # Log đầu ra stdout của command-02; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-03.stderr.log  # Log lỗi/cảnh báo stderr của command-03; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-03.stdout.log  # Log đầu ra stdout của command-03; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── compose.log  # Log nhật ký của compose; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-05.
│   │   │   ├── 20261022-compose-06/  # Nhóm bằng chứng 20261022-compose-06; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── command-01.stderr.log  # Log lỗi/cảnh báo stderr của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-01.stdout.log  # Log đầu ra stdout của command-01; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-02.stderr.log  # Log lỗi/cảnh báo stderr của command-02; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-02.stdout.log  # Log đầu ra stdout của command-02; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-03.stderr.log  # Log lỗi/cảnh báo stderr của command-03; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-03.stdout.log  # Log đầu ra stdout của command-03; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-04.stderr.log  # Log lỗi/cảnh báo stderr của command-04; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-04.stdout.log  # Log đầu ra stdout của command-04; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-05.stderr.log  # Log lỗi/cảnh báo stderr của command-05; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-05.stdout.log  # Log đầu ra stdout của command-05; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-06.stderr.log  # Log lỗi/cảnh báo stderr của command-06; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-06.stdout.log  # Log đầu ra stdout của command-06; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-07.stderr.log  # Log lỗi/cảnh báo stderr của command-07; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── command-07.stdout.log  # Log đầu ra stdout của command-07; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── compose.log  # Log nhật ký của compose; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-06.
│   │   │   ├── 20261022-compose-static-01/  # Nhóm bằng chứng 20261022-compose-static-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-compose-static-01.
│   │   │   ├── 20261022-longpath-01/  # Nhóm bằng chứng 20261022-longpath-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── full-long.stderr.log  # Log lỗi/cảnh báo stderr của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.stdout.log  # Log đầu ra stdout của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.xml  # Báo cáo JUnit XML của bộ kiểm thử ở đường dẫn Windows dài; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── full-short.stderr.log  # Log lỗi/cảnh báo stderr của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.stdout.log  # Log đầu ra stdout của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.xml  # Báo cáo JUnit XML của bộ kiểm thử đối chiếu ở đường dẫn ngắn; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── http-repeat-1.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.stdout.log  # Log đầu ra stdout của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 1 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-2.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.stdout.log  # Log đầu ra stdout của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 2 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-3.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.stdout.log  # Log đầu ra stdout của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 3 trong đợt xác minh đường dẫn dài.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-longpath-01.
│   │   │   ├── 20261022-longpath-02/  # Nhóm bằng chứng 20261022-longpath-02; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── full-long.stderr.log  # Log lỗi/cảnh báo stderr của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.stdout.log  # Log đầu ra stdout của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.xml  # Báo cáo JUnit XML của bộ kiểm thử ở đường dẫn Windows dài; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── full-short.stderr.log  # Log lỗi/cảnh báo stderr của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.stdout.log  # Log đầu ra stdout của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.xml  # Báo cáo JUnit XML của bộ kiểm thử đối chiếu ở đường dẫn ngắn; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── http-repeat-1.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.stdout.log  # Log đầu ra stdout của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 1 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-2.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.stdout.log  # Log đầu ra stdout của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 2 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-3.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.stdout.log  # Log đầu ra stdout của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 3 trong đợt xác minh đường dẫn dài.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-longpath-02.
│   │   │   ├── 20261022-longpath-03/  # Nhóm bằng chứng 20261022-longpath-03; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── full-long.stderr.log  # Log lỗi/cảnh báo stderr của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.stdout.log  # Log đầu ra stdout của full-long; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-long.xml  # Báo cáo JUnit XML của bộ kiểm thử ở đường dẫn Windows dài; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── full-short.stderr.log  # Log lỗi/cảnh báo stderr của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.stdout.log  # Log đầu ra stdout của full-short; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── full-short.xml  # Báo cáo JUnit XML của bộ kiểm thử đối chiếu ở đường dẫn ngắn; bằng chứng lịch sử của lượt này.
│   │   │   │   ├── http-repeat-1.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.stdout.log  # Log đầu ra stdout của http-repeat-1; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-1.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 1 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-2.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.stdout.log  # Log đầu ra stdout của http-repeat-2; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-2.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 2 trong đợt xác minh đường dẫn dài.
│   │   │   │   ├── http-repeat-3.stderr.log  # Log lỗi/cảnh báo stderr của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.stdout.log  # Log đầu ra stdout của http-repeat-3; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── http-repeat-3.xml  # Báo cáo JUnit XML của lượt kiểm thử HTTP lặp số 3 trong đợt xác minh đường dẫn dài.
│   │   │   │   └── verification.json  # Biên nhận/cấu hình JSON verification trong ngữ cảnh docs/release/evidence/20261022-longpath-03.
│   │   │   ├── 20261022-longpath-baseline/  # Nhóm bằng chứng 20261022-longpath-baseline; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── cache-reproduction.json  # Biên nhận/cấu hình JSON cache-reproduction trong ngữ cảnh docs/release/evidence/20261022-longpath-baseline.
│   │   │   │   ├── receipt.json  # Biên nhận/cấu hình JSON receipt trong ngữ cảnh docs/release/evidence/20261022-longpath-baseline.
│   │   │   │   ├── stderr.log  # Log nhật ký của stderr; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── stdout.log  # Log nhật ký của stdout; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   ├── 20261022-release-quality-01/  # Nhóm bằng chứng 20261022-release-quality-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   ├── architecture.stderr.log  # Log lỗi/cảnh báo stderr của architecture; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── architecture.stdout.log  # Log đầu ra stdout của architecture; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── e2e.stderr.log  # Log lỗi/cảnh báo stderr của e2e; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── e2e.stdout.log  # Log đầu ra stdout của e2e; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── eslint.stderr.log  # Log lỗi/cảnh báo stderr của eslint; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── eslint.stdout.log  # Log đầu ra stdout của eslint; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── frontend-build.stderr.log  # Log lỗi/cảnh báo stderr của frontend-build; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── frontend-build.stdout.log  # Log đầu ra stdout của frontend-build; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── isolated-health.json  # Biên nhận sức khỏe dịch vụ trong môi trường kiểm tra cô lập.
│   │   │   │   ├── mypy.stderr.log  # Log lỗi/cảnh báo stderr của mypy; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── mypy.stdout.log  # Log đầu ra stdout của mypy; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── npm-audit.stderr.log  # Log lỗi/cảnh báo stderr của npm-audit; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── npm-audit.stdout.log  # Log đầu ra stdout của npm-audit; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pip-check.stderr.log  # Log lỗi/cảnh báo stderr của pip-check; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pip-check.stdout.log  # Log đầu ra stdout của pip-check; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.stderr.log  # Log lỗi/cảnh báo stderr của pytest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.stdout.log  # Log đầu ra stdout của pytest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   │   ├── ruff.stderr.log  # Log lỗi/cảnh báo stderr của ruff; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── ruff.stdout.log  # Log đầu ra stdout của ruff; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   ├── vitest.stderr.log  # Log lỗi/cảnh báo stderr của vitest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   │   └── vitest.stdout.log  # Log đầu ra stdout của vitest; bằng chứng lịch sử, không phải kết quả kiểm tra mới.
│   │   │   ├── git-audit-01/  # Nhóm bằng chứng git-audit-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── 00.stderr.txt  # Bản ghi văn bản 00.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 01.stderr.txt  # Bản ghi văn bản 01.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 02.stderr.txt  # Bản ghi văn bản 02.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 03.stderr.txt  # Bản ghi văn bản 03.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 04.stderr.txt  # Bản ghi văn bản 04.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 04.stdout.txt  # Bản ghi văn bản 04.stdout của đợt/tài liệu tương ứng.
│   │   │   │   ├── 05.stderr.txt  # Bản ghi văn bản 05.stderr của đợt/tài liệu tương ứng.
│   │   │   │   ├── 05.stdout.txt  # Bản ghi văn bản 05.stdout của đợt/tài liệu tương ứng.
│   │   │   │   ├── ignore-checks.json  # Biên nhận/cấu hình JSON ignore-checks trong ngữ cảnh docs/release/evidence/git-audit-01.
│   │   │   │   ├── local-checkpoint.json  # Biên nhận/cấu hình JSON local-checkpoint trong ngữ cảnh docs/release/evidence/git-audit-01.
│   │   │   │   └── summary.json  # Biên nhận/cấu hình JSON summary trong ngữ cảnh docs/release/evidence/git-audit-01.
│   │   │   ├── 20261022-proof-command.json  # Biên nhận/cấu hình JSON 20261022-proof-command trong ngữ cảnh docs/release/evidence.
│   │   │   ├── 20261022-proof-replay.json  # Biên nhận/cấu hình JSON 20261022-proof-replay trong ngữ cảnh docs/release/evidence.
│   │   │   ├── clean-source-checkout.json  # Biên nhận/cấu hình JSON clean-source-checkout trong ngữ cảnh docs/release/evidence.
│   │   │   ├── compose-isolation.json  # Biên nhận/cấu hình JSON compose-isolation trong ngữ cảnh docs/release/evidence.
│   │   │   ├── local-data-and-science.json  # Biên nhận/cấu hình JSON local-data-and-science trong ngữ cảnh docs/release/evidence.
│   │   │   ├── research-preservation.json  # Biên nhận/cấu hình JSON research-preservation trong ngữ cảnh docs/release/evidence.
│   │   │   └── tool-installation.json  # Biên nhận/cấu hình JSON tool-installation trong ngữ cảnh docs/release/evidence.
│   │   ├── DEPLOYMENT_VERIFICATION.md  # Tài liệu: Kiểm chứng triển khai MongoDB và Docker Compose.
│   │   └── WINDOWS_LONG_PATH.md  # Tài liệu: Windows long-path root cause and fix.
│   ├── requirements/  # Yêu cầu và tiêu chí của hệ thống.
│   ├── research/  # Mô hình, thiết kế, kế hoạch, trạng thái và đối chiếu nghiên cứu.
│   │   ├── evidence/  # Biên nhận, log và ảnh bằng chứng đã lưu theo từng lượt kiểm chứng; mang tính lịch sử.
│   │   │   ├── 20261021/  # Nhóm bằng chứng 20261021; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   └── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   ├── changed-files.json  # Danh sách thay đổi ghi nhận trong đợt tương ứng.
│   │   │   │   ├── npm-audit.json  # Biên nhận/cấu hình JSON npm-audit trong ngữ cảnh docs/research/evidence/20261021.
│   │   │   │   ├── playwright-axe-results.json  # Biên nhận/cấu hình JSON playwright-axe-results trong ngữ cảnh docs/research/evidence/20261021.
│   │   │   │   ├── playwright-results.json  # Biên nhận/cấu hình JSON playwright-results trong ngữ cảnh docs/research/evidence/20261021.
│   │   │   │   ├── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   │   ├── services-before.json  # Biên nhận/cấu hình JSON services-before trong ngữ cảnh docs/research/evidence/20261021.
│   │   │   │   └── text-preservation.json  # Biên nhận/cấu hình JSON text-preservation trong ngữ cảnh docs/research/evidence/20261021.
│   │   │   ├── 20261022/  # Nhóm bằng chứng 20261022; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-joint-controls-01/  # Nhóm bằng chứng 20261022-joint-controls-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── command.json  # Biên nhận/cấu hình JSON command trong ngữ cảnh docs/research/evidence/20261022-joint-controls-01.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-joint-final-regression/  # Nhóm bằng chứng 20261022-joint-final-regression; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── command.json  # Biên nhận/cấu hình JSON command trong ngữ cảnh docs/research/evidence/20261022-joint-final-regression.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-joint-release-01/  # Nhóm bằng chứng 20261022-joint-release-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-joint-release-02/  # Nhóm bằng chứng 20261022-joint-release-02; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-joint-release-03/  # Nhóm bằng chứng 20261022-joint-release-03; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── joint-exact.png  # Ảnh bằng chứng giao diện/biểu đồ joint-exact thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── joint-feedback.png  # Ảnh bằng chứng giao diện/biểu đồ joint-feedback thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-release-01/  # Nhóm bằng chứng 20261022-release-01; phục vụ đối chiếu lượt kiểm chứng lịch sử tương ứng.
│   │   │   │   ├── browser/  # Bằng chứng trình duyệt của lượt kiểm tra chứa thư mục này.
│   │   │   │   │   ├── test-results/  # Trạng thái/artifact test được lưu cùng bộ bằng chứng này.
│   │   │   │   │   │   └── .last-run.json  # Trạng thái lượt chạy gần nhất được lưu cùng bằng chứng.
│   │   │   │   │   ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│   │   │   │   │   │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│   │   │   │   │   │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   ├── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│   │   │   │   │   │   └── research-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ research-dashboard thuộc bộ tài liệu chứa nó.
│   │   │   │   │   ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│   │   │   │   │   └── results.json  # Kết quả và trạng thái lượt kiểm thử đã lưu.
│   │   │   │   ├── architecture.json  # Biên nhận phân tích import, chu trình và ranh giới module.
│   │   │   │   └── pytest.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
│   │   │   ├── 20261022-closeout.json  # Biên nhận/cấu hình JSON 20261022-closeout trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-data-preservation.json  # Biên nhận/cấu hình JSON 20261022-joint-data-preservation trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-proof-cli-01.json  # Biên nhận/cấu hình JSON 20261022-joint-proof-cli-01 trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-proof-cli-02.json  # Biên nhận/cấu hình JSON 20261022-joint-proof-cli-02 trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-proof-cli-128-02.json  # Biên nhận/cấu hình JSON 20261022-joint-proof-cli-128-02 trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-proof-cli-128.json  # Biên nhận/cấu hình JSON 20261022-joint-proof-cli-128 trong ngữ cảnh docs/research/evidence.
│   │   │   ├── 20261022-joint-readiness-01.json  # Biên nhận/cấu hình JSON 20261022-joint-readiness-01 trong ngữ cảnh docs/research/evidence.
│   │   │   └── 20261022-joint-readiness-02.json  # Biên nhận/cấu hình JSON 20261022-joint-readiness-02 trong ngữ cảnh docs/research/evidence.
│   │   ├── ABLATION_STUDY.md  # Tài liệu: Ablation study.
│   │   ├── ALGORITHM_DESIGN.md  # Tài liệu: Algorithm design.
│   │   ├── BASELINE_COMPARISON.md  # Tài liệu: Baseline comparison.
│   │   ├── CONTINUATION_20261023.md  # Tài liệu: Tiếp tục thực nghiệm bài báo — 23/10/2026.
│   │   ├── DATA_PROVENANCE.md  # Tài liệu: Data provenance.
│   │   ├── Doi_chieu_workflow_va_code_thuc_nghiem_V5.docx  # Tài liệu Word Doi chieu workflow va code thuc nghiem V5; nội dung tham chiếu nghiên cứu, không phải mã thực thi.
│   │   ├── EXPERIMENT_DESIGN_DEEPMG.md  # Tài liệu: Thiết kế thực nghiệm cho bài báo (hướng A, theo phương pháp deepmg).
│   │   ├── HOW_TO_RUN_EXPERIMENTS.md  # Tài liệu: Hướng dẫn chạy thí nghiệm.
│   │   ├── HOW_TO_RUN_JOINT_OPTIMIZATION.md  # Tài liệu: Running joint T1-T4 research.
│   │   ├── JOINT_OPTIMIZATION_ACCEPTANCE.md  # Tài liệu: Joint optimization acceptance.
│   │   ├── JOINT_OPTIMIZATION_FORMULATION.md  # Tài liệu: Joint T1-T4 formulation and proof scope.
│   │   ├── MATHEMATICAL_FORMULATION.md  # Tài liệu: Executed mathematical model.
│   │   ├── OBJECTIVES_AND_HYPOTHESES.md  # Tài liệu: Objectives and hypotheses.
│   │   ├── PAPER_EXPERIMENT_RUNBOOK.md  # Tài liệu: Hướng dẫn chạy thực nghiệm bài báo (hướng A).
│   │   ├── RESEARCH_PROBLEM.md  # Tài liệu: Research problem.
│   │   ├── RESEARCH_STATUS.md  # Tài liệu: Phạm vi và trạng thái nghiên cứu.
│   │   ├── RESULTS_AND_DISCUSSION.md  # Tài liệu: Actual results: 2026-10-21.
│   │   ├── SENSITIVITY_ANALYSIS.md  # Tài liệu: Sensitivity analysis.
│   │   ├── STATISTICAL_ANALYSIS.md  # Tài liệu: Statistical analysis.
│   │   ├── THREATS_TO_VALIDITY.md  # Tài liệu: Threats to validity.
│   │   └── WORKFLOW_REPORT_CODE_MAPPING.md  # Tài liệu: Đối chiếu workflow báo cáo với mã thực nghiệm V5.
│   ├── superpowers/  # Các tài liệu thiết kế/kế hoạch được lưu theo workflow trước đây.
│   │   └── plans/  # Kế hoạch triển khai và thay đổi theo từng đợt.
│   │       └── 2026-11-03-paper-v5-surrogate.md  # Tài liệu: paper-v5: feedback_v5 (surrogate), GA, nhiều seed — kế hoạch cài đặt.
│   ├── system-audit/  # Kết quả audit, tiêu chí nghiệm thu và giới hạn kiểm chứng.
│   │   ├── API_AUDIT.md  # Tài liệu: API validation and surface audit.
│   │   ├── BUG_REPORT.md  # Tài liệu: Bugs, fixes and unsuccessful audit attempts.
│   │   ├── CLOSED_LOOP_VALIDATION.md  # Tài liệu: Closed-loop feedback and recomputation.
│   │   ├── DATA_FLOW.md  # Tài liệu: Data flow and field consumption.
│   │   ├── DATABASE_AUDIT.md  # Tài liệu: MongoDB persistence and isolation.
│   │   ├── END_TO_END_ACCEPTANCE.md  # Tài liệu: End-to-end system acceptance matrix.
│   │   ├── EXACT_SOLVER_VALIDATION.md  # Tài liệu: Finite exact and hybrid solver validation.
│   │   ├── EXPERIMENT_VALIDATION.md  # Tài liệu: Research campaigns, reports and replay.
│   │   ├── FINAL_SYSTEM_AUDIT.md  # Tài liệu: Final system audit.
│   │   ├── PERFORMANCE_REPORT.md  # Tài liệu: Bounded performance and resource observations.
│   │   ├── SYSTEM_ARCHITECTURE.md  # Tài liệu: System architecture audit.
│   │   ├── T1_T2_T3_T4_VALIDATION.md  # Tài liệu: Independent T1 through T4 validation.
│   │   └── WORKER_AUDIT.md  # Tài liệu: Durable queue and worker audit.
│   └── testing/  # Kế hoạch, fixture và bằng chứng kiểm thử đã lưu.
│       ├── ui/  # Ảnh chụp và tệp tải xuống dùng đối chiếu giao diện.
│       │   ├── desktop-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-dashboard thuộc bộ tài liệu chứa nó.
│       │   ├── desktop-editor.png  # Ảnh bằng chứng giao diện/biểu đồ desktop-editor thuộc bộ tài liệu chứa nó.
│       │   ├── downloaded-report.json  # Báo cáo JSON được tải xuống để đối chiếu chức năng xuất.
│       │   ├── evidence.json  # Danh mục hoặc kết quả thu thập bằng chứng.
│       │   ├── mobile-dashboard.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-dashboard thuộc bộ tài liệu chứa nó.
│       │   └── mobile-editor.png  # Ảnh bằng chứng giao diện/biểu đồ mobile-editor thuộc bộ tài liệu chứa nó.
│       ├── axe-results.json  # Kết quả công cụ kiểm tra accessibility trên trang được ghi nhận.
│       ├── cleanup-20261021.json  # Biên nhận/cấu hình JSON cleanup-20261021 trong ngữ cảnh docs/testing.
│       ├── playwright-results.json  # Biên nhận/cấu hình JSON playwright-results trong ngữ cảnh docs/testing.
│       ├── preservation.json  # Biên nhận bảo toàn các tệp trong phạm vi lượt kiểm tra.
│       └── pytest-results.xml  # Báo cáo JUnit XML của pytest trong lượt bằng chứng đã lưu.
├── experiments/  # Thiết kế thực nghiệm, công cụ chạy/phân tích và tài liệu đi kèm.
│   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   ├── configs/  # Manifest/cấu hình thực nghiệm; đây là thiết kế, không phải kết quả đã chạy.
│   │   ├── paper/  # Bộ cấu hình paper; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-x1-exact.json  # Thiết kế campaign paper-x1-exact: E17; 1 dataset, 30 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small.json  # Thiết kế campaign paper-x2-small: E18; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part01.json  # Thiết kế campaign paper-x2-tiny-part01: E18; 2 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part02.json  # Thiết kế campaign paper-x2-tiny-part02: E18; 1 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-medium.json  # Thiết kế campaign paper-x2b-medium: E19; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-small.json  # Thiết kế campaign paper-x2b-small: E19; 10 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-tiny.json  # Thiết kế campaign paper-x2b-tiny: E19; 10 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small.json  # Thiết kế campaign paper-x3-small: E20; 5 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny.json  # Thiết kế campaign paper-x3-tiny: E20; 5 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-large.json  # Thiết kế campaign paper-x4-large: E21; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium.json  # Thiết kế campaign paper-x4-medium: E21; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-small.json  # Thiết kế campaign paper-x4-small: E21; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-tiny.json  # Thiết kế campaign paper-x4-tiny: E21; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation.json  # Thiết kế campaign paper-x5-ablation: E22; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-sensitivity-1.json  # Thiết kế campaign paper-x6-sensitivity-1: E23, E24, E25, E26, E27, E28; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-x6-sensitivity-2.json  # Thiết kế campaign paper-x6-sensitivity-2: E29, E30, E31, E32, E33, E34; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v2/  # Bộ cấu hình paper-v2; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-x1-exact.json  # Thiết kế campaign paper-x1-exact: E17; 1 dataset, 30 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small.json  # Thiết kế campaign paper-x2-small: E18; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part01.json  # Thiết kế campaign paper-x2-tiny-part01: E18; 2 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part02.json  # Thiết kế campaign paper-x2-tiny-part02: E18; 1 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-medium-part01.json  # Thiết kế campaign paper-x2b-medium-part01: E19; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-medium-part02.json  # Thiết kế campaign paper-x2b-medium-part02: E19; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-medium-part03.json  # Thiết kế campaign paper-x2b-medium-part03: E19; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-small.json  # Thiết kế campaign paper-x2b-small: E19; 10 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2b-tiny.json  # Thiết kế campaign paper-x2b-tiny: E19; 10 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small.json  # Thiết kế campaign paper-x3-small: E20; 5 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny.json  # Thiết kế campaign paper-x3-tiny: E20; 5 dataset, 10 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-large.json  # Thiết kế campaign paper-x4-large: E21; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium-part01.json  # Thiết kế campaign paper-x4-medium-part01: E21; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium-part02.json  # Thiết kế campaign paper-x4-medium-part02: E21; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium-part03.json  # Thiết kế campaign paper-x4-medium-part03: E21; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-small.json  # Thiết kế campaign paper-x4-small: E21; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-tiny.json  # Thiết kế campaign paper-x4-tiny: E21; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation.json  # Thiết kế campaign paper-x5-ablation: E22; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-sensitivity-1.json  # Thiết kế campaign paper-x6-sensitivity-1: E23, E24, E25, E26, E27, E28; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-x6-sensitivity-2.json  # Thiết kế campaign paper-x6-sensitivity-2: E29, E30, E31, E32, E33, E34; 3 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v3/  # Bộ cấu hình paper-v3; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── calibration.json  # Cấu hình/manifest calibration của bộ thiết kế thực nghiệm này.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-x1-tiny-part01.json  # Thiết kế campaign paper-x1-tiny-part01: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-part02.json  # Thiết kế campaign paper-x1-tiny-part02: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-trap.json  # Thiết kế campaign paper-x1-trap: E17; 1 dataset, 30 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part01.json  # Thiết kế campaign paper-x2-medium-part01: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part02.json  # Thiết kế campaign paper-x2-medium-part02: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part01.json  # Thiết kế campaign paper-x2-small-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part02.json  # Thiết kế campaign paper-x2-small-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part03.json  # Thiết kế campaign paper-x2-small-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part04.json  # Thiết kế campaign paper-x2-small-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part05.json  # Thiết kế campaign paper-x2-small-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part06.json  # Thiết kế campaign paper-x2-small-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part07.json  # Thiết kế campaign paper-x2-small-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part08.json  # Thiết kế campaign paper-x2-small-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part09.json  # Thiết kế campaign paper-x2-small-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part10.json  # Thiết kế campaign paper-x2-small-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part01.json  # Thiết kế campaign paper-x2-tiny-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part02.json  # Thiết kế campaign paper-x2-tiny-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part03.json  # Thiết kế campaign paper-x2-tiny-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part04.json  # Thiết kế campaign paper-x2-tiny-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part05.json  # Thiết kế campaign paper-x2-tiny-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part06.json  # Thiết kế campaign paper-x2-tiny-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part07.json  # Thiết kế campaign paper-x2-tiny-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part08.json  # Thiết kế campaign paper-x2-tiny-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part09.json  # Thiết kế campaign paper-x2-tiny-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part10.json  # Thiết kế campaign paper-x2-tiny-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part11.json  # Thiết kế campaign paper-x2-tiny-part11: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part12.json  # Thiết kế campaign paper-x2-tiny-part12: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part13.json  # Thiết kế campaign paper-x2-tiny-part13: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part14.json  # Thiết kế campaign paper-x2-tiny-part14: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part15.json  # Thiết kế campaign paper-x2-tiny-part15: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part16.json  # Thiết kế campaign paper-x2-tiny-part16: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part17.json  # Thiết kế campaign paper-x2-tiny-part17: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part18.json  # Thiết kế campaign paper-x2-tiny-part18: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part19.json  # Thiết kế campaign paper-x2-tiny-part19: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part20.json  # Thiết kế campaign paper-x2-tiny-part20: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part01.json  # Thiết kế campaign paper-x3-small-part01: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part02.json  # Thiết kế campaign paper-x3-small-part02: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part01.json  # Thiết kế campaign paper-x3-tiny-part01: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part02.json  # Thiết kế campaign paper-x3-tiny-part02: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part03.json  # Thiết kế campaign paper-x3-tiny-part03: E20; 2 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-large.json  # Thiết kế campaign paper-x4-large: E21; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium.json  # Thiết kế campaign paper-x4-medium: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-small.json  # Thiết kế campaign paper-x4-small: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-tiny.json  # Thiết kế campaign paper-x4-tiny: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part01.json  # Thiết kế campaign paper-x5-ablation-part01: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part02.json  # Thiết kế campaign paper-x5-ablation-part02: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part03.json  # Thiết kế campaign paper-x5-ablation-part03: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part04.json  # Thiết kế campaign paper-x5-ablation-part04: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part05.json  # Thiết kế campaign paper-x5-ablation-part05: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part01.json  # Thiết kế campaign paper-x6-demand-part01: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part02.json  # Thiết kế campaign paper-x6-demand-part02: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part03.json  # Thiết kế campaign paper-x6-demand-part03: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part04.json  # Thiết kế campaign paper-x6-demand-part04: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part05.json  # Thiết kế campaign paper-x6-demand-part05: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-x6-load.json  # Thiết kế campaign paper-x6-load: E32, E33; 10 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v3-unlimited-20261026/  # Bộ cấu hình paper-v3-unlimited-20261026; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── calibration.json  # Cấu hình/manifest calibration của bộ thiết kế thực nghiệm này.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-x1-tiny-part01.json  # Thiết kế campaign paper-x1-tiny-part01: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-part02.json  # Thiết kế campaign paper-x1-tiny-part02: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-trap.json  # Thiết kế campaign paper-x1-trap: E17; 1 dataset, 30 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part01.json  # Thiết kế campaign paper-x2-medium-part01: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part02.json  # Thiết kế campaign paper-x2-medium-part02: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part01.json  # Thiết kế campaign paper-x2-small-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part02.json  # Thiết kế campaign paper-x2-small-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part03.json  # Thiết kế campaign paper-x2-small-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part04.json  # Thiết kế campaign paper-x2-small-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part05.json  # Thiết kế campaign paper-x2-small-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part06.json  # Thiết kế campaign paper-x2-small-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part07.json  # Thiết kế campaign paper-x2-small-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part08.json  # Thiết kế campaign paper-x2-small-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part09.json  # Thiết kế campaign paper-x2-small-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part10.json  # Thiết kế campaign paper-x2-small-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part01.json  # Thiết kế campaign paper-x2-tiny-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part02.json  # Thiết kế campaign paper-x2-tiny-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part03.json  # Thiết kế campaign paper-x2-tiny-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part04.json  # Thiết kế campaign paper-x2-tiny-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part05.json  # Thiết kế campaign paper-x2-tiny-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part06.json  # Thiết kế campaign paper-x2-tiny-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part07.json  # Thiết kế campaign paper-x2-tiny-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part08.json  # Thiết kế campaign paper-x2-tiny-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part09.json  # Thiết kế campaign paper-x2-tiny-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part10.json  # Thiết kế campaign paper-x2-tiny-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part11.json  # Thiết kế campaign paper-x2-tiny-part11: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part12.json  # Thiết kế campaign paper-x2-tiny-part12: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part13.json  # Thiết kế campaign paper-x2-tiny-part13: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part14.json  # Thiết kế campaign paper-x2-tiny-part14: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part15.json  # Thiết kế campaign paper-x2-tiny-part15: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part16.json  # Thiết kế campaign paper-x2-tiny-part16: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part17.json  # Thiết kế campaign paper-x2-tiny-part17: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part18.json  # Thiết kế campaign paper-x2-tiny-part18: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part19.json  # Thiết kế campaign paper-x2-tiny-part19: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part20.json  # Thiết kế campaign paper-x2-tiny-part20: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part01.json  # Thiết kế campaign paper-x3-small-part01: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part02.json  # Thiết kế campaign paper-x3-small-part02: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part01.json  # Thiết kế campaign paper-x3-tiny-part01: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part02.json  # Thiết kế campaign paper-x3-tiny-part02: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part03.json  # Thiết kế campaign paper-x3-tiny-part03: E20; 2 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-large.json  # Thiết kế campaign paper-x4-large: E21; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium.json  # Thiết kế campaign paper-x4-medium: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-small.json  # Thiết kế campaign paper-x4-small: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-tiny.json  # Thiết kế campaign paper-x4-tiny: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part01.json  # Thiết kế campaign paper-x5-ablation-part01: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part02.json  # Thiết kế campaign paper-x5-ablation-part02: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part03.json  # Thiết kế campaign paper-x5-ablation-part03: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part04.json  # Thiết kế campaign paper-x5-ablation-part04: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part05.json  # Thiết kế campaign paper-x5-ablation-part05: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part01.json  # Thiết kế campaign paper-x6-demand-part01: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part02.json  # Thiết kế campaign paper-x6-demand-part02: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part03.json  # Thiết kế campaign paper-x6-demand-part03: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part04.json  # Thiết kế campaign paper-x6-demand-part04: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part05.json  # Thiết kế campaign paper-x6-demand-part05: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-x6-load.json  # Thiết kế campaign paper-x6-load: E32, E33; 10 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v3-unlimited-time2-20261026/  # Bộ cấu hình paper-v3-unlimited-time2-20261026; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── calibration.json  # Cấu hình/manifest calibration của bộ thiết kế thực nghiệm này.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5001.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5001: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5002.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5002: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5003.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5003: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5004.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5004: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5005.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5005: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5006.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5006: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5007.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5007: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5008.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5008: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5009.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5009: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-exact-tiny_f6_s5010.json  # Thiết kế campaign paper-x1-tiny-exact-tiny_f6_s5010: E41; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-part01.json  # Thiết kế campaign paper-x1-tiny-part01: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-tiny-part02.json  # Thiết kế campaign paper-x1-tiny-part02: E41; 5 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x1-trap.json  # Thiết kế campaign paper-x1-trap: E17; 1 dataset, 30 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part01.json  # Thiết kế campaign paper-x2-medium-part01: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-medium-part02.json  # Thiết kế campaign paper-x2-medium-part02: E19; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part01.json  # Thiết kế campaign paper-x2-small-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part02.json  # Thiết kế campaign paper-x2-small-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part03.json  # Thiết kế campaign paper-x2-small-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part04.json  # Thiết kế campaign paper-x2-small-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part05.json  # Thiết kế campaign paper-x2-small-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part06.json  # Thiết kế campaign paper-x2-small-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part07.json  # Thiết kế campaign paper-x2-small-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part08.json  # Thiết kế campaign paper-x2-small-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part09.json  # Thiết kế campaign paper-x2-small-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-small-part10.json  # Thiết kế campaign paper-x2-small-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part01.json  # Thiết kế campaign paper-x2-tiny-part01: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part02.json  # Thiết kế campaign paper-x2-tiny-part02: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part03.json  # Thiết kế campaign paper-x2-tiny-part03: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part04.json  # Thiết kế campaign paper-x2-tiny-part04: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part05.json  # Thiết kế campaign paper-x2-tiny-part05: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part06.json  # Thiết kế campaign paper-x2-tiny-part06: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part07.json  # Thiết kế campaign paper-x2-tiny-part07: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part08.json  # Thiết kế campaign paper-x2-tiny-part08: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part09.json  # Thiết kế campaign paper-x2-tiny-part09: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part10.json  # Thiết kế campaign paper-x2-tiny-part10: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part11.json  # Thiết kế campaign paper-x2-tiny-part11: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part12.json  # Thiết kế campaign paper-x2-tiny-part12: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part13.json  # Thiết kế campaign paper-x2-tiny-part13: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part14.json  # Thiết kế campaign paper-x2-tiny-part14: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part15.json  # Thiết kế campaign paper-x2-tiny-part15: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part16.json  # Thiết kế campaign paper-x2-tiny-part16: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part17.json  # Thiết kế campaign paper-x2-tiny-part17: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part18.json  # Thiết kế campaign paper-x2-tiny-part18: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part19.json  # Thiết kế campaign paper-x2-tiny-part19: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x2-tiny-part20.json  # Thiết kế campaign paper-x2-tiny-part20: E18; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part01.json  # Thiết kế campaign paper-x3-small-part01: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-small-part02.json  # Thiết kế campaign paper-x3-small-part02: E20; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part01.json  # Thiết kế campaign paper-x3-tiny-part01: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part02.json  # Thiết kế campaign paper-x3-tiny-part02: E20; 4 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x3-tiny-part03.json  # Thiết kế campaign paper-x3-tiny-part03: E20; 2 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-large.json  # Thiết kế campaign paper-x4-large: E21; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-medium.json  # Thiết kế campaign paper-x4-medium: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-small.json  # Thiết kế campaign paper-x4-small: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x4-tiny.json  # Thiết kế campaign paper-x4-tiny: E21; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part01.json  # Thiết kế campaign paper-x5-ablation-part01: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part02.json  # Thiết kế campaign paper-x5-ablation-part02: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part03.json  # Thiết kế campaign paper-x5-ablation-part03: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part04.json  # Thiết kế campaign paper-x5-ablation-part04: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x5-ablation-part05.json  # Thiết kế campaign paper-x5-ablation-part05: E22; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part01.json  # Thiết kế campaign paper-x6-demand-part01: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part02.json  # Thiết kế campaign paper-x6-demand-part02: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part03.json  # Thiết kế campaign paper-x6-demand-part03: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part04.json  # Thiết kế campaign paper-x6-demand-part04: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-x6-demand-part05.json  # Thiết kế campaign paper-x6-demand-part05: E23, E24, E25, E26, E27, E28, E29, E30, E31; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-x6-load.json  # Thiết kế campaign paper-x6-load: E32, E33; 10 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v4/  # Bộ cấu hình paper-v4; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-v4-v1-medium-part01.json  # Thiết kế campaign paper-v4-v1-medium-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part02.json  # Thiết kế campaign paper-v4-v1-medium-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part03.json  # Thiết kế campaign paper-v4-v1-medium-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part04.json  # Thiết kế campaign paper-v4-v1-medium-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part05.json  # Thiết kế campaign paper-v4-v1-medium-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part06.json  # Thiết kế campaign paper-v4-v1-medium-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part07.json  # Thiết kế campaign paper-v4-v1-medium-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part08.json  # Thiết kế campaign paper-v4-v1-medium-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part09.json  # Thiết kế campaign paper-v4-v1-medium-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part10.json  # Thiết kế campaign paper-v4-v1-medium-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part01.json  # Thiết kế campaign paper-v4-v1-small-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part02.json  # Thiết kế campaign paper-v4-v1-small-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part03.json  # Thiết kế campaign paper-v4-v1-small-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part04.json  # Thiết kế campaign paper-v4-v1-small-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part05.json  # Thiết kế campaign paper-v4-v1-small-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part06.json  # Thiết kế campaign paper-v4-v1-small-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part07.json  # Thiết kế campaign paper-v4-v1-small-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part08.json  # Thiết kế campaign paper-v4-v1-small-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part09.json  # Thiết kế campaign paper-v4-v1-small-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part10.json  # Thiết kế campaign paper-v4-v1-small-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part01.json  # Thiết kế campaign paper-v4-v1-tiny-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part02.json  # Thiết kế campaign paper-v4-v1-tiny-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part03.json  # Thiết kế campaign paper-v4-v1-tiny-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part04.json  # Thiết kế campaign paper-v4-v1-tiny-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part05.json  # Thiết kế campaign paper-v4-v1-tiny-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part06.json  # Thiết kế campaign paper-v4-v1-tiny-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part07.json  # Thiết kế campaign paper-v4-v1-tiny-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part08.json  # Thiết kế campaign paper-v4-v1-tiny-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part09.json  # Thiết kế campaign paper-v4-v1-tiny-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part10.json  # Thiết kế campaign paper-v4-v1-tiny-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part11.json  # Thiết kế campaign paper-v4-v1-tiny-part11: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part12.json  # Thiết kế campaign paper-v4-v1-tiny-part12: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part13.json  # Thiết kế campaign paper-v4-v1-tiny-part13: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part14.json  # Thiết kế campaign paper-v4-v1-tiny-part14: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part15.json  # Thiết kế campaign paper-v4-v1-tiny-part15: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part16.json  # Thiết kế campaign paper-v4-v1-tiny-part16: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part17.json  # Thiết kế campaign paper-v4-v1-tiny-part17: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part18.json  # Thiết kế campaign paper-v4-v1-tiny-part18: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part19.json  # Thiết kế campaign paper-v4-v1-tiny-part19: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part20.json  # Thiết kế campaign paper-v4-v1-tiny-part20: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part01.json  # Thiết kế campaign paper-v4-v2-step-guidance-part01: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part02.json  # Thiết kế campaign paper-v4-v2-step-guidance-part02: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part03.json  # Thiết kế campaign paper-v4-v2-step-guidance-part03: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part04.json  # Thiết kế campaign paper-v4-v2-step-guidance-part04: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part05.json  # Thiết kế campaign paper-v4-v2-step-guidance-part05: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part06.json  # Thiết kế campaign paper-v4-v2-step-guidance-part06: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part07.json  # Thiết kế campaign paper-v4-v2-step-guidance-part07: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part08.json  # Thiết kế campaign paper-v4-v2-step-guidance-part08: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part09.json  # Thiết kế campaign paper-v4-v2-step-guidance-part09: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part10.json  # Thiết kế campaign paper-v4-v2-step-guidance-part10: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part01.json  # Thiết kế campaign paper-v4-v3-budget-part01: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part02.json  # Thiết kế campaign paper-v4-v3-budget-part02: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part03.json  # Thiết kế campaign paper-v4-v3-budget-part03: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part04.json  # Thiết kế campaign paper-v4-v3-budget-part04: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part05.json  # Thiết kế campaign paper-v4-v3-budget-part05: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part06.json  # Thiết kế campaign paper-v4-v3-budget-part06: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part07.json  # Thiết kế campaign paper-v4-v3-budget-part07: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part08.json  # Thiết kế campaign paper-v4-v3-budget-part08: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part09.json  # Thiết kế campaign paper-v4-v3-budget-part09: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part10.json  # Thiết kế campaign paper-v4-v3-budget-part10: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part01.json  # Thiết kế campaign paper-v4-v4-ablation-part01: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part02.json  # Thiết kế campaign paper-v4-v4-ablation-part02: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part03.json  # Thiết kế campaign paper-v4-v4-ablation-part03: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part04.json  # Thiết kế campaign paper-v4-v4-ablation-part04: E54; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part01.json  # Thiết kế campaign paper-v4-v5-screening-part01: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part02.json  # Thiết kế campaign paper-v4-v5-screening-part02: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part03.json  # Thiết kế campaign paper-v4-v5-screening-part03: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part04.json  # Thiết kế campaign paper-v4-v5-screening-part04: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part05.json  # Thiết kế campaign paper-v4-v5-screening-part05: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part06.json  # Thiết kế campaign paper-v4-v5-screening-part06: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part07.json  # Thiết kế campaign paper-v4-v5-screening-part07: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part08.json  # Thiết kế campaign paper-v4-v5-screening-part08: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part09.json  # Thiết kế campaign paper-v4-v5-screening-part09: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part10.json  # Thiết kế campaign paper-v4-v5-screening-part10: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-vl-large-part01.json  # Thiết kế campaign paper-v4-vl-large-part01: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-vl-large-part02.json  # Thiết kế campaign paper-v4-vl-large-part02: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-v4-vl-large-part03.json  # Thiết kế campaign paper-v4-vl-large-part03: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v4-unlimited-adaptive-20261028/  # Bộ cấu hình paper-v4-unlimited-adaptive-20261028; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-v4-v1-medium-part01.json  # Thiết kế campaign paper-v4-v1-medium-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part02.json  # Thiết kế campaign paper-v4-v1-medium-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part03.json  # Thiết kế campaign paper-v4-v1-medium-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part04.json  # Thiết kế campaign paper-v4-v1-medium-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part05.json  # Thiết kế campaign paper-v4-v1-medium-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part06.json  # Thiết kế campaign paper-v4-v1-medium-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part07.json  # Thiết kế campaign paper-v4-v1-medium-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part08.json  # Thiết kế campaign paper-v4-v1-medium-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part09.json  # Thiết kế campaign paper-v4-v1-medium-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-medium-part10.json  # Thiết kế campaign paper-v4-v1-medium-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part01.json  # Thiết kế campaign paper-v4-v1-small-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part02.json  # Thiết kế campaign paper-v4-v1-small-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part03.json  # Thiết kế campaign paper-v4-v1-small-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part04.json  # Thiết kế campaign paper-v4-v1-small-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part05.json  # Thiết kế campaign paper-v4-v1-small-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part06.json  # Thiết kế campaign paper-v4-v1-small-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part07.json  # Thiết kế campaign paper-v4-v1-small-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part08.json  # Thiết kế campaign paper-v4-v1-small-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part09.json  # Thiết kế campaign paper-v4-v1-small-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-small-part10.json  # Thiết kế campaign paper-v4-v1-small-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part01.json  # Thiết kế campaign paper-v4-v1-tiny-part01: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part02.json  # Thiết kế campaign paper-v4-v1-tiny-part02: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part03.json  # Thiết kế campaign paper-v4-v1-tiny-part03: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part04.json  # Thiết kế campaign paper-v4-v1-tiny-part04: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part05.json  # Thiết kế campaign paper-v4-v1-tiny-part05: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part06.json  # Thiết kế campaign paper-v4-v1-tiny-part06: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part07.json  # Thiết kế campaign paper-v4-v1-tiny-part07: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part08.json  # Thiết kế campaign paper-v4-v1-tiny-part08: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part09.json  # Thiết kế campaign paper-v4-v1-tiny-part09: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part10.json  # Thiết kế campaign paper-v4-v1-tiny-part10: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part11.json  # Thiết kế campaign paper-v4-v1-tiny-part11: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part12.json  # Thiết kế campaign paper-v4-v1-tiny-part12: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part13.json  # Thiết kế campaign paper-v4-v1-tiny-part13: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part14.json  # Thiết kế campaign paper-v4-v1-tiny-part14: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part15.json  # Thiết kế campaign paper-v4-v1-tiny-part15: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part16.json  # Thiết kế campaign paper-v4-v1-tiny-part16: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part17.json  # Thiết kế campaign paper-v4-v1-tiny-part17: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part18.json  # Thiết kế campaign paper-v4-v1-tiny-part18: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part19.json  # Thiết kế campaign paper-v4-v1-tiny-part19: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v1-tiny-part20.json  # Thiết kế campaign paper-v4-v1-tiny-part20: E51; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part01.json  # Thiết kế campaign paper-v4-v2-step-guidance-part01: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part02.json  # Thiết kế campaign paper-v4-v2-step-guidance-part02: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part03.json  # Thiết kế campaign paper-v4-v2-step-guidance-part03: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part04.json  # Thiết kế campaign paper-v4-v2-step-guidance-part04: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part05.json  # Thiết kế campaign paper-v4-v2-step-guidance-part05: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part06.json  # Thiết kế campaign paper-v4-v2-step-guidance-part06: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part07.json  # Thiết kế campaign paper-v4-v2-step-guidance-part07: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part08.json  # Thiết kế campaign paper-v4-v2-step-guidance-part08: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part09.json  # Thiết kế campaign paper-v4-v2-step-guidance-part09: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v2-step-guidance-part10.json  # Thiết kế campaign paper-v4-v2-step-guidance-part10: E52; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part01.json  # Thiết kế campaign paper-v4-v3-budget-part01: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part02.json  # Thiết kế campaign paper-v4-v3-budget-part02: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part03.json  # Thiết kế campaign paper-v4-v3-budget-part03: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part04.json  # Thiết kế campaign paper-v4-v3-budget-part04: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part05.json  # Thiết kế campaign paper-v4-v3-budget-part05: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part06.json  # Thiết kế campaign paper-v4-v3-budget-part06: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part07.json  # Thiết kế campaign paper-v4-v3-budget-part07: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part08.json  # Thiết kế campaign paper-v4-v3-budget-part08: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part09.json  # Thiết kế campaign paper-v4-v3-budget-part09: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v3-budget-part10.json  # Thiết kế campaign paper-v4-v3-budget-part10: E53; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part01.json  # Thiết kế campaign paper-v4-v4-ablation-part01: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part02.json  # Thiết kế campaign paper-v4-v4-ablation-part02: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part03.json  # Thiết kế campaign paper-v4-v4-ablation-part03: E54; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v4-ablation-part04.json  # Thiết kế campaign paper-v4-v4-ablation-part04: E54; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part01.json  # Thiết kế campaign paper-v4-v5-screening-part01: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part02.json  # Thiết kế campaign paper-v4-v5-screening-part02: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part03.json  # Thiết kế campaign paper-v4-v5-screening-part03: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part04.json  # Thiết kế campaign paper-v4-v5-screening-part04: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part05.json  # Thiết kế campaign paper-v4-v5-screening-part05: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part06.json  # Thiết kế campaign paper-v4-v5-screening-part06: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part07.json  # Thiết kế campaign paper-v4-v5-screening-part07: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part08.json  # Thiết kế campaign paper-v4-v5-screening-part08: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part09.json  # Thiết kế campaign paper-v4-v5-screening-part09: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-v5-screening-part10.json  # Thiết kế campaign paper-v4-v5-screening-part10: E56; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-vl-large-part01.json  # Thiết kế campaign paper-v4-vl-large-part01: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v4-vl-large-part02.json  # Thiết kế campaign paper-v4-vl-large-part02: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-v4-vl-large-part03.json  # Thiết kế campaign paper-v4-vl-large-part03: E55; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v5/  # Bộ cấu hình paper-v5; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các phần campaign Paper V5 và khối thực nghiệm được khai báo.
│   │   │   ├── paper-v5-w1-medium-part01.json  # Thiết kế campaign paper-v5-w1-medium-part01: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part02.json  # Thiết kế campaign paper-v5-w1-medium-part02: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part03.json  # Thiết kế campaign paper-v5-w1-medium-part03: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part04.json  # Thiết kế campaign paper-v5-w1-medium-part04: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part05.json  # Thiết kế campaign paper-v5-w1-medium-part05: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part06.json  # Thiết kế campaign paper-v5-w1-medium-part06: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part07.json  # Thiết kế campaign paper-v5-w1-medium-part07: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part08.json  # Thiết kế campaign paper-v5-w1-medium-part08: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part09.json  # Thiết kế campaign paper-v5-w1-medium-part09: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part10.json  # Thiết kế campaign paper-v5-w1-medium-part10: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part11.json  # Thiết kế campaign paper-v5-w1-medium-part11: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part12.json  # Thiết kế campaign paper-v5-w1-medium-part12: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part13.json  # Thiết kế campaign paper-v5-w1-medium-part13: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part14.json  # Thiết kế campaign paper-v5-w1-medium-part14: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part15.json  # Thiết kế campaign paper-v5-w1-medium-part15: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part16.json  # Thiết kế campaign paper-v5-w1-medium-part16: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part17.json  # Thiết kế campaign paper-v5-w1-medium-part17: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part18.json  # Thiết kế campaign paper-v5-w1-medium-part18: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part19.json  # Thiết kế campaign paper-v5-w1-medium-part19: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part20.json  # Thiết kế campaign paper-v5-w1-medium-part20: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part21.json  # Thiết kế campaign paper-v5-w1-medium-part21: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part22.json  # Thiết kế campaign paper-v5-w1-medium-part22: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part23.json  # Thiết kế campaign paper-v5-w1-medium-part23: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part24.json  # Thiết kế campaign paper-v5-w1-medium-part24: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part01.json  # Thiết kế campaign paper-v5-w1-small-part01: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part02.json  # Thiết kế campaign paper-v5-w1-small-part02: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part03.json  # Thiết kế campaign paper-v5-w1-small-part03: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part04.json  # Thiết kế campaign paper-v5-w1-small-part04: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part05.json  # Thiết kế campaign paper-v5-w1-small-part05: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part06.json  # Thiết kế campaign paper-v5-w1-small-part06: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part07.json  # Thiết kế campaign paper-v5-w1-small-part07: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part08.json  # Thiết kế campaign paper-v5-w1-small-part08: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part09.json  # Thiết kế campaign paper-v5-w1-small-part09: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part10.json  # Thiết kế campaign paper-v5-w1-small-part10: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part11.json  # Thiết kế campaign paper-v5-w1-small-part11: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part12.json  # Thiết kế campaign paper-v5-w1-small-part12: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part13.json  # Thiết kế campaign paper-v5-w1-small-part13: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part14.json  # Thiết kế campaign paper-v5-w1-small-part14: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part15.json  # Thiết kế campaign paper-v5-w1-small-part15: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part16.json  # Thiết kế campaign paper-v5-w1-small-part16: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part17.json  # Thiết kế campaign paper-v5-w1-small-part17: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part18.json  # Thiết kế campaign paper-v5-w1-small-part18: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part19.json  # Thiết kế campaign paper-v5-w1-small-part19: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part20.json  # Thiết kế campaign paper-v5-w1-small-part20: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part21.json  # Thiết kế campaign paper-v5-w1-small-part21: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part22.json  # Thiết kế campaign paper-v5-w1-small-part22: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part23.json  # Thiết kế campaign paper-v5-w1-small-part23: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part24.json  # Thiết kế campaign paper-v5-w1-small-part24: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part01.json  # Thiết kế campaign paper-v5-w1-tiny-part01: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part02.json  # Thiết kế campaign paper-v5-w1-tiny-part02: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part03.json  # Thiết kế campaign paper-v5-w1-tiny-part03: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part04.json  # Thiết kế campaign paper-v5-w1-tiny-part04: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part05.json  # Thiết kế campaign paper-v5-w1-tiny-part05: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part06.json  # Thiết kế campaign paper-v5-w1-tiny-part06: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part07.json  # Thiết kế campaign paper-v5-w1-tiny-part07: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part08.json  # Thiết kế campaign paper-v5-w1-tiny-part08: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part09.json  # Thiết kế campaign paper-v5-w1-tiny-part09: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part10.json  # Thiết kế campaign paper-v5-w1-tiny-part10: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part11.json  # Thiết kế campaign paper-v5-w1-tiny-part11: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part12.json  # Thiết kế campaign paper-v5-w1-tiny-part12: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part01.json  # Thiết kế campaign paper-v5-w2-ablation-part01: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part02.json  # Thiết kế campaign paper-v5-w2-ablation-part02: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part03.json  # Thiết kế campaign paper-v5-w2-ablation-part03: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part04.json  # Thiết kế campaign paper-v5-w2-ablation-part04: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part05.json  # Thiết kế campaign paper-v5-w2-ablation-part05: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part06.json  # Thiết kế campaign paper-v5-w2-ablation-part06: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part07.json  # Thiết kế campaign paper-v5-w2-ablation-part07: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-v5-w2-ablation-part08.json  # Thiết kế campaign paper-v5-w2-ablation-part08: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── paper-v5-unlimited-parallel-20261110/  # Bộ cấu hình paper-v5-unlimited-parallel-20261110; các file con khai báo từng campaign/miền đối chứng.
│   │   │   ├── index.json  # Chỉ mục các campaign/phần thực nghiệm trong bộ cấu hình này; không phải tiến độ thực thi.
│   │   │   ├── paper-v5-w1-medium-part01.json  # Thiết kế campaign paper-v5-w1-medium-part01: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part02.json  # Thiết kế campaign paper-v5-w1-medium-part02: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part03.json  # Thiết kế campaign paper-v5-w1-medium-part03: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part04.json  # Thiết kế campaign paper-v5-w1-medium-part04: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part05.json  # Thiết kế campaign paper-v5-w1-medium-part05: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part06.json  # Thiết kế campaign paper-v5-w1-medium-part06: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part07.json  # Thiết kế campaign paper-v5-w1-medium-part07: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part08.json  # Thiết kế campaign paper-v5-w1-medium-part08: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part09.json  # Thiết kế campaign paper-v5-w1-medium-part09: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part10.json  # Thiết kế campaign paper-v5-w1-medium-part10: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part11.json  # Thiết kế campaign paper-v5-w1-medium-part11: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part12.json  # Thiết kế campaign paper-v5-w1-medium-part12: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part13.json  # Thiết kế campaign paper-v5-w1-medium-part13: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part14.json  # Thiết kế campaign paper-v5-w1-medium-part14: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part15.json  # Thiết kế campaign paper-v5-w1-medium-part15: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part16.json  # Thiết kế campaign paper-v5-w1-medium-part16: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part17.json  # Thiết kế campaign paper-v5-w1-medium-part17: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part18.json  # Thiết kế campaign paper-v5-w1-medium-part18: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part19.json  # Thiết kế campaign paper-v5-w1-medium-part19: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part20.json  # Thiết kế campaign paper-v5-w1-medium-part20: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part21.json  # Thiết kế campaign paper-v5-w1-medium-part21: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part22.json  # Thiết kế campaign paper-v5-w1-medium-part22: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part23.json  # Thiết kế campaign paper-v5-w1-medium-part23: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-medium-part24.json  # Thiết kế campaign paper-v5-w1-medium-part24: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part01.json  # Thiết kế campaign paper-v5-w1-small-part01: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part02.json  # Thiết kế campaign paper-v5-w1-small-part02: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part03.json  # Thiết kế campaign paper-v5-w1-small-part03: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part04.json  # Thiết kế campaign paper-v5-w1-small-part04: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part05.json  # Thiết kế campaign paper-v5-w1-small-part05: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part06.json  # Thiết kế campaign paper-v5-w1-small-part06: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part07.json  # Thiết kế campaign paper-v5-w1-small-part07: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part08.json  # Thiết kế campaign paper-v5-w1-small-part08: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part09.json  # Thiết kế campaign paper-v5-w1-small-part09: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part10.json  # Thiết kế campaign paper-v5-w1-small-part10: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part11.json  # Thiết kế campaign paper-v5-w1-small-part11: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part12.json  # Thiết kế campaign paper-v5-w1-small-part12: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part13.json  # Thiết kế campaign paper-v5-w1-small-part13: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part14.json  # Thiết kế campaign paper-v5-w1-small-part14: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part15.json  # Thiết kế campaign paper-v5-w1-small-part15: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part16.json  # Thiết kế campaign paper-v5-w1-small-part16: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part17.json  # Thiết kế campaign paper-v5-w1-small-part17: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part18.json  # Thiết kế campaign paper-v5-w1-small-part18: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part19.json  # Thiết kế campaign paper-v5-w1-small-part19: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part20.json  # Thiết kế campaign paper-v5-w1-small-part20: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part21.json  # Thiết kế campaign paper-v5-w1-small-part21: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part22.json  # Thiết kế campaign paper-v5-w1-small-part22: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part23.json  # Thiết kế campaign paper-v5-w1-small-part23: E61; 1 dataset, 4 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-small-part24.json  # Thiết kế campaign paper-v5-w1-small-part24: E61; 1 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part01.json  # Thiết kế campaign paper-v5-w1-tiny-part01: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part02.json  # Thiết kế campaign paper-v5-w1-tiny-part02: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part03.json  # Thiết kế campaign paper-v5-w1-tiny-part03: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part04.json  # Thiết kế campaign paper-v5-w1-tiny-part04: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part05.json  # Thiết kế campaign paper-v5-w1-tiny-part05: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part06.json  # Thiết kế campaign paper-v5-w1-tiny-part06: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part07.json  # Thiết kế campaign paper-v5-w1-tiny-part07: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part08.json  # Thiết kế campaign paper-v5-w1-tiny-part08: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part09.json  # Thiết kế campaign paper-v5-w1-tiny-part09: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part10.json  # Thiết kế campaign paper-v5-w1-tiny-part10: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part11.json  # Thiết kế campaign paper-v5-w1-tiny-part11: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w1-tiny-part12.json  # Thiết kế campaign paper-v5-w1-tiny-part12: E61; 1 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part01.json  # Thiết kế campaign paper-v5-w2-ablation-part01: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part02.json  # Thiết kế campaign paper-v5-w2-ablation-part02: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part03.json  # Thiết kế campaign paper-v5-w2-ablation-part03: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part04.json  # Thiết kế campaign paper-v5-w2-ablation-part04: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part05.json  # Thiết kế campaign paper-v5-w2-ablation-part05: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part06.json  # Thiết kế campaign paper-v5-w2-ablation-part06: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   ├── paper-v5-w2-ablation-part07.json  # Thiết kế campaign paper-v5-w2-ablation-part07: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   │   └── paper-v5-w2-ablation-part08.json  # Thiết kế campaign paper-v5-w2-ablation-part08: E62; 1 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── ablation.json  # Thiết kế campaign ablation: E07; 6 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── algorithm_comparison.json  # Thiết kế campaign algorithm_comparison: E02, E03, E04; 7 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── failure_controls.json  # Thiết kế campaign failure-controls: E02; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_ablation.json  # Thiết kế campaign joint_ablation: E12; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_certification.json  # Thiết kế campaign joint_certification: E13; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_certification_128.json  # Thiết kế campaign joint_certification_128: E13; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_effectiveness.json  # Thiết kế campaign joint_effectiveness: E11; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_failure_controls.json  # Thiết kế campaign joint_no_incumbent_controls: E13; 3 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_holdout.json  # Thiết kế campaign joint_holdout: E15; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── joint_scalability.json  # Thiết kế campaign joint_scalability: E14; 3 dataset, 3 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── main.json  # Thiết kế campaign main: E01, E02, E03, E04, E05, E06, E07, E08; 7 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── pilot.json  # Thiết kế campaign pilot: E01, E02, E03, E04, E05, E06, E07, E08; 5 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── pilot_cv.json  # Thiết kế campaign pilot_cv: E16; 2 dataset, 1 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── reproducibility.json  # Thiết kế campaign reproducibility: E10; 1 dataset, 2 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── robustness.json  # Thiết kế campaign robustness: E09; 2 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   ├── scalability.json  # Thiết kế campaign scalability: E08; 6 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   │   └── sensitivity.json  # Thiết kế campaign sensitivity: E06; 6 dataset, 5 seed; khai báo treatment và budget, không chứa kết quả chạy.
│   ├── docs/  # Tài liệu tổ chức thực nghiệm và dữ liệu.
│   │   └── research/  # Vị trí tài liệu nghiên cứu trong cây experiments; hiện không có file trong kiểm kê.
│   │       ├── ALGORITHM_DESIGN.md  # Tài liệu: Algorithm design.
│   │       ├── DATA_PROVENANCE.md  # Tài liệu: Data provenance.
│   │       ├── EXPERIMENT_DESIGN_DEEPMG.md  # Tài liệu: Thiết kế thực nghiệm cho bài báo (hướng A, theo phương pháp deepmg).
│   │       ├── HOW_TO_RUN_EXPERIMENTS.md  # Tài liệu: Hướng dẫn chạy thí nghiệm.
│   │       ├── HOW_TO_RUN_JOINT_OPTIMIZATION.md  # Tài liệu: Running joint T1-T4 research.
│   │       ├── JOINT_OPTIMIZATION_ACCEPTANCE.md  # Tài liệu: Joint optimization acceptance.
│   │       ├── JOINT_OPTIMIZATION_FORMULATION.md  # Tài liệu: Joint T1-T4 formulation and proof scope.
│   │       ├── MATHEMATICAL_FORMULATION.md  # Tài liệu: Executed mathematical model.
│   │       ├── OBJECTIVES_AND_HYPOTHESES.md  # Tài liệu: Objectives and hypotheses.
│   │       ├── PAPER_EXPERIMENT_RUNBOOK.md  # Tài liệu: Hướng dẫn chạy thực nghiệm bài báo (hướng A).
│   │       ├── RESEARCH_PROBLEM.md  # Tài liệu: Research problem.
│   │       ├── RESEARCH_STATUS.md  # Tài liệu: Phạm vi và trạng thái nghiên cứu.
│   │       └── THREATS_TO_VALIDITY.md  # Tài liệu: Threats to validity.
│   ├── scripts/  # Công cụ thực nghiệm trong cây experiments; không giả định có thể thay thế bằng bản scripts cùng tên.
│   │   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   │   ├── paper_progress/  # Trang và máy chủ quan sát tiến độ thuộc cây experiments/scripts.
│   │   │   ├── index.html  # Trang tiến độ campaign: đọc trạng thái từ máy chủ cục bộ và cập nhật bảng quan sát; số liệu phụ thuộc thời điểm lấy mẫu.
│   │   │   └── server.py  # Phục vụ trang tiến độ cục bộ bằng cách đọc checkpoint, bản ghi và tiến trình. Trang hiển thị không trực tiếp chạy solver.
│   │   ├── build_paper_configs.py  # Sinh cấu hình campaign cho thiết kế paper, gồm dataset, nhánh so sánh, seed và giới hạn job.
│   │   ├── check_experiment_readiness.py  # Đánh giá mức sẵn sàng nghiên cứu bằng các bằng chứng thực thi đã ghi nhận và nêu rõ giới hạn.
│   │   ├── paper_recovery.py  # Chuẩn bị campaign bổ sung ngân sách từ job gốc, giữ dữ liệu và kết quả cũ để đối chiếu.
│   │   ├── paper_resource_guard.py  # Lấy mẫu RAM hệ điều hành và quyết định tiếp nhận campaign theo ngưỡng có hysteresis để tránh đổi số slot liên tục.
│   │   ├── run_paper_campaigns.py  # Chạy các campaign tuần tự theo thứ tự khối của bộ cấu hình, hỗ trợ tiếp tục và tổng hợp báo cáo.
│   │   ├── run_paper_parallel.py  # Điều phối campaign riêng biệt trên hai hoặc ba slot theo điều kiện tài nguyên và tiến độ.
│   │   ├── summarize_paper_results.py  # Tổng hợp kết quả mô tả theo job duy nhất, phân biệt lần chạy gốc và các đợt bổ sung.
│   │   └── watch_paper_campaigns.py  # Giám sát batch paper, đọc trạng thái và xác minh campaign cùng báo cáo trước khi kết thúc giám sát.
│   ├── visualization/  # Công cụ vẽ biểu đồ từ số liệu được cung cấp.
│   │   └── plots.py  # Vẽ biểu đồ từ bảng và số liệu thực nghiệm được cung cấp; biểu đồ phụ thuộc phạm vi dữ liệu đầu vào.
│   ├── analyze_campaign.py  # Phát lại kiểm tra nghiệm đã lưu và tính thống kê ghép cặp mang tính thăm dò cho campaign.
│   ├── GITHUB_ARCHIVE.md  # Tài liệu: Trạng thái bản xuất thực nghiệm cũ.
│   ├── README.md  # Tài liệu: Thực nghiệm nghiên cứu.
│   ├── run_campaign.py  # Campaign smoke với dữ liệu tổng hợp, chạy qua hàng đợi và worker production để thu kết quả thực.
│   └── VI_TRI_DU_LIEU.md  # Tài liệu: Thư mục thực nghiệm sau khi xoá kết quả cũ.
├── frontend/  # Ứng dụng React/TypeScript, cấu hình Vite và kiểm thử giao diện.
│   ├── dist/ [gộp nội dung sinh tự động/nội bộ]  # HTML/JS/CSS được sinh khi build frontend; không phải mã nguồn chỉnh tay.
│   ├── node_modules/ [gộp nội dung sinh tự động/nội bộ]  # Package npm đã cài; nhiệm vụ dependency được khai báo ở package.json/lockfile, nội dung được gộp.
│   ├── public/  # Tài nguyên tĩnh được phục vụ nguyên trạng.
│   │   └── favicon.svg  # Biểu tượng tab trình duyệt.
│   ├── src/  # Mã nguồn giao diện hiện tại.
│   │   ├── app/  # Khung ứng dụng, điều hướng, custom hook và style chung.
│   │   │   ├── App.tsx  # Ghép hook trạng thái workspace với khung giao diện chính của ứng dụng.
│   │   │   ├── AppShell.tsx  # Khung giao diện: điều hướng, trạng thái chung và trang nội dung theo workspace đang chọn.
│   │   │   ├── ErrorBoundary.tsx  # Chặn lỗi render ở cây React con và hiển thị trạng thái phục hồi thay vì làm mất toàn bộ giao diện.
│   │   │   ├── FloorplanCanvas.tsx  # Nạp lười trình biên tập mặt bằng để chỉ tải phần canvas khi trang cần dùng.
│   │   │   ├── navigation.ts  # Danh mục trang, biểu tượng và mô tả dùng chung cho điều hướng của workspace.
│   │   │   ├── styles.css  # Kiểu hiển thị chung cho workspace, bảng nhập liệu, trạng thái và bố cục theo kích thước màn hình. /
│   │   │   ├── useFloorplanState.ts  # Quản lý bản nháp mặt bằng, danh sách kệ và cờ thay đổi chưa lưu trong giao diện.
│   │   │   ├── useHashRoute.ts  # Đồng bộ trang đang mở với hash của URL và đăng ký dọn listener khi hook kết thúc.
│   │   │   ├── useProjectState.ts  # Tải danh sách dự án, giữ dự án đang chọn và thông báo lỗi tải dữ liệu.
│   │   │   ├── useRunState.ts  # Giữ lần chạy được chọn và lần chạy dùng so sánh. Danh sách activeStates xác định trạng thái còn hoạt động.
│   │   │   ├── useRuntimeStatus.ts  # Poll tình trạng dịch vụ và các lần chạy mỗi hai giây. Cleanup ngăn phản hồi cũ cập nhật state sau khi đổi dự án.
│   │   │   └── useWorkspace.tsx  # Ghép các hook dự án, bản vẽ, điều hướng và lần chạy thành model chung cho giao diện. Thao tác lưu dùng revision API mới nhất.
│   │   ├── components/  # Component giao diện dùng chung.
│   │   │   ├── Badge.tsx  # Hiển thị nhãn trạng thái với lớp CSS theo mã trạng thái và chuỗi dễ đọc. Hiển thị nhãn trạng thái với lớp CSS theo mã trạng thái và chuỗi dễ đọc.
│   │   │   ├── InputEditor.tsx  # Biên tập nội dung JSON đầu vào, phân tích dữ liệu trước khi chuyển cho thao tác lưu.
│   │   │   └── Stat.tsx  # Ô thống kê dùng lại cho nhãn, giá trị, đơn vị và nội dung phụ trên dashboard.
│   │   ├── features/  # Các chức năng giao diện chia theo nghiệp vụ.
│   │   │   ├── categories/  # Định nghĩa chức năng nhập liệu/hiển thị ngành hàng.
│   │   │   │   └── definition.ts  # Định nghĩa giao diện nhập nhóm ngành hàng, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   │   ├── demand/  # Định nghĩa chức năng nhập liệu/hiển thị nhu cầu và hành vi.
│   │   │   │   └── definition.ts  # Định nghĩa giao diện nhập nhóm nhu cầu, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   │   ├── floorplan-editor/  # Canvas Konva biên tập mặt bằng và vị trí kệ.
│   │   │   │   └── FloorplanEditor.tsx  # Canvas Konva chỉnh sửa mặt bằng và kệ, chuyển đổi tọa độ hiển thị với tọa độ dữ liệu; hỗ trợ lịch sử thao tác.
│   │   │   ├── optimization/  # Định nghĩa chức năng nhập liệu/hiển thị cấu hình tối ưu.
│   │   │   │   └── definition.ts  # Định nghĩa giao diện nhập nhóm tối ưu, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   │   ├── orders/  # Định nghĩa chức năng nhập liệu/hiển thị đơn hàng.
│   │   │   │   └── definition.ts  # Định nghĩa giao diện nhập nhóm đơn hàng, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   │   ├── products/  # Định nghĩa chức năng nhập liệu/hiển thị sản phẩm.
│   │   │   │   └── definition.ts  # Định nghĩa giao diện nhập nhóm sản phẩm, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   │   ├── projects/  # Định nghĩa chức năng nhập liệu/hiển thị dự án.
│   │   │   │   └── sample.ts  # Cung cấp dữ liệu cửa hàng tổng hợp dùng chung từ fixture JSON của dự án.
│   │   │   ├── research/  # Dashboard campaign và hiển thị tối ưu liên tầng.
│   │   │   │   ├── api.ts  # Client API nghiên cứu và các kiểu campaign, dataset, cấu hình dùng trên dashboard. Kiểu cấu hình dataset của một campaign; đây là khai báo tĩnh, không phát sinh JavaScript.
│   │   │   │   ├── JointPanel.tsx  # Hiển thị tiến độ, nghiệm và thông tin chứng nhận của tối ưu liên tầng từ kết quả đã lưu.
│   │   │   │   └── ResearchPage.tsx  # Giao diện chọn dữ liệu, cấu hình và quản lý campaign; trạng thái thực thi được lấy từ API nghiên cứu.
│   │   │   ├── results/  # Hiển thị planogram, KPI và hành trình mô phỏng.
│   │   │   │   ├── PlanogramViewer.tsx  # Mã tsx cho PlanogramViewer.
│   │   │   │   └── SimulationAnalytics.tsx  # Mã tsx cho SimulationAnalytics.
│   │   │   └── shelves/  # Định nghĩa chức năng nhập liệu/hiển thị kệ.
│   │   │       └── definition.ts  # Định nghĩa giao diện nhập nhóm kệ, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
│   │   ├── pages/  # Các trang và bộ ghép màn hình.
│   │   │   ├── workspace/  # Các trang dự án, nhập liệu, chạy tối ưu, chẩn đoán và kết quả.
│   │   │   │   ├── DashboardPage.tsx  # Tổng quan mức hoàn thành dữ liệu, sức khỏe dịch vụ và lối đi tới các bước của workspace.
│   │   │   │   ├── DiagnosticsPage.tsx  # Hiển thị kiểm tra dữ liệu, trạng thái dịch vụ và các thông tin hỗ trợ chẩn đoán.
│   │   │   │   ├── FloorplanPage.tsx  # Trang bao trình biên tập mặt bằng, kết nối bản nháp và thao tác lưu của workspace.
│   │   │   │   ├── InputPageRouter.tsx  # Chọn nhóm đầu vào theo trang điều hướng và truyền dữ liệu cùng thao tác lưu cho DataInputPage.
│   │   │   │   ├── OptimizationRunsPage.tsx  # Cấu hình tối ưu, tạo job, xem trạng thái và yêu cầu hủy hoặc phát lại lần chạy qua API.
│   │   │   │   ├── ProjectsPage.tsx  # Chọn hoặc tạo dự án, bao gồm tùy chọn nạp bộ dữ liệu tổng hợp mẫu.
│   │   │   │   └── RunResultsPage.tsx  # Ghép các màn hình bố trí, planogram, mô phỏng và báo cáo cho lần chạy đang chọn.
│   │   │   ├── DataInputPage.tsx  # Chọn định nghĩa nhóm dữ liệu và cung cấp trình biên tập, bảng nhập/xuất cho đầu vào của dự án.
│   │   │   └── ReportsPage.tsx  # Hiển thị và cung cấp liên kết tải báo cáo từ lần chạy và kết quả đã chọn.
│   │   ├── services/  # Client HTTP dùng trong workspace.
│   │   │   └── api.ts  # Client HTTP dùng chung cho dự án và lần chạy. Chuẩn hóa lỗi phản hồi và gửi expected_revision khi lưu để tránh ghi đè cập nhật đồng thời.
│   │   ├── types/  # Kiểu TypeScript cho dữ liệu đầu vào, API và kết quả.
│   │   │   └── models.ts  # Các kiểu TypeScript cho dữ liệu API, đầu vào và kết quả. Trường có hậu tố đơn vị giữ đúng ý nghĩa từ backend.
│   │   ├── utils/  # Hàm tiện ích, trong đó có hình học cho canvas.
│   │   │   └── geometry.ts  # Hàm hình học canvas: bắt lưới, góc quay và kiểm tra vị trí kệ; được kiểm thử riêng bằng Vitest.
│   │   └── main.tsx  # Điểm khởi tạo React, ghép ứng dụng với StrictMode, ErrorBoundary và stylesheet.
│   ├── test-results/ [gộp nội dung sinh tự động/nội bộ]  # Artifact chạy kiểm thử trình duyệt ở máy hiện tại; nội dung được gộp.
│   ├── Dockerfile  # Build frontend và đóng gói để phục vụ tĩnh qua Nginx.
│   ├── eslint.config.js  # Cấu hình ESLint cho JavaScript và TypeScript của giao diện.
│   ├── index.html  # HTML khởi tạo ứng dụng React và metadata trang.
│   ├── nginx.conf  # Cấu hình Nginx phục vụ frontend và chuyển tiếp yêu cầu API.
│   ├── package-lock.json  # Khóa cây dependency và integrity npm để cài đặt nhất quán.
│   ├── package.json  # Script npm và dependency/devDependency của frontend.
│   ├── tsconfig.json  # Tùy chọn biên dịch TypeScript và phạm vi file cần kiểm tra.
│   ├── tsconfig.tsbuildinfo  # Cache biên dịch tăng dần TypeScript sinh tự động; không phải mã nguồn.
│   └── vite.config.ts  # Cấu hình dev server và build Vite cho React, gồm chuyển tiếp API đến backend.
├── scripts/  # Công cụ cài đặt, khởi động/dừng, thực nghiệm và xác minh từ root.
│   ├── __pycache__/ [gộp nội dung sinh tự động/nội bộ]  # Bytecode Python sinh tự động; không cần chỉnh tay, nội dung được gộp.
│   ├── paper_progress/  # Trang và máy chủ cục bộ quan sát tiến độ thực nghiệm.
│   │   ├── index.html  # Trang tiến độ campaign: đọc trạng thái từ máy chủ cục bộ và cập nhật bảng quan sát; số liệu phụ thuộc thời điểm lấy mẫu.
│   │   └── server.py  # Phục vụ trang tiến độ cục bộ bằng cách đọc checkpoint, bản ghi và tiến trình. Trang hiển thị không trực tiếp chạy solver.
│   ├── build_joint_configs.py  # Tạo cấu hình thực nghiệm E11–E15 từ thiết kế đã khai báo; việc sinh cấu hình không tạo ra kết quả thực nghiệm.
│   ├── build_joint_fixtures.py  # Tạo fixture tổng hợp nhỏ với miền quyết định tường minh cho kiểm tra joint và chứng nhận.
│   ├── build_paper_configs.py  # Sinh cấu hình campaign cho thiết kế paper, gồm dataset, nhánh so sánh, seed và giới hạn job.
│   ├── build_paper_v4_configs.py  # Sinh các nhánh và phần campaign Paper V4, bảo đảm cấu hình được chốt theo giới hạn thiết kế.
│   ├── build_paper_v5_configs.py  # Sinh thiết kế Paper V5 với khối ablation W2 và so sánh chính W1; tách campaign theo giới hạn số job.
│   ├── build_x1_union_configs.py  # Tạo pha exact X1 từ hợp miền nghiệm heuristic pha trước. Kết luận chỉ áp dụng cho miền hợp đã dựng.
│   ├── check_experiment_readiness.py  # Đánh giá mức sẵn sàng nghiên cứu bằng các bằng chứng thực thi đã ghi nhận và nêu rõ giới hạn.
│   ├── check_joint_readiness.py  # Kiểm tra gate joint từ receipt chạy và chứng nhận; sự tồn tại của tệp chưa đủ chứng minh đã đạt.
│   ├── paper_recovery.py  # Chuẩn bị campaign bổ sung ngân sách từ job gốc, giữ dữ liệu và kết quả cũ để đối chiếu.
│   ├── paper_resource_guard.py  # Lấy mẫu RAM hệ điều hành và quyết định tiếp nhận campaign theo ngưỡng có hysteresis để tránh đổi số slot liên tục.
│   ├── publish_experiment_archive.py  # Đóng gói kết quả thành các phần ZIP có checksum và hỗ trợ xuất bản release. Việc gọi script có thể tạo thao tác lên GitHub.
│   ├── replay_failed_campaign_jobs.py  # Chạy lại đúng đầu vào các job thất bại trong đích mới theo nguồn hiện tại để giữ bằng chứng lịch sử.
│   ├── run_paper_adaptive.py  # Điều phối Paper V3 với ba slot; giảm tiếp nhận khi RAM vượt ngưỡng và chờ job hiện tại kết thúc.
│   ├── run_paper_campaigns.py  # Chạy các campaign tuần tự theo thứ tự khối của bộ cấu hình, hỗ trợ tiếp tục và tổng hợp báo cáo.
│   ├── run_paper_parallel.py  # Điều phối campaign riêng biệt trên hai hoặc ba slot theo điều kiện tài nguyên và tiến độ.
│   ├── run_paper_v4_adaptive.py  # Điều phối Paper V4 theo ngưỡng RAM, giữ nhận diện cấu hình và kiểm tra kết quả giữa các lượt chạy.
│   ├── run_paper_v5_parallel.py  # Chạy Paper V5 trên ba slot độc lập, mỗi campaign một worker và mỗi lượt một job. Kiểm tra drift, integrity và trạng thái trước khi nhận thêm việc.
│   ├── setup.ps1  # Chuẩn bị môi trường Python và frontend cùng dependency theo quy trình cài đặt của dự án.
│   ├── start.ps1  # Kiểm tra cổng và MongoDB, khởi động API, worker và frontend; ghi PID để quản lý vòng đời dịch vụ.
│   ├── start_mongodb.ps1  # Chuẩn bị và khởi động MongoDB cục bộ theo cấu hình riêng, có tùy chọn cài bản portable.
│   ├── stop.ps1  # Đọc trạng thái dịch vụ đã lưu và dừng các tiến trình thuộc lượt khởi động đó theo kiểm tra trong script.
│   ├── stop_mongodb.ps1  # Dừng MongoDB cục bộ theo thông tin tiến trình đã ghi và các kiểm tra nhận diện trong script.
│   ├── summarize_paper_results.py  # Tổng hợp kết quả mô tả theo job duy nhất, phân biệt lần chạy gốc và các đợt bổ sung.
│   ├── verify_architecture.py  # Phân tích import Python và TypeScript để kiểm tra chiều phụ thuộc cùng chu trình module.
│   └── watch_paper_campaigns.py  # Giám sát batch paper, đọc trạng thái và xác minh campaign cùng báo cáo trước khi kết thúc giám sát.
├── var/ [gộp nội dung sinh tự động/nội bộ]  # Runtime/artifact, MongoDB cục bộ, log, checkpoint và biên nhận công việc; chỉ mô tả vùng, không công bố file riêng/bí mật.
├── .dockerignore  # Các đường dẫn loại khỏi Docker build context.
├── .env.example  # Mẫu biến môi trường để cấu hình triển khai, không phải cấu hình bí mật đang chạy.
├── .gitignore  # Các đường dẫn Git bỏ qua: môi trường, cache, dữ liệu runtime, kết quả và bí mật cục bộ.
├── AGENTS.md  # Quy tắc làm việc với repository, kiến trúc và các giới hạn bảo toàn dữ liệu/Git.
├── CAU_TRUC_HE_THONG.md  # Bản đồ cây thư mục này, giải thích nhiệm vụ từng thư mục và file trong phạm vi công bố.
├── docker-compose.yml  # Khai báo MongoDB, bước khởi tạo, API, worker, frontend và các volume Docker.
├── HANDOFF.md  # Bàn giao hiện tại và các mốc lịch sử; dùng để biết việc đã làm, kiểm chứng và bước tiếp theo.
├── README.md  # Hướng dẫn tổng thể: kiến trúc, T1–T4, cài đặt, API, kiểm thử và tái lập nghiên cứu.
└── Smart_Retail_E.code-workspace  # Định nghĩa workspace VS Code và các thư mục/cài đặt liên quan.
```

## 4. Các vùng sinh tự động và dữ liệu vận hành

`var/` là vùng local cho artifact worker, log, MongoDB portable/cấu hình riêng, biên nhận audit/refactor và các trạng thái điều phối. Các file bên trong có thể thay đổi theo từng lần chạy. Không coi chúng là mã thừa và không xoá dựa vào việc bản đồ này gộp nội dung.

Các vùng `experiments/results/`, `experiments/reports/`, `experiments/runtime/` hoặc database/backups thực nghiệm có thể được tạo theo cấu hình khi chạy. Chỉ vùng thực sự tồn tại ở thời điểm kiểm kê mới xuất hiện trong cây. Đường dẫn output của lượt cũ có thể không còn trong checkout; đọc HANDOFF và biên nhận tương ứng trước khi resume/replay.

Bộ replay/validation trong `backend/src/smart_retail/engines` và `application/experiments/validation.py` phục vụ kiểm tra tính hợp lệ của kết quả ứng dụng, nên vẫn được trình bày trong cây.

## 5. Giới hạn của bản đồ

Đây là ảnh chụp cấu trúc tại thời điểm ghi tài liệu. File mới được thêm sau đó cần được cập nhật vào cây. Các file bằng chứng có ngày/lượt riêng vẫn là lịch sử; số file hoặc sự tồn tại của báo cáo không chứng minh thuật toán đúng hay thực nghiệm đã hoàn tất. Tài liệu không thay thế README hướng dẫn chạy, hợp đồng dữ liệu hoặc báo cáo kiểm chứng.
