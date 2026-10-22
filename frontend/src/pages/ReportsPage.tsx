import { ArrowDownToLine } from "lucide-react";
import type { Run, RunResult } from "../types/models";

export function ReportsPage({
  run,
  result,
  successful,
  comparison,
  compareId,
  setCompareId,
}: {
  run: Run;
  result: RunResult;
  successful: Run[];
  comparison?: RunResult | null;
  compareId: string;
  setCompareId: (id: string) => void;
}) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Xuất & so sánh phương án</h2>
        <div className="actions">
          <a
            className="button primary"
            href={`/api/runs/${run.id}/report?format=json`}
            download
          >
            <ArrowDownToLine size={14} />
            Báo cáo JSON
          </a>
          <a
            className="button"
            href={`/api/runs/${run.id}/report?format=csv`}
            download
          >
            Planogram CSV
          </a>
        </div>
      </div>
      <label>
        So với lần chạy
        <select
          aria-label="So sánh với lần chạy"
          value={compareId}
          onChange={(e) => setCompareId(e.target.value)}
        >
          <option value="">Chọn phương án đối chiếu</option>
          {successful
            .filter((r) => r.id !== run.id)
            .map((r) => (
              <option key={r.id} value={r.id}>
                {r.id.slice(0, 8)} · revision {r.project_revision}
              </option>
            ))}
        </select>
      </label>
      <table>
        <thead>
          <tr>
            <th>Chỉ số</th>
            <th>Phương án đang chọn</th>
            <th>Đối chiếu</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>T2 khoảng cách chuẩn hóa</td>
            <td>{result.stages.T2.objective.toFixed(4)}</td>
            <td>{comparison?.stages.T2.objective.toFixed(4) || "—"}</td>
          </tr>
          <tr>
            <td>Quãng đường TB (m)</td>
            <td>{result.stages.T4.metrics.mean_distance_m.toFixed(2)}</td>
            <td>
              {comparison?.stages.T4.metrics.mean_distance_m.toFixed(2) || "—"}
            </td>
          </tr>
          <tr>
            <td>Chờ tại kệ TB (s)</td>
            <td>{result.stages.T4.metrics.mean_wait_s.toFixed(2)}</td>
            <td>
              {comparison?.stages.T4.metrics.mean_wait_s.toFixed(2) || "—"}
            </td>
          </tr>
        </tbody>
      </table>
      <p className="muted">
        Báo cáo JSON gồm snapshot đầu vào, cấu hình, runtime identity, kết quả
        và checksum.
      </p>
      {result.integrated && (
        <section aria-label="So sánh phương án liên tầng">
          <h3>Đánh giá liên tầng</h3>
          <p>Chọn phương án {result.integrated.selected_candidate} trong {result.integrated.evaluated_candidates}/{result.integrated.requested_candidates} phương án.
            {" "}Điều kiện dừng: {result.integrated.termination}. Chưa chứng minh tối ưu toàn cục.</p>
          <table>
            <thead><tr><th>Phương án</th><th>Trạng thái</th><th>Điểm chuẩn hóa</th><th>Không bị trội</th></tr></thead>
            <tbody>{result.integrated.candidates.map((c) => (
              <tr key={c.candidate}><td>{c.candidate}</td><td>{c.status}</td><td>{c.score?.toFixed(4) ?? "—"}</td>
                <td>{result.integrated!.pareto_candidates.includes(c.candidate) ? "Có" : "—"}</td></tr>
            ))}</tbody>
          </table>
          <details><summary>Chuẩn hóa và giả định đánh giá</summary>
            <ul>{[...result.integrated.normalization, ...result.integrated.assumptions].map((s) => <li key={s}>{s}</li>)}</ul>
          </details>
        </section>
      )}
    </section>
  );
}
