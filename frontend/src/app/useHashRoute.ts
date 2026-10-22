import { useEffect, useState } from "react";

export function useHashRoute() {
  const [page, setPage] = useState(location.hash.slice(1) || "dashboard");
  useEffect(() => {
    const change = () => setPage(location.hash.slice(1) || "dashboard");
    addEventListener("hashchange", change);
    return () => removeEventListener("hashchange", change);
  }, []);
  return page;
}
