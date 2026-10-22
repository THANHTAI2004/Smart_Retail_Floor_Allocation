import type { Health, Project, Run, Section } from "../types/models";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`/api${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
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
  projects: () => request<Project[]>("/projects"),
  create: (name: string) =>
    request<Project>("/projects", {
      method: "POST",
      body: JSON.stringify({ name }),
    }),
  project: (id: string) => request<Project>(`/projects/${id}`),
  save: (p: Project, section: Section, value: unknown) =>
    request<Project>(
      `/projects/${p.id}/inputs/${section}?expected_revision=${p.revision}`,
      { method: "PUT", body: JSON.stringify(value) },
    ),
  validate: (id: string) =>
    request<{ valid: boolean; missing: string[]; errors: string[] }>(
      `/projects/${id}/validate`,
      { method: "POST" },
    ),
  enqueue: (id: string) =>
    request<Run>(`/projects/${id}/runs`, { method: "POST" }),
  runs: (id: string) => request<Run[]>(`/projects/${id}/runs`),
  cancel: (id: string) =>
    request<Run>(`/runs/${id}/cancel`, { method: "POST" }),
  replay: (id: string) =>
    request<Run>(`/runs/${id}/replay`, { method: "POST" }),
  health: () => request<Health>("/health"),
};
