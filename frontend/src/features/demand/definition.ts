// Vai trò: Định nghĩa giao diện nhập nhóm nhu cầu, gồm giá trị mẫu và gợi ý trường dữ liệu cho trình biên tập dùng chung.
import sample from "../projects/sample";
export const demandDefinition = {
  title: "Nhu cầu & hành vi",
  defaultValue: sample.demand,
  note: "Baseline dùng giỏ hàng tổng hợp và khách đến theo Poisson. Chưa có dữ liệu hành trình quan sát thực tế. horizon_s giới hạn thời điểm đến; các hành trình đã nhận được xử lý đến khi hoàn tất.",
};
