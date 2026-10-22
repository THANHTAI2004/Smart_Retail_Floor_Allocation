import { test, expect } from "@playwright/test";
import path from "node:path";
import fs from "node:fs/promises";
const output = process.env.SMART_RETAIL_E2E_OUTPUT || "../var/playwright";

test("loading state keeps project creation disabled until data arrives", async ({
  page,
}) => {
  await page.route("**/api/projects", async (route) => {
    await new Promise((resolve) => setTimeout(resolve, 700));
    await route.continue();
  });
  await page.goto("/#projects");
  await expect(
    page.getByText("Đang tải dự án…", { exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Tạo dự án", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByRole("button", { name: "Tạo dự án", exact: true }),
  ).toBeEnabled();
});

test("create, edit, persist, run, inspect, replay, compare and download", async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  page.on("pageerror", (error) => consoleErrors.push(error.message));
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto("/#projects");
  await page
    .getByLabel("Tên dự án", { exact: true })
    .fill(`E2E study ${Date.now()}`);
  await page
    .getByRole("button", { name: "Tạo dự án mẫu", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Mặt bằng", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByText("Đã tạo dự án với 7 nhóm dữ liệu tổng hợp."),
  ).toBeVisible();
  await page.getByLabel("Lối đi tối thiểu", { exact: true }).fill("0.9");
  await page
    .getByRole("button", { name: "Lưu bản vẽ & kệ", exact: true })
    .click();
  await expect(page.getByText(/Đã lưu bản vẽ và kệ/)).toBeVisible();
  await page.reload();
  await expect(
    page.getByLabel("Lối đi tối thiểu", { exact: true }),
  ).toHaveValue("0.9");
  await fs.mkdir(path.resolve(`${output}/ui`), { recursive: true });
  await page.screenshot({
    path: `${output}/ui/desktop-editor.png`,
    fullPage: true,
  });
  await page.getByRole("link", { name: "Lần chạy", exact: true }).click();
  await page
    .getByRole("button", { name: "Kiểm tra dữ liệu", exact: true })
    .click();
  await expect(
    page.getByText("7 nhóm dữ liệu hợp lệ, sẵn sàng chạy."),
  ).toBeVisible();
  await page
    .getByRole("button", { name: "Chạy baseline", exact: true })
    .click();
  await expect(
    page.locator("tbody").getByText("SUCCEEDED", { exact: true }).first(),
  ).toBeVisible({ timeout: 45000 });
  await page
    .getByRole("button", { name: "Kết quả", exact: true })
    .first()
    .click();
  await expect(
    page.getByRole("heading", { name: "Mặt bằng nghiệm T1" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Planogram", exact: true }).click();
  await expect(
    page.getByRole("cell", { name: "WATER", exact: true }),
  ).toBeVisible();
  await expect(
    page.getByRole("cell", { name: "24", exact: true }),
  ).toBeVisible();
  await page
    .getByRole("link", { name: "Mô phỏng & phân tích", exact: true })
    .click();
  await expect(
    page.getByRole("heading", { name: "Giả định mô phỏng" }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Lần chạy", exact: true }).click();
  await page.getByRole("button", { name: "Replay", exact: true }).click();
  await expect(
    page.locator("tbody").getByText("SUCCEEDED", { exact: true }),
  ).toHaveCount(2, { timeout: 45000 });
  await page
    .getByRole("link", { name: "So sánh & báo cáo", exact: true })
    .click();
  await page.getByLabel("So sánh với lần chạy").selectOption({ index: 1 });
  const downloadEvent = page.waitForEvent("download");
  await page.getByRole("link", { name: "Báo cáo JSON", exact: true }).click();
  const download = await downloadEvent;
  await download.saveAs(`${output}/ui/downloaded-report.json`);
  const report = JSON.parse(
    await fs.readFile(`${output}/ui/downloaded-report.json`, "utf-8"),
  );
  expect(report.run.status).toBe("SUCCEEDED");
  expect(report.run.result.stages.T3.placements).toHaveLength(2);
  await page.getByRole("link", { name: "Tổng quan", exact: true }).click();
  await page.screenshot({
    path: `${output}/ui/desktop-dashboard.png`,
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.emulateMedia({ reducedMotion: "reduce" });
  await page.screenshot({
    path: `${output}/ui/mobile-dashboard.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.getByRole("button", { name: "Mở menu", exact: true }).click();
  await page.getByRole("link", { name: "Mặt bằng", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Lưu bản vẽ & kệ" }),
  ).toBeVisible();
  await page.screenshot({
    path: `${output}/ui/mobile-editor.png`,
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.keyboard.press("Tab");
  expect(await page.locator(":focus").count()).toBe(1);
  expect(consoleErrors).toEqual([]);
});

test("backend validation error is visible and invalid edits are not persisted", async ({
  page,
}) => {
  await page.goto("/#projects");
  await page
    .getByRole("button", { name: "Tạo dự án mẫu", exact: true })
    .click();
  await expect(
    page.getByText("Đã tạo dự án với 7 nhóm dữ liệu tổng hợp."),
  ).toBeVisible();
  await page.getByLabel("Lối đi tối thiểu", { exact: true }).fill("-1");
  await page
    .getByRole("button", { name: "Lưu bản vẽ & kệ", exact: true })
    .click();
  await expect(page.getByRole("alert")).toContainText("422");
  await page.reload();
  await expect(
    page.getByLabel("Lối đi tối thiểu", { exact: true }),
  ).toHaveValue("0.8");
});

test("empty and partial project and offline worker feedback", async ({
  page,
  request,
}) => {
  await page.goto("/#projects");
  await page
    .getByLabel("Tên dự án", { exact: true })
    .fill(`Empty ${Date.now()}`);
  await page.getByRole("button", { name: "Tạo dự án", exact: true }).click();
  await expect(
    page.getByText("Đã tạo dự án. Bắt đầu bằng mặt bằng."),
  ).toBeVisible();
  await page.getByRole("link", { name: "Tổng quan", exact: true }).click();
  await expect(
    page.getByText("0/7 nhóm đã lưu", { exact: true }),
  ).toBeVisible();
  await page.getByRole("link", { name: "Mặt bằng", exact: true }).click();
  await page
    .getByRole("button", { name: "Lưu bản vẽ & kệ", exact: true })
    .click();
  await expect(page.getByText(/Đã lưu bản vẽ và kệ/)).toBeVisible();
  await page.getByRole("link", { name: "Tổng quan", exact: true }).click();
  await expect(
    page.getByText("2/7 nhóm đã lưu", { exact: true }),
  ).toBeVisible();
  await page.route("**/api/health", async (route) => {
    const response = await request.get("/api/health");
    await route.fulfill({
      json: { ...(await response.json()), worker_online: false },
    });
  });
  await page.getByRole("link", { name: "Lần chạy", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "Chạy baseline", exact: true }),
  ).toBeDisabled();
  await expect(
    page.getByText("Worker chưa sẵn sàng.", { exact: false }),
  ).toBeVisible();
});
