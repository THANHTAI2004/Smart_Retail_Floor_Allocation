// Vai trò: Hiển thị nhãn trạng thái với lớp CSS theo mã trạng thái và chuỗi dễ đọc.
// Hiển thị nhãn trạng thái với lớp CSS theo mã trạng thái và chuỗi dễ đọc.
export function Badge({ status }: { status: string }) {
  return <span className={`badge ${status.toLowerCase()}`}>{status.replaceAll("_", " ")}</span>;
}
