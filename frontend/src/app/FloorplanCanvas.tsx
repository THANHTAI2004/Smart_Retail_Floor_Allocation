// Vai trò: Nạp lười trình biên tập mặt bằng để chỉ tải phần canvas khi trang cần dùng.
import { lazy } from "react";
export const FloorplanEditor = lazy(() => import("../features/floorplan-editor/FloorplanEditor").then(module => ({ default: module.FloorplanEditor })));
