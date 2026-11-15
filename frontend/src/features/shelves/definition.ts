// Vai trò: Định nghĩa giao diện nhập nhóm kệ, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
import sample from "../projects/sample";
export const shelfDefinition = {
  title: "Cấu hình kệ",
  defaultValue: sample.shelves,
  template: { ...sample.shelves.items[0], id: "S", x: null, y: null },
  note: "Optimizable cho phép x/y để null. Khai báo từng tầng và kích thước hữu dụng trong JSON levels. Vị trí và hướng kệ có thể chỉnh ở trang Mặt bằng.",
};
