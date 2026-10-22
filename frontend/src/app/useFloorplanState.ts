import { useCallback, useState } from "react";
import sample from "../features/projects/sample";
import type { Floorplan, Project, Shelf } from "../types/models";

export function useFloorplanState() {
  const [floor, setFloor] = useState<Floorplan>(sample.floorplan as unknown as Floorplan);
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [mode, setMode] = useState<"fixed" | "optimizable">("optimizable");
  const [dirty, setDirty] = useState(false);
  const resetDrawing = useCallback((project: Project) => {
    setFloor((project.sections.floorplan as unknown as Floorplan) || sample.floorplan as unknown as Floorplan);
    setShelves((project.sections.shelves?.items as Shelf[]) || []);
    setMode((project.sections.shelves?.layout_mode as "fixed" | "optimizable") || "optimizable");
    setDirty(false);
  }, []);
  return { floor, setFloor, shelves, setShelves, mode, setMode, dirty, setDirty, resetDrawing };
}
