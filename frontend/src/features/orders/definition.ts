import sample from "../projects/sample";
export const orderDefinition = {
  title: "Đơn hàng",
  defaultValue: sample.orders,
  note: "Nhập riêng orders và order_lines. placed_at cần múi giờ; mỗi cặp (order_id, sku) chỉ xuất hiện một lần và quantity phải dương. due_s là hạn xử lý tính từ thời điểm đơn đến.",
};
