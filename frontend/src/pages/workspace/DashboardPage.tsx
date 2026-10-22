import { navigation } from "../../app/navigation";
import { Stat } from "../../components/Stat";
import { ArrowRight, ChartNoAxesCombined, Check, ChevronRight, Map, Play, SquareStack } from "lucide-react";
import type { Floorplan } from "../../types/models";
import { area } from "../../utils/geometry";
import { sections } from "../../app/useWorkspace";
import type { WorkspaceModel } from "../../app/useWorkspace";
import { Badge } from "../../components/Badge";

export function DashboardPage({ model }: { model: WorkspaceModel }) {
  const { project, page, completed, successful, go, runs, setSelectedRun } = model;
  return (<>{project && page === "dashboard" && (
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
  )}</>);
}
