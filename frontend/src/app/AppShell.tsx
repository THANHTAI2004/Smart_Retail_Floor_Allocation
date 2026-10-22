import { ResearchPage } from "../features/research/ResearchPage";
import { navigation, descriptions } from "./navigation";
import { Check, ChevronRight, FolderOpen, Layers, Menu, Settings2, X } from "lucide-react";
import { api } from "../services/api";
import type { WorkspaceModel } from "./useWorkspace";
import "./styles.css";
import { ProjectsPage } from "../pages/workspace/ProjectsPage";
import { DashboardPage } from "../pages/workspace/DashboardPage";
import { FloorplanPage } from "../pages/workspace/FloorplanPage";
import { InputPageRouter } from "../pages/workspace/InputPageRouter";
import { OptimizationRunsPage } from "../pages/workspace/OptimizationRunsPage";
import { RunResultsPage } from "../pages/workspace/RunResultsPage";
import { DiagnosticsPage } from "../pages/workspace/DiagnosticsPage";

export function AppShell({ model }: { model: WorkspaceModel }) {
  const { mobile, setMobile, page, running, health, nav, busy, loading, project, projects, loadProject, completed, message, error, pollError, projectError, setError, act, setProjects } = model;
  return (
    <div className="shell">
      <a
        href="#main"
        className="skip-link"
        onClick={(e) => {
          e.preventDefault();
          document.getElementById("main")?.focus();
        }}
      >
        Đến nội dung chính
      </a>
      <aside
        className={mobile ? "sidebar open" : "sidebar"}
        aria-label="Điều hướng chính"
      >
        <div className="brand">
          <div className="brand-mark">
            <Layers size={24} />
          </div>
          <div>
            smart<span>retail</span>
            <small>LAYOUT STUDIO</small>
          </div>
          <button
            className="mobile-close"
            aria-label="Đóng menu"
            onClick={() => setMobile(false)}
          >
            <X size={18} />
          </button>
        </div>
        <div className="workspace-label">
          KHÔNG GIAN NGHIÊN CỨU <span>01</span>
        </div>
        <nav>
          {navigation.map((n) => (
            <div key={n.id}>
              {n.group && <div className="nav-group">{n.group}</div>}
              <a
                href={`#${n.id}`}
                onClick={() => setMobile(false)}
                aria-current={page === n.id ? "page" : undefined}
                className={page === n.id ? "nav-item selected" : "nav-item"}
              >
                <n.icon size={17} />
                <span>{n.title}</span>
                {n.id === "runs" && running && <i className="pulse" />}
              </a>
            </div>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <div
            className={health?.worker_online ? "connection on" : "connection"}
          >
            <i />
            {health?.worker_online ? "Worker sẵn sàng" : "Đang kiểm tra worker"}
          </div>
          <small>RESEARCH BASELINE · 0.1</small>
        </div>
      </aside>
      <div className="workspace">
        <header className="topbar">
          <button
            className="mobile-menu"
            onClick={() => setMobile(true)}
            aria-label="Mở menu"
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumb">
            Workspace <ChevronRight size={13} />
            <strong>{nav.title}</strong>
          </div>
          <div className="project-switch">
            <FolderOpen size={15} />
            <select
              aria-label="Dự án hiện tại"
              disabled={busy || loading}
              value={project?.id || ""}
              onChange={(e) => {
                const p = projects.find((x) => x.id === e.target.value);
                if (p) loadProject(p);
              }}
            >
              <option value="" disabled>
                Chọn dự án
              </option>
              {projects.map((p) => (
                <option value={p.id} key={p.id}>
                  {p.name}
                </option>
              ))}
            </select>
          </div>
          <span className="user-avatar">SR</span>
        </header>
        <main id="main" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <div className="eyebrow">SMART RETAIL FLOOR ALLOCATION</div>
              <h1>{nav.title}</h1>
              <p>{descriptions[page]}</p>
            </div>
            {project && (
              <div className="revision">
                <i className="dot" />
                Revision {project.revision}
                <small>{completed}/7 nhóm đã lưu</small>
              </div>
            )}
          </div>
          <div aria-live="polite">
            {loading && <div className="notice">Đang tải dự án…</div>}
            {message && (
              <div className="notice success">
                <Check size={16} />
                {message}
              </div>
            )}
          </div>
          {(error || pollError || projectError) && (
            <div className="notice error" role="alert">
              <span>{error || pollError || projectError}</span>
              <button
                onClick={() => {
                  setError("");
                  void act(async () => {
                    const list = await api.projects();
                    setProjects(list);
                    if (project) loadProject(await api.project(project.id));
                  });
                }}
              >
                Tải lại dữ liệu
              </button>
            </div>
          )}
          {page === "research" && <ResearchPage />}
          <ProjectsPage model={model} />
          <DashboardPage model={model} />
          <FloorplanPage model={model} />
          <InputPageRouter model={model} />
          <OptimizationRunsPage model={model} />
          <RunResultsPage model={model} />
          <DiagnosticsPage model={model} />
          <footer>
            <span>Smart Retail Floor Allocation</span>
            <span>Đơn vị chuẩn: mét · Dữ liệu nghiên cứu có truy vết</span>
            <Settings2 size={13} />
          </footer>
        </main>
      </div>
    </div>
  );
}
