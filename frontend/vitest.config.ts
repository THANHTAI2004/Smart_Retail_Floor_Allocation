// Vai trò: Chọn các bài unit test Vitest; kiểm tra trình duyệt đầu cuối dùng cấu hình Playwright riêng.
import { defineConfig } from "vitest/config";
export default defineConfig({
  test: { include: ["tests/**/*.test.ts"], exclude: ["tests/e2e/**"] },
});
