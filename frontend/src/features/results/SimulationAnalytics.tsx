import type { RunResult } from "../../types/models";
import { Stat } from "../../components/Stat";

export function SimulationAnalytics({ result }: { result: RunResult }) {
  return (
    <>
      <div className="stat-grid">
        <Stat
          label="HÀNH TRÌNH HOÀN TẤT"
          value={String(result.stages.T4.metrics.completed)}
          unit="lượt"
        />
        <Stat
          label="QUÃNG ĐƯỜNG TRUNG BÌNH"
          value={result.stages.T4.metrics.mean_distance_m.toFixed(2)}
          unit="m"
        />
        <Stat
          label="CHỜ TẠI KỆ TRUNG BÌNH"
          value={result.stages.T4.metrics.mean_wait_s.toFixed(2)}
          unit="giây"
        />
        <Stat
          label="ĐƠN TRỄ"
          value={String(result.stages.T4.metrics.late_orders)}
          unit="đơn"
        />
      </div>
      <section className="panel">
        <h2>Giả định mô phỏng</h2>
        <ul className="assumptions">
          {result.stages.T4.assumptions.map((a) => (
            <li key={a}>{a}</li>
          ))}
        </ul>
      </section>
    </>
  );
}
