import { useState } from "react";
export const activeStates = ["QUEUED", "RUNNING", "CANCEL_REQUESTED"];

export function useRunState() {
  const [selectedRun, setSelectedRun] = useState("");
  const [compareId, setCompareId] = useState("");
  return { selectedRun, setSelectedRun, compareId, setCompareId };
}
