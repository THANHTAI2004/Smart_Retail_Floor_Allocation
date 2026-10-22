import { describe, expect, it } from "vitest";
import sample from "../../datasets/samples/small_store.json";
import type { Shelf } from "../src/types/models";
import {
  area,
  inside,
  shelfRect,
  shelfWarnings,
  snap,
} from "../src/utils/geometry";

describe("floorplan editing math", () => {
  it("computes real area independent of winding and origin", () => {
    expect(
      area([
        [0, 0],
        [12, 0],
        [12, 9],
        [0, 9],
      ]),
    ).toBe(108);
    expect(
      area([
        [2, 3],
        [2, 12],
        [14, 12],
        [14, 3],
      ]),
    ).toBe(108);
  });
  it("snaps positive and negative coordinates", () => {
    expect(snap(1.36, 0.25)).toBe(1.25);
    expect(snap(-1.36, 0.25)).toBe(-1.25);
  });
  it("detects inside and outside a concave polygon", () => {
    const polygon: [number, number][] = [
      [0, 0],
      [4, 0],
      [4, 1],
      [1, 1],
      [1, 4],
      [0, 4],
    ];
    expect(inside([0.5, 3], polygon)).toBe(true);
    expect(inside([2, 2], polygon)).toBe(false);
  });
  it("rotates shelf geometry and flags overlaps", () => {
    const shelf = { ...sample.shelves.items[0], x: 1, y: 1 } as Shelf;
    expect(shelfRect({ ...shelf, rotation: 90 })).toEqual({
      x: 1,
      y: 1,
      w: 0.6,
      h: 2,
    });
    expect(
      shelfWarnings(
        [shelf, { ...shelf, id: "S02" }],
        [
          [0, 0],
          [12, 0],
          [12, 9],
          [0, 9],
        ],
      ),
    ).toContain("S02 / S01: chồng lấn");
  });
});
