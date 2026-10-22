export type Point = [number, number];
interface Level {
  id: string;
  width_m: number;
  depth_m: number;
  height_m: number;
  max_load_kg?: number | null;
}
export interface Shelf {
  id: string;
  kind: string;
  width_m: number;
  depth_m: number;
  height_m: number;
  levels: Level[];
  x: number | null;
  y: number | null;
  rotation: 0 | 90;
  faces: 1 | 2;
  locked: boolean;
}
export interface Floorplan {
  units: "m";
  boundary: Point[];
  entrance: Point;
  obstacles: Point[][];
  min_aisle_m: number;
  grid_m: number;
}
export type Section =
  | "floorplan"
  | "shelves"
  | "categories"
  | "products"
  | "demand"
  | "orders"
  | "optimization";
type Inputs = Partial<Record<Section, Record<string, unknown>>>;
export interface Project {
  id: string;
  name: string;
  revision: number;
  created_at: string;
  sections: Inputs;
  completion: Record<Section, boolean>;
}
interface Placement {
  sku: string;
  shelf_id: string;
  level_id: string;
  face: number;
  x_m: number;
  width_m: number;
  capacity_units: number;
}
export interface RunResult {
  input_sha256: string;
  status: string;
  floorplan: Floorplan;
  integrated?: {
    algorithm: string;
    selected_candidate: number;
    requested_candidates: number;
    evaluated_candidates: number;
    pareto_candidates: number[];
    termination: string;
    global_optimality_proven: boolean;
    candidates: { candidate: number; status: string; score?: number; components?: number[] }[];
    assumptions: string[];
    normalization: string[];
  };
  stages: {
    T1: { shelves: Shelf[]; status: string };
    T2: {
      assignment: Record<string, string>;
      status: string;
      objective: number;
    };
    T3: { placements: Placement[]; status: string };
    T4: {
      metrics: {
        completed: number;
        mean_distance_m: number;
        mean_wait_s: number;
        late_orders: number;
      };
      assumptions: string[];
    };
  };
}
export interface Run {
  id: string;
  project_id: string;
  project_revision: number;
  input_sha256: string;
  status: string;
  stage: string;
  created_at: string;
  result: RunResult | null;
  result_sha256: string | null;
  error: { code: string; message: string } | null;
}
export interface Health {
  status: string;
  database: string;
  worker_online: boolean;
  runtime: {
    python: string;
    source_sha256: string;
    packages: Record<string, string>;
  };
}
