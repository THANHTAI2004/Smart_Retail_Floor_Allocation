import { useRuntimeStatus } from "./useRuntimeStatus";
import { navigation, descriptions } from "./navigation";
import { PlanogramViewer } from "../features/results/PlanogramViewer";
import { SimulationAnalytics } from "../features/results/SimulationAnalytics";
import { ReportsPage } from "../pages/ReportsPage";
import { Stat } from "../components/Stat";
import { lazy, Suspense, useCallback, useEffect, useState } from "react";
import {
  ArrowRight,
  ChartNoAxesCombined,
  Check,
  ChevronRight,
  FolderOpen,
  Layers,
  Map,
  Menu,
  Play,
  RefreshCw,
  Settings2,
  SquareStack,
  X,
} from "lucide-react";
import sample from "../features/projects/sample";
import { DataInputPage } from "../pages/DataInputPage";
const FloorplanEditor = lazy(() =>
  import("../features/floorplan-editor/FloorplanEditor").then((module) => ({
    default: module.FloorplanEditor,
  })),
);
import { api } from "../services/api";
import type {
  Floorplan,
  Project,
  Section,
  Shelf,
} from "../types/models";
import { area } from "../utils/geometry";
import "./styles.css";

const sections: Section[] = [
  "floorplan",
  "shelves",
  "categories",
  "products",
  "demand",
  "orders",
  "optimization",
];
const activeStates = ["QUEUED", "RUNNING", "CANCEL_REQUESTED"];
const defaultFloor = sample.floorplan as Floorplan;

