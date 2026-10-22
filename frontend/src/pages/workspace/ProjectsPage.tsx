import { ArrowRight, FolderOpen } from "lucide-react";
import type { WorkspaceModel } from "../../app/useWorkspace";

export function ProjectsPage({ model }: { model: WorkspaceModel }) {
  const { page, project, loading, projects, name, setName, busy, act, create, loadProject, go } = model;
  return (<>{(page === "projects" || (!project && !loading && page !== "research")) && (
    <section className="panel">
      <div className="panel-heading">
        <h2>Không gian dự án</h2>
        <span>{projects.length} dự án</span>
      </div>
      <div className="project-create">
        <label>
          Tên dự án
          <input
            placeholder="Ví dụ: Cửa hàng Quận 3"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
        </label>
        <button
          className="primary"
          disabled={busy || loading}
          onClick={() => void act(() => create(false))}
        >
          Tạo dự án
        </button>
        <button
          disabled={busy || loading}
          onClick={() => void act(() => create(true))}
        >
          Tạo dự án mẫu
        </button>
      </div>
      <p className="muted">
        Dự án mẫu dùng dữ liệu tổng hợp, được lưu vào cơ sở dữ liệu và
        có thể chỉnh sửa.
      </p>
      <div className="project-list">
        {projects.map((p) => (
          <button
            key={p.id}
            className="project-row"
            onClick={() => {
              loadProject(p);
              go("dashboard");
            }}
          >
            <FolderOpen size={20} />
            <span>
              <strong>{p.name}</strong>
              <small>
                {p.id} · revision {p.revision}
              </small>
            </span>
            <ArrowRight size={18} />
          </button>
        ))}
      </div>
    </section>
  )}</>);
}
