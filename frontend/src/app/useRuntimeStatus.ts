// Vai trò: Poll tình trạng dịch vụ và các lần chạy mỗi hai giây.
// Cleanup ngăn phản hồi cũ cập nhật state sau khi đổi dự án.
import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { Health, Run } from "../types/models";

// Poll tình trạng dịch vụ và các lần chạy mỗi hai giây. Cleanup ngăn phản hồi cũ cập nhật state sau khi đổi dự án.
export function useRuntimeStatus(projectId: string | undefined) {
  const [health, setHealth] = useState<Health | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [pollError, setPollError] = useState("");
  useEffect(() => {
    // Cờ này ngăn phản hồi bất đồng bộ của dự án cũ cập nhật state sau khi effect đã được dọn.
    let alive = true;
    // Tải lại trạng thái và dữ liệu quan sát; phản hồi chỉ cập nhật state khi effect còn hiệu lực.
    const refresh = async () => {
      try {
        const [h, values] = await Promise.all([
          api.health(), projectId ? api.runs(projectId) : Promise.resolve([]),
        ]);
        if (alive) { setHealth(h); setRuns(values); setPollError(""); }
      } catch (error) {
        if (alive) setPollError(String(error));
      }
    };
    setRuns([]);
    void refresh();
    // Poll riêng cho quan sát tiến độ; cleanup bên dưới gỡ timer khi đổi dự án hoặc unmount.
    const timer = window.setInterval(() => void refresh(), 2000);
    return () => { alive = false; window.clearInterval(timer); };
  }, [projectId]);
  return { health, setHealth, runs, setRuns, pollError };
}
