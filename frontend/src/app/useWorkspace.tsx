import { useFloorplanState } from "./useFloorplanState";
import { useProjectState } from "./useProjectState";
import { useHashRoute } from "./useHashRoute";
import { useRunState, activeStates } from "./useRunState";
import { useRuntimeStatus } from "./useRuntimeStatus";
import { navigation } from "./navigation";
import { useCallback, useState } from "react";
import sample from "../features/projects/sample";
import { api } from "../services/api";
import type { Project, Section, Shelf } from "../types/models";
export const sections: Section[] = ["floorplan", "shelves", "categories", "products", "demand", "orders", "optimization"];
export function useWorkspace() {
  const page = useHashRoute();
  const [mobile, setMobile] = useState(false);
  const { selectedRun, setSelectedRun, compareId, setCompareId } = useRunState();
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [name, setName] = useState("");
  const { floor, setFloor, shelves, setShelves, mode, setMode, dirty, setDirty, resetDrawing } = useFloorplanState();
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    missing: string[];
  } | null>(null);
  const go = (id: string) => {
    window.location.hash = id;
    setMobile(false);
  };
  const onProjectLoad = useCallback((p: Project) => {
    resetDrawing(p); setValidation(null); setSelectedRun("");
  }, [resetDrawing, setSelectedRun]);
  const { projects, setProjects, project, setProject, loading, projectError, loadProject } = useProjectState(onProjectLoad);
  const { health, setHealth, runs, setRuns, pollError } = useRuntimeStatus(project?.id);
  const act = async (action: () => Promise<void>) => {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  };
  const updateProject = (p: Project) => {
    setProject(p);
    setProjects((list) => list.map((x) => (x.id === p.id ? p : x)));
    setValidation(null);
  };
  const save = async (section: Section, value: unknown) => {
    if (!project) return;
    const p = await api.save(project, section, value);
    updateProject(p);
    setMessage(`Đã lưu ${section} · revision ${p.revision}`);
  };
  const create = async (demo: boolean) => {
    let p = await api.create(
      name.trim() ||
      (demo ? "Cửa hàng nghiên cứu · dữ liệu tổng hợp" : "Dự án mới"),
    );
    setProjects((list) => [p, ...list]);
    loadProject(p);
    if (demo)
      for (const section of sections) {
        p = await api.save(p, section, sample[section]);
        updateProject(p);
      }
    loadProject(p);
    setName("");
    setMessage(
      demo
        ? "Đã tạo dự án với 7 nhóm dữ liệu tổng hợp."
        : "Đã tạo dự án. Bắt đầu bằng mặt bằng.",
    );
    go("floorplan");
  };
  const saveDrawing = () =>
    act(async () => {
      if (!project) return;
      let p = await api.save(project, "floorplan", floor);
      updateProject(p);
      p = await api.save(p, "shelves", { ...project.sections.shelves, layout_mode: mode, items: shelves });
      updateProject(p);
      setDirty(false);
      setMessage(`Đã lưu bản vẽ và kệ · revision ${p.revision}`);
    });
  const completed = project
    ? sections.filter((k) => project.completion[k]).length
    : 0;
  const successful = runs.filter((r) => r.status === "SUCCEEDED");
  const run =
    runs.find((r) => r.id === selectedRun) || successful[0] || runs[0];
  const result = run?.result?.stages.T4 ? run.result : null;
  const comparison = runs.find((r) => r.id === compareId)?.result;
  const running = runs.some((r) => activeStates.includes(r.status));
  const nav = navigation.find((n) => n.id === page) || navigation[0];
  const selectRun = (
    <label className="run-select">
      Kết quả của lần chạy
      <select
        aria-label="Chọn lần chạy"
        value={run?.id || ""}
        onChange={(e) => setSelectedRun(e.target.value)}
      >
        {runs.map((r) => (
          <option key={r.id} value={r.id}>
            {r.id.slice(0, 8)} · {r.status} · rev {r.project_revision}
          </option>
        ))}
      </select>
    </label>
  );
  const addShelf = () => {
    const ids = new Set(shelves.map((s) => s.id));
    let i = shelves.length + 1;
    while (ids.has(`S${i}`)) i++;
    setShelves([
      ...shelves,
      { ...sample.shelves.items[0], id: `S${i}`, x: null, y: null } as Shelf,
    ]);
    setDirty(true);
  };
  return { mobile, setMobile, page, running, health, nav, busy, loading, project, projects, loadProject, completed, message, error, pollError, projectError, setError, act, setProjects, name, setName, create, go, successful, runs, setSelectedRun, addShelf, saveDrawing, mode, setMode, setDirty, floor, setFloor, dirty, shelves, setShelves, save, setValidation, setRuns, setMessage, validation, selectRun, result, run, comparison, compareId, setCompareId, setHealth };
}
export type WorkspaceModel = ReturnType<typeof useWorkspace>;
