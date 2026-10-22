import type { RunResult } from "../../types/models";

export function PlanogramViewer({ result }: { result: RunResult }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <h2>Sản phẩm theo tầng kệ</h2>
        <span>{result.stages.T3.status}</span>
      </div>
      <div className="planogram">
        {result.stages.T1.shelves.map((s) => (
          <div className="planogram-shelf" key={s.id}>
            <h3>
              {s.id}{" "}
              <small>
                {s.width_m} × {s.depth_m} m
              </small>
            </h3>
            {Array.from({ length: s.faces }, (_, face) =>
              s.levels.map((level) => (
                <div key={`${face}-${level.id}`}>
                  <span className="level-label">
                    Mặt {face + 1} · {level.id} · {level.width_m} m
                  </span>
                  <div className="shelf-level">
                    {result.stages.T3.placements
                      .filter(
                        (p) =>
                          p.shelf_id === s.id &&
                          p.level_id === level.id &&
                          p.face === face,
                      )
                      .map((p) => (
                        <div
                          key={p.sku}
                          className="product-block"
                          style={{
                            left: `${(p.x_m / level.width_m) * 100}%`,
                            width: `${(p.width_m / level.width_m) * 100}%`,
                          }}
                          title={`${p.sku} · ${p.capacity_units} đơn vị`}
                        >
                          <strong>{p.sku}</strong>
                          <small>{p.capacity_units} sp</small>
                        </div>
                      ))}
                  </div>
                </div>
              )),
            )}
          </div>
        ))}
      </div>
      <div className="table-scroll">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Kệ / tầng / mặt</th>
              <th>Vị trí x (m)</th>
              <th>Rộng (m)</th>
              <th>Sức chứa</th>
            </tr>
          </thead>
          <tbody>
            {result.stages.T3.placements.map((p) => (
              <tr key={p.sku}>
                <td>{p.sku}</td>
                <td>
                  {p.shelf_id} / {p.level_id} / {p.face + 1}
                </td>
                <td>{p.x_m.toFixed(2)}</td>
                <td>{p.width_m.toFixed(2)}</td>
                <td>{p.capacity_units}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
