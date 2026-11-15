// Vai trò: Đồng bộ trang đang mở với hash của URL và đăng ký dọn listener khi hook kết thúc.
import { useEffect, useState } from "react";

// Đồng bộ trang đang mở với hash của URL và đăng ký dọn listener khi hook kết thúc.
export function useHashRoute() {
  const [page, setPage] = useState(location.hash.slice(1) || "dashboard");
  useEffect(() => {
    // Đồng bộ trang với URL, dùng dashboard khi hash rỗng.
    const change = () => setPage(location.hash.slice(1) || "dashboard");
    addEventListener("hashchange", change);
    return () => removeEventListener("hashchange", change);
  }, []);
  return page;
}
