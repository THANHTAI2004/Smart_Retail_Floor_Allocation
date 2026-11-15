// Vai trò: Điểm khởi tạo React, ghép ứng dụng với StrictMode, ErrorBoundary và stylesheet.
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./app/App";
import { ErrorBoundary } from "./app/ErrorBoundary";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ErrorBoundary><App /></ErrorBoundary>
  </StrictMode>,
);
