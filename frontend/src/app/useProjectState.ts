// Vai trò: Tải danh sách dự án, giữ dự án đang chọn và thông báo lỗi tải dữ liệu.
import { useCallback, useEffect, useState } from "react";
import type { Project } from "../types/models";
import { api } from "../services/api";

// Tải danh sách dự án, giữ dự án đang chọn và thông báo lỗi tải dữ liệu.
export function useProjectState(onLoad: (project: Project) => void) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [projectError, setProjectError] = useState("");
  // Chọn dự án, reset vùng làm việc liên quan và lưu mã dự án để mở lại.
  const loadProject = useCallback((value: Project) => {
    setProject(value);
    onLoad(value);
    localStorage.setItem("smart-retail-project", value.id);
  }, [onLoad]);
  useEffect(() => {
    let alive = true;
    api.projects().then((list) => {
      if (!alive) return;
      setProjects(list);
      const current = list.find((p) => p.id === localStorage.getItem("smart-retail-project")) || list[0];
      if (current) loadProject(current);
    }).catch((error) => { if (alive) setProjectError(String(error)); })
      .finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [loadProject]);
  return { projects, setProjects, project, setProject, loading, projectError, loadProject };
}
