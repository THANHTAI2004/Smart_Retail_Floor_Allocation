import sample from "../projects/sample";
export const categoryDefinition = {
  title: "Ngành hàng",
  defaultValue: sample.categories,
  template: { ...sample.categories.items[0], id: "CAT" },
  note: "required_width_m là tổng chiều rộng hữu dụng yêu cầu. near/separate tham chiếu mã ngành hàng; distance_m áp dụng khoảng cách giữa tâm kệ.",
};