export default function App() {
  const [page, setPage] = useState(
    window.location.hash.slice(1) || "dashboard",
  );
  const [mobile, setMobile] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [project, setProject] = useState<Project | null>(null);
  const [selectedRun, setSelectedRun] = useState("");
  const [compareId, setCompareId] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState("");
  const [floor, setFloor] = useState<Floorplan>(defaultFloor);
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [mode, setMode] = useState<"fixed" | "optimizable">("optimizable");
  const [dirty, setDirty] = useState(false);
  const [validation, setValidation] = useState<{
    valid: boolean;
    errors: string[];
    missing: string[];
  } | null>(null);
  const go = (id: string) => {
    window.location.hash = id;
    setMobile(false);
  };
  useEffect(() => {
    const change = () => setPage(window.location.hash.slice(1) || "dashboard");
    window.addEventListener("hashchange", change);
    return () => window.removeEventListener("hashchange", change);
  }, []);
  const loadProject = useCallback((p: Project) => {
    setProject(p);
    setFloor((p.sections.floorplan as unknown as Floorplan) || defaultFloor);
    setShelves((p.sections.shelves?.items as Shelf[]) || []);
    setMode(
      (p.sections.shelves?.layout_mode as "fixed" | "optimizable") ||
        "optimizable",
    );
    setDirty(false);
    setValidation(null);
    setSelectedRun("");
    window.localStorage.setItem("smart-retail-project", p.id);
  }, []);
  useEffect(() => {
    let alive = true;
    api
      .projects()
      .then((list) => {
        if (!alive) return;
        setProjects(list);
        const current =
          list.find(
            (p) => p.id === window.localStorage.getItem("smart-retail-project"),
          ) || list[0];
        if (current) loadProject(current);
      })
      .catch((e) => {
        if (alive) setError(String(e));
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, [loadProject]);
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
      p = await api.save(p, "shelves", { layout_mode: mode, items: shelves });
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
  const result = run?.result;
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
          {(error || pollError) && (
            <div className="notice error" role="alert">
              <span>{error || pollError}</span>
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
          {(page === "projects" || (!project && !loading)) && (
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
          )}
          {project && page === "dashboard" && (
            <>
              <div className="stat-grid">
                <Stat
                  label="DIỆN TÍCH MẶT BẰNG"
                  value={
                    project.sections.floorplan
                      ? area(
                          (project.sections.floorplan as unknown as Floorplan)
                            .boundary,
                        ).toFixed(1)
                      : "—"
                  }
                  unit="m²"
                  icon={<Map size={19} />}
                />
                <Stat
                  label="KỆ TRƯNG BÀY"
                  value={String(
                    ((project.sections.shelves?.items as unknown[]) || [])
                      .length,
                  )}
                  unit="kệ"
                  icon={<SquareStack size={19} />}
                />
                <Stat
                  label="DỮ LIỆU ĐÃ LƯU"
                  value={`${completed}/7`}
                  unit="nhóm"
                  icon={<Check size={19} />}
                />
                <Stat
                  label="PHƯƠNG ÁN THÀNH CÔNG"
                  value={String(successful.length)}
                  unit="lần chạy"
                  icon={<ChartNoAxesCombined size={19} />}
                />
              </div>
              <section className="panel">
                <div className="panel-heading">
                  <h2>Thiết lập nghiên cứu</h2>
                  <span>7 nhóm dữ liệu chính thức</span>
                </div>
                <div className="workflow">
                  {sections.map((s, i) => (
                    <button key={s} onClick={() => go(s)}>
                      <span
                        className={project.completion[s] ? "step done" : "step"}
                      >
                        {project.completion[s] ? (
                          <Check size={15} />
                        ) : (
                          `0${i + 1}`
                        )}
                      </span>
                      <span>
                        <strong>
                          {navigation.find((n) => n.id === s)?.title}
                        </strong>
                        <small>
                          {project.completion[s]
                            ? "Đã lưu · có thể chỉnh sửa"
                            : "Chưa nhập dữ liệu"}
                        </small>
                      </span>
                      <ChevronRight size={15} />
                    </button>
                  ))}
                </div>
              </section>
              <div className="two-columns">
                <section className="panel">
                  <div className="panel-heading">
                    <h2>Lần chạy gần nhất</h2>
                    <button onClick={() => go("runs")}>
                      Xem tất cả <ArrowRight size={13} />
                    </button>
                  </div>
                  {runs.slice(0, 4).map((r) => (
                    <button
                      className="run-row"
                      key={r.id}
                      onClick={() => {
                        setSelectedRun(r.id);
                        go("layout");
                      }}
                    >
                      <code>{r.id.slice(0, 8)}</code>
                      <Badge status={r.status} />
                      <span>rev {r.project_revision}</span>
                    </button>
                  ))}
                  {!runs.length && (
                    <div className="empty">
                      <Play size={24} />
                      <p>Chưa có lần chạy.</p>
                      <button onClick={() => go("runs")}>
                        Kiểm tra & chạy baseline
                      </button>
                    </div>
                  )}
                </section>
                <section className="research-note">
                  <span>PHẠM VI NGHIÊN CỨU</span>
                  <h2>Bắt đầu bằng một baseline có thể tái lập.</h2>
                  <p>
                    Từng nghiệm gắn với dữ liệu đầu vào, seed và phiên bản
                    engine. Phân biệt nghiệm khả thi, tối ưu có chứng minh và
                    giới hạn mô phỏng.
                  </p>
                  <a href="#diagnostics">
                    Xem môi trường tính toán <ArrowRight size={15} />
                  </a>
                </section>
              </div>
            </>
          )}
          {project && page === "floorplan" && (
            <section className="panel drawing-panel">
              <div className="panel-heading">
                <div>
                  <h2>Khu vực trưng bày</h2>
                  <span className="muted">
                    Input 01 & 02 · hình học theo mét
                  </span>
                </div>
                <div className="actions">
                  <button disabled={busy} onClick={addShelf}>
                    + Thêm kệ
                  </button>
                  <button
                    className="primary"
                    disabled={busy}
                    onClick={() => void saveDrawing()}
                  >
                    {busy ? "Đang lưu…" : "Lưu bản vẽ & kệ"}
                  </button>
                </div>
              </div>
              <div className="mode-bar">
                <label>
                  Chế độ bố trí
                  <select
                    aria-label="Chế độ bố trí"
                    value={mode}
                    onChange={(e) => {
                      setMode(e.target.value as "fixed" | "optimizable");
                      setDirty(true);
                    }}
                  >
                    <option value="optimizable">
                      Optimizable · T1 tìm vị trí
                    </option>
                    <option value="fixed">Fixed · giữ vị trí kệ</option>
                  </select>
                </label>
                <label>
                  Lối đi tối thiểu (m)
                  <input
                    aria-label="Lối đi tối thiểu"
                    type="number"
                    min="0.1"
                    step="0.1"
                    value={floor.min_aisle_m}
                    onChange={(e) => {
                      setFloor({
                        ...floor,
                        min_aisle_m: Number(e.target.value),
                      });
                      setDirty(true);
                    }}
                  />
                </label>
                <label>
                  Lưới (m)
                  <input
                    type="number"
                    min="0.1"
                    max="2"
                    step="0.1"
                    value={floor.grid_m}
                    onChange={(e) => {
                      setFloor({
                        ...floor,
                        grid_m: Math.max(0.1, Number(e.target.value)),
                      });
                      setDirty(true);
                    }}
                  />
                </label>
                <span className={dirty ? "draft" : "muted"}>
                  {dirty
                    ? "Có thay đổi chưa lưu"
                    : project.completion.floorplan
                      ? "Bản vẽ đã lưu"
                      : "Bản nháp · cần lưu"}
                </span>
              </div>
              <Suspense
                fallback={
                  <div className="notice">Loading floorplan editor...</div>
                }
              >
                <FloorplanEditor
                  key={project.id}
                  floor={floor}
                  shelves={shelves}
                  onFloor={(f) => {
                    setFloor(f);
                    setDirty(true);
                  }}
                  onShelves={(s) => {
                    setShelves(s);
                    setDirty(true);
                  }}
                />
              </Suspense>
            </section>
          )}
          {project &&
            sections.includes(page as Section) &&
            page !== "floorplan" && (
              <DataInputPage
                project={project}
                section={page as Exclude<Section, "floorplan">}
                busy={busy}
                onSave={(value) =>
                  act(async () => save(page as Section, value))
                }
              />
            )}
          {project && page === "runs" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>Thực thi T1 → T4</h2>
                <div className="actions">
                  <button
                    disabled={busy}
                    onClick={() =>
                      void act(async () =>
                        setValidation(await api.validate(project.id)),
                      )
                    }
                  >
                    Kiểm tra dữ liệu
                  </button>
                  <button
                    className="primary"
                    disabled={busy || !health?.worker_online}
                    onClick={() =>
                      void act(async () => {
                        const r = await api.enqueue(project.id);
                        setRuns([r, ...runs]);
                        setSelectedRun(r.id);
                        setMessage(`Đã xếp hàng ${r.id.slice(0, 8)}`);
                      })
                    }
                  >
                    <Play size={15} />
                    Chạy baseline
                  </button>
                </div>
              </div>
              {!health?.worker_online && (
                <p className="notice warning">
                  Worker chưa sẵn sàng. Khởi động worker theo README rồi tải
                  lại.
                </p>
              )}
              {validation && (
                <div
                  className={`notice ${validation.valid ? "success" : "error"}`}
                >
                  {validation.valid
                    ? "7 nhóm dữ liệu hợp lệ, sẵn sàng chạy."
                    : validation.errors.join(" · ")}
                </div>
              )}
              <div className="table-scroll">
                <table>
                  <thead>
                    <tr>
                      <th>Run ID</th>
                      <th>Trạng thái</th>
                      <th>Tầng</th>
                      <th>Revision</th>
                      <th>SHA-256 đầu vào</th>
                      <th>Thao tác</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((r) => (
                      <tr key={r.id}>
                        <td>
                          <code>{r.id.slice(0, 8)}</code>
                        </td>
                        <td>
                          <Badge status={r.status} />
                        </td>
                        <td>{r.stage}</td>
                        <td>{r.project_revision}</td>
                        <td>
                          <code title={r.input_sha256}>
                            {r.input_sha256.slice(0, 12)}
                          </code>
                        </td>
                        <td>
                          {activeStates.includes(r.status) ? (
                            <button
                              disabled={busy || r.status === "CANCEL_REQUESTED"}
                              onClick={() =>
                                void act(async () => {
                                  await api.cancel(r.id);
                                  setRuns(await api.runs(project.id));
                                })
                              }
                            >
                              Hủy
                            </button>
                          ) : (
                            <button
                              disabled={busy}
                              onClick={() =>
                                void act(async () => {
                                  const next = await api.replay(r.id);
                                  setRuns([next, ...runs]);
                                  setMessage(
                                    "Đã tạo lần replay từ snapshot gốc.",
                                  );
                                })
                              }
                            >
                              <RefreshCw size={13} />
                              Replay
                            </button>
                          )}
                          <button
                            onClick={() => {
                              setSelectedRun(r.id);
                              go("layout");
                            }}
                          >
                            Kết quả
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {!runs.length && (
                <div className="empty">
                  <p>
                    Chưa có lần chạy. Kiểm tra dữ liệu trước khi chạy baseline.
                  </p>
                </div>
              )}
              {runs
                .filter((r) => r.error)
                .map((r) => (
                  <p className="notice error" key={r.id}>
                    {r.id.slice(0, 8)} · {r.error?.code}: {r.error?.message}
                  </p>
                ))}
            </section>
          )}
          {project &&
            ["layout", "planogram", "simulation", "reports"].includes(page) && (
              <>
                {selectRun}
                {!result ? (
                  <section className="panel empty">
                    <Layers size={28} />
                    <h2>
                      {run ? `Trạng thái ${run.status}` : "Chưa có kết quả"}
                    </h2>
                    <p>
                      {run?.error?.message ||
                        "Chạy baseline T1–T4 để tạo phương án đầu tiên."}
                    </p>
                    <button onClick={() => go("runs")}>Đến lần chạy</button>
                  </section>
                ) : (
                  <>
                    <div className="result-meta">
                      <Badge status={run.status} />
                      <span>Đầu vào revision {run.project_revision}</span>
                      <code title={run.input_sha256}>
                        SHA {run.input_sha256.slice(0, 16)}
                      </code>
                    </div>
                    {page === "layout" && (
                      <section className="panel">
                        <div className="panel-heading">
                          <h2>Mặt bằng nghiệm T1</h2>
                          <span>{result.stages.T1.status}</span>
                        </div>
                        <Suspense
                          fallback={
                            <div className="notice">
                              Loading floorplan editor...
                            </div>
                          }
                        >
                          <FloorplanEditor
                            floor={result.floorplan}
                            shelves={result.stages.T1.shelves}
                            onFloor={() => {}}
                            onShelves={() => {}}
                            readonly
                          />
                        </Suspense>
                        <div className="assignment-list">
                          {Object.entries(result.stages.T2.assignment).map(
                            ([c, s]) => (
                              <span key={c}>
                                {c}
                                <ArrowRight size={12} />
                                <strong>{s}</strong>
                              </span>
                            ),
                          )}
                        </div>
                        <small className="muted">
                          Nghiệm kệ thuộc snapshot của lần chạy. Bản vẽ nền sẽ
                          dùng snapshot khi tải chi tiết bên dưới.
                        </small>
                      </section>
                    )}
                    {page === "planogram" && (
                      <PlanogramViewer result={result} />
                    )}
                    {page === "simulation" && (
                      <SimulationAnalytics result={result} />
                    )}
                    {page === "reports" && (
                      <ReportsPage
                        run={run}
                        result={result}
                        successful={successful}
                        comparison={comparison}
                        compareId={compareId}
                        setCompareId={setCompareId}
                      />
                    )}
                  </>
                )}
              </>
            )}
          {page === "diagnostics" && (
            <section className="panel">
              <div className="panel-heading">
                <h2>Trạng thái dịch vụ</h2>
                <button
                  onClick={() =>
                    void act(async () => setHealth(await api.health()))
                  }
                >
                  <RefreshCw size={14} />
                  Làm mới
                </button>
              </div>
              {health ? (
                <>
                  <div className="diagnostic-grid">
                    <span>
                      API<strong>{health.status}</strong>
                    </span>
                    <span>
                      Database<strong>{health.database}</strong>
                    </span>
                    <span>
                      Worker
                      <strong>
                        {health.worker_online ? "Online" : "Offline"}
                      </strong>
                    </span>
                    <span>
                      Python<strong>{health.runtime.python}</strong>
                    </span>
                  </div>
                  <p>
                    <strong>Source identity</strong>
                  </p>
                  <code className="hash">{health.runtime.source_sha256}</code>
                  <table>
                    <thead>
                      <tr>
                        <th>Thư viện</th>
                        <th>Phiên bản</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(health.runtime.packages).map(([k, v]) => (
                        <tr key={k}>
                          <td>{k}</td>
                          <td>{v}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </>
              ) : (
                <p>Chưa kết nối backend. Kiểm tra dịch vụ rồi làm mới.</p>
              )}
              <a
                href="http://127.0.0.1:8010/docs"
                target="_blank"
                rel="noreferrer"
              >
                Mở tài liệu API <ArrowRight size={14} />
              </a>
            </section>
          )}
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

function Badge({ status }: { status: string }) {
  return (
    <span className={`badge ${status.toLowerCase()}`}>
      {status.replaceAll("_", " ")}
    </span>
  );
}
