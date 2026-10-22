import { useEffect, useRef, useState } from "react";
import {
  Circle,
  Group,
  Image as KonvaImage,
  Layer,
  Line,
  Rect,
  Stage,
  Text,
} from "react-konva";
import type { Floorplan, Point, Shelf } from "../../types/models";
import { area, shelfRect, shelfWarnings, snap } from "../../utils/geometry";

interface Props {
  floor: Floorplan;
  shelves: Shelf[];
  onFloor: (floor: Floorplan) => void;
  onShelves: (shelves: Shelf[]) => void;
  readonly?: boolean;
}
export function FloorplanEditor({
  floor,
  shelves,
  onFloor: publishFloor,
  onShelves: publishShelves,
  readonly = false,
}: Props) {
  const container = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(800);
  const [tool, setTool] = useState<
    "select" | "boundary" | "obstacle" | "entrance"
  >("select");
  const [drawing, setDrawing] = useState<Point[]>([]);
  const [selected, setSelected] = useState<string>("");
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [imageWidth, setImageWidth] = useState(0);
  const [gridSnap, setGridSnap] = useState(true);
  const [past, setPast] = useState<{ floor: Floorplan; shelves: Shelf[] }[]>([]);
  const [future, setFuture] = useState<{ floor: Floorplan; shelves: Shelf[] }[]>([]);
  const remember = () => {
    setPast((items) => [...items.slice(-49), structuredClone({ floor, shelves })]);
    setFuture([]);
  };
  const onFloor = (next: Floorplan) => { remember(); publishFloor(next); };
  const onShelves = (next: Shelf[]) => { remember(); publishShelves(next); };
  const restore = (direction: "undo" | "redo") => {
    const source = direction === "undo" ? past : future;
    const previous = source.at(-1);
    if (!previous) return;
    const current = structuredClone({ floor, shelves });
    if (direction === "undo") {
      setPast(past.slice(0, -1)); setFuture([...future, current]);
    } else {
      setFuture(future.slice(0, -1)); setPast([...past, current]);
    }
    publishFloor(previous.floor); publishShelves(previous.shelves);
    setDrawing([]);
  };
  useEffect(() => {
    const observer = new ResizeObserver((entries) =>
      setWidth(entries[0].contentRect.width),
    );
    if (container.current) observer.observe(container.current);
    return () => observer.disconnect();
  }, []);
  const minx = Math.min(0, ...floor.boundary.map((p) => p[0])) - 1;
  const miny = Math.min(0, ...floor.boundary.map((p) => p[1])) - 1;
  const maxx = Math.max(10, ...floor.boundary.map((p) => p[0])) + 1;
  const maxy = Math.max(8, ...floor.boundary.map((p) => p[1])) + 1;
  const scale = Math.min((width - 28) / (maxx - minx), 470 / (maxy - miny));
  const stageHeight = Math.max(360, (maxy - miny) * scale + 28);
  const px = (x: number) => (x - minx) * scale + 14;
  const py = (y: number) => (y - miny) * scale + 14;
  const points = (value: Point[]) => value.flatMap(([x, y]) => [px(x), py(y)]);
  const coordinate = (x: number, y: number): Point => {
    const step = gridSnap ? floor.grid_m : 0.01;
    return [
      snap((x - 14) / scale + minx, step),
      snap((y - 14) / scale + miny, step),
    ];
  };
  const updateShelf = (id: string, update: Partial<Shelf>) =>
    onShelves(shelves.map((s) => (s.id === id ? { ...s, ...update } : s)));
  const active = shelves.find((s) => s.id === selected);
  const warnings = shelfWarnings(shelves, floor.boundary);
  function finish() {
    if (drawing.length < 3) return;
    onFloor(
      tool === "boundary"
        ? { ...floor, boundary: drawing }
        : { ...floor, obstacles: [...floor.obstacles, drawing] },
    );
    setDrawing([]);
    setTool("select");
  }
  return (
    <div className="editor" ref={container}>
      {!readonly && (
        <div className="canvas-toolbar" aria-label="Công cụ mặt bằng">
          <button disabled={!past.length} onClick={() => restore("undo")}>Hoàn tác</button>
          <button disabled={!future.length} onClick={() => restore("redo")}>Làm lại</button>
          {(["select", "boundary", "obstacle", "entrance"] as const).map(
            (t, i) => (
              <button
                key={t}
                className={tool === t ? "active" : ""}
                onClick={() => {
                  setTool(t);
                  setDrawing([]);
                }}
              >
                {["Chọn / kéo", "Vẽ đa giác", "Vật cản", "Cửa vào"][i]}
              </button>
            ),
          )}
          {drawing.length > 0 && (
            <>
              <button onClick={finish} disabled={drawing.length < 3}>
                Khép đa giác ({drawing.length})
              </button>
              <button onClick={() => setDrawing(drawing.slice(0, -1))}>
                Bỏ điểm cuối
              </button>
            </>
          )}
          <label className="check">
            <input
              type="checkbox"
              checked={gridSnap}
              onChange={(e) => setGridSnap(e.target.checked)}
            />
            Snap {floor.grid_m} m
          </label>
        </div>
      )}
      <div
        className="canvas-wrap"
        role="img"
        aria-label="Bản vẽ mặt bằng theo mét; dùng bảng tọa độ bên dưới để chỉnh bằng bàn phím"
      >
        <Stage
          width={width}
          height={stageHeight}
          onMouseDown={(event) => {
            if (readonly || tool === "select") return;
            const p = event.target.getStage()?.getPointerPosition();
            if (!p) return;
            const value = coordinate(p.x, p.y);
            if (tool === "entrance") {
              onFloor({ ...floor, entrance: value });
              setTool("select");
            } else setDrawing([...drawing, value]);
          }}
        >
          <Layer>
            <Rect width={width} height={520} fill="#f5f7f3" />
            {image && imageWidth > 0 && (
              <KonvaImage
                image={image}
                x={px(0)}
                y={py(0)}
                width={imageWidth * scale}
                height={(imageWidth * scale * image.height) / image.width}
                opacity={0.35}
              />
            )}
            {Array.from(
              {
                length: Math.min(200, Math.ceil((maxx - minx) / floor.grid_m)),
              },
              (_, i) => (
                <Line
                  key={`x${i}`}
                  points={[
                    px(minx + i * floor.grid_m),
                    py(miny),
                    px(minx + i * floor.grid_m),
                    py(maxy),
                  ]}
                  stroke="#dce3dc"
                  strokeWidth={0.6}
                />
              ),
            )}
            {Array.from(
              {
                length: Math.min(200, Math.ceil((maxy - miny) / floor.grid_m)),
              },
              (_, i) => (
                <Line
                  key={`y${i}`}
                  points={[
                    px(minx),
                    py(miny + i * floor.grid_m),
                    px(maxx),
                    py(miny + i * floor.grid_m),
                  ]}
                  stroke="#dce3dc"
                  strokeWidth={0.6}
                />
              ),
            )}
            <Line
              points={points(floor.boundary)}
              closed
              fill="rgba(235,242,232,0.6)"
              stroke="#476757"
              strokeWidth={2}
            />
            {floor.boundary.map((p, i) => {
              const q = floor.boundary[(i + 1) % floor.boundary.length];
              return (
                <Group key={i}>
                  <Text
                    x={(px(p[0]) + px(q[0])) / 2 + 5}
                    y={(py(p[1]) + py(q[1])) / 2 - 15}
                    text={`${Math.hypot(q[0] - p[0], q[1] - p[1]).toFixed(2)} m`}
                    fontSize={11}
                    fill="#526355"
                  />
                  <Circle
                    x={px(p[0])}
                    y={py(p[1])}
                    radius={5}
                    fill="#fff"
                    stroke="#285342"
                    draggable={!readonly && tool === "select"}
                    onDragEnd={(e) =>
                      onFloor({
                        ...floor,
                        boundary: floor.boundary.map((v, j) =>
                          i === j ? coordinate(e.target.x(), e.target.y()) : v,
                        ),
                      })
                    }
                  />
                </Group>
              );
            })}
            {floor.obstacles.map((p, i) => (
              <Line
                key={i}
                points={points(p)}
                closed
                fill="#bac2b9"
                stroke="#7e887d"
                dash={[4, 3]}
              />
            ))}
            {shelves.map((s, i) => {
              const r = shelfRect(s);
              const missing = s.x === null;
              return (
                <Group
                  key={s.id}
                  x={px(missing ? 1 + i * 2.5 : r.x)}
                  y={py(missing ? 2 : r.y)}
                  draggable={!readonly && tool === "select"}
                  onClick={() => setSelected(s.id)}
                  onTap={() => setSelected(s.id)}
                  onDragEnd={(e) => {
                    const [x, y] = coordinate(e.target.x(), e.target.y());
                    updateShelf(s.id, { x, y });
                  }}
                >
                  <Rect
                    width={r.w * scale}
                    height={r.h * scale}
                    fill={selected === s.id ? "#d9a34b" : "#407363"}
                    stroke={selected === s.id ? "#92621b" : "#244d40"}
                    strokeWidth={2}
                    cornerRadius={2}
                    opacity={missing ? 0.45 : 1}
                  />
                  <Text text={s.id} x={4} y={4} fontSize={11} fill="#fff" />
                  <Text
                    text={`${s.width_m} × ${s.depth_m} m${missing ? " · chưa đặt" : ""}`}
                    visible={scale >= 35 || selected === s.id}
                    x={0}
                    y={r.h * scale + 5}
                    fontSize={10}
                    fill="#284b3c"
                  />
                </Group>
              );
            })}
            <Circle
              x={px(floor.entrance[0])}
              y={py(floor.entrance[1])}
              radius={7}
              fill="#c5753a"
              stroke="#fff"
              strokeWidth={2}
            />
            <Text
              x={px(floor.entrance[0]) + 10}
              y={py(floor.entrance[1]) - 5}
              text="CỬA VÀO"
              fontSize={10}
              fill="#8f5026"
            />
            {drawing.length > 0 && (
              <Line
                points={points(drawing)}
                stroke="#ca773b"
                strokeWidth={2}
                dash={[5, 3]}
              />
            )}
            {Array.from({ length: Math.floor(maxx - minx) }, (_, i) => (
              <Text
                key={i}
                x={px(minx + i)}
                y={3}
                text={`${(minx + i).toFixed(0)}`}
                fontSize={9}
                fill="#718073"
              />
            ))}
            <Line
              points={[25, stageHeight - 28, 25 + scale, stageHeight - 28]}
              stroke="#264c3c"
              strokeWidth={3}
            />
            <Text
              text="1 m"
              x={25}
              y={stageHeight - 20}
              fontSize={10}
              fill="#264c3c"
            />
          </Layer>
        </Stage>
      </div>
      <div className="canvas-status">
        <span>Diện tích {area(floor.boundary).toFixed(2)} m²</span>
        <span>Tọa độ (x, y) · mét · y hướng xuống</span>
        <span>{shelves.length} kệ</span>
      </div>
      {warnings.length > 0 && (
        <div className="notice warning">
          {warnings.join(" · ")}. Backend sẽ kiểm tra đầy đủ hình học khi chạy
          T1.
        </div>
      )}
      {!readonly && (
        <div className="editor-details">
          <details>
            <summary>Tọa độ & kích thước cạnh</summary>
            <div className="vertices">
              {floor.boundary.map((p, i) => (
                <div className="vertex" key={i}>
                  <strong>Đỉnh {i + 1}</strong>
                  {p.map((v, axis) => (
                    <label key={axis}>
                      {axis === 0 ? "x (m)" : "y (m)"}
                      <input
                        type="number"
                        step="0.1"
                        value={v}
                        onChange={(e) => {
                          const updated: Point = [...p];
                          updated[axis] = Number(e.target.value);
                          onFloor({
                            ...floor,
                            boundary: floor.boundary.map((q, j) =>
                              i === j ? updated : q,
                            ),
                          });
                        }}
                      />
                    </label>
                  ))}
                  <label>
                    Cạnh kế (m)
                    <input
                      type="number"
                      step="0.1"
                      min="0.1"
                      value={Number(
                        Math.hypot(
                          floor.boundary[(i + 1) % floor.boundary.length][0] -
                            p[0],
                          floor.boundary[(i + 1) % floor.boundary.length][1] -
                            p[1],
                        ).toFixed(3),
                      )}
                      onChange={(e) => {
                        const j = (i + 1) % floor.boundary.length,
                          q = floor.boundary[j];
                        const len = Math.hypot(q[0] - p[0], q[1] - p[1]);
                        if (!len) return;
                        const ratio = Number(e.target.value) / len;
                        onFloor({
                          ...floor,
                          boundary: floor.boundary.map((v, idx) =>
                            idx === j
                              ? [
                                  p[0] + (q[0] - p[0]) * ratio,
                                  p[1] + (q[1] - p[1]) * ratio,
                                ]
                              : v,
                          ),
                        });
                      }}
                    />
                  </label>
                </div>
              ))}
            </div>
          </details>
          <details open={!!active}>
            <summary>Kệ được chọn</summary>
            <label>
              Mã kệ
              <select
                value={selected}
                onChange={(e) => setSelected(e.target.value)}
              >
                <option value="">Chọn kệ</option>
                {shelves.map((s) => (
                  <option key={s.id}>{s.id}</option>
                ))}
              </select>
            </label>
            {active && (
              <div className="form-grid">
                {(["x", "y"] as const).map((axis) => (
                  <label key={axis}>
                    {axis} (m)
                    <input
                      type="number"
                      step="0.1"
                      value={active[axis] ?? ""}
                      onChange={(e) =>
                        updateShelf(active.id, {
                          [axis]:
                            e.target.value === ""
                              ? null
                              : Number(e.target.value),
                        })
                      }
                    />
                  </label>
                ))}
                <label>
                  Hướng
                  <select
                    value={active.rotation}
                    onChange={(e) =>
                      updateShelf(active.id, {
                        rotation: Number(e.target.value) as 0 | 90,
                      })
                    }
                  >
                    <option value="0">0°</option>
                    <option value="90">90°</option>
                  </select>
                </label>
                <label className="check">
                  <input
                    type="checkbox"
                    checked={active.locked}
                    onChange={(e) =>
                      updateShelf(active.id, { locked: e.target.checked })
                    }
                  />
                  Khóa vị trí trong T1
                </label>
              </div>
            )}
          </details>
          <details>
            <summary>Ảnh tham chiếu & vật cản</summary>
            <label>
              Ảnh nền (chỉ lưu trong phiên này)
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  const url = URL.createObjectURL(file);
                  const img = new window.Image();
                  img.onload = () => {
                    setImage(img);
                    URL.revokeObjectURL(url);
                  };
                  img.src = url;
                }}
              />
            </label>
            {image && (
              <label>
                Hiệu chuẩn: chiều rộng thực của toàn ảnh (m)
                <input
                  type="number"
                  min="0"
                  step="0.1"
                  value={imageWidth}
                  onChange={(e) => setImageWidth(Number(e.target.value))}
                />
                <small>
                  Ảnh chỉ hiện sau khi nhập chiều rộng đã đo; không suy ra kích
                  thước từ pixel.
                </small>
              </label>
            )}
            <button
              onClick={() =>
                onFloor({ ...floor, obstacles: floor.obstacles.slice(0, -1) })
              }
              disabled={!floor.obstacles.length}
            >
              Bỏ vật cản cuối
            </button>
          </details>
        </div>
      )}
    </div>
  );
}
