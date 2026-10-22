import { Play, RefreshCw } from "lucide-react";
import { api } from "../../services/api";
import type { WorkspaceModel } from "../../app/useWorkspace";
import { Badge } from "../../components/Badge";
import { activeStates } from "../../app/useRunState";

export function OptimizationRunsPage({ model }: { model: WorkspaceModel }) {
  const { project, page, busy, act, setValidation, health, setRuns, runs, setSelectedRun, setMessage, validation, go } = model;
  return (<>{project && page === "runs" && (
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
  )}</>);
}
