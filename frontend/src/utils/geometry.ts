import type { Point, Shelf } from "../types/models";

export const snap = (value: number, step: number) =>
  Math.round(value / step) * step;
export function area(points: Point[]): number {
  return Math.abs(
    points.reduce((sum, p, i) => {
      const q = points[(i + 1) % points.length];
      return sum + p[0] * q[1] - q[0] * p[1];
    }, 0) / 2,
  );
}
export function inside(point: Point, polygon: Point[]): boolean {
  let result = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
    const [x, y] = polygon[i],
      [xx, yy] = polygon[j];
    if (
      y > point[1] !== yy > point[1] &&
      point[0] < ((xx - x) * (point[1] - y)) / (yy - y) + x
    )
      result = !result;
  }
  return result;
}
export function shelfRect(s: Shelf) {
  return {
    x: s.x ?? 0,
    y: s.y ?? 0,
    w: s.rotation === 90 ? s.depth_m : s.width_m,
    h: s.rotation === 90 ? s.width_m : s.depth_m,
  };
}
export function shelfWarnings(shelves: Shelf[], polygon: Point[]): string[] {
  const warnings: string[] = [];
  for (const s of shelves.filter((s) => s.x !== null)) {
    const r = shelfRect(s);
    const epsilon = 0.00001;
    if (
      ![
        [r.x + epsilon, r.y + epsilon],
        [r.x + r.w - epsilon, r.y + epsilon],
        [r.x + r.w - epsilon, r.y + r.h - epsilon],
        [r.x + epsilon, r.y + r.h - epsilon],
      ].every((p) => inside(p as Point, polygon))
    )
      warnings.push(`${s.id}: vượt ranh giới (kiểm tra nhanh)`);
    for (const other of shelves.filter((x) => x.id < s.id && x.x !== null)) {
      const q = shelfRect(other);
      if (
        r.x < q.x + q.w &&
        r.x + r.w > q.x &&
        r.y < q.y + q.h &&
        r.y + r.h > q.y
      )
        warnings.push(`${s.id} / ${other.id}: chồng lấn`);
    }
  }
  return warnings;
}
