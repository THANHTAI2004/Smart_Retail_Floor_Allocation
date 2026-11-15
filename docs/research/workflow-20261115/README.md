# Workflow hệ thống — 15/11/2026

- `01-workflow-tong-the`: luồng chung, gồm dispatch joint=null và các mode joint.
- `02-workflow-feedback-v5`: chi tiết phương pháp đề xuất theo cấu hình V5 hiện tại.
- Mỗi hình có PNG để xem/chèn Word, SVG để chỉnh sửa vector và PDF để in.

Giới hạn: warm start/pool là giới hạn lấy mẫu hoặc lần thử, không bảo đảm số ứng viên hợp lệ cuối cùng. Lỗi, hủy, hết thời gian/ngân sách có thể kết thúc sớm; hình biểu diễn luồng chính. Khi hội tụ, chỉ kick nếu còn lượt và điều kiện tài nguyên cho phép. Hình không chứng minh hiệu quả thuật toán hoặc hoàn tất một campaign.

Nguồn đối chiếu: `DOI_CHIEU_WORKFLOW_THUC_TE.md`, `application/feedback/coordinator.py`, `neighborhood.py`, `stage_workflow.py`, `evaluation.py` và bộ cấu hình `paper-v5-unlimited-parallel-20261110`.
