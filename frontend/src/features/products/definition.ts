// Vai trò: Định nghĩa giao diện nhập nhóm sản phẩm, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
import sample from "../projects/sample";
export const productDefinition = {
  title: "Sản phẩm",
  defaultValue: sample.products,
  template: { ...sample.products.items[0], sku: "SKU" },
  note: "Kích thước theo mét; weight_kg theo kg. orientations hỗ trợ 0/90°. clearance_m là khoảng hở mỗi ô sản phẩm. Tải trọng áp dụng tổng hai mặt của từng tầng.",
};
