import { lazy } from "react";
export const FloorplanEditor = lazy(() => import("../features/floorplan-editor/FloorplanEditor").then(module => ({ default: module.FloorplanEditor })));
