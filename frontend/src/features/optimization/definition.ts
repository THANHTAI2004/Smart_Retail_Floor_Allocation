import sample from "../projects/sample";
export const optimizationDefinition = {
  title: "Cấu hình tối ưu",
  defaultValue: sample.optimization,
  note: "algorithm: milp hoặc greedy cho T2. slotting_algorithm: first_fit hoặc milp cho T3. candidate_count: 1–8 phương án T1–T4 trong cùng ngân sách thời gian. travel_weight, wait_weight, stock_weight là trọng số không âm; ít nhất một trọng số phải dương. Tập không bị trội chỉ xét các phương án đã tìm được, chưa chứng minh tối ưu toàn cục.",
};
