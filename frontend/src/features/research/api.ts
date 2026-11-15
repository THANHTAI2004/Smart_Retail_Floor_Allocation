// Vai trò: Client API nghiên cứu và các kiểu campaign, dataset, cấu hình dùng trên dashboard.
// Kiểu cấu hình dataset của một campaign; đây là khai báo tĩnh, không phát sinh JavaScript.
interface ResearchDataset {
  // Giữ nguyên mã dataset, quy mô và seed của hợp đồng đang dùng.
  id: string; scale: string; seed: number;
  // Kịch bản vẫn là tùy chọn, cùng kiểu và tên trường như trước.
  scenario?: string;
}

// Một nhánh so sánh giữ mã treatment và các phần cấu hình ghi đè.
interface ResearchTreatment {
  // Mã nhánh và dữ liệu override được truyền nguyên trạng cho API.
  id: string; overrides: Record<string, unknown>;
}

// Tách kiểu lồng nhau để đọc rõ danh sách dataset và treatment của một thực nghiệm.
interface ResearchExperiment {
  // Các khóa dữ liệu giữ nguyên cấu trúc trước khi đặt tên kiểu.
  id: string; datasets: string[]; treatments: ResearchTreatment[];
}

export interface ResearchSpec {
  name: string; seeds: number[];
  datasets: ResearchDataset[];
  experiments: ResearchExperiment[];
  job_time_limit_s: number; memory_limit_mb: number | null; max_wall_s: number;
}
export interface Campaign {
  id: string; status: string; completed?: number; planned?: number; not_executed?: number;
  error?: string; configuration: ResearchSpec; supervisor?: { status: string; report?: string; error?: string };
  datasets?: { dataset_id: string; sha256: string; version: string }[];
  records?: {
    job_key: string; experiment: string; dataset: string; treatment: string; seed: number; status: string;
    wall_s: number; peak_child_rss_bytes: number | null; mean_distance_m?: number; mean_wait_s?: number;
    input_sha256: string; error?: { code: string; message: string } | null; validation: { status: string }
    joint_objective?: number | null; proof_status?: string;
  }[];
}
export interface Dataset {
  id: string; version: string; data_origin: string; source: string;
  counts: Record<string, number>;
}
// Gửi yêu cầu HTTP và chuyển lỗi phản hồi cho caller theo hợp đồng của client này.
async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api/research${path}`, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`${response.status}: ${await response.text()}`);
  return response.json() as Promise<T>;
}
export const researchApi = {
  // Đọc danh mục dataset nghiên cứu.
  datasets: () => request<Dataset[]>("/datasets"),
  // Đọc danh sách cấu hình thực nghiệm được cung cấp.
  configurations: () => request<{ id: string; configuration: ResearchSpec }[]>("/configurations"),
  // Đọc danh sách campaign và trạng thái giám sát.
  campaigns: () => request<Campaign[]>("/campaigns"),
  // Đọc cấu hình và kết quả đã ghi nhận của campaign theo mã.
  detail: (id: string) => request<Campaign>(`/campaigns/${id}`),
  // Gửi cấu hình campaign cho API và nhận mã theo dõi.
  start: (spec: ResearchSpec) => request<{ id: string }>("/campaigns", spec),
  // Gửi thao tác điều khiển campaign theo endpoint được chọn.
  action: (id: string, action: "cancel" | "resume" | "replay") => request<{ id: string }>(`/campaigns/${id}/${action}`, {}),
};
