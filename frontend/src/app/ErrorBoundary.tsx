import { Component, type ReactNode } from "react";

export class ErrorBoundary extends Component<
  { children: ReactNode },
  { failed: boolean }
> {
  state = { failed: false };
  static getDerivedStateFromError() {
    return { failed: true };
  }
  render() {
    if (this.state.failed) {
      return (
        <main className="panel" role="alert">
          <h1>Không thể hiển thị màn hình</h1>
          <p>Dữ liệu đã lưu vẫn ở máy chủ. Tải lại trang để tiếp tục.</p>
          <button onClick={() => window.location.reload()}>Tải lại trang</button>
        </main>
      );
    }
    return this.props.children;
  }
}
