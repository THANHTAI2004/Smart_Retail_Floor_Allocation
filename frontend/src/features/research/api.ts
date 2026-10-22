export interface ResearchSpec {
  name: string; seeds: number[];
  datasets: { id: string; scale: string; seed: number; scenario?: string }[];
  experiments: { id: string; datasets: string[]; treatments: { id: string; overrides: Record<string, unknown> }[] }[];
  job_time_limit_s: number; memory_limit_mb: number; max_wall_s: number;
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
async function request<T>(path: string, body?: unknown): Promise<T> {
  const response = await fetch(`/api/research${path}`, body === undefined ? {} : {
    method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(`${response.status}: ${await response.text()}`);
  return response.json() as Promise<T>;
}
export const researchApi = {
  datasets: () => request<Dataset[]>("/datasets"),
  configurations: () => request<{ id: string; configuration: ResearchSpec }[]>("/configurations"),
  campaigns: () => request<Campaign[]>("/campaigns"),
  detail: (id: string) => request<Campaign>(`/campaigns/${id}`),
  start: (spec: ResearchSpec) => request<{ id: string }>("/campaigns", spec),
  action: (id: string, action: "cancel" | "resume" | "replay") => request<{ id: string }>(`/campaigns/${id}/${action}`, {}),
};
