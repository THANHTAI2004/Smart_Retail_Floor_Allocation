// Vai trò: Giữ lần chạy được chọn và lần chạy dùng so sánh.
// Danh sách activeStates xác định trạng thái còn hoạt động.
import { useState } from "react";
export const activeStates = ["QUEUED", "RUNNING", "CANCEL_REQUESTED"];

// Giữ lần chạy được chọn và lần chạy dùng so sánh. Danh sách activeStates xác định trạng thái còn hoạt động.
export function useRunState() {
  const [selectedRun, setSelectedRun] = useState("");
  const [compareId, setCompareId] = useState("");
  return { selectedRun, setSelectedRun, compareId, setCompareId };
}
