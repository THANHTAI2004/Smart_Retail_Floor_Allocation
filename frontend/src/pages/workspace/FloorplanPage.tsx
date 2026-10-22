import { Suspense } from "react";
import { FloorplanEditor } from "../../app/FloorplanCanvas";
import type { WorkspaceModel } from "../../app/useWorkspace";

export function FloorplanPage({ model }: { model: WorkspaceModel }) {
  const { project, page, busy, addShelf, saveDrawing, mode, setMode, setDirty, floor, setFloor, dirty, shelves, setShelves } = model;
  return (<>{project && page === "floorplan" && (
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
  )}</>);
}
