// Vai trò: Ô thống kê dùng lại cho nhãn, giá trị, đơn vị và nội dung phụ trên dashboard.
import type { ReactNode } from "react";
// Ô thống kê dùng lại cho nhãn, giá trị, đơn vị và nội dung phụ trên dashboard.
export function Stat({
  label,
  value,
  unit,
  icon,
}: {
  label: string;
  value: string;
  unit: string;
  icon?: ReactNode;
}) {
  return (
    <div className="stat">
      <div className="stat-label">
        {label}
        {icon}
      </div>
      <div className="stat-value">
        {value}
        <small>{unit}</small>
      </div>
    </div>
  );
}
