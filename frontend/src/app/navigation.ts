import { Activity, Box, ChartNoAxesCombined, ClipboardList, FileChartColumn, FolderOpen, Grid2X2, Layers, LayoutDashboard, Map, Play, ShoppingBasket, SlidersHorizontal, SquareStack, Users } from "lucide-react";

export const navigation = [
  {
    id: "dashboard",
    title: "Tổng quan",
    icon: LayoutDashboard,
    group: "WORKSPACE",
  },
  { id: "projects", title: "Dự án", icon: FolderOpen },
  { id: "research", title: "Thực nghiệm nghiên cứu", icon: ChartNoAxesCombined },
  {
    id: "floorplan",
    title: "Mặt bằng",
    icon: Map,
    group: "THIẾT KẾ & DỮ LIỆU",
  },
  { id: "shelves", title: "Cấu hình kệ", icon: SquareStack },
  { id: "categories", title: "Ngành hàng", icon: Grid2X2 },
  { id: "products", title: "Sản phẩm", icon: Box },
  { id: "demand", title: "Nhu cầu & hành vi", icon: Users },
  { id: "orders", title: "Đơn hàng", icon: ShoppingBasket },
  {
    id: "optimization",
    title: "Cấu hình tối ưu",
    icon: SlidersHorizontal,
    group: "TỐI ƯU & PHÂN TÍCH",
  },
  { id: "runs", title: "Lần chạy", icon: Play },
  { id: "layout", title: "Kết quả mặt bằng", icon: Layers },
  { id: "planogram", title: "Planogram", icon: ClipboardList },
  {
    id: "simulation",
    title: "Mô phỏng & phân tích",
    icon: ChartNoAxesCombined,
  },
  { id: "reports", title: "So sánh & báo cáo", icon: FileChartColumn },
  { id: "diagnostics", title: "Chẩn đoán hệ thống", icon: Activity },
];
export const descriptions: Record<string, string> = {
  dashboard: "Từ dữ liệu cửa hàng đến phương án có thể kiểm chứng.",
  projects: "Lưu riêng dữ liệu, cấu hình và kết quả của từng nghiên cứu.",
  research: "Dataset tổng hợp, campaign thực, checkpoint, replay và báo cáo có kiểm chứng.",
  floorplan:
    "Vẽ theo kích thước thực. Đặt kệ, lối đi và vùng cấm trong cùng hệ tọa độ.",
  shelves:
    "Kích thước vật lý theo mét. Từng tầng kệ có sức chứa và tải trọng riêng.",
  categories: "Nhu cầu, chiều rộng yêu cầu và ràng buộc phân bổ ngành hàng.",
  products: "Kích thước SKU, mặt trưng bày, hướng đặt và giới hạn xếp chồng.",
  demand: "Khai báo giỏ hàng và giả định hành vi trước khi mô phỏng.",
  orders: "Đơn hàng và dòng đơn được lưu riêng với khóa tham chiếu SKU.",
  optimization:
    "Baseline T1 lưới → T2 MILP/greedy → T3 first-fit → T4 mô phỏng.",
  runs: "Mỗi lần chạy giữ nguyên bản chụp đầu vào và dấu vết tính toán.",
  layout: "Nghiệm T1 đã kiểm tra ranh giới, khoảng cách kệ và vật cản.",
  planogram: "Vị trí và sức chứa sản phẩm theo tầng, mặt kệ.",
  simulation:
    "Tuyến đường trên lưới và hàng đợi phục vụ tại kệ; hành vi khách được mô phỏng.",
  reports: "Đối chiếu các nghiệm đã lưu và xuất dữ liệu có truy vết.",
  diagnostics: "Kết nối cơ sở dữ liệu, worker và phiên bản thư viện đang chạy.",
};

