import { useEffect, useState } from "react";
import { api } from "../services/api";
import type { Health, Run } from "../types/models";

export function useRuntimeStatus(projectId: string | undefined) {
  const [health, setHealth] = useState<Health | null>(null);
  const [runs, setRuns] = useState<Run[]>([]);
  const [pollError, setPollError] = useState("");
  useEffect(() => {
    let alive = true;
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
    const timer = window.setInterval(() => void refresh(), 2000);
    return () => { alive = false; window.clearInterval(timer); };
  }, [projectId]);
  return { health, setHealth, runs, setRuns, pollError };
}
