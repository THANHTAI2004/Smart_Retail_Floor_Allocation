import { ArrowRight, RefreshCw } from "lucide-react";
import { api } from "../../services/api";
import type { WorkspaceModel } from "../../app/useWorkspace";

export function DiagnosticsPage({ model }: { model: WorkspaceModel }) {
  const { page, act, setHealth, health } = model;
  return (<>{page === "diagnostics" && (
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
  )}</>);
}
