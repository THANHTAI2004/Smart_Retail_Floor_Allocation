// Vai trò: Client HTTP dùng chung cho dự án và lần chạy.
// Chuẩn hóa lỗi phản hồi và gửi expected_revision khi lưu để tránh ghi đè cập nhật đồng thời.
import type { Health, Project, Run, Section } from "../types/models";

// Gửi yêu cầu HTTP và chuyển lỗi phản hồi cho caller theo hợp đồng của client này.
async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  // Đưa lỗi HTTP về một Error thống nhất để các trang có thể hiển thị cùng cơ chế.
  if (!response.ok) {
    const body = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail);
    throw new Error(`${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}
export const api = {
  // Đọc danh sách dự án qua API.
  projects: () => request<Project[]>("/projects"),
  // Tạo dự án, nạp các nhóm dữ liệu mẫu khi được chọn rồi mở trang mặt bằng.
  create: (name: string) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  // Đọc dự án theo mã định danh.
  project: (id: string) => request<Project>(`/projects/${id}`),
  // Gửi revision đang biết; backend từ chối nếu dự án đã được cập nhật bởi thao tác khác.
  save: (p: Project, section: Section, value: unknown) =>
    request<Project>(
      `/projects/${p.id}/inputs/${section}?expected_revision=${p.revision}`,
      { method: "PUT", body: JSON.stringify(value) },
    ),
  // Yêu cầu backend kiểm tra đầy đủ đầu vào của dự án.
  validate: (id: string) =>
    request<{ valid: boolean; missing: string[]; errors: string[] }>(
      `/projects/${id}/validate`,
      { method: "POST" },
    ),
  // Gửi yêu cầu tạo lần chạy vào hàng đợi và trả trạng thái tiếp nhận.
  enqueue: (id: string) =>
    request<Run>(`/projects/${id}/runs`, { method: "POST" }),
  // Đọc danh sách các lần chạy của dự án.
  runs: (id: string) => request<Run[]>(`/projects/${id}/runs`),
  // Gửi yêu cầu hủy theo trạng thái hiện tại của lần chạy.
  cancel: (id: string) =>
    request<Run>(`/runs/${id}/cancel`, { method: "POST" }),
  // Yêu cầu phát lại lần chạy với snapshot được lưu.
  replay: (id: string) =>
    request<Run>(`/runs/${id}/replay`, { method: "POST" }),
  // Đọc sức khỏe dịch vụ qua API.
  health: () => request<Health>("/health"),
};
